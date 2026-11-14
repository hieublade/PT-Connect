# PT-Connect Backend (Python FastAPI)

Hệ thống Backend nền tảng kết nối Huấn luyện viên cá nhân và Học viên (PT Connect), xây dựng hoàn toàn bằng **Python 3.12** kết hợp **FastAPI** và **SQLAlchemy 2.0 ORM**, tuân thủ nghiêm ngặt kiến trúc phân tầng (Clean / Layered Architecture) và chuẩn hóa CSDL đạt dạng chuẩn Boyce-Codd (BCNF).

---

## 1. Sơ Đồ Kiến Trúc Hệ Thống (System Architecture)

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (Python Streamlit)"]
        UI_Admin["Admin Dashboard View"]
        UI_PT["PT Dashboard View"]
        UI_Student["Student Dashboard View"]
    end

    subgraph API_Gateway["FastAPI Gateway & Security"]
        Router["API Router (/api/v1)"]
        JWT["PyJWT Auth & RBAC (HS384)"]
        CORS["CORS Middleware"]
        Pydantic["Pydantic v2 Schema Validation"]
    end

    subgraph Service_Layer["Business Domain Services"]
        S_Auth["Auth & User Service"]
        S_PT["PT & Catalog Service"]
        S_Booking["Booking & Cancellation Service"]
        S_Dispute["Dispute Resolution Service (48h SLA)"]
        S_Wallet["Wallet & Payment Service"]
        S_Audit["Attendance & Review Service"]
        S_Admin["Admin Statistics & Revenue Service"]
    end

    subgraph Repository_Layer["Persistence Layer (SQLAlchemy 2.0)"]
        ORM_Base["Declarative Base (Mapped Column)"]
        Repo_User["User & Profile Repo"]
        Repo_Booking["Booking Repo (BCNF Composite FK)"]
        Repo_Dispute["Dispute Repo"]
        Repo_Wallet["Wallet Repo (with_for_update Row Lock)"]
    end

    subgraph Database["Relational Storage (MySQL 8.0 ACID)"]
        DB_Tables["16 Tables (BCNF Normalized)"]
        DB_Triggers["Audit Triggers (trg_wallets_audit_ledger)"]
        DB_Procedures["Stored Procedures (sp_expire_enrollments)"]
        DB_Views["Views Đối Soát (v_wallet_reconciliation)"]
    end

    UI_Admin -->|HTTP / JSON| Router
    UI_PT -->|HTTP / JSON| Router
    UI_Student -->|HTTP / JSON| Router

    Router --> CORS
    CORS --> JWT
    JWT --> Pydantic

    Pydantic --> S_Auth
    Pydantic --> S_PT
    Pydantic --> S_Booking
    Pydantic --> S_Dispute
    Pydantic --> S_Wallet
    Pydantic --> S_Audit
    Pydantic --> S_Admin

    S_Auth --> Repo_User
    S_PT --> Repo_User
    S_Booking --> Repo_Booking
    S_Dispute --> Repo_Dispute
    S_Wallet --> Repo_Wallet
    S_Audit --> Repo_Booking
    S_Admin --> Repo_Wallet

    Repo_User --> ORM_Base
    Repo_Booking --> ORM_Base
    Repo_Dispute --> ORM_Base
    Repo_Wallet --> ORM_Base

    ORM_Base --> DB_Tables
    DB_Tables --- DB_Triggers
    DB_Tables --- DB_Procedures
    DB_Tables --- DB_Views
