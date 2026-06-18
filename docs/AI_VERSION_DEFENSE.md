# Trình bày sự phát triển các phiên bản AI

Tài liệu này là bản tóm tắt dùng để trình bày và phản biện. Mô tả kỹ thuật đầy đủ
nằm tại [`AI_ENGINES.md`](AI_ENGINES.md).

## Thông điệp chính

```text
V1: xây dựng baseline Python dễ hiểu
V2: dùng WukongJS độc lập để học search và làm đối thủ tham chiếu
V3: triển khai search Python mate-aware, evaluator lai và opening book
V4: thử nghiệm thay evaluator V3 bằng NNUE lượng tử hóa
```

Nhiều thuật toán hơn không tự động đồng nghĩa mạnh hơn. Sức mạnh thực tế phụ
thuộc đồng thời vào chất lượng evaluation, độ sâu đạt được, move ordering, luật
chơi và các tham số pruning.

## Tóm tắt phiên bản

| Phiên bản | Mục tiêu | Điểm nổi bật | Hạn chế chính |
| --- | --- | --- | --- |
| V1 | Baseline hoàn chỉnh, dễ giải thích | Minimax, Alpha-Beta, tapered PST | Terminal và quiescence còn hạn chế |
| V2 | Đối thủ tham chiếu nhanh | WukongJS, PVS/LMR/selective pruning, PST nghiên cứu | Không phải code Python của dự án; luật cục bộ phải kiểm tra lại |
| V3 | Engine Python chính | Mate-aware search, flat board, feature động nhẹ, opening book | Chậm hơn V2 nên thua khi cùng thời gian |
| V4 | Neural evaluation | Search V3 + NNUE accumulator lượng tử hóa | Model chủ yếu bắt chước V3; pipeline train còn hạn chế |

## V1

V1 chứng minh dự án có thể:

- Sinh và kiểm tra nước đi.
- Tìm kiếm bằng Minimax Alpha-Beta.
- Quản lý thời gian bằng iterative deepening.
- Đánh giá thế cờ bằng tapered material/PST.

Vấn đề quan trọng của V1 là có thể đánh giá tĩnh trước khi nhận ra chiếu hết nằm
đúng tại chân trời tìm kiếm.

## V2

V2 là WukongJS độc lập. Nó cho dự án một mốc tham chiếu về:

- Negamax và Zobrist TT.
- PVS, LMR, Null Move, Futility và Razoring.
- Killer/history move ordering.
- PST cờ tướng đã được lấy từ nguồn nghiên cứu.

V2 chạy nhanh hơn V3 đáng kể và thường tìm sâu hơn nhiều khi cùng thời gian.

## V3

V3 sửa terminal handling và xây dựng lại hot path search:

- Terminal-first và check-aware quiescence.
- Flat board, integer moves, piece lists và undo stack.
- Zobrist TT, PVS, aspiration, LMR và selective pruning.
- Opening book nhỏ nhưng search vẫn chọn giữa các ứng viên tốt.

Evaluation V3 có ba lớp sử dụng khác nhau:

1. **Evaluator incremental nhanh:** tapered material/PST cho pruning và search sâu.
2. **Evaluator search nhẹ:** thêm chân Mã, Xe xâm nhập và phòng thủ gần Tướng tại
   fallback/cửa vào quiescence.
3. **Evaluator breakdown đầy đủ:** mobility, Mã, Xe, Pháo và King Safety cho phân
   tích/test, không chạy ở mọi node.

PST Tốt và Mã khai cuộc hiện học lại tín hiệu từ V2. Đây là lý do V3 cải thiện
chất lượng mỗi node nhưng vẫn giữ tapered evaluation cho tàn cuộc.

### Kết quả V3 so với V2

Benchmark mẫu nhỏ, bắt đầu sau hai nước khai cuộc cố định:

| Cấu hình | Kết quả V3 - V2 - hòa |
| --- | ---: |
| Cùng depth 3 | `4-0-2` |
| Cùng depth 4 | `1-0-5` |
| V3 depth 3, V2 depth 4 | `1-0-5` |
| V3 depth 4, V2 depth 5 | `1-0-5` |
| Cùng thời gian `0.1s` | `0-1-5` |
| Cùng thời gian `0.3s` | `0-5-1` |

Kết luận thận trọng:

