# Trình bày sự phát triển các phiên bản AI

Tài liệu này dùng để trình bày và bảo vệ quá trình phát triển AI cờ tướng của dự án.
Mục tiêu không phải khẳng định phiên bản có nhiều thuật toán nhất chắc chắn mạnh
nhất, mà giải thích rõ mỗi phiên bản giải quyết vấn đề gì, đánh đổi điều gì và được
kiểm chứng như thế nào.

## Thông điệp chính

Quá trình phát triển trả lời lần lượt ba câu hỏi:

1. **V1:** Làm thế nào xây dựng một AI cờ tướng hoàn chỉnh, dễ hiểu và có thể dùng
   làm mốc so sánh?
2. **V2:** Một engine tham chiếu có search tối ưu hơn đang sử dụng những kỹ thuật
   nào?
3. **V3:** Làm thế nào đưa các kỹ thuật phù hợp vào engine Python, sửa lỗi nhận diện
   chiếu hết và giúp AI hiểu thế cờ tốt hơn?

V2 là WukongJS độc lập, không phải bản nâng cấp trực tiếp từ V1. V3 mới là bước phát
triển tiếp theo của engine Python dựa trên những vấn đề tìm thấy ở V1 và kiến thức
tham khảo từ V2.

```text
V1 Python baseline
    |
    | phát hiện hạn chế về chiếu hết, hiệu năng search và evaluation
    v
V2 WukongJS tham chiếu ---- học các kỹ thuật search tiên tiến
    |                                     |
    +-------------------------------------+
                                          v
                              V3 Python cải tiến
```

## Tóm tắt ba phiên bản

| Phiên bản | Mục tiêu | Search | Evaluation |
| --- | --- | --- | --- |
| V1 | Xây dựng baseline hoàn chỉnh, dễ hiểu | Minimax, Alpha-Beta, IDS, TT, quiescence | Tapered material + PST |
| V2 | Làm đối thủ và nguồn tham khảo độc lập | Negamax cùng nhiều kỹ thuật pruning nâng cao | Material + PST nghiên cứu |
| V3 | Sửa hạn chế của V1 và phát triển engine Python | Mate-aware Negamax, Zobrist TT, PVS, LMR, selective pruning | Tapered material/PST + activity + King Safety |

## V1 - Baseline dễ hiểu

### Vấn đề cần giải quyết

Dự án cần một AI có thể:

- Tuân thủ luật cờ tướng.
- Tìm nước đi bằng cây trò chơi.
- Hoạt động trong giới hạn thời gian.
- Có hàm đánh giá đủ nhanh để gọi tại nhiều nút.

### Giải pháp

V1 sử dụng Minimax:

```text
Đỏ tối đa hóa điểm
Đen tối thiểu hóa điểm
```

Alpha-Beta bỏ qua các nhánh không thể thay đổi quyết định. Iterative Deepening tìm
từ độ sâu thấp lên cao để luôn giữ được một kết quả hoàn chỉnh khi hết thời gian.

Hàm đánh giá V1 sử dụng Tapered Evaluation:

```text
score = (MG_score * phase + EG_score * (16 - phase)) / 16
```

Giá trị quân và PST được cập nhật gia tăng sau mỗi nước đi nên evaluation gần như
`O(1)`.

### Ưu điểm

- Cấu trúc thuật toán dễ giải thích và kiểm tra.
- Có đầy đủ nền tảng: Alpha-Beta, IDS, TT, move ordering và quiescence.
- Phân biệt khai/trung cuộc với tàn cuộc.
- Evaluation rất nhanh.
- Phù hợp làm baseline để đo các cải tiến sau.

### Nhược điểm

- Minimax viết riêng logic MAX/MIN nên dài và khó mở rộng hơn Negamax.
- TT dùng chuỗi toàn bàn làm khóa, tốn chi phí tạo khóa.
- Move ordering chủ yếu dựa trên nước bắt quân.
- Quiescence chỉ xét nước bắt quân.
- Nếu chiếu hết xuất hiện đúng tại `depth == 0`, V1 có thể đánh giá tĩnh trước khi
  nhận diện chiếu hết.
