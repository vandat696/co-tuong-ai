# Các engine AI cờ tướng

Tài liệu này mô tả các engine thực sự đang có trong dự án, cách chúng hoạt động và
vai trò của từng thuật toán.

## Danh sách engine

Hiện tại dự án có ba implementation AI:

| Engine | Vai trò | Mã nguồn |
| --- | --- | --- |
| V1 - Minimax Alpha-Beta | Engine chính của dự án | `backend/src/ai_engine.py`, `backend/src/eval.py` |
| V2 - WukongJS Negamax | Đối thủ độc lập để quan sát và so sánh | `backend/references/wukong/wukong.js` |
| V3 - Mate-Aware Negamax | Engine Python xử lý chuỗi chiếu và chiếu hết | `backend/src/engine_v3/` |

WukongJS không phải phiên bản tiếp theo của AI Python. Nó có cách cài đặt, thuật
toán và hàm đánh giá độc lập với các engine Python.

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
   +-- runner=python_v3 --> AIEngineV3.get_best_move()
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

## V3 - Mate-Aware Negamax

V3 giữ V1 nguyên trạng để có thể đấu A/B, nhưng tổ chức search thành package riêng:

- `engine_v3/engine.py`: iterative deepening, Negamax, Alpha-Beta, TT và quiescence.
- `engine_v3/context.py`: sinh nước, đi/hoàn tác, timeout và chuyển điểm theo bên đến lượt.

V3 kiểm tra trạng thái kết thúc trước khi đánh giá tĩnh. Trong quiescence, nếu bên
đến lượt đang bị chiếu, engine tìm tất cả nước thoát chiếu thay vì chỉ tìm nước ăn
quân. Check extension giúp theo chuỗi chiếu sâu hơn, còn mate-distance score giúp
ưu tiên chiếu hết nhanh và trì hoãn bị chiếu hết.

### Hàm đánh giá V3

V3 giữ tapered material/PST của V1 làm nền và bổ sung các feature động:

- Mobility của Mã, Pháo và Xe.
- Phạt Mã theo số chân bị chặn.
- Thưởng Xe xâm nhập sang phần bàn đối phương.
- Thưởng Pháo có ngòi gây áp lực lên quân hoặc Tướng.
- King Safety dựa trên Sĩ/Tượng gần Tướng, quân tấn công quanh cung và trạng thái bị chiếu.

Mỗi feature trả về điểm MG/EG riêng rồi được nội suy theo phase. Mã nguồn nằm trong
`backend/src/engine_v3/evaluation/`; `EvaluatorV3.evaluate_breakdown()` trả breakdown
để test và điều chỉnh trọng số. Vì feature động phải quét quan hệ giữa các quân nên
đắt hơn evaluator V1; V3 dùng cache theo Zobrist để tránh tính lại cùng một thế.

Các tối ưu tìm kiếm lấy ý tưởng từ Wukong đã được đưa vào V3:

- Zobrist Hashing gia tăng và TT giới hạn kích thước.
- Killer Move, History Heuristic, TT move và MVV-LVA.
- Aspiration Windows và Principal Variation Search.
- Late Move Reduction.
- Null Move, Futility Pruning, Razoring và reverse futility pruning.

Selective pruning chỉ chạy khi bên đến lượt không bị chiếu. Nước ăn quân và nước
chiếu cũng được bảo vệ khỏi Futility Pruning và LMR.

## So sánh các engine

| Đặc điểm | V1 - Minimax Alpha-Beta | V2 - WukongJS Negamax | V3 - Mate-Aware Negamax |
| --- | --- | --- | --- |
| Kiểu tìm kiếm | Minimax | Negamax | Negamax |
| Alpha-Beta | Có | Có | Có |
| Iterative Deepening | Có | Có | Có |
| Transposition Table | Có | Có | Có |
| Zobrist Hashing | Chưa có | Có | Có |
| Quiescence Search | Chỉ nước ăn quân | Chỉ nước ăn quân | Xử lý cả nước thoát chiếu |
| Check extension | Chưa có | Có | Có |
| Mate-distance score | Chưa có | Có | Có |
| Killer Move / History | Chưa có | Có | Có |
| Aspiration Windows | Chưa có | Chưa có | Có |
| Null Move / Futility / LMR / PVS | Chưa có | Có | Có |
| Razoring / Reverse Futility | Chưa có | Có | Có |
| Hàm đánh giá | Tapered material + PST | Material + PST | Tapered material/PST + activity + King Safety |
| Vai trò | Baseline Python | Engine đối chiếu độc lập | Engine Python xử lý chiếu hết |