```text
V3 có chất lượng evaluation mỗi node tốt hơn trong mẫu thử.
V2 vẫn mạnh hơn khi cùng thời gian vì đạt độ sâu lớn hơn.
```

## V4

V4 không thay search. Nó kế thừa V3 và thay evaluation runtime bằng NNUE:

```text
V4 = V3 search + V3 opening book + NNUE evaluation
```

NNUE dùng sparse piece-square feature, hidden layer 128 unit, accumulator gia
tăng và trọng số lượng tử hóa. Model `xiangqi.nnue` đã được train/export và tải
được, nhưng mục tiêu train hiện tại chủ yếu là bắt chước điểm heuristic V3.

Điểm cần nói chính xác khi trình bày:

- Implementation hiện chưa phải HalfKP đầy đủ vì feature chưa dùng vị trí Tướng.
- V4 fallback về heuristic V3 nếu model lỗi.
- File runtime là `xiangqi.nnue`; `nnue_float.pt` chỉ cần để train tiếp/export lại.
- V4 chưa được chứng minh mạnh hơn V3 bằng benchmark đủ lớn.

## Các câu hỏi phản biện

### V3 có mạnh hơn V2 không?

Không thể trả lời chỉ bằng một chữ "có". Cùng depth 3-4, V3 đang có kết quả tốt
hơn trong mẫu thử. Cùng thời gian không giới hạn depth, V2 mạnh hơn vì chạy nhanh
và tìm sâu hơn nhiều.

### Vì sao V3 tìm ít node hơn nhưng vẫn thắng ở cùng depth?

Evaluator mới cung cấp tín hiệu vị trí tốt hơn cho Tốt, Mã và một số feature động.
V3 có thể chọn nước tốt hơn dù xét ít node. Tuy nhiên, khi V2 sâu hơn nhiều ply,
lợi thế nhìn xa thường lớn hơn lợi thế evaluation.

### Vì sao không dùng evaluator breakdown đầy đủ ở mọi node?

Evaluator đầy đủ phải sinh mobility và phân tích quan hệ quân, chậm hơn evaluator
incremental hơn nhiều. V3 chỉ đưa một số feature rẻ vào search để cân bằng chất
lượng mỗi node và độ sâu.

### Opening book có ép cứng một nước không?

Không. Tại vị trí có book, V3/V4 search giữa một tập ứng viên khai cuộc tốt. Khi
ra khỏi book, engine tìm toàn bộ nước hợp lệ như bình thường.

### V4 đã được train chưa?

Có. Repo chứa `ml/models/xiangqi.nnue`, là model đã train và lượng tử hóa. Nhưng
nó chủ yếu học điểm heuristic V3, chưa học trực tiếp sức mạnh thắng/thua từ
self-play hoàn chỉnh.

## Đoạn trình bày ngắn

> V1 là baseline Python dùng Minimax Alpha-Beta và tapered evaluation. V2 là
> WukongJS độc lập, được dùng để học các kỹ thuật search hiện đại và làm đối thủ
> tham chiếu. V3 triển khai lại search Python theo hướng mate-aware, sử dụng flat
> board, Zobrist TT, PVS, LMR, selective pruning, opening book và evaluator lai.
> Kết quả thử nghiệm cho thấy V3 có chất lượng mỗi node tốt hơn ở cùng depth,
> nhưng V2 vẫn mạnh hơn khi cùng thời gian vì tìm sâu hơn. V4 giữ nguyên search
> V3 và thử nghiệm NNUE lượng tử hóa; model đã chạy được nhưng hiện chủ yếu bắt
> chước evaluator V3 và chưa phải HalfKP đầy đủ.

## File nên mở khi trình bày

| Nội dung | File |
| --- | --- |
| V1 baseline | `backend/engines/v1/ai_engine.py`, `backend/engines/v1/eval.py` |
| V2 search/evaluation | `backend/engines/v2_wukong/wukong.js` |
| V3 search | `backend/engines/v3/engine.py` |
| V3 position/hot path | `backend/engines/v3/position.py` |
| V3 opening book | `backend/engines/v3/opening.py` |
| V3 breakdown | `backend/engines/v3/evaluation/` |
| V4 NNUE | `backend/engines/v4/engine_v4.py`, `backend/engines/v3/accumulator.py` |
| Training/export | `backend/ml/train_nnue.py`, `backend/ml/export_nnue.py` |
| Benchmark gần nhất | `docs/V2_V3_BENCHMARK_RESULTS.md` |
