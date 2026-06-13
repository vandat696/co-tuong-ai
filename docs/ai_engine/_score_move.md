````mermaid
flowchart TD
    %% Định nghĩa các node
    Start(["Bắt đầu _score_move(move, tt_move)"])
    EndTT(["Trả về 1,000,000<br>(Ưu tiên tuyệt đối)"])
    EndMVV(["Trả về điểm số MVV-LVA"])
    EndQuiet(["Trả về 0<br>(Nước đi thường)"])

    %% Luồng xử lý kiểm tra Cache
    Start --> CheckTT{"move == tt_move?"}
    CheckTT -- Đúng --> EndTT

    %% Luồng xử lý kiểm tra Ăn quân
    CheckTT -- Sai --> GetCaptured["Lấy thông tin quân cờ tại ô đích:<br>captured_piece"]
    GetCaptured --> CheckCapture{"captured_piece != Board.EMPTY?"}

    %% Nhánh tính điểm MVV-LVA
    CheckCapture -- Đúng (Nước ăn quân) --> GetAttacker["Lấy thông tin quân đi ăn:<br>attacker"]
    GetAttacker --> CalcMVV["Tính điểm theo công thức MVV-LVA:<br>10 * Value(captured) - Value(attacker)"]
    CalcMVV --> EndMVV

    %% Nhánh nước đi bình thường
    CheckCapture -- Sai (Nước đi tĩnh) --> EndQuiet

    %% Định dạng màu sắc sơ đồ
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style EndTT fill:#6f6,stroke:#333,stroke-width:2px
    style EndMVV fill:#6f6,stroke:#333,stroke-width:2px
    style EndQuiet fill:#6f6,stroke:#333,stroke-width:2px```
````
