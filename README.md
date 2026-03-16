# ♞ Cờ Tướng AI Bot

Đây là project học tập nhập môn Trí Tuệ Nhân Tạo - Xây dựng bot chơi cờ tướng (Xiangqi) có khả năng tự học.

## 📋 Tính năng

- **Backend**: Minimax + Alpha-Beta Pruning + Transposition Table
- **Evaluation**: Heuristic + Mạng neural ML (PyTorch)
- **Frontend**: React + Vite, bàn cờ tương tác 10x9

## 🏗️ Cấu trúc dự án
co-tuong-ai/
├── backend/ # Python engine + API
├── frontend/ # React UI
├── docs/ # Tài liệu
└── README.md

## 🚀 Setup & Chạy

### Backend
```bash
cd backend
pip install -r requirements.txt
python api.py
```
### Frontend
```bash
cd frontend
npm install
npm run dev
````
📝 Tiến trình
 Bước 1: board.py + move_gen.py
 Bước 2: Minimax cơ bản
 Bước 3: React + Vite setup
 Bước 4: API FastAPI
 ... (tiếp theo)
 👥 Vai trò
AI Engine + API: Board, Move Generation, Minimax, FastAPI
ML & Training: Dataset, Preprocessing, PyTorch
Frontend: React, CSS, UX
Last updated: 16/03/2026