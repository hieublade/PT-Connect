# PT Connect – Tài liệu mô tả dự án

## 1\. Tổng quan dự án

PT Connect là website kết nối học viên với huấn luyện viên cá nhân (PT): học viên chọn PT, mua một khóa tập cố định, đặt lịch từng buổi và đánh giá sau khi tập; PT quản lý khóa học, giờ rảnh và giáo án; Admin duyệt PT và theo dõi thống kê.

**Đối tượng thực hiện:** nhóm 5 sinh viên năm 3 (Thắng, Thành, Hưng, Huy, Hiệu).

**Mục tiêu học tập** – dự án kết hợp kiến thức của 3 môn:

* Lập trình hướng đối tượng – Java (Backend Spring Boot).  
* Cơ sở dữ liệu – MySQL 8\.  
* Lập trình Python (Frontend Streamlit, phân tích dữ liệu, kiểm thử API).

Hệ thống thể hiện rõ:

* Kiến thức OOP trong Backend Java: đóng gói, kế thừa, đa hình, trừu tượng.  
* Thiết kế và thao tác CSDL: ERD, 3NF, ràng buộc, transaction, trigger.  
* Python Frontend giao tiếp với Java Backend qua REST API.  
* Tổ chức mã nguồn theo kiến trúc 3 lớp rõ ràng.  
* Làm việc nhóm bằng Git/GitHub và chạy toàn bộ hệ thống bằng Docker Compose.

Không đặt mục tiêu xây dựng hệ thống production hay thương mại hoàn chỉnh. Thanh toán, ví điện tử và hợp đồng điện tử đều được **mô phỏng** nội bộ, không kết nối cổng thanh toán thật.

## 2\. Phạm vi dự án

**Nguyên tắc:** làm ít nhưng hoàn chỉnh, ưu tiên chức năng phục vụ trực tiếp 3 môn học. Vì CSDL có 13 bảng, nhóm chia chức năng thành 3 mức để không bị quá tải:

* **Bắt buộc (MVP):** phải xong để đạt mục tiêu cốt lõi.  
* **Nên có:** làm nếu đúng tiến độ, bảng DB đã có sẵn.  
* **Mở rộng:** chỉ làm khi dư thời gian.

Hệ thống có 3 vai trò: **Student** (học viên), **PT** (huấn luyện viên), **Admin** (quản trị viên).

### 2.1. Chức năng theo vai trò

| Vai trò | Chức năng | Mức | Bảng DB liên quan |
| ----- | ----- | ----- | ----- |
| Tất cả | Đăng ký, đăng nhập, JWT, phân quyền theo role, mã hóa mật khẩu BCrypt | Bắt buộc | users, wallets |
| Student | Xem danh sách PT, tìm theo tên, xem hồ sơ PT và các khóa học của PT | Bắt buộc | pt\_profiles, courses |
| Student | Nạp tiền vào ví (mô phỏng), mua khóa học, chọn địa điểm tập, nhận hợp đồng | Bắt buộc | wallets, payments, enrollments |
| Student | Xem slot trống, đặt buổi học thử 0đ hoặc đặt buổi trừ vào khóa đã mua | Bắt buộc | availability\_slots, bookings |
| Student | Xem lịch cá nhân, hủy lịch theo chính sách | Bắt buộc | bookings, cancellations |
| Student | Điểm danh xác nhận buổi tập (phía học viên) | Bắt buộc | attendance |
| Student | Đánh giá PT sau buổi tập COMPLETED | Bắt buộc | reviews |
| Student | Xem giáo án và bài tập được giao | Nên có | workout\_plans, workouts |
| PT | Cập nhật hồ sơ (giới thiệu, kinh nghiệm, địa điểm nhận dạy, chính sách phụ thu, chứng chỉ) | Bắt buộc | pt\_profiles |
| PT | Tạo, sửa, ngưng bán khóa học | Bắt buộc | courses |
| PT | Tạo slot giờ rảnh, xóa slot chưa được đặt | Bắt buộc | availability\_slots |
| PT | Xem booking chờ xác nhận, xác nhận hoặc từ chối | Bắt buộc | bookings, cancellations |
| PT | Điểm danh xác nhận buổi tập (phía PT), đánh dấu hoàn thành | Bắt buộc | attendance, bookings |
| PT | Soạn giáo án và bài tập cho từng hợp đồng | Nên có | workout\_plans, workouts |
| Admin | Xem PT chờ duyệt, duyệt hoặc từ chối PT (xem chứng chỉ) | Bắt buộc | users, pt\_profiles |
| Admin | Xem danh sách người dùng, trạng thái tài khoản | Bắt buộc | users |
| Admin | Dashboard thống kê (Pandas \+ Plotly) | Bắt buộc | toàn bộ |
| Admin | Khóa / mở khóa tài khoản (SUSPENDED), xử lý khiếu nại hủy lịch (DISPUTED → RESOLVED) | Mở rộng | users, cancellations |

### 2.2. Kỹ thuật bắt buộc

* **Database:** ERD, chuẩn hóa 3NF, PK/FK/UNIQUE/CHECK, Transaction cho nghiệp vụ mua khóa và đặt lịch, 1 Trigger cập nhật điểm đánh giá.  
* **Java:** Spring Boot, Spring Data JPA, Spring Security \+ JWT, kiến trúc 3 lớp, DTO, `@RestControllerAdvice`, OOP (kế thừa, interface, đa hình).  
* **Python:** Streamlit, Requests, JSON, Pandas, Plotly, Data Generator, API Testing.  
* **DevOps cơ bản:** Git/GitHub, Docker, Docker Compose; AWS EC2 chỉ làm ở giai đoạn cuối nếu bản local đã ổn định.

### 2.3. Ngoài phạm vi

* Thanh toán thật (VNPay, Momo...), chi trả doanh thu cho PT, rút tiền.  
* Email verification, Refresh Token, OAuth, Google Login.  
* Realtime notification, chat, lịch lặp hàng tuần.  
* Lưu trữ S3 Private/Presigned: thay bằng thư mục lưu trữ cục bộ (Docker volume), các cột `*_url` vẫn dùng như thiết kế.  
* Xác thực điểm danh bằng QR/GEO: chỉ dùng OTP; enum `QR_CODE`, `GEO_LOCATION` giữ lại cho mở rộng.  
* Distributed Lock, Redis, xử lý concurrency mức production.

## 3\. Nghiệp vụ cốt lõi

### 3.1. Đăng ký tài khoản

**User Story:** là người dùng mới, tôi muốn đăng ký tài khoản để sử dụng hệ thống.

**Dữ liệu đầu vào:** họ tên, email, mật khẩu, số điện thoại, vai trò (Student hoặc PT). Nếu là PT: thêm kinh nghiệm (năm), địa điểm có thể nhận dạy, danh sách chứng chỉ.

**AC:**

* Email đúng định dạng, không trùng; số điện thoại không trùng (cột `email` và `phone` đều UNIQUE).  
* Mật khẩu tối thiểu 6 ký tự, lưu dưới dạng BCrypt hash trong `password_hash`.  
* Student: `users.status = ACTIVE`, tự động tạo 1 ví (`wallets`) số dư 0\.  
* PT: `users.status = PENDING`, tạo `pt_profiles` với `verification_status = PENDING` và 1 ví; không xuất hiện trong danh sách PT của Student cho đến khi Admin duyệt.  
* Tạo `users`, `pt_profiles`, `wallets` trong **cùng một transaction**.  
* Không tự đăng ký role ADMIN; tài khoản Admin được seed sẵn trong `init.sql`.  
* Không làm email verification.

### 3.2. Đăng nhập và phân quyền

**User Story:** là người dùng đã có tài khoản, tôi muốn đăng nhập để truy cập chức năng tương ứng.

**AC:**

