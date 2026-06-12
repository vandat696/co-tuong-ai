# BÁO CÁO TIẾN ĐỘ DỰ ÁN

## ♞ Cờ Tướng AI Bot - Nhập Môn Trí Tuệ Nhân Tạo

---

## THÔNG TIN CƠ BẢN

### Tên Dự Án
Ứng dụng các giải thuật Heuristic và Deep Learning và kết hợp chúng trong nhận diện và phản xạ thế trận Cờ tướng

### Thành Viên
- **Nhóm 34**: 

20235677 Văn Thành Đạt
20235773 Đặng Thị Hiền Lương
20235837 Ngô Thanh Thảo
- **Giảng viên hướng dẫn**: TS. Đỗ Tiến Dũng

### Loại Dự Án
- **Môn học**: Nhập Môn Trí Tuệ Nhân Tạo (AI 101)
- **Mục tiêu**: Xây dựng một agent AI có khả năng:
  - Sinh nước đi hợp lệ theo luật cờ tướng
  - Tìm kiếm nước đi tối ưu sử dụng Minimax
  - Đánh giá tình thế dựa trên heuristic
  - Giao tiếp với giao diện người dùng qua API

---

## TỔNG QUAN DỰ ÁN

Dự án xây dựng một **hệ thống chơi cờ tướng tương tác** với ba thành phần chính:

1. **Backend** (Python): Engine AI chạy thuật toán Minimax và Cắt tỉa alpha-beta
2. **Frontend** (React): Giao diện bàn cờ tương tác trực quan (10x9)
3. **API** (FastAPI): Kết nối backend-frontend, xử lý nước đi của AI

### Kiến Trúc Hệ Thống
```
┌─────────────────────────────────────────┐
│         Frontend (React + Vite)         │
│  • Bàn cờ 10x9 với visualize di chuyển  │
│  • Xử lý click quân, hiển thị nước đi    │
│  • Giao tiếp API để lấy nước đi AI      │
└────────────────┬────────────────────────┘
                 │ HTTP API
┌────────────────▼────────────────────────┐
│        Backend API (FastAPI)             │
│  • Endpoint /move - Lấy nước đi AI      │
│  • Endpoint /health - Kiểm tra trạng thái│
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       AI Engine & Logic (Python)         │
│  • Board: Biểu diễn bàn cờ 10x9         │
│  • MoveGen: Sinh nước đi theo luật       │
│  • AIEngine: Minimax + Alpha-Beta        │
│  • Evaluator: Đánh giá thế cờ           │
└─────────────────────────────────────────┘
```

---

## TÌNH TRẠNG DỰ ÁN

### Mức Độ Hoàn Thành: **70%**

| Thành Phần | Trạng Thái | Ghi Chú |
|-----------|-----------|--------|
| **Board Logic** | Hoàn thành | Biểu diễn bàn cờ 10x9, lưu trữ quân |
| **Luật Chơi** | Hoàn thành | Sinh nước đi hợp lệ, kiểm tra luật chống tướng |
| **Minimax** | Hoàn thành | Tìm kiếm nước đi với độ sâu tối đa 5 |
| **Cắt tỉa α-β** | Hoàn thành | Tối ưu hóa tìm kiếm, cắt bỏ nhánh vô ích |
| **Transposition Table** | Hoàn thành | Cache kết quả tìm kiếm để tránh tính lặp |
| **Hàm đánh giá thế cờ** | Hoàn thành | Heuristic + Piece-Square Tables |
| **FastAPI Backend** | Hoàn thành | API /move hoạt động, CORS config |
| **React Frontend** | Hoàn thành | Bàn cờ hiển thị, quân di chuyển |
| **Xử lý nước Đi** | Hoàn thành | Tính toán nước đi hợp lệ cho mỗi quân |
| **AI Integration** | Hoàn thành | AI tính nước tối ưu, giao tiếp qua API |
| **ML Training** | Dự kiến | Chuẩn bị dataset + neural network |

---

## FRONTEND - Giao Diện Người Dùng

### Công Nghệ
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: CSS3 + CSS Transition

### Tính Năng Đã Thực Hiện
**- Bàn cờ** 

**- Hiển thị quân cờ** 

**- Tương tác người chơi**
---

## BACKEND - Engine AI

### Công Nghệ
- **Framework**: FastAPI (Python)
- **Thuật toán chính**: Minimax + Alpha-Beta Pruning
- **Tối ưu hóa**: Transposition Table, Iterative Deepening

### Thành Phần Backend

#### 1. **Board.py** - Biểu Diễn Bàn Cờ
```python
# Bàn cờ 10 hàng × 9 cột
# Mã hóa quân:
#  Dương (Đỏ):  1=Tướng, 2=Sĩ, 3=Tượng, 4=Xe, 5=Mã, 6=Pháo, 7=Tốt
#  Âm (Đen):   -1=Tướng, -2=Sĩ, -3=Tượng, -4=Xe, -5=Mã, -6=Pháo, -7=Tốt
```

