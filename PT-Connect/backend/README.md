# Backend Project Documentation

## 1. Tổng quan

Thư mục `backend` chứa ứng dụng Spring Boot cho hệ thống PT Connect. Hiện tại, backend tập trung chủ yếu vào tầng dữ liệu và model domain:

- JPA Entity
- Repository layer
- Spring Boot bootstrap
- Cấu hình kết nối MySQL
- Container hóa với Docker

Dữ liệu hiện có trong backend chưa có `controller`, `service`, `dto` hay `security` custom class rõ ràng; tệp đang tập trung nhiều vào mô hình dữ liệu và truy vấn JPA.

## 2. Cấu trúc thư mục

```text
backend/
├── .dockerignore
├── .gitattributes
├── .gitignore
├── .mvn/
│   └── wrapper/
│       ├── maven-wrapper.jar
│       └── maven-wrapper.properties
├── Dockerfile
├── mvnw
├── mvnw.cmd
├── pom.xml
├── README.md
├── src/
│   └── main/
│       ├── java/com/ptconnect/
│       │   ├── BackendApplication.java
│       │   ├── entity/
│       │   │   ├── Admin.java
│       │   │   ├── PT.java
│       │   │   ├── PTProfile.java
│       │   │   ├── Student.java
│       │   │   ├── User.java
│       │   │   ├── Wallet.java
│       │   │   └── enums/
│       │   │       ├── Role.java
│       │   │       ├── UserStatus.java
│       │   │       ├── VerificationStatus.java
│       │   │       └── WalletStatus.java
│       │   └── repository/
│       │       ├── PTProfileRepository.java
│       │       ├── UserRepository.java
│       │       └── WalletRepository.java
│       └── resources/
│           └── application.yml
└── target/   (build output tự sinh)
```

## 3. Mô tả từng file

### `pom.xml`

File cấu hình Maven cho project Spring Boot.

- Parent: `org.springframework.boot:spring-boot-starter-parent` version `4.0.8`
- Java target: `17`
- Dependencies chính:
  - `spring-boot-starter-data-jpa`
  - `spring-boot-starter-security`
  - `spring-boot-starter-web`
  - `spring-boot-starter-validation`
  - `mysql-connector-j`
  - `lombok`
  - `spring-boot-starter-test`
  - `spring-boot-starter-security-test`

Vai trò: định nghĩa toàn bộ dependency, plugin build và cấu hình annotation processor cho Lombok.

### `application.yml`

File cấu hình môi trường của Spring Boot.

- Kết nối MySQL qua các biến môi:
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
- Mặc định:
  - host: `localhost`
  - port: `3306`
  - db: `pt_marketplace`
  - user: `root`
  - password: rỗng
- `hibernate.ddl-auto: none` nghĩa là schema không được tự tạo/sửa bởi Hibernate.
- `open-in-view: false` giúp tránh lazy loading ngoài transaction.

### `BackendApplication.java`

Lớp bootstrap của Spring Boot.

- Khởi chạy ứng dụng bằng `SpringApplication.run(...)`
- Đánh dấu bằng `@SpringBootApplication`
- Đây là entry point của backend.

### `src/main/java/com/ptconnect/entity/User.java`

Lớp cơ sở cho tất cả tài khoản trong hệ thống.

- Là `@Entity`
- Mapping table `users`
- Dùng `SINGLE_TABLE` inheritance với discriminator column `role`
- `role` được lưu ở cột `role` và không cho insert/update trực tiếp trong entity
- Các trường chính:
  - `id`
  - `fullName`
  - `email`
  - `passwordHash`
  - `phone`
  - `role`
  - `status`
  - `avatarUrl`
  - `createdAt`
  - `updatedAt`
- Có các phương thức abstract:
  - `getHomePage()`
  - `getDisplayRole()`

Mô hình này cho phép có nhiều loại user như `Student`, `PT`, `Admin` trong cùng bảng `users`.

### `src/main/java/com/ptconnect/entity/Student.java`

Lớp đại diện cho học viên.

- Kế thừa từ `User`
- `@DiscriminatorValue("STUDENT")`
- Override:
  - `getHomePage() -> "STUDENT_HOME"`
  - `getDisplayRole() -> "Học viên"`

### `src/main/java/com/ptconnect/entity/PT.java`

Lớp đại diện cho huấn luyện viên / PT.

- Kế thừa từ `User`
- `@DiscriminatorValue("PT")`
- Có quan hệ 1-1 với `PTProfile` thông qua `mappedBy = "pt"`
- Override:
  - `getHomePage() -> "PT_DASHBOARD"`
  - `getDisplayRole() -> "Huấn luyện viên"`

### `src/main/java/com/ptconnect/entity/Admin.java`

Lớp đại diện cho quản trị viên.

- Kế thừa từ `User`
- `@DiscriminatorValue("ADMIN")`
- Override:
  - `getHomePage() -> "ADMIN_DASHBOARD"`
  - `getDisplayRole() -> "Quản trị viên"`

### `src/main/java/com/ptconnect/entity/PTProfile.java`

Entity mô tả hồ sơ chi tiết của PT.

