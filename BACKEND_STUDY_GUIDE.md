# CẨM NANG TOÀN DIỆN BACKEND PT-CONNECT (HẠN 01/11)
> **Chiến lược 80/20:** 20% cốt lõi kiến trúc quyết định 80% điểm số và sự ổn định của hệ thống. 
> Hiểu rõ dòng chảy dữ liệu từ Frontend qua từng tầng Backend xuống Database và ngược lại.

---

## 🚀 PHẦN 1: BẢN ĐỒ DÒNG CHẢY DỮ LIỆU (FE $\rightarrow$ BE $\rightarrow$ DB $\rightarrow$ FE)

Khi người dùng bấm một nút trên màn hình (Frontend), dữ liệu đi qua toàn bộ các thư mục của Backend theo chu trình sau:

```
[ FRONTEND (React / Streamlit / Postman) ]
      │  ▲
(1)   │  │ (10) HTTP Response (JSON chuẩn qua ApiResponse & DTO Response)
HTTP  │  │
Req   ▼  │
┌────────────────────────────────────────────────────────────────────────┐
│ BACKEND (Spring Boot)                                                  │
│                                                                        │
│ 1. [ resources/ ]   : Chứa cấu hình nền (DB URL, Port, Secret Key)     │
│                         được nạp ngay khi khởi động server.            │
│ 2. [ config/ ]      : "Người gác cổng" (JwtFilter & SecurityConfig)    │
│                         chặn Request -> Kiểm tra Token -> Cấp quyền.   │
│ 3. [ dto/request/ ] : "Thùng hàng đầu vào" bóc tách JSON thành Object, │
│                         kiểm tra dữ liệu hợp lệ (@NotNull, @Min).      │
│ 4. [ controller/ ]  : "Quầy tiếp tân" hứng Request theo URL (Route),  │
│                         gọi hàm Service tương ứng xử lý.               │
│ 5. [ service/ ]     : "Bộ não trung tâm" xử lý nghiệp vụ, tính toán,   │
│                         quản lý Transaction (Rollback nếu lỗi).        │
│    ├── [ policy/ ]  : Chiến lược riêng biệt (Strategy/Factory hủy ca). │
│    ├── [ handler/ ] : Chiến lược riêng cho đăng ký theo Role.         │
│    └── [ util/ ]    : Công cụ phụ trợ (Sinh OTP, xuất file PDF).       │
│ 6. [ exception/ ]   : "Bệnh viện cấp cứu" bắt mọi lỗi văng ra từ       │
│                         Service -> Đóng gói thành mã lỗi sạch (400,404)│
│ 7. [ repository/ ]  : "Thủ kho" sinh câu SQL, khóa dữ liệu (Lock),     │
│                         thực hiện CRUD với Database.                   │
│ 8. [ entity/ ]      : "Bản thiết kế" ánh xạ bảng DB thành Java Class.  │
│ 9. [ dto/response/ ]: "Thùng hàng đầu ra" chọn lọc dữ liệu an toàn     │
│                         trả về cho người dùng.                         │
└────────────────────────────────────────────────────────────────────────┘
      │  ▲
(6)   │  │ (7) SQL Result
SQL   │  │
Query ▼  │
[ DATABASE (MySQL / PostgreSQL) ]
```

---

## 📦 PHẦN 2: BẢN CHẤT CỦA JSON & CƠ CHẾ "THÔNG DỊCH VIÊN" (HTTP BODY & SPRING BOOT)

### 1. JSON thực chất là gì?
- **JSON (JavaScript Object Notation)** bản chất **chỉ là một đoạn văn bản thuần (plain text)** được viết theo định dạng cặp `"key": "value"`, bao bọc bởi `{}`.
- **Tại sao phải có JSON?**
  - Trình duyệt/Frontend viết bằng **JavaScript/TypeScript**.
  - Backend viết bằng **Java**.
  - Hai ngôn ngữ này không thể trực tiếp hiểu được Object của nhau (JavaScript không biết `Java Class` là gì, còn Java không thể đọc trực tiếp `JS Object`).
  - $\rightarrow$ **JSON là "ngôn ngữ chung" quốc tế** giúp hai bên nói chuyện với nhau qua dây mạng.

### 2. JSON đi lại như thế nào khi người dùng bấm nút?