- Evaluation chưa hiểu chân Mã, hoạt động Xe/Pháo hoặc an toàn Tướng thực tế.

### Ví dụ hạn chế quan trọng

Trong ca kiểm thử một thế Đen đã bị chiếu hết:

```text
V1 minimax(depth=1) = 10000   # nhận diện thắng
V1 minimax(depth=0) = 1916    # chỉ đánh giá thế cờ
```

Điều này giải thích vì sao V1 đôi lúc chọn ăn quân thay vì thực hiện đòn chiếu hết
nằm đúng tại chân trời tìm kiếm.

## V2 - Engine tham chiếu WukongJS

### Vai trò

V2 được đưa vào để:

- Có một đối thủ độc lập cho V1.
- Quan sát cách một engine khác tổ chức Negamax.
- Tham khảo các kỹ thuật tối ưu search đã được triển khai.
- So sánh hai triết lý evaluation khác nhau.

### Điểm tiên tiến hơn V1

Wukong sử dụng:

- Zobrist Hashing.
- Principal Variation Search.
- Null Move Pruning.
- Futility Pruning và Razoring.
- Late Move Reduction.
- Killer Move và History Heuristic.
- Check Extension và mate-distance score.

Các kỹ thuật này không làm thay đổi luật chơi. Chúng giúp engine tìm sâu hơn bằng
cách ưu tiên nhánh tốt và giảm công sức ở nhánh ít triển vọng.

### Evaluation V2

V2 sử dụng material cố định và PST lấy từ tài liệu nghiên cứu cờ tướng:

```text
evaluation = material + PST
```

PST của V2 chi tiết cho Tốt, Mã, Pháo và Xe. V2 đặc biệt thưởng mạnh Tốt tiến sâu
gần cung đối phương.

### Ưu điểm

- Search có nhiều kỹ thuật tối ưu hơn V1.
- Move ordering tốt hơn nhờ killer/history và hash move.
- PST được lấy từ nguồn nghiên cứu.
- Là nguồn tham khảo tốt vì được phát triển độc lập.

### Nhược điểm

- Không dùng Tapered Evaluation.
- Không có PST Tướng.
- Evaluation chưa hiểu quan hệ động như chân Mã hoặc chất lượng ngòi Pháo.
- Quiescence vẫn chỉ xét nước bắt quân và có thể chưa xử lý đúng trạng thái bị
  chiếu tại chân trời.
- Chạy qua Node bridge nên việc tích hợp luật cục bộ như cấm lặp cần backend Python
  kiểm tra lại.

### Vì sao không chỉ dùng V2?

Mục tiêu dự án không chỉ là lấy một engine có sẵn để chơi. Dự án cần làm chủ engine
Python, có thể giải thích, kiểm thử và tiếp tục phát triển evaluation riêng. Vì vậy
V2 được giữ làm đối thủ tham chiếu, còn các ý tưởng phù hợp được triển khai lại
trong V3.

## V3 - Engine Python cải tiến

### Mục tiêu

V3 giải quyết đồng thời ba nhóm hạn chế:

1. Nhận diện chuỗi chiếu và chiếu hết chính xác hơn.
2. Tìm sâu hiệu quả hơn trong cùng giới hạn tài nguyên.
3. Hiểu thêm các đặc điểm động riêng của cờ tướng.

### Thay đổi kiến trúc

V1 chứa phần lớn search trong một file dài. V3 chia trách nhiệm thành các module:

```text
engine_v3/
├── engine.py          # Negamax, PVS, LMR và pruning
├── context.py         # trạng thái search, đi/hoàn tác, cache evaluation
├── ordering.py        # MVV-LVA, killer và history
├── transposition.py   # TT giới hạn kích thước
├── zobrist.py         # hash gia tăng
└── evaluation/
    ├── evaluator.py   # tổng hợp và breakdown
    ├── activity.py    # mobility, Mã, Xe và Pháo
    └── king_safety.py # an toàn Tướng
```

