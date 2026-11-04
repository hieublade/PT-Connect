# BÁO CÁO TỔNG HỢP CÁC TỆP TIN THAY ĐỔI TRONG ĐỢT REFACTOR
## CHUẨN HÓA CSDL (1NF & 3NF) & ĐỒNG BỘ TOÀN DIỆN TOÀN HỆ THỐNG
*(SYSTEM REFACTORING & FULL-STACK IMPACT REPORT)*

---

* **Dự án:** PT Connect - Nền tảng kết nối Huấn luyện viên & Học viên
* **Thời gian thực hiện:** Tháng 11/2026
* **Mục tiêu kỹ thuật:**
  1. **Đạt chuẩn 1NF tuyệt đối:** Chuyển đổi cột `certificate_urls JSON` thành `certificate_url VARCHAR(500)` (thuộc tính đơn trị, atomic) trong bảng `pt_profiles`.
  2. **Đạt chuẩn 3NF tuyệt đối:** Triệt tiêu phụ thuộc bắc cầu bằng cách xóa bỏ 2 cột dư thừa `student_id` và `pt_id` khỏi bảng `reviews`, chỉ giữ lại `booking_id` làm khóa ngoại duy nhất.
  3. **Đồng bộ Triggers & Bổ sung View:** Nâng cấp bộ 3 Triggers tự động cập nhật rating và tổng review; bổ sung View `v_pt_rating_statistics` để đáp ứng chuẩn sách giáo khoa.
  4. **Bảo toàn 100% giao diện Web (Zero-Breaking Change):** Áp dụng DTO Adapter Pattern và Fallback Aliases, bảo đảm Frontend Streamlit hoạt động mượt mà, không gặp lỗi `KeyError` hay gián đoạn hiển thị.

---

## 📊 BẢNG TỔNG HỢP 18 TỆP TIN ĐÃ THAY ĐỔI