Không nên kết luận engine mạnh hơn chỉ dựa vào số lượng thuật toán. Độ chính xác
luật chơi, chất lượng hàm đánh giá, move ordering và hiệu năng implementation đều
ảnh hưởng lớn tới kết quả.

## Các hướng cải tiến AI, giải thích dễ hiểu

Phần này mô tả các kỹ thuật có thể dùng để phát triển những phiên bản AI tiếp theo.
Mỗi kỹ thuật cần trả lời bốn câu hỏi:

1. Vấn đề hiện tại là gì?
2. Kỹ thuật giải quyết vấn đề đó như thế nào?
3. Nó có thể gây lỗi hoặc làm AI yếu đi trong trường hợp nào?
4. Làm sao kiểm chứng nó thực sự tốt hơn?

### Negamax: làm code đối xứng, không làm AI tự mạnh hơn

Minimax hiện tại viết hai nhánh riêng:

```text
Đỏ chọn điểm lớn nhất
Đen chọn điểm nhỏ nhất
```

Negamax dựa trên tính chất trò chơi tổng bằng không:

```text
Điểm tốt cho mình = điểm xấu cho đối thủ
```

Thay vì viết cả `max` và `min`, Negamax luôn chọn điểm lớn nhất rồi đổi dấu điểm
khi chuyển lượt:

```text
score = -negamax(thế_cờ_sau_nước_đi)
```

Nếu dùng cùng độ sâu, cùng hàm đánh giá và cùng thứ tự nước, Minimax và Negamax cho
kết quả tương đương. Lợi ích chính của Negamax là code ngắn, đối xứng và dễ bổ sung
PVS, LMR hoặc Null Move hơn.

**Có nên tạo phiên bản mới?** Không nên coi việc chỉ đổi Minimax thành Negamax là
một phiên bản mạnh hơn. Đây chủ yếu là refactor kiến trúc tìm kiếm.

### Zobrist Hashing: tạo khóa thế cờ nhanh hơn

AI Python hiện dùng chuỗi toàn bộ bàn cờ làm khóa bảng chuyển vị. Cách này dễ hiểu
nhưng phải tạo và xử lý một chuỗi lớn tại rất nhiều nút tìm kiếm.

Zobrist Hashing gán một số ngẫu nhiên cố định cho mỗi cặp:

```text
(quân cờ, vị trí)
```

Hash của thế cờ là phép XOR các số tương ứng. Khi một quân di chuyển, chỉ cần XOR
bỏ vị trí cũ và XOR thêm vị trí mới, thay vì quét lại toàn bàn.

**Lợi ích:** tăng tốc bảng chuyển vị, kiểm tra lặp và undo.

**Rủi ro:** có xác suất va chạm hash rất nhỏ; cần đưa cả bên đến lượt vào hash.

**Đo lường:** nodes/second, thời gian mỗi độ sâu và tỷ lệ trúng bảng chuyển vị.

### Transposition Table bền vững hơn

Bảng chuyển vị hiện bị xóa trước mỗi lượt AI. Điều này đơn giản và tránh tăng bộ
nhớ, nhưng mất các kết quả hữu ích từ lượt trước.

Cải tiến có thể gồm:

- Dùng Zobrist hash làm khóa.
- Đặt giới hạn dung lượng cố định.
- Lưu `generation` để ưu tiên dữ liệu mới.
- Chính sách thay thế ưu tiên entry có độ sâu lớn hơn.
- Giữ bảng giữa các lượt.

**Lợi ích:** giảm tìm lại các thế cờ quen thuộc.

**Rủi ro:** dùng entry cũ sai điều kiện hoặc lưu sai loại biên có thể làm AI chọn
nước sai.

### Principal Variation Search (PVS)

Sau khi move ordering tốt, nước đầu tiên thường là nước tốt nhất. PVS tìm nước đầu
tiên với cửa sổ Alpha-Beta đầy đủ, còn các nước sau được thử bằng cửa sổ rất hẹp:

```text
[alpha, alpha + 1]
```

