# Bằng Chứng Xác Nhận Cơ Sở Dữ Liệu - Milestone 3 

## 1. Xác nhận tài khoản Admin & Chuỗi băm BCrypt hợp lệ
* **Mục tiêu:** Đảm bảo tài khoản hệ thống đã tồn tại và mật khẩu được băm bằng thuật toán BCrypt (chiều dài 60 ký tự, cost factor 10).
* **Bằng chứng chạy thực tế:**
  ```text
  mysql> SELECT id, email, role, password_hash, LENGTH(password_hash) AS hash_length FROM users WHERE role = 'ADMIN';
  +----+--------------------+-------+--------------------------------------------------------------+-------------+
  | id | email              | role  | password_hash                                                | hash_length |
  +----+--------------------+-------+--------------------------------------------------------------+-------------+
  |  5 | admin@ptconnect.vn | ADMIN | $2a$10$IciBJIW1NX.1Za3YIyYqjO7H/SpL//eFExQrDxRk/33YLKZjOvyey |          60 |
  +----+--------------------+-------+--------------------------------------------------------------+-------------+
  1 row in set (0.00 sec)
  ```
* **Kết luận:** Đạt chuẩn bảo mật, không lưu plaintext password.

## 2. Kiểm tra ràng buộc UNIQUE (Chống đăng ký trùng Email và Phone)
* **Mục tiêu:** Ngăn chặn tuyệt đối việc tạo nhiều tài khoản có cùng email hoặc số điện thoại.
* **Bằng chứng chạy thực tế (Email):**
  ```text
  mysql> INSERT INTO users (full_name, email, password_hash, phone, role) 
      -> VALUES ('Hacker Test', 'admin@ptconnect.vn', '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0999999999', 'STUDENT'); 
  ERROR 1062 (23000): Duplicate entry 'admin@ptconnect.vn' for key 'users.email'
  ```
* **Bằng chứng chạy thực tế (Phone):**
  ```text
  mysql> INSERT INTO users (full_name, email, password_hash, phone, role) 
      -> VALUES ('Test Phone', 'phone_dup@ptconnect.vn', '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000005', 'STUDENT');
  ERROR 1062 (23000): Duplicate entry '0900000005' for key 'users.phone'
  ```
* **Kết luận:** Cơ sở dữ liệu chặn đứng việc đăng ký trùng lặp thông tin định danh ở cấp độ schema.

## 3. Kiểm tra liên kết Ví người dùng (Wallets)
* **Mục tiêu:** Đảm bảo mô hình liên kết 1-1 giữa User và Wallet sẵn sàng phục vụ tạo tài khoản mới kèm ví ban đầu.
* **Bằng chứng chạy thực tế:**
  ```text
  mysql> SELECT u.id, u.email, u.role, w.id AS wallet_id, w.balance, w.currency 
      -> FROM users u 
      -> LEFT JOIN wallets w ON u.id = w.user_id;
  +----+------------------------+---------+-----------+------------+----------+
  | id | email                  | role    | wallet_id | balance    | currency |
  +----+------------------------+---------+-----------+------------+----------+
  |  1 | student.a@ptconnect.vn | STUDENT |         1 | 5000000.00 | VND      |
  |  2 | student.b@ptconnect.vn | STUDENT |         2 | 4200000.00 | VND      |
  |  3 | pt.hoangc@ptconnect.vn | PT      |         3 |       0.00 | VND      |
  |  4 | pt.minhd@ptconnect.vn  | PT      |         4 |       0.00 | VND      |
  |  5 | admin@ptconnect.vn     | ADMIN   |      NULL |       NULL | NULL     |
  +----+------------------------+---------+-----------+------------+----------+
  5 rows in set (0.00 sec)
  ```
* **Kết luận:** Cấu trúc bảng ví và quan hệ khóa ngoại toàn vẹn (Admin mặc định không có ví theo đúng seed data).