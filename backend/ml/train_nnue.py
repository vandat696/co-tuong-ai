import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.nnue_model import XiangqiNNUE
from engines.v3.halfkp import NUM_FEATURES_PER_SIDE

class XiangqiDataset(Dataset):
    def __init__(self, data_path):
        data = np.load(data_path, allow_pickle=True)
        self.us_features = data['us_features']
        self.them_features = data['them_features']
        self.targets = data['targets'] if 'targets' in data else data['values']
        
    def __len__(self):
        return len(self.targets)
    def __getitem__(self, idx):
        # Return raw indices and scaled target
        target = self.targets[idx] / 400.0
        return self.us_features[idx], self.them_features[idx], np.float32(target)

def train_model(data_path='ml/dataset/self_play_data.npz', epochs=10, batch_size=32):
    if not os.path.exists(data_path):
        print(f"Data not found: {data_path}")
        return
        
    dataset = XiangqiDataset(data_path)
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    model = XiangqiNNUE()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Starting training on {len(dataset)} samples...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_idx, (us_idx, them_idx, targets) in enumerate(train_loader):
            b_size = us_idx.size(0)
            us_feats = torch.zeros(b_size, 1620, dtype=torch.float32)
            them_feats = torch.zeros(b_size, 1620, dtype=torch.float32)
            us_feats.scatter_(1, us_idx.long(), 1.0)
            them_feats.scatter_(1, them_idx.long(), 1.0)
            us_feats[:, 0] = 0.0
            them_feats[:, 0] = 0.0
            targets = targets.unsqueeze(1)
            
            optimizer.zero_grad()
            outputs = model(us_feats, them_feats)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
            if (batch_idx + 1) % 50 == 0:
                print(f"Epoch {epoch+1} - Batch {batch_idx+1}/{len(train_loader)} - Loss: {loss.item():.4f}")
            
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for us_idx, them_idx, targets in val_loader:
                b_size = us_idx.size(0)
                us_feats = torch.zeros(b_size, 1620, dtype=torch.float32)
                them_feats = torch.zeros(b_size, 1620, dtype=torch.float32)
                us_feats.scatter_(1, us_idx.long(), 1.0)
                them_feats.scatter_(1, them_idx.long(), 1.0)
                us_feats[:, 0] = 0.0
                them_feats[:, 0] = 0.0
                targets = targets.unsqueeze(1)
                
                outputs = model(us_feats, them_feats)
                val_loss += criterion(outputs, targets).item()
                
        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {total_loss/len(train_loader):.4f} - Val Loss: {val_loss/len(val_loader):.4f}")
        
    os.makedirs('ml/models', exist_ok=True)
    torch.save(model.state_dict(), 'ml/models/nnue_float.pt')
    print("Saved PyTorch model to ml/models/nnue_float.pt")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train NNUE model")
    parser.add_argument("--data_path", type=str, default="ml/dataset/kaggle_data.npz")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    args = parser.parse_args()
    
    train_model(data_path=args.data_path, epochs=args.epochs, batch_size=args.batch_size)