```
[ FRONTEND ]                                             [ BACKEND (Java) ]
     │                                                          │
(1) Người dùng bấm nút                                          │
     │                                                          │
(2) FE gom dữ liệu thành                                        │
    CHUỖI CHỮ JSON                                              │
     │                                                          │
(3) Bỏ chuỗi JSON vào "Ruột" (Body)                             │
    của gói tin HTTP Request ──────── GỬI QUA DÂY MẠNG ────────►│
                                                                │ (4) Spring Boot dùng
                                                                │     Jackson "thông dịch"
                                                                │     JSON -> Class Java DTO
                                                                │
                                                                │ (5) Service xử lý logic...
                                                                │
                                                                │ (6) Biến kết quả Java
                                                                │     thành CHUỖI JSON mới
                                                                │
(8) FE nhận chuỗi JSON ◄──────── GỬI QUA DÂY MẠNG ──────────────┘
    bóc ra hiển thị màn hình
```

### 3. Ví dụ thực tế: Nút "Đăng Nhập" (`POST /api/auth/login`)

1. **Trên màn hình web:** Bạn gõ `nam@gmail.com` và mật khẩu `123456`, rồi bấm **"Đăng Nhập"**.
2. **Frontend đóng hàng:** Trình duyệt tạo một đoạn văn bản JSON:
   ```json
   {
     "email": "nam@gmail.com",
     "password": "123456"
   }
   ```
   Sau đó nhét đoạn chữ này vào phần **Body** của gói tin HTTP POST gửi tới `http://localhost:8080/api/auth/login`.
3. **Backend nhận hàng qua `@RequestBody`:**
   Tại `AuthController.java`:
   ```java
   @PostMapping("/login")
   public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) { ... }
   ```
   - Chú thích **`@RequestBody`** ra lệnh cho thư viện **Jackson** (thông dịch viên tích hợp sẵn trong Spring Boot):
     *Hãy đọc chuỗi JSON từ Body mạng vào $\rightarrow$ Tự động tạo đối tượng `LoginRequest` $\rightarrow$ Tự gán `setEmail` và `setPassword`.*
   - Lập tức trong code Java, lập trình viên có sẵn đối tượng `request` để dùng `request.getEmail()`, không phải tự cắt chuỗi thủ công.
4. **Backend trả lời bằng JSON qua `ApiResponse`:**
   Khi đăng nhập thành công, code Java trả về:
   ```java
   return ResponseEntity.ok(ApiResponse.success("Đăng nhập thành công", authResponse));
   ```
   - Jackson lại tự động làm chiều ngược lại: Biến Object `ApiResponse` thành đoạn text JSON chuẩn gửi về cho Frontend:
   ```json
   {
     "status": 200,
     "message": "Đăng nhập thành công",
     "data": {
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "role": "STUDENT"
     }
   }
   ```
5. **Frontend mở hàng:** Trình duyệt đọc đoạn JSON, lấy `data.token` lưu vào bộ nhớ và chuyển hướng người dùng vào trang chủ.

---

## 🏢 PHẦN 3: TÁC DỤNG TỪNG THƯ MỤC & PHÂN LOẠI "BLACK BOX" VS "PHẢI CÀY"

Hệ thống có đúng **11 thư mục** trong mã nguồn Java + Resources:

| Thư mục | Tác dụng trong dòng chảy | Mức độ học | Lý do |
| :--- | :--- | :---: | :--- |
| **`resources/`** | Chứa file `application.yml` (chuỗi kết nối DB, mật khẩu, JWT secret, cổng chạy 8080). | 💤 **Black Box cả thư mục** | Chỉ là file text cấu hình tham số môi trường, không có logic để học. |
| **`util/`** | Hộp đồ nghề dùng chung: `ContractPdfGenerator` (vẽ PDF), `OtpUtil` (random mã 6 số), `ApiResponse` (format JSON). | 💤 **Black Box cả thư mục** | Là code tiện ích gọi thư viện bên thứ ba. Chỉ cần biết gọi nó ra cái gì. |
| **`dto/`** | Chứa `request/` (hứng data gửi lên) và `response/` (đóng gói data trả về). | 💤 **Black Box từng file** | 100% là khai báo biến, getter/setter. Chỉ cần liếc qua để biết API nhận trường nào, trả trường nào. |
| **`config/`** | Cấu hình bảo mật: `JwtFilter` (bóc token), `SecurityConfig` (chặn route theo role), CORS. | 💤 **Black Box từng file** | Code mẫu chuẩn mực của Spring Security 6. Dev nào cũng kế thừa template, không cần học thuộc từng dòng config. |
| **`exception/`** | Chứa các loại lỗi tự chế (`BadRequestException`, `BookingConflictException`...) và `GlobalExceptionHandler`. | 💤 **Black Box cả thư mục** | Chỉ cần hiểu: Thay vì để app văng lỗi đỏ ngầu (500), tầng này tóm lấy lỗi và trả ra JSON sạch đẹp thông báo cho FE. |
| **`controller/`** | Tiếp tân: Ánh xạ URL (`@PostMapping`, `@GetMapping`), hứng dữ liệu từ DTO và chuyển cho Service. | 👁️ **Đọc lướt** | Không có logic nghiệp vụ. Chỉ cần đọc lướt để biết API nào gọi sang hàm nào của Service. |
| **`entity/`** | Bản thiết kế bảng dữ liệu (User, Booking, Slot, Wallet, Course...) và Enums trạng thái. | 🔥 **BẮT BUỘC CÀY** | Nắm chắc quan hệ 1-1, 1-N, N-N và các trạng thái chuyển đổi (`SlotStatus`, `BookingStatus`). |
| **`repository/`** | Tầng truy vấn DB: Kế thừa `JpaRepository`, chứa các câu `@Query` phức tạp và khóa tranh chấp `@Lock`. | 🔥 **BẮT BUỘC CÀY** | Phải hiểu câu query kiểm tra trùng giờ (`findOverlapping`) và khóa bi quan (`findByIdWithLock`). |
| **`service/`** | **Bộ não trung tâm**: Chứa toàn bộ luật nghiệp vụ, tính tiền, trừ buổi học, kiểm tra điều kiện. | 🔥 **BẮT BUỘC CÀY SÂU** | 90% câu hỏi vấn đáp và lỗi logic nằm ở `service/impl/` (đặc biệt `Booking`, `Wallet`, `Attendance`). |
| **`policy/`** | Áp dụng **Strategy Pattern & Factory Pattern** để xử lý chính sách phạt/hoàn tiền khi hủy lịch theo Role. | 🔥 **BẮT BUỘC CÀY** | Điểm sáng kiến trúc phần mềm, thể hiện tư duy thiết kế SOLID. |
| **`handler/`** | Áp dụng **Strategy Pattern** cho việc tạo người dùng theo từng Role (`PtRegistrationHandler`, `StudentRegistrationHandler`). | 🔥 **BẮT BUỘC CÀY** | Tách riêng luồng tạo PT (kèm Profile) và Học viên, tuân thủ nguyên lý Open-Closed. |

---

## 🎬 PHẦN 4: HAI VÍ DỤ CỤ THỂ MINH HỌA DÒNG CHẢY DỮ LIỆU

### 📌 VÍ DỤ 1: Học viên bấm ĐẶT LỊCH TẬP (`POST /api/bookings`)

*Kịch bản:* Học viên tên Nam bấm nút "Xác nhận đặt lịch" cho khung giờ chiều thứ Năm (Slot ID: 15) của PT Tuấn.

1. **Frontend $\rightarrow$ Backend:** 
   - FE gửi HTTP POST đến URL `/api/bookings` kèm Header `Authorization: Bearer eyJhbGci...` và Body JSON:
     ```json
     { "slotId": 15, "bookingType": "PACKAGE", "enrollmentId": 3, "studentNote": "Tập ngực nhé anh" }
     ```
2. **`config/` đón đầu:** 
   - `JwtFilter.java` chặn request lại $\rightarrow$ giải mã token bằng secret key $\rightarrow$ xác định người gửi là `nam@gmail.com`, Role là `STUDENT`.
   - `SecurityConfig.java` kiểm tra thấy route `/api/bookings` cho phép role `STUDENT` $\rightarrow$ Mở cửa cho đi tiếp.
3. **`dto/request/` & `controller/` tiếp nhận:**
   - Spring Boot tự động bốc dữ liệu JSON nhét vào class `CreateBookingRequest.java`.
   - `BookingController.java` đón nhận DTO này và chuyển ngay vào:
     `bookingService.createBooking("nam@gmail.com", request)`.
4. **`service/` & `repository/` xử lý bộ não:**
   - `BookingServiceImpl.java` bắt đầu chạy trong một `@Transactional`:
     - **Bước 4.1:** Gọi `AvailabilitySlotRepository.java` hàm `findByIdWithLock(15)`. Database lập tức thực hiện `SELECT ... FOR UPDATE` để **khóa chặt dòng slot 15 lại** (chống người khác đặt đè).
     - **Bước 4.2:** Kiểm tra nếu slot đã bị ai đặt trước (`status != AVAILABLE`) $\rightarrow$ văng lỗi `BookingConflictException` (tại `exception/`).
     - **Bước 4.3:** Kiểm tra xem Nam có bị trùng giờ học nào khác không qua `bookingRepository.existsOverlappingBookingForStudent(...)`.
     - **Bước 4.4:** Do `bookingType = PACKAGE`, service tìm gói học `Enrollment.java` ID 3 của Nam $\rightarrow$ kiểm tra còn buổi không $\rightarrow$ trừ 1 buổi (`remainingSessions - 1`).
     - **Bước 4.5:** Đổi trạng thái slot `AvailabilitySlot.java` thành `BOOKED`.
     - **Bước 4.6:** Tạo đối tượng `Booking.java` mới lưu thông tin Nam, PT Tuấn, Slot 15, trạng thái `CONFIRMED`.
     - **Bước 4.7:** Gọi `bookingRepository.save(booking)` để lưu xuống Database.
