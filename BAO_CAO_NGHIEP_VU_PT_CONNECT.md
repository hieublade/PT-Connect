# TÀI LIỆU TOÀN TẬP ĐẶC TẢ NGHIỆP VỤ & KỊCH BẢN HỆ THỐNG PT-CONNECT

> **Mục đích tài liệu**: Dùng để ôn luyện bảo vệ đồ án, làm báo cáo môn học (CSDL, Kiến trúc Phần mềm), hoặc nạp vào AI đóng vai Giảng viên chấm thi để vấn đáp phản biện.

---

## MỤC LỤC
1. [TỔNG QUAN HỆ THỐNG & CÁC TÁC NHÂN (ACTORS)](#1-tổng-quan-hệ-thống--các-tác-nhân-actors)
2. [PHÂN TÍCH TÍNH NGHIỆP VỤ & TÍNH THỰC TIỄN CỦA HỆ THỐNG](#2-phân-tích-tính-nghiệp-vụ--tính-thực-tiễn-của-hệ-thống)
   - *Bối cảnh, Nỗi đau thị trường, 6 Trụ cột nghiệp vụ cốt lõi & Quy tắc bất biến*
3. [KỊCH BẢN THỰC TẾ CHI TIẾT TỪ A - Z (CASE STUDY END-TO-END)](#3-kịch-bản-thực-tế-chi-tiết-từ-a---z-case-study-end-to-end)
   - *Hành trình Học viên Nam: Nạp tiền $\to$ Mua khóa học $\to$ Xuất hợp đồng PDF $\to$ Đặt lịch $\to$ Điểm danh OTP $\to$ Đánh giá & Giải ngân*
4. [ĐẶC TẢ CHI TIẾT 7 LUỒNG NGHIỆP VỤ HỆ THỐNG](#4-đặc-tả-chi-tiết-7-luồng-nghiệp-vụ-hệ-thống)
5. [BỘ 10 CÂU HỎI VẶN CỦA HỘI ĐỒNG GIÁM KHẢO & CÁCH ĐỐI ĐÁP](#5-bộ-10-câu-hỏi-vặn-của-hội-đồng-giám-khảo--cách-đối-đáp)

---

# 1. TỔNG QUAN HỆ THỐNG & CÁC TÁC NHÂN (ACTORS)

**PT-Connect** là nền tảng quản trị và kết nối trực tuyến giữa **Học viên thể hình (Student)** và **Huấn luyện viên cá nhân (Personal Trainer - PT)**. Hệ thống giải quyết trọn vẹn các bài toán nhức nhối của mô hình thuê PT truyền thống:
* Học viên sợ bị bùng buổi, sợ PT dạy qua loa, hợp đồng giấy tờ mập mờ.
* PT sợ học viên hủy lịch phút chót gây lãng phí thời gian, khó quản lý doanh thu.
* Trung gian phòng gym ăn hoa hồng quá cao (40-60%).

### 3 Vai trò (Roles) trong hệ thống:
1. **Học viên (`STUDENT`)**:
   * Tìm kiếm PT theo vị trí địa lý, giá cả, đánh giá sao.
   * Nạp ví cá nhân, mua khóa học, ký hợp đồng điện tử PDF tự động.
   * Đặt lịch tập (học thử hoặc theo gói).
   * Điểm danh tại phòng tập bằng mã OTP bảo mật.
   * Đánh giá chất lượng dịch vụ (Review).
2. **Huấn luyện viên (`PT`)**:
   * Đăng ký hồ sơ chuyên môn, tải lên chứng chỉ (Certificates).
   * Mở các khung giờ rảnh hàng tuần (`availability_slots`).
   * Tạo các khóa học (`courses`) theo chuyên môn (Tăng cơ, Giảm mỡ, Yoga, Boxing...).
   * Mở ca tập, phát mã OTP cho học viên, xác nhận kết thúc ca tập để nhận thù lao vào ví.
3. **Quản trị viên (`ADMIN`)**:
   * Thẩm định bằng cấp/chứng chỉ của PT trước khi cho phép hoạt động (`PENDING` $\to$ `VERIFIED`).
   * Quản lý người dùng, khóa tài khoản gian lận (`SUSPENDED`).
   * Giám sát dashboard doanh thu, dòng tiền ký quỹ và phí sàn.

---

# 2. PHÂN TÍCH TÍNH NGHIỆP VỤ & TÍNH THỰC TIỄN CỦA HỆ THỐNG

### 2.1. Nỗi đau thị trường & Bài toán thực tế giải quyết
Trong thị trường tập luyện thể hình cá nhân (Personal Training) truyền thống tại Việt Nam:
1. **Nỗi đau của Học viên**:
   * Bị nhân viên phòng gym chèo kéo ký hợp đồng dài hạn giá hàng chục triệu đồng, sau đó PT nghỉ việc hoặc đổi người dạy mà không báo trước.
   * Hợp đồng giấy tờ mập mờ, khó đòi lại tiền khi bận rộn, chấn thương hoặc chuyển chỗ ở.
   * Không có cách nào đánh giá khách quan trình độ và bằng cấp của PT trước khi xuống tiền.
2. **Nỗi đau của Huấn luyện viên (PT)**:
   * Bị các chuỗi phòng tập lớn cắt phế hoa hồng từ 40% đến 60% giá trị hợp đồng.
   * Học viên thường xuyên "bùng lịch" sát giờ hẹn (No-show), khiến PT mất công đến phòng tập, lãng phí thời gian và không được đền bù tiền công.
3. **Nỗi đau của Người quản trị / Phòng gym**:
   * Điểm danh thủ công bằng sổ ký hoặc tin nhắn Zalo rất dễ xảy ra tình trạng **PT ký khống buổi tập** để làm báo cáo rút hoa hồng sớm.
   * Khó kiểm soát xung đột lịch giữa các PT và học viên.

---

### 2.2. Sáu (06) Trụ cột Tính chất Nghiệp vụ của PT-Connect

#### 1. Tính Ký Quỹ & Bảo hộ Tài chính (Escrow Mechanism)
* **Bản chất**: Tiền học viên mua gói tập không được chuyển thẳng cho PT ngay lúc mua. Nền tảng đóng vai trò trung gian giữ tiền (`locked_balance`).
* **Nghiệp vụ**: Tiền chỉ được **giải ngân lũy tiến (Per-session payout)**: học xong buổi nào, nghiệm thu xong thì tiền của đúng 1 buổi đó mới được giải phóng sang ví khả dụng của PT.
* **Ý nghĩa**: Bảo vệ học viên không bị mất trắng tiền nếu PT nghỉ dạy giữa chừng, đồng thời bảo vệ PT luôn được thanh toán sòng phẳng khi hoàn thành ca dạy.

#### 2. Tính Chống Gian Lận Hai Chiều (Two-Sided Anti-Fraud Verification)
* **Bản chất**: Nghiệm thu buổi tập đòi hỏi **sự hiện diện vật lý đồng thời của cả 2 bên tại phòng tập**.
* **Nghiệp vụ**:
  * PT mở ca $\to$ Hệ thống sinh mã OTP ngẫu nhiên có hiệu lực 30 phút.
  * Học viên nhập mã OTP $\to$ Hệ thống mới ghi nhận điểm danh.
  * Buổi tập kết thúc $\to$ PT bấm xác nhận nghiệm thu.
* **Ý nghĩa**:
  * Chống kịch bản PT ngồi ở nhà tự bấm hoàn thành để rút tiền.
  * Chống kịch bản Học viên đã tập xong nhưng về nhà chối bỏ không xác nhận để đòi hoàn tiền.

#### 3. Tính Pháp Lý & Minh Bạch Hợp Đồng (Legal Compliance & Digital Contracts)
* **Bản chất**: Mọi giao dịch mua bán khóa học đều được thể chế hóa bằng văn bản pháp lý có giá trị ràng buộc.
* **Nghiệp vụ**: Ngay khi thanh toán thành công, hệ thống tự động biên soạn và render ra **Hợp đồng điện tử PDF** gồm mã hợp đồng duy nhất, thông tin pháp lý bên A (Học viên), bên B (PT), số buổi, hạn sử dụng, và các điều khoản giải quyết tranh chấp.
* **Ý nghĩa**: Minh bạch hóa cam kết đào tạo, bảo vệ cả hai bên khi phát sinh khiếu nại.

#### 4. Tính Công Bằng & Ràng Buộc Trách Nhiệm (Fair SLA & Cancellation Policy)
* **Bản chất**: Áp dụng hạn mốc thời gian **24 giờ vàng** để phân xử hủy lịch:
  * **Học viên hủy sát giờ (< 24h)**: Mất buổi tập, đền bù **50% học phí** cho PT để bù đắp chi phí cơ hội và thời gian chờ đợi.
  * **PT tự ý bùng lịch sát giờ (< 24h)**: Hoàn trả 1 buổi cho học viên, **phạt trừ ví PT 20%** và **đền bù 20% vào ví học viên** để bù đắp trải nghiệm tiêu cực.
* **Ý nghĩa**: Tạo văn hóa tập luyện chuyên nghiệp, tôn trọng thời gian của nhau.

#### 5. Tính Kiểm Soát Chất Lượng & Chống Review Rác (Quality Assurance & Clean Reviews)
* **Bản chất**:
  * PT muốn mở lớp phải qua khâu kiểm duyệt bằng cấp, chứng chỉ thể hình bởi Admin (`PENDING` $\to$ `VERIFIED`).
  * Chỉ những học viên **đã thực sự hoàn thành buổi tập (`COMPLETED`)** mới được phép để lại đánh giá sao và bình luận.
* **Ý nghĩa**: Triệt tiêu 100% tình trạng "đánh giá ảo", nick ảo vào dìm hàng đối thủ hoặc tự chấm 5 sao nâng điểm.

#### 6. Tính Nhất Quán & Toàn Vẹn Dữ Liệu Tự Động (ACID & Database Triggers)
* **Bản chất**: Điểm đánh giá trung bình (`rating_avg`) và tổng số đánh giá (`total_reviews`) được cập nhật **hoàn toàn tự động bằng MySQL Triggers** chạy bên trong Database Engine mỗi khi có chèn/sửa/xóa review.
* **Ý nghĩa**: Đảm bảo tính nhất quán tức thì (Real-time Consistency), giảm tải 100% việc tính toán lặp đi lặp lại ở tầng ứng dụng Backend.

---

### 2.3. Bảng Ma Trận Các Quy Tắc Nghiệp Vụ Bất Biến (Business Invariants)

| Mã quy tắc | Tên quy tắc nghiệp vụ | Ràng buộc kỹ thuật đảm bảo | Hậu quả nếu vi phạm |
| :--- | :--- | :--- | :--- |
| **BR-01** | Một PT không thể dạy 2 ca trùng giờ bắt đầu | `UNIQUE KEY uq_slot_pt_start (pt_id, start_time)` | Database từ chối ngay lập tức |
| **BR-02** | Học viên không thể đặt 2 lịch tập trùng khung giờ | Quét giao thoa thời gian trong `booking_service` | Báo lỗi 400 xung đột lịch |
| **BR-03** | Khung giờ tập kết thúc phải sau giờ bắt đầu | `CHECK (end_time > start_time)` | Database quăng lỗi Check Constraint |
| **BR-04** | Chỉ mở điểm danh quanh khung giờ tập | Logic `slot.start_time - 15 phút` | Báo lỗi mở ca quá sớm |
| **BR-05** | Mã OTP chỉ sống trong 30 phút | Time-to-Live (TTL = 30m) trong In-Memory Store | Báo lỗi OTP hết hạn |
| **BR-06** | Ví tiền không được âm số dư | Giao dịch nguyên tố `Atomic Transaction` | Rollback giao dịch nếu không đủ tiền |

---

# 3. KỊCH BẢN THỰC TẾ CHI TIẾT TỪ A - Z (CASE STUDY END-TO-END)

> **Nhân vật ví dụ**:
> * **Học viên**: Nguyễn Văn Nam (Sinh viên, cần giảm cân).
> * **Huấn luyện viên (PT)**: Trần Mạnh Hùng (PT thể hình tại Cầu Giấy, Hà Nội, giá 200.000 đ/buổi).

```
                      HÀNH TRÌNH ĐIỂN HÌNH TỪ A ĐẾN Z
                      ==============================

 [Bước 1: Nam Đăng ký & Nạp ví] ──> Số dư: 2.000.000 đ
               │
               ▼
 [Bước 2: Tìm kiếm & Chọn PT Hùng] ──> Xem Profile, Rating 4.9 sao
               │
               ▼
 [Bước 3: Mua gói tập 10 buổi] ──> Trừ ví 1.500.000 đ ──> Sinh Hợp đồng PDF tự động
               │
               ▼
 [Bước 4: Đặt lịch sáng Thứ 4] ──> Chọn Slot 08:00 - 09:30 ──> Slot đổi sang BOOKED
               │                                                (Còn lại 9 buổi)
               ▼
 [Bước 5: Tại phòng tập (07:50 Sáng Thứ 4)]
   ├── PT Hùng bấm "Bắt đầu ca tập" ──> Sinh mã OTP: 482910 (Hạn 30p)
   ├── Nam nhập mã OTP: 482910      ──> Ghi nhận PRESENT (Có mặt đúng giờ)
   └── Kết thúc buổi (09:30)        ──> PT bấm Xác nhận hoàn tất
               │
               ▼
 [Bước 6: Nghiệm thu & Giải ngân]
   ├── Trạng thái Booking: COMPLETED
   ├── Hệ thống cộng 150.000 đ vào ví PT Hùng
   └── Nam đánh giá 5 sao ──> MySQL Trigger tự động nhảy lại Rating PT Hùng
```

---

### BƯỚC 1: Nam Tạo tài khoản & Nạp ví tiền
1. Nam truy cập trang chủ, chọn *"Đăng ký Học viên"*.
2. Nhập: Email `nam@gmail.com`, SĐT `0912345678`, Mật khẩu `Pass123!`.
3. **Hệ thống xử lý**:
   * Kiểm tra email/phone chưa từng tồn tại trong bảng `users`.
   * Băm mật khẩu bằng thuật toán `Bcrypt`.
   * Tạo bản ghi `users` với `role = STUDENT, status = ACTIVE`.
   * **Tự động mở ví (`wallets`)**: Tạo ví liên kết với `user_id` của Nam, `balance = 0 đ, status = ACTIVE`.
4. Nam đăng nhập, hệ thống cấp chuỗi **JWT Token**.
5. Nam vào mục *"Ví của tôi"*, chọn Nạp tiền `2.000.000 đ` qua hình thức Chuyển khoản:
   * Bản ghi `payments` được tạo: `type = TOPUP, amount = 2000000, status = SUCCESS`.
   * Ví của Nam cập nhật: `balance = 2.000.000 đ`.

---

### BƯỚC 2: Nam Tìm kiếm & Chọn Huấn luyện viên
1. Nam vào trang *"Tìm kiếm Huấn luyện viên"*, chọn bộ lọc:
   * Thành phố: `Hà Nội`
   * Khoảng giá: `150.000 đ - 300.000 đ`
   * Sắp xếp theo: `Điểm đánh giá cao nhất (Rating DESC)`
2. Backend thực thi câu query tối ưu qua **B-Tree Composite Index** `(city, rating_avg, hourly_rate)`.
3. Danh sách trả về hồ sơ của **PT Trần Mạnh Hùng**:
   * Chuyên môn: Giảm mỡ cấp tốc, Tăng cơ.
   * Đã được Admin kiểm duyệt bằng cấp (`status = VERIFIED`).
   * Rating: 4.9 sao (tổng 38 lượt đánh giá).
   * Khóa học tiêu biểu: *"Khóa Giảm mỡ Chuyên sâu 10 buổi"* (Giá: 1.500.000 đ).

---

### BƯỚC 3: Mua khóa học & Tự động sinh Hợp đồng điện tử PDF
1. Nam bấm nút **"Mua khóa học ngay"**.
2. **Backend `EnrollmentService` xử lý trong 1 Transaction nguyên tố**:
   * Kiểm tra ví của Nam: Số dư `2.000.000 đ` $\ge$ `1.500.000 đ` (Hợp lệ).
   * Trừ tiền trong ví của Nam: `balance` giảm từ `2.000.000 đ` $\to$ `500.000 đ`.
   * Tạo bản ghi `payments`: `type = PURCHASE_PACKAGE, amount = 1500000, status = SUCCESS`.
   * Tạo bản ghi `enrollments`:
     * `student_id`: Nam
     * `course_id`: Khóa 10 buổi của Hùng
     * `total_sessions`: 10
     * `remaining_sessions`: 10
     * `status`: `ACTIVE`
     * `expires_at`: 90 ngày kể từ ngày mua.
3. **Tự động sinh Hợp đồng điện tử PDF (`contract.py`)**:
   * Hệ thống tự động nạp dữ liệu: Tên bên A (Học viên Nam), Tên bên B (PT Hùng), Số buổi (10 buổi), Giá trị (1.500.000 đ), Điều khoản cam kết điểm danh, điều khoản bảo vệ hủy lịch.
   * Render file PDF chuẩn định dạng, lưu vào thư mục `/uploads/contracts/contract_NAM_HUNG_101.pdf`.
   * Cập nhật đường link file PDF vào trường `enrollments.contract_pdf_url`.
   * Nam có thể bấm xem và tải hợp đồng điện tử về máy bất kỳ lúc nào.

---

### BƯỚC 4: Nam Đặt lịch tập (Booking Slot)
1. PT Hùng đã mở sẵn một khung giờ rảnh vào tuần tới:
   * Ngày: Thứ Tư, thời gian từ `08:00:00` đến `09:30:00`.
   * Bản ghi `availability_slots` tương ứng có `id = 502, status = AVAILABLE`.
2. Nam vào trang cá nhân của PT Hùng, thấy slot sáng Thứ 4 đang trống, Nam bấm **"Đặt lịch tập"**:
   * Loại đặt: `PACKAGE` (Theo gói đã mua).
   * Chọn hợp đồng: Khóa học 10 buổi ở Bước 3.
   * Ghi chú cho PT: *"Hôm nay tập trung vào bài tập chân và cardio giúp em nhé anh Hùng"*.
3. **Kiểm tra nghiệp vụ chống xung đột (`booking_service.py`)**:
   * `slot.status` có còn là `AVAILABLE` không? $\to$ Có.
   * Nam có bị trùng giờ học nào khác không? $\to$ Quét toàn bộ lịch của Nam trong khung `08:00 - 09:30` ngày hôm đó $\to$ Không trùng.
   * Khóa học của Nam còn buổi không? $\to$ `remaining_sessions = 10 > 0` $\to$ Hợp lệ.
4. **Cập nhật dữ liệu**:
   * Giảm số buổi trong hợp đồng: `remaining_sessions` từ `10` $\to$ `9`.
   * Khung giờ `slot` đổi trạng thái từ `AVAILABLE` $\to$ `BOOKED` (không cho ai khác đặt đè lên).
   * Tạo bản ghi `bookings`: `student_id = Nam, pt_id = Hùng, slot_id = 502, status = CONFIRMED, booking_type = PACKAGE`.

---

### BƯỚC 5: Tại phòng tập — Điểm danh 2 phía bằng OTP
*Thời gian thực tế: 07:50 Sáng Thứ Tư (Cách giờ tập 10 phút).*

1. **PT Hùng mở phiên điểm danh**:
   * PT Hùng mở điện thoại, vào danh sách ca tập hôm nay, thấy ca của Nam lúc 08:00.
   * Hùng bấm nút **"Bắt đầu ca tập"** (`POST /api/v1/attendance/502/start`).
   * **Backend kiểm tra**:
     * Hiện tại là 07:50, nằm trong khung cho phép (trước giờ tập $\le$ 15 phút) $\to$ Hợp lệ.
     * Do mở trước 08:15 nên trạng thái là `PRESENT` (Đúng giờ).
     * Hệ thống sinh mã OTP ngẫu nhiên 6 chữ số: **`482910`**, lưu vào `otp_store` với hạn dùng 30 phút.
     * Màn hình của PT Hùng hiện to mã: **`482910`**.
2. **Nam tiến hành Check-in**:
   * Nam đã có mặt ở phòng tập, gặp anh Hùng.
   * Hùng đọc: *"Mã của em hôm nay là 482910 nhé"*.
   * Nam mở app trên điện thoại mình, vào ca tập sáng nay, nhập **`482910`** và bấm **"Xác nhận điểm danh"** (`POST /api/v1/attendance/502/student-checkin`).
   * **Backend kiểm tra**:
     * Mã `482910` khớp với bộ nhớ tạm, chưa hết hạn $\to$ Thành công!
     * Bản ghi `attendance` cập nhật: `student_confirmed = True, check_in_time = 07:52`.
3. **Tập luyện & Kết thúc ca tập**:
   * Hai người hoàn thành 90 phút tập luyện chăm chỉ.
   * Lúc 09:30, PT Hùng bấm nút **"Xác nhận kết thúc buổi tập"** (`POST /api/v1/attendance/502/pt-confirm`).
   * **Backend thực thi nghiệm thu (`_complete_session`)**:
     * Ghi nhận `pt_confirmed = True, check_out_time = 09:30`.
     * Bản ghi `bookings` chuyển trạng thái sang **`COMPLETED`**.
     * Xóa mã OTP khỏi bộ nhớ.
     * **Giải ngân tiền cho PT**: Hệ thống tính học phí 1 buổi của gói (150.000 đ), cộng trực tiếp vào `balance` của ví PT Hùng $\to$ Hùng nhận được tiền công ngay lập tức!

---

### BƯỚC 6: Đánh giá (Review) & Kích hoạt Database Trigger
1. Sau khi ca tập `COMPLETED`, trên app của Nam xuất hiện thông báo: *"Bạn thấy buổi tập hôm nay với HLV Mạnh Hùng thế nào?"*.
2. Nam chấm: **5 sao ⭐⭐⭐⭐⭐** kèm lời nhắn: *"Anh Hùng hướng dẫn kỹ thuật Squat rất kỹ, nhiệt tình và đúng giờ!"*.
3. Nam bấm gửi đánh giá (`POST /api/v1/reviews`).
4. **Database Engine MySQL tự động chạy Trigger (`trg_reviews_after_insert`)**:
   * Bản ghi mới được chèn vào bảng `reviews`.
   * Trigger ngầm chạy lệnh `UPDATE pt_profiles`:
     * `total_reviews` tăng từ `38` $\to$ `39`.
     * `rating_avg` tính toán lại đạt `4.92`.
   * Toàn bộ dữ liệu hiển thị tức thì ra ngoài web cho các học viên khác thấy mà không làm tốn tài nguyên tính toán của Backend!

---

# 4. ĐẶC TẢ CHI TIẾT 7 LUỒNG NGHIỆP VỤ HỆ THỐNG

---

## Luồng 1: Xác thực, Phân quyền & Vòng đời tài khoản

| Tác nhân | Hành động | API Endpoint | Bảng CSDL tác động |
| :--- | :--- | :--- | :--- |
| Khách | Đăng ký Student | `POST /api/v1/auth/register` | `users`, `wallets` |
| Khách | Đăng ký PT (kèm profile) | `POST /api/v1/auth/register` | `users`, `pt_profiles`, `wallets` |
| User | Đăng nhập lấy JWT | `POST /api/v1/auth/login` | Đọc `users` |
| Admin | Duyệt hồ sơ PT | `PUT /api/v1/admin/pts/{id}/verify` | `pt_profiles (status = VERIFIED)` |
| Admin | Khóa tài khoản vi phạm | `PUT /api/v1/admin/users/{id}/suspend` | `users (status = SUSPENDED)` |

* **Luật nghiệp vụ**:
  * Mật khẩu băm một chiều bằng `bcrypt`, không lưu bản rõ (plain text).
  * PT khi mới đăng ký chỉ ở trạng thái `PENDING`. Chỉ khi Admin vào xem ảnh chứng chỉ và duyệt sang `VERIFIED` thì PT mới xuất hiện trên thanh tìm kiếm và được tạo khóa học.
  * Nếu tài khoản bị `SUSPENDED`, hàm đăng nhập và mọi middleware sẽ từ chối truy cập (401 Unauthorized / 403 Forbidden).

---

## Luồng 2: Quản lý Ví tiền & Cơ chế Ký quỹ (Escrow)

* **Cấu trúc bảng `wallets`**:
  * `balance`: Số dư khả dụng (tiền thực có thể rút hoặc mua gói).
  * `locked_balance`: Số dư tạm giữ (đang nằm trong các giao dịch chờ thanh toán).
* **Nạp tiền (`TOPUP`)**:
  * Học viên chọn nạp tiền $\to$ Tạo giao dịch `payments` trạng thái `SUCCESS` $\to$ `balance` tăng lên.
* **Rút tiền (`WITHDRAW`)**:
  * PT yêu cầu rút tiền về số tài khoản ngân hàng cá nhân.
  * `balance` phải $\ge$ số tiền muốn rút.
  * Hệ thống trừ `balance` và ghi nhận lịch sử rút tiền.

---

## Luồng 3: Mua khóa học & Tự động sinh Hợp đồng PDF

1. **Điều kiện mua**:
   * Khóa học phải ở trạng thái `ACTIVE`.
   * Số dư `wallet.balance >= course.price`.
2. **Quy trình thanh toán nguyên tố**:
   * Chạy trong khối `with db.begin_nested():`
   * Trừ `balance` ví học viên.
   * Tạo bản ghi `enrollments` với `remaining_sessions = total_sessions`.
   * Gọi module `app/pdf/contract.py` sinh file PDF hợp đồng có đầy đủ điều khoản và lưu trữ trên đĩa.
   * Ghi log giao dịch vào `payments`.

---

## Luồng 4: Quản lý Lịch rảnh của PT (Availability Slots)

* **Quy tắc tạo slot**:
  * Slot thuộc về 1 `pt_id`.
  * Có `start_time` và `end_time` (`end_time > start_time`).
  * **Ràng buộc duy nhất (Unique Constraint)**: `UNIQUE KEY uq_slot_pt_start (pt_id, start_time)`. Một PT không thể nào mở 2 slot trùng giờ bắt đầu.
* **Trạng thái của Slot (`SlotStatus`)**:
  * `AVAILABLE`: Rảnh, đang mở cho học viên đặt.
  * `BOOKED`: Đã có học viên đặt thành công.
  * `LOCKED`: PT tạm khóa khung giờ (ví dụ bận việc đột xuất).

---

## Luồng 5: Đặt lịch tập & Thuật toán chống trùng lịch

Khi học viên gửi yêu cầu đặt lịch (`POST /api/v1/bookings`):
1. **Kiểm tra Slot**:
   * Gọi `slot_repo.get_by_id_with_lock(slot_id)` (Sử dụng khóa `SELECT ... FOR UPDATE` để chống Race Condition).
   * Nếu `slot.status != AVAILABLE` $\to$ Báo lỗi *"Khung giờ này đã có người đặt"*.
2. **Kiểm tra lịch học viên**:
   * Quét bảng `bookings` tìm các ca tập của học viên có khung giờ giao nhau với slot này. Nếu có $\to$ Báo lỗi *"Bạn đã có lịch tập khác vào khung giờ này"*.
3. **Xử lý theo loại đặt**:
   * Nếu là `TRIAL` (học thử): Miễn phí hoặc tính phí đơn buổi.
   * Nếu là `PACKAGE` (theo gói): Giảm `remaining_sessions` của hợp đồng đi 1.
4. **Cập nhật trạng thái**:
   * `slot.status = BOOKED`.
   * `booking.status = CONFIRMED` (hoặc `PENDING` nếu cần PT duyệt tay).

---

## Luồng 6: Điểm danh 2 phía bằng OTP (Two-sided Attendance)

* **Giai đoạn 1: Mở phiên (PT thực hiện)**:
  * PT bấm *"Bắt đầu ca tập"*.
  * Kiểm tra thời gian: Chỉ được mở sớm **tối đa 15 phút** trước giờ bắt đầu.
  * Nếu mở trễ quá 15 phút sau giờ bắt đầu $\to$ Đánh dấu ca tập là `LATE` (Đi muộn).
  * Sinh mã OTP 6 số ngẫu nhiên qua `otp_store`, lưu trong RAM với thời gian hết hạn **30 phút**.
* **Giai đoạn 2: Check-in (Học viên thực hiện)**:
  * Học viên nhập mã OTP được PT đọc cho tại phòng tập.
  * Hệ thống so khớp OTP:
    * Đúng mã & còn hạn $\to$ `student_confirmed = True`, lưu `check_in_time`.
    * Sai mã hoặc quá hạn $\to$ Trả về mã lỗi 400.
* **Giai đoạn 3: Nghiệm thu hoàn thành**:
  * PT bấm *"Xác nhận kết thúc"*.
  * Cả hai bên đã xác nhận $\to$ Gọi `_complete_session()`:
    * `attendance.check_out = now()`.
    * `booking.status = COMPLETED`.
    * Xóa mã OTP khỏi bộ nhớ.
    * Giải ngân tiền buổi tập từ hệ thống vào ví của PT.
* **Trường hợp vắng mặt (`ABSENT`)**:
  * Nếu học viên không đến, PT bấm *"Đánh dấu vắng mặt"*.
  * Ca tập bị tính là `ABSENT`, học viên mất buổi tập, PT vẫn nhận được tiền ca tập đó.

---

## Luồng 7: Chính sách Hủy lịch, Đền bù & Đánh giá (Review Trigger)

### Ma trận Chính sách Hủy lịch (Áp dụng Factory Pattern):

| Người hủy | Trạng thái Booking | Thời gian hủy | Xử lý Buổi tập | Xử lý Tiền phạt / Bồi thường |
| :--- | :--- | :--- | :--- | :--- |
| **Học viên** | `PENDING` (Chờ duyệt) | Bất kỳ lúc nào | Hoàn 1 buổi vào gói | Không phạt ai |
| **Học viên** | `CONFIRMED` | **$\ge$ 24 giờ** trước ca tập | Hoàn 1 buổi vào gói | Không phạt ai, mở lại slot rảnh |
| **Học viên** | `CONFIRMED` | **$<$ 24 giờ** (Sát giờ) | **Mất buổi tập** (không hoàn) | Trích **50% học phí** buổi tập đền bù vào ví của PT |
| **PT** | `PENDING` (Từ chối) | Bất kỳ lúc nào | Hoàn 1 buổi cho học viên | Không phạt |
| **PT** | `CONFIRMED` | **$\ge$ 24 giờ** trước ca tập | Hoàn 1 buổi cho học viên | Không phạt |
| **PT** | `CONFIRMED` | **$<$ 24 giờ** (Bùng lịch) | Hoàn 1 buổi cho học viên | **Phạt PT 20%** học phí (trừ ví PT), **Đền bù 20%** vào ví Học viên |

### Luồng Đánh giá (Review) & Trigger:
1. Học viên chỉ được review cho các đơn `booking` có trạng thái `COMPLETED` và chưa từng review trước đó.
2. MySQL Trigger `trg_reviews_after_insert` tự động tính lại `rating_avg = AVG(rating)` và `total_reviews = COUNT(*)` cập nhật thẳng vào bảng `pt_profiles`.

---

# 5. BỘ 10 CÂU HỎI VẶN CỦA HỘI ĐỒNG GIÁM KHẢO & CÁCH ĐỐI ĐÁP

### Câu 1: "Nếu 2 học viên cùng bấm đặt 1 slot vào cùng 1 tích tắc mili-giây, hệ thống xử lý thế nào để không bị trùng?"
* **Trả lời**: *"Dạ thưa thầy/cô, hệ thống bảo vệ 2 lớp:
  * **Lớp 1 (Tầng Code)**: Trong `BookingService`, em dùng phương thức `get_by_id_with_lock()` với kỹ thuật **Pessimistic Locking (`SELECT ... FOR UPDATE`)**. Khi request đầu tiên chạm vào slot, database sẽ khóa dòng dữ liệu đó lại. Request thứ hai đến sau phải đợi, khi giải phóng khóa thì slot đã đổi sang `BOOKED` nên request sau sẽ bị từ chối với lỗi 400.
  * **Lớp 2 (Tầng Database)**: Bảng `bookings` có ràng buộc duy nhất `UNIQUE KEY uq_active_slot (active_slot_id)`. Dù có vượt qua code thì Database cũng chặn đứng và quăng lỗi `IntegrityError` ngay lập tức."*

### Câu 2: "Tại sao không để PT tự bấm điểm danh hoàn thành luôn cho nhanh mà phải sinh mã OTP 2 bên?"
* **Trả lời**: *"Dạ, đây là bài toán chống gian lận kinh điển trong dịch vụ thể hình. Nếu để PT tự bấm, PT có thể thông đồng hoặc tự bấm khống các ca tập để rút tiền hoa hồng từ ví ký quỹ của học viên mà không dạy buổi nào. Bắt buộc dùng OTP đảm bảo: PT phải có mặt để mở ca và nhìn thấy mã, còn Học viên phải có mặt để nhập mã thì buổi tập mới được ghi nhận."*

### Câu 3: "Mã OTP lưu ở đâu? Có lưu vào Database MySQL không?"
* **Trả lời**: *"Dạ không lưu vào MySQL ạ. Mã OTP là dữ liệu tạm thời có hạn dùng ngắn (TTL = 30 phút), nếu lưu vào MySQL sẽ gây rác đĩa và nghẽn I/O. Hệ thống lưu tại tầng bộ nhớ (In-Memory Store / Redis trong module `app/otp/store.py`). Khi buổi tập kết thúc hoặc quá 30 phút, mã sẽ tự động bị dọn dẹp sạch khỏi RAM."*

### Câu 4: "Tại sao lại phân tách `balance` và `locked_balance` trong bảng Ví?"
* **Trả lời**: *"Dạ, đây là mô hình Ký quỹ trung gian (Escrow). Khi học viên mua gói 10 buổi trị giá 2 triệu, tiền này không thể trao đứt cho PT ngay vì dịch vụ chưa hoàn thành. Hệ thống sẽ giữ tiền làm trung gian. Sau mỗi buổi điểm danh hoàn tất, tiền của đúng 1 buổi (200.000 đ) mới được giải phóng sang ví của PT. Nếu học viên hủy lịch hoặc PT bùng kèo, hệ thống sẽ căn cứ vào ví ký quỹ để hoàn trả minh bạch."*

### Câu 5: "Quy tắc hủy lịch trước 24h và sau 24h được cài đặt bằng Design Pattern nào trong code?"
* **Trả lời**: *"Dạ, em áp dụng **Strategy Pattern** kết hợp **Factory Pattern** tại thư mục `app/policies/`. Em tạo một class trừu tượng `BaseCancellationPolicy`, sau đó triển khai thành 3 class con riêng biệt: `StudentCancellationPolicy`, `PtCancellationPolicy`, và `AdminCancellationPolicy`. Khi có yêu cầu hủy, `CancellationPolicyFactory` sẽ căn cứ vào Role của người bấm để chọn đúng bộ luật tính toán. Thiết kế này tuân thủ nguyên lý **Open/Closed (SOLID)**, sau này mở rộng thêm luật cho đối tượng khác em chỉ cần thêm file mới mà không làm vỡ code cũ."*

### Câu 6: "Tại sao điểm đánh giá trung bình (Rating) lại dùng MySQL Trigger mà không tính bằng Python Backend?"
* **Trả lời**: *"Dạ, nếu dùng Python, mỗi khi học viên mở trang tìm kiếm, Backend sẽ phải chạy lệnh `SELECT AVG(rating) FROM reviews` trên hàng triệu dòng đánh giá, gây nghẽn CPU và chậm trang web. Bằng cách dùng **MySQL Trigger `trg_reviews_after_insert`**, phép tính trung bình chỉ chạy duy nhất 1 lần khi có đánh giá mới được gửi lên, kết quả được lưu sẵn vào cột `rating_avg` của bảng `pt_profiles`. Khi người dùng tìm kiếm, database chỉ việc đọc ra với độ phức tạp $O(1)$ tức thì."*

### Câu 7: "Nếu học viên không đến tập (Bùng kèo) thì PT có bị mất tiền không?"
* **Trả lời**: *"Dạ không ạ. Nếu quá giờ tập mà học viên không tới, PT có quyền bấm nút 'Đánh dấu vắng mặt' (`ABSENT`). Hệ thống ghi nhận học viên vắng mặt không lý do: hợp đồng của học viên vẫn bị trừ buổi tập đó, và thù lao buổi dạy vẫn được giải ngân bình thường vào ví của PT để bảo vệ quyền lợi và thời gian của HLV."*

### Câu 8: "Hợp đồng điện tử PDF được sinh ra khi nào và lưu trữ ở đâu?"
* **Trả lời**: *"Dạ, hợp đồng được sinh ra ngay thời điểm học viên thanh toán thành công khóa học thông qua module `app/pdf/contract.py` sử dụng thư viện ReportLab. File PDF được đánh mã số hợp đồng duy nhất, chứa thông tin pháp lý của hai bên và được lưu vào thư mục `backend-py/uploads/contracts/`. Đường dẫn URL được lưu trong trường `contract_pdf_url` của bảng `enrollments` để hai bên xem lại bất cứ lúc nào."*

### Câu 9: "Làm thế nào để bảo vệ API trước việc người ngoài giả mạo quyền Học viên để vào sửa lịch của PT?"
* **Trả lời**: *"Dạ, thông qua tầng Dependency Injection của FastAPI tại file `app/core/deps.py`. Tại mỗi API nhạy cảm, em gắn hàm kiểm tra: `current_user: User = Depends(require_roles(Role.PT))`. Hệ thống sẽ giải mã chữ ký JWT trong Header, kiểm tra claim `role`. Nếu một token có role `STUDENT` cố tình gọi API của PT, hệ thống sẽ chặn đứng tại cửa với mã lỗi `403 Forbidden`."*

### Câu 10: "Hệ thống có phương án dự phòng nào nếu tính năng OTP gặp sự cố không?"
* **Trả lời**: *"Dạ có. Bảng `attendances` được thiết kế trường `verification_method` dạng Enum gồm: `OTP`, `QR_CODE`, và `GEO_LOCATION` (định vị GPS). Ngoài ra, Quản trị viên (`ADMIN`) có quyền hạn cao nhất trong `admin_service` để kiểm tra bằng chứng nhật ký camera phòng tập và can thiệp xác nhận điểm danh thủ công nếu hai bên có khiếu nại tranh chấp."*

---
*Tài liệu được biên soạn dựa trên cấu trúc chuẩn BCNF và kiến trúc mã nguồn thực tế của dự án PT-Connect.*