* Đăng nhập bằng email \+ mật khẩu; thành công trả JWT chứa `userId` và `role`.  
* Frontend lưu JWT trong `st.session_state` và gửi kèm header `Authorization: Bearer ...`.  
* Điều hướng sau đăng nhập: Student → Student Home, PT → PT Dashboard, Admin → Admin Dashboard.  
* Sai email/mật khẩu → báo lỗi (401).  
* `status = SUSPENDED` → báo tài khoản bị khóa.  
* PT `status = PENDING` hoặc `verification_status = REJECTED` → đăng nhập được nhưng chỉ xem trạng thái hồ sơ, không dùng được chức năng PT (403).  
* Backend kiểm tra quyền ở từng API (ví dụ Student gọi API xác nhận booking → 403), không chỉ dựa vào việc ẩn nút ở Frontend.  
* Không làm Refresh Token.

### 3.3. Admin duyệt PT

**User Story:** là Admin, tôi muốn xem và duyệt hồ sơ PT để chỉ PT đã xác minh mới được nhận học viên.

**AC:**

* Xem danh sách PT có `verification_status = PENDING`, kèm kinh nghiệm và danh sách chứng chỉ (`certificate_urls`).  
* Duyệt: `verification_status = VERIFIED` và `users.status = ACTIVE`; PT bắt đầu hiển thị cho Student.  
* Từ chối: `verification_status = REJECTED`, `users.status` giữ PENDING.  
* Không làm quy trình duyệt nhiều bước.

### 3.4. PT: hồ sơ và khóa học

**User Story:** là PT, tôi muốn cập nhật hồ sơ và đăng các khóa tập để học viên có thể mua.

**Hồ sơ** gồm: họ tên, số điện thoại, avatar, giới thiệu (`bio`), số năm kinh nghiệm, địa điểm nhận dạy (`available_locations`), chính sách phụ thu theo địa điểm (`location_pricing_note`), danh sách chứng chỉ (`certificate_urls`, dạng JSON).

**Khóa học** gồm: tên, mô tả, tổng số buổi, hạn sử dụng (ngày), giá gốc.

**AC:**

* `experience_years >= 0`, `available_locations` bắt buộc; `total_sessions > 0`, `validity_days > 0`, `base_price >= 0` (khớp CHECK của DB).  
* Khóa chỉ bán trọn gói, **không bán lẻ từng buổi**.  
* PT chỉ sửa/ngưng bán (`status = INACTIVE`) khóa của chính mình; khóa đã có hợp đồng ACTIVE không được xóa, chỉ được ngưng bán; hợp đồng đang chạy không bị ảnh hưởng.  
* Sửa giá/số buổi của khóa **không** làm đổi hợp đồng đã bán (hợp đồng lưu bản chụp `final_price`, `total_sessions`).

### 3.5. PT: tạo slot giờ rảnh

**Input:** ngày, giờ bắt đầu, giờ kết thúc (ví dụ 14/10/2026, 17:00–18:00).

**AC:**

* Không tạo slot trong quá khứ; giờ kết thúc lớn hơn giờ bắt đầu (`chk_slot_time`).  
* Không trùng/chồng thời gian với slot khác của chính PT (DB chặn trùng giờ bắt đầu bằng UNIQUE `pt_id + start_time`; chồng lấn khoảng được Service kiểm tra thêm).  
* Chỉ xóa được slot đang `AVAILABLE` và chưa từng có booking.  
* Mỗi slot tạo thủ công, không làm lịch lặp.

### 3.6. Student xem và tìm PT

**User Story:** là học viên, tôi muốn xem danh sách PT và hồ sơ chi tiết để chọn người phù hợp.

**AC:**

* Danh sách chỉ gồm PT có `verification_status = VERIFIED` và `users.status = ACTIVE`; hiển thị avatar, họ tên, số năm kinh nghiệm, điểm đánh giá trung bình, số lượt đánh giá, giá thấp nhất trong các khóa.  
* Tìm kiếm theo tên; không có kết quả thì hiển thị "Không tìm thấy PT phù hợp".  
* Hồ sơ PT hiển thị giới thiệu, kinh nghiệm, địa điểm nhận dạy, chính sách phụ thu, các khóa `ACTIVE`, các slot `AVAILABLE` trong tương lai và các đánh giá.  
* **Không** trả `certificate_urls` cho Student (chỉ Admin và chính PT được xem).  
* Không bắt buộc: fuzzy search, full-text search, sort nâng cao, phân trang phức tạp.

### 3.7. Ví nội bộ và mua khóa học

**User Story:** là học viên, tôi muốn mua trọn một khóa tập và chốt địa điểm tập để có hợp đồng và kho buổi tập.

**Input:** khóa học, địa điểm tập (chọn 1 trong `available_locations` của PT), ngày bắt đầu.

**Quy trình** (một Transaction):

Student chọn khóa \+ địa điểm  
  ↓  
Backend tính final\_price (= base\_price; nếu địa điểm "tại nhà" thì cộng phụ thu 20%)  
  ↓  
Kiểm tra ví: balance \>= final\_price, ví ACTIVE  
  ↓  
Trừ wallets.balance  
  ↓  
Tạo enrollments (remaining\_sessions \= total\_sessions, end\_date \= start\_date \+ validity\_days)  
  ↓  
Tạo payments (PURCHASE\_PACKAGE, SUCCESS) \+ sinh file hợp đồng PDF → contract\_url  
  ↓  
COMMIT (lỗi bất kỳ bước nào → ROLLBACK)

**AC:**

* Nạp tiền (mô phỏng): tạo `payments` loại `TOPUP`, trạng thái SUCCESS, cộng `balance`.  
* Không đủ tiền → 400, không tạo enrollment.  
* Địa điểm tập cố định duy nhất trong hợp đồng (`training_location`), không đổi sau khi mua.  
* `contract_url` là bắt buộc (NOT NULL): Backend tự sinh file hợp đồng PDF đơn giản và lưu vào thư mục lưu trữ cục bộ.  
* Không cho mua khóa `INACTIVE` hoặc của PT chưa `VERIFIED`.

### 3.8. Đặt lịch (học thử hoặc trừ vào khóa)

**User Story:** là học viên, tôi muốn đặt một slot trống để tập thử hoặc dùng một buổi trong khóa đã mua.

**Input:** slot, loại booking (`TRIAL` hoặc `PACKAGE`), hợp đồng (bắt buộc nếu PACKAGE), ghi chú tùy chọn.

**Quy trình** (`POST /api/v1/bookings`, một Transaction):

Khóa dòng slot (SELECT ... FOR UPDATE), kiểm tra status \= AVAILABLE và start\_time \> now  
  ↓  
PACKAGE: khóa dòng enrollment; kiểm tra ACTIVE, remaining\_sessions \> 0,  
         slot thuộc đúng PT của hợp đồng, slot.start\_time \<= end\_date  
         session\_fee \= final\_price / total\_sessions; remaining\_sessions \- 1  
TRIAL:   enrollment\_id \= NULL, session\_fee \= 0  
  ↓  
Tạo bookings (PENDING) ; slot.status → BOOKED  
  ↓  
COMMIT / ROLLBACK

**AC:**

* Địa điểm buổi PACKAGE tự động theo `training_location` của hợp đồng; Student không chọn lại.  
* Học thử: mỗi Student chỉ được 1 buổi thử với mỗi PT (quy tắc do Service kiểm tra, đề xuất của nhóm).  
* Chống đặt trùng 2 lớp: Service kiểm tra slot \+ ràng buộc UNIQUE trên `active_slot_id` (cột sinh tự động, chỉ có giá trị khi booking còn hiệu lực). Vi phạm → 409 Conflict.  
* Booking bị hủy thì `active_slot_id = NULL`, slot được trả về `AVAILABLE` cho người khác đặt.  
* Student không đặt hai buổi trùng giờ với nhau.  
* Không yêu cầu Distributed Lock hay Redis.

### 3.9. PT xác nhận booking