```

---

## 2. Sơ Đồ Thực Thể - Quan Hệ CSDL (ERD Chuẩn BCNF)

Hệ thống gồm 16 bảng dữ liệu đã được chứng minh đạt chuẩn **Boyce-Codd (BCNF)**, triệt tiêu hoàn toàn thuộc tính đa trị (1NF), phụ thuộc một phần (2NF) và phụ thuộc bắc cầu (3NF & BCNF):

```mermaid
erDiagram
    USERS ||--o| PT_PROFILES : "extends (1:1)"
    USERS ||--|| WALLETS : "owns (1:1)"
    USERS ||--o{ ENROLLMENTS : "student_id (1:N)"
    USERS ||--o{ BOOKINGS : "student_id (1:N)"
    USERS ||--o{ BOOKING_DISPUTES : "sender_id (1:N)"
    USERS ||--o{ CANCELLATIONS : "cancelled_by_id (1:N)"

    PT_PROFILES ||--o{ PT_LOCATIONS : "operates_at (1:N)"
    PT_PROFILES ||--o{ COURSES : "offers (1:N)"
    PT_PROFILES ||--o{ AVAILABILITY_SLOTS : "opens (1:N)"

    COURSES ||--o{ ENROLLMENTS : "course_id (1:N)"

    ENROLLMENTS ||--o{ BOOKINGS : "composite fk (enrollment_id, student_id)"
    ENROLLMENTS ||--o{ WORKOUT_PLANS : "enrollment_id (1:N)"
    ENROLLMENTS ||--o{ PAYMENTS : "enrollment_id (1:N)"

    WORKOUT_PLANS ||--o{ WORKOUTS : "plan_id (1:N)"

    AVAILABILITY_SLOTS ||--o| BOOKINGS : "slot_id (active_slot_id UNIQUE)"

    BOOKINGS ||--o| REVIEWS : "booking_id (1:1 UNIQUE)"
    BOOKINGS ||--o| ATTENDANCE : "booking_id (1:1 UNIQUE)"
    BOOKINGS ||--o| CANCELLATIONS : "booking_id (1:1 UNIQUE)"
    BOOKINGS ||--o| BOOKING_DISPUTES : "booking_id (1:1 UNIQUE)"

    WALLETS ||--o{ PAYMENTS : "wallet_id (1:N)"
    WALLETS ||--o{ WALLET_AUDIT_LOGS : "wallet_id (1:N)"

    USERS {
        bigint id PK
        varchar email UK
        varchar phone UK
        varchar full_name
        varchar password_hash
        enum role
        enum status
        varchar avatar_url
        timestamp created_at
        timestamp updated_at
    }

    PT_PROFILES {
        bigint id PK
        bigint user_id UK,FK
        text bio
        int experience_years
        text location_pricing_note
        varchar certificate_url
        decimal average_rating
        int total_reviews
        enum verification_status
        timestamp created_at
        timestamp updated_at
    }

    PT_LOCATIONS {
        bigint id PK
        bigint pt_id FK
        varchar location_name
    }

    COURSES {
        bigint id PK
        bigint pt_id FK
        varchar title
        text description
        int total_sessions
        int validity_days
        decimal base_price
        enum status
        timestamp created_at
    }

    ENROLLMENTS {
        bigint id PK
        bigint student_id FK
        bigint course_id FK
        varchar training_location
        decimal final_price
        int total_sessions
        int remaining_sessions
        date start_date
        date end_date
        varchar contract_url
        enum status
        timestamp created_at
    }

    AVAILABILITY_SLOTS {
        bigint id PK
        bigint pt_id FK
        datetime start_time
        datetime end_time
        enum status
        timestamp created_at
    }

    BOOKINGS {
        bigint id PK
        enum booking_type
        bigint enrollment_id FK
        bigint student_id FK
        bigint slot_id FK
        decimal session_fee
        enum status
        varchar student_note
        timestamp created_at
        timestamp updated_at
        bigint active_slot_id UK "generated physical column for conditional unique"
    }

    REVIEWS {
        bigint id PK
        bigint booking_id UK,FK
        smallint rating
        text comment
        timestamp created_at
    }

    ATTENDANCE {
        bigint id PK
        bigint booking_id UK,FK
        datetime check_in_time
        datetime check_out_time
        enum verification_method
        boolean student_confirmed
        boolean pt_confirmed
        enum status
    }

    CANCELLATIONS {
        bigint id PK
        bigint booking_id UK,FK
        bigint cancelled_by_id FK
        enum cancelled_by_role
        varchar reason
        timestamp cancelled_at
        decimal hours_before_session
        decimal refund_amount
        decimal compensation_amount
        decimal penalty_amount
        decimal penalty_shortfall
        varchar evidence_url
        enum status
    }

    BOOKING_DISPUTES {
        bigint id PK
        bigint booking_id UK,FK
        bigint sender_id FK
        enum dispute_type
        text reason
        varchar evidence_url
        varchar counter_evidence_url
        text counter_argument
        enum status
        text admin_notes
        timestamp deadline_at
        timestamp resolved_at
        timestamp created_at
    }

    WALLETS {
        bigint id PK
        bigint user_id UK,FK
        decimal balance
        decimal locked_balance
        varchar currency
        enum status
        timestamp updated_at
    }

    PAYMENTS {
        bigint id PK
        bigint wallet_id FK
        bigint enrollment_id FK
        decimal amount
        enum payment_type
        enum payment_method
        enum status
        varchar transaction_ref UK
        timestamp created_at
    }

    WALLET_AUDIT_LOGS {
        bigint id PK
        bigint wallet_id FK
        decimal old_balance
        decimal new_balance
        decimal old_locked_balance
        decimal new_locked_balance
        enum action_type
        varchar reason
        timestamp created_at
    }

    WORKOUT_PLANS {
        bigint id PK
        bigint enrollment_id FK
        varchar title
        varchar goal
        date start_date
        date end_date
        timestamp created_at
    }

    WORKOUTS {
        bigint id PK
        bigint plan_id FK
        int exercise_order
        varchar exercise_name
        varchar target_muscle
        int sets
        int reps
        decimal weight_kg
        int rest_seconds
        varchar video_demo_url
    }
```

---

## 3. Đặc Điểm Chuẩn Hóa BCNF Trọng Tâm

1. **Khử phụ thuộc bắc cầu `pt_id`:** Các bảng `bookings`, `enrollments`, `workout_plans` hoàn toàn không lưu `pt_id`. Thông tin Huấn luyện viên được suy diễn qua quan hệ BCNF: `bookings -> availability_slots -> pt_profiles`.
2. **Khóa ngoại ghép bảo toàn phụ thuộc hàm:** Ràng buộc `fk_booking_enroll_student` trên `(enrollment_id, student_id) REFERENCES enrollments(id, student_id)` đảm bảo tính toàn vẹn học viên trong hợp đồng mà không vi phạm 3NF/BCNF.
3. **Phân rã dọc (Vertical Partitioning) 1:1:** Bốn bảng `reviews`, `attendance`, `cancellations`, `booking_disputes` mở rộng ca tập qua khóa ngoại `booking_id UNIQUE NOT NULL`, giữ kích thước bản ghi `bookings` tinh gọn và đạt BCNF tuyệt đối.
4. **Không lưu cột dẫn xuất `sender_role`:** Vai trò bên khiếu nại (STUDENT hay PT) được suy diễn động ở tầng ứng dụng bằng Python property, triệt tiêu mọi nguy cơ phụ thuộc hàm vi phạm chuẩn hóa.

---

## 4. Danh Mục Đầy Đủ 68 API Endpoints

### 1. Xác thực & Hồ sơ cá nhân (Auth & Profile - 6 endpoints)
* `POST /api/v1/auth/register` - Đăng ký tài khoản (Học viên / PT)
* `POST /api/v1/auth/login` - Đăng nhập nhận JWT Token
* `GET /api/v1/auth/me` - Lấy thông tin tài khoản đang đăng nhập
* `GET /api/v1/users/{id}` - Lấy thông tin người dùng theo ID
* `PUT /api/v1/users/avatar` - Cập nhật ảnh đại diện người dùng
* `GET /api/v1/public/health` - Health check hệ thống

### 2. Danh mục Khóa học & Lịch PT (Catalogue - 14 endpoints)
* `GET /api/v1/student/dashboard` - Dữ liệu tổng quan màn hình Học viên
* `GET /api/v1/pt-profiles` - Khám phá danh sách Huấn luyện viên
* `GET /api/v1/pt-profiles/{id}` - Chi tiết hồ sơ Huấn luyện viên
* `GET /api/v1/pt-profiles/{id}/courses` - Khóa học của một Huấn luyện viên
* `GET /api/v1/pt-profiles/{id}/slots` - Khung giờ khả dụng của một Huấn luyện viên
* `GET /api/v1/pt/profile` - PT xem hồ sơ cá nhân
* `PUT /api/v1/pt/profile` - PT cập nhật bio, kinh nghiệm, địa điểm
* `POST /api/v1/pt/courses` - PT tạo khóa học mới
* `GET /api/v1/pt/courses` - PT xem danh sách khóa học của mình
* `PUT /api/v1/pt/courses/{id}` - PT chỉnh sửa khóa học
* `DELETE /api/v1/pt/courses/{id}` - PT vô hiệu hóa khóa học
* `POST /api/v1/pt/slots` - PT tạo khung giờ tập mới
* `GET /api/v1/pt/slots` - PT xem danh sách khung giờ tập
* `DELETE /api/v1/pt/slots/{id}` - PT xóa khung giờ trống

### 3. Đặt lịch & Hủy ca tập (Bookings - 9 endpoints)
* `POST /api/v1/bookings` - Học viên đặt lịch ca tập (PACKAGE hoặc TRIAL)
* `GET /api/v1/bookings/my` - Học viên xem danh sách ca tập của mình
* `GET /api/v1/bookings/{id}` - Xem chi tiết một ca tập
* `PUT /api/v1/bookings/{id}/cancel` - Học viên hủy ca tập theo chính sách bồi thường
* `GET /api/v1/bookings/{id}/cancel-preview` - Xem trước hoàn tiền / phạt khi hủy
* `GET /api/v1/pt/bookings` - PT xem danh sách ca tập học viên đặt
* `PUT /api/v1/pt/bookings/{id}/confirm` - PT phê duyệt ca tập
* `PUT /api/v1/pt/bookings/{id}/reject` - PT từ chối ca tập kèm lý do
* `PUT /api/v1/pt/bookings/{id}/cancel` - PT hủy ca tập đã duyệt

### 4. Ví điện tử & Hợp đồng (Wallet & Enrollments - 7 endpoints)
* `GET /api/v1/wallet` - Xem số dư và lịch sử biến động ví
* `POST /api/v1/wallet/topup` - Nạp tiền vào ví điện tử
* `POST /api/v1/enrollments` - Mua khóa học & ký kết hợp đồng điện tử
* `GET /api/v1/enrollments/my` - Học viên xem danh sách hợp đồng
* `GET /api/v1/enrollments/{id}` - Xem chi tiết một hợp đồng
* `GET /api/v1/enrollments/{id}/contract` - Tải văn bản PDF hợp đồng đào tạo
* `GET /api/v1/pt/enrollments` - PT xem danh sách hợp đồng phụ trách

### 5. Giáo án tập luyện (Workout Plans - 6 endpoints)
* `POST /api/v1/pt/workout-plans` - PT tạo giáo án cho hợp đồng
* `POST /api/v1/pt/workout-plans/{id}/workouts` - PT thêm bài tập vào giáo án
* `GET /api/v1/enrollments/{id}/workout-plans` - Học viên xem giáo án của khóa
* `GET /api/v1/pt/workout-plans` - PT xem danh sách giáo án
* `DELETE /api/v1/pt/workout-plans/{id}` - PT xóa giáo án
* `DELETE /api/v1/pt/workout-plans/{planId}/workouts/{workoutId}` - PT xóa bài tập

### 6. Điểm danh & Đánh giá (Attendance & Reviews - 9 endpoints)
* `POST /api/v1/attendance/{bookingId}/start` - PT mở ca tập & phát mã OTP
* `POST /api/v1/attendance/{bookingId}/student-checkin` - Học viên nhập OTP điểm danh
* `POST /api/v1/attendance/{bookingId}/pt-confirm` - PT xác nhận hoàn thành buổi tập
* `POST /api/v1/attendance/{bookingId}/absent` - Điểm danh vắng mặt ca tập
* `GET /api/v1/attendance/{bookingId}` - Xem thông tin điểm danh của ca tập
* `POST /api/v1/reviews` - Học viên đánh giá sao và nhận xét buổi tập
* `GET /api/v1/reviews/pt/{ptId}` - Xem danh sách đánh giá của PT
* `GET /api/v1/reviews/my` - Xem các đánh giá của bản thân
* `GET /api/v1/reviews/booking/{bookingId}` - Xem đánh giá của một ca tập

### 7. Quản trị & Ví Doanh thu Sàn (Admin Management - 11 endpoints)
* `GET /api/v1/admin/users` - Danh sách người dùng hệ thống
* `PUT /api/v1/admin/users/{id}/status` - Khóa / Mở khóa tài khoản người dùng
* `GET /api/v1/admin/pt/pending` - Danh sách hồ sơ PT chờ duyệt
* `PUT /api/v1/admin/pt/{id}/approve` - Phê duyệt hồ sơ PT
* `PUT /api/v1/admin/pt/{id}/reject` - Từ chối hồ sơ PT kèm lý do
* `GET /api/v1/admin/statistics` - Thống kê doanh thu và tỷ lệ hoạt động
* `GET /api/v1/admin/bookings` - Danh sách booking toàn hệ thống
* `GET /api/v1/admin/bookings/page` - Phân trang booking toàn sàn
* `GET /api/v1/admin/payments` - Danh sách giao dịch toàn hệ thống
* `GET /api/v1/admin/payments/page` - Phân trang giao dịch thanh toán
* `GET /api/v1/admin/wallet` - Xem số dư ví doanh thu sàn Admin
* `POST /api/v1/admin/wallet/withdraw` - Admin rút doanh thu về tài khoản ngân hàng (0đ số dư tối thiểu)

### 8. Giải quyết tranh chấp & Khiếu nại (Dispute Resolution - 6 endpoints)
* `POST /api/v1/disputes` - Tạo đơn khiếu nại ca tập (Hạn 48h từ khi hủy, tối đa 1 lần/ca)
* `GET /api/v1/disputes` - Xem danh sách tranh chấp (theo quyền người dùng/Admin)
* `GET /api/v1/disputes/{id}` - Xem chi tiết hồ sơ khiếu nại và phản biện
* `POST /api/v1/disputes/{id}/counter` - Bên bị khiếu nại nộp văn bản & ảnh phản biện (48h)
* `POST /api/v1/disputes/{id}/request-evidence` - Admin yêu cầu bổ sung bằng chứng
* `POST /api/v1/disputes/{id}/resolve` - Admin ra phán quyết phân xử cuối cùng

---

## 5. Khởi Chạy & Kiểm Thử

### Chạy hệ thống với Docker Compose
```bash
docker compose -f docker-compose.python.yml up -d --build
```

### Chạy kiểm thử tự động (Pytest)
```bash
pytest -v
```

### Kiểm tra cú pháp và chất lượng mã nguồn (Ruff)
```bash
ruff check .
```