5. **Database thực thi:**
   - DB chạy các lệnh SQL `UPDATE availability_slots`, `UPDATE enrollments`, `INSERT INTO bookings`.
6. **`dto/response/` & `util/` trả về kết quả:**
   - `BookingServiceImpl` chuyển đổi Entity `Booking` thành `BookingResponse.java` (loại bỏ các thông tin nhạy cảm).
   - `BookingController` bọc vào `ApiResponse.java` $\rightarrow$ Trả về cho Frontend mã HTTP 201 Created kèm JSON thành công.
7. **Frontend nhận dữ liệu:**
   - Ứng dụng hiển thị thông báo: *"Bạn đã đặt lịch tập thành công với PT Tuấn vào 18h thứ Năm!"*.

---

### 📌 VÍ DỤ 2: Điểm Danh Bằng Mã OTP Tại Phòng Tập (`POST /api/attendance/check-in`)

*Kịch bản:* Đến giờ tập, PT Tuấn tạo mã điểm danh và học viên Nam nhập mã trên điện thoại để xác nhận buổi tập.

1. **PT bấm bắt đầu (Tạo mã OTP):**
   - PT gọi API `POST /api/attendance/start/{bookingId}`.
   - `AttendanceServiceImpl.java` gọi `OtpUtil.java` sinh ngẫu nhiên mã 6 số (ví dụ: `729401`) có hạn trong 15 phút $\rightarrow$ Lưu vào bảng `Attendance.java` dưới DB. Màn hình PT hiện số `729401`.
2. **Học viên nhập mã (Gửi dữ liệu lên):**
   - Nam mở app, nhập `729401` $\rightarrow$ FE gửi `POST /api/attendance/check-in` kèm Body JSON:
     ```json
     { "otpCode": "729401" }
     ```
3. **`config/` kiểm tra:**
   - `JwtFilter` giải mã token, biết đây là Nam (`STUDENT`), hợp lệ cho đi tiếp.
4. **`dto/request/` & `controller/` chuyển dữ liệu:**
   - DTO `StudentCheckInRequest.java` hứng mã `otpCode`.
   - `AttendanceController.java` gọi `attendanceService.studentCheckIn("nam@gmail.com", request)`.
5. **`service/` & `exception/` kiểm tra logic:**
   - `AttendanceServiceImpl` tìm ca tập của Nam trong ngày hôm nay.
   - So sánh mã Nam nhập với mã trong bảng `Attendance`:
     - **Nếu nhập sai hoặc quá 15 phút:** Ném lỗi `BadRequestException("Mã OTP không hợp lệ hoặc đã hết hạn")`. Lập tức `GlobalExceptionHandler.java` tóm lấy và trả về HTTP 400 Bad Request cho FE hiển thị thông báo lỗi.
     - **Nếu khớp chính xác:** Cập nhật `Attendance` với thời gian `checkInTime = now()`, đổi trạng thái `Booking` sang `COMPLETED`.
6. **Trả về kết quả:**
   - Service đóng gói thành `AttendanceResponse.java` $\rightarrow$ FE Nam và PT Tuấn đều hiện dấu tick xanh: *"Điểm danh thành công! Ca tập đã hoàn tất"*.

---

## 🗺️ PHẦN 5: LỘ TRÌNH THỰC CHIẾN 4 NGÀY (TRACE CODE TỪNG BƯỚC)

```
  28/10 (Tối)    : LUỒNG 1 - TÀI KHOẢN & ĐĂNG KÝ ĐA VAI TRÒ (Strategy Pattern ở Handler)
  29/10 (Cả ngày): LUỒNG 2 - ĐẶT LỊCH & KHÓA BI QUAN (Pessimistic Lock & Concurrency)
  30/10 (Cả ngày): LUỒNG 3 - HỦY LỊCH (Design Pattern Policy) & LUỒNG TIỀN VÍ
  31/10 (Cả ngày): LUỒNG 4 - ĐIỂM DANH OTP & TẬP DƯỢT VẤN ĐÁP 360 ĐỘ
  01/11 (Sáng)   : BẢO VỆ / CHỐT DỰ ÁN
```