* PT xem danh sách booking `PENDING` (tên Student, loại booking, thời gian, địa điểm, ghi chú).  
* **Xác nhận:** `PENDING → CONFIRMED`; slot giữ `BOOKED`.  
* **Từ chối:** booking chuyển `CANCELLED`, ghi 1 bản ghi `cancellations` (`cancelled_by_role = PT`, lý do bắt buộc theo DB), trả lại 1 buổi vào `remaining_sessions` (nếu PACKAGE), slot về `AVAILABLE`. Khi từ chối ngay khi PENDING thì không phạt.

### 3.10. Điểm danh và hoàn thành buổi tập

* Điểm danh xác thực hai phía bằng **OTP**: PT mở buổi và hiện mã OTP 6 số, Student nhập mã → `student_confirmed = true`; PT bấm xác nhận → `pt_confirmed = true`.  
* Chỉ ghi `check_in_time` khi booking `CONFIRMED` và trong khoảng \[giờ bắt đầu − 15 phút, giờ kết thúc\]; đến muộn quá 15 phút → `status = LATE`.  
* Khi `student_confirmed` và `pt_confirmed` đều true và có `check_out_time` → booking `COMPLETED`.  
* Quá giờ kết thúc mà không ai check-in → `ABSENT` (Student vắng, buổi vẫn bị tính); làm bằng xử lý khi PT/Admin đánh dấu, không cần job nền.  
* Khi hợp đồng hết buổi và mọi booking đã COMPLETED/CANCELLED → `enrollments.status = COMPLETED`; quá `end_date` → `EXPIRED` (kiểm tra khi truy cập hoặc bằng `@Scheduled` đơn giản).

### 3.11. Hủy lịch, phạt và đền bù

Mỗi lần hủy sinh 1 bản ghi `cancellations` (mỗi booking tối đa 1 bản ghi). Chính sách **đề xuất** (nhóm có thể chỉnh con số, được đặt thành hằng số trong code):

| Người hủy | Thời điểm | Khôi phục buổi (`refund_amount`) | Đền bù (`compensation_amount`) | Phạt (`penalty_amount`) |
| ----- | ----- | ----- | ----- | ----- |
| Student | PENDING, hoặc CONFIRMED và cách giờ tập ≥ 24 giờ | Có, trả 1 buổi (= session\_fee) | 0 | 0 |
| Student | CONFIRMED, cách giờ tập \< 24 giờ | Không (mất buổi) | 50% session\_fee cộng vào ví PT | 0 |
| PT | CONFIRMED, cách giờ tập ≥ 24 giờ | Có, trả 1 buổi | 0 | 0 |
| PT | CONFIRMED, cách giờ tập \< 24 giờ | Có, trả 1 buổi | 20% session\_fee cộng vào ví Student | 20% session\_fee trừ ví PT |
| Admin | Bất khả kháng (có `evidence_url`) | Có, trả 1 buổi | 0 | 0 |
| Student | Booking TRIAL | Không có buổi để trả, chỉ trả slot | 0 | 0 |

* `hours_before_session` \= số giờ từ lúc hủy đến `slot.start_time`.  
* Tiền đền bù ghi thành `payments` loại `COMPENSATION`; khôi phục tiền dùng `REFUND`.  
* Sau khi hủy: slot về `AVAILABLE`, `remaining_sessions + 1` nếu được khôi phục, khiếu nại để `status = DISPUTED`, Admin xử lý xong đổi thành `RESOLVED` (mở rộng).  
* Cả 3 giá trị tiền đều \>= 0 (CHECK `chk_cancel_amounts`).

### 3.12. Đánh giá PT và Trigger

**Input:** số sao 1–5, nhận xét tùy chọn.

**AC:**

* Chỉ đánh giá khi booking `COMPLETED` và đúng Student đã đặt booking đó; mỗi booking đúng 1 review (`booking_id` UNIQUE).  
* Sau khi thêm review, **Trigger** `AFTER INSERT ON reviews` tự cập nhật `pt_profiles.average_rating` (AVG) và `total_reviews` (COUNT). Java không tự tính điểm này.  
* Đây là chức năng minh họa Trigger của môn CSDL.

### 3.13. Giáo án (Nên có)

* PT tạo `workout_plans` cho mỗi hợp đồng (tiêu đề, mục tiêu, ngày bắt đầu/kết thúc) và thêm các bài tập `workouts` (tên, nhóm cơ, hiệp, lần lặp, tạ, nghỉ, link video demo).  
* Chỉ PT của hợp đồng được tạo; chỉ Student của hợp đồng được xem.  
* Ngày giáo án nằm trong khoảng hợp đồng; `sets > 0`, `reps > 0`, `rest_seconds >= 0`.

### 3.14. Dashboard Admin

**User Story:** là Admin, tôi muốn xem thống kê để theo dõi tình hình sử dụng hệ thống.

**AC:**

* Hiển thị tổng Student, tổng PT, tổng Booking, tổng doanh thu bán khóa (`payments` PURCHASE\_PACKAGE SUCCESS).  
* Có ít nhất 3 biểu đồ Plotly: Booking theo trạng thái, Booking/doanh thu theo tháng, Top PT theo điểm đánh giá.  
* Dữ liệu lấy qua REST API, xử lý bằng Pandas.

## **4\. Trạng thái hệ thống**

| Đối tượng | Trạng thái | Ý nghĩa |
| ----- | ----- | ----- |
| users.status | ACTIVE, PENDING, SUSPENDED | PENDING dành cho PT chờ duyệt; SUSPENDED \= bị khóa (mở rộng) |
| pt\_profiles.verification\_status | PENDING, VERIFIED, REJECTED | Chỉ VERIFIED mới hiển thị cho Student |
| courses.status | ACTIVE, INACTdan+ | INACTIVE \= ngừng bán, không ảnh hưởng hợp đồng đã bán |
| enrollments.status | ACTIVE, EXPIRED, CANCELLED, COMPLETED | EXPIRED khi quá `end_date`; COMPLETED khi dùng hết buổi |
| availability\_slots.status | AVAILABLE, BOOKED, LOCKED | BOOKED \= đã có 1 booking còn hiệu lực; LOCKED \= PT tạm khóa (mở rộng) |
| bookings.status | PENDING, CONFIRMED, COMPLETED, CANCELLED | Xem luồng bên dưới |
| attendance.status | PRESENT, ABSENT, LATE | Kết quả điểm danh |
| cancellations.status | PROCESSED, DISPUTED, RESOLVED | DISPUTED và RESOLVED là mở rộng |
| wallets.status | ACTIVE, FROZEN | FROZEN \= không được giao dịch |
| payments.status | PENDING, SUCCESS, FAILED, REFUNDED | Giao dịch mô phỏng thường SUCCESS ngay |

**Vòng đời PT:**

Đăng ký → users.status \= PENDING, verification\_status \= PENDING  
   → Admin duyệt → ACTIVE \+ VERIFIED → xuất hiện cho Student  
   → Admin từ chối → verification\_status \= REJECTED

**Vòng đời Booking:**

PENDING ──PT xác nhận──► CONFIRMED ──điểm danh 2 phía──► COMPLETED ──► (Student đánh giá)  
   │                        │  
   └──Student/PT hủy────────┴──Student/PT/Admin hủy──► CANCELLED (+ bản ghi cancellations)

**Ràng buộc trạng thái chính:**

* Slot `BOOKED` khi và chỉ khi tồn tại 1 booking PENDING/CONFIRMED/COMPLETED trỏ tới nó.  
* Booking `CANCELLED` luôn trả slot về `AVAILABLE` (nếu slot chưa diễn ra).  
* Review chỉ được tạo khi booking `COMPLETED`.  
* `remaining_sessions` luôn trong khoảng 0 đến `total_sessions`; trừ khi tạo booking PACKAGE, hoàn khi booking bị hủy theo chính sách.

## **5\. Thiết kế cơ sở dữ liệu**

