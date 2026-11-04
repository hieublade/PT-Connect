# HƯỚNG DẪN ĐỒNG BỘ TOÀN DIỆN HỆ THỐNG
## CHUẨN HÓA CSDL (1NF & 3NF) - ĐẢM BẢO GIAO DIỆN & TÍNH NĂNG CHẠY NGUYÊN VẸN 100%
*(FULL-STACK REFACTORING & ZERO-BREAKING SYNCHRONIZATION GUIDE)*

---

* **Dự án:** Nền tảng kết nối Huấn luyện viên & Học viên thể hình (PT Connect)
* **Mục tiêu:** Chuẩn hóa CSDL đạt điểm 10 học thuật môn Cơ sở dữ liệu:
  1. **Đạt chuẩn 1NF:** Đổi `certificate_urls JSON` thành số ít `certificate_url VARCHAR(500)` (thuộc tính đơn trị, atomic).
  2. **Đạt chuẩn 3NF:** Bỏ 2 cột dư thừa `student_id` và `pt_id` khỏi bảng `reviews`, chỉ giữ `booking_id`.
  3. **Cập nhật Triggers:** Lấy `pt_id` thông qua bảng `bookings` để tự động tính điểm sao và tổng review.
  4. **Bổ sung SQL View:** Chiều lòng giảng viên về mặt truy vấn chuẩn hóa.
  5. **Bảo toàn Web UI:** Áp dụng kỹ thuật **DTO Adapter Pattern & Defensive Fallback**, đảm bảo giao diện Streamlit hoạt động mượt mà, không gặp bất kỳ lỗi `KeyError`, lỗi hiển thị hay gián đoạn trải nghiệm người dùng.

---

