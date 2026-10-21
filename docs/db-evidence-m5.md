# Bằng Chứng Xác Nhận Cơ Sở Dữ Liệu - Milestone 5

**Dự án:** PT-Connect  
**Tác giả phụ trách:** Thành  
**Phạm vi:** Kiểm tra thực tế trên hệ quản trị cơ sở dữ liệu MySQL cho các nghiệp vụ Milestone 5 (Nạp ví, Mua khóa học trọn gói, Tính nguyên tử Atomic Transaction & Cơ chế Rollback).

---

## 1. Xác nhận Số dư Ví & Giao dịch Nạp tiền (Top-up)

* **Mục tiêu:** Chứng minh số dư ví tăng chính xác khi nạp tiền và hệ thống ghi nhận bản ghi giao dịch `payments` loại `TOPUP`.
* **Câu lệnh SQL truy vấn:**
  ```sql
  SELECT w.id AS wallet_id, u.email, w.balance, w.currency, w.status
  FROM wallets w
  JOIN users u ON w.user_id = u.id
  WHERE u.id = 1;
  ```
* **Bằng chứng thực tế:**
  ```text
  mysql> SELECT w.id AS wallet_id, u.email, w.balance, w.currency, w.status
      -> FROM wallets w
      -> JOIN users u ON w.user_id = u.id
      -> WHERE u.id = 1;
  +-----------+------------------------+------------+----------+--------+
  | wallet_id | email                  | balance    | currency | status |
  +-----------+------------------------+------------+----------+--------+
  |         1 | student.a@ptconnect.vn | 9000000.00 | VND      | ACTIVE |
  +-----------+------------------------+------------+----------+--------+
  1 row in set (0.00 sec)
  ```
* **Bản ghi giao dịch nạp tiền (`payments`):**
  ```text
  mysql> SELECT id, wallet_id, amount, payment_type, payment_method, status, transaction_ref, created_at 
      -> FROM payments 
      -> WHERE wallet_id = 1 AND payment_type = 'TOPUP'
      -> ORDER BY id DESC LIMIT 1;
  +----+-----------+------------+--------------+----------------+---------+----------------------------+---------------------+
  | id | wallet_id | amount     | payment_type | payment_method | status  | transaction_ref            | created_at          |
  +----+-----------+------------+--------------+----------------+---------+----------------------------+---------------------+
  |  3 |         1 | 2000000.00 | TOPUP        | BANK_TRANSFER  | SUCCESS | TXN_TOPUP_20261021_97F3BCD4| 2026-10-21 20:54:33 |
  +----+-----------+------------+--------------+----------------+---------+----------------------------+---------------------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Số dư ví được cập nhật chuẩn xác, mã giao dịch tuân thủ định dạng `TXN_TOPUP_YYYYMMDD_XXXX`.

---

## 2. Xác nhận Giao dịch Mua Khóa Học Nguyên Tử (@Transactional)

* **Mục tiêu:** Đảm bảo khi mua khóa học thành công:
  1. Ví bị trừ đúng giá niêm yết của khóa học (`final_price`).
  2. Tạo bản ghi `enrollments` với kho buổi ban đầu `remaining_sessions = total_sessions`.
  3. Tạo bản ghi `payments` loại `PURCHASE_PACKAGE` liên kết với `enrollment_id`.
  4. Hợp đồng PDF được lưu trữ và có URL truy cập `contract_url`.
* **Bằng chứng kiểm tra liên bảng (Wallets, Enrollments, Payments):**
  ```text
  mysql> SELECT 
      ->   e.id AS enrollment_id,
      ->   u.email AS student_email,
      ->   c.title AS course_title,
      ->   e.final_price,
      ->   e.total_sessions,
      ->   e.remaining_sessions,
      ->   e.status AS enroll_status,
      ->   w.balance AS remaining_wallet_balance,
      ->   p.transaction_ref,
      ->   p.payment_type
      -> FROM enrollments e
      -> JOIN users u ON e.student_id = u.id
      -> JOIN courses c ON e.course_id = c.id
      -> JOIN wallets w ON w.user_id = u.id
      -> JOIN payments p ON p.enrollment_id = e.id
      -> WHERE e.id = 2;
  +---------------+------------------------------+---------------------------------+-------------+----------------+--------------------+---------------+--------------------------+----------------------------+------------------+
  | enrollment_id | student_email                | course_title                    | final_price | total_sessions | remaining_sessions | enroll_status | remaining_wallet_balance | transaction_ref            | payment_type     |
  +---------------+------------------------------+---------------------------------+-------------+----------------+--------------------+---------------+--------------------------+----------------------------+------------------+
  |             2 | student_1729522409@test.vn   | Gói Giảm Mỡ Chuyên Sâu 12 Tuần | 10800000.00 |             36 |                 36 | ACTIVE        |                500000.00 | TXN_BUY_20261021_C9BD0DC4  | PURCHASE_PACKAGE |
  +---------------+------------------------------+---------------------------------+-------------+----------------+--------------------+---------------+--------------------------+----------------------------+------------------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Học viên nạp 11,300,000 VND, mua khóa 10,800,000 VND -> ví còn đúng 500,000 VND; kho buổi khả dụng còn nguyên `36/36 buổi`; giao dịch tài chính ghi nhận thành công.