CSDL gồm **13 bảng** (MySQL 8.0.16 trở lên để CHECK có hiệu lực), định nghĩa trong `database/init.sql`: tạo bảng → index → khóa ngoại → dữ liệu mẫu.

### **5.1. Danh sách bảng**

| \# | Bảng | Vai trò | Khóa ngoại | Ràng buộc đáng chú ý |
| ----- | ----- | ----- | ----- | ----- |
| 1 | users | Tài khoản, định danh, role, trạng thái | – | `email`, `phone` UNIQUE |
| 2 | pt\_profiles | Hồ sơ năng lực PT, địa điểm nhận dạy, chứng chỉ (JSON), điểm đánh giá | user\_id | `user_id` UNIQUE (1-1); rating 0–5; kinh nghiệm \>= 0 |
| 3 | wallets | Ví nội bộ (balance, locked\_balance) | user\_id | `user_id` UNIQUE (1-1); `balance >= 0`; `locked_balance <= balance` |
| 4 | courses | Khóa học cố định của PT | pt\_id | số buổi \> 0, hạn \> 0, giá \>= 0 |
| 5 | enrollments | Hợp đồng khóa tập đã mua, kho buổi còn lại | student\_id, course\_id, pt\_id | `0 <= remaining <= total`; `end_date >= start_date`; `contract_url` NOT NULL |
| 6 | availability\_slots | Khung giờ rảnh của PT | pt\_id | UNIQUE (`pt_id`, `start_time`); `end_time > start_time`; index (`pt_id`, `start_time`, `status`) |
| 7 | bookings | Đặt lịch (TRIAL hoặc PACKAGE) | enrollment\_id, student\_id, pt\_id, slot\_id | UNIQUE `active_slot_id` (cột sinh); TRIAL ⇔ enrollment NULL |
| 8 | reviews | Đánh giá sau buổi tập | booking\_id, student\_id, pt\_id | `booking_id` UNIQUE; rating 1–5 |
| 9 | cancellations | Hủy lịch, phạt, đền bù | booking\_id, cancelled\_by\_id | `booking_id` UNIQUE; 3 số tiền \>= 0 |
| 10 | workout\_plans | Giáo án theo hợp đồng | enrollment\_id, pt\_id | `end_date >= start_date` |
| 11 | workouts | Bài tập trong giáo án | plan\_id | sets, reps \> 0; rest \>= 0 |
| 12 | attendance | Điểm danh hai phía | booking\_id | `booking_id` UNIQUE; `check_out >= check_in` |
| 13 | payments | Giao dịch tài chính | wallet\_id, enrollment\_id | `amount > 0`; `transaction_ref` UNIQUE |

### **5.2. Quan hệ chính (ERD dạng chữ)**

users 1───—1 pt\_profiles          (chỉ user có role PT)  
users 1───—1 wallets  
pt\_profiles 1───—N courses  
pt\_profiles 1───—N availability\_slots  
users(Student) 1───—N enrollments —N──—1 courses  
enrollments 1───—N bookings          (booking TRIAL thì enrollment\_id \= NULL)  
availability\_slots 1───—N bookings   (nhưng chỉ tối đa 1 booking còn hiệu lực)  
bookings 1───—1 reviews | 1───—1 cancellations | 1───—1 attendance   (các quan hệ tùy chọn)  
enrollments 1───—N workout\_plans 1───—N workouts  
wallets 1───—N payments —N───—1 enrollments (tùy chọn)

**Cạm bẫy cần nhớ khi code:** các cột `pt_id` trong `courses`, `enrollments`, `availability_slots`, `bookings`, `reviews`, `workout_plans` đều trỏ tới **`pt_profiles.id`**, không phải `users.id`. Còn `student_id` và `cancelled_by_id` trỏ tới `users.id`.

### **5.3. Chuẩn hóa và đánh đổi thiết kế (để trả lời vấn đáp)**

Thiết kế hướng tới 3NF; có 3 chỗ **chủ động** không thuần 3NF và nhóm phải giải thích được:

* **Bản chụp hợp đồng:** `enrollments.final_price` và `total_sessions` sao chép từ khóa học → đúng nghiệp vụ, vì sửa khóa sau này không được làm đổi hợp đồng đã ký.  
* **`pt_id` dư trong `enrollments`, `bookings`, `reviews`:** có thể suy ra qua course/slot/booking, nhưng giữ để truy vấn nhanh và đơn giản. Đánh đổi: Service phải bảo đảm nhất quán (ví dụ `slot.pt_id = enrollment.pt_id` khi đặt lịch PACKAGE).  
* **`pt_profiles.average_rating`, `total_reviews`:** dữ liệu dẫn xuất, được Trigger duy trì để tránh `AVG()` mỗi lần liệt kê PT.

`certificate_urls` dùng kiểu JSON vì số chứng chỉ mỗi PT không cố định; `available_locations` là text phân tách bằng dấu `;` (Service tách thành danh sách khi hiển thị).

### **5.4. Transaction**

Hai nghiệp vụ bắt buộc dùng Transaction (`@Transactional` ở lớp Service):

* **Mua khóa:** trừ ví → tạo enrollment → tạo payment (mục 3.7).  
* **Đặt lịch:** khóa slot (và enrollment) → tạo booking → đổi slot BOOKED → trừ `remaining_sessions` (mục 3.8).  
* Các nghiệp vụ phụ cùng dùng Transaction: đăng ký (users \+ pt\_profiles \+ wallets), hủy lịch (booking \+ cancellation \+ hoàn buổi \+ payment đền bù).

Chống đặt trùng dùng khóa dòng (`@Lock(PESSIMISTIC_WRITE)` trên Repository) cộng với UNIQUE `active_slot_id` làm chốt chặn cuối ở DB.

### **5.5. Trigger (bắt buộc, chỉ 1 trigger)**

DELIMITER \$\$  
CREATE TRIGGER trg\_reviews\_after\_insert  
AFTER INSERT ON reviews  
FOR EACH ROW  
BEGIN  
  UPDATE pt\_profiles  
  SET average\_rating \= (SELECT ROUND(AVG(rating), 2\) FROM reviews WHERE pt\_id \= NEW.pt\_id),  
      total\_reviews  \= (SELECT COUNT(\*)               FROM reviews WHERE pt\_id \= NEW.pt\_id)  
  WHERE id \= NEW.pt\_id;  
END\$\$  
DELIMITER ;

Trigger được thêm vào cuối `init.sql` (phần 5\) hoặc file `database/trigger.sql` chạy sau `init.sql`. Stored Procedure không bắt buộc; nếu giảng viên yêu cầu thì viết 1 procedure thống kê số booking theo trạng thái.

## **6\. Kiến trúc Backend Java và OOP**

### **6.1. Công nghệ**

Java 17+, Spring Boot 4.x (theo khung đã khởi tạo ở Milestone 1), Spring Web, Spring Data JPA, Spring Security, JJWT, Lombok, MySQL 8.0, Maven.

### **6.2. Kiến trúc 3 lớp**

Controller  →  Service (Interface \+ Impl)  →  Repository  →  MySQL

* **Controller:** nhận request, validate (`@Valid`), gọi Service, trả `ApiResponse`. Không được truy cập Repository trực tiếp.  
* **Service:** chứa nghiệp vụ, kiểm tra điều kiện, quản lý Transaction.  
* **Repository:** Spring Data JPA làm việc với DB.

### **Cấu trúc gói chuẩn (Package root: com.PTconnect.backend):**

### **backend/src/main/java/com/PTconnect/backend/**

### **├── config/        SecurityConfig, JwtFilter, CorsConfig**

### **├── controller/    AuthController, PTProfileController, CourseController, SlotController,**

### **│                  BookingController, EnrollmentController, WalletController,**

### **│                  AttendanceController, ReviewController, WorkoutPlanController, AdminController**

### **├── service/       interface I\*Service**

### **│   └── impl/      \*ServiceImpl**

### **├── policy/        CancellationPolicy \+ StudentCancellationPolicy, PtCancellationPolicy, AdminCancellationPolicy**

