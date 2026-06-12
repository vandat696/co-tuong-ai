# Các engine AI cờ tướng

Tài liệu này mô tả các engine thực sự đang có trong dự án, cách chúng hoạt động và
vai trò của từng thuật toán.

## Danh sách engine

Hiện tại dự án có hai implementation AI độc lập:

| Engine | Vai trò | Mã nguồn |
| --- | --- | --- |
| V1 - Minimax Alpha-Beta | Engine chính của dự án | `backend/src/ai_engine.py`, `backend/src/eval.py` |
| V2 - WukongJS Negamax | Đối thủ độc lập để quan sát và so sánh | `backend/references/wukong/wukong.js` |

WukongJS không phải phiên bản tiếp theo của AI Python. Hai engine có cách cài đặt,
thuật toán và hàm đánh giá riêng.

## Luồng hoạt động chung

Khi frontend yêu cầu một nước đi:

1. Frontend gửi bàn cờ, bên đến lượt và ID engine tới `POST /move`.
2. `backend/api.py` đọc cấu hình trong `AI_VERSIONS`.
3. Trường `runner` quyết định chạy AI Python hay WukongJS.
4. Engine tìm nước đi tốt nhất trong giới hạn cấu hình.
5. Backend kiểm tra nước đi, cập nhật trạng thái và trả kết quả cho frontend.

Backend Python là nguồn luật chính thức qua các endpoint:

- `POST /legal-moves`: lấy các nước hợp lệ của một quân.
- `POST /validate-move`: kiểm tra một nước mà không thực hiện.
- `POST /apply-move`: xác nhận và thực hiện nước người chơi.
- `POST /ai-move` hoặc alias tương thích `POST /move`: lấy và xác nhận nước do AI đề xuất.

Frontend không còn chứa bộ sinh nước đi riêng. Nó chỉ hiển thị các nước do backend
Python trả về và áp dụng nước sau khi backend xác nhận.

```text
Frontend
   |
   | POST /move + ai_version
   v
backend/api.py
   |
   +-- runner=python --> AIEngine.get_best_move()
   |
   +-- runner=wukong --> Node bridge --> WukongJS.search()
```

## V1 - Minimax Alpha-Beta

### Cấu trúc

- `board.py`: lưu bàn cờ, thực hiện/hoàn tác nước đi, lịch sử và bộ đếm hòa.
- `move_gen.py`: sinh nước đi cho từng loại quân.
- `ai_engine.py`: tìm kiếm nước đi tốt nhất.
- `eval.py`: đánh giá điểm của thế cờ.

### Minimax

AI coi Đỏ là bên tối đa hóa điểm và Đen là bên tối thiểu hóa điểm.

```text
Đỏ: chọn nước có điểm lớn nhất
Đen: chọn nước có điểm nhỏ nhất
```

Engine thử một nước đi, tìm kiếm các câu trả lời của đối thủ, sau đó hoàn tác nước
đi để thử nhánh tiếp theo.

### Alpha-Beta Pruning

Alpha-Beta bỏ qua các nhánh không thể thay đổi quyết định cuối cùng:

- `alpha`: điểm tốt nhất Đỏ đã đảm bảo được.
- `beta`: điểm tốt nhất Đen đã đảm bảo được.
- Khi `beta <= alpha`, nhánh còn lại được cắt bỏ.

Thuật toán cho kết quả tương đương Minimax đầy đủ nhưng thường duyệt ít trạng thái
hơn đáng kể.

### Iterative Deepening

Engine tìm lần lượt từ độ sâu 1 đến `max_depth`:

```text
depth 1 -> depth 2 -> depth 3 -> ...
```

Nếu hết thời gian giữa một vòng tìm kiếm, engine dùng kết quả hoàn chỉnh của độ sâu
trước đó. Nước tốt nhất của vòng trước cũng được ưu tiên duyệt trước ở vòng sau.

### Move Ordering

Các nước triển vọng được tìm trước để Alpha-Beta cắt tỉa hiệu quả hơn:

1. Nước tốt nhất lấy từ bảng chuyển vị hoặc vòng tìm kiếm trước.
2. Nước bắt quân, ưu tiên bắt quân giá trị cao bằng quân giá trị thấp.
3. Các nước thông thường.

Quy tắc ưu tiên nước bắt quân sử dụng MVV-LVA:
`Most Valuable Victim - Least Valuable Attacker`.

### Transposition Table

Nhiều chuỗi nước đi có thể dẫn tới cùng một thế cờ. Bảng chuyển vị lưu kết quả đã
tìm để tránh tính lại:

- Khóa: bàn cờ và bên đến lượt.
- Giá trị: độ sâu, điểm, loại biên và nước tốt nhất.
- Loại biên: `EXACT`, `LOWERBOUND`, `UPPERBOUND`.

Hiện tại bảng được xóa trước mỗi lượt AI để giới hạn bộ nhớ.

### Quiescence Search

Nếu dừng tìm kiếm ngay ở một thế đang có chuỗi ăn quân, điểm đánh giá có thể sai do
`horizon effect`. Vì vậy tại độ sâu 0, engine tiếp tục tìm các nước bắt quân cho
đến khi thế cờ ổn định hơn rồi mới dùng hàm đánh giá.

