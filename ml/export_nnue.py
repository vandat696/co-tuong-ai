import os
import sys
import torch
import numpy as np
import struct

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.nnue_model import XiangqiNNUE

# Quantization scaling factors
QA = 255  # Quantization of activation (typically 127 or 255 for clipped ReLU)
QB = 64   # Quantization of weights (power of 2 for fast shifting)

def export_to_binary(model_path, out_path):
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return
        
    model = XiangqiNNUE()
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    # Extract weights
    ft_weights = model.feature_transformer.weight.detach().numpy() # shape (128, 1620)
    ft_bias = model.feature_transformer.bias.detach().numpy()      # shape (128,)
    
    out_weights = model.output.weight.detach().numpy() # shape (1, 256)
    out_bias = model.output.bias.detach().numpy()      # shape (1,)
    
    # Transpose for easier C/NumPy memory layout
    # ft_weights: (1620, 128) - so we can just index by feature and add to accumulator
    ft_weights_t = ft_weights.T 
    out_weights_t = out_weights.T # shape (256, 1)
    
    # Quantize Feature Transformer
    # W_quant = round(W_float * QA)
    # B_quant = round(B_float * QA)
    ft_weights_q = np.round(ft_weights_t * QA).astype(np.int16)
    ft_bias_q = np.round(ft_bias * QA).astype(np.int16)
    
    # Quantize Output Layer
    # Output weight quant = round(W_float * QB)
    # Output bias quant = round(B_float * QA * QB)
    out_weights_q = np.round(out_weights_t * QB).astype(np.int16)
    out_bias_q = np.round(out_bias * QA * QB).astype(np.int32)
    
    # Write to binary format
    with open(out_path, 'wb') as f:
        # Magic number / Version
        f.write(b'NNUE')
        f.write(struct.pack('<I', 1)) # Version 1
        
        # Write dimensions
        f.write(struct.pack('<III', 1620, 128, 1))
        
        # Write Feature Transformer Weights (1620 x 128 x int16)
        f.write(ft_weights_q.tobytes())
        # Write Feature Transformer Biases (128 x int16)
        f.write(ft_bias_q.tobytes())
        
        # Write Output Weights (256 x 1 x int16)
        f.write(out_weights_q.tobytes())
        # Write Output Bias (1 x int32)
        f.write(out_bias_q.tobytes())
        
    print(f"Successfully exported quantized model to {out_path}")
    print(f"FT Weights max: {np.max(ft_weights_q)}, min: {np.min(ft_weights_q)}")
    print(f"Out Weights max: {np.max(out_weights_q)}, min: {np.min(out_weights_q)}")

if __name__ == "__main__":
    export_to_binary('ml/models/nnue_float.pt', 'ml/models/xiangqi.nnue')
