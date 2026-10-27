# BÁO CÁO RÀ SOÁT BẢO MẬT TOÀN DIỆN & LỘ LỌT DỮ LIỆU
## (COMPREHENSIVE APPLICATION SECURITY & SECRETS AUDIT REPORT)

> **Dự án:** PT-Connect (Personal Trainer Marketplace System)  
> **Phiên bản rà soát:** Nhánh `develop`  
> **Thời điểm thực hiện:** 2026-10-28  
> **Phạm vi kiểm tra:** Toàn bộ source code Backend (Spring Boot 4.0.8), Frontend (Streamlit), Database Scripts, Docker / Compose, Lịch sử Git tracking và Cấu hình bảo mật hệ thống.  
> **Mục tiêu:** Rà soát và ngăn chặn rò rỉ Secrets, Credentials, PII và các lỗ hổng cấu hình trước khi Publish lên GitHub công khai.

---

## TỔNG KẾT BẢNG ĐÁNH GIÁ NGUY CƠ (EXECUTIVE SUMMARY)

| Mã | Phát hiện bảo mật | Mức độ | Trạng thái hiện tại | Vị trí / Tệp tin |
| :---: | :--- | :---: | :---: | :--- |
| **SEC-01** | **Khóa ký JWT Hardcode (Mặc định Fallback công khai)** | **NGHIÊM TRỌNG (Critical)** | Có nguy cơ lộ lọt | `application.yml`, `JwtUtil.java`, `application-test.yml` |
| **SEC-02** | **File hợp đồng PDF runtime vô tình bị commit vào Git** | **CAO (High)** | Đang bị theo dõi bởi Git | `backend/uploads/contracts/*.pdf` (5 tệp) |
| **SEC-03** | **Cấu hình CORS mở toang (`*`) đi kèm `allowCredentials(true)`** | **CAO (High)** | Lỗ hổng cấu hình | `SecurityConfig.java:51-54` |
| **SEC-04** | **API lấy toàn bộ danh sách User không giới hạn quyền Admin (BOLA / IDOR)** | **CAO (High)** | Thiếu phân quyền | `SecurityConfig.java:104`, `UserController.java:39` |
| **SEC-05** | **File `.gitignore` chưa chặn tệp upload và biến thể `.env`** | **TRUNG BÌNH (Medium)** | Thiếu quy tắc | `.gitignore`, `backend/.gitignore`, `.dockerignore` |
| **SEC-06** | **Mật khẩu cơ sở dữ liệu mặc định & kết nối tắt SSL** | **TRUNG BÌNH (Medium)** | Giá trị mặc định | `docker-compose.yml`, `application.yml` |
| **SEC-07** | **Dữ liệu Seed Demo dùng chung mật khẩu & hash tĩnh** | **THẤP (Low)** | Dữ liệu mẫu (Synthetic) | `database/seed_demo.sql`, `generate_data.py` |

---

## 1. RÀ SOÁT CẤU HÌNH & BIẾN MÔI TRƯỜNG (CONFIGURATION & SECRETS)

### 1.1. Khóa ký JWT (JWT Signing Secret) bị gán cứng mặc định
- **Vị trí phát hiện:**
  - `backend/src/main/resources/application.yml` (dòng 17):
    ```yaml
    jwt:
      secret: ${JWT_SECRET:404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970}
      expiration: ${JWT_EXPIRATION:86400000}
    ```
  - `backend/src/main/java/com/PTconnect/backend/config/JwtUtil.java` (dòng 21):
    ```java
    @Value("${jwt.secret:404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970}")
    private String secret;
    ```
  - `docker-compose.yml` (service `backend`, dòng 32-39):
    ```yaml
    backend:
      environment:
        DB_HOST: mysql
        DB_PORT: 3306
        DB_NAME: ${MYSQL_DATABASE:-ptconnect}
        DB_USER: ${MYSQL_USER:-ptuser}
        DB_PASSWORD: ${MYSQL_PASSWORD:-ptpassword}
        # KHÔNG HỀ TRUYỀN BIẾN JWT_SECRET!
    ```