### 🟢 Ngày 1 (Tối nay 28/10): LUỒNG ĐĂNG KÝ & KHỞI TẠO TÀI KHOẢN
*Mục tiêu: Hiểu cách dữ liệu đi qua `controller` $\rightarrow$ `dto` $\rightarrow$ `service` $\rightarrow$ `handler` $\rightarrow$ `entity` $\rightarrow$ `repo`.*
1. **Thứ tự mở file (Click theo thứ tự):**
   - Mở `AuthController.java` $\rightarrow$ Xem hàm `register(...)`.
   - Mở `RegisterRequest.java` $\rightarrow$ Xem các trường thông tin.
   - Mở `AuthServiceImpl.java` $\rightarrow$ Xem cách gọi `registrationHandlers`.
   - Mở thư mục `handler/`: `StudentRegistrationHandler.java` và `PtRegistrationHandler.java`.
   - Mở các Entity: `User.java`, `PTProfile.java`, `Wallet.java`.
2. **Điểm kiến trúc cần thuộc nằm lòng:**
   - Áp dụng **Strategy Pattern** ở `handler/` để tách riêng luồng tạo PT và Student, tuân thủ nguyên lý **Open-Closed (SOLID)**.
   - Mã hóa mật khẩu một chiều bằng `BCryptPasswordEncoder`.

---

### 🔴 Ngày 2 (29/10): LUỒNG ĐẶT LỊCH & KHÓA TRANH CHẤP (TRỌNG TÂM NHẤT)
*Mục tiêu: Nắm bài toán kỹ thuật hóc búa nhất hệ thống (Ăn trọn điểm Concurrency).*
1. **Thứ tự mở file (Click theo thứ tự):**
   - Mở `BookingController.java` $\rightarrow$ Xem hàm `createBooking(...)`.
   - Mở `CreateBookingRequest.java`.
   - Mở `BookingServiceImpl.java` $\rightarrow$ **Đọc kỹ từng dòng trong hàm `createBooking`** (Dòng 55-120).
   - Mở `AvailabilitySlotRepository.java`: Xem `@Lock(LockModeType.PESSIMISTIC_WRITE)` và `findOverlapping`.
   - Mở `BookingRepository.java` $\rightarrow$ Xem `existsOverlappingBookingForStudent`.
2. **Điểm kiến trúc cần thuộc nằm lòng:**
   - **Pessimistic Lock:** Hiểu tại sao dùng `SELECT ... FOR UPDATE` khóa tại database để chống 2 học viên đặt đè slot cùng lúc.
   - **Rollback:** `@Transactional(rollbackFor = Exception.class)` đảm bảo toàn vẹn giao dịch.

---

### 🟡 Ngày 3 (30/10): LUỒNG HỦY LỊCH (DESIGN PATTERN) & LUỒNG TIỀN VÍ
*Mục tiêu: Nắm cơ chế hoàn tiền tự động và mẫu thiết kế Factory/Strategy.*
1. **Thứ tự mở file (Click theo thứ tự):**
   - Mở `BookingController.java` $\rightarrow$ Xem `cancelBooking(...)`.
   - Mở `BookingServiceImpl.java` $\rightarrow$ Xem `cancellationPolicyFactory.getPolicy(role)`.
   - Mở thư mục `policy/`: `CancellationPolicyFactory.java`, `StudentCancellationPolicy.java`, `PtCancellationPolicy.java`.
   - Mở `WalletServiceImpl.java` $\rightarrow$ Xem hàm `topup`, `deductBalance`, `refund`.
   - Mở Entity `Wallet.java` và `Payment.java`.
2. **Điểm kiến trúc cần thuộc nằm lòng:**
   - **Strategy & Factory Pattern:** Tách rời thuật toán tính phí phạt theo từng role, không lồng `if-else`.
   - **BigDecimal:** Đảm bảo tính toán tiền tệ không bị sai số dấu phẩy động IEEE 754.

---

### 🔵 Ngày 4 (31/10): LUỒNG ĐIỂM DANH OTP & TỔNG DUYỆT VẤN ĐÁP
*Mục tiêu: Hoàn tất luồng cuối cùng và luyện tập trả lời trơn tru.*
1. **Thứ tự mở file (Click theo thứ tự):**
   - Mở `AttendanceController.java`.
   - Mở `AttendanceServiceImpl.java`: Xem `startAttendance` (gọi `OtpUtil.java`) và `studentCheckIn`.
   - Mở `GlobalExceptionHandler.java`: Xem cách bắt lỗi trả về JSON chuẩn.
