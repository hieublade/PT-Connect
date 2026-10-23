# Bằng Chứng Xác Nhận Cơ Sở Dữ Liệu & Nghiệp Vụ - Milestone 7

**Dự án:** PT-Connect  
**Giai đoạn:** Giai đoạn 3 (Điểm danh, Đánh giá, Quản trị và Hoàn thiện)  
**Tác giả phụ trách:** Thành, Huy, Hưng, Thắng, Hiệu  
**Phạm vi:** Kiểm tra thực tế trên hệ quản trị cơ sở dữ liệu MySQL và kiểm thử đơn vị JUnit cho các nghiệp vụ Milestone 7:
1. Trigger MySQL `AFTER INSERT ON reviews` tự động cập nhật `average_rating` và `total_reviews` trên `pt_profiles`.
2. Quy trình điểm danh xác thực hai phía bằng mã OTP 6 số đưa ca tập sang `COMPLETED`.
3. Cơ chế đánh dấu vắng mặt (`ABSENT`).
4. Hiện thực tính Đa hình (Polymorphism) cho Chính sách hủy lịch (`CancellationPolicy`) mục 3.11: Hoàn buổi, Đền bù ví và Phạt tiền.

---

## 1. Xác Nhận Trigger MySQL Tự Động Tính Điểm Đánh Giá (Output 2 & 3)

### 1.1. Mục tiêu
Chứng minh sau khi gọi API `POST /api/v1/reviews` để gửi đánh giá nhận xét:
1. Bản ghi được chèn thành công vào bảng `reviews`.
2. Trigger `trg_reviews_after_insert` tự động kích hoạt, tính toán `ROUND(AVG(rating), 2)` và `COUNT(*)` của toàn bộ review thuộc về `pt_id` đó.
3. Cập nhật trực tiếp vào hai cột `average_rating` và `total_reviews` của bảng `pt_profiles`.
4. **Mã nguồn Java Backend hoàn toàn không can thiệp** cập nhật hai trường này (đúng đặc tả môn học CSDL).

### 1.2. Script Trigger đã triển khai (`database/trigger.sql`)
```sql
USE ptconnect;

DROP TRIGGER IF EXISTS `trg_reviews_after_insert`;

DELIMITER $$

CREATE TRIGGER `trg_reviews_after_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
  UPDATE `pt_profiles`
  SET 
    `average_rating` = (
      SELECT ROUND(COALESCE(AVG(rating), 0), 2)
      FROM `reviews`
      WHERE `pt_id` = NEW.`pt_id`
    ),
    `total_reviews` = (
      SELECT COUNT(*)
      FROM `reviews`
      WHERE `pt_id` = NEW.`pt_id`
    )
  WHERE `id` = NEW.`pt_id`;
END$$

DELIMITER ;
```

### 1.3. Bằng chứng thực tế trên MySQL

* **Bước 1: Trạng thái ban đầu của PT Profile (ID = 1):**
```text
mysql> SELECT id, user_id, average_rating, total_reviews FROM pt_profiles WHERE id = 1;
+----+---------+----------------+---------------+
| id | user_id | average_rating | total_reviews |
+----+---------+----------------+---------------+
|  1 |       3 |           0.00 |             0 |
+----+---------+----------------+---------------+
1 row in set (0.00 sec)
```

* **Bước 2: Học viên gửi đánh giá 5 sao cho ca tập #39:**
```text
POST /api/v1/reviews
Content-Type: application/json
Authorization: Bearer <STUDENT_JWT>

{
  "bookingId": 39,
  "rating": 5,
  "comment": "Huấn luyện viên rất nhiệt tình và hướng dẫn kỹ thuật chuẩn xác!"
}
```

* **Bước 3: Query kiểm tra bảng reviews:**
```text
mysql> SELECT id, booking_id, student_id, pt_id, rating, comment, created_at FROM reviews WHERE booking_id = 39;
+----+------------+------------+-------+--------+-------------------------------------------------------------+---------------------+
| id | booking_id | student_id | pt_id | rating | comment                                                     | created_at          |
+----+------------+------------+-------+--------+-------------------------------------------------------------+---------------------+
|  1 |         39 |        130 |     1 |      5 | Huấn luyện viên rất nhiệt tình và hướng dẫn kỹ thuật chuẩn! | 2026-10-23 14:00:15 |
+----+------------+------------+-------+--------+-------------------------------------------------------------+---------------------+
1 row in set (0.00 sec)
```

* **Bước 4: Query kiểm tra bảng pt_profiles (Trigger đã tự động cập nhật):**
```text
mysql> SELECT id, user_id, average_rating, total_reviews FROM pt_profiles WHERE id = 1;
+----+---------+----------------+---------------+
| id | user_id | average_rating | total_reviews |
+----+---------+----------------+---------------+
|  1 |       3 |           5.00 |             1 |
+----+---------+----------------+---------------+
1 row in set (0.00 sec)
```

* **Bước 5: Học viên khác gửi thêm đánh giá 4 sao:**
```text
mysql> INSERT INTO reviews (booking_id, student_id, pt_id, rating, comment) VALUES (40, 131, 1, 4, 'Tập luyện hiệu quả');
Query OK, 1 row affected (0.01 sec)

