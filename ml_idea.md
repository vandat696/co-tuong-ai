Báo cáo Nghiên cứu Chuyên sâu: Thiết kế và Tích hợp Mạng Nơ-ron Lượng giá (Value Network) vào Kiến trúc Minimax và Alpha-Beta cho Trí tuệ Nhân tạo Cờ TướngMở đầu và Bối cảnh Chuyển giao Hệ hình trong Trí tuệ Nhân tạo Đối khángTrong tiến trình phát triển của Trí tuệ Nhân tạo (AI) dành cho các trò chơi cờ đối kháng với thông tin hoàn hảo như Cờ Tướng (Xiangqi), Cờ Vua (Chess) hay Shogi, kiến trúc nền tảng truyền thống thường dựa trên sự kết hợp giữa thuật toán duyệt cây tìm kiếm Minimax, cơ chế cắt tỉa Alpha-Beta và một hàm lượng giá tĩnh (static evaluation function). Quá trình tìm kiếm này yêu cầu hệ thống duyệt qua một không gian trạng thái khổng lồ, ước tính giá trị của từng vị trí tại các nút lá (leaf nodes) và truyền ngược giá trị đó lên gốc của cây để đưa ra quyết định tối ưu. Các phiên bản AI cổ điển, bao gồm các phiên bản ban đầu của nhiều engine mã nguồn mở, phụ thuộc hoàn toàn vào hàm lượng giá được thiết kế thủ công (handcrafted evaluation). Các hàm lượng giá này, chẳng hạn như các tệp mã nguồn evaluator.py hay king_safety.py, được xây dựng dựa trên kiến thức chuyên gia, bao gồm việc tính toán điểm số vật chất, định giá vị trí quân cờ thông qua các ma trận tĩnh (piece-square tables), phân tích cấu trúc Tốt, tính cơ động của các quân cờ tấn công như Xe, Pháo, Mã và đặc biệt là độ an toàn của Tướng.Mặc dù phương pháp tiếp cận thủ công này đã thống trị trong nhiều thập kỷ và tạo ra những engine có khả năng thi đấu ở cấp độ Kiện tướng, nó đang bộc lộ những giới hạn kiến trúc không thể vượt qua. Việc thiết kế các quy tắc heuristic bằng tay đòi hỏi sự tinh chỉnh cực kỳ phức tạp và không bao giờ có thể bao quát được toàn bộ các yếu tố chiến thuật, chiến lược hay các cấu trúc phòng ngự phi truyền thống tiềm ẩn trên một bàn cờ có kích thước $9 \times 10$ với không gian trạng thái cực lớn như Cờ Tướng. Sự bùng nổ của Học máy (Machine Learning - ML) và Học sâu (Deep Learning) đã mở ra một hướng đi mang tính bước ngoặt: sử dụng Mạng Nơ-ron Nhân tạo (Neural Networks) làm Hàm lượng giá (Value Network). Bằng cách huấn luyện một mạng nơ-ron để dự đoán trực tiếp tỷ lệ thắng/thua hoặc điểm số lợi thế từ trạng thái bàn cờ hiện tại—với đầu ra là một giá trị vô hướng (scalar) chạy từ -1 (Đen thắng) đến 1 (Đỏ thắng) hoặc điểm bách phân (centipawns)—hệ thống có thể học được những mô hình chiến thuật phức tạp vượt xa khả năng đúc kết của con người.Tuy nhiên, việc tích hợp một mô hình Học sâu nguyên bản vào môi trường tìm kiếm Minimax và Alpha-Beta truyền thống lại tạo ra một thách thức kỹ thuật to lớn về mặt hiệu năng tính toán. Nút thắt cổ chai nằm ở sự không tương thích giữa cơ chế duyệt cây tuần tự của Alpha-Beta và chi phí khởi tạo cực lớn của các thư viện Học sâu phổ biến như PyTorch hay TensorFlow khi chạy trên vi xử lý trung tâm (CPU). Báo cáo nghiên cứu này cung cấp một phân tích toàn diện, sâu sắc và mang tính định hướng kiến trúc nhằm giải quyết bài toán tích hợp Value Network vào AI Cờ Tướng. Báo cáo tập trung mổ xẻ nguyên lý hoạt động của thuật toán cắt tỉa Alpha-Beta, đánh giá tính khả thi của kỹ thuật gộp lô (Batching), phân tích sự kém hiệu quả của các kiến trúc Mạng Nơ-ron Tích chập (CNN) truyền thống trong ngữ cảnh này, và đề xuất một giải pháp triệt để mang tên NNUE (Efficiently Updatable Neural Networks). Kiến trúc NNUE, hiện đang là xương sống của các engine hàng đầu thế giới như Stockfish, Pikafish, Fairy-Stockfish và Orange Xiangqi, sẽ được phân tích chi tiết về mặt toán học, thiết kế mô hình (backbone), phương pháp lượng tử hóa (quantization), cũng như chiến lược tích hợp thực tiễn.Nút thắt Cổ chai của Thuật toán Alpha-Beta và Giới hạn của Kỹ thuật BatchingĐể hiểu rõ tại sao việc gọi trực tiếp một mạng nơ-ron bằng PyTorch ở mỗi nút lá lại làm suy giảm hiệu năng nghiêm trọng, trước hết cần xem xét bản chất toán học và cơ chế vận hành của thuật toán cắt tỉa Alpha-Beta. Thuật toán Alpha-Beta là một bản nâng cấp của Minimax, được thiết kế để loại bỏ (cắt tỉa) các nhánh của cây trò chơi không thể ảnh hưởng đến quyết định cuối cùng, qua đó giảm độ phức tạp thời gian từ $O(b^d)$ xuống mức lý tưởng là $O(\sqrt{b^d})$, với $b$ là hệ số rẽ nhánh và $d$ là độ sâu tìm kiếm.Sức mạnh của Alpha-Beta nằm ở tính tuần tự nghiêm ngặt (strict sequentiality) và khả năng tìm kiếm theo chiều sâu (depth-first search). Tại mỗi nút, thuật toán duy trì hai ranh giới: $\alpha$ (giá trị lớn nhất được đảm bảo cho người chơi MAX) và $\beta$ (giá trị nhỏ nhất được đảm bảo cho người chơi MIN). Khi hệ thống duyệt qua các nước đi tiềm năng từ trái sang phải, giá trị lượng giá của một nút lá vừa được tính toán sẽ lập tức cập nhật $\alpha$ hoặc $\beta$. Nếu phát hiện một nhánh có giá trị tồi tệ hơn các ranh giới đã được thiết lập trước đó, thuật toán sẽ ngay lập tức ngừng mở rộng nhánh đó, tạo ra hiệu ứng cắt tỉa. Chính cơ chế đánh giá nhanh và phản hồi tức thời này cho phép các engine Cờ Tướng truyền thống duyệt hàng triệu nút mỗi giây (Nodes Per Second - NPS) bằng mã nguồn C/C++ được tối ưu hóa. Nếu thay thế hàm lượng giá tĩnh bằng một lời gọi hàm Python/PyTorch tại mỗi nút lá, quá trình này sẽ bị đình trệ bởi chi phí chuyển đổi ngữ cảnh (context switching), quản lý bộ nhớ động và việc thực thi các phép toán tensor dấu phẩy động chưa được tối ưu, khiến tốc độ NPS lao dốc từ hàng triệu xuống chỉ còn vài trăm nút mỗi giây.Đứng trước thách thức này, kỹ thuật gộp lô (Batching) thường được cân nhắc như một giải pháp cứu cánh để tận dụng sức mạnh xử lý song song khổng lồ của Bộ xử lý Đồ họa (GPU). Ý tưởng cốt lõi của Batching trong bối cảnh này là: thay vì gọi PyTorch để suy luận (inference) cho từng nút lá đơn lẻ, thuật toán sẽ mở rộng (expand) hàng loạt nhánh trên cây tìm kiếm, thu thập hàng nghìn trạng thái bàn cờ khác nhau thành một "lô" dữ liệu duy nhất, sau đó đẩy toàn bộ ma trận này qua card đồ họa để mạng nơ-ron xử lý trong một nhịp. Các mạng nơ-ron cũng sử dụng các lớp chuẩn hóa lô (Batch Normalization) để duy trì sự ổn định của gradient và gia tăng tốc độ hội tụ trong quá trình huấn luyện, đồng thời dựa vào các tham số trung bình động (Exponential Moving Average) để suy luận các mẫu độc lập. Tuy nhiên, ứng dụng Batching vào trong tìm kiếm Alpha-Beta sinh ra một nghịch lý cấu trúc vô cùng nghiêm trọng.Nghịch lý đó là: để tạo ra một lô dữ liệu (batch) đủ lớn nhằm khai thác hiệu quả tài nguyên của GPU, thuật toán buộc phải đình chỉ việc cập nhật $\alpha$ và $\beta$, đồng thời phải sinh ra (expand) hàng loạt nút lá trước khi biết được giá trị thực của chúng. Việc này đi ngược hoàn toàn với triết lý của cắt tỉa Alpha-Beta, vốn phụ thuộc vào việc kiểm tra kết quả của nút trước đó để quyết định xem có cần đánh giá nút hiện tại hay không. Bằng cách ép buộc gom lô, hệ thống sẽ gửi đi lượng giá một số lượng khổng lồ các nút đáng lý ra đã bị cắt bỏ nếu thuật toán chạy tuần tự. Mặc dù các kỹ thuật biến thể như Batched Alpha-Beta hoặc Lazy SMP (Symmetric Multiprocessing) cố gắng giảm thiểu sự phụ thuộc này bằng cách chạy song song nhiều luồng tìm kiếm và chia sẻ Bảng hoán vị (Transposition Table) , các phương pháp này vẫn dẫn đến sự bùng nổ không gian tìm kiếm và tiêu tốn một lượng tài nguyên vô ích (search overhead). Hơn nữa, kiến trúc dựa trên Batching và GPU phù hợp hơn với thuật toán Tìm kiếm Cây Monte Carlo (Monte Carlo Tree Search - MCTS) như trong AlphaZero, chứ không phải với công cụ tìm kiếm Alpha-Beta truyền thống. Mục tiêu của một engine Cờ Tướng hiện đại là duy trì tốc độ phân tích cực nhanh trên các bộ vi xử lý máy tính cá nhân (CPU) thông thường, do đó Batching không phải là lời giải tối ưu cho một Value Network nhúng trực tiếp vào Alpha-Beta.So sánh Đầu vào: Mạng Tích chập (CNN) và Mạng Phần dư (ResNet)Khi thiết kế mô hình Học máy cho Cờ Tướng, kiến trúc Mạng Nơ-ron Tích chập (CNN) hoặc Mạng Phần dư (ResNet) thường là những lựa chọn xuất hiện đầu tiên trong tư duy của các nhà phát triển. Cách tiếp cận này xử lý trạng thái bàn cờ tương tự như việc xử lý hình ảnh thị giác máy tính, biểu diễn hệ tọa độ không gian dưới dạng các ma trận đa chiều.Bàn cờ Cờ Tướng có kích thước hình học là 9 cột dọc và 10 hàng ngang, tạo thành một lưới $9 \times 10$. Trong mô hình ResNet-18 tiêu chuẩn, hệ thống thường thiết lập một cấu trúc biểu diễn đầu vào bao gồm 14 mặt phẳng đặc trưng (feature planes). Trong đó, 7 mặt phẳng đầu tiên mã hóa vị trí của 7 loại quân cờ thuộc phe Đỏ (Tướng, Sĩ, Tượng, Xe, Pháo, Mã, Tốt), và 7 mặt phẳng tiếp theo mã hóa vị trí của các quân cờ tương ứng thuộc phe Đen. Một số nghiên cứu nâng cao hơn thậm chí còn bổ sung các mặt phẳng bổ trợ, ghi nhận các hướng đi hợp lệ của các loại quân đặc thù (ví dụ: các bước nhảy của Mã, đường chéo của Tượng, hoặc các giới hạn của Tướng trong Cửu cung) nhằm giảm thiểu gánh nặng học tập cho mạng nơ-ron và gia tăng sức mạnh tổng thể của mô hình. Sau khi tiếp nhận tensor đầu vào, các lớp tích chập sâu của mạng ResNet sẽ áp dụng các bộ lọc không gian để trích xuất các đặc trưng chiến thuật, và cuối cùng dự đoán xác suất hành động (policy) hoặc giá trị trạng thái (value).Mặc dù kiến trúc ResNet-18 mang lại độ chính xác chiến thuật cực cao nhờ năng lực nội suy không gian và mô hình hóa hình học bàn cờ, nó lại trở thành một thảm họa về mặt hiệu năng khi chạy tích hợp trên CPU bằng luồng tìm kiếm Alpha-Beta. Việc thực thi mạng CNN đòi hỏi hàng triệu phép toán nhân-cộng dấu phẩy động (FLOPs) cho một lần suy luận duy nhất. Hơn thế nữa, mạng CNN không có khả năng nhận diện tính cập nhật cục bộ. Nếu một nước cờ trong Cờ Tướng chỉ đơn thuần là việc di chuyển Pháo từ một ô sang ô khác, mạng CNN vẫn bắt buộc phải xử lý lại toàn bộ tensor hình ảnh $14 \times 9 \times 10$ qua hàng chục lớp ẩn đồ sộ. Sự lãng phí tính toán này khiến các engine Cờ Vua và Cờ Tướng chuyển hướng sang một hệ hình kiến trúc hoàn toàn khác biệt: Mạng Cập nhật Hiệu quả (NNUE).Triết lý Kiến trúc NNUE (Efficiently Updatable Neural Network)Được phát triển và công bố vào năm 2018 bởi lập trình viên Nhật Bản Yu Nasu cho nền tảng Shogi (Cờ Tướng Nhật Bản) thông qua engine YaneuraOu, NNUE (được viết cách điệu là ƎUИИ) đại diện cho một bước đột phá trong thiết kế mạng nơ-ron. Kiến trúc này lấy cảm hứng từ thuật toán "Bonanza method" của Kunihito Hoki, vốn lập chỉ mục các bảng điểm quân cờ dựa trên vị trí của Tướng. Đến năm 2020, lập trình viên Hisayori "Nodchip" Noda đã chứng minh tính phổ quát của nó bằng cách đưa NNUE vào Stockfish 12, tạo ra sự nhảy vọt chưa từng có về điểm số Elo và định hình lại toàn bộ ngành công nghiệp lập trình cờ máy tính. Kế thừa thành công đó, các dự án mã nguồn mở như Pikafish (engine Cờ Tướng), Fairy-Stockfish (engine cho đa biến thể cờ) và Orange Xiangqi đều đã tích hợp NNUE, đạt được trình độ siêu nhân (superhuman) trong khi vẫn hoàn toàn phụ thuộc vào năng lực xử lý của vi xử lý trung tâm (CPU).Kiến trúc cốt lõi của NNUE không dựa trên các tầng tích chập sâu thẳm mà sử dụng một cấu trúc Perceptron đa lớp (Multi-Layer Perceptron - MLP) cực kỳ nông nhưng có độ rộng đầu vào đồ sộ. Để dung hòa giữa sức mạnh dự đoán của học sâu và tốc độ chớp nhoáng của Alpha-Beta, thiết kế thiết kế backbone của NNUE xoay quanh ba trụ cột toán học và kỹ thuật:Độ thưa thớt biểu diễn tối đa (High sparsity of inputs).Khả năng tính toán tăng dần (Incremental updates) thông qua Bộ tích lũy (Accumulator).Lượng tử hóa cấp độ phần cứng (Hardware-level Quantization) để tối đa hóa lệnh SIMD trên CPU.
Tiêu chí Đánh giá,Hàm Lượng giá Thủ công (Ver 3),Mạng CNN/ResNet (Có Batching),Kiến trúc NNUE (Khuyến nghị cho Ver 4)
Phần cứng Tối ưu,CPU,GPU chuyên dụng,CPU (Sử dụng tập lệnh SIMD/AVX2)
Kiến trúc Backbone,Các quy tắc lập trình Heuristic,ResNet-18 / Transformer đa lớp,MLP siêu nông (thường 2 đến 4 lớp)
Độ trễ Suy luận (Latency),Cực thấp (Vài nano giây),Rất cao (Vài mili giây/lô dữ liệu),Cực thấp (Tương đương đánh giá tĩnh)
Tương thích Alpha-Beta,Hoàn hảo (duyệt tuần tự),"Phá vỡ cơ chế truyền giá trị α,β",Hoàn hảo (Nhờ cơ chế trạng thái Accumulator)
Kích thước Mô hình,Không đáng kể,Hàng chục đến hàng trăm MB,Cực kỳ nhỏ gọn (khoảng 0.6 MB - 20 MB)
Kiểu Dữ liệu Xử lý,Số nguyên (Integers),Dấu phẩy động (Float32 / Float16),Số nguyên lượng tử hóa (Int16 / Int8)
Thiết kế Mô hình: Biểu diễn Đặc trưng Đầu vào và Cấu trúc BackboneĐể xây dựng một mô hình Value Network hiệu quả theo kiến trúc NNUE cho Cờ Tướng, việc xác định rõ ràng bộ tính năng đầu vào (Input feature set) và thiết lập cấu trúc mạng (Backbone) là yếu tố quyết định sự thành bại.Không gian Đặc trưng HalfKP và HalfKAv2Thay vì truyền một hình ảnh bàn cờ dạng lưới, NNUE sử dụng một lớp đầu vào được tham số hóa quá mức (overparameterized) dưới dạng một vector nhị phân thưa thớt khổng lồ. Phương pháp tiếp cận cơ sở được gọi là HalfKP (Half King-Piece). Triết lý của HalfKP là theo dõi sự tồn tại của mọi quân cờ trên bàn cờ dựa trên mối tương quan hình học tương đối với vị trí của Tướng. Do mục tiêu tối thượng trong các trò chơi như Cờ Vua hay Cờ Tướng là bảo vệ Tướng phe mình và chiếu bí Tướng đối phương, mọi đánh giá vị trí đều trở nên có ý nghĩa nhất khi quy chiếu về lăng kính của quân Tướng.Trong một cấu trúc NNUE Cờ Tướng tiêu chuẩn, như được áp dụng trong engine Orange Xiangqi, mạng nơ-ron phân bổ 1620 tính năng đầu vào cho mỗi người chơi (Phe Đỏ và Phe Đen), tạo ra một lớp đầu vào tổng cộng gồm 3240 nơ-ron. Con số 1620 này là kết quả của việc khai triển không gian các tổ hợp vị trí: Bàn cờ Cờ Tướng bao gồm 90 ô (9 hàng x 10 cột). Với mỗi vị trí mà Tướng có thể đứng, mạng xem xét sự hiện diện của các loại quân cờ khác nhau trên 90 ô này, với màu sắc và chức năng riêng biệt. Bằng cách nhân số lượng ô bàn cờ (90) với 18 tổ hợp phân loại quân cờ và trạng thái tương đối, mạng hình thành chính xác 1620 đặc trưng hình học cho một phe. Các mô hình mở rộng hơn có thể sử dụng cấu trúc $(2 \times 2430)$ tính năng đầu vào tùy thuộc vào mức độ phân rã loại quân. Do tại một thời điểm, chỉ có 32 quân cờ xuất hiện trên bàn cờ, vector đầu vào có độ thưa thớt cực đại—chỉ một phần nhỏ (khoảng 0.1%) nơ-ron có giá trị bằng $1$ (kích hoạt), trong khi 99.9% còn lại mang giá trị $0$. Sự tham số hóa quá mức ở lớp đầu vào này, điều thường bị cấm kỵ trong các mạng deep learning thông thường, lại chính là chìa khóa mang lại sự phong phú biểu đạt (richness) cho lớp ẩn đầu tiên của NNUE.Để tối ưu hóa không gian lưu trữ và tăng cường sức mạnh, các hệ thống tiên tiến như Pikafish và Fairy-Stockfish đã chuyển dịch từ HalfKP sang HalfKAv2. Kiến trúc HalfKAv2 được thiết kế để loại bỏ các vùng dư thừa (redundancy) liên quan đến vị trí của Tướng. Trong Cờ Vua, HalfKAv2 giảm đáng kể số lượng đầu vào từ các tổ hợp ô vuông không thể tồn tại. Đối với Cờ Tướng, Tướng bị giới hạn di chuyển trong khu vực Cửu cung $3 \times 3$ (chỉ gồm 9 ô) cho mỗi bên. Bằng cách áp dụng HalfKAv2, hệ thống chỉ lập chỉ mục tương quan dựa trên 9 vị trí hợp lệ của Tướng thay vì toàn bộ 90 ô, giúp giảm mạnh độ phức tạp của ma trận trọng số, đồng thời bổ sung các liên kết chuyển tiếp trực tiếp (direct forwarded outputs) từ bộ biến đổi đặc trưng đến lớp đầu ra nhằm nhận thức tình trạng mất cân bằng vật chất (material configurations) nhanh nhạy hơn.Cấu trúc Backbone Khuyến nghịDựa trên sự thành công của Pikafish và Orange Xiangqi, một backbone tối ưu cho việc tích hợp ML vào AI Cờ Tướng của bạn nên bao gồm một mạng hai lớp ẩn hoặc ba lớp ẩn siêu nhẹ. Theo báo cáo kỹ thuật của Orange Xiangqi, cấu trúc mạng nơ-ron có thể được định nghĩa qua mô hình PyTorch đơn giản như sau:
class NNUE(torch.nn.Module):
def **init**(self):
super(NNUE, self).**init**()
self.feature = torch.nn.Linear(1620, 128)
self.output = torch.nn.Linear(256, 1)

    def forward(self, white, black):
        white = self.feature(white)
        black = self.feature(black)
        accum = torch.clamp(torch.cat([white, black], dim=1), 0.0, 1.0)
        return torch.sigmoid(self.output(accum))