Lợi ích của việc tách module:

- Mỗi file có một trách nhiệm rõ ràng.
- Có thể test từng thành phần độc lập.
- Dễ bật/tắt hoặc điều chỉnh một kỹ thuật.
- Giảm nguy cơ sửa search làm hỏng evaluation và ngược lại.

### Search V3

V3 dùng Negamax:

```text
điểm tốt cho mình = -điểm tốt cho đối thủ
```

V3 triển khai các tối ưu search tham khảo từ Wukong:

- Zobrist TT giới hạn kích thước.
- Killer Move, History Heuristic, TT move và MVV-LVA.
- Aspiration Windows và PVS.
- LMR.
- Null Move, Futility, Reverse Futility và Razoring.
- Check Extension và mate-distance pruning.

V3 bổ sung hàng rào an toàn:

- Kiểm tra terminal trước leaf evaluation.
- Nếu đang bị chiếu, quiescence xét mọi nước thoát chiếu.
- Không chạy selective pruning khi đang bị chiếu.
- Không Futility Pruning hoặc LMR nước bắt quân và nước chiếu.

### Evaluation V3

V3 dùng evaluation lai. Search sâu dùng tapered material/PST của V1 làm nền nhanh:

```text
base = tapered material + tapered PST
```

Evaluation động dùng cho breakdown, phân tích và fallback khi chưa hoàn thành vòng
iterative deepening:

```text
evaluation =
    base
  + mobility
  + horse_activity
  + rook_activity
  + cannon_activity
  + king_safety
```

Ý nghĩa từng feature:

| Feature | Vấn đề giải quyết |
| --- | --- |
| Mobility | Phân biệt quân hoạt động tốt với quân bị nhốt |
| Horse activity | Phạt Mã bị chặn chân |
| Rook activity | Thưởng Xe xâm nhập sang phần bàn đối phương |
| Cannon activity | Đánh giá ngòi Pháo và mục tiêu sau ngòi |
| King Safety | Đánh giá Sĩ/Tượng bảo vệ, quân áp sát cung và trạng thái bị chiếu |

`EvaluatorV3.evaluate_breakdown()` trả điểm từng feature để giải thích và tuning.
Cách lai này tránh gọi các feature động đắt tiền tại mọi leaf, giúp V3 đạt depth
cao hơn trong cùng thời gian.

### Ưu điểm

- Nhận diện chiếu hết ở chân trời đúng hơn V1 và V2.
- Ưu tiên chiếu hết nhanh bằng mate-distance score.
- Search có đầy đủ nhóm tối ưu nâng cao.
- Có evaluation động để phân tích thêm đặc điểm riêng của cờ tướng.
- Kiến trúc module hóa và có test từng thành phần.
- Cache evaluation theo Zobrist tránh tính lại cùng một thế.

### Nhược điểm

- Evaluation động chậm hơn V1 đáng kể nên chưa được dùng tại mọi leaf.
- Selective pruning luôn có rủi ro cắt nhầm nếu trọng số hoặc điều kiện chưa tốt.
- Trọng số feature hiện là giá trị khởi đầu, chưa được tuning bằng hàng trăm ván.
- Chưa có benchmark Elo đủ lớn để khẳng định V3 chắc chắn mạnh hơn mọi phiên bản.

## Chuẩn so sánh thời gian

Đấu trường cấp cùng ngân sách suy nghĩ `0.5` giây cho V1, V2 và V3. Cả ba dùng
iterative deepening với `max_depth = 64` làm trần an toàn và trả nước tốt nhất
của độ sâu đã hoàn thành. Nhờ vậy phép so sánh tập trung vào độ sâu, số node và
chất lượng nước đi đạt được trong cùng thời gian, thay vì ép các engine chạy cùng
độ sâu dù tốc độ triển khai khác nhau.

## Sự tiến bộ qua từng phiên bản

