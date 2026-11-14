# TÀI LIỆU TỔNG HỢP TOÀN BỘ LOGIC NGHIỆP VỤ HỆ THỐNG PT-CONNECT
> **Dự án:** Nền tảng kết nối Huấn luyện viên cá nhân (PT) và Học viên (PT-Connect)  
> **Mục tiêu tài liệu:** Tổng hợp toàn diện, chi tiết 100% các quy tắc nghiệp vụ (Business Rules), quy chế sàn, điều kiện kiểm tra, công thức tính toán tài chính và luồng xử lý của hệ thống. Tài liệu được thiết kế thuần nghiệp vụ, không chứa mã code kỹ thuật.

---

## MỤC LỤC TỔNG QUAN

1. [Tổng quan hệ thống & Các chủ thể tham gia (Actors & Roles)](#1-tổng-quan-hệ-thống--các-chủ-thể-tham-gia)
2. [Nghiệp vụ Đăng ký, Đăng nhập & Xác thực người dùng](#2-nghiệp-vụ-đăng-ký-đăng-nhập--xác-thực-người-dùng)
3. [Nghiệp vụ Quản lý Hồ sơ PT, Khóa học & Khung giờ làm việc](#3-nghiệp-vụ-quản-lý-hồ-sơ-pt-khóa-học--khung-giờ-làm-việc)
4. [Nghiệp vụ Tài chính, Nạp - Rút tiền & Cơ chế Thu hoa hồng nền tảng](#4-nghiệp-vụ-tài-chính-nạp---rút-tiền--cơ-chế-thu-hoa-hồng-nền-tảng)
5. [Nghiệp vụ Mua khóa học, Ký hợp đồng điện tử & Quản lý Kho buổi tập](#5-nghiệp-vụ-mua-khóa-học-ký-hợp-đồng-điện-tử--quản-lý-kho-buổi-tập)
6. [Nghiệp vụ Đặt lịch tập, Chống tranh chấp & Phê duyệt ca tập](#6-nghiệp-vụ-đặt-lịch-tập-chống-tranh-chấp--phê-duyệt-ca-tập)
7. [Nghiệp vụ Hủy lịch tập & Chính sách Phạt / Hoàn tiền / Đền bù](#7-nghiệp-vụ-hủy-lịch-tập--chính-sách-phạt--hoàn-tiền--đền-bù)
8. [Nghiệp vụ Điểm danh xác thực hai chiều qua mã OTP & Báo vắng](#8-nghiệp-vụ-điểm-danh-xác-thực-hai-chiều-qua-mã-otp--báo-vắng)
9. [Nghiệp vụ Đánh giá, Nhận xét & Tính sao tự động](#9-nghiệp-vụ-đánh-giá-nhận-xét--tính-sao-tự-động)
10. [Nghiệp vụ Giáo án huấn luyện cá nhân hóa theo Hợp đồng](#10-nghiệp-vụ-giáo-án-huấn-luyện-cá-nhân-hóa-theo-hợp-đồng)
11. [Nghiệp vụ Trung tâm Xử lý tranh chấp & Quy chế Trọng tài 48 giờ](#11-nghiệp-vụ-trung-tâm-xử-lý-tranh-chấp--quy-chế-trọng-tài-48-giờ)
12. [Nghiệp vụ Nhắn tin trao đổi trực tiếp 1-1](#12-nghiệp-vụ-nhắn-tin-trao-đổi-trực-tiếp-1-1)
13. [Nghiệp vụ Quản trị viên, Kiểm duyệt & Báo cáo phân tích](#13-nghiệp-vụ-quản-trị-viên-kiểm-duyệt--báo-cáo-phân-tích)
14. [Bảng ma trận vòng đời trạng thái dữ liệu (State Lifecycle Matrix)](#14-bảng-ma-trận-vòng-đời-trạng-thái-dữ-liệu)

---

## 1. TỔNG QUAN HỆ THỐNG & CÁC CHỦ THỂ THAM GIA

### 1.1. Mục tiêu cốt lõi của hệ thống
**PT-Connect** là sàn thương mại dịch vụ kết nối trực tuyến giữa **Học viên thể hình (Student)** có nhu cầu tập luyện cá nhân hóa và **Huấn luyện viên cá nhân (Personal Trainer - PT)**. Hệ thống giải quyết trọn vẹn bài toán vận hành phòng gym truyền thống:
* Loại bỏ tình trạng bùng lịch không rõ trách nhiệm, gian lận chấm công buổi tập giữa PT và học viên.
* Bảo vệ dòng tiền minh bạch: Học viên đóng tiền mua khóa học được lưu giữ an toàn, PT chỉ được giải ngân từng buổi sau khi học viên xác nhận đã hoàn thành ca tập.
* Ký hợp đồng điện tử có giá trị cam kết, xuất file PDF minh bạch.
* Cơ chế trọng tài công bằng đứng giữa hòa giải và xử lý tranh chấp khi có sự cố phát sinh.

### 1.2. Các chủ thể tham gia (Actors & Roles)
1. **Học viên (STUDENT)**:
   * Tìm kiếm PT phù hợp theo tên, khu vực tập luyện, chuyên môn thể hình.
   * Nạp tiền vào ví điện tử cá nhân.
   * Đăng ký mua khóa học, ký kết hợp đồng điện tử cam kết địa điểm tập cố định.
   * Đặt lịch học thử miễn phí (Trial) hoặc đặt lịch tập theo gói đã mua (Package).
   * Điểm danh hai chiều tại phòng tập thông qua mã số OTP bảo mật.
   * Đánh giá chất lượng và chấm điểm sao sau mỗi buổi tập hoàn thành.
   * Gửi khiếu nại, phản biện đối chứng khi xảy ra tranh chấp với PT.
2. **Huấn luyện viên cá nhân (PT)**:
   * Đăng ký hồ sơ chuyên môn, số năm kinh nghiệm, khu vực nhận dạy và tải lên chứng chỉ nghề nghiệp để chờ Admin xét duyệt.
   * Thiết lập và mở các khung giờ rảnh trong tuần để học viên vào đặt lịch.
   * Tạo và quản lý danh mục các gói khóa học (số buổi, thời hạn, học phí chuẩn).
   * Tiếp nhận, phê duyệt hoặc từ chối yêu cầu đặt lịch tập từ học viên.
   * Điểm danh buổi tập cùng học viên hoặc đánh dấu học viên vắng mặt (No-show).
   * Soạn thảo giáo án luyện tập chi tiết (bài tập, số hiệp, số lần lặp, mức tạ, clip hướng dẫn) cá nhân hóa cho từng hợp đồng học viên.
   * Quản lý ví thu nhập, tạo lệnh rút tiền về tài khoản ngân hàng cá nhân.
   * Tiếp nhận và gửi phản biện đối chứng khi có khiếu nại.
3. **Quản trị viên (ADMIN)**:
   * Thẩm định hồ sơ năng lực, bằng cấp của PT trước khi cho phép xuất hiện trên sàn.
   * Đóng vai trò Hội đồng Trọng tài độc lập, phân xử các vụ việc tranh chấp giữa PT và Học viên.
   * Quản lý trạng thái tài khoản người dùng (kích hoạt, cảnh cáo, khóa tài khoản vi phạm).
   * Giám sát dòng tiền, tổng doanh thu toàn sàn, trích thu 10% hoa hồng dịch vụ điều phối.
   * Theo dõi các báo cáo phân tích, tỷ lệ hủy lịch, điều tra các ca tập bất thường.

---

## 2. NGHIỆP VỤ ĐĂNG KÝ, ĐĂNG NHẬP & XÁC THỰC NGƯỜI DÙNG

### 2.1. Quy tắc đăng ký tài khoản (Registration Rules)
* **Duy nhất toàn hệ thống (Uniqueness)**: Email và Số điện thoại là định danh bắt buộc và duy nhất. Hệ thống từ chối đăng ký nếu email hoặc số điện thoại đã tồn tại.
* **Bảo mật mật khẩu**: Mật khẩu của người dùng bắt buộc phải được mã hóa một chiều qua thuật toán băm tiêu chuẩn an toàn (BCrypt). Mật khẩu thô không bao giờ được lưu trữ hay phản hồi trên đường truyền mạng.
* **Phân luồng khởi tạo tự động theo vai trò**:
  * **Nếu đăng ký là Học viên (`STUDENT`)**:
    * Tài khoản được tự động cấp trạng thái kích hoạt ngay lập tức (`ACTIVE`).
    * Hệ thống tự động tạo một Ví điện tử cá nhân (`Wallet`) với số dư khả dụng ban đầu là `0 VNĐ`, trạng thái ví `ACTIVE`.
  * **Nếu đăng ký là Huấn luyện viên (`PT`)**:
    * Tài khoản người dùng được tạo ở trạng thái chờ duyệt (`PENDING`).
    * Hệ thống đồng thời khởi tạo một bản ghi Hồ sơ PT (`PTProfile`) liên kết chặt chẽ với tài khoản, lưu các thông tin ban đầu: tiểu sử, số năm kinh nghiệm, khu vực nhận dạy, đường dẫn chứng chỉ bằng cấp, điểm đánh giá khởi điểm `0.0 sao`, trạng thái kiểm duyệt hồ sơ là `PENDING`.
    * Hệ thống tự động khởi tạo Ví điện tử cho PT với số dư ban đầu `0 VNĐ`.
    * PT chưa được phép xuất hiện trên danh sách công khai cho học viên tìm kiếm và chưa được mở khung giờ tập cho đến khi được Admin phê duyệt.

### 2.2. Quy tắc đăng nhập & Kiểm soát phiên (Login & Access Control)
* Người dùng xác thực bằng cặp thông tin `Email` và `Mật khẩu`.
* **Kiểm tra trạng thái tài khoản**:
  * Nếu tài khoản có trạng thái là `ACTIVE`: Cho phép đăng nhập thành công, cấp phát mã phiên làm việc bảo mật (JWT) có thời hạn, chứa định danh và quyền hạn (Role) của người dùng.
  * Nếu tài khoản có trạng thái là `SUSPENDED` (bị khóa/tạm ngừng do vi phạm hoặc gian lận): Hệ thống lập tức chặn truy cập và thông báo tài khoản đã bị khóa, yêu cầu liên hệ Ban Quản Trị.
  * Nếu tài khoản PT có trạng thái `PENDING`: Vẫn cho phép đăng nhập để xem thông báo trạng thái hồ sơ đang chờ xét duyệt hoặc bổ sung thông tin cá nhân.
* **Quy tắc phân quyền truy cập chức năng**:
  * Học viên chỉ được xem và thao tác trên dữ liệu ví, hợp đồng, lịch tập, khiếu nại của chính mình.
  * PT chỉ được quản lý khung giờ, khóa học, giáo án, lịch tập của các học viên đã đăng ký với mình.
  * Chỉ Admin mới có quyền truy cập vào bảng điều khiển tài chính toàn sàn, duyệt hồ sơ PT, khóa tài khoản và ban hành phán quyết trọng tài.

### 2.3. Cập nhật hồ sơ & Ảnh đại diện cá nhân
* Người dùng có thể cập nhật họ tên, ảnh đại diện, số điện thoại.
* Nếu thay đổi số điện thoại, hệ thống phải kiểm tra xem số điện thoại mới có bị trùng với người dùng khác hay không.
* **Quy chuẩn tải ảnh đại diện**: Chỉ chấp nhận tệp định dạng hình ảnh chuẩn (JPEG, PNG, WEBP, GIF), dung lượng không vượt quá 5MB.

---

## 3. NGHIỆP VỤ QUẢN LÝ HỒ SƠ PT, KHÓA HỌC & KHUNG GIỜ LÀM VIỆC

### 3.1. Quản lý Hồ sơ năng lực PT & Quy trình Kiểm duyệt của Admin
* **Thông tin hồ sơ PT bao gồm**:
  * Tiểu sử giới thiệu bản thân (Bio).
  * Số năm kinh nghiệm làm việc thực tế (bắt buộc $\ge 0$).
  * Danh sách các địa điểm/quận huyện/phòng tập nhận dạy (tuân thủ cấu trúc chuẩn hóa địa chỉ).
  * Ghi chú chính sách phụ thu di chuyển (nếu dạy tại nhà hoặc phòng ngoài).
  * Chứng chỉ hành nghề thể hình/bằng cấp chuyên môn (đường dẫn chứng chỉ công khai).
  * Điểm đánh giá trung bình (`average_rating`, từ 0.00 đến 5.00 sao) và tổng số lượt đánh giá (`total_reviews`).
* **Quy trình Phê duyệt của Admin**:
  * Admin vào danh sách các PT đang chờ duyệt (`PENDING`), mở kiểm tra chứng chỉ bằng cấp và thông tin khai báo.
  * **Hành động Duyệt (`APPROVE`)**: Trạng thái kiểm duyệt chuyển thành `VERIFIED`, tài khoản người dùng của PT chuyển thành `ACTIVE`. PT chính thức được kích hoạt trên hệ thống và hiển thị công khai trên giao diện "Khám Phá PT" của học viên.
  * **Hành động Từ chối (`REJECT`)**: Trạng thái hồ sơ chuyển thành `REJECTED`, tài khoản chuyển `SUSPENDED`, không hiển thị trên sàn.

### 3.2. Quản lý Khóa học / Gói tập luyện của PT (Course Management)
* PT tự xây dựng các gói khóa học phục vụ nhu cầu đa dạng của học viên (ví dụ: Giảm cân cấp tốc, Tăng cơ thể hình, Boxing rèn phản xạ, Yoga phục hồi...).
* **Các thuộc tính bắt buộc của một Khóa học**:
  * Tên khóa học (Title).
  * Mô tả mục tiêu, đối tượng phù hợp và quyền lợi.
  * Tổng số buổi tập (`total_sessions` bắt buộc $> 0$, ví dụ: 12, 24, 36 buổi).
  * Thời hạn giá trị sử dụng gói (`validity_days` bắt buộc $> 0$ ngày, ví dụ: 30, 60, 90 ngày kể từ ngày mua).
  * Giá niêm yết chuẩn (`base_price` bắt buộc $\ge 0$ VNĐ).
  * Trạng thái khóa học: `ACTIVE` (đang mở bán) hoặc `INACTIVE` (tạm ngừng nhận học viên mới).
* **Ràng buộc an toàn khi Sửa / Xóa Khóa học**:
  * PT được quyền chỉnh sửa thông tin mô tả, học phí, số buổi của khóa học. Việc thay đổi này chỉ áp dụng cho các học viên đăng ký mới sau thời điểm sửa, không làm ảnh hưởng đến các hợp đồng đã ký trước đó.
  * **Cấm xóa cứng (Delete Constraint)**: Nếu khóa học đã có ít nhất một học viên đăng ký hợp đồng (kể cả hợp đồng đã kết thúc), hệ thống **nghiêm cấm xóa cứng** bản ghi khóa học khỏi cơ sở dữ liệu để bảo vệ lịch sử thanh toán và tính toàn vẹn của hợp đồng. Thay vào đó, hệ thống chỉ cho phép chuyển trạng thái sang `INACTIVE` (ẩn khỏi danh mục bán).

### 3.3. Quản lý Khung giờ làm việc rảnh (Availability Slots)
* Để học viên có thể đặt lịch tập, PT phải chủ động tạo các khung giờ rảnh của mình trong tuần.
* **Quy tắc tạo khung giờ**:
  * Mỗi khung giờ có mốc bắt đầu (`startTime`) và kết thúc (`endTime`).
  * Giờ kết thúc bắt buộc phải sau giờ bắt đầu.
  * Khung giờ không được nằm trong quá khứ so với thời điểm tạo.
  * **Quy tắc chống chồng lấn lịch (Overlap Check)**: Hệ thống kiểm tra trong cùng một PT, thời gian của slot mới không được phép giao cắt hoặc trùng lặp với bất kỳ slot nào đã tồn tại trước đó.
  * Trạng thái khởi tạo của slot luôn là `AVAILABLE` (sẵn sàng đón học viên).
* **Quy tắc Xóa khung giờ**:
  * PT chỉ được quyền xóa khung giờ khi slot đó đang ở trạng thái `AVAILABLE`.
  * Nếu khung giờ đang có ca tập ở trạng thái `PENDING` (chờ duyệt) hoặc `CONFIRMED` (đã duyệt), hệ thống kiên quyết ngăn chặn thao tác xóa để đảm bảo quyền lợi của học viên.

---

## 4. NGHIỆP VỤ TÀI CHÍNH, NẠP - RÚT TIỀN & CƠ CHẾ THU HOA HỒNG NỀN TẢNG

### 4.1. Cơ cấu Ví điện tử & Đảm bảo an toàn số dư
* Mỗi tài khoản người dùng sở hữu duy nhất 1 ví điện tử nội bộ.
* Mọi phép toán cộng trừ tiền tệ đều sử dụng kiểu dữ liệu số thập phân chính xác cao (`BigDecimal`), triệt tiêu hoàn toàn sai số dấu phẩy động nhị phân.
* **Số dư ví gồm hai thành phần**:
  * `balance`: Tổng số dư thực tế trong ví.
  * `locked_balance`: Số dư đang bị đóng băng tạm thời (dùng khi xử lý các nghiệp vụ ký quỹ hoặc giữ chỗ, mặc định $\ge 0$).
  * **Số dư khả dụng để chi tiêu/rút tiền** = `balance - locked_balance`.
* Mọi giao dịch phát sinh đều sinh một mã tham chiếu giao dịch duy nhất (`transaction_ref` có tiền tố phân loại như `TXN_TOPUP_...`, `TXN_BUY_...`, `TXN_EARN_...`, `TXN_WD_...`) và lưu vết dòng tiền chi tiết.

### 4.2. Nghiệp vụ Nạp tiền ví (Top-up)
* Học viên có thể nạp tiền vào ví qua các phương thức được hỗ trợ (Chuyển khoản ngân hàng, Quét mã thanh toán).
* **Quy tắc**: Số tiền nạp bắt buộc phải $> 0$ VNĐ.
* Tiền được cộng trực tiếp vào số dư khả dụng của học viên ngay khi giao dịch thành công.

### 4.3. Nghiệp vụ Rút tiền ví (Withdrawal)
* Cả PT và Học viên đều có thể rút số dư khả dụng về tài khoản ngân hàng cá nhân.
* **Các điều kiện kiểm tra nghiêm ngặt khi Rút tiền**:
  1. Ví của người dùng phải ở trạng thái hoạt động (`ACTIVE`). Nếu ví bị đóng băng (`FROZEN`), hệ thống từ chối rút tiền.
  2. **Hạn mức rút tiền tối thiểu**: Số tiền yêu cầu rút bắt buộc phải $\ge 50.000$ VNĐ / lần rút.
  3. **Kiểm tra số dư khả dụng**: Số tiền rút phải $\le (balance - locked\_balance)$. Nếu rút quá số dư khả dụng, giao dịch bị từ chối với lỗi không đủ số dư.
  4. Người dùng phải cung cấp đầy đủ: Tên ngân hàng thụ hưởng, Số tài khoản ngân hàng, Tên chủ tài khoản hợp lệ.
* Khi thỏa mãn, hệ thống trừ tiền trong ví và tạo bản ghi giao dịch rút tiền `WITHDRAW` với trạng thái `SUCCESS`.

### 4.4. Chính sách Thu hoa hồng & Giải ngân thù lao ca tập (Platform Commission Policy)
Hệ thống vận hành theo mô hình sàn chia sẻ doanh thu:
* **Tỷ lệ trích thưởng cố định**:
  * **90% Thù lao**: Chuyển trả vào ví của Huấn luyện viên cá nhân (PT).
  * **10% Phí dịch vụ sàn**: Thu về Quỹ doanh thu nền tảng (Ví của Admin) phục vụ chi phí vận hành máy chủ, tiếp thị và quỹ phân xử trọng tài.
* **Thời điểm kích hoạt giải ngân**:
  * Nền tảng **không giải ngân toàn bộ tiền khóa học một lần** khi học viên mua gói, nhằm bảo vệ học viên trước rủi ro PT bỏ dạy giữa chừng.
  * Tiền học phí được giữ lại an toàn trên hệ thống. Sau mỗi buổi tập hoàn thành (`COMPLETED`) hợp lệ:
    * Hệ thống tự động tính thù lao buổi tập: $Tiền\_buổi = \frac{Tổng\_học\_phí\_khóa}{Tổng\_số\_buổi}$.
    * Hệ thống trích $90\% \times Tiền\_buổi$ cộng trực tiếp vào ví của PT (`PaymentType.EARNING`).
    * Hệ thống trích $10\% \times Tiền\_buổi$ cộng vào ví doanh thu của Admin (`PaymentType.EARNING`, mã `TXN_COMMISSION_...`).

---

## 5. NGHIỆP VỤ MUA KHÓA HỌC, KÝ HỢP ĐỒNG ĐIỆN TỬ & QUẢN LÝ KHO BUỔI TẬP

### 5.1. Quy trình Mua khóa học & Ký kết Hợp đồng (Enrollment Process)
Khi học viên quyết định đăng ký một gói tập của PT, quy trình diễn ra khép kín trong một giao dịch cơ sở dữ liệu duy nhất (`@Transactional`):
1. **Kiểm tra trạng thái khóa học**: Gói tập phải đang ở trạng thái `ACTIVE` (đang mở bán).
2. **Quy tắc chống mua chồng gói chưa học xong (Active Enrollment Conflict Check)**:
   * Nếu học viên hiện đang có một hợp đồng `ACTIVE` với chính khóa học này mà vẫn còn buổi học chưa hoàn thành (`remainingSessions > 0`), hệ thống sẽ **từ chối đăng ký mới**.
   * *Mục đích*: Ngăn chặn tình trạng học viên bấm nhầm mua nhiều lần hoặc tồn đọng buổi tập quá hạn gây tranh chấp biểu phí. Học viên bắt buộc phải tập hết số buổi của hợp đồng cũ trước khi mua gói tiếp theo.
3. **Địa điểm tập luyện cố định cam kết**:
   * Học viên bắt buộc phải chọn hoặc điền một địa điểm tập luyện cố định duy nhất (`trainingLocation`, ví dụ: *FitZone Thanh Xuân* hoặc *Cali Cầu Giấy*).
   * Địa điểm này sẽ được in trực tiếp vào hợp đồng pháp lý, không được tự ý thay đổi trong suốt quá trình tập để tránh bất đồng về chi phí di chuyển giữa PT và học viên.
4. **Thanh toán tiền khóa học qua ví**:
   * Hệ thống kiểm tra số dư ví học viên. Nếu số dư khả dụng $< Giá\_khóa\_học$, giao dịch bị hủy bỏ ngay lập tức, tiền trong ví được giữ nguyên vẹn.
   * Nếu đủ tiền: Trừ chính xác số tiền khóa học khỏi ví học viên và ghi nhận giao dịch `PURCHASE_PACKAGE`.

### 5.2. Khởi tạo Hợp đồng & Cơ chế Kho buổi tập (Session Inventory)
* **Khởi tạo dữ liệu hợp đồng (`Enrollment`)**:
  * Tổng số buổi (`total_sessions`): Bằng số buổi cam kết của gói khóa học.
  * Kho buổi tập khả dụng (`remaining_sessions`): Khởi tạo bằng đúng `total_sessions`.
  * Ngày bắt đầu (`start_date`): Ngày hiện tại mua khóa học.
  * Ngày hết hạn (`end_date`): Bằng $Ngày\_bắt\_đầu + validity\_days$ của khóa học.
  * Trạng thái hợp đồng ban đầu: `ACTIVE`.
* **Tự động xuất Hợp đồng điện tử PDF (E-Contract PDF Generation)**:
  * Ngay khi giao dịch hoàn tất, hệ thống tự động sinh một bản Hợp đồng điện tử định dạng PDF chuẩn.
  * File PDF chứa đầy đủ thông tin: Mã hợp đồng, Ngày ký kết, Mã giao dịch tài chính đối soát, Thông tin bên A (Học viên: Họ tên, Email, SĐT), Thông tin bên B (PT: Họ tên, Email, SĐT, Bằng cấp), Tên gói tập, Địa điểm tập luyện cam kết, Thời hạn hợp đồng, và các điều khoản chế tài xử phạt khi hủy lịch hoặc vi phạm nghĩa vụ.
  * Đường dẫn hợp đồng được lưu vào hệ thống, cho phép cả Học viên và PT tải về lưu trữ hoặc in ấn bất kỳ lúc nào.

---

## 6. NGHIỆP VỤ ĐẶT LỊCH TẬP, CHỐNG TRANH CHẤP & PHÊ DUYỆT CA TẬP

### 6.1. Hai hình thức đặt lịch tập (Booking Types)
1. **Lịch tập thử (TRIAL)**:
   * Dành cho học viên muốn trải nghiệm phong cách huấn luyện của PT trước khi xuống tiền mua gói lớn.
   * Học phí buổi tập thử: `sessionFee = 0 VNĐ`.
   * **Quy tắc giới hạn nghiêm ngặt (Single Trial Rule)**: Mỗi học viên chỉ được phép đặt lịch tập thử **tối đa 1 lần duy nhất với mỗi Huấn luyện viên**. Hệ thống chặn tuyệt đối nếu học viên cố tình đặt thử lần thứ 2 với cùng một PT.
   * Lịch tập thử không yêu cầu mã hợp đồng (`enrollmentId = NULL`).
2. **Lịch tập theo gói khóa học (PACKAGE)**:
   * Yêu cầu học viên phải có Hợp đồng hợp lệ (`enrollmentId NOT NULL`).
   * **Điều kiện hợp đồng để được đặt lịch**:
     * Hợp đồng phải ở trạng thái `ACTIVE`.
     * Thời điểm diễn ra ca tập phải nằm trong khoảng từ `start_date` đến `end_date` của hợp đồng (chưa hết hạn).
     * Kho buổi tập còn lại phải còn buổi: `remaining_sessions > 0`.
   * **Đơn giá buổi tập ghi nhận vào ca (`sessionFee`)**:  
     $sessionFee = \frac{Học\_phí\_hợp\_đồng}{Tổng\_số\_buổi\_hợp\_đồng}$.

### 6.2. Cơ chế Khóa bi quan chống tranh chấp lịch (Pessimistic Locking & Overlap Control)
Khi nhiều học viên cùng truy cập và bấm đặt cùng 1 khung giờ rảnh của PT tại cùng một tích tắc mili-giây, hệ thống áp dụng cơ chế bảo vệ tối cao:
* **Khóa dữ liệu mức Database (`Pessimistic Write Lock`)**:
  * Khi Học viên A gửi yêu cầu đặt lịch cho Slot X, câu lệnh SQL sẽ khóa chặt dòng dữ liệu của Slot X lại (`SELECT ... FOR UPDATE`).
  * Yêu cầu của Học viên B đến sau bắt buộc phải xếp hàng chờ giao dịch của Học viên A hoàn tất.
* **Các bước thẩm định hợp lệ khi đặt lịch**:
  1. Kiểm tra trạng thái slot: Slot bắt buộc phải là `AVAILABLE`. Nếu đã bị đặt trước (`BOOKED` hoặc `LOCKED`), ném lỗi xung đột lịch (Conflict) và từ chối ngay.
  2. Kiểm tra mốc thời gian: Giờ bắt đầu của slot không được ở trong quá khứ.
  3. **Kiểm tra trùng lịch của chính Học viên**: Học viên không được có bất kỳ ca tập nào khác (ở trạng thái `PENDING` hoặc `CONFIRMED`) trùng giờ hoặc giao cắt với khung giờ đang đặt.
* **Tạm trừ kho buổi tập ngay khi đặt**:
  * Đối với hình thức `PACKAGE`, ngay khi lệnh đặt lịch thành công, hệ thống lập tức tạm trừ 1 buổi trong hợp đồng của học viên:  
    $remaining\_sessions = remaining\_sessions - 1$.
  * Slot chuyển trạng thái sang `BOOKED`.
  * Bản ghi ca tập (`Booking`) được tạo với trạng thái ban đầu là **`PENDING`** (Chờ Huấn luyện viên phê duyệt).

### 6.3. Quy trình Phê duyệt / Từ chối ca tập của PT
Học viên sau khi đặt lịch phải chờ PT phản hồi:
* **Trường hợp PT Chấp thuận (`APPROVE`)**:
  * Ca tập chuyển trạng thái từ `PENDING` $\rightarrow$ **`CONFIRMED`**.
  * Ca tập chính thức có hiệu lực, sẵn sàng bước vào khâu tập luyện và điểm danh.
* **Trường hợp PT Từ chối (`REJECT`)**:
  * Áp dụng khi PT bận đột xuất hoặc có lý do chính đáng không thể nhận ca. PT bắt buộc phải cung cấp lý do từ chối.
  * Ca tập chuyển trạng thái từ `PENDING` $\rightarrow$ **`CANCELLED`**.
  * **Giải phóng khung giờ**: Trạng thái slot được hoàn trả ngay về **`AVAILABLE`** để học viên khác có thể đặt.
  * **Hoàn trả kho buổi tập**: Nếu là ca theo gói (`PACKAGE`), hệ thống hoàn trả lại 1 buổi tập vào kho hợp đồng của học viên ($remaining\_sessions = remaining\_sessions + 1$).
  * Ca từ chối khi đang `PENDING` không phát sinh bất kỳ khoản tiền phạt hay đền bù nào cho đôi bên.

---

## 7. NGHIỆP VỤ HỦY LỊCH TẬP & CHÍNH SÁCH PHẠT / HOÀN TIỀN / ĐỀN BÙ

Chính sách hủy lịch của PT-Connect được thiết kế chặt chẽ nhằm bảo đảm tính kỷ luật, tôn trọng thời gian của nhau nhưng vẫn nhân văn và công bằng, phân định rõ ràng theo vai trò của người hủy và mốc thời gian **24 giờ trước ca tập**.

```
                           BẢNG QUY TẮC XỬ LÝ HỦY CA TẬP
┌──────────┬─────────────────┬─────────────────┬──────────────────┬─────────────────┐
│ Người hủy│ Trạng thái ca   │ Thời điểm hủy   │ Hoàn buổi học    │ Chế tài tài chính│
├──────────┼─────────────────┼─────────────────┼──────────────────┼─────────────────┤
│ Học viên │ PENDING         │ Mọi lúc         │ Có (Hoàn 1 buổi) │ Không phạt      │
│ Học viên │ CONFIRMED       │ Trước >= 24 giờ │ Có (Hoàn 1 buổi) │ Phạt học viên 50%│
│          │                 │                 │                  │ Đền bù PT 50%    │
│ Học viên │ CONFIRMED       │ Sát giờ < 24 giờ│ KHÔNG (Mất buổi) │ PT hưởng 100%    │
│          │                 │                 │                  │ (sàn thu 10% phí)│
├──────────┼─────────────────┼─────────────────┼──────────────────┼─────────────────┤
│ PT       │ PENDING (Từ chối) Mọi lúc         │ Có (Hoàn 1 buổi) │ Không phạt      │
│ PT       │ CONFIRMED       │ Trước >= 24 giờ │ Có (Hoàn 1 buổi) │ Không phạt      │
│ PT       │ CONFIRMED       │ Sát giờ < 24 giờ│ Có (Hoàn 1 buổi) │ Phạt PT 100%    │
│          │                 │                 │                  │ Đền bù học viên  │
├──────────┼─────────────────┼─────────────────┼──────────────────┼─────────────────┤
│ ADMIN    │ Mọi trạng thái  │ Bất khả kháng   │ Có (Khôi phục)   │ Không phạt đôi bên│
└──────────┴─────────────────┴─────────────────┴──────────────────┴─────────────────┘
```

### 7.1. Chi tiết Chính sách Hủy lịch phía Học viên (Student Cancellation Policy)
1. **Ca đang chờ duyệt (`PENDING`)**:
   * Học viên có toàn quyền hủy bất kỳ lúc nào mà không chịu bất kỳ chế tài nào.
   * Hệ thống hoàn trả ngay 1 buổi vào hợp đồng ($remaining\_sessions + 1$). Slot được giải phóng về `AVAILABLE`.
2. **Ca đã được PT duyệt (`CONFIRMED`) và Học viên hủy báo trước $\ge 24$ giờ**:
   * *Ý nghĩa*: Học viên có ý thức báo sớm, PT vẫn có cơ hội sắp xếp việc khác hoặc mở lại cho người khác đặt.
   * *Quyền lợi buổi tập*: Học viên **được hoàn trả 1 buổi tập** vào kho hợp đồng ($remaining\_sessions + 1$).
   * *Chế tài tài chính*: Học viên bị **phạt trừ 50% tiền buổi học** từ ví để đền bù tổn thất giữ chỗ cho PT ($50\% \times sessionFee$).
3. **Ca đã được PT duyệt (`CONFIRMED`) và Học viên hủy sát giờ ($< 24$ giờ)**:
   * *Ý nghĩa*: Hủy cận giờ khiến PT bị động, lãng phí thời gian di chuyển và mất cơ hội nhận ca khác.
   * *Quyền lợi buổi tập*: Học viên **bị mất buổi tập này** (không hoàn lại vào kho hợp đồng).
   * *Chế tài tài chính*: Toàn bộ tiền của buổi học ($sessionFee$) được giải ngân đền bù: 90% chuyển vào ví của PT, 10% thu phí dịch vụ sàn.
4. **Đối với ca tập thử (`TRIAL`)**:
   * Do buổi tập thử có phí bằng 0 VNĐ, khi học viên hủy chỉ giải phóng khung giờ về `AVAILABLE`, không phát sinh đền bù tiền hay hoàn buổi.

### 7.2. Chi tiết Chính sách Hủy lịch phía Huấn luyện viên (PT Cancellation Policy)
1. **Ca đã duyệt (`CONFIRMED`) và PT hủy báo trước $\ge 24$ giờ**:
   * Học viên được hoàn trả 1 buổi tập vào hợp đồng.
   * Khung giờ được giải phóng. PT không bị trừ tiền phạt nhưng hệ thống ghi nhận lịch sử hủy ca.
2. **Ca đã duyệt (`CONFIRMED`) và PT hủy sát giờ ($< 24$ giờ)**:
   * *Ý nghĩa*: PT vi phạm cam kết sát giờ làm ảnh hưởng nghiêm trọng đến lịch trình của học viên.
   * *Hoàn trả quyền lợi*: Học viên được hoàn trả lại 1 buổi tập vào hợp đồng.
   * *Đền bù học viên*: Hệ thống trích tiền đền bù **100% giá trị một buổi học** ($100\% \times sessionFee$) cộng vào ví học viên để xin lỗi về sự bất tiện.
   * *Xử phạt PT*: Hệ thống phạt trừ trực tiếp **100% giá trị buổi học** ($100\% \times sessionFee$) từ ví của PT.

### 7.3. Chính sách Hủy lịch do Sự cố Bất khả kháng (Admin Force Majeure Policy)
* Áp dụng khi phòng gym đóng cửa đột xuất do thiên tai, dịch bệnh, hoặc một trong hai bên gặp tai nạn y tế đột xuất có xác nhận hợp lệ.
* Admin có thẩm quyền can thiệp hủy ca: Khôi phục lại 1 buổi tập cho học viên vào hợp đồng, giải phóng khung giờ, không áp dụng bất kỳ khoản phạt hay khấu trừ tiền nào của cả hai bên.

---

## 8. NGHIỆP VỤ ĐIỂM DANH XÁC THỰC HAI CHIỀU QUA MÃ OTP & BÁO VẮNG

Hệ thống loại bỏ hoàn toàn cơ chế điểm danh một chiều dễ gian lận (như PT tự bấm hoàn thành mà không dạy), thay bằng **Quy trình xác thực chéo hai phía thông qua mã OTP bảo mật tại phòng tập**.

### 8.1. Điều kiện & Giới hạn thời gian mở điểm danh
* Ca tập bắt buộc phải đang ở trạng thái đã được xác nhận (**`CONFIRMED`**).
* **Quy tắc khung giờ vàng (15-Minute Advance Guardrail)**:
  * Một ca tập chỉ được phép mở phiên điểm danh **trước tối đa 15 phút** so với giờ bắt đầu ca tập ($now \ge startTime - 15\text{ phút}$).
  * *Mục đích*: Ngăn chặn tình trạng học viên và PT thông đồng "chấm công khống" từ nhiều ngày hoặc nhiều giờ trước khi ca tập thực sự diễn ra.

### 8.2. Quy trình sinh & Xác thực mã OTP chéo
1. **Bước 1: Mở phiên điểm danh & Sinh mã OTP ngẫu nhiên**:
   * Một trong hai bên (thường là Học viên khi đã có mặt tại phòng tập) nhấn nút **"Mở điểm danh / Nhận mã OTP"**.
   * Hệ thống tự động sinh một mã OTP bí mật gồm **6 chữ số ngẫu nhiên** (ví dụ: `849201`), có thời hạn hiệu lực chính xác trong **30 phút**.
   * Mã OTP hiển thị nổi bật trên màn hình của người mở điểm danh.
2. **Bước 2: Phân loại Đúng giờ hay Đến muộn**:
   * Nếu thời điểm mở điểm danh sau mốc bắt đầu ca tập quá 15 phút ($now > startTime + 15\text{ phút}$): Ghi nhận trạng thái điểm danh là **`LATE`** (Đến muộn).
   * Nếu thời điểm mở điểm danh đúng giờ ($now \le startTime + 15\text{ phút}$): Ghi nhận trạng thái điểm danh là **`PRESENT`** (Đúng giờ).
3. **Bước 3: Nhập mã đối soát chéo**:
   * Người mở điểm danh đọc hoặc cho đối tác (PT) xem mã số OTP.
   * PT mở màn hình duyệt ca tập, nhấn nút **"Xác nhận OTP"**, nhập chuỗi 6 số và gửi lên hệ thống.
   * Nếu mã nhập sai hoặc đã quá 30 phút hiệu lực: Hệ thống lập tức từ chối và cảnh báo lỗi.
   * Nếu mã chính xác: Hệ thống đồng thời xác nhận cả hai phía: `studentConfirmed = true` và `ptConfirmed = true`, lưu vết thời gian xác nhận (`checkInTime = now`).

### 8.3. Tự động Giải ngân & Hoàn tất Hợp đồng khi Hoàn thành ca
Ngay khi mã OTP được xác thực thành công:
1. **Đổi trạng thái ca tập**: Ca tập chuyển trạng thái sang **`COMPLETED`** (Đã hoàn thành trọn vẹn). Mã OTP được thu hồi ngay lập tức để chống tái sử dụng.
2. **Tự động giải ngân thù lao buổi tập**:
   * Hệ thống kích hoạt thanh toán tự động: Chuyển $90\%$ tiền buổi học vào ví của PT, trích $10\%$ hoa hồng vào ví Admin.
3. **Kiểm tra kết thúc Hợp đồng**:
   * Hệ thống kiểm tra hợp đồng liên kết: Nếu kho buổi còn lại đã hết ($remaining\_sessions == 0$) và **không còn bất kỳ ca tập nào khác đang `PENDING` hoặc `CONFIRMED`**:
   * Hợp đồng chính thức chuyển trạng thái từ `ACTIVE` $\rightarrow$ **`COMPLETED`** (Đã hoàn thành toàn bộ khóa học).

### 8.4. Quy trình Báo vắng mặt (Học viên No-Show)
* Nếu đến giờ tập mà học viên không có mặt và không hề liên lạc xin đổi lịch, PT chờ sau 15-30 phút có quyền nhấn nút **"Đánh dấu học viên vắng mặt (ABSENT)"** kèm lý do giải trình.
* **Quy tắc chế tài No-Show**:
  * Điểm danh ghi nhận trạng thái **`ABSENT`** (`studentConfirmed = false`, `ptConfirmed = true`).
  * Ca tập vẫn được tính là đã diễn ra và chuyển sang **`COMPLETED`**; học viên **bị mất buổi tập đó** trong hợp đồng.
  * **Bảo vệ quyền lợi PT**: PT vẫn được nhận đủ 90% thù lao buổi tập để bù đắp công sức và thời gian đã đến phòng tập chờ đợi.

---

## 9. NGHIỆP VỤ ĐÁNH GIÁ, NHẬN XÉT & TÍNH SAO TỰ ĐỘNG

### 9.1. Điều kiện gửi đánh giá (Review Conditions)
* Chỉ học viên sở hữu ca tập mới có quyền đánh giá buổi học đó.
* **Ràng buộc hoàn thành**: Ca tập bắt buộc phải ở trạng thái **`COMPLETED`** mới được gửi đánh giá (không được đánh giá ca đang chờ, đã hủy hay chưa học).
* **Ràng buộc duy nhất (1-1 Constraint)**: Mỗi ca tập hoàn thành chỉ được phép gửi đánh giá **đúng 1 lần duy nhất** (ràng buộc `booking_id UNIQUE`). Không thể sửa đổi để spam số lượng đánh giá.
* Điểm đánh giá: Thang điểm chuẩn từ 1 đến 5 sao (sao nguyên) kèm nội dung bình luận nhận xét chi tiết.

### 9.2. Cơ chế Tự động tính sao qua MySQL Database Trigger
Để đảm bảo hiệu năng tối ưu, tính toàn vẹn dữ liệu đa luồng và giảm tải cho tầng ứng dụng, logic tính toán điểm uy tín của PT được xử lý hoàn toàn tự động ở tầng cơ sở dữ liệu:
* **Trigger kích hoạt**: Mỗi khi một đánh giá mới được thêm vào (`AFTER INSERT`), sửa đổi (`AFTER UPDATE`), hoặc xóa bỏ (`AFTER DELETE`) trong bảng `reviews`:
  * Hệ thống cơ sở dữ liệu tự động truy vết ngược từ đánh giá qua ca tập đến hồ sơ của PT tương ứng.
  * Tự động tính toán lại:
    * Điểm trung bình cộng: $average\_rating = \text{ROUND}(\text{AVG}(rating), 2)$.
    * Tổng số lượt đánh giá: $total\_reviews = \text{COUNT}(rating)$.
  * Tự động cập nhật trực tiếp hai chỉ số này vào bản ghi của `pt_profiles`.
* Giao diện học viên khi tìm kiếm PT sẽ luôn nhìn thấy điểm sao trung bình và số lượt đánh giá thực tế cập nhật tức thì.

---

## 10. NGHIỆP VỤ GIÁO ÁN HUẤN LUYỆN CÁ NHÂN HÓA THEO HỢP ĐỒNG

### 10.1. Nguyên lý Cá nhân hóa theo Hợp đồng (Enrollment-Bound Plan)
* Trong mô hình thể hình cá nhân (PT 1-kèm-1), mỗi học viên có thể trạng, chỉ số InBody (mỡ/cơ), bệnh lý nền và mục tiêu khác nhau.
* **Quy tắc nghiệp vụ**: Giáo án huấn luyện (`WorkoutPlan`) **bắt buộc phải gắn liền với một Hợp đồng cụ thể** (`enrollment_id NOT NULL`), không được tạo giáo án vô định danh. Huấn luyện viên chỉ soạn giáo án cho học viên sau khi hợp đồng đã được ký kết.

### 10.2. Cấu trúc Giáo án & Chi tiết Bài tập (Workouts)
1. **Thông tin Giáo án (`WorkoutPlan`)**:
   * Tiêu đề giáo án (ví dụ: *Lộ trình giảm mỡ bụng 4 tuần đầu*).
   * Mục tiêu huấn luyện cụ thể (ví dụ: *Tăng khối cơ vai ngực, giảm 3% mỡ cơ thể*).
   * Mốc thời gian áp dụng: Ngày bắt đầu và ngày kết thúc (phải nằm trong thời hạn của Hợp đồng).
2. **Chi tiết từng Bài tập (`Workout`)**:
   * Tên bài tập (ví dụ: *Barbell Bench Press*, *Bulgarian Split Squat*, *Lat Pulldown*).
   * Nhóm cơ mục tiêu tác động: Ngực, Lưng xô, Đùi trước, Mông đùi sau, Vai, Tay trước/sau, Cơ lõi (Core).
   * Khối lượng vận động chuẩn: Số hiệp (`sets` $> 0$), số lần lặp mỗi hiệp (`reps` $> 0$), mức tạ đề xuất (`weightKg`), thời gian nghỉ giữa các hiệp (`restSeconds` $\ge 0$).
   * Đường dẫn video hướng dẫn chuẩn form (`videoDemoUrl`): Giúp học viên xem trước kỹ thuật động tác để tránh chấn thương khi tự ôn luyện.

### 10.3. Quyền hạn truy cập Giáo án
* **Quyền tạo/sửa/xóa bài tập**: Chỉ duy nhất PT phụ trách hợp đồng đó mới có quyền thêm, sửa, xóa các bài tập trong giáo án.
* **Quyền xem giáo án**: Học viên sở hữu hợp đồng, PT phụ trách và Quản trị viên (Admin) có quyền xem toàn bộ nội dung giáo án.

---

## 11. NGHIỆP VỤ TRUNG TÂM XỬ LÝ TRANH CHẤP & QUY CHẾ TRỌNG TÀI 48 GIỜ

Khi xảy ra bất đồng ý kiến giữa PT và Học viên mà hai bên không thể tự thương lượng, hệ thống cung cấp Trung tâm Phân xử Trọng tài (Arbitration Dispute Center) do Ban Quản Trị làm chủ tọa.

### 11.1. Các dạng Tranh chấp được tiếp nhận
1. **Khiếu nại ca tập đơn lẻ**:
   * Học viên khiếu nại: HLV vắng mặt không báo trước (No-show), HLV đến muộn $> 15$ phút hoặc cắt bớt giờ tập, nghi vấn ép điểm danh OTP sai quy trình, thái độ thô lỗ/vi phạm đạo đức nghề nghiệp.
   * HLV khiếu nại: Học viên bùng lịch không đến nhưng từ chối trừ buổi, học viên có hành vi thiếu chuẩn mực hoặc vi phạm an toàn phòng tập.
2. **Khiếu nại yêu cầu Thanh lý / Hủy bỏ toàn bộ Hợp đồng**:
   * HLV liên tục không xếp được lịch dạy, hủy hẹn nhiều lần làm trôi thời hạn hợp đồng.
   * HLV không thực hiện đúng cam kết giáo án, thiếu chuyên môn.
   * Sự cố y tế, chấn thương thể thao hoặc chuyển nơi cư trú bất khả kháng.
   * Học viên biến mất (Ghosting), bùng lịch kéo dài và mất liên lạc $> 14$ ngày (HLV yêu cầu tất toán hợp đồng).

### 11.2. Quy chế Trọng tài Chống phán quyết độc đoán (48-Hour Anti-Arbitrary Clause)
Để đảm bảo tính khách quan và dân chủ tuyệt đối, tránh việc Admin phán quyết một chiều khi mới chỉ nghe một bên trình bày:
* **Quy tắc thời hạn phản biện 48 giờ**:
  * Khi Đơn khiếu nại được tạo, bên bị khiếu nại (bị đơn) được cấp **thời hạn 48 giờ** để gửi "Bản phản biện đối chứng" (`counter_statement`) và bổ sung chứng cứ chứng minh mình vô tội.
  * **Hạn chế quyền của Admin**: Trong vòng 48 giờ kể từ lúc tạo khiếu nại, nếu bên bị khiếu nại **chưa gửi bản phản biện**, hệ thống **chặn không cho Admin ban hành phán quyết**. Admin chỉ được phép phán quyết khi:
    * Bên bị khiếu nại đã gửi bản phản biện; **HOẶC**
    * Đã quá thời hạn 48 giờ mà bên bị khiếu nại vẫn im lặng bỏ quyền phản biện; **HOẶC**
    * Admin sử dụng quyền ghi đè khẩn cấp có giải trình đặc biệt (Bypass 48h).

### 11.3. Yêu cầu Bổ sung Bằng chứng (Additional Evidence Request)
* Trong quá trình thụ lý, Admin có thể gửi trát yêu cầu bổ sung chứng cứ tới: Học viên, HLV hoặc Cả hai bên.
* Trạng thái hồ sơ chuyển sang **`AWAITING_ADDITIONAL_EVIDENCE`**.
* Hai bên có thể tải lên hình ảnh biên bản phòng tập, ảnh chụp tin nhắn trao đổi, giấy khám viện y tế để làm căn cứ phán quyết.

### 11.4. Các loại Phán quyết Trọng tài & Cơ chế Thực thi tự động
Khi Admin ban hành phán quyết, hệ thống tự động chạy các giao dịch tài chính để giải quyết dứt điểm vụ việc:
1. **Xử thắng cho Học viên (`REFUND_STUDENT`)**:
   * *Nội dung*: HLV có lỗi vi phạm.
   * *Thực thi*: Hoàn trả 100% học phí buổi tập vào ví của học viên; khôi phục lại 1 buổi tập vào hợp đồng cho học viên; hủy bỏ ca tập vi phạm; khiển trách hoặc cảnh cáo tài khoản PT.
2. **Xử thắng cho Huấn luyện viên (`PAID_PT`)**:
   * *Nội dung*: Học viên khiếu nại vô căn cứ, HLV thực hiện đúng quy trình.
   * *Thực thi*: Xác nhận ca tập hợp lệ và chuyển trạng thái sang `COMPLETED`; giải ngân thù lao buổi tập vào ví PT (sau khi trừ 10% phí sàn); khấu trừ dứt điểm buổi tập của học viên.
3. **Hòa giải Sự cố Bất khả kháng (`RESOLVED_FORCE_MAJEURE`)**:
   * *Nội dung*: Cả hai bên đều gặp sự cố khách quan xác minh hợp lệ.
   * *Thực thi*: Khôi phục 1 buổi tập vào hợp đồng cho học viên, ca tập hủy bỏ, không áp dụng bất kỳ khoản phạt hay khấu trừ tiền nào của đôi bên.
4. **Thanh lý toàn bộ Hợp đồng - Hoàn tiền học viên (`CANCEL_CONTRACT_REFUND_STUDENT`)**:
   * *Nội dung*: HLV vi phạm cam kết nghiêm trọng hoặc học viên gặp sự cố y tế không thể tiếp tục tập luyện.
   * *Thực thi*: Chuyển trạng thái hợp đồng sang `CANCELLED`. Tính toán số tiền hoàn trả theo tỷ lệ các buổi chưa học:  
     $Tiền\_hoàn = Giá\_hợp\_đồng \times \frac{Số\_buổi\_chưa\_tập}{Tổng\_số\_buổi}$.  
     Cộng tiền hoàn vào ví học viên; tự động hủy bỏ toàn bộ các ca tập trong tương lai thuộc hợp đồng này để giải phóng lịch cho cả 2 bên.
5. **Thanh lý toàn bộ Hợp đồng - Thanh toán thù lao PT (`CANCEL_CONTRACT_PAID_PT`)**:
   * *Nội dung*: Học viên vi phạm nghiêm trọng (quấy rối, mất liên lạc kéo dài).
   * *Thực thi*: Hủy hợp đồng, giải ngân toàn bộ giá trị gói tập cho PT để bảo vệ quyền lợi của người lao động.

---

## 12. NGHIỆP VỤ NHẮN TIN TRAO ĐỔI TRỰC TIẾP 1-1

### 12.1. Kết nối Hội thoại giữa PT và Học viên
* Hệ thống hỗ trợ kênh trao đổi tin nhắn trực tiếp giữa Học viên và Huấn luyện viên nhằm giải quyết các nhu cầu: hẹn giờ tập, dặn dò dinh dưỡng trước buổi tập, thông báo đến muộn vài phút.
* **Khởi tạo danh sách đối tác trò chuyện**:
  * Học viên có thể mở trò chuyện với bất kỳ PT nào đã từng đặt lịch hoặc có hợp đồng.
  * Danh sách hội thoại tự động cập nhật đối tác trò chuyện gần nhất, hiển thị nội dung tin nhắn cuối cùng kèm thời gian gửi.

### 12.2. Trạng thái Đã đọc & Thông báo tin mới
* Mỗi tin nhắn có trạng thái `is_read` (đã xem hay chưa).
* Khi người dùng mở hộp thoại với một đối tác, toàn bộ các tin nhắn do đối tác gửi đến sẽ tự động được đánh dấu là đã đọc (`markAsRead`).
* Biểu tượng chat hiển thị số lượng tin nhắn chưa đọc theo thời gian thực để người dùng không bỏ lỡ thông báo từ đối phương.

---

## 13. NGHIỆP VỤ QUẢN TRỊ VIÊN, KIỂM DUYỆT & BÁO CÁO PHÂN TÍCH

### 13.1. Quản lý Người dùng & Chế tài Vi phạm
* Admin có quyền tra cứu toàn bộ danh sách người dùng trong hệ thống theo họ tên, email, số điện thoại, vai trò (`STUDENT`, `PT`, `ADMIN`).
* **Cơ chế Khóa tài khoản (`Update User Status`)**:
  * Khi phát hiện người dùng gian lận điểm danh, có thái độ thô lỗ hoặc nhận nhiều phán quyết thua kiện từ trọng tài: Admin có quyền đổi trạng thái người dùng thành **`SUSPENDED`** (Khóa tài khoản).
  * Người dùng bị khóa sẽ lập tức bị đá khỏi hệ thống ở lần đăng nhập tiếp theo và không thể thực hiện bất kỳ giao dịch nào.
  * Khi giải quyết xong khiếu nại, Admin có thể mở khóa lại thành `ACTIVE`.

### 13.2. Giám sát Dòng tiền & Quỹ Doanh thu Sàn
* Admin có màn hình chuyên biệt theo dõi biến động tài chính toàn sàn:
  * Tổng tiền học viên đã nạp vào ví (`TOPUP`).
  * Tổng doanh thu mua khóa học thành công (`PURCHASE_PACKAGE`).
  * Tổng số tiền đã thanh toán thù lao cho các PT (`EARNING`).
  * Tổng tiền đã giải ngân rút về ngân hàng (`WITHDRAW`).
  * Tổng quỹ hoa hồng dịch vụ 10% thực tế mà nền tảng đã thu được (`TXN_COMMISSION`).
* Toàn bộ các khoản tiền đều có thể tra cứu mã tham chiếu `transactionRef` để đối soát với sao kê ngân hàng.

### 13.3. Giám sát Ca tập & Điều tra Hành vi Hủy ca Bất thường
* Bảng điều khiển Admin cung cấp góc nhìn toàn cảnh về toàn bộ các ca tập:
  * Tỷ lệ ca hoàn thành (`COMPLETED`), ca đang chờ (`PENDING`), ca đã duyệt (`CONFIRMED`) và ca bị hủy (`CANCELLED`).
  * Phân tích đối tượng hủy ca: Tỷ lệ hủy do Học viên khởi xướng vs do Huấn luyện viên khởi xướng.
  * Hiển thị chi tiết lý do hủy ca, số tiền phạt và đền bù đã tự động khấu trừ.
  * Giúp Ban Quản Trị dễ dàng phát hiện các PT có tỷ lệ hủy ca cao bất thường để tiến hành cảnh cáo hoặc thanh tra chuyên môn.

---

## 14. BẢNG MA TRẬN VÒNG ĐỜI TRẠNG THÁI DỮ LIỆU

### 14.1. Vòng đời Trạng thái Khung giờ (`AvailabilitySlot`)
```
[ Khởi tạo slot ] ──────────► AVAILABLE (Sẵn sàng)
                                 │
                    Học viên đặt │ (Khóa bi quan)
                                 ▼
                             BOOKED (Đã được đặt)
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                 ▼
PT Từ chối / Hủy ca                               Ca hoàn thành
  (Trả về AVAILABLE)                              (Giữ nguyên trạng thái lịch sử)
```

### 14.2. Vòng đời Trạng thái Ca tập (`Booking`)
```
[ Học viên đặt lịch ] ──────► PENDING (Chờ duyệt, tạm trừ 1 buổi trong kho)
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                                                 ▼
   PT Từ chối                                         PT Duyệt
        │                                                 │
        ▼                                                 ▼
   CANCELLED (Hủy ca,                                 CONFIRMED (Đã xác nhận ca)
   hoàn 1 buổi vào kho)                                   │
                                ┌─────────────────────────┴─────────────────────────┐
                                ▼                                                   ▼
                         Hủy lịch (PT/Học viên/Admin)                         Điểm danh OTP 2 bên
                                │                                                   │
                                ▼                                                   ▼
                         CANCELLED (Xử lý                                      COMPLETED (Hoàn tất,
                         phạt/đền bù theo chính sách)                          giải ngân 90% thù lao)
```

### 14.3. Vòng đời Trạng thái Hợp đồng (`Enrollment`)
```
[ Học viên thanh toán gói ] ──► ACTIVE (Kho buổi = Tổng số buổi, Hạn = Start + ValidityDays)
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
  Học hết số buổi            Hết hạn thời gian         Trọng tài phán quyết
  (remainingSessions = 0     (now > endDate)           thanh lý hợp đồng
   và không còn ca PENDING)        │                          │
        │                          ▼                          ▼
        ▼                      EXPIRED                    CANCELLED
    COMPLETED
```

### 14.4. Vòng đời Trạng thái Vụ việc Tranh chấp (`DisputeCase`)
```
[ Gửi đơn khiếu nại ] ───────► PENDING_ARBITRATION (Khởi tạo, kích hoạt đồng hồ 48h)
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
Bị đơn gửi phản biện         Admin yêu cầu thêm bằng chứng     Hết thời hạn 48 giờ
        │                             │                             │
        │                             ▼                             │
        │                 AWAITING_ADDITIONAL_EVIDENCE              │
        │                             │                             │
        └────────────────────────────►│◄────────────────────────────┘
                                      │
                                      ▼
                        Admin ban hành Phán quyết
                                      │
     ┌──────────────────┬─────────────┴─────────────┬──────────────────┐
     ▼                  ▼                           ▼                  ▼
RESOLVED_          RESOLVED_                   RESOLVED_          RESOLVED_
REFUND_STUDENT     PAID_PT                     FORCE_MAJEURE      CONTRACT_TERMINATION
(Hoàn tiền HV,     (Giải ngân PT,              (Khôi phục buổi,   (Thanh lý hợp đồng,
 phạt/cảnh cáo PT)  trừ buổi HV)                không phạt đôi bên) chia tiền tồn dư)
```

---
*Tài liệu được biên soạn và chuẩn hóa toàn diện cho dự án PT-Connect, phản ánh chính xác 100% logic vận hành của hệ thống.*