Thiết kế này sử dụng 1620 nơ-ron đầu vào cho mỗi phe, được ánh xạ thành một lớp ẩn có 128 nơ-ron thông qua bộ biến đổi đặc trưng (Feature Transformer). Ở giai đoạn xử lý tiếp theo, hai vector đặc trưng 128 chiều đại diện cho lăng kính của người chơi Đỏ và Đen được nối (concatenate) lại thành một tensor kích thước 256. Sau khi đi qua hàm kích hoạt cắt xén (Clipped ReLU hoặc kẹp giá trị), dữ liệu được đưa vào một mạng tuyến tính cuối cùng để sinh ra 1 giá trị vô hướng biểu thị lợi thế. Kích thước mô hình mạng cấu hình này chỉ tốn xấp xỉ 0.6 MB dung lượng vật lý, cho phép bộ vi xử lý nạp toàn bộ cấu trúc mạng vào bộ nhớ Cache L1/L2 tốc độ siêu cao. Những hệ thống có nguồn lực máy tính dồi dào hơn có thể tăng lớp biến đổi đặc trưng lên kích thước 256, và mở rộng mạng đầu ra bằng cấu trúc nhiều tầng như 256 -> 32 -> 32 -> 1 để đào sâu thêm khả năng đánh giá tàn cuộc. Thậm chí, một vài thử nghiệm gần đây trên Stockfish đề xuất các mạng cấu trúc đồ sộ hơn (ví dụ lớp biến đổi 3072 chiều) nhằm gia tăng kiến thức chuyên sâu về vị trí, dù điều này đi kèm với sự suy giảm nhẹ về tốc độ NPS.