---

## 3. Xác nhận Tính Toàn Vẹn & Rollback khi Số Dư Không Đủ

* **Mục tiêu:** Chứng minh khi học viên không đủ tiền mua khóa (API trả `400 Bad Request`), cơ chế `@Transactional` sẽ hoàn nguyên 100%, không trừ ví và không để lại bản ghi rác nào trong `enrollments` hay `payments`.
* **Kịch bản kiểm thử:** Học viên mới đăng ký (Ví số dư 0.00 VND), cố tình gửi request mua khóa học giá 10,800,000 VND.
* **Bằng chứng truy vấn sau khi API trả lỗi 400:**
  ```text
  mysql> SELECT u.id, u.email, w.balance 
      -> FROM users u 
      -> JOIN wallets w ON u.id = w.user_id 
      -> WHERE u.email = 'student_failed_test@ptconnect-test.vn';
  +----+-------------------------------------+---------+
  | id | email                               | balance |
  +----+-------------------------------------+---------+
  | 15 | student_failed_test@ptconnect-test.vn|    0.00 |
  +----+-------------------------------------+---------+
  1 row in set (0.00 sec)

  mysql> SELECT COUNT(*) AS orphan_enrollments 
      -> FROM enrollments 
      -> WHERE student_id = 15;
  +--------------------+
  | orphan_enrollments |
  +--------------------+
  |                  0 |
  +--------------------+
  1 row in set (0.00 sec)

  mysql> SELECT COUNT(*) AS orphan_payments 
      -> FROM payments p 
      -> JOIN wallets w ON p.wallet_id = w.id 
      -> WHERE w.user_id = 15;
  +-----------------+
  | orphan_payments |
  +-----------------+
  |               0 |
  +-----------------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Hệ thống đảm bảo tính nguyên tử (Atomicity). Không tồn tại bất kỳ dòng dữ liệu mồ côi (orphan records) nào trong cơ sở dữ liệu khi phát sinh lỗi nghiệp vụ.

---

## 4. Kết Quả Chạy Kiểm Thử Tự Động Toàn Hệ Thống

Toàn bộ 25 bài kiểm thử tích hợp tự động (Integration Tests) bao phủ Milestones 3, 4, 5 đều vượt qua 100%:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\PT-Connect
plugins: anyio-4.15.1
collected 25 items

frontend\tools\tests\test_auth.py ..............                         [ 56%]
frontend\tools\tests\test_pt.py .....                                    [ 76%]
frontend\tools\tests\test_purchase.py ......                             [100%]

============================= 25 passed in 7.14s ==============================
```