- Mapping table `pt_profiles`
- Quan hệ 1-1 với `PT` thông qua `@OneToOne` với `user_id` unique
- Các trường chính:
  - `bio`
  - `experienceYears`
  - `availableLocations`
  - `locationPricingNote`
  - `certificateUrls` (JSON string)
  - `averageRating` (read-only, DB trigger cập nhật)
  - `totalReviews` (read-only)
  - `verificationStatus`
  - `createdAt`, `updatedAt`

Vai trò: lưu hồ sơ chuyên môn và trạng thái xác minh của PT.

### `src/main/java/com/ptconnect/entity/Wallet.java`

Entity mô tả ví tiền của người dùng.

- Mapping table `wallets`
- Quan hệ 1-1 với `User`
- Trường chính:
  - `balance`
  - `lockedBalance`
  - `currency` mặc định `VND`
  - `status`
- Có các phương thức nghiệp vụ:
  - `credit(BigDecimal amount)`
  - `debit(BigDecimal amount)`
- Logic kiểm tra:
  - ví phải ở trạng thái `ACTIVE`
  - số tiền phải > 0
  - `debit` không cho phép số dư âm

Đây là nơi chứa logic nghiệp vụ của ví, thay vì để logic đó ở service layer.

### `src/main/java/com/ptconnect/entity/enums/Role.java`

Enum vai trò người dùng:

```java
STUDENT, PT, ADMIN
```

### `src/main/java/com/ptconnect/entity/enums/UserStatus.java`

Enum trạng thái tài khoản người dùng:

```java
ACTIVE, PENDING, SUSPENDED
```

### `src/main/java/com/ptconnect/entity/enums/VerificationStatus.java`

Enum trạng thái xác minh hồ sơ PT:

```java
PENDING, VERIFIED, REJECTED
```

### `src/main/java/com/ptconnect/entity/enums/WalletStatus.java`

Enum trạng thái ví:

```java
ACTIVE, FROZEN
```

### `src/main/java/com/ptconnect/repository/UserRepository.java`

Repository cho entity `User`.

Các method chính:
- `findByEmail(String email)`
- `existsByEmail(String email)`
- `existsByPhone(String phone)`
- `findByRole(Role role)`

Dùng để truy vấn tài khoản người dùng theo email, phone, vai trò.

### `src/main/java/com/ptconnect/repository/PTProfileRepository.java`

Repository cho `PTProfile` với truy vấn nâng cao.

Các method chính:
- `findVerifiedAndActivePTs(...)`:
  - lọc PT có `verificationStatus` và `pt.status`
  - dùng cho danh sách PT đã xác minh và active
- `searchVerifiedPTs(...)`:
  - tìm PT theo tên và trạng thái
- `findByVerificationStatus(...)`
- `findByPtId(Long userId)`

Các query dùng JPQL với `@Query`.

### `src/main/java/com/ptconnect/repository/WalletRepository.java`

Repository cho `Wallet`.

- `findByUserId(Long userId)`: tra cứu ví theo user id

### `Dockerfile`

Dockerfile multi-stage để build và chạy ứng dụng Java.

- Stage 1: build jar bằng Maven
- Stage 2: chạy ứng dụng bằng JRE 17
- Expose port `8080`
- Command chạy cuối: `java -jar app.jar`

### `.dockerignore`

Loại trừ file không cần copy vào build Docker, gồm:
- `target/`
- `.git`
- `.idea`

### `.gitignore`

Cấu hình Git loại bỏ các file build, IDE và artifact tạm từ project Java/Spring Boot.

### `.gitattributes`

File cấu hình quy tắc xử lý line endings / attributes Git. Hiện tại chưa có nội dung cụ thể trong repo.

### `.mvn/wrapper/maven-wrapper.properties`

Cấu hình Maven Wrapper. Chỉ định:
- wrapper version `3.3.4`
- distribution type: `only-script`
- Maven version: `3.9.16`

### `mvnw` / `mvnw.cmd`

Các script wrapper giúp chạy Maven mà không cần cài đặt Maven hệ thống.

- `mvnw`: dùng cho Unix/Linux/macOS
- `mvnw.cmd`: dùng cho Windows

## 4. Mối quan hệ chính giữa các entity

- `User` là lớp cha của `Student`, `PT`, `Admin`
- `PT` có `PTProfile` 1-1
- `Wallet` thuộc về 1 `User`
- `User` dùng discriminator column `role` để phân loại trong cùng bảng `users`

## 5. Kết luận

Backend hiện tại đang ở giai đoạn xây dựng mô hình dữ liệu nền tảng cho hệ thống PT Connect. Trọng tâm là:

- định nghĩa `User` và các role
- mô hình PT profile
- ví tiền và trạng thái
- truy vấn JPA cho dữ liệu người dùng và PT

Hiện chưa thấy các module API (Controller), business service, authentication flow thực thi rõ ràng và cả project đang chưa có `DTO` hoặc `config/security` custom.

## 6. Cách chạy project

Trong thư mục `backend`, có thể dùng:

```bash
./mvnw clean install
./mvnw spring-boot:run
```

Hoặc với Docker:

```bash
docker build -t ptconnect-backend .
docker run -p 8080:8080 --env-file .env ptconnect-backend
```

Lưu ý: cần cấu hình biến môi MySQL như `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` trước khi chạy ứng dụng.