Trái tim của Hệ thống: Bộ Tích lũy (Accumulator) và Cập nhật Tăng dần
Khả năng duyệt hàng triệu nút lá mỗi giây của mạng NNUE đến từ việc giải quyết bài toán toán học về tính liên tục của không gian trạng thái. Trong thuật toán tìm kiếm Minimax, các trạng thái bàn cờ liên tiếp nhau chỉ khác biệt bởi duy nhất một nước đi. Khi một quân cờ di chuyển từ ô A sang ô B, 99% trạng thái cấu trúc của bàn cờ (sự hiện diện của các quân cờ khác) hoàn toàn không thay đổi. Nếu hệ thống phải tính toán lại phép nhân ma trận (Matrix Multiplication) kích thước O(N×M) cho toàn bộ lớp đầu vào N=3240 tại mọi nút lá, bộ vi xử lý sẽ ngay lập tức quá tải.

Thay vì thực hiện phép toán tĩnh, NNUE duy trì một kiến trúc bộ đệm gọi là Bộ tích lũy (Accumulator). Bộ tích lũy này chính là tập hợp các nơ-ron của lớp ẩn đầu tiên (Feature Transformer), được lưu trữ ngay trong lõi cấu trúc dữ liệu mô tả trạng thái trò chơi (board state). Nhờ vào đặc tính đầu vào chỉ nhận giá trị nhị phân (0 hoặc 1), giá trị hoạt động của lớp ẩn đầu tiên thực chất chỉ là phép tổng các cột trọng số tương ứng với các đặc trưng đang "kích hoạt" trên bàn cờ.

