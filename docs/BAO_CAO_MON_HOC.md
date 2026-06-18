# BÁO CÁO PROJECT MÔN TRÍ TUỆ NHÂN TẠO

## Xây dựng và đánh giá hệ thống AI chơi Cờ Tướng

## 1. Tóm tắt

Project xây dựng một hệ thống chơi Cờ Tướng hoàn chỉnh gồm luật chơi, giao diện,
API và nhiều phiên bản AI. Phương pháp Trí tuệ nhân tạo chính được lựa chọn là
**tìm kiếm đối kháng Minimax/Negamax kết hợp Alpha-Beta Pruning và hàm đánh giá
heuristic**. Project đồng thời thử nghiệm **mạng neural NNUE** để thay thế hàm
đánh giá thủ công.

Quá trình phát triển tạo ra bốn engine:

- V1: Minimax Alpha-Beta làm baseline.
- V2: WukongJS Negamax làm đối thủ tham chiếu.
- V3: Mate-Aware Negamax, evaluator lai và opening book.
- V4: Search V3 kết hợp NNUE lượng tử hóa.

Thực nghiệm cho thấy V3 có chất lượng đánh giá mỗi node tốt hơn V2 trong các
phép thử cùng độ sâu 3-4. Tuy nhiên, khi cấp cùng thời gian, V2 vẫn mạnh hơn vì
tốc độ thực thi cao và đạt độ sâu lớn hơn. Kết quả minh họa rõ đánh đổi cơ bản
trong AI tìm kiếm đối kháng: **chất lượng đánh giá mỗi trạng thái và số trạng
thái có thể tìm kiếm**.

## 2. Bài toán và mục tiêu

Cờ Tướng là trò chơi đối kháng hai người, tổng bằng không, thông tin hoàn hảo và
có không gian trạng thái lớn. Một AI chơi cờ cần giải quyết:

1. Biểu diễn bàn cờ và luật di chuyển.
2. Sinh nước đi hợp lệ, phát hiện chiếu và chiếu hết.
3. Dự đoán phản ứng tối ưu của đối thủ.
4. Đánh giá các thế cờ chưa thể tìm đến kết thúc.
5. Trả nước đi trong giới hạn thời gian thực tế.

Mục tiêu project:

- Xây dựng ứng dụng Cờ Tướng có thể chơi Người-AI và AI-AI.
- Minh họa và so sánh các phương pháp tìm kiếm đối kháng đã học.
- Phát triển nhiều phiên bản AI để phân tích ảnh hưởng của search và evaluation.
- Thử nghiệm tích hợp Machine Learning bằng NNUE.
- Đánh giá kết quả bằng test, benchmark và đấu đối kháng.

## 3. Phương pháp Trí tuệ nhân tạo lựa chọn

### 3.1 Minimax và Negamax

Minimax giả định cả hai bên đều chọn nước tối ưu:

```text
Đỏ chọn giá trị lớn nhất.
Đen chọn giá trị nhỏ nhất.
```

Negamax sử dụng tính chất trò chơi tổng bằng không:

```text
score(position, side) = -score(position, opponent)
```

Negamax không làm thay đổi kết quả lý thuyết của Minimax, nhưng giúp code đối
xứng và dễ tích hợp PVS, LMR, Null Move và các kỹ thuật search nâng cao.

### 3.2 Alpha-Beta Pruning

Alpha-Beta loại bỏ các nhánh không thể ảnh hưởng đến quyết định cuối cùng:

- `alpha`: kết quả tốt nhất bên đang tối đa hóa đã đảm bảo.
- `beta`: giới hạn mà đối thủ có thể chấp nhận.
- Khi `alpha >= beta`, các nhánh còn lại được cắt bỏ.

Theo lý thuyết, Alpha-Beta cho cùng kết quả với Minimax đầy đủ nhưng có thể giảm
độ phức tạp từ gần `O(b^d)` xuống gần `O(b^(d/2))` khi move ordering tốt.

### 3.3 Iterative Deepening và quản lý thời gian

Engine lần lượt tìm depth 1, 2, 3,... và giữ kết quả hoàn thành gần nhất. Cách
này bảo đảm AI luôn có nước trả về khi hết thời gian, đồng thời dùng kết quả
depth trước để sắp xếp nước cho depth sau.

### 3.4 Hàm đánh giá heuristic

Khi chưa thể tìm đến kết thúc ván, engine dùng:

```text
evaluation = material + điểm vị trí + đặc trưng động
```

V1 và V3 sử dụng Tapered Evaluation:

```text
score = (MG_score * phase + EG_score * (16 - phase)) / 16
```

Trong đó `MG` đại diện khai/trung cuộc, `EG` đại diện tàn cuộc. Điểm được cập
nhật gia tăng sau mỗi nước đi để giảm chi phí tại node lá.