2. **Luyện tập bộ câu hỏi phản biện:**
   - Tự đứng trước gương trả lời to, rõ ràng 5 câu hỏi cốt lõi ở Phần 6.

---

### ⚪ Ngày 5 (01/11): NGÀY BẢO VỆ DỰ ÁN
- Giữ tinh thần thoải mái, tự tin.
- Luôn trả lời theo tư duy kiến trúc: **Controller hứng DTO $\rightarrow$ Service xử lý nghiệp vụ $\rightarrow$ Repository thực thi DB và khóa dữ liệu $\rightarrow$ Trả về Response DTO an toàn.**

---

## 💡 PHẦN 6: BỘ CÂU HỎI PHẢN BIỆN "SỐNG CÒN" (CHEATSHEET)

#### Câu 1: Hệ thống của bạn xử lý bài toán Race Condition (tranh chấp) khi đặt lịch như thế nào?
> **Trả lời:** Hệ thống áp dụng **Pessimistic Locking (Khóa bi quan)** tại tầng database thông qua Spring Data JPA `@Lock(LockModeType.PESSIMISTIC_WRITE)` trên phương thức `findByIdWithLock(slotId)`. Khi một giao dịch đang đọc để đặt lịch, câu lệnh SQL `SELECT ... FOR UPDATE` sẽ khóa record đó lại, ngăn các giao dịch khác sửa đổi cho đến khi transaction hoàn tất. Nếu slot đã đổi sang trạng thái `BOOKED`, request tiếp theo sẽ bị từ chối bằng `BookingConflictException`.

#### Câu 2: Tại sao bạn lại tách riêng các Policy hủy lịch trong package `policy` mà không viết thẳng vào Service?
> **Trả lời:** Em áp dụng kết hợp **Strategy Pattern** và **Factory Pattern** tuân theo nguyên lý **Open-Closed (SOLID)**. Mỗi đối tượng (Student, PT, Admin) có một thuật toán tính phí hoàn tiền và chế tài khác nhau. Việc tách thành các class riêng giúp code dễ bảo trì, dễ viết Unit Test độc lập và khi hệ thống mở rộng thêm đối tượng mới thì chỉ cần tạo class mới mà không làm thay đổi logic đang chạy ổn định của các bên khác.

#### Câu 3: Tại sao lại dùng `BigDecimal` cho số dư ví và giá tiền thay vì `double` hay `float`?
> **Trả lời:** Vì kiểu `double` và `float` lưu trữ số thực dưới dạng nhị phân theo chuẩn IEEE 754, dễ gây ra sai số làm tròn khi thực hiện các phép tính cộng trừ tiền tệ (ví dụ 0.1 + 0.2 = 0.30000000000000004). Đối với hệ thống tài chính/ví tiền, bắt buộc phải dùng `BigDecimal` để đảm bảo độ chính xác tuyệt đối từng đơn vị tiền tệ.

#### Câu 4: `@Transactional` trong hàm đặt lịch/mua gói học có ý nghĩa gì? Nếu xảy ra lỗi giữa chừng thì sao?
> **Trả lời:** `@Transactional(rollbackFor = Exception.class)` đảm bảo tính toàn vẹn **Atomicity** trong chuẩn ACID. Một thao tác mua gói gồm nhiều bước: trừ tiền ví, tạo bản ghi thanh toán, tạo hợp đồng và tạo enrollment. Nếu bất kỳ bước nào phía sau bị lỗi (ví dụ lỗi sinh file PDF hợp đồng hoặc lỗi mạng), Spring sẽ tự động Rollback (hoàn tác) toàn bộ giao dịch, hoàn lại tiền ví về trạng thái ban đầu, tránh tình trạng tiền bị trừ mà người dùng không nhận được dịch vụ.

#### Câu 5: Dữ liệu JSON từ Frontend được xử lý thế nào khi truyền xuống Backend?
> **Trả lời:** Frontend đóng gói dữ liệu vào chuỗi JSON nằm trong **HTTP Request Body**. Tại Backend, chú thích **`@RequestBody`** kích hoạt thư viện **Jackson** tự động giải mã (deserialization) chuỗi text JSON thành đối tượng Java DTO tương ứng. Ngược lại, khi Backend trả về đối tượng `ApiResponse`, Jackson sẽ tuần tự hóa (serialization) thành chuỗi JSON chuẩn để Frontend bóc tách hiển thị.

---