Nếu nước sau không vượt qua alpha, engine biết nó không tốt hơn và tiết kiệm được
nhiều tìm kiếm. Nếu nó bất ngờ tốt hơn, engine tìm lại bằng cửa sổ đầy đủ.

**Ví dụ trực giác:** phỏng vấn kỹ ứng viên đầu tiên rất mạnh; với ứng viên sau chỉ
kiểm tra nhanh xem họ có vượt ứng viên tốt nhất không.

**Điều kiện:** chỉ hiệu quả khi move ordering đã tốt.

**Rủi ro:** move ordering kém khiến phải tìm lại nhiều lần và chậm hơn.

### Aspiration Windows

Khi đào sâu lặp từ depth `n` lên `n + 1`, điểm thường không thay đổi quá lớn.
Thay vì bắt đầu Alpha-Beta bằng cửa sổ vô hạn, engine tìm quanh điểm vòng trước:

```text
[điểm_cũ - biên, điểm_cũ + biên]
```

Cửa sổ hẹp giúp cắt tỉa mạnh hơn. Nếu điểm thật nằm ngoài cửa sổ, engine mở rộng
và tìm lại.

**Rủi ro:** vị trí chiến thuật làm điểm thay đổi lớn sẽ gây nhiều lần tìm lại.

### Killer Move Heuristic

Một nước không bắt quân nhưng gây beta cutoff ở một nhánh thường cũng mạnh trong
các nhánh khác cùng độ sâu. Engine lưu một vài `killer move` cho mỗi ply và ưu tiên
chúng trong move ordering.

**Ví dụ:** một nước chiếu hoặc đe dọa mạnh thường buộc đối thủ phản ứng trong nhiều
thế cờ tương tự.

**Lợi ích:** Alpha-Beta cắt sớm hơn.

**Rủi ro:** killer move chỉ nên ưu tiên, không được mặc định là nước hợp lệ hoặc tốt.

### History Heuristic

History Heuristic chấm điểm các nước yên lặng từng gây cutoff trong quá khứ:

```text
history[from][to] += depth * depth
```

Các nước có điểm history cao được tìm trước. Khác với Killer Move lưu theo ply,
History Heuristic học xu hướng hiệu quả của một nước trên nhiều nhánh.

**Lợi ích:** cải thiện thứ tự nước không bắt quân.

**Rủi ro:** cần giảm hoặc làm già điểm định kỳ để dữ liệu cũ không thống trị.

### Null Move Pruning

Null Move dựa trên giả định:

> Nếu một bên bỏ lượt mà vị trí vẫn đủ tốt để vượt beta, thì khi được đi thật vị
> trí đó rất có thể cũng đủ tốt.

Engine tạm bỏ lượt, giảm độ sâu và tìm nhanh. Nếu kết quả vẫn vượt beta, nhánh được
cắt bỏ.

**Lợi ích:** cắt rất mạnh ở các vị trí một bên đang vượt trội.

**Rủi ro quan trọng:** sai trong zugzwang, nơi bắt buộc phải đi lại làm vị trí xấu
đi. Cần tắt hoặc xác minh Null Move trong tàn cuộc ít quân, khi đang bị chiếu và
các vị trí nhạy cảm.

### Futility Pruning

Ở gần lá cây, nếu đánh giá tĩnh cộng với một biên an toàn vẫn không thể vượt alpha,
engine có thể bỏ qua một số nước yên lặng.

```text
static_eval + margin <= alpha
```

**Ví dụ:** đang kém rất xa ở depth thấp; một nước đi yên lặng khó có thể đảo ngược
kết quả ngay lập tức.

**Không được áp dụng tùy tiện cho:** nước chiếu, nước bắt quân, nước phong cấp
(nếu có), hoặc vị trí chiến thuật.

### Razoring

Razoring cũng dùng đánh giá tĩnh ở độ sâu thấp. Nếu vị trí kém hơn alpha rất nhiều,
engine chuyển sớm sang Quiescence Search thay vì tìm đầy đủ.

**Lợi ích:** giảm thời gian ở các nhánh rất kém.

**Rủi ro:** có thể bỏ lỡ chiến thuật yên lặng; cần biên an toàn và chỉ dùng ở depth
thấp.

### Late Move Reduction (LMR)

