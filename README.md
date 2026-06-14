# Cờ Tướng AI

Dự án cờ tướng gồm FastAPI backend, React/Vite frontend và bốn lựa chọn engine:

- **V1:** baseline Python Minimax Alpha-Beta.
- **V2:** WukongJS Negamax dùng làm đối thủ tham chiếu.
- **V3:** engine Python mate-aware với PVS/LMR/selective pruning, evaluator lai
  và opening book.
- **V4:** search V3 kết hợp NNUE lượng tử hóa.

## Chạy dự án

Backend:

```powershell
cd backend
pip install -r requirements.txt
python api.py
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Cấu trúc

```text
backend/   API, luật chơi, engine, ML và benchmark
frontend/  giao diện React/Vite
docs/      tài liệu kỹ thuật và kết quả benchmark
ml/        model runtime và dataset cục bộ
```

## Tài liệu

- [Mô tả kỹ thuật các engine](docs/AI_ENGINES.md)
- [Bản trình bày/phản biện phiên bản](docs/AI_VERSION_DEFENSE.md)
- [Kết quả benchmark V2/V3](docs/V2_V3_BENCHMARK_RESULTS.md)

## Trạng thái hiện tại

V3 cho kết quả tốt hơn V2 trong mẫu thử cùng depth 3-4, nhưng V2 vẫn mạnh hơn khi
cùng thời gian vì tìm sâu hơn nhiều. V4 đã tải và chạy model NNUE, nhưng model
hiện chủ yếu học để bắt chước evaluator V3 và pipeline training còn cần hoàn thiện.
