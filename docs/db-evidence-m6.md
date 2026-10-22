# Bằng Chứng Xác Nhận Cơ Sở Dữ Liệu - Milestone 6

**Dự án:** PT-Connect  
**Tác giả phụ trách:** Thành  
**Phạm vi:** Kiểm tra thực tế trên hệ quản trị cơ sở dữ liệu MySQL cho các nghiệp vụ Milestone 6 (Đặt lịch PACKAGE & TRIAL, Trừ/Hoàn buổi tập, PT Confirm/Reject, Chống đặt trùng đa luồng và Cập nhật Avatar).

---

## 1. Xác Nhận Đặt Lịch PACKAGE: Trừ Buổi Tập & Đổi Trạng Thái Slot (Output 1)

* **Mục tiêu:** Chứng minh khi học viên đặt lịch theo gói hợp đồng (`PACKAGE`):
  1. Bản ghi `bookings` được tạo với trạng thái `PENDING`.
  2. Khung giờ `availability_slots` chuyển từ `AVAILABLE` sang `BOOKED`.
  3. Kho buổi tập `enrollments.remaining_sessions` bị trừ đúng 1 buổi qua phương thức `consumeSession()`.
  4. Cột sinh `active_slot_id` nhận giá trị bằng `slot_id` để khóa slot ở tầng DB.

* **Bằng chứng SQL thực tế trên MySQL:**
  ```text
  mysql> SELECT id, booking_type, enrollment_id, student_id, pt_id, slot_id, status, session_fee, active_slot_id 
      -> FROM bookings 
      -> WHERE id = 39;
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  | id | booking_type | enrollment_id | student_id | pt_id | slot_id | status  | session_fee | active_slot_id |
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  | 39 | PACKAGE      |            65 |        130 |     1 |      58 | PENDING |   300000.00 |             58 |
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  1 row in set (0.00 sec)

  mysql> SELECT id, pt_id, start_time, end_time, status 
      -> FROM availability_slots 
      -> WHERE id = 58;
  +----+-------+---------------------+---------------------+--------+
  | id | pt_id | start_time          | end_time            | status |
  +----+-------+---------------------+---------------------+--------+
  | 58 |     1 | 2026-11-25 09:00:00 | 2026-11-25 10:30:00 | BOOKED |
  +----+-------+---------------------+---------------------+--------+
  1 row in set (0.00 sec)

  mysql> SELECT id, student_id, total_sessions, remaining_sessions, status 
      -> FROM enrollments 
      -> WHERE id = 65;
  +----+------------+----------------+--------------------+--------+
  | id | student_id | total_sessions | remaining_sessions | status |
  +----+------------+----------------+--------------------+--------+
  | 65 |        130 |             12 |                 11 | ACTIVE |
  +----+------------+----------------+--------------------+--------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Slot 58 đã chuyển sang `BOOKED`, `remaining_sessions` giảm từ 12 xuống 11, `active_slot_id = 58`.

---

## 2. Xác Nhận Đặt Lịch Học Thử TRIAL & Chặn Học Thử Lần 2 (Output 1)

* **Mục tiêu:** Chứng minh đặt lịch `TRIAL` không yêu cầu `enrollment_id`, `session_fee = 0`, slot chuyển sang `BOOKED` và ngăn chặn học thử lần 2 với cùng PT.

* **Bằng chứng SQL thực tế:**
  ```text
  mysql> SELECT id, booking_type, enrollment_id, student_id, pt_id, slot_id, status, session_fee, active_slot_id 
      -> FROM bookings 
      -> WHERE id = 37;
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  | id | booking_type | enrollment_id | student_id | pt_id | slot_id | status  | session_fee | active_slot_id |
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  | 37 | TRIAL        |          NULL |        125 |     1 |      54 | PENDING |        0.00 |             54 |
  +----+--------------+---------------+------------+-------+---------+---------+-------------+----------------+
  1 row in set (0.00 sec)
  ```
* Khi cùng học viên ID 125 cố gắng đặt buổi học thử lần 2 với PT ID 1, hệ thống kiểm tra qua `existsByStudentIdAndPtIdAndBookingType` và lập tức từ chối trả về HTTP `400 Bad Request`.

---

## 3. Xác Nhận PT Phê Duyệt Booking Confirm (Output 3)

* **Mục tiêu:** Chứng minh khi PT gọi `PUT /api/v1/pt/bookings/{id}/confirm`, trạng thái `bookings.status` chuyển từ `PENDING` sang `CONFIRMED`.

* **Bằng chứng SQL thực tế:**
  ```text
  mysql> SELECT id, booking_type, enrollment_id, student_id, pt_id, slot_id, status, active_slot_id 
      -> FROM bookings 
      -> WHERE id = 40;
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  | id | booking_type | enrollment_id | student_id | pt_id | slot_id | status    | active_slot_id |
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  | 40 | PACKAGE      |            66 |        131 |     1 |      59 | CONFIRMED |             59 |
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Booking ID 40 chuyển sang `CONFIRMED`, `active_slot_id = 59` vẫn được duy trì để bảo lưu khung giờ cho học viên.

---

## 4. Xác Nhận PT Từ Chối Reject: Hoàn Slot, Hoàn Buổi & Bảng Cancellations (Output 3)

* **Mục tiêu:** Chứng minh khi PT gọi `PUT /api/v1/pt/bookings/{id}/reject`:
  1. `bookings.status` chuyển sang `CANCELLED`.
  2. Cột sinh `active_slot_id` tự động trở về `NULL`.
  3. `availability_slots.status` tự động phục hồi về `AVAILABLE`.
  4. Hợp đồng `enrollments.remaining_sessions` được hoàn lại 1 buổi qua `restoreSession()`.
  5. Có bản ghi ghi nhận vào bảng `cancellations`.