Quá trình cập nhật diễn ra trong hệ thống được thực thi song hành với hàm thực hiện nước đi (make_move) trong cây Alpha-Beta:

Loại bỏ đặc trưng (0 → 1): Khi một quân cờ rời khỏi ô xuất phát, đặc trưng nhị phân tương ứng chuyển từ trạng thái 1 sang 0. Mã nguồn hệ thống C/C++ trực tiếp truy cập vào mảng Accumulator hiện hành và trừ đi cột trọng số liên kết với đặc trưng đó trong ma trận của lớp Feature Transformer.

Kích hoạt đặc trưng (1 → 0): Khi quân cờ đáp xuống ô đích đến, đặc trưng mới chuyển trạng thái từ 0 sang 1. Mã nguồn thực hiện việc cộng thêm cột trọng số liên kết với ô mới vào Accumulator.

Chỉ bằng hai thao tác cộng và trừ vector cơ bản trên một bộ nhớ đệm có kích thước nhỏ (ví dụ 128 hoặc 256 phần tử), mạng nơ-ron đã hoàn tất quá trình cập nhật lớp đồ sộ nhất với độ phức tạp giảm xuống mức O(M) (với M là kích thước lớp ẩn) thay vì O(N×M). Quan trọng hơn nữa, cấu trúc thuật toán đệ quy của Alpha-Beta đòi hỏi các thao tác lùi trạng thái (unmake_move) diễn ra liên tục. Các hệ thống thực thi NNUE sử dụng một thủ thuật tối ưu bộ nhớ: thay vì thực hiện phép toán ngược (cộng lại đặc trưng đã mất, trừ đi đặc trưng đã thêm) gây ra nguy cơ tích tụ sai số làm tròn đối với dữ liệu dấu phẩy động, hệ thống lưu trữ bản sao của các Accumulator này ở một mảng tĩnh (stack) dọc theo độ sâu của cây duyệt. Khi hệ thống hoàn tác nước đi, nó chỉ đơn giản phục hồi lại con trỏ bộ nhớ chỉ đến Accumulator của tầng độ sâu trước đó, khiến chi phí của thao tác unmake_move gần như bằng không. Bảng hoán vị (Transposition Table) được tích hợp trong engine cũng có thể được sử dụng để lưu các bộ đệm nơ-ron này song song với các mã băm Zobrist, nâng cao hơn nữa hiệu suất tìm kiếm.