### **├── payment/       PaymentMethodHandler \+ WalletPaymentHandler, BankTransferHandler (mô phỏng)**

### **├── repository/    \*Repository**

### **├── entity/        User, Student, PT, Admin, PTProfile, Wallet, Course, Enrollment, AvailabilitySlot,**

### **│                  Booking, Review, Cancellation, WorkoutPlan, Workout, Attendance, Payment**

### **│   └── enums/     Role, UserStatus, VerificationStatus, WalletStatus, CourseStatus,**

### **│                  EnrollmentStatus, SlotStatus, BookingType, BookingStatus, AttendanceStatus,**

### **│                  VerificationMethod, CancellationStatus, PaymentType, PaymentMethod, PaymentStatus**

### **├── dto/           request/ và response/**

### **├── exception/     GlobalExceptionHandler \+ các exception nghiệp vụ**

### **└── util/          JwtUtil, ApiResponse, ContractPdfGenerator, OtpUtil**

### 

### **6.3. Bốn tính chất OOP và nơi thể hiện**

| Tính chất | Thể hiện trong dự án |
| ----- | ----- |
| Đóng gói | Mọi Entity có thuộc tính `private` \+ getter/setter. Quy tắc nghiệp nằm trong phương thức của Entity thay vì setter trần: `Wallet.debit(amount)`, `Wallet.credit(amount)` (không cho số dư âm), `Enrollment.consumeSession()`, `Enrollment.restoreSession()` (giữ 0 ≤ remaining ≤ total), `AvailabilitySlot.book()`, `release()`. |
| Kế thừa | `User` (abstract, `@Inheritance(SINGLE_TABLE)`, `@DiscriminatorColumn(name = "role")`) → `Student`, `PT`, `Admin`. Cột `role` của bảng `users` chính là discriminator. `PTProfile` là Entity riêng, quan hệ `@OneToOne` với `PT`. |
| Đa hình | `User` khai báo phương thức trừu tượng như `getHomePage()`, `getDisplayRole()`, `canAccess(Feature)`; 3 lớp con override khác nhau. Ngoài ra: `CancellationPolicy.calculate(booking, now)` có 3 hiện thực (Student/PT/Admin) trả về `refund`, `compensation`, `penalty`; `PaymentMethodHandler.pay(...)` có hiện thực theo `payment_method`. Service chỉ gọi qua interface (mẫu Strategy). |
| Trừu tượng | Mỗi nhóm nghiệp vụ có interface Service: `IAuthService`, `IUserService`, `IPTService`, `ICourseService`, `ISlotService`, `IEnrollmentService`, `IWalletService`, `IBookingService`, `ICancellationService`, `IAttendanceService`, `IReviewService`, `IWorkoutPlanService`, `IStatisticsService`; Controller phụ thuộc interface, không phụ thuộc lớp cài đặt. |

Không tạo kế thừa chỉ để làm hệ thống phức tạp hơn.

### **6.4. DTO và ánh xạ**

* Không trả trực tiếp Entity ra API; `UserDTO` không chứa `password_hash`; `PTPublicDTO` dành cho Student không chứa `certificate_urls`, `PTPrivateDTO` dành cho Admin/chính PT mới có.  
* Ánh xạ Entity ↔ DTO viết tay (các lớp `*Mapper`), không bắt buộc MapStruct.  
* Request DTO dùng Bean Validation (`@NotBlank`, `@Email`, `@Size`, `@Min`...).

### **6.5. Xử lý ngoại lệ**

Dùng `@RestControllerAdvice` (`GlobalExceptionHandler`) ánh xạ exception sang HTTP status:

| Exception | HTTP | Tình huống |
| ----- | ----- | ----- |
| `ResourceNotFoundException` | 404 | Không tìm thấy PT, slot, khóa... |
| `BookingConflictException` | 409 | Slot đã có người đặt, trùng giờ |
| `InvalidBookingException` | 400 | Hết buổi, quá hạn hợp đồng, slot quá khứ, sai PT |
| `InsufficientBalanceException` | 400 | Ví không đủ tiền mua khóa |
| `UnauthorizedException` | 401 / 403 | Sai thông tin đăng nhập / không đủ quyền |
| `MethodArgumentNotValidException` | 400 | Dữ liệu đầu vào sai định dạng |

Không tạo thêm quá nhiều custom exception.

## **7\. API contract**

Tất cả endpoint có tiền tố `/api/v1`. API ngoài nhóm Auth đều yêu cầu JWT; cột "Quyền" là role được phép gọi, Backend kiểm tra ở từng API.

### **7.1. Authentication**

| Method | Endpoint | Quyền | Mô tả |
| ----- | ----- | ----- | ----- |
| POST | /auth/register | Công khai | Đăng ký Student hoặc PT |
| POST | /auth/login | Công khai | Đăng nhập, trả JWT |
| GET | /auth/me | Mọi role | Thông tin tài khoản đang đăng nhập |
| PUT | /users/avatar | Mọi role | Cập nhật ảnh đại diện (avatar) |

### **7.2. Student**

| Method | Endpoint | Quyền | Mô tả |
| ----- | ----- | ----- | ----- |
| GET | /pt-profiles?name= | Student | Danh sách PT đã duyệt, tìm theo tên |
| GET | /pt-profiles/{id} | Student | Hồ sơ PT (không có chứng chỉ) |
| GET | /pt-profiles/{id}/courses | Student | Khóa ACTIVE của PT |
| GET | /pt-profiles/{id}/slots | Student | Slot AVAILABLE trong tương lai |
| GET | /pt-profiles/{id}/reviews | Student | Đánh giá của PT |
| GET | /wallet | Student, PT | Xem ví và lịch sử giao dịch |
| POST | /wallet/topup | Student | Nạp tiền (mô phỏng) |
| POST | /enrollments | Student | Mua khóa, tạo hợp đồng |
| GET | /enrollments/my | Student | Hợp đồng của tôi, số buổi còn lại |
| GET | /enrollments/{id}/contract | Student | Tải hợp đồng PDF |
| POST | /bookings | Student | Đặt lịch TRIAL/PACKAGE |
| GET | /bookings/my | Student | Lịch của tôi, lọc theo trạng thái |
| PUT | /bookings/{id}/cancel | Student | Hủy lịch theo chính sách |
| POST | /attendance/{bookingId}/student-confirm | Student | Nhập OTP để điểm danh |
| POST | /reviews | Student | Đánh giá booking COMPLETED |
| GET | /enrollments/{id}/workout-plans | Student, PT | Giáo án và bài tập của hợp đồng |

### **7.3. PT**

| Method | Endpoint | Quyền | Mô tả |
| ----- | ----- | ----- | ----- |
| GET | /pt/profile | PT | Xem hồ sơ của mình (cả chứng chỉ) |
| PUT | /pt/profile | PT | Cập nhật hồ sơ |
| POST | /pt/courses | PT | Tạo khóa học |
| GET | /pt/courses | PT | Danh sách khóa của mình |
| PUT | /pt/courses/{id} | PT | Sửa khóa, đổi ACTIVE/INACTIVE |
| POST | /pt/slots | PT | Tạo slot |
| GET | /pt/slots | PT | Danh sách slot của mình |
| DELETE | /pt/slots/{id} | PT | Xóa slot chưa có booking |
| GET | /pt/bookings?status= | PT | Booking của mình (mặc định PENDING) |
| PUT | /pt/bookings/{id}/confirm | PT | PENDING → CONFIRMED |
| PUT | /pt/bookings/{id}/reject | PT | Từ chối, hủy kèm lý do |
| PUT | /pt/bookings/{id}/cancel | PT | Hủy booking đã CONFIRMED |
| GET | /pt/bookings/{id}/otp | PT | Lấy mã OTP điểm danh |
| POST | /pt/attendance/{bookingId}/confirm | PT | PT xác nhận, hoàn thành buổi |
| GET | /pt/enrollments | PT | Hợp đồng đang dạy |
| POST | /pt/workout-plans | PT | Tạo giáo án cho hợp đồng |
| POST | /pt/workout-plans/{id}/workouts | PT | Thêm bài tập |