Sau khi move ordering tốt, các nước ở cuối danh sách thường ít triển vọng. LMR tìm
chúng với độ sâu giảm:

```text
nước đầu: tìm đầy đủ
nước muộn, yên lặng: giảm 1-2 ply
```

Nếu kết quả giảm sâu bất ngờ vượt alpha, engine tìm lại ở độ sâu đầy đủ.

**Lợi ích:** cho phép tập trung tài nguyên vào các nước triển vọng và tăng độ sâu
tổng thể.

**Không nên giảm:** nước chiếu, nước bắt quân, nước PV, killer move hoặc khi đang
bị chiếu.

**Rủi ro:** giảm quá mạnh có thể bỏ lỡ một nước yên lặng rất tốt.

### Check Extension

Khi một bên đang bị chiếu, vị trí có tính bắt buộc cao và nguy hiểm. Engine có thể
tăng thêm một ply để nhìn rõ chuỗi phản ứng.

**Lợi ích:** giảm bỏ sót chiếu hết hoặc đòn chiến thuật liên quan đến Tướng.

**Rủi ro:** chuỗi chiếu dài có thể làm cây tìm kiếm phình mạnh; cần giới hạn tổng
số extension.

### Delta Pruning trong Quiescence Search

Quiescence Search hiện duyệt các nước bắt quân. Delta Pruning bỏ qua một nước bắt
quân nếu ngay cả giá trị quân bắt được cộng đánh giá hiện tại vẫn không thể cải
thiện alpha.

**Lợi ích:** giảm cây tìm kiếm tĩnh.

**Rủi ro:** không nên áp dụng gần chiếu hết hoặc cho các nước có yếu tố chiến thuật
đặc biệt.

### Static Exchange Evaluation (SEE)

Không phải mọi nước bắt quân đều tốt. SEE ước lượng chuỗi đổi quân trên một ô mà
không cần tìm toàn bộ cây:

```text
Xe ăn Tốt, nhưng sau đó Xe bị bắt -> có thể là trao đổi lỗ
```

SEE giúp:

- Sắp xếp nước bắt quân tốt hơn MVV-LVA.
- Bỏ bớt nước bắt quân thua vật chất trong Quiescence Search.

**Rủi ro:** cờ tướng có Pháo, chân Mã và nhiều quan hệ chặn đặc biệt; SEE cần được
thiết kế đúng luật cờ tướng, không thể bê nguyên từ cờ vua.

## Thiết kế và cải tiến hàm đánh giá

Thuật toán tìm kiếm trả lời câu hỏi **AI có thể nhìn xa bao nhiêu nước**. Hàm đánh
giá trả lời câu hỏi **AI hiểu thế cờ đang nhìn thấy tốt đến đâu**.

Ví dụ, Alpha-Beta có thể giúp AI tìm đến độ sâu lớn hơn. Tuy nhiên, nếu hàm đánh giá
chỉ đếm giá trị quân, AI vẫn có thể đổi một quân lấy thế bị chiếu bí hoặc tự nhốt
Xe, Mã vào vị trí xấu. Vì vậy, mỗi phiên bản AI nên ghi rõ cả:

- Kỹ thuật tìm kiếm đang dùng.
- Các thành phần của hàm đánh giá đang dùng.
- Trọng số của từng thành phần.

### Hàm đánh giá hiện tại hiểu những gì?

AI Python hiện tính điểm theo công thức gần đúng:

```text
MG = tổng(giá trị quân MG + điểm vị trí MG)
EG = tổng(giá trị quân EG + điểm vị trí EG)

điểm cuối = (MG * phase + EG * (16 - phase)) / 16
```

Trong đó:

- `MG` là điểm khai cuộc và trung cuộc.
- `EG` là điểm tàn cuộc.
- `phase` được tính từ số Xe, Mã và Pháo còn trên bàn.
- Điểm dương có lợi cho Đỏ, điểm âm có lợi cho Đen.
- Điểm vật chất và PST được cập nhật gia tăng sau mỗi nước đi nên đánh giá rất nhanh.

AI hiện đã biết:

- Giá trị vật chất của từng loại quân.
- Mã và Tốt thường mạnh hơn trong tàn cuộc.
- Pháo thường giảm giá trị khi ít quân làm ngòi.
- Vị trí tốt/xấu cơ bản của Tướng, Tốt, Mã, Pháo và Xe thông qua PST.