#### 2. **Move_Gen.py** - Sinh Nước Đi Hợp Lệ
Sinh nước đi thô (pseudo-moves) cho mỗi loại quân, sau đó lọc bỏ nước đi vi phạm.

**Luật Chống Tướng:**
- Hai Tướng không được đối diện nhau trên cùng cột dọc nếu không có quân cản ở giữa
- Kiểm tra trước khi xác nhận nước đi hợp lệ

#### 3. **AI_Engine.py** - Minimax + Cắt tỉa α-β 
**Thuật toán: Minimax với tối ưu hóa**

```
Minimax(node, depth, α, β, isMaximizing):
  if depth == 0 or node is terminal:
    return evaluate(node)
  
  if isMaximizing:  # Lượt của AI (Đen)
    value = -∞
    for each child of node:
      value = max(value, Minimax(child, depth-1, α, β, False))
      α = max(α, value)
      if α ≥ β:
        break  # β-cutoff (Alpha-Beta Pruning)
    return value
  
  else:  # Lượt của người chơi (Đỏ)
    value = +∞
    for each child of node:
      value = min(value, Minimax(child, depth-1, α, β, True))
      β = min(β, value)
      if α ≥ β:
        break  # α-cutoff
    return value
```

**Tối ưu hóa:**
- **Cắt tỉa α-β**: Cắt bỏ nhánh không cần tính
- **Move Ordering**: Sắp xếp nước đi ưu tiên 
- **Transposition Table**: Cache kết quả tìm kiếm theo bàn cờ hash
- **Iterative Deepening**: Tìm kiếm lần lượt từ depth 1 tới max_depth với time limit chọn trước

**Độ sâu tìm kiếm hiện tại:** 5 nước
**Thời gian tìm kiếm tối đa:** 0.5s/nước (có thể điều chỉnh)

#### 4. **Eval.py** - Hàm đánh giá thế cờ 
**Heuristic đánh giá:**

```
Score = Σ(Piece_Value) + Σ(Position_Bonus)
```

**Giá Trị Quân:**
| Quân | Điểm |
|-----|------|
| Tướng | 10,000 |
| Xe | 200 |
| Mã | 90 |
| Pháo | 100 |
| Tượng | 50 |
| Sĩ | 40 |
| Tốt | 20 |

**Bảng đánh giá giá trị quân cờ:**
Vì quân cờ có thể thay đổi giá trị nếu nó ở vị trí thuận lợi, chiếm lợi thế gây áp lực đối thủ nên để chính xác hơn ta thêm yếu tố này
- **Tốt**: Khuyến khích đi sâu vào đất địch, +12 điểm ở trung tâm
- **Mã**: Khuyến khích chiếm vị trí trung tâm, +8 điểm

**Ví dụ tính điểm:**
- Nếu Đỏ có: 2 Xe (400), 2 Mã (180), 5 Tốt chiếm vị trí tốt (100) = **680 điểm**
- Nếu Đen có: 1 Xe (200), 1 Mã (90), 2 Tốt (40) = **330 điểm**
- **Score = +350** (Đỏ tốt)

### API Endpoint

#### POST `/move` - Lấy Nước Đi AI
```javascript
Request:
{
  "board_state": [[...], ...],  // Bàn cờ 10x9 (mã int)
  "is_red_turn": true           // Lượt chơi (true=Đỏ, false=Đen)
}

Response:
{
  "from_row": 9,
  "from_col": 4,
  "to_row": 8,
  "to_col": 4,
  "score": 350  // Điểm số sau nước đi
}
```

---

##  CÁC KỸ THUẬT ĐƯỢC SỬ DỤNG CHO AI ENGINE

### Thuật toán chính: Minimax

**Mô tả:**
Minimax là thuật toán tìm kiếm trong không gian trạng thái, tìm nước đi có lợi thế nhất cho mình và tạo bất lợi nhất có thể cho đối thủ:
- **Max Player** (AI/Đen): Tìm nước đi maximize điểm số
- **Min Player** (Người/Đỏ): Giả định sẽ tìm nước đi minimize điểm số

Tuy nhiên cho thuật toán minimax khá lâu và khối lượng tính toán lớn, để hợp lý thì ta sẽ sử dụng thêm các kĩ thuật khác bên dưới

### Cắt tỉa α-β 

**Vấn đề mà nó giải quyết:**
Minimax cơ bản kiểm tra tất cả các nhánh nên sẽ khá chậm vì thế:

**Giải pháp:**
Cắt tỉa α-β sẽ cắt bỏ các nhánh không cần thiết bằng cách theo dõi:
- **α**: Giá trị tốt nhất mà Max Player đã tìm được
- **β**: Giá trị tốt nhất mà Min Player đã tìm được