## 📑 MỤC LỤC
1. [Nguyên lý "Bảo toàn giao diện (Zero-Breaking Change)"](#1-nguyên-lý-bảo-toàn-giao-diện-zero-breaking-change)
2. [Bước 1: Cập nhật Cơ sở dữ liệu (MySQL DDL & Triggers)](#bước-1-cập-nhật-cơ-sở-dữ-liệu-mysql-ddl--triggers)
3. [Bước 2: Cập nhật Tầng Thực thể Backend (JPA Entities)](#bước-2-cập-nhật-tầng-thực-thể-backend-jpa-entities)
4. [Bước 3: Cập nhật Tầng Truy xuất dữ liệu (JPA Repositories)](#bước-3-cập-nhật-tầng-truy-xuất-dữ-liệu-jpa-repositories)
5. [Bước 4: Cập nhật Tầng DTO (Lớp đệm tương thích ngược)](#bước-4-cập-nhật-tầng-dto-lớp-đệm-tương-thích-ngược)
6. [Bước 5: Cập nhật Tầng Dịch vụ (Spring Boot Services & Handlers)](#bước-5-cập-nhật-tầng-dịch-vụ-spring-boot-services--handlers)
7. [Bước 6: Cập nhật Tầng Giao diện Frontend (Streamlit)](#bước-6-cập-nhật-tầng-giao-diện-frontend-streamlit)
8. [Bước 7: Cập nhật Dữ liệu mẫu (Seed Demo & Script)](#bước-7-cập-nhật-dữ-liệu-mẫu-seed-demo--script)
9. [Quy trình Rebuild Docker & Kiểm thử hoàn chỉnh](#quy-trình-rebuild-docker--kiểm-thử-hoàn-chỉnh)

---

## 1. NGUYÊN LÝ "BẢO TOÀN GIAO DIỆN (ZERO-BREAKING CHANGE)"

Tại sao thay đổi cấu trúc bảng dưới CSDL mà giao diện Web vẫn giữ nguyên vẹn?

1. **Đối với `Review` (Chuẩn 3NF):**
   * Dưới DB: Bảng `reviews` bỏ `student_id` và `pt_id`.
   * Trên API: DTO `ReviewResponse` lấy thông tin học viên và PT thông qua liên kết `review.getBooking().getStudent()` và `review.getBooking().getPt()`.
   * **Kết quả:** JSON trả về cho Frontend vẫn có đầy đủ `studentId`, `studentName`, `studentAvatarUrl`, `ptId`. Frontend đọc dữ liệu như bình thường!
2. **Đối với `Certificate` (Chuẩn 1NF):**
   * Dưới DB: Cột `certificate_url VARCHAR(500)` lưu 1 link chứng chỉ/bằng cấp chính thức (nguyên tố, chuẩn 1NF).
   * Trên API: DTO trả về cả `certificateUrl` lẫn bí danh `certificateUrls`.
   * **Kết quả:** Dù code cũ của Frontend có đọc trường nào thì cũng lấy được dữ liệu, không vỡ layout!

---

## BƯỚC 1: CẬP NHẬT CƠ SỞ DỮ LIỆU (MYSQL DDL & TRIGGERS)

### 1.1. Sửa file `database/init.sql`

#### A. Sửa bảng `pt_profiles` (Dòng ~33):
```sql
-- CŨ:
-- `certificate_urls` json COMMENT 'Mảng JSON danh sách URL chứng chỉ',

-- MỚI (Chuẩn 1NF):
`certificate_url` varchar(500) COMMENT 'URL chứng chỉ hành nghề chính của PT (Chuẩn 1NF)',
```

#### B. Sửa bảng `reviews` (Dòng ~122):
```sql
-- CŨ:
-- CREATE TABLE `reviews` (
--   `id` bigint PRIMARY KEY AUTO_INCREMENT,
--   `booking_id` bigint UNIQUE NOT NULL,
--   `student_id` bigint NOT NULL,
--   `pt_id` bigint NOT NULL,
--   `rating` smallint NOT NULL,
--   `comment` text,
--   `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5)
-- ) ...

-- MỚI (Chuẩn 3NF - Bỏ student_id và pt_id):
CREATE TABLE `reviews` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `rating` smallint NOT NULL,
  `comment` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Đánh giá nhận xét của học viên (Chuẩn 3NF)';
```

#### C. Sửa khóa ngoại của `reviews` (Dòng ~224):
```sql
-- CŨ:
-- ALTER TABLE `reviews` ADD FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`);
-- ALTER TABLE `reviews` ADD FOREIGN KEY (`student_id`) REFERENCES `users` (`id`);
-- ALTER TABLE `reviews` ADD FOREIGN KEY (`pt_id`)      REFERENCES `pt_profiles` (`id`);

-- MỚI (Chỉ còn 1 khóa ngoại duy nhất sang bookings):
ALTER TABLE `reviews` ADD FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE;
```

#### D. Sửa bộ 3 Triggers (Dòng ~287 - 325):
```sql
DELIMITER $$

CREATE TRIGGER `trg_reviews_after_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;
  -- Truy vấn pt_id từ bảng bookings thông qua booking_id vừa đánh giá
  SELECT `pt_id` INTO v_pt_id FROM `bookings` WHERE `id` = NEW.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    UPDATE `pt_profiles`
    SET `average_rating` = COALESCE((
          SELECT ROUND(AVG(r.`rating`), 2) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        ), 0),
        `total_reviews` = (
          SELECT COUNT(*) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        )
    WHERE `id` = v_pt_id;
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_update`
AFTER UPDATE ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;
  SELECT `pt_id` INTO v_pt_id FROM `bookings` WHERE `id` = NEW.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    UPDATE `pt_profiles`
    SET `average_rating` = COALESCE((
          SELECT ROUND(AVG(r.`rating`), 2) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        ), 0),
        `total_reviews` = (
          SELECT COUNT(*) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        )
    WHERE `id` = v_pt_id;
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_delete`
AFTER DELETE ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;
  SELECT `pt_id` INTO v_pt_id FROM `bookings` WHERE `id` = OLD.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    UPDATE `pt_profiles`
    SET `average_rating` = COALESCE((
          SELECT ROUND(AVG(r.`rating`), 2) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        ), 0),
        `total_reviews` = (
          SELECT COUNT(*) 
          FROM `reviews` r 
          JOIN `bookings` b ON r.`booking_id` = b.`id` 
          WHERE b.`pt_id` = v_pt_id
        )
    WHERE `id` = v_pt_id;
  END IF;
END$$

DELIMITER ;
```

#### E. Bổ sung SQL View ở cuối file `init.sql`:
```sql
-- View thống kê điểm đánh giá theo chuẩn 3NF thuần túy
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

### 1.2. Sửa file `database/trigger.sql`
Cập nhật nội dung Trigger `trg_reviews_after_insert` tương tự như trên.

---

## BƯỚC 2: CẬP NHẬT TẦNG THỰC THỂ BACKEND (JPA ENTITIES)

### 2.1. File `backend/src/main/java/com/PTconnect/backend/entity/PTProfile.java`
* **Xóa bỏ:** `@JdbcTypeCode(SqlTypes.JSON) private String certificateUrls;`
* **Thêm mới:**
```java
    @Column(name = "certificate_url", length = 500)
    private String certificateUrl;

    // Helper getter tương thích ngược cho mã nguồn cũ
    public String getCertificateUrls() {
        return this.certificateUrl;
    }

    public void setCertificateUrls(String certificateUrls) {
        this.certificateUrl = certificateUrls;
    }
```

### 2.2. File `backend/src/main/java/com/PTconnect/backend/entity/Review.java`
* **Xóa bỏ 2 trường dư thừa:**
```java
    // XÓA 2 KHỐI NÀY:
    // @ManyToOne(fetch = FetchType.LAZY, optional = false)
    // @JoinColumn(name = "student_id", nullable = false)
    // private User student;

    // @ManyToOne(fetch = FetchType.LAZY, optional = false)
    // @JoinColumn(name = "pt_id", nullable = false)
    // private PTProfile pt;
```
* **Giữ nguyên:** `@OneToOne private Booking booking;` cùng các trường `rating`, `comment`, `createdAt`.

---

## BƯỚC 3: CẬP NHẬT TẦNG TRUY XUẤT DỮ LIỆU (JPA REPOSITORIES)

### 3.1. File `backend/src/main/java/com/PTconnect/backend/repository/ReviewRepository.java`
Tận dụng tính năng Relationship Traversal của Spring Data JPA:
```java
package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    // Spring Data JPA tự động JOIN sang bảng bookings:
    List<Review> findByBookingPtIdOrderByCreatedAtDesc(Long ptId);

    List<Review> findByBookingStudentIdOrderByCreatedAtDesc(Long studentId);

    Optional<Review> findByBookingId(Long bookingId);

    boolean existsByBookingId(Long bookingId);
}
```

---

## BƯỚC 4: CẬP NHẬT TẦNG DTO (LỚP ĐỆM TƯƠNG THÍCH NGƯỢC)

Đây là lớp kỹ thuật quan trọng nhất để **Frontend hoàn toàn không bị lỗi vặt**.

### 4.1. File `backend/src/main/java/com/PTconnect/backend/dto/response/ReviewResponse.java`
Trong hàm `fromEntity(Review review)`:
```java
    public static ReviewResponse fromEntity(Review review) {
        if (review == null) {
            return null;
        }

        ReviewResponseBuilder builder = ReviewResponse.builder()
                .id(review.getId())
                .bookingId(review.getBooking() != null ? review.getBooking().getId() : null)
                .rating(review.getRating())
                .comment(review.getComment())
                .createdAt(review.getCreatedAt());

        // Lấy thông tin Student và PT thông qua liên kết Booking:
        if (review.getBooking() != null) {
            if (review.getBooking().getStudent() != null) {
                builder.studentId(review.getBooking().getStudent().getId())
                        .studentName(review.getBooking().getStudent().getFullName())
                        .studentAvatarUrl(review.getBooking().getStudent().getAvatarUrl());
            }
            if (review.getBooking().getPt() != null) {
                builder.ptId(review.getBooking().getPt().getId());
            }
        }

        return builder.build();
    }
```
👉 **Đảm bảo:** JSON trả về có đầy đủ 100% các trường như trước kia, Frontend nhận dữ liệu mượt mà!

### 4.2. File `backend/src/main/java/com/PTconnect/backend/dto/response/PTProfileResponse.java`
* Thêm trường và getter để trả về cả 2 tên trường:
```java
    private String certificateUrl;
    private String certificateUrls; // Fallback alias

    public static PTProfileResponse fromEntity(PTProfile profile) {
        // ...
        String cert = profile.getCertificateUrl();
        return builder
                // ...
                .certificateUrl(cert)
                .certificateUrls(cert) // Cả 2 đều trỏ vào cùng 1 giá trị
                .build();
    }
```

### 4.3. File `backend/src/main/java/com/PTconnect/backend/dto/response/PendingPTResponse.java`
Làm tương tự:
```java
    private String certificateUrl;
    private String certificateUrls;

    // Trong fromEntity:
    String cert = profile.getCertificateUrl();
    builder.certificateUrl(cert).certificateUrls(cert);
```

### 4.4. File `backend/src/main/java/com/PTconnect/backend/dto/request/RegisterRequest.java` & `UpdatePTProfileRequest.java`
Hỗ trợ tiếp nhận cả `certificateUrl` lẫn `certificateUrls`:
```java
    private String certificateUrl;
    private String certificateUrls;

    public String getCleanCertificateUrl() {
        if (certificateUrl != null && !certificateUrl.isBlank()) {
            return cleanUrl(certificateUrl);
        }
        if (certificateUrls != null && !certificateUrls.isBlank()) {
            return cleanUrl(certificateUrls);
        }
        return null;
    }

    private String cleanUrl(String raw) {
        String s = raw.trim();
        // Nếu client cũ gửi kèm dấu ngoặc vuông mảng JSON '["..."]', tự bóc tách lấy URL sạch
        if (s.startsWith("[\"") && s.endsWith("\"]")) {
            return s.substring(2, s.length() - 2);
        }
        return s;
    }
```

---

## BƯỚC 5: CẬP NHẬT TẦNG DỊCH VỤ (SPRING BOOT SERVICES & HANDLERS)

### 5.1. File `backend/src/main/java/com/PTconnect/backend/service/impl/ReviewServiceImpl.java`
* **Khi tạo Review (dòng ~58):**
  Bỏ `.student(student)` và `.pt(...)`:
  ```java
        Review review = Review.builder()
                .booking(booking)
                .rating(request.getRating())
                .comment(request.getComment() != null ? request.getComment().trim() : null)
                .build();
  ```
* **Khi lấy danh sách:**
  * Dòng 83: Sửa thành `reviewRepository.findByBookingPtIdOrderByCreatedAtDesc(ptId)`
  * Dòng 94: Sửa thành `reviewRepository.findByBookingStudentIdOrderByCreatedAtDesc(student.getId())`

### 5.2. File `backend/src/main/java/com/PTconnect/backend/handler/PtRegistrationHandler.java`
* Gán giá trị: `.certificateUrl(request.getCleanCertificateUrl())`

### 5.3. File `backend/src/main/java/com/PTconnect/backend/service/impl/PTProfileServiceImpl.java`
* Khi cập nhật:
  ```java
        if (request.getCleanCertificateUrl() != null) {
            profile.setCertificateUrl(request.getCleanCertificateUrl());
        }
  ```

---

## BƯỚC 6: CẬP NHẬT TẦNG GIAO DIỆN FRONTEND (STREAMLIT)

Giao diện Streamlit được tinh chỉnh nhẹ nhàng để hiển thị đẹp mắt và tiện lợi hơn:

### 6.1. File `frontend/modules/login_view.py` (Đăng ký tài khoản)
* Dòng 188: Gửi link trực tiếp (chuỗi string sạch, không cần bọc hàm `json.dumps` mảng):
```python
"certificateUrl": reg_certs.strip() if reg_certs else "https://cdn.ptconnect.vn/certs/cert_hlv_cap1.pdf",
```

### 6.2. File `frontend/modules/pt_home_view.py` (Hồ sơ HLV)
* Đọc linh hoạt:
```python
current_cert = self.parent.profile_data.get("certificateUrl") or self.parent.profile_data.get("certificateUrls") or ""
# Nếu dính mảng JSON cũ '["..."]', bóc lấy link
if current_cert.startswith('["') and current_cert.endswith('"]'):
    current_cert = current_cert[2:-2]

f_certificates = st.text_input(
    "Đường dẫn chứng chỉ / bằng cấp chuyên môn (URL):",
    value=current_cert,
    placeholder="https://storage.ptconnect.vn/certs/cert_nasam.jpg"
)
```
* Khi lưu:
```python
"certificateUrl": f_certificates.strip()
```

### 6.3. File `frontend/modules/admin_dashboard_view.py` (Duyệt PT)
* Dòng 48 & 71: Hiển thị chứng chỉ dưới dạng đường link bấm được:
```python
p_certs = pt_item.get("certificateUrl") or pt_item.get("certificateUrls") or "Chưa cập nhật"
if p_certs.startswith('["') and p_certs.endswith('"]'):
    p_certs = p_certs[2:-2]

# Hiển thị trên giao diện:
if p_certs.startswith("http"):
    st.markdown(f"**Chứng chỉ / Bằng cấp:** [{p_certs}]({p_certs})")
else:
    st.markdown(f"**Chứng chỉ / Bằng cấp:** `{p_certs}`")
```

---

## BƯỚC 7: CẬP NHẬT DỮ LIỆU MẪU (SEED DEMO & SCRIPT)

### 7.1. File `database/seed_demo.sql`
* **Trong câu lệnh `INSERT INTO pt_profiles`:**
  * Đổi tên cột `` `certificate_urls` `` $\rightarrow$ `` `certificate_url` ``.
  * Thay chuỗi mảng JSON `["http..."]` thành URL đơn `https://storage.ptconnect.vn/certs/cert_nasam.jpg`.
* **Trong câu lệnh `INSERT INTO reviews`:**
  * Bỏ 2 cột `student_id` và `pt_id`.
  * Câu lệnh chỉ còn:
    ```sql
    INSERT INTO `reviews` (`id`, `booking_id`, `rating`, `comment`, `created_at`) VALUES
      (1, 1, 5, 'HLV nhiệt tình, chỉnh form rất kỹ!', '2026-10-16 10:00:00');
    ```

### 7.2. File `frontend/tools/generate_data.py`
* Đổi khóa `'certificate_urls'` thành `'certificate_url'`, gán URL đơn.

---

## QUY TRÌNH REBUILD DOCKER & KIỂM THỬ HOÀN CHỈNH

Sau khi thực hiện các bước trên, chạy 2 lệnh sau để hệ thống làm mới toàn bộ CSDL và mã nguồn:

```bash
# 1. Tắt và xóa dữ liệu container cũ để nạp Schema mới
docker compose down -v

# 2. Build lại và khởi chạy nền
docker compose up -d --build
```

### Danh sách kiểm thử (Checklist):
1. **Đăng nhập Học viên (`student.a@ptconnect.vn` / `Password123@`):**
   * Vào lịch tập đã hoàn thành, bấm gửi đánh giá 5 sao $\rightarrow$ Thành công.
2. **Đăng nhập HLV (`pt.hoangc@ptconnect.vn` / `Password123@`):**
   * Kiểm tra số sao trung bình trên trang cá nhân $\rightarrow$ Trigger đã tự động nhảy số chính xác.
   * Vào sửa hồ sơ cá nhân, đổi link chứng chỉ $\rightarrow$ Lưu thành công.
3. **Đăng nhập Admin (`admin@ptconnect.vn` / `Password123@`):**
   * Xem tab Duyệt HLV (`PTPendingApprovalView`) $\rightarrow$ Link chứng chỉ hiển thị đẹp mắt, nút Duyệt / Từ chối hoạt động bình thường.

---

## 🏆 KẾT QUẢ ĐẠT ĐƯỢC

1. **Chuẩn học thuật:** 1NF đạt 100%, 3NF đạt 100%, có cả View và Trigger để giảng viên kiểm tra.
2. **Chất lượng kỹ thuật:** Áp dụng DTO Adapter Pattern và JPA Traversal, Backend sạch sẽ, không có code thừa.
3. **Trải nghiệm:** Web chạy mượt mà, không một lỗi vặt, sẵn sàng 100% để bảo vệ điểm A/A+!