### Điều kiện kết thúc trong tìm kiếm

- Một bên mất Tướng: thắng hoặc thua.
- Không còn nước đi: bên đến lượt thua.
- Bộ đếm không bắt quân/không đi Tốt đạt 120 nửa nước: hòa.
- Nước đi tạo lại cùng một thế cờ lần thứ ba bị cấm; bên đi phải chọn nước khác.
- Hết giới hạn thời gian: dừng vòng tìm kiếm hiện tại.

### Hàm đánh giá Tapered Evaluation

Điểm dương có lợi cho Đỏ; điểm âm có lợi cho Đen.

Mỗi quân có:

- Giá trị vật chất ở khai/trung cuộc (`MG_PIECE_VALUES`).
- Giá trị vật chất ở tàn cuộc (`EG_PIECE_VALUES`).
- Bảng điểm vị trí (`Piece-Square Table`, viết tắt PST).

Ví dụ:

- Xe có giá trị cao ở cả hai giai đoạn.
- Mã được tăng giá trị trong tàn cuộc.
- Pháo giảm giá trị trong tàn cuộc vì thường thiếu quân làm ngòi.
- Tốt tăng giá trị khi vào tàn cuộc.

Engine tính `phase` dựa trên số quân lớn còn lại, sau đó nội suy:

```text
score = (MG_score * phase + EG_score * (16 - phase)) / 16
```

Điểm đánh giá được cập nhật gia tăng khi đi và hoàn tác nước, thay vì quét lại toàn
bộ bàn cờ tại mọi nút.

## V2 - WukongJS Negamax

WukongJS là engine JavaScript độc lập. Backend chuyển bàn cờ Python sang FEN rồi
gọi engine thông qua `backend/references/wukong/bridge.js`.

### Thuật toán tìm kiếm

Wukong dùng Negamax, một cách viết gọn của Minimax cho trò chơi đối kháng. Nó còn
có nhiều kỹ thuật tối ưu nâng cao:

- Alpha-Beta Pruning.
- Iterative Deepening.
- Transposition Table bằng hash.
- Quiescence Search.
- Principal Variation Search (PVS).
- Null Move Pruning.
- Futility Pruning.
- Late Move Reduction (LMR).
- Razoring và check extension.
- Killer moves và sắp xếp nước đi.

Các kỹ thuật này giúp Wukong bỏ qua hoặc giảm độ sâu ở những nhánh ít triển vọng,
để tìm sâu hơn trong cùng lượng tài nguyên.

### Hàm đánh giá

Wukong đánh giá bằng:

- Giá trị vật chất của quân.
- Bảng điểm vị trí PST.

Các trọng số trong mã Wukong được ghi chú là lấy từ tài liệu nghiên cứu về cờ
tướng. Không giống AI Python, Wukong hiện không dùng Tapered Evaluation tách riêng
khai/trung cuộc và tàn cuộc.

## So sánh hai engine

| Đặc điểm | V1 - Minimax Alpha-Beta | V2 - WukongJS Negamax |
| --- | --- | --- |
| Kiểu tìm kiếm | Minimax | Negamax |
| Alpha-Beta | Có | Có |
| Iterative Deepening | Có | Có |
| Transposition Table | Có | Có |
| Quiescence Search | Có | Có |
| Null Move / Futility / LMR / PVS | Chưa có | Có |
| Hàm đánh giá | Tapered material + PST | Material + PST |
| Vai trò | Engine chính để phát triển | Engine đối chiếu độc lập |

Không nên kết luận engine mạnh hơn chỉ dựa vào số lượng thuật toán. Độ chính xác
luật chơi, chất lượng hàm đánh giá, move ordering và hiệu năng implementation đều
ảnh hưởng lớn tới kết quả.

## Cách thêm phiên bản AI mới

Một phiên bản mới chỉ nên được thêm khi có implementation hoặc cấu hình có ý nghĩa
thực sự. Thêm metadata vào `AI_VERSIONS` trong `backend/api.py`:

```python
"python_next": {
    "id": "python_next",
    "order": 3,
    "name": "AI Python tiếp theo",
    "description": "Mô tả thay đổi chính.",
    "engine": "Python",
    "runner": "python",
    "search": "Các thuật toán tìm kiếm.",
    "evaluation": "Cách đánh giá thế cờ.",
    "max_depth": 7,
    "time_limit": 1.0,
}
```

Nếu phiên bản chỉ thay đổi tên nhưng vẫn chạy cùng code và cùng cấu hình, không nên
coi nó là một phiên bản AI riêng.

## Hạn chế hiện tại

- Trạng thái ván hiện vẫn được frontend gửi kèm mỗi request; backend chưa lưu session ván đấu.
- Chưa có hệ thống đấu hàng trăm ván và tính Elo.
- Chưa lưu thống kê nodes, nodes/second, độ sâu hoàn thành hoặc số lần trúng TT.
- AI Python chưa có giao diện UCI.
- Source code lịch sử của các phiên bản Python cũ chưa được lưu riêng.