### 3.5 Các kỹ thuật search nâng cao

V3 triển khai:

- Zobrist Hashing và Transposition Table.
- Principal Variation Search và Aspiration Window.
- Killer Move, History Heuristic và MVV-LVA.
- Late Move Reduction.
- Null Move, Futility, Razoring và Reverse Futility.
- Quiescence Search xử lý cả nước thoát chiếu.
- Check extension và mate-distance score.

Các kỹ thuật này minh họa khái niệm **heuristic search**: ưu tiên hoặc giảm công
sức ở các nhánh dựa trên kỳ vọng, thay vì duyệt toàn bộ cây.

### 3.6 NNUE

V4 thử nghiệm Efficiently Updatable Neural Network:

```text
Sparse piece-square features
    -> hidden layer 128 unit
    -> scalar evaluation
```

Khi một quân di chuyển, accumulator chỉ trừ feature cũ và cộng feature mới,
không tính lại toàn bộ lớp đầu vào. Trọng số runtime được lượng tử hóa sang số
nguyên để tăng tốc.

Model hiện tại được train để dự đoán điểm heuristic V3 từ dữ liệu ván đấu
Kaggle. Vì vậy V4 minh họa được quy trình Machine Learning và inference gia
tăng, nhưng chưa phải hệ thống tự học hoàn chỉnh từ kết quả thắng/thua.

## 4. Kiến trúc hệ thống

```text
React/Vite Frontend
        |
        | HTTP JSON
        v
FastAPI Backend
        |
        +-- Luật chơi và kiểm tra nước đi
        +-- V1 Python
        +-- V2 WukongJS qua Node bridge
        +-- V3 Python
        +-- V4 Python + NNUE
```

Backend là nguồn luật chính thức. Frontend gửi trạng thái bàn cờ, bên đến lượt,
lịch sử và cấu hình AI. Backend sinh hoặc kiểm tra nước đi, chạy engine, kiểm
tra lại kết quả rồi trả trạng thái mới.

## 5. Các thành phẩm đã thực hiện

### 5.1 Ứng dụng chơi Cờ Tướng

- Bàn cờ tương tác 10x9 bằng React.
- Người chơi có thể chọn quân và xem nước hợp lệ.
- Hỗ trợ Người-AI, AI-Người và AI-AI.
- Chọn riêng engine cho bên Đỏ và bên Đen.
- Điều chỉnh thời gian suy nghĩ và độ sâu tối đa.
- Hiển thị lịch sử nước đi, thời gian, depth, nodes và điểm đánh giá.
- Hiển thị trạng thái chiếu, chiếu hết và bên thắng.

### 5.2 Backend luật chơi và API

Các endpoint chính:

| Endpoint | Chức năng |
| --- | --- |
| `GET /ai-versions` | Danh sách và mô tả các engine |
| `POST /legal-moves` | Lấy nước hợp lệ của một quân |
| `POST /validate-move` | Kiểm tra nước người chơi |
| `POST /apply-move` | Áp dụng nước người chơi |
| `POST /move`, `/ai-move` | Yêu cầu AI tìm nước |

Hệ thống xử lý chiếu, chiếu hết, chống Tướng, lặp thế lần ba và luật hòa 120
half-move.

### 5.3 Bốn engine AI

| Engine | Thành phẩm minh họa |
| --- | --- |
| V1 | Baseline Minimax Alpha-Beta và tapered evaluation |
| V2 | Engine tham chiếu WukongJS, search nhanh |
| V3 | Search Python module hóa, mate-aware, evaluator lai và opening book |
| V4 | Search V3 kết hợp NNUE accumulator lượng tử hóa |

### 5.4 Opening book

V3/V4 có tập ứng viên khai cuộc gồm Pháo đầu, phát triển Mã, tiến Tốt cánh và
Bình phong Mã. Search vẫn lựa chọn giữa các ứng viên; book không ép cứng duy
nhất một nước.

### 5.5 Pipeline Machine Learning

- Dataset ván đấu Kaggle và dữ liệu đã chuyển đổi.
- Script parse/chuyển dữ liệu thành feature NNUE.
- Mô hình PyTorch `XiangqiNNUE`.
- Script training và validation.
- Script lượng tử hóa/export model.
- Model runtime `ml/models/xiangqi.nnue`.
- Inference accumulator cập nhật gia tăng trong search.

### 5.6 Test và benchmark

- 27 test cho search, mate, quiescence, Zobrist, TT, move ordering, evaluation,
  opening book và push/pop state.
- Benchmark cùng thời gian V2/V3.
- Benchmark tốc độ V3/V4.
- Đấu đối kháng nhiều cấu hình depth, thời gian và khai cuộc.

