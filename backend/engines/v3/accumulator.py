import numpy as np
import struct
import os

QA = 255
QB = 64
SHIFT_BITS = 14 # Output shift (approximate for standard NNUE, usually derived from scale factors)
# The actual evaluation formula in int: (raw_out) / (QA * QB)
# Since QA=255 (~256=2^8) and QB=64 (2^6), product is ~2^14
# We can use a right shift to de-quantize

class NNUEAccumulator:
    """
    Accumulator for the Hidden Layer (Feature Transformer).
    Operates using int16 arithmetic via NumPy.
    """
    def __init__(self, weights_int16, biases_int16):
        # weights: shape (1620, 128)
        # biases: shape (128,)
        self.weights = weights_int16
        self.biases = biases_int16
        self.values = np.copy(biases_int16)
        
    def full_compute(self, active_features):
        self.values = np.copy(self.biases)
        for idx in active_features:
            self.values += self.weights[idx]
            
    def update_add(self, feature_index):
        self.values += self.weights[feature_index]
        
    def update_sub(self, feature_index):
        self.values -= self.weights[feature_index]
        
    def clipped_relu(self):
        # Clipped ReLU: clamp between 0 and QA (255)
        # return np.clip(self.values, 0, QA).astype(np.int16)
        # Faster with np.maximum/minimum
        return np.minimum(np.maximum(self.values, 0), QA).astype(np.int16)

class NNUEInference:
    """
    Full Quantized NNUE Inference engine.
    """
    def __init__(self, model_path):
        self.ft_weights = None
        self.ft_biases = None
        self.out_weights = None
        self.out_bias = None
        
        self.load(model_path)
        
        self.red_acc = NNUEAccumulator(self.ft_weights, self.ft_biases)
        self.black_acc = NNUEAccumulator(self.ft_weights, self.ft_biases)
        
        self.acc_stack_red = []
        self.acc_stack_black = []

    def load(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"NNUE model not found: {path}")
            
        with open(path, 'rb') as f:
            magic = f.read(4)
            if magic != b'NNUE':
                raise ValueError("Invalid NNUE file format")
                
            version = struct.unpack('<I', f.read(4))[0]
            
            in_dim, hidden_dim, out_dim = struct.unpack('<III', f.read(12))
            
            # Read ft weights (in_dim * hidden_dim * 2 bytes)
            ft_w_bytes = f.read(in_dim * hidden_dim * 2)
            self.ft_weights = np.frombuffer(ft_w_bytes, dtype=np.int16).reshape((in_dim, hidden_dim))
            
            # Read ft bias (hidden_dim * 2 bytes)
            ft_b_bytes = f.read(hidden_dim * 2)
            self.ft_biases = np.frombuffer(ft_b_bytes, dtype=np.int16)
            
            # Read out weights (hidden_dim * 2 * out_dim * 2 bytes) -> 256 x 1
            out_w_bytes = f.read(hidden_dim * 2 * out_dim * 2)
            self.out_weights = np.frombuffer(out_w_bytes, dtype=np.int16).reshape((hidden_dim * 2, out_dim))
            
            # Read out bias (out_dim * 4 bytes) -> int32
            out_b_bytes = f.read(out_dim * 4)
            self.out_bias = np.frombuffer(out_b_bytes, dtype=np.int32)

    def evaluate(self, is_red_turn):
        us_acc = self.red_acc if is_red_turn else self.black_acc
        them_acc = self.black_acc if is_red_turn else self.red_acc
        
        us_out = us_acc.clipped_relu()
        them_out = them_acc.clipped_relu()
        
        combined = np.concatenate([us_out, them_out]) # shape (256,)
        
        # Output layer calculation: int16 * int16 -> int32
        raw = np.dot(combined.astype(np.int32), self.out_weights.astype(np.int32).flatten())
        raw += self.out_bias[0]
        
        # De-quantize
        # The model is trained on Centipawns / 400.0.
        # raw = output * QA * QB = (score / 400) * 16320 = score * 40.8
        score = int(raw // 41)
        return score
    def full_recompute(self, red_feats, black_feats):
        self.red_acc.full_compute(red_feats)
        self.black_acc.full_compute(black_feats)

    def push(self, removed_red, added_red, removed_black, added_black):
        self.acc_stack_red.append(np.copy(self.red_acc.values))
        self.acc_stack_black.append(np.copy(self.black_acc.values))
        
        for f in removed_red: self.red_acc.update_sub(f)
        for f in added_red: self.red_acc.update_add(f)
        
        for f in removed_black: self.black_acc.update_sub(f)
        for f in added_black: self.black_acc.update_add(f)
        
    def pop(self):
        self.red_acc.values = self.acc_stack_red.pop()
        self.black_acc.values = self.acc_stack_black.pop()
