# Các engine AI cờ tướng

Tài liệu này mô tả implementation hiện tại của các engine trong dự án. Kết quả
benchmark V2/V3 gần nhất nằm tại
[`V2_V3_BENCHMARK_RESULTS.md`](V2_V3_BENCHMARK_RESULTS.md).

## Tổng quan

| Engine | Vai trò | Search | Evaluation |
| --- | --- | --- | --- |
| V1 - Minimax Alpha-Beta | Baseline Python | Minimax, Alpha-Beta, iterative deepening, TT, quiescence | Tapered material + PST |
| V2 - WukongJS Negamax | Đối thủ tham chiếu độc lập | Negamax, PVS, LMR, Null Move, Futility, Razoring, TT | Material + PST nghiên cứu |
| V3 - Mate-Aware Negamax | Engine Python chính để phát triển search heuristic | Mate-aware Negamax, PVS, LMR, selective pruning, opening book | Tapered material/PST + evaluation động nhẹ tại lá |
| V4 - NNUE Evaluation | Thử nghiệm neural evaluation | Kế thừa toàn bộ search và opening book của V3 | NNUE lượng tử hóa, fallback về heuristic V3 |

Mã nguồn hiện tại:

```text
backend/
├── core/                       # bàn cờ và sinh nước đi dùng tại biên API
├── engines/
│   ├── v1/                    # baseline Python
│   ├── v2_wukong/             # WukongJS và Node bridge
│   ├── v3/                    # search Python chính
│   └── v4/                    # V3 + NNUE
├── ml/                        # tạo dữ liệu, train và export NNUE
└── benchmarks/                # benchmark V2/V3 và V3/V4
```

## Luồng API

`backend/api.py` chọn engine theo trường `ai_version`:

```text
python_current   -> AIEngine V1
wukong_reference -> WukongJS qua Node bridge
python_v3        -> AIEngineV3
python_v4        -> AIEngineV4
```

Backend kiểm tra lại nước AI trả về trước khi áp dụng. Trạng thái ván đấu, lịch sử
và bộ đếm hòa được frontend gửi kèm mỗi request; backend chưa lưu session riêng.

## V1 - Minimax Alpha-Beta

V1 là baseline dễ giải thích. Engine dùng Minimax với Alpha-Beta, iterative
deepening, transposition table, move ordering và quiescence search.

Evaluation V1 dùng điểm dương cho Đỏ và điểm âm cho Đen:

```text
score = (MG_score * phase + EG_score * (16 - phase)) / 16
```

`MG_score`, `EG_score` và `phase` được cập nhật gia tăng khi đi/hoàn tác nước.

V1 còn hạn chế ở terminal handling tại chân trời tìm kiếm, quiescence chỉ tập
trung vào nước bắt quân, và search khó mở rộng hơn kiến trúc Negamax.

## V2 - WukongJS Negamax

V2 là implementation JavaScript độc lập, không phải phiên bản tiếp theo trực
tiếp của V1. Nó được giữ làm đối thủ tham chiếu và nguồn học kỹ thuật search.

V2 có:

- Negamax, Alpha-Beta và iterative deepening.
- Zobrist transposition table lớn.
- PVS, LMR, Null Move, Futility, Razoring và reverse futility.
- Killer move, history heuristic và MVV-LVA.
- Check extension và mate-distance score.

Evaluation V2 quét bàn cờ và tính:

```text
score = material cố định + PST
```

PST Tốt, Mã, Pháo và Xe được lấy từ nguồn nghiên cứu cờ tướng. V2 đặc biệt
thưởng mạnh Tốt tiến sâu và phân biệt vị trí Mã chi tiết.

V2 chạy nhanh hơn V3 đáng kể nhờ Node.js/V8 và hot path đơn giản hơn. Khi cho
cùng thời gian không giới hạn depth, V2 hiện thường đạt sâu hơn V3 nhiều ply.

## V3 - Mate-Aware Negamax

### Search

V3 triển khai lại các ý tưởng phù hợp từ V2 trong Python và bổ sung xử lý luật,
terminal và chuỗi chiếu chặt hơn:

- Flat board 90 ô, integer move và piece list theo từng bên.
- Zobrist hash gia tăng và transposition table cố định.
- Negamax, PVS, aspiration window và iterative deepening.
- Killer/history, TT move, MVV-LVA và ưu tiên nước chiếu.
- LMR, Null Move, Futility, Razoring và reverse futility.
- Terminal-first: kiểm tra thắng/thua/hòa trước leaf evaluation.
- Quiescence tìm mọi nước thoát chiếu khi bên đến lượt đang bị chiếu.
- Mate-distance score ưu tiên chiếu hết nhanh.
- Cấm nước tạo lặp thế lần ba và xử lý luật 120 half-move.

### Opening book

V3 có opening book nhỏ tại `backend/engines/v3/opening.py`. Book chỉ kích hoạt ở
một số thế khai cuộc đã khai báo và cung cấp tập ứng viên root:

- Pháo đầu hai phía.
- Phát triển Mã hai phía.
- Tiến Tốt cánh.
- Bình phong Mã và một số đáp trả cơ bản.

Search vẫn so sánh các ứng viên trong book. Khi ra khỏi vị trí đã biết, engine
trở lại tìm kiếm toàn bộ nước hợp lệ. V4 kế thừa book này.