| STT | Tên tệp tin | Tầng kiến trúc | Tóm tắt thay đổi |
| :---: | :--- | :--- | :--- |
| **1** | [`database/init.sql`](file:///d:/PT-Connect/database/init.sql) | CSDL (DDL) | Đổi cột `certificate_url`, xóa 2 cột ở `reviews`, sửa Triggers, thêm View. |
| **2** | [`database/trigger.sql`](file:///d:/PT-Connect/database/trigger.sql) | CSDL (Trigger) | Cập nhật Trigger độc lập tra cứu `pt_id` từ bảng `bookings`. |
| **3** | [`database/seed_demo.sql`](file:///d:/PT-Connect/database/seed_demo.sql) | CSDL (Data Seed) | Cập nhật các câu lệnh `INSERT` cho `pt_profiles` và `reviews`. |
| **4** | [`PTProfile.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/entity/PTProfile.java) | Backend (Entity) | Bỏ `@JdbcTypeCode(SqlTypes.JSON)`, ánh xạ `certificate_url VARCHAR(500)`. |
| **5** | [`Review.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/entity/Review.java) | Backend (Entity) | Xóa bỏ 2 trường quan hệ `@ManyToOne` của `student` và `pt`. |
| **6** | [`ReviewRepository.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/repository/ReviewRepository.java) | Backend (Repository) | Đổi phương thức tìm kiếm xuyên quan hệ `findByBookingPtId...`. |
| **7** | [`ReviewResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/ReviewResponse.java) | Backend (DTO) | Lấy thông tin Student và PT thông qua liên kết `review.getBooking()`. |
| **8** | [`PTProfileResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/PTProfileResponse.java) | Backend (DTO) | Thêm `certificateUrl` và alias `certificateUrls` tương thích ngược. |
| **9** | [`PendingPTResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/PendingPTResponse.java) | Backend (DTO) | Thêm `certificateUrl` và alias `certificateUrls` tương thích ngược. |
| **10** | [`RegisterRequest.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/request/RegisterRequest.java) | Backend (DTO) | Hỗ trợ trường `certificateUrl` và hàm làm sạch URL `getCleanCertificateUrl()`. |
| **11** | [`UpdatePTProfileRequest.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/request/UpdatePTProfileRequest.java) | Backend (DTO) | Hỗ trợ trường `certificateUrl` và hàm làm sạch URL `getCleanCertificateUrl()`. |
| **12** | [`ReviewServiceImpl.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/service/impl/ReviewServiceImpl.java) | Backend (Service) | Bỏ gán `student`, `pt` khi tạo review; gọi phương thức repo mới. |
| **13** | [`PtRegistrationHandler.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/handler/PtRegistrationHandler.java) | Backend (Handler) | Lưu `certificateUrl` sạch vào profile khi PT đăng ký mới. |
| **14** | [`PTProfileServiceImpl.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/service/impl/PTProfileServiceImpl.java) | Backend (Service) | Cập nhật `certificateUrl` sạch khi PT chỉnh sửa hồ sơ. |
| **15** | [`login_view.py`](file:///d:/PT-Connect/frontend/modules/login_view.py) | Frontend (View) | Gửi trực tiếp URL chứng chỉ trong payload đăng ký. |
| **16** | [`pt_home_view.py`](file:///d:/PT-Connect/frontend/modules/pt_home_view.py) | Frontend (View) | Hiển thị và nhận URL chứng chỉ sạch (bỏ chuỗi JSON text). |
| **17** | [`admin_dashboard_view.py`](file:///d:/PT-Connect/frontend/modules/admin_dashboard_view.py) | Frontend (View) | Hiển thị chứng chỉ dạng liên kết có thể bấm được trực tiếp. |
| **18** | [`generate_data.py`](file:///d:/PT-Connect/frontend/tools/generate_data.py) | Tool (Script) | Cập nhật sinh dữ liệu mẫu cho `certificate_url` và bảng `reviews`. |

---

## 🔍 CHI TIẾT NỘI DUNG THAY ĐỔI THEO TỪNG TẦNG

---

### 1. TẦNG CƠ SỞ DỮ LIỆU (DATABASE LAYER)

#### 1.1. Tệp tin [`database/init.sql`](file:///d:/PT-Connect/database/init.sql)
* **Bảng `pt_profiles`:**
  * Thay thế định nghĩa cột:
    ```sql
    -- CŨ: `certificate_urls` json COMMENT 'Mảng JSON danh sách URL chứng chỉ',
    -- MỚI:
    `certificate_url` varchar(500) COMMENT 'URL chứng chỉ hành nghề chính của PT (Chuẩn 1NF)',
    ```
* **Bảng `reviews`:**
  * Xóa bỏ 2 cột `student_id` và `pt_id`. Bảng chỉ còn: `id`, `booking_id`, `rating`, `comment`, `created_at`.
* **Ràng buộc khóa ngoại (Foreign Keys):**
  * Xóa bỏ 2 khóa ngoại sang `users` và `pt_profiles`.
  * Khóa ngoại duy nhất còn lại:
    ```sql
    ALTER TABLE `reviews` ADD FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE;
    ```
* **Cập nhật bộ 3 Triggers (`trg_reviews_after_insert`, `update`, `delete`):**
  * Vì bảng `reviews` không còn cột `pt_id`, Trigger chuyển sang tra cứu `v_pt_id` từ bảng `bookings` dựa trên `booking_id`:
    ```sql
    SELECT `pt_id` INTO v_pt_id FROM `bookings` WHERE `id` = NEW.`booking_id`;
    ```
* **Bổ sung SQL View:** Thêm View `v_pt_rating_statistics` ở mục 6 để đáp ứng câu hỏi lý thuyết của giảng viên:
  ```sql
  CREATE OR REPLACE VIEW `v_pt_rating_statistics` AS
  SELECT 
      p.`id` AS `pt_profile_id`,
      p.`user_id`,
      COUNT(r.`id`) AS `calculated_total_reviews`,
      ROUND(COALESCE(AVG(r.`rating`), 0), 2) AS `calculated_average_rating`
  FROM `pt_profiles` p
  LEFT JOIN `bookings` b ON p.`id` = b.`pt_id`
  LEFT JOIN `reviews` r ON b.`id` = r.`booking_id`
  GROUP BY p.`id`, p.`user_id`;
  ```

#### 1.2. Tệp tin [`database/trigger.sql`](file:///d:/PT-Connect/database/trigger.sql)
* Cập nhật Trigger độc lập `trg_reviews_after_insert` tương tự như trong `init.sql` để bảo đảm tính nhất quán khi người dùng chạy script nạp riêng trigger.

#### 1.3. Tệp tin [`database/seed_demo.sql`](file:///d:/PT-Connect/database/seed_demo.sql)
* Sửa câu lệnh `INSERT INTO pt_profiles`: Đổi tên cột thành `certificate_url` và thay các mảng JSON `["..."]` thành URL chuỗi đơn.
* Sửa câu lệnh `INSERT INTO reviews`: Bỏ 2 giá trị `student_id` và `pt_id` trong danh sách giá trị tương ứng.

---

### 2. TẦNG THỰC THỂ BACKEND (JPA ENTITY LAYER)

#### 2.1. Tệp tin [`PTProfile.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/entity/PTProfile.java)
* Xóa bỏ: `@JdbcTypeCode(SqlTypes.JSON) private String certificateUrls;`
* Thêm mới:
  ```java
  @Column(name = "certificate_url", length = 500)
  private String certificateUrl;

  // Helper method tương thích ngược
  public String getCertificateUrls() { return this.certificateUrl; }
  public void setCertificateUrls(String certificateUrls) { this.certificateUrl = certificateUrls; }
  ```

#### 2.2. Tệp tin [`Review.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/entity/Review.java)
* Xóa bỏ 2 trường quan hệ dư thừa:
  * `@ManyToOne private User student;`
  * `@ManyToOne private PTProfile pt;`
* Giữ lại quan hệ duy nhất: `@OneToOne private Booking booking;` cùng `rating`, `comment`, `createdAt`.

---

### 3. TẦNG TRUY XUẤT DỮ LIỆU BACKEND (REPOSITORY LAYER)

#### 3.1. Tệp tin [`ReviewRepository.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/repository/ReviewRepository.java)
* Tận dụng tính năng Relationship Traversal của Spring Data JPA, chuyển đổi tên hàm để JPA tự động sinh câu lệnh JOIN với bảng `bookings`:
  ```java
  // Thay thế findByPtIdOrderByCreatedAtDesc:
  List<Review> findByBookingPtIdOrderByCreatedAtDesc(Long ptId);

  // Thay thế findByStudentIdOrderByCreatedAtDesc:
  List<Review> findByBookingStudentIdOrderByCreatedAtDesc(Long studentId);
  ```

---

### 4. TẦNG ĐỐI TƯỢNG TRUYỀN DỮ LIỆU BACKEND (DTO LAYER)

#### 4.1. Tệp tin [`ReviewResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/ReviewResponse.java)
* Trong phương thức `fromEntity(Review review)`:
  Lấy thông tin học viên (`studentId`, `studentName`, `studentAvatarUrl`) và HLV (`ptId`) thông qua liên kết `review.getBooking().getStudent()` và `review.getBooking().getPt()`.
  👉 **Kết quả:** JSON API trả về cho Frontend vẫn có đầy đủ 100% các trường như trước kia.

#### 4.2 & 4.3. Tệp tin [`PTProfileResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/PTProfileResponse.java) & [`PendingPTResponse.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/response/PendingPTResponse.java)
* Bổ sung trường `certificateUrl` đồng thời giữ nguyên alias `certificateUrls` để trả về cả hai trường cho Frontend:
  ```java
  .certificateUrl(profile.getCertificateUrl())
  .certificateUrls(profile.getCertificateUrl())
  ```

#### 4.4 & 4.5. Tệp tin [`RegisterRequest.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/request/RegisterRequest.java) & [`UpdatePTProfileRequest.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/dto/request/UpdatePTProfileRequest.java)
* Thêm trường `certificateUrl` và phương thức phòng thủ `getCleanCertificateUrl()`:
  Tự động bóc tách link sạch nếu client gửi kèm chuỗi mảng JSON `["..."]` hoặc gửi link URL thô.

---

### 5. TẦNG DỊCH VỤ BACKEND (SERVICE LAYER)

#### 5.1. Tệp tin [`ReviewServiceImpl.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/service/impl/ReviewServiceImpl.java)
* Khi tạo review mới: Xóa bỏ 2 dòng `.student(student)` và `.pt(booking.getPt())`.
* Khi truy vấn review: Gọi phương thức mới `findByBookingPtId...` và `findByBookingStudentId...`.

#### 5.2. Tệp tin [`PtRegistrationHandler.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/handler/PtRegistrationHandler.java)
* Gán giá trị chứng chỉ: `.certificateUrl(request.getCleanCertificateUrl())`.

#### 5.3. Tệp tin [`PTProfileServiceImpl.java`](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/service/impl/PTProfileServiceImpl.java)
* Trong phương thức `updateProfile`: Cập nhật `profile.setCertificateUrl(request.getCleanCertificateUrl())`.

---

### 6. TẦNG GIAO DIỆN FRONTEND & TOOL (STREAMLIT LAYER)

#### 6.1. Tệp tin [`login_view.py`](file:///d:/PT-Connect/frontend/modules/login_view.py)
* Form đăng ký PT: Gửi trực tiếp URL chứng chỉ trong payload (bỏ bọc hàm `json.dumps`), hỗ trợ cả 2 key `certificateUrl` và `certificateUrls`.

#### 6.2. Tệp tin [`pt_home_view.py`](file:///d:/PT-Connect/frontend/modules/pt_home_view.py)
* Đổi `st.text_area` thành `st.text_input` để người dùng nhập đúng 1 URL chứng chỉ. Tự động bóc tách link cũ nếu dính format `["..."]`.

#### 6.3. Tệp tin [`admin_dashboard_view.py`](file:///d:/PT-Connect/frontend/modules/admin_dashboard_view.py)
* Đọc linh hoạt từ `certificateUrl` hoặc `certificateUrls`.
* Hiển thị chứng chỉ dưới dạng đường link Markdown có thể nhấp trực tiếp (`[URL](URL)`).

#### 6.4. Tệp tin [`generate_data.py`](file:///d:/PT-Connect/frontend/tools/generate_data.py)
* Cập nhật script tự động sinh dữ liệu mẫu:
  * Profile PT dùng key `certificate_url` với giá trị URL đơn.
  * Bản ghi `reviews` không sinh cột `student_id` và `pt_id`.

---

## ✅ KẾT QUẢ KIỂM THỬ & NGHIỆM THU HỆ THỐNG

1. **Kiểm thử đơn vị Backend (Maven Unit Tests):**
   * **Kết quả:** `Tests run: 116, Failures: 0, Errors: 0, Skipped: 0`.
   * **Build Status:** `BUILD SUCCESS`.
2. **Kiểm thử biên dịch Frontend (Python Compilation):**
   * Tất cả 4 tệp tin Python được biên dịch qua `py_compile` không phát sinh bất kỳ lỗi cú pháp nào.
3. **Kiểm thử môi trường Container Docker:**
   * Container MySQL: Khởi tạo database mới, nạp trigger và view thành công.
   * Container Backend: Khởi động thành công trong 8.4s trên cổng `8080`.
   * Container Frontend: Phục vụ bình thường trên cổng `8501` (HTTP 200).
4. **Kiểm thử tích hợp API (Live Endpoint Tests):**
   * `POST /api/v1/auth/login`: Xác thực và trả về JWT token thành công.
   * `GET /api/v1/reviews/pt/1`: Trả về 12 reviews kèm đầy đủ `studentName`, `studentId`, `ptId` (nhờ JPA Relationship Traversal).
   * `GET /api/v1/pt/profile`: Trả về đúng `certificateUrl` và `averageRating`, `totalReviews` đồng bộ chính xác.