AI hiện chưa trực tiếp biết:

- Một quân có bao nhiêu ô hoạt động.
- Tướng đang được bảo vệ tốt hay sắp bị tấn công.
- Mã có bị chặn chân hay không.
- Pháo có ngòi tốt để tấn công hay không.
- Xe có đang chiếm đường mở hay bị nhốt.
- Quân nào đang bị treo, bị tấn công nhưng không được bảo vệ.
- Hai hoặc nhiều quân có phối hợp tấn công cùng mục tiêu hay không.

Tượng và Sĩ hiện chỉ có điểm vật chất, chưa có PST riêng. Điều đó khiến AI chưa phân
biệt rõ một Sĩ/Tượng đang bảo vệ Tướng tốt với một Sĩ/Tượng đứng kém hiệu quả.

### Công thức evaluation nên hướng tới

Không nên viết toàn bộ logic trong một biểu thức lớn. Nên chia thành các feature độc
lập để có thể bật/tắt, test và thay đổi trọng số:

```text
evaluation =
    material
  + piece_square
  + mobility
  + king_safety
  + pawn_structure
  + rook_activity
  + cannon_activity
  + horse_activity
  + advisor_elephant_defense
  + threats
  + piece_coordination
  + tempo
```

Mỗi feature trả về:

```text
điểm của Đỏ - điểm của Đen
```

Sau đó có thể áp dụng Tapered Evaluation cho cả các feature động:

```text
feature_score =
    (feature_MG * phase + feature_EG * (16 - phase)) / 16
```

Ví dụ, an toàn Tướng quan trọng hơn trong trung cuộc, còn khả năng hoạt động của
Tướng có thể quan trọng hơn trong tàn cuộc.

### Material: giá trị vật chất

Material là tổng giá trị các quân còn trên bàn. Đây là nền tảng ổn định nhất của
hàm đánh giá.

```text
material = tổng giá trị quân Đỏ - tổng giá trị quân Đen
```

Điểm cần cải tiến:

- Điều chỉnh giá trị quân bằng kết quả thi đấu thay vì chỉ dựa vào cảm tính.
- Giữ giá trị MG và EG riêng biệt.
- Có thể thêm bonus nhỏ cho cặp quân phối hợp tốt, ví dụ hai Xe hoặc Mã + Pháo.

**Rủi ro:** tăng giá trị một quân quá cao khiến AI không dám đổi quân dù đổi quân có
lợi về thế.

### Piece-Square Table: giá trị vị trí

PST cộng hoặc trừ điểm theo ô mà quân đang đứng. Đây là cách rẻ và nhanh để dạy AI
những nguyên tắc vị trí cơ bản.

Ví dụ:

- Tốt được thưởng khi qua sông và tiến gần cung đối phương.
- Mã được thưởng ở vị trí trung tâm, có nhiều đường đi.
- Xe được thưởng khi hoạt động trên hàng hoặc cột quan trọng.
- Tướng được khuyến khích ở vị trí an toàn trong trung cuộc.

Điểm cần cải tiến:

- Tạo PST riêng cho Sĩ và Tượng.
- Tách PST MG và EG thực sự cho Mã, Pháo và Xe; hiện chúng đang dùng chung.
- Kiểm tra tính đối xứng giữa Đỏ và Đen.
- Không để bonus PST lớn đến mức lấn át việc mất quân.

### Mobility: độ cơ động

Mobility đo số nước đi hữu ích mà một quân có thể thực hiện.

```text
mobility = tổng(mobility_bonus[loại quân][số ô đi được])
```

Nên ưu tiên tính cho Xe, Mã và Pháo. Không nên chỉ đếm mọi nước hợp lệ như nhau:

- Nước đi vào ô an toàn có giá trị cao hơn.
- Nước đi chỉ khiến quân bị bắt ngay không nên được thưởng.
- Mã bị chặn nhiều chân cần bị trừ điểm.
- Xe có nhiều ô đi trên đường mở cần được thưởng.

**Lợi ích:** AI bớt nhốt quân và biết phát triển quân.

**Chi phí:** phải sinh hoặc kiểm tra thêm nước đi tại mỗi nút, làm evaluation chậm
hơn. Có thể tính mobility đầy đủ ở nút chính và dùng bản rẻ hơn trong tìm kiếm sâu.