### **7.4. Admin**

| Method | Endpoint | Quyền | Mô tả |
| ----- | ----- | ----- | ----- |
| GET | /admin/pt/pending | Admin | PT chờ duyệt kèm chứng chỉ |
| PUT | /admin/pt/{id}/approve | Admin | Duyệt PT |
| PUT | /admin/pt/{id}/reject | Admin | Từ chối PT |
| GET | /admin/users?role= | Admin | Danh sách người dùng |
| GET | /admin/statistics | Admin | Số liệu tổng hợp |
| GET | /admin/bookings | Admin | Dữ liệu booking cho Pandas |
| GET | /admin/payments | Admin | Dữ liệu thanh toán cho Pandas |
| PUT | /admin/users/{id}/status | Admin | Khóa/mở khóa tài khoản (mở rộng) |
| PUT | /admin/bookings/{id}/cancel | Admin | Hủy do bất khả kháng (mở rộng) |

### **7.5. Mã trạng thái HTTP**

`200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict` (xung đột nghiệp vụ như slot không còn khả dụng), `500 Internal Server Error`.

### **7.6. Định dạng phản hồi thống nhất**

{  
  "timestamp": "2026-10-13T20:00:00Z",  
  "status": 200,  
  "message": "Lấy dữ liệu thành công",  
  "data": {}  
}

Điều quan trọng là Frontend biết request thành công hay thất bại và hiển thị được nội dung lỗi; lỗi không cần cấu trúc phức tạp.

## **8\. Frontend Python, dữ liệu và kiểm thử**

Python đóng vai trò **Frontend Client** giao tiếp với Java Backend qua REST API. Công nghệ: Python 3.10+, Streamlit, Requests, Pandas, Plotly, Faker, bcrypt, pytest.

### **8.1. Cấu trúc thư mục**

frontend/  
├── app.py                 điểm vào, điều hướng theo role, quản lý st.session\_state  
├── requirements.txt  
├── api/                   mỗi file bọc các lời gọi requests, tự gắn JWT và xử lý lỗi  
│   ├── client.py          hàm request dùng chung (base URL, header Bearer, parse ApiResponse)  
│   ├── auth\_api.py  pt\_api.py  course\_api.py  booking\_api.py  
│   ├── wallet\_api.py  attendance\_api.py  admin\_api.py  
├── pages/  
│   ├── login.py  register.py  
│   ├── student.py         (chia nhỏ: pt\_list, pt\_detail, wallet, my\_courses, my\_bookings, review)  
│   ├── pt.py              (dashboard, profile, courses, slots, bookings, workout\_plans)  
│   └── admin.py           (pending\_pt, users, dashboard)  
├── components/            pt\_card.py, booking\_table.py, slot\_picker.py, course\_card.py  
├── analytics/             stats.py (Pandas), charts.py (Plotly)  
└── tools/  
    ├── generate\_data.py   Data Generator  
    └── tests/             API Testing (pytest)

Không viết toàn bộ Frontend vào một file. Streamlit không triển khai Refresh Token, OAuth hay Google Login; JWT được lưu trong `st.session_state`.

### **8.2. Màn hình theo vai trò**

| Vai trò | Màn hình |
| ----- | ----- |
| Chung | Login, Register |
| Student | Danh sách PT (lưới), Chi tiết PT (khóa \+ slot \+ đánh giá), Ví (nạp tiền, lịch sử), Mua khóa, Khóa của tôi (số buổi còn lại, hợp đồng, giáo án), Đặt lịch, Lịch của tôi (chờ duyệt / sắp tới / lịch sử), Điểm danh OTP, Đánh giá |
| PT | Dashboard, Hồ sơ (cả chứng chỉ), Khóa học của tôi, Slot của tôi, Booking chờ duyệt, Lịch dạy sắp tới \+ OTP, Giáo án |
| Admin | Dashboard thống kê, PT chờ duyệt, Người dùng |

Không cần thiết kế UI quá cầu kỳ; lỗi hiển thị bằng `st.error`, thành công bằng `st.success`.

### **8.3. Data Generator (`tools/generate_data.py`)**

* Dùng Faker tạo dữ liệu tiếng Việt: \~30 Student, \~8 PT (các trạng thái khác nhau), khóa học, slot, enrollment, \~150 booking trải đều 3 tháng, review, payment.  
* Sinh mật khẩu BCrypt thật (`bcrypt`), mật khẩu mặc định của tài khoản demo được ghi trong README.  
* Xuất `database/seed_demo.sql` đúng thứ tự phụ thuộc FK và **tuân thủ mọi CHECK/UNIQUE** (ví dụ `remaining_sessions` khớp số booking, `session_fee = final_price / total_sessions`). Không tự tính `average_rating`: để Trigger tự chạy khi insert review.  
* Chạy lại nhiều lần cho cùng kết quả (cố định `seed`).

### **8.4. Phân tích dữ liệu (Pandas \+ Plotly)**

Dữ liệu lấy từ `/admin/statistics`, `/admin/bookings`, `/admin/payments` bằng Requests, đưa vào DataFrame rồi vẽ. Tối thiểu 3 biểu đồ:

1. Booking theo trạng thái (biểu đồ cột).  
2. Booking và doanh thu bán khóa theo tháng (đường).  
3. Top PT theo điểm đánh giá và số buổi đã dạy (cột ngang).

Mở rộng: tỷ lệ hủy theo người hủy, phân bố khung giờ được đặt nhiều nhất.

### **8.5. API Testing (`tools/tests/`)**

Bộ pytest \+ Requests chạy trên hệ thống đang bật, in PASS/FAIL cho từng ca. Danh sách ca tối thiểu:

| \# | Ca kiểm thử | Kết quả mong đợi |
| ----- | ----- | ----- |
| 1 | Đăng ký Student hợp lệ | 201 |
| 2 | Đăng ký email trùng | 409 hoặc 400 |
| 3 | Đăng nhập sai mật khẩu | 401 |
| 4 | Student gọi API Admin | 403 |
| 5 | PT tạo slot trong quá khứ | 400 |
| 6 | PT tạo slot trùng giờ | 400 hoặc 409 |
| 7 | Mua khóa khi ví không đủ tiền | 400, số dư không đổi |
| 8 | Mua khóa thành công | 201, ví bị trừ, `remaining_sessions` \= `total_sessions` |
| 9 | Đặt slot AVAILABLE | 201, booking PENDING, slot BOOKED |
| 10 | Hai Student cùng đặt 1 slot | đúng 1 request 201, request còn lại 409 |
| 11 | PT confirm rồi Student hủy trước 24 giờ | `remaining_sessions` tăng lại 1 |
| 12 | Đánh giá booking chưa COMPLETED | 400 |
| 13 | Đánh giá lần 2 cùng booking | 409 hoặc 400 |
| 14 | Đánh giá hợp lệ | 201, `average_rating` của PT đổi (Trigger) |

## **9. Kế hoạch triển khai theo Milestone**

#### **GIAI ĐOẠN 1: Nền tảng (đến 18/10)**

### **Milestone 1: Khởi tạo project (Hạn chót: 07/10/2026) – ĐÃ XONG**

* **Mục tiêu:** Java chạy được, Python chạy được, MySQL chạy được bằng Docker.  
* **Công việc chi tiết:**  
  * Khởi tạo repo GitHub, chia nhánh `main`, `develop`.  
  * Viết `docker-compose.yml` gồm 3 service: MySQL 8.0, Backend, Frontend.  
  * Tạo khung Spring Boot 4.x trống và file `app.py` Streamlit in ra chữ "Hello".