**Quy tắc cắt bỏ:**
```
if value ≥ β:  # α-cutoff: Nhánh này không cải thiện cho Min
    break

if value ≤ α:  # β-cutoff: Nhánh này không cải thiện cho Max
    break
```

**Tác động:**
- **Trường hợp tốt nhất**: Độ phức tạp giảm xuống O(b^(d/2)), có thể cải thiện đến gấp 100 lần
- **Trường hợp trung bình**: Giảm ~60-80% số nút tính toán
- **Trường hợp xấu nhất**: Không cải thiện tuy nhiên sẽ hiếm khi xảy ra

### Transposition Table

**Vấn đề:**
Cùng một bàn cờ có thể được tính nhiều lần ở các đường dẫn khác nhau

**Giải pháp:**
Lưu kết quả đã tính vào cache theo hash bàn cờ

**Cài đặt:**
```python
self.transposition_table = {
    board_hash: {
        'score': value,
        'depth': d,
        'flag': 'EXACT'|'LOWER'|'UPPER'
    }
}
```

**Tác động:** Giảm 30-50% số lượng nút cần tính

### Move Ordering

**Vấn đề:**
Kĩ thuật cắt tỉa α-β hiệu quả khi nước tốt được kiểm tra trước, vì thế ta sẽ đưa ra chiến lược ưu tiên cho hợp lý

**Giải pháp:**
Sắp xếp nước đi theo độ ưu tiên:
**Capture moves** (bắt quân) > **Check moves** (chiếu tướng) > **Advancement moves** (tiến lên trung tâm) >**Other moves** (nước đi bình thường)

**Công thức sắp xếp:**
```python
def _score_move(self, move):
    from_row, from_col, to_row, to_col = move
    captured = board[to_row][to_col]
    if captured:  # Bắt quân
        return piece_value[abs(captured)] * 10 + 1000
    else:  # Không bắt quân
        return 0
```

**Tác động:** Cải thiện Kĩ thuật cắt tỉa α-β đến 10-20 lần

### Quản lý thời gian bằng tìm kiếm sâu dần

**Giải pháp:**
Thay vì cố gắng tính thật sâu ngay từ đầu, máy tính sẽ "nhìn" từng bước một: xét hết các khả năng ở 1 nước, sau đó đến 2 nước, 3 nước, và cứ thế tăng dần.
- Mỗi lần tăng độ sâu, tìm nước đi tốt hơn
- Dừng khi hết thời gian
- Trả về kết quả tốt nhất tìm được

### Hàm đánh giá thế trận Heuristic 

**Mục tiêu:** Đánh giá bàn cờ mà không cần tính Minimax sâu hơn

**Công thức:**
```
Score = 
  + Σ(Red_Piece_Values) - Σ(Black_Piece_Values)
  + Σ(Red_Position_Bonuses) - Σ(Black_Position_Bonuses)
```

**Ma trận bảng giá trị vị trí**
- Khuyến khích Tốt đi sâu vào đất địch, và giảm giá trị khi ở góc bàn cờ
- Khuyến khích Mã chiếm vị trí trung tâm, tấn công vào cung tướng của địch

**Ví dụ:**
Đỏ có 2 Xe, 2 Mã, 5 Tốt mạnh
             Đen có 2 Xe, 1 Mã, 3 Tốt
  Score = 680 - 430 = +250 (Đỏ chiếm lợi thế)


---

## TIẾN TRÌNH ĐÃ THỰC HIỆN
Hiện tại trò chơi đã có thể thực hiện và chơi được thật, tuy nhiên vẫn đang trong quá trình kiểm thử và sẽ fix các bug trong quá trình này
### Phase 1: Backend Core Logic
### Phase 2: API Integration
### Phase 3: Frontend Development

## DỰ TÍNH CÓ THỂ TRONG TƯƠNG LAI

Có thể ứng dụng Machine Learning: Bên cạnh Heuristic có thể xem xét gia tăng độ thông minh bằng cách tích hợp thêm Machine Learning từ Dataset đã tìm được
Tối ưu lượng giá: Bổ sung bảng vị trí cho mọi loại quân, đánh giá khả năng kiểm soát trung tâm và độ an toàn của Tướng, tìm hiểu thêm các kĩ thuật khác để khiến AI thông minh hơn.
Hiệu năng: Tìm cách tăng tốc độ tính toán, tối ưu hơn qua internet, tài liệu tham khảo,...

---

## TÀI LIỆU THAM KHẢO 

### Kiến thức cơ bản
- Minimax Algorithm: https://en.wikipedia.org/wiki/Minimax
- Alpha-Beta Pruning: https://en.wikipedia.org/wiki/Alpha–beta_pruning
- Xiangqi Rules: https://en.wikipedia.org/wiki/Xiangqi
- Slide bài giảng (Chương 4, 5, 6)

### Framework & Library
- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- PyTorch: https://pytorch.org

### Dataset
- Online Xiangqi Games: https://www.kaggle.com/chinese-chess-xiangqi

---