* **Bằng chứng SQL thực tế:**
  ```text
  mysql> SELECT id, booking_type, enrollment_id, student_id, pt_id, slot_id, status, active_slot_id 
      -> FROM bookings 
      -> WHERE id = 41;
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  | id | booking_type | enrollment_id | student_id | pt_id | slot_id | status    | active_slot_id |
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  | 41 | PACKAGE      |            67 |        132 |     1 |      60 | CANCELLED |           NULL |
  +----+--------------+---------------+------------+-------+---------+-----------+----------------+
  1 row in set (0.00 sec)

  mysql> SELECT id, pt_id, start_time, end_time, status 
      -> FROM availability_slots 
      -> WHERE id = 60;
  +----+-------+---------------------+---------------------+-----------+
  | id | pt_id | start_time          | end_time            | status    |
  +----+-------+---------------------+---------------------+-----------+
  | 60 |     1 | 2026-11-27 09:00:00 | 2026-11-27 10:30:00 | AVAILABLE |
  +----+-------+---------------------+---------------------+-----------+
  1 row in set (0.00 sec)

  mysql> SELECT id, student_id, total_sessions, remaining_sessions, status 
      -> FROM enrollments 
      -> WHERE id = 67;
  +----+------------+----------------+--------------------+--------+
  | id | student_id | total_sessions | remaining_sessions | status |
  +----+------------+----------------+--------------------+--------+
  | 67 |        132 |             12 |                 12 | ACTIVE |
  +----+------------+----------------+--------------------+--------+
  1 row in set (0.00 sec)

  mysql> SELECT id, booking_id, cancelled_by_id, cancelled_by_role, reason, hours_before_session, refund_amount, status 
      -> FROM cancellations 
      -> WHERE booking_id = 41;
  +----+------------+-----------------+-------------------+-------------------------------------------------------------+----------------------+---------------+-----------+
  | id | booking_id | cancelled_by_id | cancelled_by_role | reason                                                      | hours_before_session | refund_amount | status    |
  +----+------------+-----------------+-------------------+-------------------------------------------------------------+----------------------+---------------+-----------+
  |  4 |         41 |               3 | PT                | PT có lịch tập huấn đột xuất của Liên đoàn Thể hình         |               951.00 |     300000.00 | PROCESSED |
  +----+------------+-----------------+-------------------+-------------------------------------------------------------+----------------------+---------------+-----------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Khi bị từ chối, slot 60 đã được giải phóng về `AVAILABLE`, `active_slot_id` trở về `NULL` giúp slot có thể được đặt lại bởi người khác, học viên được hoàn trả 1 buổi (`remaining_sessions = 12/12`), nhật ký hủy lịch được lưu trữ minh bạch.

---

## 5. Xác Nhận Chống Đặt Trùng Lịch Đồng Thời (Output 4)

* **Mục tiêu:** Chứng minh cơ chế bảo vệ kép giữa khóa bi quan `@Lock(LockModeType.PESSIMISTIC_WRITE)` và ràng buộc `UNIQUE KEY uq_active_slot (active_slot_id)`:
  * Khi 2 luồng đồng thời gọi `POST /api/v1/bookings` vào cùng 1 slot ID:
    * Luồng A nhanh hơn: tạo booking thành công (HTTP 201 Created), `active_slot_id = slotId`.
    * Luồng B: bị chặn bởi khóa dòng hoặc xung đột khóa duy nhất `uq_active_slot` và nhận HTTP **409 Conflict**.
* **Kết quả kiểm thử tự động `test_05_concurrent_double_booking_anti_conflict_proof`:**
  ```text
  Thread-1: POST /api/v1/bookings -> HTTP 201 Created (Booking ID: 38, Active Slot: 57)
  Thread-2: POST /api/v1/bookings -> HTTP 409 Conflict: "Khung giờ này đã được đặt hoặc không còn khả dụng"
  ```
* **Bằng chứng trên Database:**
  * Chỉ tồn tại đúng 1 bản ghi `bookings` có `active_slot_id = 57`.
  * Không bao giờ xảy ra tình trạng duplicate slot active trên database.

---

## 6. Xác Nhận Cập Nhật Ảnh Đại Diện Người Dùng (Output 5 - Hiệu)

* **Mục tiêu:** Chứng minh người dùng cập nhật thành công avatar qua `PUT /api/v1/users/avatar` và dữ liệu được ghi nhận vào cột `users.avatar_url`.

* **Bằng chứng SQL thực tế trên MySQL:**
  ```text
  mysql> SELECT id, full_name, email, role, avatar_url, updated_at 
      -> FROM users 
      -> WHERE id IN (133, 3);
  +-----+-----------------+--------------------------------------+---------+-----------------------------------------------------------------------+---------------------+
  | id  | full_name       | email                                | role    | avatar_url                                                            | updated_at          |
  +-----+-----------------+--------------------------------------+---------+-----------------------------------------------------------------------+---------------------+
  |   3 | Le Hoang C      | pt.hoangc@ptconnect.vn               | PT      | https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=400   | 2026-10-22 13:57:35 |
  | 133 | Student Test M6 | student_523443716efb@ptconnect-m6.vn | STUDENT | https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400   | 2026-10-22 13:57:35 |
  +-----+-----------------+--------------------------------------+---------+-----------------------------------------------------------------------+---------------------+
  2 rows in set (0.00 sec)
  ```
* **Kết luận:** Avatar URL được lưu trữ chuẩn xác trên MySQL và phản ánh tức thì qua API `GET /api/v1/auth/me` cũng như giao diện Streamlit.