**Output 1:** Repository trên GitHub với 2 nhánh chuẩn `main` và `develop` ([github.com/hieublade/PT-Connect](https://github.com/hieublade/PT-Connect)).

**Output 2:** File `docker-compose.yml` định nghĩa mạng nội bộ và 3 container.

**Output 3:** Terminal hiển thị trạng thái Running của 3 container sau `docker compose up -d`.

**Output 4:** `localhost:8501` hiển thị trang Streamlit "Hello World"; log Spring Boot báo Tomcat khởi động thành công ở port 8080.

### **Milestone 2: Kết nối Backend với Database (Hạn chót: 15/10/2026)**

* **Mục tiêu:** Chốt schema 13 bảng, hoàn thiện toàn bộ Entity và Repository; kiểm tra kết nối Backend với MySQL qua API.  
* **Công việc chi tiết:**  
  * Chốt script `init.sql` và schema chuẩn 3NF cho 13 bảng.  
  * Backend ánh xạ toàn bộ Entity (sử dụng `@Inheritance` cho User, ánh xạ khóa ngoại chính xác, `pt_id` trỏ `pt_profiles.id`) và Repository tương ứng.  
  * Viết API GET đơn giản (danh sách Users) qua Controller → Service → Repository để kiểm tra kết nối CSDL thành công.

**Output 1:** Script `init.sql` tạo cấu trúc 13 bảng đúng chuẩn 3NF và dữ liệu mẫu khởi tạo.

**Output 2:** Toàn bộ class Entity và Repository trong Java với annotation ánh xạ chính xác quan hệ CSDL.

**Output 3:** Backend kết nối thành công với MySQL, API kiểm tra trả về HTTP 200 OK.

**📌 Quy ước cấu trúc mã nguồn Backend (Package gốc: com.PTconnect.backend):**

* **Entity & Enum:** backend/src/main/java/com/PTconnect/backend/entity/ (Enum để trong entity/enums/)  
* **Repository:** backend/src/main/java/com/PTconnect/backend/repository/  
* **Controller, Service, DTO, Exception:** backend/src/main/java/com/PTconnect/backend/{controller, service, dto, exception}/

### **Milestone 3: Authentication (Hạn chót: 18/10/2026) – *Nút thắt kỹ thuật***

* **Mục tiêu:** Register, Login, BCrypt, JWT, Role. Milestone bắt buộc phải xong trước khi làm các tính năng khác.  
* **Công việc chi tiết:**  
  * Backend: cấu hình Spring Security Filter Chain; hash mật khẩu bằng BCrypt; API trả JWT; kiểm tra phân quyền (Student không gọi được API Admin).  
  * Frontend: màn Login/Register; lưu JWT vào `st.session_state` để giữ đăng nhập khi chuyển trang và điều hướng theo vai trò.

**Output 1:** `POST /api/v1/auth/register` insert thành công user vào DB với mật khẩu đã băm BCrypt, tự động tạo ví và hồ sơ PT (ở trạng thái PENDING) trong cùng một transaction.

**Output 2:** `POST /api/v1/auth/login` trả chuỗi JWT chứa thông tin định danh và role (STUDENT, PT, ADMIN).

**Output 3:** Frontend Python gọi `requests` đăng nhập thành công, trích JWT từ JSON, lưu vào `st.session_state` và điều hướng đúng trang theo role.

**Output 4:** Cơ chế phân quyền API theo Role hoạt động chính xác (trả 403 Forbidden khi người dùng gọi API vượt quyền hạn).

#### **GIAI ĐOẠN 2: Nghiệp vụ PT và Student (18/10 – 28/10)**

### **Milestone 4: Chức năng PT (Hạn chót: 21/10/2026)**

* **Mục tiêu:** PT Profile, Course, Create/Delete/View Slot; Admin duyệt PT.  
* **Công việc chi tiết:**  
  * Backend: logic slot không nằm trong quá khứ, giờ kết thúc lớn hơn giờ bắt đầu, không chồng giờ, chỉ xóa slot chưa có booking; CRUD khóa học; Admin duyệt/từ chối PT.  
  * Frontend: PT Dashboard, form cập nhật hồ sơ, quản lý khóa học và slot, trang Admin duyệt PT.

**Output 1:** Giao diện Dashboard PT trên Streamlit hiển thị form cập nhật hồ sơ cá nhân và quản lý danh sách khóa học.

**Output 2:** Bộ API quản lý slot giờ rảnh (`/pt/slots`) ghi slot vào DB với trạng thái mặc định `AVAILABLE` và đầy đủ xác thực (chặn quá khứ, chặn trùng/chồng giờ, chỉ xóa slot chưa booking).

**Output 3:** Bộ API quản lý khóa học (`/pt/courses`) cho phép tạo, sửa, ngưng bán khóa học (không cho xóa khóa đã có hợp đồng).

**Output 4:** Chức năng Admin duyệt/từ chối PT thành công: cập nhật `verification_status = VERIFIED`, `users.status = ACTIVE`, kích hoạt hiển thị cho Student.

### **Milestone 5: Chức năng Student (Hạn chót: 24/10/2026)**

* **Mục tiêu:** View PT, Search PT, View Profile, View Slot, Nạp ví, Mua khóa.  
* **Công việc chi tiết:**  
  * Backend: API danh sách PT đã duyệt; nạp tiền; mua khóa trong 1 Transaction (trừ ví → enrollment → payment → hợp đồng PDF).  
  * Frontend: lưới danh sách PT, tìm kiếm theo tên, hiển thị slot chỉ ở trạng thái AVAILABLE, trang Ví và Mua khóa.

**Output 1:** Giao diện danh sách PT trên Streamlit chỉ hiển thị PT `VERIFIED` và `ACTIVE`, hỗ trợ tìm kiếm theo tên.

**Output 2:** Màn Chi tiết PT hiển thị thông tin giới thiệu, các gói khóa học đang mở bán và các slot giờ rảnh khả dụng (AVAILABLE).

**Output 3:** Chức năng Ví nội bộ: nạp tiền mô phỏng và theo dõi số dư, lịch sử giao dịch.

**Output 4:** Mua khóa thành công trong 1 Transaction: ví bị trừ đúng `final_price`, tạo bản ghi `enrollments` (`remaining_sessions = total_sessions`), ghi nhận `payments` PURCHASE_PACKAGE và sinh file hợp đồng PDF.

### **Milestone 6: Luồng Booking – Trái tim hệ thống (Hạn chót: 28/10/2026)**

* **Mục tiêu:** Student Book → PENDING → PT Confirm / Reject → CONFIRMED / CANCELLED; hỗ trợ cả TRIAL và PACKAGE. Cập nhật avatar người dùng.  
* **Công việc chi tiết:**  
  * Backend: Dùng `@Transactional` bao bọc kiểm tra slot và tạo booking; khóa bi quan (`PESSIMISTIC_WRITE`) trên dòng slot và enrollment; kiểm tra slot tại thời điểm request để chống đặt trùng; trừ `remaining_sessions`.  
  * Frontend: Streamlit gọi API Booking, hiển thị thông báo trạng thái; giao diện PT duyệt booking; đổi avatar người dùng.

**Output 1:** API `POST /api/v1/bookings` chạy thành công khối `@Transactional`: tạo bản ghi `bookings` trạng thái PENDING, slot thành BOOKED, `remaining_sessions` giảm 1 (với PACKAGE).

**Output 2:** Giao diện PT Dashboard hiển thị danh sách booking đang PENDING; hỗ trợ thao tác Confirm (chuyển CONFIRMED) hoặc Reject (chuyển CANCELLED, hoàn buổi, trả slot về AVAILABLE).

**Output 3:** Xử lý chống đặt trùng slot: hai request đồng thời vào cùng 1 slot chỉ 1 request thành công, request còn lại nhận 409 Conflict.

**Output 4:** Trang quản lý lịch cá nhân của Student (hiển thị lịch chờ duyệt, sắp tới và lịch sử).

**Output 5:** Chức năng cập nhật ảnh đại diện người dùng qua API và hiển thị chuẩn xác trên hồ sơ cá nhân và danh sách tìm kiếm.

#### **GIAI ĐOẠN 3: Điểm danh, Đánh giá, Quản trị và Hoàn thiện (28/10 – 04/11)**

### **Milestone 7: Điểm danh, Hủy lịch và Review + Trigger (Hạn chót: 01/11/2026)**

* **Mục tiêu:** CONFIRMED → điểm danh hai phía → COMPLETED → Đánh giá → Trigger tính `average_rating`; hủy lịch có chính sách hoàn/đền bù.  
* **Công việc chi tiết:**  
  * Database: viết đúng 1 Trigger MySQL `AFTER INSERT ON reviews` cập nhật `AVG(rating)` và `total_reviews` vào `pt_profiles`.  
  * Backend: API điểm danh hai phía bằng OTP; API hủy lịch theo `CancellationPolicy` áp dụng hoàn buổi, phạt, đền bù; API tạo Review (chỉ đánh giá khi COMPLETED, 1 lần duy nhất).  
  * Frontend: Giao diện PT hiển thị OTP; giao diện Student nhập OTP và giao diện gửi đánh giá số sao (1–5).

**Output 1:** Chức năng điểm danh hai phía bằng OTP đưa booking sang trạng thái COMPLETED.

**Output 2:** Chức năng hủy lịch tự động áp dụng chính sách hoàn buổi, đền bù hoặc phạt tiền vào ví nội bộ dựa trên mốc thời gian trước/sau 24 giờ.

**Output 3:** Giao diện đánh giá (1–5 sao) trên màn hình học viên cho các buổi tập COMPLETED; Trigger MySQL tự động cập nhật `average_rating` và `total_reviews` của PT ngay khi đánh giá được lưu.

### **Milestone 8: Giáo án, Admin và Thống kê (Hạn chót: 04/11/2026)**

* **Mục tiêu:**  
  * Hoàn thiện Admin Dashboard và quản lý tài khoản.  
  * Hoàn thiện phân tích dữ liệu (Pandas + Plotly) trên giao diện Admin.  
  * Chuẩn bị dữ liệu mẫu phục vụ demo.  
  * Hoàn thành chức năng Giáo án (mức Nên có).  
* **Công việc chi tiết:**  
  * Backend: API thống kê tổng quan (Student/PT/Booking/Doanh thu); API trả dữ liệu cho phân tích; API quản lý giáo án và bài tập (`workout_plans`, `workouts`); API khóa/mở khóa tài khoản người dùng.  
  * Python: Streamlit Admin Dashboard; Requests lấy dữ liệu từ Backend; Pandas xử lý; Plotly tối thiểu 3 biểu đồ; Data Generator tạo dữ liệu mẫu phong phú.

**Output 1:** Admin Dashboard hiển thị thống kê tổng quan (tổng Student, PT, Booking, doanh thu) và quản lý danh sách, trạng thái người dùng (khóa/mở khóa).

**Output 2:** Hệ thống biểu đồ trực quan hóa dữ liệu (Plotly + Pandas) trên Dashboard Admin (trạng thái booking, doanh thu theo tháng, top PT).

**Output 3:** Chức năng Giáo án và bài tập (PT soạn giáo án theo từng hợp đồng, Student theo dõi bài tập được giao).

**Output 4:** Script Python (`tools/generate_data.py`) tự động sinh dữ liệu mẫu hợp lệ, đầy đủ ràng buộc để phục vụ chạy demo hệ thống.

#### **GIAI ĐOẠN 4: Triển khai hạ tầng và Chuẩn bị bảo vệ (04/11 – 10/11)**

### **Milestone 9: Đóng gói Docker Compose hoàn chỉnh (Hạn chót: 07/11/2026)**

* **Mục tiêu:** Bất kỳ ai clone về gõ `docker compose up -d` là chạy; toàn bộ luồng MVP chạy ổn trên môi trường Docker.  
* **Công việc chi tiết:**  
  * Tối ưu Dockerfile của Spring Boot (đóng gói file `.jar` độc lập) và Streamlit (`requirements.txt` ghim phiên bản).  
  * Cấu hình container Backend tự đợi MySQL sẵn sàng (`healthcheck` kết hợp `depends_on: condition: service_healthy`).  
  * Chạy hồi quy toàn bộ luồng MVP, dọn dẹp mã nguồn.

**Output 1:** Repository sạch sẽ, chuẩn hóa cấu trúc thư mục, biến môi trường `.env.example` và README hướng dẫn khởi chạy.

**Output 2:** Dockerfile Backend multi-stage build thành `.jar` và Dockerfile Frontend Streamlit hoạt động ổn định.

**Output 3:** File `docker-compose.yml` hoàn chỉnh, khởi động toàn bộ 3 dịch vụ đồng bộ chỉ với lệnh `docker compose up -d`.

## **10. Git, Docker, MVP và tiêu chí nghiệm thu**

### **Git workflow**

* Nhánh: `main` (ổn định, dùng để nộp), `develop` (tích hợp), `feature/*` (mỗi người làm việc tại đây), ví dụ `feature/auth`, `feature/database`, `feature/course-wallet`, `feature/booking`, `feature/review-trigger`, `feature/analytics`, `feature/frontend`.  
* Không push trực tiếp vào `main`; mọi thay đổi qua Pull Request, ít nhất 1 thành viên khác review trước khi merge vào `develop`.  
* Commit theo Conventional Commits: `feat: add login api`, `feat: add booking feature`, `fix: fix slot conflict`, `chore: update docker compose`.

### **Docker**

| Service | Image / cách chạy | Ghi chú |
| ----- | ----- | ----- |
| mysql | `mysql:8.0` | Volume lưu dữ liệu; mount `database/init.sql` vào `/docker-entrypoint-initdb.d`; có `healthcheck` |
| backend | Build từ Dockerfile (Spring Boot `.jar`) | `depends_on: mysql (service_healthy)`; volume cho thư mục hợp đồng PDF |
| frontend | Build từ Dockerfile (Streamlit) | Gọi Backend qua tên service; mở port 8501 |

Nghiệm thu: sau khi clone, `docker compose up -d` là khởi động được toàn bộ hệ thống. Không yêu cầu tối ưu production.

### **MVP cuối cùng**

Phiên bản được xem là hoàn thành khi chạy trơn được luồng sau:

1. PT đăng ký (PENDING), Admin duyệt → PT xuất hiện trên hệ thống.  
2. PT tạo khóa học và slot giờ rảnh.  
3. Student đăng nhập, tìm PT, xem hồ sơ, khóa và slot.  
4. Student đặt buổi học thử → booking PENDING → PT xác nhận → CONFIRMED.  
5. Student nạp ví, mua khóa → hợp đồng, `remaining_sessions` \= `total_sessions`.  
6. Student đặt buổi theo khóa → PENDING → PT xác nhận → CONFIRMED; `remaining_sessions` giảm 1\.  
7. Buổi tập diễn ra, điểm danh hai phía bằng OTP → COMPLETED.  
8. Student đánh giá → Trigger cập nhật `average_rating`.  
9. Admin xem Dashboard thống kê (Pandas \+ Plotly).  
10. Một lịch bị hủy: hoàn buổi, đền bù, phạt đúng chính sách.

BOOKED có nghĩa là slot đã có một booking đang xử lý và không thể được Student khác đặt.

### **Tiêu chí thành công**

1. Database có thiết kế hợp lý.  
2. Python gọi được REST API.  
3. Luồng Student → Mua khóa → Booking → PT Confirm chạy được.  
4. Luồng Review → Trigger → Rating chạy được.  
5. Phân quyền hoạt động.  
6. Nhóm giải thích được code.  
7. Nhóm giải thích được ERD (kể cả 3 chỗ denormalize có chủ đích).  
8. Nhóm giải thích được các tính chất OOP đã dùng.  
9. Mọi thành viên có thể clone và chạy project.