### King Safety: an toàn Tướng

King Safety đánh giá khả năng Tướng bị tấn công trong vài nước tới. Đây là feature
quan trọng vì chỉ chênh lệch vật chất không phản ánh được nguy cơ chiếu bí.

Các tín hiệu có thể tính:

- Số Sĩ và Tượng còn bảo vệ.
- Số ô chạy an toàn của Tướng.
- Xe hoặc Pháo đối phương đang hướng vào cung.
- Có quân làm ngòi Pháo nguy hiểm trên đường tới Tướng.
- Đường mặt Tướng có nguy cơ bị mở.
- Số quân đối phương tập trung gần cung.
- Tướng đang bị chiếu hoặc liên tục chịu các nước chiếu.

Nên dùng penalty tăng nhanh khi nhiều quân cùng tấn công:

```text
1 quân tấn công  -> phạt nhỏ
2 quân phối hợp  -> phạt lớn
3 quân phối hợp  -> phạt rất lớn
```

**Rủi ro:** phạt quá cao khiến AI chỉ phòng thủ và bỏ lỡ cơ hội phản công hoặc ăn
quân.

### Pawn Structure: cấu trúc Tốt

Tốt có giá trị phụ thuộc mạnh vào vị trí:

- Tốt qua sông được thưởng vì có thể đi ngang và tạo đe dọa.
- Tốt tiến sâu gần cung đối phương được thưởng thêm.
- Tốt bị chặn hoàn toàn nên bị trừ điểm.
- Hai Tốt hỗ trợ hoặc cùng ép một khu vực có thể được thưởng.
- Tốt biên thường ít ảnh hưởng hơn Tốt trung tâm.

PST hiện đã biểu diễn một phần các đặc điểm này. Feature Pawn Structure nên chỉ cộng
những thông tin quan hệ giữa các quân mà PST không thể biểu diễn.

### Rook Activity: hoạt động của Xe

Xe là quân mạnh nhất ngoài Tướng, nhưng giá trị thực tế phụ thuộc vào khả năng hoạt
động.

Có thể thưởng cho:

- Xe trên cột hoặc hàng mở.
- Xe xâm nhập sâu vào phần bàn đối phương.
- Xe khống chế đường vào cung.
- Hai Xe phối hợp trên cùng hàng/cột.

Có thể phạt khi:

- Xe bị quân mình chặn và gần như không có nước hữu ích.
- Xe bị quân nhẹ tấn công mà không có ô lui an toàn.

### Cannon Activity: chất lượng vị trí Pháo

Pháo cần đúng một quân làm ngòi để ăn quân. Vì vậy chỉ đếm giá trị Pháo và vị trí
ô đứng là chưa đủ.

Có thể đánh giá:

- Pháo có ngòi để tấn công quân giá trị cao.
- Pháo đang tạo áp lực vào Tướng.
- Ngòi Pháo ổn định hay có thể bị đối phương di chuyển.
- Pháo không có mục tiêu hoặc bị nhiều quân chắn.
- Hai Pháo phối hợp tạo chuỗi chiếu.

Feature này đặc biệt quan trọng trong cờ tướng và là điểm khác biệt lớn so với hàm
đánh giá cờ vua.

### Horse Activity: hoạt động của Mã

Mã có thể trông rất gần mục tiêu nhưng hoàn toàn vô dụng nếu bị chặn chân.

Có thể tính:

- Số chân Mã đang bị chặn.
- Số ô tấn công hợp lệ.
- Số mục tiêu có giá trị mà Mã đang tấn công.
- Mã có ô đứng an toàn gần cung đối phương.
- Mã có được Tốt hoặc quân khác hỗ trợ hay không.

Feature này giúp AI phân biệt Mã hoạt động tốt với Mã bị nhốt, điều mà material và
PST đơn giản chưa thể hiện đủ.

### Advisor và Elephant Defense: hệ thống phòng thủ

Sĩ và Tượng ít cơ động nhưng rất quan trọng đối với an toàn Tướng.

Có thể đánh giá:

- Số Sĩ/Tượng còn lại.
- Đội hình phòng thủ có giữ được các điểm quan trọng quanh cung hay không.
- Sĩ/Tượng có đang bị ghim hoặc bị tấn công.
- Việc mất Sĩ/Tượng có mở đường cho Xe, Pháo đối phương hay không.