| Khía cạnh | V1 | V2 | V3 |
| --- | --- | --- | --- |
| Vai trò | Baseline Python | Tham chiếu độc lập | Engine Python phát triển |
| Tổ chức search | Một file chính | Engine JS độc lập | Module hóa |
| Biểu diễn Minimax | MAX/MIN riêng | Negamax | Negamax |
| Khóa TT | Chuỗi bàn cờ | Zobrist | Zobrist gia tăng |
| Move ordering | TT move + MVV-LVA | Hash, MVV-LVA, killer/history | TT, MVV-LVA, killer/history |
| Search nâng cao | Cơ bản | PVS, LMR, selective pruning | PVS, LMR, selective pruning có hàng rào |
| Chiếu tại quiescence | Chưa xử lý đầy đủ | Chưa xử lý đầy đủ | Tìm mọi nước thoát chiếu |
| Ưu tiên mate nhanh | Chưa có | Có | Có |
| Giai đoạn ván đấu | Có | Không | Có |
| Feature động | Chưa có | Chưa có | Có |
| Tốc độ evaluation | Rất nhanh | Nhanh | Chậm hơn nhưng hiểu thế cờ hơn |
| Khả năng giải thích điểm | Tổng điểm | Tổng điểm | Breakdown theo feature |

## Luận điểm bảo vệ quan trọng

### Nhiều thuật toán hơn có chắc chắn mạnh hơn không?

Không. Sức mạnh thực chiến phụ thuộc vào:

- Độ chính xác của luật và terminal handling.
- Chất lượng move ordering.
- Chất lượng evaluation.
- Tốc độ implementation.
- Trọng số và điều kiện pruning.

V3 có nền tảng tiên tiến hơn, nhưng cần đấu A/B đủ nhiều để kết luận sức mạnh.

### Vì sao V3 evaluation tốt hơn nhưng lại có thể tìm ít nút hơn?

Feature động phải kiểm tra quan hệ giữa nhiều quân nên đắt hơn material/PST gia
tăng của V1. Đây là đánh đổi giữa:

```text
nhìn nhiều thế cờ hơn
và
hiểu mỗi thế cờ tốt hơn
```

V3 dùng cache Zobrist để giảm chi phí, nhưng vẫn cần benchmark để tìm điểm cân bằng.

### Vì sao không thay đổi trực tiếp V1?

Giữ V1 giúp:

- Có baseline ổn định.
- Đấu A/B giữa phiên bản cũ và mới.
- Xác định cải tiến nào thực sự có hiệu quả.
- Tránh mất khả năng tái hiện hành vi cũ.

### Vì sao V2 không được gọi là bản mạnh hơn V1?

V2 là implementation độc lập, khác ngôn ngữ, search, evaluation và cấu hình độ sâu.
Nếu V2 thắng V1, chưa thể biết nguyên nhân đến từ thuật toán nào. V2 phù hợp làm đối
thủ tham chiếu hơn là một bước trong chuỗi phát triển Python.

### Bằng chứng nào cho thấy V3 sửa được lỗi chiếu hết?

Regression test xác nhận:

- Terminal tại `depth == 0` trả mate score.
- Quiescence tìm nước thoát chiếu không ăn quân.
- Mate-in-one tại chân trời được tìm đúng.
- API trả `is_checkmate=True` và đúng người thắng.

### Bằng chứng nào cho thấy evaluation V3 hoạt động đúng hướng?

Unit test xác nhận:

- Mã bị chặn chân được chấm thấp hơn Mã tự do.
- Xe tiến sâu nhận activity bonus.
- Pháo có ngòi hướng vào Tướng nhận pressure bonus.
- Tướng có đủ Sĩ/Tượng bảo vệ nhận King Safety tốt hơn.
- Tổng breakdown bằng tổng các feature.
- Bàn khởi đầu đối xứng có điểm bằng `0`.

## Cách trình bày demo

Một bài bảo vệ ngắn có thể đi theo thứ tự:

