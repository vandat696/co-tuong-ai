import torch
import torch.nn as nn
import torch.nn.functional as F

class XiangqiNNUE(nn.Module):
    """
    NNUE architecture for Xiangqi.
    Input: HalfKP features (1620 per side)
    Hidden layer: 128 units per side
    Output: 1 value (scalar) representing evaluation score.
    """
    def __init__(self, input_features=1620, hidden_dim=128):
        super().__init__()
        
        # Shared weights for feature transformation for both sides
        self.feature_transformer = nn.Linear(input_features, hidden_dim)
        
        # Output layer taking combined features from both sides (128 + 128)
        self.output = nn.Linear(hidden_dim * 2, 1)
        
    def forward(self, us_features, them_features):
        """
        us_features: Sparse tensor of shape (batch_size, 1620)
        them_features: Sparse tensor of shape (batch_size, 1620)
        """
        # Feature transformation
        # Clipped ReLU: clamp between 0.0 and 1.0 (or another scale for quantized models, typically 1.0 for float)
        us_acc = torch.clamp(self.feature_transformer(us_features), 0.0, 1.0)
        them_acc = torch.clamp(self.feature_transformer(them_features), 0.0, 1.0)
        
        # Combine (Concatenate)
        combined = torch.cat([us_acc, them_acc], dim=1)
        
        # Since we use MSELoss on raw centipawn scores, return raw linear output
        return self.output(combined)