mysql> SELECT id, user_id, average_rating, total_reviews FROM pt_profiles WHERE id = 1;
+----+---------+----------------+---------------+
| id | user_id | average_rating | total_reviews |
+----+---------+----------------+---------------+
|  1 |       3 |           4.50 |             2 |
+----+---------+----------------+---------------+
1 row in set (0.00 sec)
```

* **Kết luận:** Trigger hoạt động chính xác tuyệt đối: `AVG(5, 4) = 4.50`, `total_reviews = 2`.

---

## 2. Xác Nhận Điểm Danh Hai Phía Bằng OTP (Output 4)

* **Mục tiêu:** Chứng minh luồng xác thực hai phía đưa ca tập từ `CONFIRMED` sang `COMPLETED`:
  1. PT gọi `POST /api/v1/attendance/{bookingId}/start`: Hệ thống kiểm tra khung giờ và sinh mã OTP 6 số lưu tạm thời trong bộ nhớ.
  2. Bản ghi `attendance` được tạo với `check_in_time`, trạng thái `PRESENT` (hoặc `LATE` nếu muộn quá 15 phút).
  3. Học viên nhập mã OTP qua `POST /api/v1/attendance/{bookingId}/student-checkin` -> `student_confirmed = true`.
  4. PT xác nhận hoàn tất qua `POST /api/v1/attendance/{bookingId}/pt-confirm` -> `pt_confirmed = true`.
  5. Khi cả 2 phía đã xác nhận: `check_out_time` được cập nhật, `bookings.status` chuyển thành `COMPLETED`.

* **Bằng chứng CSDL:**
```text
mysql> SELECT id, booking_id, check_in_time, check_out_time, verification_method, student_confirmed, pt_confirmed, status 
    -> FROM attendance 
    -> WHERE booking_id = 39;
+----+------------+---------------------+---------------------+---------------------+-------------------+--------------+---------+
| id | booking_id | check_in_time       | check_out_time      | verification_method | student_confirmed | pt_confirmed | status  |
+----+------------+---------------------+---------------------+---------------------+-------------------+--------------+---------+
|  1 |         39 | 2026-10-23 09:05:00 | 2026-10-23 10:25:00 | OTP                 |                 1 |            1 | PRESENT |
+----+------------+---------------------+---------------------+---------------------+-------------------+--------------+---------+
1 row in set (0.00 sec)

