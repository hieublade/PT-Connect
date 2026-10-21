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

**Output 4:** `localhost:8501` hiển thị trang Streamlit "Hello World"; log Spring Boot báo Tomcat khởi động thành công ở port 8080\.

### **Milestone 2: Kết nối Backend với Database (Hạn chót: 15/10/2026)**

* **Mục tiêu:** Chốt schema 13 bảng, toàn bộ Entity và Repository; test bằng Postman.  
* **Công việc chi tiết:**  
  * Chốt `init.sql` và ERD chuẩn 3NF cho 13 bảng.  
  * Backend map Entity với `@Inheritance` cho User, map khóa ngoại đúng (nhớ `pt_id` trỏ `pt_profiles.id`).  
  * Viết 1 API GET đơn giản (danh sách Users) để kiểm tra nối DB thành công.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Thắng** (DB Lead) | Script `init.sql` 13 bảng đúng 3NF, có PK, FK, UNIQUE, CHECK, cột sinh `active_slot_id`. Thay mật khẩu mẫu bằng BCrypt hợp lệ, bổ sung dữ liệu mẫu nhất quán (payment cho enrollment \#1). Chạy `docker compose down -v && up` không lỗi. Entity `Course`, `Enrollment`, `Payment` và 3 Repository. |  |
| 2 | **Thành** (ERD và Tài liệu) | Sơ đồ ERD thể hiện rõ 13 bảng, PK, FK, quan hệ 1-1 và 1-N. File hợp đồng schema và giải thích 3NF (kèm 3 chỗ denormalize có chủ đích). Entity `Review` và `ReviewRepository`. |  |
| 3 | **Hưng** (Backend – nhóm User) | Entity `User` (dùng `@Inheritance`) cùng `Student`, `PT`, `Admin`; enum `Role`, `UserStatus`, `VerificationStatus`; Entity `PTProfile` (1-1 với PT), `Wallet`; `UserRepository`, `PTProfileRepository`, `WalletRepository`. |  |
| 4 | **Huy** (Backend – nhóm nghiệp vụ) | Entity `AvailabilitySlot` (N-1 với PTProfile), `Booking` (N-1 Student, N-1 Slot, cột `active_slot_id` chỉ đọc), `Cancellation`, `Attendance`, các enum trạng thái và 4 Repository. |  |
| 5 | **Hiệu** (API và Postman) | 1 API GET danh sách Users qua Controller → Service → Repository, dùng `UserDTO` (không trả password), kèm `ApiResponse` và `GlobalExceptionHandler`. Entity `WorkoutPlan`, `Workout`. Postman Collection có request trả 200 OK và `[]`. |  |

**Output 1:** Script `init.sql` tạo cấu trúc 13 bảng đúng chuẩn 3NF.

**Output 2:** Các class Entity trong Java với annotation ánh xạ chính xác quan hệ khóa ngoại 1-1, 1-N.

**Output 3:** Collection Postman test kết nối thành công, trả HTTP 200 OK (ví dụ mảng rỗng `[]` khi chưa có user, chứng tỏ Backend đã query MySQL thành công).

**Output 4:** Sơ đồ ERD hoàn chỉnh (.png hoặc .drawio / Mermaid) thể hiện 13 bảng, PK, FK và quan hệ 1-1, 1-N.

**📌 Quy ước thư mục chung cho cả 5 người (Package gốc: com.PTconnect.backend):**

* **Entity & Enum:** backend/src/main/java/com/PTconnect/backend/entity/ (Enum để trong entity/enums/)  
* **Repository:** backend/src/main/java/com/PTconnect/backend/repository/  
* **Controller, Service, DTO, Exception:** backend/src/main/java/com/PTconnect/backend/{controller, service, dto, exception}/  
* **Tài liệu & Postman:** Thư mục docs/ và postman/ ở thư mục gốc.

### **Milestone 3: Authentication (Hạn chót: 18/10/2026) – *Nút thắt kỹ thuật***

* **Mục tiêu:** Register, Login, BCrypt, JWT, Role. Milestone bắt buộc phải xong trước khi làm các tính năng khác.  
* **Công việc chi tiết:**  
  * Backend: cấu hình Spring Security Filter Chain; hash mật khẩu bằng BCrypt; API trả JWT; test kỹ phân quyền (Student không gọi được API Admin).  
  * Frontend: màn Login/Register; lưu JWT vào `st.session_state` để giữ đăng nhập khi chuyển trang.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Hưng** | `SecurityConfig`, `JwtFilter`, `JwtUtil`; `POST /auth/register` (tạo users \+ pt\_profiles \+ wallets trong 1 transaction), `POST /auth/login`, `GET /auth/me`; BCrypt; PT mới đăng ký ở PENDING. | `backend/.../config/`, `.../controller/AuthController`, `.../service/` |
| 2 | **Hiệu** | `api/client.py` (gắn Bearer, parse `ApiResponse`), `auth_api.py`, trang Login/Register, lưu JWT trong `st.session_state`, điều hướng theo role. | `frontend/app.py`, `frontend/api/`, `frontend/pages/login.py` |
| 3 | **Huy** | Bộ test phân quyền: ma trận role × nhóm API (401/403) bằng MockMvc, chụp log Security từ chối Student gọi API Admin. | `backend/src/test/`, `postman/` |
| 4 | **Thắng** | Xác nhận DB: `password_hash` là BCrypt, ví được tạo, trùng email/phone bị UNIQUE chặn; seed tài khoản Admin dùng được. | `database/init.sql`, `docs/db-evidence-m3.md` |
| 5 | **Thành** | Tài liệu luồng Auth (sơ đồ trình tự) và bộ pytest đầu tiên: đăng ký hợp lệ, email sai/trùng, mật khẩu \< 6 ký tự, đăng nhập sai. | `docs/api-auth.md`, `frontend/tools/tests/test_auth.py` |

**Output 1:** `POST /api/v1/auth/register` insert thành công user vào DB với mật khẩu đã băm BCrypt.

**Output 2:** `POST /api/v1/auth/login` trả chuỗi JWT chứa role (STUDENT, PT, ADMIN).

**Output 3:** Frontend Python gọi `requests` đăng nhập thành công, trích JWT từ JSON và lưu vào `st.session_state`.

**Output 4:** Log Spring Security từ chối (403 Forbidden) khi cố tình dùng token Student gọi API Admin.

#### **GIAI ĐOẠN 2: Nghiệp vụ PT và Student (18/10 – 28/10)**

### **Milestone 4: Chức năng PT (Hạn chót: 21/10/2026)**

* **Mục tiêu:** PT Profile, Course, Create/Delete/View Slot; Admin duyệt PT.  
* **Công việc chi tiết:**  
  * Backend: logic slot không nằm trong quá khứ, giờ kết thúc lớn hơn giờ bắt đầu, không chồng giờ, chỉ xóa slot chưa có booking; CRUD khóa học; Admin duyệt/từ chối PT.  
  * Frontend: PT Dashboard, form cập nhật hồ sơ, quản lý khóa học và slot, trang Admin duyệt PT.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Hưng** | `GET/PUT /pt/profile` (validate, lưu `certificate_urls` dạng JSON); `GET /admin/pt/pending`, \`PUT /admin/pt/{id}/approve | reject\`; trang PT: Hồ sơ; trang Admin: PT chờ duyệt. |
| 2 | **Thắng** | `POST/GET/PUT /pt/courses` với quy tắc không xóa khóa đã có hợp đồng, ngưng bán được; trang PT: Khóa học. | `.../CourseController`, `frontend/pages/pt.py` |
| 3 | **Huy** | `POST/GET/DELETE /pt/slots` với đủ quy tắc (quá khứ, kết thúc \> bắt đầu, chồng giờ, chỉ xóa slot chưa booking); trang PT: Slot của tôi. | `.../SlotController`, `frontend/pages/pt.py` |
| 4 | **Hiệu** | Khung PT Dashboard (menu theo role, layout), component dùng chung; Postman cho toàn bộ API PT; chốt request/response nhóm API Student (mục 7.2) cho M5. | `frontend/components/`, `postman/` |
| 5 | **Thành** | Test tự động các quy tắc slot và khóa học (các ca 400); tài liệu API PT; cập nhật ERD nếu schema đổi. | `frontend/tools/tests/test_pt.py`, `docs/api-pt.md` |

**Output 1:** Giao diện Dashboard PT trên Streamlit hiển thị form cập nhật hồ sơ cá nhân và danh sách khóa học.

**Output 2:** API `POST /api/v1/pt/slots` ghi slot vào DB với trạng thái mặc định `AVAILABLE`.

**Output 3:** Xử lý lỗi API (400 Bad Request) khi PT tạo slot có giờ bắt đầu trong quá khứ hoặc trùng giờ với slot cũ.

**Output 4:** Admin duyệt PT thành công: `verification_status = VERIFIED`, `users.status = ACTIVE`.

### **Milestone 5: Chức năng Student (Hạn chót: 24/10/2026)**

* **Mục tiêu:** View PT, Search PT, View Profile, View Slot, Nạp ví, Mua khóa.  
* **Công việc chi tiết:**  
  * Backend: API danh sách PT đã duyệt; nạp tiền; mua khóa trong 1 Transaction (trừ ví → enrollment → payment → hợp đồng PDF).  
  * Frontend: lưới danh sách PT, hiển thị slot chỉ ở trạng thái AVAILABLE, trang Ví và Mua khóa.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Hiệu** | `GET /pt-profiles?name=`, `/pt-profiles/{id}`, `/{id}/courses`; Streamlit: Danh sách PT dạng lưới, tìm theo tên, Chi tiết PT. | `.../PTProfileController`, `frontend/pages/student.py`, `frontend/components/pt_card.py` |
| 2 | **Thắng** | `POST /wallet/topup`, `GET /wallet`, `POST /enrollments` (Transaction \+ sinh hợp đồng PDF \+ `payments`), `GET /enrollments/my`; trang Student: Ví, Mua khóa. | `.../WalletController`, `.../EnrollmentController`, `.../util/ContractPdfGenerator` |
| 3 | **Hưng** | Phân tách `PTPublicDTO` / `PTPrivateDTO` (Student không thấy chứng chỉ); `GET /admin/users`, trang Admin: Người dùng; test phân quyền cho API mới. | `.../dto/`, `frontend/pages/admin.py` |
| 4 | **Huy** | `GET /pt-profiles/{id}/slots` chỉ trả slot AVAILABLE trong tương lai; viết nháp `BookingService` và test đơn vị cho logic kiểm tra đặt lịch (chuẩn bị M6). | `.../SlotController`, `backend/src/test/` |
| 5 | **Thành** | Test mua khóa (thiếu tiền 400, thành công 201), bằng chứng SQL: rollback không để lại enrollment/payment rác; cập nhật tài liệu. | `frontend/tools/tests/test_purchase.py`, `docs/db-evidence-m5.md` |

**Output 1:** Giao diện danh sách PT trên Streamlit chỉ render PT `VERIFIED` và `ACTIVE`.

**Output 2:** Tìm kiếm theo tên trả danh sách đã lọc, hoặc hiển thị "Không tìm thấy PT phù hợp" nếu mảng JSON rỗng.

**Output 3:** Màn Chi tiết PT hiển thị hồ sơ, khóa học và các giờ trống (AVAILABLE).

**Output 4:** Mua khóa thành công: ví bị trừ đúng `final_price`, có dòng `enrollments` (`remaining_sessions = total_sessions`), dòng `payments` PURCHASE\_PACKAGE và file hợp đồng PDF tải được.

### **Milestone 6: Luồng Booking – Trái tim hệ thống (Hạn chót: 28/10/2026)**

* **Mục tiêu:** Student Book → PENDING → PT Confirm / Reject → CONFIRMED / CANCELLED; hỗ trợ cả TRIAL và PACKAGE.  
* **Công việc chi tiết:**  
  * Backend: đây là phần cần khoe code với giảng viên. Dùng `@Transactional` bao bọc kiểm tra slot và tạo booking; khóa dòng slot và enrollment; kiểm tra slot tại thời điểm request để chống đặt trùng; trừ `remaining_sessions`.  
  * Frontend: Streamlit gọi API Booking, hiển thị lỗi bằng `st.error`, thành công bằng `st.success`.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Huy** | `POST /bookings` (TRIAL và PACKAGE) với `@Transactional`, `PESSIMISTIC_WRITE`, 409 khi trùng; `PUT /pt/bookings/{id}/confirm` và `/reject` (reject ghi `cancellations`, trả buổi, trả slot); trang PT: Booking chờ duyệt. | `.../BookingController`, `.../BookingServiceImpl`, `frontend/pages/pt.py` |
| 2 | **Hưng** | `GET /bookings/my` (lọc theo trạng thái) và `GET /pt/bookings` với `BookingResponse` DTO (ghép tên PT/Student, thời gian, địa điểm); chặn xem booking của người khác. | `.../dto/BookingResponse`, `.../BookingController` |
| 3 | **Hiệu** | Trang Student: Đặt lịch (chọn TRIAL/PACKAGE \+ hợp đồng), Lịch của tôi (chờ duyệt / sắp tới / lịch sử). | `frontend/pages/student.py`, `frontend/components/booking_table.py` |
| 4 | **Thắng** | `Enrollment.consumeSession()`/`restoreSession()` và kiểm tra hạn/hết buổi trong `EnrollmentService`; script kiểm thử 2 luồng cùng đặt 1 slot chứng minh UNIQUE `active_slot_id` chặn được. | `.../entity/Enrollment`, `database/tests/concurrency.sql` hoặc `backend/src/test/` |
| 5 | **Thành** | Test tự động: đặt slot AVAILABLE, 2 Student đặt cùng slot, hết buổi, quá hạn, học thử lần 2; bằng chứng SQL trước/sau. | `frontend/tools/tests/test_booking.py`, `docs/db-evidence-m6.md` |

**Output 1:** `POST /api/v1/bookings` chạy thành công khối `@Transactional`: tạo bản ghi `bookings` trạng thái PENDING, slot thành BOOKED, `remaining_sessions` giảm 1 (PACKAGE).

**Output 2:** Giao diện PT Dashboard hiển thị danh sách booking đang PENDING.

**Output 3:** PT bấm Confirm → booking CONFIRMED. Bấm Reject → booking CANCELLED, có bản ghi `cancellations`, slot tự động về AVAILABLE, `remaining_sessions` được hoàn.

**Output 4:** Chứng minh chống đặt trùng: hai request cùng lúc vào 1 slot, chỉ một request thành công, request còn lại nhận 409 Conflict.

#### **GIAI ĐOẠN 3: Điểm danh, Đánh giá, Quản trị và Hoàn thiện (28/10 – 04/11)**

### **Milestone 7: Điểm danh, Hủy lịch và Review \+ Trigger (Hạn chót: 01/11/2026)**

* **Mục tiêu:** CONFIRMED → điểm danh hai phía → COMPLETED → Đánh giá → Trigger tính `average_rating`; hủy lịch có chính sách hoàn/đền bù.  
* **Công việc chi tiết:**  
  * Database: viết đúng 1 Trigger MySQL `AFTER INSERT ON reviews` cập nhật `AVG(rating)` và `total_reviews` vào `pt_profiles`.  
  * Backend: API điểm danh OTP; API hủy lịch theo `CancellationPolicy`; API tạo Review (booking phải COMPLETED, chỉ đánh giá 1 lần).

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Thành** | Script Trigger `AFTER INSERT ON reviews`; `POST /reviews` (chỉ booking COMPLETED, đúng chủ booking, 1 lần); trang Student: Đánh giá (chọn 1–5 sao); bằng chứng `average_rating` tự đổi. | `database/trigger.sql`, `.../ReviewController`, `frontend/pages/student.py`, `docs/db-evidence-m7.md` |
| 2 | **Huy** | `AttendanceService`: sinh/kiểm tra OTP (`OtpUtil`), Student xác nhận, PT xác nhận, trạng thái PRESENT/LATE/ABSENT, booking → COMPLETED; `CancellationPolicy` \+ 3 hiện thực (Student/PT/Admin); trang PT: Điểm danh \+ OTP. | `.../AttendanceController`, `.../policy/`, `frontend/pages/pt.py` |
| 3 | **Thắng** | Áp kết quả chính sách lên ví: ghi `payments` loại REFUND/COMPENSATION, cộng/trừ `wallets` trong cùng Transaction; khôi phục `remaining_sessions`; trạng thái enrollment COMPLETED/EXPIRED. | `.../WalletServiceImpl`, `.../EnrollmentServiceImpl` |
| 4 | **Hưng** | `PUT /bookings/{id}/cancel`, `PUT /pt/bookings/{id}/cancel` (lý do bắt buộc, `evidence_url` tùy chọn); unit test JUnit cho từng dòng bảng chính sách mục 3.11 (chứng minh đa hình). | `.../BookingController`, `backend/src/test/policy/` |
| 5 | **Hiệu** | Trang Student: nút Hủy lịch (hiển thị trước số tiền hoàn/đền bù), nhập OTP điểm danh; Postman cho nhóm API mới. | `frontend/pages/student.py`, `postman/` |

**Output 1:** Màn Student My Bookings cho phép đánh giá (chọn 1–5 sao) các lịch có trạng thái COMPLETED.

**Output 2:** Script SQL chứa Trigger `AFTER INSERT ON reviews`.

**Output 3:** Bằng chứng minh họa CSDL: sau khi gọi API gửi review, query thủ công `pt_profiles` cho thấy `average_rating` và `total_reviews` tự động thay đổi mà không có logic Java nào tác động.

**Output 4:** Điểm danh hai phía thành công đưa booking sang COMPLETED; hủy trước/sau 24 giờ cho kết quả khôi phục buổi, đền bù, phạt đúng bảng chính sách (JUnit PASS).

### **Milestone 8: Giáo án, Admin và Thống kê (Hạn chót: 04/11/2026)**

* **Mục tiêu:**  
  * Hoàn thiện Admin.  
  * Hoàn thiện Python Data Analytics.  
  * Hoàn thiện Python API Testing.  
  * Chuẩn bị dữ liệu mẫu phục vụ demo.  
  * Hoàn thành Giáo án (mức Nên có).  
* **Công việc chi tiết:**  
  * Backend: API thống kê Student/PT/Booking/Doanh thu; API trả dữ liệu cho Python Analytics; API giáo án.  
  * Python: Streamlit Admin Dashboard; Requests lấy dữ liệu từ Backend; Pandas xử lý; Plotly ít nhất 3 biểu đồ; Data Generator; API Testing.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Thành** | `GET /admin/statistics`, `/admin/bookings`, `/admin/payments`; `analytics/stats.py` (Pandas) và `charts.py` (Plotly) ít nhất 3 biểu đồ; Admin Dashboard. | `.../AdminController`, `frontend/analytics/`, `frontend/pages/admin.py` |
| 2 | **Thắng** | `generate_data.py` tạo `seed_demo.sql` hợp lệ mọi CHECK/UNIQUE, có `seed` cố định; nạp vào DB; kiểm tra Trigger tính đúng rating cho dữ liệu mẫu. | `frontend/tools/generate_data.py`, `database/seed_demo.sql` |
| 3 | **Hiệu** | `WorkoutPlan`/`Workout` API (PT tạo, Student xem) và giao diện tương ứng; Postman cuối cùng cho toàn bộ API. | `.../WorkoutPlanController`, `frontend/pages/`, `postman/` |
| 4 | **Hưng** | `PUT /admin/users/{id}/status` (khóa/mở khóa, chặn đăng nhập khi SUSPENDED); gắn các trang Admin thành một Dashboard thống nhất. | `.../AdminController`, `frontend/pages/admin.py` |
| 5 | **Huy** | Xử lý ABSENT và công việc `@Scheduled` đánh dấu enrollment EXPIRED; bổ sung test pytest cho điểm danh, hủy lịch (các ca 11–14 mục 8.5). | `.../scheduler/`, `frontend/tools/tests/test_attendance.py` |

**Output 1:** Admin Dashboard hiển thị thống kê cơ bản (tổng Student, PT, Booking, doanh thu).

**Output 2:** Ít nhất 3 biểu đồ Plotly dùng dữ liệu đã xử lý bằng Pandas.

**Output 3:** Script Python có thể tạo dữ liệu mẫu hợp lệ và nạp vào DB.

**Output 4:** Script Python API Testing chạy được và hiển thị PASS/FAIL cho 14 ca.

**Output 5:** Có thể chứng minh Python lấy dữ liệu từ Java Backend thông qua REST API.

#### **GIAI ĐOẠN 4: Triển khai hạ tầng và Chuẩn bị bảo vệ (04/11 – 10/11)**

### **Milestone 9: Đóng gói Docker Compose hoàn chỉnh (Hạn chót: 07/11/2026)**

* **Mục tiêu:** Bất kỳ ai clone về gõ `docker compose up -d` là chạy; toàn bộ luồng MVP chạy ổn trên môi trường Docker.  
* **Công việc chi tiết:**  
  * Tối ưu Dockerfile của Spring Boot (đóng gói file `.jar`) và Streamlit (`requirements.txt`).  
  * Đảm bảo container backend tự đợi container DB sẵn sàng (healthcheck).  
  * Chạy hồi quy toàn bộ luồng MVP, sửa lỗi còn lại.

| \# | Người | Output cần nộp | File / vị trí |
| ----- | ----- | ----- | ----- |
| 1 | **Thắng** | Dockerfile Backend đa giai đoạn (build `.jar`), `docker-compose.yml` với `healthcheck` MySQL \+ `depends_on: condition: service_healthy`, volume cho MySQL và thư mục hợp đồng PDF, `.env.example`. | `backend/Dockerfile`, `docker-compose.yml` |
| 2 | **Hiệu** | Dockerfile Frontend, `requirements.txt` ghim phiên bản, `.gitignore`, README hướng dẫn chạy; dọn repo; merge `develop` → `main`. | `frontend/Dockerfile`, `README.md` |
| 3 | **Hưng** | Đưa JWT secret, mật khẩu DB ra biến môi trường; tắt profile `dev`; rà lại CORS và phân quyền; hồi quy Auth/Role. | `backend/src/main/resources/`, `.env.example` |
| 4 | **Huy** | Hồi quy Booking, Hủy, Điểm danh trên môi trường Docker; sửa lỗi. | issue tracker / PR |
| 5 | **Thành** | Chạy toàn bộ pytest trên bản clone sạch, lưu kết quả; cập nhật tài liệu, ERD cuối cùng. | `docs/test-report.md` |

**Output 1:** Repository sạch sẽ (không chứa file rác, file build cục bộ).

**Output 2:** Dockerfile Backend được tối ưu, build độc lập thành `.jar` và tự động đợi MySQL sẵn sàng.

**Output 3:** Bất kỳ thành viên nào xóa toàn bộ môi trường cũ, clone code mới nhất và gõ `docker compose up -d`, hệ thống tự build lại image và chạy mượt.

## **Git, Docker, MVP và tiêu chí nghiệm thu**

### **Git workflow**

* Nhánh: `main` (ổn định, dùng để nộp), `develop` (tích hợp), `feature/*` (mỗi người làm việc tại đây), ví dụ `feature/auth`, `feature/database`, `feature/course-wallet`, `feature/booking`, `feature/review-trigger`, `feature/analytics`, `feature/frontend`.  
* Không push trực tiếp vào `main`; mọi thay đổi qua Pull Request, ít nhất 1 thành viên khác review trước khi merge vào `develop` (cặp review ở mục 9.3).  
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