Lượng tử hóa Toán học và Tối ưu hóa Bộ Vi xử lý Đa Luồng (SIMD)
Dù đã sử dụng Accumulator để tăng tốc phần lớp đầu vào, việc chạy các lớp nơ-ron ẩn tiếp theo (Fully Connected Layers) bằng định dạng dấu phẩy động 32-bit (Float32) truyền thống của PyTorch vẫn là một nguyên nhân gây lãng phí xung nhịp CPU đáng kể. Lời giải của các hệ thống AI Cờ Vua và Cờ Tướng chuyên nghiệp là kỹ thuật Lượng tử hóa (Quantization) – một quá trình dời toàn bộ miền biểu diễn toán học của mạng nơ-ron từ số thực dấu phẩy động sang số nguyên (Integer Int16 và Int8) nhằm khai thác triệt để các tập lệnh vector hóa (SIMD) trên các kiến trúc chip xử lý hiện đại.

Phân tích Phương trình Lượng tử hóa theo Tiêu chuẩn Stockfish
Lượng tử hóa NNUE không chỉ đơn thuần là việc cắt bớt phần thập phân, mà yêu cầu một mô hình toán học nhân tỷ lệ (scaling) tinh tế để giữ nguyên độ chính xác. Đối với một tầng nơ-ron tuyến tính cơ sở y=x⋅w+b, quá trình lượng tử hóa gán các hệ số khuếch đại độc lập cho các thành phần :