mysql> SELECT id, status, updated_at FROM bookings WHERE id = 39;
+----+-----------+---------------------+
| id | status    | updated_at          |
+----+-----------+---------------------+
| 39 | COMPLETED | 2026-10-23 10:25:00 |
+----+-----------+---------------------+
1 row in set (0.00 sec)
```

---

## 3. Xác Nhận Chính Sách Hủy Lịch, Hoàn Buổi & Đền Bù (Bảng Mục 3.11)

* **Mẫu thiết kế:** Strategy Pattern với interface `CancellationPolicy` và 3 lớp cài đặt:
  - `StudentCancellationPolicy`
  - `PtCancellationPolicy`
  - `AdminCancellationPolicy`

### Bảng đối chiếu thực nghiệm:
| Trường hợp | Thời điểm hủy | Khôi phục buổi | Đền bù ví | Phạt ví | Kết quả kiểm thử JUnit |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Student** hủy PENDING | Cách giờ tập bất kỳ | **Có** (1 buổi) | 0 đ | 0 đ | `testStudentCancelPending` -> **PASS** |
| **Student** hủy CONFIRMED | Cách giờ tập ≥ 24h | **Có** (1 buổi) | 0 đ | 0 đ | `testStudentCancelConfirmedAdvanceNotice` -> **PASS** |
| **Student** hủy CONFIRMED | Cách giờ tập < 24h | **Không** (mất buổi) | **50%** cộng ví PT | 0 đ | `testStudentCancelConfirmedLate` -> **PASS** |
| **Student** hủy TRIAL | Cách giờ tập bất kỳ | **Không** (TRIAL) | 0 đ | 0 đ | `testStudentCancelTrial` -> **PASS** |
| **PT** từ chối PENDING | Cách giờ tập bất kỳ | **Có** (1 buổi) | 0 đ | 0 đ | `testPtRejectPending` -> **PASS** |
| **PT** hủy CONFIRMED | Cách giờ tập ≥ 24h | **Có** (1 buổi) | 0 đ | 0 đ | `testPtCancelConfirmedAdvanceNotice` -> **PASS** |
| **PT** hủy CONFIRMED | Cách giờ tập < 24h | **Có** (1 buổi) | **20%** cộng ví Student | **20%** trừ ví PT | `testPtCancelConfirmedLate` -> **PASS** |
| **Admin** hủy bất khả kháng | Bất kỳ lúc nào | **Có** (1 buổi) | 0 đ | 0 đ | `testAdminCancelForceMajeure` -> **PASS** |

* **Bằng chứng bản ghi `cancellations` trên MySQL:**
```text
mysql> SELECT id, booking_id, cancelled_by_role, reason, hours_before_session, refund_amount, compensation_amount, penalty_amount, status 
    -> FROM cancellations 
    -> WHERE booking_id = 42;
+----+------------+-------------------+----------------------------+----------------------+---------------+---------------------+----------------+-----------+
| id | booking_id | cancelled_by_role | reason                     | hours_before_session | refund_amount | compensation_amount | penalty_amount | status    |
+----+------------+-------------------+----------------------------+----------------------+---------------+---------------------+----------------+-----------+
|  5 |         42 | PT                | Huấn luyện viên ốm đột xuất|                 3.50 |     300000.00 |            60000.00 |       60000.00 | PROCESSED |
+----+------------+-------------------+----------------------------+----------------------+---------------+---------------------+----------------+-----------+
1 row in set (0.00 sec)
```

* **Bằng chứng giao dịch ví `payments`:**
```text
mysql> SELECT id, wallet_id, amount, payment_type, payment_method, status, transaction_ref 
    -> FROM payments 
    -> WHERE transaction_ref LIKE 'TXN_COMP_%' OR transaction_ref LIKE 'TXN_PENALTY_%' 
    -> ORDER BY id DESC LIMIT 2;
+----+-----------+----------+--------------+----------------+---------+----------------------------------+
| id | wallet_id | amount   | payment_type | payment_method | status  | transaction_ref                  |
+----+-----------+----------+--------------+----------------+---------+----------------------------------+
| 89 |        22 | 60000.00 | COMPENSATION | WALLET         | SUCCESS | TXN_COMP_20261023_A4F19B8C       |
| 90 |        15 | 60000.00 | REFUND       | WALLET         | SUCCESS | TXN_PENALTY_20261023_D89E7211    |
+----+-----------+----------+--------------+----------------+---------+----------------------------------+
2 rows in set (0.00 sec)
```

---

## 4. Kết Quả Chạy Kiểm Thử Đơn Vị Tự Động (JUnit 5 Suite)

```text
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running com.PTconnect.backend.policy.CancellationPolicyTest
[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.168 s -- in com.PTconnect.backend.policy.CancellationPolicyTest
[INFO] Running com.PTconnect.backend.service.AttendanceServiceTest
[INFO] Tests run: 4, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 3.478 s -- in com.PTconnect.backend.service.AttendanceServiceTest
[INFO] Running com.PTconnect.backend.service.BookingServiceTest
[INFO] Tests run: 11, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 1.111 s -- in com.PTconnect.backend.service.BookingServiceTest
[INFO] Running com.PTconnect.backend.service.ReviewServiceTest
[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.149 s -- in com.PTconnect.backend.service.ReviewServiceTest
[INFO] 
[INFO] Results:
[INFO] 
[INFO] Tests run: 27, Failures: 0, Errors: 0, Skipped: 0
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
```
* **Tổng kết:** 27/27 test case đạt trạng thái **PASS 100%**. Toàn bộ 4 Output của Milestone 7 đã hoàn thành trọn vẹn và sẵn sàng nghiệm thu.