Giá trị của Sĩ/Tượng nên liên kết với King Safety thay vì chỉ cộng điểm vật chất cố
định.

### Threats và quân bị treo

Feature Threats đánh giá quan hệ tấn công/phòng thủ:

- Thưởng khi tấn công quân có giá trị cao hơn bằng quân có giá trị thấp hơn.
- Phạt quân đang bị tấn công nhưng không được bảo vệ.
- Phạt quân có nhiều bên tấn công hơn số bên bảo vệ.
- Thưởng cho đòn đôi hoặc ghim quân bảo vệ Tướng.

Không nên kết luận một quân bị treo chỉ bằng số bên tấn công và phòng thủ. Thứ tự ăn
quân cũng quan trọng; về sau có thể dùng SEE để ước lượng chuỗi đổi quân.

### Piece Coordination: phối hợp quân

Material đánh giá từng quân riêng lẻ, còn coordination đánh giá cách chúng hỗ trợ
nhau.

Ví dụ:

- Xe và Pháo cùng hướng vào một đường tấn công.
- Mã được bảo vệ khi tiến gần cung.
- Một quân ghim quân phòng thủ để quân khác tấn công.
- Hai quân cùng khống chế ô chạy của Tướng.

Feature này nên được thêm sau các feature đơn giản vì dễ bị tính trùng điểm với
King Safety và Threats.

### Tempo: lợi thế lượt đi

Bên đang đến lượt thường có một lợi thế nhỏ vì có thể chủ động tạo đe dọa.

```text
tempo = +bonus nếu Đỏ đến lượt, -bonus nếu Đen đến lượt
```

Tempo chỉ nên có trọng số nhỏ. Nếu quá lớn, điểm đánh giá sẽ dao động mạnh chỉ vì
đổi lượt.

### Giải thích điểm evaluation trên giao diện

Để quan sát sự tiến hóa giữa các phiên bản, API có thể trả thêm breakdown:

```json
{
  "total": 42,
  "material": 0,
  "piece_square": 10,
  "mobility": 8,
  "king_safety": 20,
  "pawn_structure": 4
}
```

Frontend có thể hiển thị breakdown này để giải thích vì sao AI cho rằng Đỏ hoặc Đen
đang có lợi. Đây cũng là cách nhanh để phát hiện một feature có trọng số bất thường.

### Cách phát triển và chỉnh trọng số

Mỗi feature mới cần trải qua ba loại kiểm tra:

1. **Unit test theo thế cờ:** thế có Xe đường mở phải được đánh giá cao hơn thế Xe
   bị nhốt; thế Mã bị chặn chân phải có điểm thấp hơn.
2. **Regression test:** các thế cờ quan trọng cũ không được thay đổi điểm sai hướng.
3. **Đấu A/B:** phiên bản mới đấu phiên bản cũ với cùng thuật toán tìm kiếm và cùng
   thời gian.

Không nên chỉnh trọng số bằng một vài ván quan sát thủ công. Có thể bắt đầu bằng
trọng số nhỏ, sau đó dùng kết quả từ nhiều ván tự đấu để điều chỉnh. Khi đủ dữ liệu,
có thể nghiên cứu các phương pháp tự động như Texel tuning hoặc tối ưu tham số từ
tập thế cờ có kết quả.

### Opening Book

Opening Book lưu các nước khai cuộc tốt đã biết. AI chọn nhanh trong vài nước đầu
thay vì tìm kiếm từ đầu.

**Lợi ích:** khai cuộc ổn định, tiết kiệm thời gian cho trung cuộc.

**Rủi ro:** book kém chất lượng làm AI đi vào thế xấu; nếu luôn chọn một nước sẽ
làm các ván đấu thiếu đa dạng.

### Endgame Tablebase

Tablebase lưu kết quả chính xác của các tàn cuộc ít quân:

```text
thắng / hòa / thua và số nước tối ưu
```

**Lợi ích:** chơi tàn cuộc hoàn hảo trong phạm vi dữ liệu.

**Chi phí:** cần sinh và lưu lượng dữ liệu lớn; nên bắt đầu từ một vài loại tàn
cuộc quan trọng.

## Lộ trình tạo các phiên bản tiếp theo