## 🎯 PHẦN 7: CÔNG THỨC TRẢ LỜI VẤN ĐÁP "BẤT BẠI" KHI CÔ HỎI VỀ FRONTEND (NÚT BẤM / LUỒNG GIAO DIỆN)

### ⚠️ CẢNH BÁO: TẠI SAO KHÔNG ĐƯỢC TRẢ LỜI CHUNG CHUNG "GỬI JSON RỒI V.V."?
Nếu cô chỉ vào một nút trên giao diện và hỏi: *"Khi bấm nút này thì chuyện gì xảy ra?"*, mà bạn chỉ trả lời: 
> ❌ *"Dạ nó gửi gói tin HTTP Request có thân là JSON xuống Backend xử lý v.v... rồi trả JSON về lại cho Frontend hiển thị ạ"*

👉 **Bạn sẽ bị cô giáo vặn tiếp ngay 3 câu hiểm hóc:**
1. *"Cô biết là HTTP rồi, nhưng cụ thể là Method gì? GET, POST hay PUT? Gửi vào URL nào?"*
2. *"Trong thân JSON đó cụ thể có những chữ gì (fields gì)? Mở code Frontend chỉ đúng dòng `axios`/`fetch` đó cho cô xem!"*
3. *"Bên Backend DTO nào, Controller nào hứng cái JSON đó? Map với sơ đồ tuần tự (Sequence Diagram) ở chỗ nào?"*

Nếu không trả lời được, cô sẽ kết luận ngay nhóm đi copy code hoặc không hiểu luồng hệ thống.

---

### 🏆 CÔNG THỨC 4 BƯỚC VÀNG (TRẢ LỜI TRƠN TRU - ĂN ĐIỂM TUYỆT ĐỐI)

Khi cô hỏi bất kỳ nút bấm nào trên màn hình, hãy trả lời đúng theo cấu trúc 4 bước sau:

1. **Bước 1 (FE & Endpoint):** Màn hình nào $\rightarrow$ Bấm nút gì $\rightarrow$ Gửi HTTP Method gì (GET/POST/PUT) tới URL (Endpoint) nào.
2. **Bước 2 (Payload JSON):** Thân (Body) JSON gửi đi gồm những trường dữ liệu cụ thể nào.
3. **Bước 3 (Chủ động lái về sở trường BE):** Spring Boot bóc JSON vào DTO nào $\rightarrow$ Đẩy sang Service nào xử lý logic (Transaction, Lock, DB).
4. **Bước 4 (Kết quả phản hồi):**
   - **Thành công:** BE trả mã HTTP (200/201) kèm JSON $\rightarrow$ FE hiển thị thông báo gì (Toast/Alert/Modal) và chuyển hướng đi đâu.
   - **Thất bại/Lỗi:** Nếu vi phạm điều kiện, BE văng Exception gì (mã 400) $\rightarrow$ FE hứng mã lỗi hiển thị dòng chữ đỏ thế nào.

---

### 📋 MẪU TRẢ LỜI THỰC CHIẾN CHO 4 CHỨC NĂNG CHÍNH CỦA PT-CONNECT

#### 📌 Luồng 1: Bấm nút "Xác Nhận Đặt Lịch Tập"
* **Bối cảnh:** Học viên chọn giờ tập của PT và bấm nút "Xác nhận".
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa cô, tại màn hình đặt lịch của Frontend:*
  > 1. *Khi học viên bấm nút **'Xác nhận đặt lịch'**, Frontend sẽ kích hoạt một gói tin **HTTP POST** gửi tới endpoint `/api/bookings`.*
  > 2. *Thân (Body) JSON gửi đi gồm 4 trường dữ liệu: `slotId` (ID khung giờ), `bookingType` (loại gói), `enrollmentId` (ID gói học) và `studentNote`.*
  > 3. *Xuống Backend, chú thích `@RequestBody` bóc chuỗi JSON này vào đối tượng `CreateBookingRequest`. `BookingController` chuyển ngay sang `BookingServiceImpl`.*
  >    *(Lái về sở trường BE)*: *Tại đây, BE chạy `@Transactional`, dùng câu lệnh `findByIdWithLock` để khóa slot bằng **Pessimistic Lock** tránh đặt đè, kiểm tra trùng giờ và trừ 1 buổi trong gói học.*
  > 4. *Xử lý xong, BE trả về mã **HTTP 201 Created** kèm `BookingResponse`. FE nhận được sẽ tắt modal, hiện thông báo Toast 'Đặt lịch thành công' và chuyển người dùng về trang lịch tập cá nhân."*