## 6. Kết quả thực nghiệm

### 6.1 V3 so với V2 khi cùng độ sâu

Mỗi cấu hình gồm ba hệ khai cuộc và đổi màu, tổng cộng sáu ván:

| V3 depth | V2 depth | V3 thắng - V2 thắng - hòa |
| ---: | ---: | ---: |
| 3 | 3 | `4-0-2` |
| 4 | 4 | `1-0-5` |
| 3 | 4 | `1-0-5` |
| 4 | 5 | `1-0-5` |
| 3 | 5 | `0-0-6` |
| 4 | 6 | `0-0-6` |

V3 thể hiện lợi thế rõ nhất tại depth 3 và vẫn cạnh tranh khi V2 sâu hơn một
ply. Điều này cho thấy evaluator và terminal handling của V3 cung cấp chất lượng
tốt trên mỗi node.

### 6.2 V3 so với V2 khi cùng thời gian

| Thời gian mỗi nước | Kết quả V3 - V2 - hòa | Depth V3 | Depth V2 |
| ---: | ---: | ---: | ---: |
| `0.1s` | `0-1-5` | `2.3-2.8` | `4.7-5.7` |
| `0.3s` | `0-5-1` | `3.1-3.6` | `6.3-7.9` |

V2 thắng khi cùng thời gian vì thực thi JavaScript/V8 nhanh hơn và đạt độ sâu
lớn hơn V3 từ khoảng 2 đến 4 ply.

Ước lượng hiện tại:

```text
V3 cạnh tranh hoặc mạnh hơn khi V3 depth >= V2 depth - 1.
```

### 6.3 V3 so với V4

V4 chạy được model NNUE và accumulator incremental khớp với full recompute.
Trong các benchmark đã chạy, V4 có thể thắng V3 ở một số ván hoặc cấu hình,
nhưng chưa tạo ưu thế ổn định.

Nguyên nhân:

- Model NNUE chủ yếu học điểm heuristic V3.
- Sai lệch nhỏ của NNUE làm thay đổi move ordering và pruning.
- NNUE hiện chưa học trực tiếp kết quả thắng/thua.
- Pipeline training và feature set còn đơn giản.

## 7. Phân tích kết quả và so sánh với lý thuyết

### 7.1 Alpha-Beta phụ thuộc mạnh vào move ordering

Lý thuyết dự đoán Alpha-Beta đạt hiệu quả cao khi nước tốt được xét trước.
Thực nghiệm phù hợp với lý thuyết: TT move, killer/history, opening book và ưu
tiên nước chiếu làm thay đổi lớn số node và depth hoàn thành.

### 7.2 Depth danh nghĩa không hoàn toàn tương đương

Hai engine cùng depth vẫn có thể duyệt cây khác nhau do:

- Check extension.
- LMR và selective pruning.
- Quiescence khác nhau.
- Move ordering và transposition table khác nhau.

Vì vậy, cùng depth phù hợp để so chất lượng evaluation, còn cùng thời gian phù
hợp hơn để so sức mạnh thực tế.

### 7.3 Tìm sâu hơn và hiểu mỗi trạng thái tốt hơn

Kết quả thể hiện một đánh đổi quan trọng:

```text
V2: đánh giá đơn giản hơn, thực thi nhanh, tìm sâu hơn.
V3: đánh giá và xử lý terminal tốt hơn, nhưng tìm nông hơn khi cùng thời gian.
```

V3 thắng ở cùng depth nhưng thua ở cùng thời gian. Điều này đúng với lý thuyết
rằng sức mạnh engine phụ thuộc đồng thời vào **search depth** và **evaluation
quality**, không chỉ số lượng thuật toán.

### 7.4 Selective pruning không bảo đảm luôn tốt hơn

Null Move, Futility, Razoring và LMR giảm số nhánh nhưng có nguy cơ bỏ sót chiến
thuật. Project bảo vệ nước chiếu, nước bắt quân và trạng thái đang bị chiếu khỏi
một số pruning. Kết quả cho thấy các tham số vẫn cần tuning bằng nhiều ván đấu,
đúng với tính chất heuristic: hiệu quả thực nghiệm quan trọng hơn tính đúng tuyệt
đối.

### 7.5 Machine Learning không tự động mạnh hơn heuristic

NNUE chỉ mạnh khi:

- Feature biểu diễn đủ thông tin.
- Dataset và target có chất lượng.
- Model được train đủ lớn.
- Inference đủ nhanh để không mất độ sâu.

V4 hiện minh họa đúng kỹ thuật NNUE incremental, nhưng do học để bắt chước V3,
nó chưa có cơ sở để vượt xa V3. Kết quả này phù hợp với lý thuyết học có giám
sát: chất lượng mô hình bị giới hạn bởi target và dữ liệu huấn luyện.