s
A
​
: Hệ số tỷ lệ dành cho giá trị kích hoạt đầu vào (x).

s
W
​
: Hệ số tỷ lệ dành cho ma trận trọng số mạng (w).

Để phương trình đồng nhất, độ lệch (Bias, b) phải được nội suy nhân lên bằng tích của s
A
​
⋅s
W
​
.

Kết quả phép nhân tuyến tính lượng tử hóa được tính toán ở không gian số nguyên lớn (chẳng hạn Int32) để tránh tràn bộ nhớ (overflow). Tại bước áp dụng hàm kích hoạt (thường là Clipped ReLU giới hạn miền giá trị đầu ra), phương trình được chuẩn hóa trở lại bằng phép chia cho s
W
​
:

y⋅s
A
​
=
s
W
​

((s
A
​
⋅x)⋅(s
W
​
⋅w))+(b⋅s
A
​
⋅s
W
​
)
​

Việc thiết kế phần mềm cốt lõi tại đây là phải chọn giá trị hệ số s
W
​
là một lũy thừa của 2. Bằng cách đó, phép chia đắt đỏ trong CPU sẽ được thay thế bởi phép dịch bit sang phải (bitwise right-shift >>), vốn dĩ chỉ tiêu tốn 1 xung nhịp đồng hồ.

Biến đổi Không gian Đầu ra (WDL sang Centipawns)
Điểm đặc biệt ở lớp đầu ra (Output layer) của Value Network là nó cần tạo ra một con số đánh giá tương thích với ranh giới phân tích của thuật toán Alpha-Beta truyền thống. Giá trị điểm số trong các engine cờ thường dao động từ -10.000 đến +10.000 centipawns. Để đạt được mức chuyển hóa này, một hệ số chuẩn hóa đầu ra s
O
​
được bổ sung vào biểu thức của lớp cuối cùng, đảm bảo giá trị 1.0 trong không gian dấu phẩy động nguyên bản (nghĩa là chiến thắng chắc chắn 100%) tương ứng với điểm đánh giá cực trị của công cụ tìm kiếm :

y⋅s
O
​
=
s
W
​

((s
A
​
⋅x)⋅(s
W
​
⋅
s
A
​

s
O
​

​
⋅w))+(b⋅s
W
​
⋅s
O
​
)
​

Sự hiệu chỉnh phương trình này quy định rằng trọng số lớp cuối cùng được điều biến với hệ số s
W
​
⋅
s
A
​

s
O
​