- **Phân tích rủi ro:**
  - Chuỗi Hex `404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970` là một khóa mẫu 256-bit phổ biến trên mạng (thường gặp trong các bài hướng dẫn Spring Security mẫu).
  - Do `docker-compose.yml` không định nghĩa biến `JWT_SECRET`, khi ứng dụng khởi chạy trong môi trường container, Spring Boot sẽ **tự động fallback về chuỗi bí mật này**.
  - **Hậu quả:** Bất kỳ kẻ tấn công nào cũng có thể tự sinh một chuỗi JWT hợp lệ với `sub=admin@ptconnect.vn` và `role=ADMIN`, ký bằng chính khóa này để chiếm toàn quyền điều khiển hệ thống Backend mà không cần mật khẩu.
- **Biện pháp khắc phục khuyến nghị:**
  1. Loại bỏ fallback mặc định trong `JwtUtil.java`:
     ```java
     @Value("${jwt.secret}")
     private String secret;
     ```
  2. Bắt buộc truyền `JWT_SECRET` qua biến môi trường trong `docker-compose.yml`:
     ```yaml
     backend:
       environment:
         JWT_SECRET: ${JWT_SECRET}
     ```
  3. Bổ sung `JWT_SECRET=your_super_strong_random_secret_here` vào tệp `.env.example`.

---

### 1.2. Mật khẩu cơ sở dữ liệu mặc định & tham số kết nối tắt SSL
- **Vị trí phát hiện:**
  - `docker-compose.yml` (dòng 7-10):
    ```yaml
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root123}
    MYSQL_DATABASE: ${MYSQL_DATABASE:-ptconnect}
    MYSQL_USER: ${MYSQL_USER:-ptuser}
    MYSQL_PASSWORD: ${MYSQL_PASSWORD:-ptpassword}
    ```
  - `backend/src/main/resources/application.yml` (dòng 8):
    ```yaml
    url: jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME:ptconnect}?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Ho_Chi_Minh
    ```
- **Phân tích rủi ro:**
  - Fallback `root123` và `ptpassword` là mật khẩu yếu, dễ đoán. Khi chạy trên máy chủ thật nếu quên tạo `.env`, CSDL sẽ bị chiếm quyền dễ dàng.
  - Tham số `useSSL=false` làm cho luồng dữ liệu giữa Backend và MySQL truyền dạng plain-text (không mã hóa).
  - Tham số `allowPublicKeyRetrieval=true` tiềm ẩn nguy cơ bị khai thác bởi máy chủ MySQL giả mạo (Man-in-the-Middle Rogue MySQL Server).
- **Biện pháp khắc phục khuyến nghị:**
  - Xóa giá trị mặc định fallback trong môi trường Production; bắt buộc cấu hình mật khẩu mạnh qua `.env`.
  - Trên Production, bật `useSSL=true` và tắt `allowPublicKeyRetrieval=false`.

---

### 1.3. Khóa API bên thứ ba & Chứng chỉ SSL/TLS
- **Kết quả quét:**
  - AWS Access Keys (`AKIA...`): **Không tìm thấy (Sạch)**
  - Cloudinary / Firebase / Mailgun / SendGrid: **Không tìm thấy (Sạch)**
  - Google API Keys (`AIza...`): **Không tìm thấy (Sạch)**
  - File khóa riêng tư (`.pem`, `.key`, `.p12`, `.crt`): **Không tìm thấy (Sạch)**

---

## 2. RÀ SOÁT CẤU HÌNH KIỂM SOÁT PHIÊN BẢN (.GITIGNORE & GIT INDEX)

### 2.1. File PDF hợp đồng thực tế bị Commit vào Git Index (VI PHẠM NẶNG)
- **Vị trí phát hiện:**
  Qua lệnh kiểm tra `git ls-files`, 5 tệp hợp đồng PDF đang nằm trong chỉ mục của Git:
  ```text
  backend/uploads/contracts/contract_2.pdf
  backend/uploads/contracts/contract_3.pdf
  backend/uploads/contracts/contract_4.pdf
  backend/uploads/contracts/contract_6.pdf
  backend/uploads/contracts/contract_7.pdf
  ```