#### 📌 Luồng 2: Bấm nút "Xác Nhận Điểm Danh OTP"
* **Bối cảnh:** Học viên nhập 6 số OTP do PT đọc để xác nhận buổi tập.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa cô, tại màn hình điểm danh:*
  > 1. *Sau khi học viên gõ 6 số và bấm **'Xác nhận'**, FE kích hoạt **HTTP POST** gửi tới URL `/api/attendance/check-in`.*
  > 2. *Thân (Body) JSON chỉ gồm đúng 1 trường duy nhất: `{ "otpCode": "729401" }`.*
  > 3. *Backend bóc JSON vào `StudentCheckInRequest`, đẩy sang `AttendanceServiceImpl`. Service sẽ truy vấn mã OTP trong bảng `Attendance` và kiểm tra thời hạn 15 phút.*
  > 4. *Kết quả:*
  >    - *Nếu hợp lệ: BE cập nhật `checkInTime`, đổi trạng thái Booking sang `COMPLETED`, trả về **HTTP 200 OK**. FE đóng pop-up và hiện dấu tick xanh 'Điểm danh thành công'.*
  >    - *Nếu mã sai hoặc hết hạn: Service văng lỗi `BadRequestException`, `GlobalExceptionHandler` bắt lại trả về mã **HTTP 400**. FE bắt mã lỗi này và hiện dòng chữ đỏ cảnh báo 'Mã OTP không chính xác hoặc đã hết hạn'."*

#### 📌 Luồng 3: Bấm nút "Hủy Lịch Tập"
* **Bối cảnh:** Học viên hoặc PT bấm hủy ca tập đã đặt.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa cô, tại danh sách ca tập:*
  > 1. *Khi bấm nút **'Hủy lịch'**, FE gửi **HTTP POST** tới URL `/api/bookings/{bookingId}/cancel`.*
  > 2. *Thân JSON gửi đi có thể kèm trường `{ "reason": "Bận việc đột xuất" }`.*
  > 3. *Backend nhận qua `BookingController`, đẩy vào `BookingServiceImpl`.*
  >    *(Lái về Design Pattern)*: *Tại đây, Service gọi `CancellationPolicyFactory` lấy ra chính sách hủy tương ứng (`StudentCancellationPolicy` hoặc `PtCancellationPolicy`) để tính toán xem hủy trước mấy tiếng, có được hoàn tiền/buổi tập hay không.*
  > 4. *BE cập nhật DB, trả về **HTTP 200 OK**. FE cập nhật lại bảng danh sách ca tập sang trạng thái 'ĐÃ HỦY'."*

#### 📌 Luồng 4: Bấm nút "Đăng Nhập"
* **Bối cảnh:** Màn hình đăng nhập hệ thống.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa cô:*
  > 1. *Khi người dùng nhập xong thông tin và bấm **'Đăng nhập'**, FE gửi **HTTP POST** tới URL `/api/auth/login`.*
  > 2. *Body JSON gồm 2 trường: `{ "email": "...", "password": "..." }`.*
  > 3. *Backend đưa vào `LoginRequest`, `AuthServiceImpl` kiểm tra email trong DB và dùng `BCryptPasswordEncoder.matches()` để so khớp mật khẩu đã băm.*
  > 4. *Nếu đúng, BE sinh mã JWT Token và trả về **HTTP 200** chứa Token và Role. FE nhận chuỗi Token này lưu vào `localStorage`, đồng thời điều hướng sang trang Dashboard tương ứng với Role."*

---

### 📊 BẢNG "PHA CỨU SINH" TRA CỨU NHANH TRONG 3 GIÂY

| Chức năng | Nút bấm trên FE | HTTP Method & URL | Ruột JSON gửi đi (Request Body) | DTO Backend hứng | Mã HTTP trả về |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Đăng nhập** | "Đăng nhập" | `POST /api/auth/login` | `email`, `password` | `LoginRequest` | 200 OK |
| **Đặt lịch** | "Xác nhận đặt lịch" | `POST /api/bookings` | `slotId`, `bookingType`, `enrollmentId`, `studentNote` | `CreateBookingRequest` | 201 Created |
| **Điểm danh OTP** | "Xác nhận OTP" | `POST /api/attendance/check-in` | `otpCode` | `StudentCheckInRequest` | 200 OK |
| **Hủy lịch** | "Hủy ca tập" | `POST /api/bookings/{id}/cancel` | `reason` | `CancelBookingRequest` | 200 OK |

---
*File này đã được lưu trực tiếp tại `BACKEND_STUDY_GUIDE.md` trong thư mục dự án của bạn để tiện tra cứu mọi lúc.*