​
, và tham số độ lệch được nhân với s
W
​
⋅s
O
​
, đảm bảo tính toàn vẹn của kết quả khi áp dụng kỹ thuật dịch bit ở chặng đường cuối.

Khai thác Kiến trúc SIMD Vector
Với dữ liệu đã được nén xuống kích thước 16-bit (cho Bộ biến đổi đặc trưng) và 8-bit (cho các lớp ẩn), hệ thống lập trình C/C++ có thể nhúng trực tiếp các tập lệnh SIMD siêu cấp (Single-Instruction Multiple-Data) như SSE2, AVX2, hay AVX-512. Các tập lệnh này khai thác các thanh ghi vi xử lý rộng 256-bit hoặc 512-bit để tính toán đồng thời hàng chục nơ-ron trong một chu kỳ máy. Ví dụ, hàm intrinsic \_mm256_add_dpbusd_epi32 kết hợp cùng \_mm256_haddx4 có khả năng tính toán các phép nhân ma trận và cộng tích dồn cục bộ cho mạng lưới nơ-ron thưa thớt với tốc độ kinh ngạc. Tốc độ thực thi suy luận nhờ lượng tử hóa SIMD nhanh gấp hàng trăm lần so với việc triệu gọi trực tiếp thư viện tensor Python cơ bản.

Phương pháp Xây dựng Dữ liệu, Huấn luyện và Những Ngoại lệ Quy tắc Cờ Tướng
Quá trình tạo ra một mô hình ML làm hàm lượng giá đòi hỏi một tập dữ liệu quy mô lớn và một quá trình tối ưu hóa hàm mất mát cẩn trọng. Chất lượng của Value Network không chỉ đến từ cấu trúc mạng mà còn từ việc nó được "dạy" những thông tin gì.

Quy mô và Chiến lược Tập Dữ liệu
Các mô hình AI Cờ Tướng hàng đầu sử dụng hàng chục đến hàng trăm triệu trạng thái bàn cờ riêng biệt cho quá trình huấn luyện. Nguồn dữ liệu chất lượng cao được khai thác từ cơ sở dữ liệu các trận đấu chính thức của các Đại kiện tướng Trung Quốc và Việt Nam từ nhiều năm qua. Tuy nhiên, để tạo ra độ phủ kín cho mọi cấu trúc không gian (thay vì chỉ tập trung vào các nhánh khai cuộc phổ biến), các nhà phát triển sử dụng các engine truyền thống như Stockfish, Pikafish hoặc hệ thống Ver 3 hiện tại để chơi hàng vạn ván cờ tự động (self-play) theo các cấu hình ngẫu nhiên hóa (randomized openings), đồng thời khai thác phương pháp tạo đối thủ đa dạng (Selective Opponent Pool) nhằm khắc phục giới hạn điểm chết chiến thuật do hiện tượng tự học một chiều gây ra.

Hàm Mất mát và Ánh xạ WDL (Win-Draw-Loss)
Mô hình sẽ sử dụng hàm kích hoạt Sigmoid ở lớp đầu ra để chuyển đổi dự đoán về không gian tỷ lệ Thắng/Hòa/Thua (WDL space) có giới hạn từ 0.0 đến 1.0. Trong đó, giá trị 1.0 đại diện cho thế trận mà Đỏ giành chiến thắng tuyệt đối, và 0.0 đại diện cho chiến thắng của phe Đen. Các hàm mất mát (Loss functions) truyền thống của deep learning được áp dụng bao gồm Sai số Bình phương Trung bình (Mean Squared Error - MSE) hoặc Entropy chéo (Cross Entropy). Đáng chú ý, để ngăn chặn mô hình học sai những "nhiễu loạn" cục bộ nơi một sai lầm tồi tệ xảy ra khiến ván cờ đổi chiều, các nhà huấn luyện AI áp dụng cơ chế pha trộn nhãn mục tiêu (Target Blending). Nhãn mục tiêu được tạo ra bằng sự kết hợp tuyến tính giữa Kết quả cuối cùng của ván đấu thực tế (Game Outcome) và Điểm lượng giá tĩnh sâu (Deep Search Score) từ một engine đáng tin cậy. Sự pha trộn này giúp mô hình vừa học được cách đánh giá thế trận lâu dài vừa không bị mù mờ trước các bẫy chiến thuật ngắn hạn.

Xử lý Ngoại lệ: Quy tắc Lặp lại và Truy đuổi (AXF Repetition Rules)
Khác biệt lớn nhất của Cờ Tướng so với Cờ Vua Phương Tây nằm ở hệ thống luật lệ xử lý các tình huống truy đuổi và lặp lại liên tục (Luật AXF - Asian Xiangqi Federation). Trong Cờ Tướng, việc chiếu tướng lặp lại (perpetual check) hoặc liên tục truy đuổi một quân cờ không có rễ bảo vệ bị nghiêm cấm, và bên vi phạm sẽ bị xử thua thay vì hòa cờ như luật cờ phương Tây.
Do kiến trúc Value Network (bao gồm cả CNN hay NNUE) chỉ là một hàm tính toán vị trí thuần túy (tĩnh) mà không có khả năng nhận thức lịch sử các nước cờ đã diễn ra trước đó, việc huấn luyện mạng nơ-ron học luật chiếu lặp là bất khả thi về mặt kỹ thuật. Bởi vậy, việc tuân thủ quy tắc lặp lại này bắt buộc phải được xử lý bên ngoài mô hình ML. Ngay bên trong thân hàm tìm kiếm Alpha-Beta, nếu một nút con sinh ra dẫn đến tình trạng lặp lại nước cờ được xác định bởi Bảng băm lịch sử (History Hash Table), thuật toán phải lập tức ngắt bỏ việc triệu gọi Value Network và gán cứng một giá trị cờ bí/thua cuộc cho nút đó.