## 8. Ý nghĩa thực tế

Project không chỉ tạo một bot chơi cờ mà còn minh họa quy trình xây dựng hệ
thống AI thực tế:

- Chuyển lý thuyết tìm kiếm đối kháng thành phần mềm hoạt động.
- Đánh giá phương pháp bằng test và benchmark thay vì chỉ quan sát cảm tính.
- Nhận biết đánh đổi giữa độ chính xác, tốc độ và tài nguyên.
- Tích hợp nhiều công nghệ: Python, JavaScript, FastAPI, React, PyTorch.
- Xây dựng giao diện giúp người dùng quan sát trực tiếp depth, nodes, thời gian
  và kết quả của từng phương pháp.

Ứng dụng có thể dùng làm công cụ giảng dạy Minimax, Alpha-Beta, heuristic search
và neural evaluation thông qua các ván đấu AI-AI.

## 9. Hạn chế

- Benchmark mới dùng số lượng khai cuộc và số ván nhỏ, chưa đủ tính Elo.
- V3 chậm hơn V2 đáng kể khi cùng thời gian.
- Opening book còn nhỏ.
- Một số tham số evaluator/pruning chưa được tuning tự động.
- V4 chưa phải HalfKP đầy đủ vì feature chưa dùng vị trí Tướng.
- Model NNUE chưa học trực tiếp kết quả thắng/thua.
- Pipeline self-play chưa hoàn thiện.
- API V4 hiện trả điểm giải thích bằng evaluator V3, không phải điểm NNUE.

## 10. Hướng phát triển

1. Xây dựng harness đấu hàng trăm ván và tính Elo/confidence interval.
2. Tối ưu hot path V3 để giảm khoảng cách depth với V2.
3. Tune evaluator và pruning bằng dữ liệu thực nghiệm.
4. Mở rộng opening book từ dữ liệu ván đấu.
5. Hoàn thiện self-play và train NNUE từ kết quả thắng/thua kết hợp evaluation.
6. Chuyển feature NNUE sang HalfKP/HalfKAv2 thực sự.
7. Thêm endgame tablebase cho các tàn cuộc ít quân.

## 11. Kết luận

Project đã hoàn thành một hệ thống Cờ Tướng AI có thể chạy, quan sát và so sánh
nhiều phương pháp Trí tuệ nhân tạo.

Kết quả quan trọng nhất không phải là một engine luôn mạnh nhất, mà là làm rõ
được tính chất của các phương pháp:

- Minimax/Negamax mô hình hóa đối kháng tối ưu.
- Alpha-Beta và heuristic ordering giúp giảm không gian tìm kiếm.
- Evaluation tốt làm tăng chất lượng mỗi node.
- Tốc độ thực thi quyết định độ sâu đạt được.
- Neural network chỉ hiệu quả khi dữ liệu, feature và inference được thiết kế
  phù hợp.

V3 cho thấy cải thiện về chất lượng mỗi node so với V2 ở cùng độ sâu. V2 cho
thấy lợi thế thực tế của implementation nhanh khi cùng thời gian. V4 chứng minh
khả năng tích hợp NNUE nhưng cũng cho thấy Machine Learning cần dữ liệu và quy
trình huấn luyện tốt để tạo sức mạnh vượt trội.

## 12. Minh chứng và demo đề xuất

Trình tự demo ngắn:

1. Mở giao diện và cho người chơi thử một nước hợp lệ.
2. Cho V1 đấu V3 để minh họa các phiên bản AI.
3. Chọn V2 và V3, thay đổi time limit/max depth, quan sát depth và nodes.
4. Cho V3/V4 đấu để minh họa heuristic evaluation và NNUE.
5. Mở lịch sử nước đi để chỉ số thời gian, depth, nodes và evaluation.
6. Trình bày bảng benchmark cùng depth và cùng thời gian.

Các file minh chứng:

| Nội dung | File |
| --- | --- |
| API và lựa chọn engine | `backend/api.py` |
| V1 | `backend/engines/v1/` |
| V2 | `backend/engines/v2_wukong/` |
| V3 search | `backend/engines/v3/engine.py` |
| V3 evaluation/hot path | `backend/engines/v3/position.py` |
| Opening book | `backend/engines/v3/opening.py` |
| V4 NNUE | `backend/engines/v4/engine_v4.py`, `backend/engines/v3/accumulator.py` |
| Training NNUE | `backend/ml/` |
| Frontend đấu trường | `frontend/src/components/ArenaPanel.jsx` |
| Test | `backend/tests/` |
| Benchmark | `backend/benchmarks/`, `docs/V2_V3_BENCHMARK_RESULTS.md` |