Không nên thêm mọi kỹ thuật vào một lần. Mỗi phiên bản nên có một mục tiêu rõ ràng
để kết quả đấu cho biết kỹ thuật đó có hiệu quả hay không.

| Bước đề xuất | Thay đổi chính | Mục tiêu |
| --- | --- | --- |
| Baseline | V1 Minimax Alpha-Beta | Làm mốc so sánh |
| Mate-aware search | V3 Negamax, terminal-first, check-aware quiescence | Tìm chuỗi chiếu và chiếu hết chính xác hơn |
| Zobrist + TT | Hash nhanh, TT cố định và giữ qua lượt | Tăng nodes/second, giảm tính lại |
| Move Ordering | Killer Move + History Heuristic | Tăng cutoff, đạt depth cao hơn |
| PVS + Aspiration | Tối ưu cửa sổ Alpha-Beta | Giảm số nút tìm kiếm |
| LMR | Giảm sâu nước muộn, tìm lại khi cần | Tăng độ sâu trong cùng thời gian |
| Selective Pruning | Null Move + Futility + Razoring | Cắt nhánh ít triển vọng |
| Evaluation Mobility | Mobility, chân Mã, đường mở của Xe | Phát triển quân và tránh tự nhốt quân |
| Evaluation King Safety | An toàn Tướng, Sĩ/Tượng phòng thủ, áp lực vào cung | Nhận biết tấn công và nguy cơ chiếu bí |
| Evaluation Xiangqi | Ngòi Pháo, cấu trúc Tốt, phối hợp quân | Hiểu các đặc điểm riêng của cờ tướng |
| Evaluation Threats | Quân bị treo, attackers/defenders, SEE | Đánh giá đổi quân và chiến thuật chính xác hơn |
| Tuned Evaluation | Điều chỉnh trọng số bằng dữ liệu tự đấu | Cân bằng các feature bằng kết quả thực nghiệm |
| Knowledge | Opening Book hoặc Tablebase | Cải thiện khai cuộc/tàn cuộc |

WukongJS nên giữ vai trò đối thủ tham chiếu, không tính là một bước triển khai trong
chuỗi phiên bản Python.

Tên đầy đủ của một phiên bản nên thể hiện cả search và evaluation. Ví dụ:

```text
V8 - PVS/LMR + Tapered PST/King Safety
```

Nhờ vậy, khi hai AI đấu với nhau, ta biết khác biệt đến từ khả năng tìm kiếm, khả
năng đánh giá thế cờ hay cả hai.

## Cách kiểm chứng mỗi cải tiến

Mỗi phiên bản mới phải đấu với phiên bản ngay trước nó trong cùng điều kiện:

- Cùng máy và cùng số luồng.
- Cùng thời gian mỗi nước.
- Đổi màu Đỏ/Đen cân bằng.
- Dùng nhiều thế khai cuộc.
- Chạy đủ nhiều ván để giảm ảnh hưởng may rủi.

Các chỉ số cần ghi:

| Chỉ số | Ý nghĩa |
| --- | --- |
| Thắng / hòa / thua | Đo sức mạnh thực chiến |
| Tỷ lệ điểm | `(thắng + 0.5 * hòa) / tổng ván` |
| Elo tương đối | Ước lượng chênh lệch sức mạnh |
| Nodes | Số trạng thái đã duyệt |
| Nodes/second | Hiệu năng implementation |
| Độ sâu hoàn thành | Khả năng nhìn xa trong giới hạn thời gian |
| Beta cutoff | Hiệu quả Alpha-Beta và move ordering |
| TT hit rate | Hiệu quả bảng chuyển vị |
| Số lần re-search | Chi phí của PVS, Aspiration và LMR |
| Nước lỗi / timeout | Độ ổn định |

### Nguyên tắc phát triển

1. Chỉ thay đổi một nhóm kỹ thuật trong mỗi phiên bản.
2. Giữ phiên bản cũ để đấu A/B.
3. Thêm test trước khi tối ưu tìm kiếm.
4. Một kỹ thuật giảm số nút nhưng làm tỷ lệ thắng giảm không phải là cải tiến.
5. Không kết luận sau vài ván; kết quả nhỏ dễ bị nhiễu.
6. Ghi rõ cấu hình và commit dùng trong mỗi lần benchmark.

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