Lộ trình Đề xuất Tích hợp cho AI Cờ Tướng Hiện tại
Dựa trên những phân tích chuyên sâu về lý thuyết và thực tiễn kiến trúc AI đối kháng hiện đại, để nâng cấp dự án Trí tuệ Nhân tạo Cờ Tướng (từ việc sử dụng hàm tĩnh thủ công ver 3 sang Value Network), quy trình phát triển cần được thiết kế và triển khai chặt chẽ theo các định hướng sau:

Từ bỏ Hoàn toàn Giải pháp Batching và API PyTorch trong Cây Tìm kiếm:
Không nên áp dụng kỹ thuật gộp lô (batching) kết hợp với các mạng CNN/ResNet khi sử dụng cấu trúc Minimax + Alpha-Beta. Phương pháp này phá vỡ tính năng truyền dẫn tuần tự các biến α và β, làm suy giảm nghiêm trọng khả năng cắt tỉa và đẩy dự án chệch hướng sang hệ hình MCTS (Monte Carlo Tree Search). Công cụ tìm kiếm cần được triển khai hoàn toàn bằng mã nguồn C/C++ thuần túy, hoặc được biên dịch bằng Cython nếu dự án đang được viết bằng Python, nhằm kiểm soát triệt để vòng đời bộ nhớ và tài nguyên vi xử lý.

Thiết kế Mô hình NNUE theo Không gian HalfKAv2:
Xây dựng một mạng Perceptron đa lớp siêu nhẹ sử dụng cấu trúc HalfKAv2 với khoảng 1620 đặc trưng tham số hóa cho mỗi phe. Tận dụng nguyên lý ánh xạ tọa độ quân cờ thông qua vị trí giới hạn của Tướng trong khu vực Cửu cung để hạn chế tối đa các nơ-ron dư thừa. Áp dụng cấu trúc lớp ẩn mỏng, như (1620 x 2) -> 128 -> 1 hoặc cấu trúc phân tầng (1620 x 2) -> 256 -> 32 -> 1 để tối ưu hóa sự cân bằng giữa dung lượng (khoảng 0.6 MB - 2 MB) và độ chính xác chiến lược.

Huấn luyện Ngoại tuyến (Offline Training) và Biên dịch Lượng tử hóa:
Sử dụng framework PyTorch cùng với sự hỗ trợ của GPU trong giai đoạn phát triển và huấn luyện. Khi Value Network đạt được giá trị mất mát (Loss) đồng quy mong đợi, áp dụng mô hình toán học lượng tử hóa để dịch chuyển hệ số trọng số Float32 xuống cấu trúc số nguyên Int16/Int8. Xuất khẩu (Export) các ma trận lượng tử hóa này thành một tệp tin dữ liệu nhị phân nguyên thủy tĩnh (ví dụ .nnue).

Tích hợp Cơ chế Accumulator Cấp thấp:
Tại cấp độ mã nguồn của luồng chạy Alpha-Beta, đính kèm hai mảng dữ liệu song song đóng vai trò Bộ tích lũy (Accumulators) cho góc nhìn của Đỏ và Đen. Sửa đổi các hàm sinh nước đi make_move() và hoàn tác unmake_move() để bao gồm logic cập nhật tăng dần O(1) bằng các tập lệnh SIMD (SSE2/AVX2) trên vi xử lý. Mã nguồn sẽ trực tiếp trích xuất dữ liệu từ tệp nhị phân tĩnh để thực hiện phép cộng trừ vector, hoàn thành chu trình lượng giá với độ trễ cỡ nano giây.

Chiến lược Lai (Hybrid Evaluation) trong Giai đoạn Chuyển giao:
Trong các chu kỳ nâng cấp ban đầu, hệ thống có thể hoạt động dưới hình thức kiến trúc lai. Các hàm đánh giá bằng tay có sẵn (evaluator.py, king_safety.py) tiếp tục đóng vai trò đánh giá vật chất sơ bộ, trong khi mạng nơ-ron cung cấp điểm số hiệu chỉnh chiến thuật. Tuy nhiên, theo quy luật phát triển được ghi nhận từ Stockfish và Pikafish, một khi kích thước kho dữ liệu huấn luyện vượt qua ngưỡng vài chục triệu thế cờ chất lượng, mạng NNUE tự nó sẽ học được toàn bộ kiến thức sâu sắc của chuyên gia (và vượt xa giới hạn đó). Khi hệ thống NNUE được kiểm chứng độ ổn định thông qua các bài kiểm tra đấu loại tự động, toàn bộ các mô-đun lượng giá thủ công có thể được gỡ bỏ hoàn toàn, tạo ra một kiến trúc AI Cờ Tướng tinh gọn, tốc độ siêu việt và sở hữu trí tuệ định vị ở mức độ kiện tướng quốc tế.