### Evaluation dùng trong search

Evaluation lõi của V3 là tapered material/PST cập nhật gia tăng O(1). PST khai
cuộc của Tốt và Mã hiện học lại tín hiệu đã được kiểm chứng từ V2:

- Tốt tiến sâu được thưởng mạnh hơn.
- Vị trí Mã tốt/xấu được phân biệt rõ hơn.

Tại fallback và cửa vào quiescence, V3 dùng thêm `PositionV3.evaluate_search()`
với một số feature động đủ rẻ:

- Phạt Mã bị chặn chân.
- Thưởng Xe xâm nhập nửa bàn đối phương.
- Thưởng Sĩ/Tượng ở gần bảo vệ Tướng.

Các node pruning nội bộ và quiescence sâu hơn vẫn dùng evaluator incremental
nhanh để giữ tốc độ.

### Evaluation giải thích đầy đủ

`EvaluatorV3.evaluate_breakdown()` vẫn cung cấp breakdown chi tiết cho phân tích
và test:

- Mobility.
- Horse activity.
- Rook activity.
- Cannon activity.
- King safety.

Evaluator đầy đủ này rất đắt và không được gọi tại mọi node search.

### Sức mạnh hiện tại so với V2

Benchmark mẫu nhỏ cho thấy:

- Cùng depth 3: V3 thắng `4-0-2`.
- Cùng depth 4: V3 thắng `1-0-5`.
- V3 vẫn cạnh tranh khi V2 sâu hơn một ply.
- Cùng thời gian không giới hạn depth: V2 mạnh hơn vì tìm sâu hơn nhiều.

Ước lượng hiện tại:

```text
V3 cạnh tranh hoặc mạnh hơn khi V3 depth >= V2 depth - 1.
```

Đây chưa phải Elo test chính thức.

## V4 - NNUE Evaluation

V4 kế thừa trực tiếp `AIEngineV3`; khác biệt chính là `SearchContext` tải model
`ml/models/xiangqi.nnue` và gắn NNUE vào `PositionV3`.

Pipeline:

```text
kaggle_data.npz
    -> train_nnue.py
    -> nnue_float.pt
    -> export_nnue.py
    -> xiangqi.nnue
```

Runtime chỉ cần `xiangqi.nnue`. File `nnue_float.pt` chứa trọng số float PyTorch
để tiếp tục training hoặc export lại, nhưng hiện không có trong repo.

NNUE hiện tại:

- Input: hai phía, mỗi phía 1620 feature `piece type x square`.
- Hidden layer dùng chung: 128 unit.
- Output: một điểm scalar.
- Trọng số runtime lượng tử hóa `int16`, bias output `int32`.
- Accumulator được cập nhật gia tăng khi đi quân và phục hồi khi hoàn tác.

Tên module là `halfkp.py`, nhưng feature hiện tại chưa thực sự phụ thuộc vị trí
Tướng; tham số `king_square` chưa tham gia vào `feature_index()`. Vì vậy nên mô
tả chính xác đây là sparse piece-square NNUE, chưa phải HalfKP đầy đủ.

Model hiện được train để bắt chước điểm heuristic V3 từ dataset Kaggle, chưa
được train trực tiếp bằng kết quả thắng/thua hoặc self-play hoàn chỉnh. Nếu model
không tải được, V4 âm thầm fallback về heuristic V3.

Các hạn chế V4 hiện tại:

- Chưa có test suite riêng đầy đủ cho V4/NNUE.
- Pipeline `generate_training_data.py` chưa tương thích hoàn toàn với API V3.
- API hiện trả `score` bằng `EvaluatorV3`, không phải điểm NNUE của V4.
- `AIEngineV4.NNUE_MODEL_PATH` được khai báo nhưng constructor vẫn dựng đường dẫn
  model cố định.

## So sánh nhanh

| Đặc điểm | V1 | V2 | V3 | V4 |
| --- | --- | --- | --- | --- |
| Search chính | Minimax | Negamax | Negamax | Search V3 |
| Zobrist TT | Không | Có | Có | Có |
| PVS / LMR / selective pruning | Không | Có | Có | Có |
| Check-aware quiescence | Không | Không đầy đủ | Có | Có |
| Opening book | Không | Không | Có | Có |
| Evaluation runtime | Tapered PST | Material + PST | Tapered PST + feature nhẹ | NNUE |
| Evaluation breakdown | Không | Không | Có | Có qua evaluator V3 |
| Neural network | Không | Không | Không | Có |

## Kiểm chứng

Các lệnh benchmark hiện có:

```powershell
cd backend
python benchmarks/compare_v2_v3.py 10 0.5
python benchmarks/benchmark_v4.py
```

Test chính:

```text
backend/tests/test_engine_v3.py
backend/tests/test_engine_v3_components.py
backend/tests/test_evaluation_v3.py
```

Khi đánh giá sức mạnh engine, cần ghi rõ:

- Cùng depth hay cùng thời gian.
- Bộ khai cuộc và việc đổi màu.
- Số ply tối đa và luật hòa.
- Nodes, qnodes, depth hoàn thành và NPS.
- Commit/worktree dùng để chạy.