- **Lịch sử commit tạo ra:**
  - Commit `1bf6c67`: Thêm `contract_2.pdf`, `contract_3.pdf`
  - Commit `ee019ab`: Thêm `contract_4.pdf`
  - Commit `98d8707`: Thêm `contract_6.pdf`, `contract_7.pdf`
- **Nội dung bên trong các tệp PDF này:**
  - Được sinh tự động bởi [ContractPdfGenerator.java](file:///d:/PT-Connect/backend/src/main/java/com/PTconnect/backend/util/ContractPdfGenerator.java).
  - Chứa đầy đủ: Họ tên học viên, Họ tên PT, Số điện thoại hai bên, Email, Tên khóa học, Số tiền và Mã giao dịch tham chiếu.
- **Biện pháp xử lý ngay lập tức:**
  1. Xóa các tệp này khỏi Git index (nhưng vẫn giữ lại trên đĩa nếu cần demo):
     ```bash
     git rm --cached -r backend/uploads/
     ```
  2. Bổ sung thư mục `uploads/` vào `.gitignore`.

---

### 2.2. Đánh giá tệp cấu hình `.gitignore`
Hiện dự án có 2 tệp `.gitignore`:
1. **Tại thư mục gốc (`.gitignore`):**
   ```gitignore
   # Secrets
   .env

   # Java / Maven
   backend/target/
   *.class

   # Python
   __pycache__/
   *.pyc
   venv/
   .venv/

   # IDE / OS
   .idea/
   .vscode/
   *.iml
   .DS_Store

   # Static avatars uploads
   frontend/static/avatars/*
   !frontend/static/avatars/.gitkeep
   ```
2. **Tại thư mục Backend (`backend/.gitignore`):**
   Chứa các quy tắc cho Eclipse, NetBeans, IntelliJ, target/.

**Các lỗ hổng cần bổ sung ngay vào `.gitignore` gốc:**
- **Chưa chặn các biến thể `.env`:** Chỉ chặn `.env`, chưa chặn `.env.*` (như `.env.local`, `.env.prod`, `.env.production`).
- **Chưa chặn thư mục uploads của Backend:** `backend/uploads/` và `uploads/`.
- **Chưa chặn file chứng chỉ / khóa bảo mật:** `*.pem`, `*.key`, `*.p12`, `*.jks`, `*.crt`.
- **Chưa chặn tệp log:** `*.log`, `logs/`.
- **Chưa chặn tệp tạm của Windows / macOS:** `Thumbs.db`, `desktop.ini`.

---

### 2.3. Rà soát `.dockerignore`
- `backend/.dockerignore`: Mới chỉ có `target/`, `.git`, `.idea`. Cần thêm `uploads/` và `.env*` để tránh việc build image kéo theo dữ liệu nhạy cảm vào Docker Image.
- `frontend/.dockerignore`: Cần thêm `static/avatars/*.jpg` (chỉ giữ `.gitkeep`) và `.env*`.

---

## 3. RÀ SOÁT DỮ LIỆU NGƯỜI DÙNG & BẢO MẬT API (DATA & API SECURITY)

### 3.1. Dữ liệu hạt giống (Seed Demo Data)
- **Kiểm tra tệp:** `database/seed_demo.sql` và `frontend/tools/generate_data.py`.
- **Dữ liệu tài khoản:**
  - 1 tài khoản `ADMIN`: `admin@ptconnect.vn`
  - 8 tài khoản `PT`: `pt.hoangc@ptconnect.vn`, `pt.minhd@ptconnect.vn`, v.v.
  - 25 tài khoản `STUDENT`: `student.a@ptconnect.vn`, `student_02@ptconnect.vn`, v.v.
- **Mật khẩu & Hash:**
  - Mật khẩu đăng nhập mặc định: `Password123@`
  - Chuỗi băm BCrypt: `$2b$10$pPC4wbKRgav.Qmi2TZEG7eQtYe2iyNDtD8Jf97rBnY95DelG056Gq`
- **Đánh giá PII:**
  - Số điện thoại đều là dãy số giả lập tuần tự: `0900000000`, `0900000001`, `0910000002`...
  - Email thuộc domain giả định `@ptconnect.vn`.
  - Không có số CMND/CCCD thật, không có số thẻ ngân hàng thật.
  - **Kết luận:** Dữ liệu hoàn toàn là Synthetic Mock Data, không vi phạm PII thực tế.

---

### 3.2. Lỗ hổng Broken Object Level Authorization (BOLA) trên `GET /api/v1/users`
- **Vị trí phát hiện:**
  - `SecurityConfig.java` (dòng 104):
    ```java
    .requestMatchers("/api/v1/users/**", "/api/users/**").authenticated()
    ```
  - `UserController.java` (dòng 21-28):
    ```java
    @GetMapping
    public ResponseEntity<ApiResponse<List<UserDTO>>> getUsers(@RequestParam(required = false) Role role) {
        List<UserDTO> users = (role != null) ? userService.getUsersByRole(role) : userService.getAllUsers();
        return ResponseEntity.ok(ApiResponse.success(users));
    }
    ```
- **Phân tích nguy cơ:**
  - Endpoint `GET /api/v1/users` chỉ yêu cầu `.authenticated()`, nghĩa là **bất kỳ ai có tài khoản (kể cả Học viên hoặc Huấn luyện viên thông thường) đều có thể gọi API này**.
  - Khi gọi, hệ thống trả về toàn bộ danh sách người dùng bao gồm: `id`, `fullName`, `email`, `phone`, `role`, `status`, `avatarUrl`.
  - Đây là lỗi rò rỉ dữ liệu danh bạ người dùng (User Enumeration & Data Leakage).
- **Khắc phục:**
  - Cần nâng quyền cho endpoint lấy danh sách người dùng lên `hasRole('ADMIN')`:
    ```java
    .requestMatchers(HttpMethod.GET, "/api/v1/users", "/api/users").hasRole("ADMIN")
    ```

---

### 3.3. Lỗ hổng CORS Wildcard với AllowCredentials (`CORS Misconfiguration`)
- **Vị trí phát hiện:**
  - `SecurityConfig.java` (dòng 50-54):
    ```java
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOriginPatterns(List.of("*"));
    configuration.setAllowCredentials(true);
    ```
- **Phân tích nguy cơ:**
  - Khi kết hợp `allowedOriginPatterns("*")` với `allowCredentials(true)`, trình duyệt sẽ chấp nhận mọi yêu cầu AJAX từ bất kỳ website nào gửi đến Backend kèm thông tin xác thực.
  - Trang web độc hại có thể lợi dụng điều này để đọc trộm dữ liệu API của người dùng đã đăng nhập nếu người dùng truy cập trang đó (Cross-Origin Data Theft).
- **Khắc phục:**
  - Giới hạn các origin cụ thể (ví dụ: `http://localhost:8501`, `http://127.0.0.1:8501` hoặc domain chính thức).

---

## 4. BẢNG CHECKLIST HÀNH ĐỘNG KHUYẾN NGHỊ TRƯỚC KHI PUSH CODE

| STT | Hành động cần thực hiện | Mức ưu tiên | Lệnh / File thực hiện |
| :---: | :--- | :---: | :--- |
| 1 | **Gỡ bỏ 5 file contract PDF khỏi Git tracking** | **Khẩn cấp** | `git rm --cached backend/uploads/contracts/*.pdf` |
| 2 | **Cập nhật `.gitignore` toàn diện** | **Khẩn cấp** | Thêm `backend/uploads/`, `.env.*`, `*.key`, `*.pem`, `*.log` vào `.gitignore` |
| 3 | **Cấu hình chặt chẽ `SecurityConfig.java`** | **Cao** | Đổi rule `GET /api/v1/users` thành `hasRole('ADMIN')`; siết CORS origins |
| 4 | **Bổ sung `JWT_SECRET` vào `.env.example` & `docker-compose.yml`** | **Cao** | Truyền biến `JWT_SECRET` qua container environment |
| 5 | **Cập nhật `.dockerignore` cho cả 2 module** | **Trung bình** | Thêm `uploads/` và `.env*` vào `backend/.dockerignore` & `frontend/.dockerignore` |

---
*Báo cáo được hoàn thiện và xuất bản tự động phục vụ mục đích kiểm toán an toàn thông tin dự án PT-Connect.*