1. Chọn V1 và giải thích đây là baseline dễ hiểu.
2. Trình bày lỗi chiếu hết tại chân trời bằng đoạn `depth == 0`.
3. Giới thiệu V2 như nguồn tham khảo cho search nâng cao.
4. Chọn V3 và cho chạy thế mate-in-one mà V1 từng đánh giá sai.
5. Hiển thị breakdown evaluation V3 cho hai thế Mã tự do và Mã bị chặn.
6. Kết luận bằng đánh đổi: V3 hiểu thế cờ tốt hơn nhưng cần benchmark Elo để tuning.

## Các đoạn code nên mở khi bảo vệ

| Nội dung cần chứng minh | File và hàm |
| --- | --- |
| V1 dùng Minimax và đánh giá leaf bằng quiescence | `backend/src/ai_engine.py`: `minimax()`, `quiescence_search()` |
| V1 dùng Tapered Evaluation | `backend/src/eval.py`: `evaluate()` |
| V2 dùng Negamax và selective pruning | `backend/references/wukong/wukong.js`: `negamax()` |
| V3 kiểm tra terminal trước leaf evaluation | `backend/src/engine_v3/engine.py`: `_negamax()` |
| V3 quiescence xử lý nước thoát chiếu | `backend/src/engine_v3/engine.py`: `_quiescence()` |
| V3 dùng Zobrist và TT | `backend/src/engine_v3/zobrist.py`, `transposition.py` |
| V3 dùng killer/history | `backend/src/engine_v3/ordering.py` |
| V3 evaluation có breakdown | `backend/src/engine_v3/evaluation/evaluator.py`: `evaluate_breakdown()` |
| Feature chân Mã, Xe và Pháo | `backend/src/engine_v3/evaluation/activity.py` |
| Feature an toàn Tướng | `backend/src/engine_v3/evaluation/king_safety.py` |
| Bằng chứng regression test | `backend/tests/test_engine_v3.py`, `test_evaluation_v3.py` |

## Kịch bản trình bày ngắn

Có thể trình bày trong khoảng ba phút:

> V1 là baseline Python dùng Minimax Alpha-Beta và Tapered Evaluation. Ưu điểm của
> nó là dễ hiểu, evaluation rất nhanh và phân biệt được giai đoạn ván đấu. Khi kiểm
> thử, nhóm phát hiện V1 có thể bỏ lỡ chiếu hết xuất hiện đúng tại chân trời tìm
> kiếm vì chuyển sang quiescence trước khi kiểm tra terminal.
>
> V2 là WukongJS độc lập được dùng làm đối thủ tham chiếu. Engine này cho thấy lợi
> ích của Negamax, Zobrist Hashing, PVS, LMR, Null Move và các kỹ thuật move
> ordering. Tuy nhiên V2 không phải bản nâng cấp trực tiếp vì dùng code, evaluation
> và cấu hình khác.
>
> V3 là engine Python được thiết kế lại theo module. V3 sửa terminal handling,
> xử lý nước thoát chiếu trong quiescence, đưa các tối ưu search phù hợp từ Wukong
> vào và mở rộng evaluation để hiểu chân Mã, hoạt động Xe/Pháo và an toàn Tướng.
> Đánh đổi là evaluation V3 chậm hơn, nên nhóm dùng cache Zobrist và xác định rằng
> cần benchmark A/B nhiều ván trước khi kết luận sức mạnh thực chiến.

## Kết luận

Sự tiến hóa quan trọng nhất không phải là số lượng thuật toán:

```text
V1: xây được nền tảng đúng và dễ hiểu
V2: học được cách tối ưu search từ một engine độc lập
V3: làm chủ engine Python, sửa terminal handling và bổ sung hiểu biết cờ tướng
```

V3 là phiên bản có kiến trúc và khả năng biểu diễn thế cờ tiên tiến nhất trong dự
án hiện tại. Tuy nhiên, kết luận về sức mạnh cuối cùng phải dựa trên benchmark nhiều
ván, cùng thời gian, đổi màu cân bằng và có thống kê rõ ràng.
