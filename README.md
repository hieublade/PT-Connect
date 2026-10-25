# PT Connect - Nền tảng kết nối Huấn luyện viên cá nhân & Học viên

PT Connect là nền tảng quản trị và kết nối trực tuyến giữa **Học viên (Student)** và **Huấn luyện viên cá nhân (Personal Trainer - PT)**. Hệ thống giải quyết trọn vẹn luồng nghiệp vụ thể hình: tìm kiếm PT theo khu vực/chuyên môn, đặt lịch tập thử, nạp ví mua khóa học, tự động xuất hợp đồng điện tử PDF, điểm danh hai phía bằng mã OTP, đánh giá chất lượng tự động qua MySQL Trigger và bảng điều khiển phân tích dữ liệu chuyên sâu cho Quản trị viên.

---

## Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ | Chi tiết |
| :--- | :--- | :--- |
| **Backend** | Java 17 / Spring Boot 3.3.4 | Spring Data JPA, Spring Security, JJWT, OpenPDF (Xuất hợp đồng), RESTful API |
| **Frontend** | Python 3.11 / Streamlit 1.38 | Giao diện tương tác trực quan, Plotly & Pandas (Dashboard phân tích Admin) |
| **Database** | MySQL 8.0 | Ràng buộc toàn vẹn dữ liệu (CHECK, FK, UNIQUE), Triggers, Views, utf8mb4 |
| **DevOps** | Docker & Docker Compose | Multi-stage build, container hóa toàn bộ 3 dịch vụ, Healthcheck & Volume đồng bộ |

---

## Cấu trúc thư mục dự án

```text
PT-Connect/
├── backend/                  # Mã nguồn Spring Boot REST API
│   ├── src/                  # Controllers, Services, Entities, Repositories, Utils
│   ├── Dockerfile            # Multi-stage build (Maven compile -> JRE 17 runtime)
│   └── pom.xml               # Quản lý dependencies Java
├── frontend/                 # Giao diện web Streamlit & Phân tích dữ liệu
│   ├── pages/                # Giao diện theo vai trò (Login, Student, PT, Admin)
│   ├── api/                  # HTTP Client kết nối tới Spring Boot REST API
│   ├── analytics/            # Biểu đồ Plotly & thống kê Pandas
│   ├── tools/                # Script sinh dữ liệu mẫu hợp lệ (generate_data.py)
│   ├── Dockerfile            # Container chạy Streamlit trên nền python:3.11-slim
│   └── requirements.txt      # Thư viện Python đã ghim phiên bản
├── database/                 # Cơ sở dữ liệu MySQL
│   ├── init.sql              # Khởi tạo Schema DDL, bảng, khóa ngoại, chỉ mục
│   ├── trigger.sql           # Trigger tự động tính rating trung bình và tổng review
│   └── seed_demo.sql         # Dữ liệu mẫu demo đã sinh sẵn
├── docker-compose.yml        # Điều phối 3 container: mysql, backend, frontend
├── .env.example              # Cấu hình biến môi trường mẫu
└── README.md                 # Hướng dẫn chi tiết vận hành dự án
```

---

## Hướng dẫn cài đặt Docker Desktop & Thiết lập dự án (Chi tiết từ A-Z)

Dự án PT Connect đã được container hóa 100% bằng **Docker & Docker Compose**. Bạn **không cần** cài đặt trước Java, Maven, Python hay MySQL trên máy tính. Toàn bộ môi trường sẽ được Docker tự động tải, biên dịch và vận hành khép kín.

---

### PHẦN 1: Hướng dẫn cài đặt Docker Desktop

#### 1. Cài đặt trên hệ điều hành Windows (Khuyến nghị WSL 2)

##### Bước 1.1: Kiểm tra tính năng ảo hóa phần cứng (Hardware Virtualization)
1. Mở **Task Manager** (nhấn tổ hợp phím `Ctrl + Shift + Esc`).
2. Chọn tab **Performance** -> chọn mục **CPU**.
3. Nhìn xuống góc dưới bên phải, kiểm tra dòng **Virtualization**:
   - Nếu hiển thị **Enabled**: Máy đã sẵn sàng.
   - Nếu hiển thị **Disabled**: Cần khởi động lại máy vào BIOS/UEFI (nhấn phím `F2`, `F10`, `Del` tùy dòng máy) và bật tính năng **Intel Virtualization Technology (VT-x)** hoặc **AMD-V / SVM Mode**.

##### Bước 1.2: Kích hoạt WSL 2 (Windows Subsystem for Linux)
1. Mở menu Start, tìm kiếm **PowerShell**, nhấp chuột phải và chọn **Run as Administrator**.
2. Nhập lệnh sau để tự động cài đặt và cập nhật WSL:
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```
3. Khởi động lại máy tính (Restart) nếu Windows yêu cầu.

##### Bước 1.3: Tải và cài đặt Docker Desktop
1. Truy cập trang tải chính thức của Docker: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) (hoặc tải trực tiếp bản Windows x86_64).
2. Chạy file `Docker Desktop Installer.exe` vừa tải về.
3. Trong màn hình cấu hình cài đặt:
   - Tích chọn **"Use WSL 2 instead of Hyper-V (recommended)"**.
   - Tích chọn **"Add shortcut to desktop"** để tiện mở ứng dụng.
4. Nhấn **OK** và chờ quá trình giải nén, cài đặt hoàn tất.
5. Nhấn **Close and restart** để hoàn tất cài đặt.

##### Bước 1.4: Khởi chạy và thiết lập Docker Desktop
1. Mở ứng dụng **Docker Desktop** từ màn hình Desktop hoặc menu Start.
2. Cửa sổ **Docker Subscription Service Agreement** xuất hiện -> chọn **Accept**.
3. Bạn có thể chọn **Continue without signing in** (không bắt buộc đăng nhập tài khoản Docker Hub).
4. Quan sát góc dưới bên trái của cửa sổ Docker Desktop: Khi biểu tượng hiển thị **Engine running** màu xanh lá cây là Docker đã hoạt động ổn định.
5. *(Khuyên dùng)* Nhấp vào biểu tượng bánh răng **Settings** ở góc trên -> vào tab **General** -> tích chọn **"Start Docker Desktop when you log in"** để Docker tự động chạy khi khởi động máy.

---

#### 2. Cài đặt trên hệ điều hành macOS

1. Truy cập [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/).
2. Chọn phiên bản tương thích với chip máy của bạn:
   - **Mac with Apple Silicon** (chip M1, M2, M3, M4...).
   - **Mac with Intel chip**.
3. Mở file `.dmg` đã tải về và kéo biểu tượng **Docker.app** vào thư mục **Applications**.
4. Mở **Docker** từ Launchpad hoặc Spotlight, cấp quyền bảo mật khi macOS hỏi (`Privileged Helper Tool`).
5. Đợi Docker Desktop hiển thị trạng thái **Engine running**.

---

#### 3. Cài đặt trên Linux (Ubuntu / Debian)

Nếu sử dụng Ubuntu/Debian Server hoặc Desktop:
```bash
# Cài đặt Docker Engine & Docker Compose Plugin chính thức
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Cấp quyền chạy docker không cần sudo:
sudo usermod -aG docker $USER
newgrp docker
```

---

#### 4. Kiểm tra môi trường Docker đã sẵn sàng

Mở Terminal (trên Linux/macOS) hoặc PowerShell/CMD (trên Windows) và chạy lệnh:
```bash
docker --version
docker compose version
```
*Kết quả xuất hiện phiên bản Docker (ví dụ: `Docker version 27.x.x...`) và Docker Compose (ví dụ: `Docker Compose version v2.x.x...`) là thành công.*

---

### PHẦN 2: Thiết lập dự án & Khởi chạy hệ thống PT Connect

#### Bước 1: Mở thư mục dự án
Mở cửa sổ dòng lệnh (PowerShell, CMD hoặc Terminal) và di chuyển vào thư mục dự án:
```bash
cd d:/PT-Connect
# hoặc đường dẫn thực tế nơi bạn lưu dự án
```

#### Bước 2: Khởi tạo file cấu hình biến môi trường (.env)
Dự án cung cấp sẵn file `.env.example` với các thông số mặc định an toàn. Tạo file cấu hình `.env`:

* **Trên Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
* **Trên Linux / macOS / Git Bash / CMD:**
  ```bash
  cp .env.example .env
  ```

> **Chi tiết các biến môi trường trong file `.env`:**
> * `MYSQL_ROOT_PASSWORD`: Mật khẩu của tài khoản `root` MySQL (mặc định: `root123`).
> * `MYSQL_DATABASE`: Tên cơ sở dữ liệu dự án (mặc định: `ptconnect`).
> * `MYSQL_USER`: Tên tài khoản database cho backend kết nối (mặc định: `ptuser`).
> * `MYSQL_PASSWORD`: Mật khẩu kết nối database (mặc định: `ptpassword`).
>
> *(Lưu ý: Nếu bạn không tạo file `.env`, hệ thống sẽ tự động sử dụng cấu hình mặc định sẵn có trong `docker-compose.yml` mà không gặp bất kỳ lỗi nào).*

#### Bước 3: Khởi chạy toàn bộ hệ thống bằng 1 lệnh duy nhất

Chạy lệnh Docker Compose để build và khởi động 3 container ngầm:
```bash
docker compose up -d --build
```

**Quá trình tự động diễn ra:**
1. **Container `ptconnect-mysql` (MySQL 8.0):** Tải image MySQL, cấu hình bảng mã tiếng Việt `utf8mb4_unicode_ci`, tự động nạp cấu trúc Schema (`01_init.sql`) và bộ Trigger nghiệp vụ (`02_trigger.sql`). Dữ liệu mẫu demo mở rộng (`seed_demo.sql`) có thể nạp riêng khi cần.
2. **Container `ptconnect-backend` (Spring Boot 3.3.4):** Chạy quy trình Multi-stage build (tải dependencies Maven, biên dịch source code Java 17 thành file `app.jar` và chạy trên nền Java Runtime nhẹ). Container tự động chờ MySQL hoàn toàn **Healthy** mới khởi động.
3. **Container `ptconnect-frontend` (Streamlit Python 3.11):** Cài đặt các thư viện trực quan hóa dữ liệu và kết nối an toàn tới Backend.

> ⏱️ **Thời gian khởi tạo lần đầu:** Quá trình tải các images và build Maven lần đầu tiên sẽ mất khoảng **2 - 4 phút** tùy thuộc vào tốc độ mạng. Ở các lần khởi động tiếp theo chỉ mất khoảng **5 - 10 giây**.

#### Bước 4: Kiểm tra trạng thái các container

Sau khi lệnh trên hoàn tất, kiểm tra danh sách dịch vụ đang chạy:
```bash
docker compose ps
```
Bảng trạng thái tiêu chuẩn sẽ như sau:
```text
NAME                 IMAGE                   COMMAND                  SERVICE    STATUS
ptconnect-mysql      mysql:8.0               "docker-entrypoint.s…"   mysql      Up (healthy)
ptconnect-backend    pt-connect-backend      "java -jar app.jar"      backend    Up
ptconnect-frontend   pt-connect-frontend     "streamlit run app.p…"   frontend   Up
```

---

### PHẦN 3: Cổng truy cập dịch vụ & Sử dụng hệ thống

Khi cả 3 container ở trạng thái `Up`:

| Dịch vụ | Địa chỉ truy cập | Ghi chú |
| :--- | :--- | :--- |
| **Giao diện Web (Streamlit)** | **[http://localhost:8501](http://localhost:8501)** | Giao diện chính cho Học viên, PT và Admin |
| **Backend REST API** | **[http://localhost:8080](http://localhost:8080)** | Máy chủ API Spring Boot & Endpoints |
| **Cơ sở dữ liệu MySQL** | **`localhost:3307`** | Kết nối qua DBeaver, DataGrip, HeidiSQL hoặc MySQL Workbench |

---

## Tài khoản kiểm thử hệ thống (Demo Credentials)

Sau khi mở giao diện tại [http://localhost:8501](http://localhost:8501), bạn nhập trực tiếp **Email** và **Mật khẩu** tương ứng vào form Đăng nhập:

> 🔑 **Mật khẩu dùng chung cho tất cả tài khoản mẫu:** **`Password123@`**

| Vai trò | Email đăng nhập | Tên người dùng | Mục đích kiểm thử tính năng |
| :--- | :--- | :--- | :--- |
| 🛡️ **Quản trị viên** | `admin@ptconnect.vn` | Quản Trị Viên Hệ Thống | Duyệt/từ chối hồ sơ PT, theo dõi Dashboard doanh thu & biểu đồ phân tích |
| 🏋️ **Huấn luyện viên** | `pt.hoangc@ptconnect.vn` | Lê Hoàng Cường | PT đã duyệt (`VERIFIED`), xem lịch dạy, xác nhận booking, mở slot rảnh |
| ⏳ **Huấn luyện viên** | `pt.hoangnam@ptconnect.vn` | Vũ Hoàng Nam | PT đang chờ duyệt (`PENDING`) dùng để test tính năng Admin phê duyệt |
| 🏃 **Học viên** | `student.a@ptconnect.vn` | Nguyễn Văn A | Đã có sẵn số dư ví, hợp đồng PDF, lịch tập; test đặt lịch, thanh toán, điểm danh OTP |

*Bạn cũng có thể chuyển sang tab **"Đăng ký tài khoản"** để tự tạo tài khoản Học viên hoặc PT mới hoàn toàn.*

---

## Nạp lại dữ liệu mẫu Demo (Seed Data Generator)

Hệ thống có sẵn script Python độc lập tự động sinh dữ liệu thực tế, chuẩn ràng buộc Foreign Key và giữ nguyên 100% font tiếng Việt có dấu.

Nếu bạn muốn nạp bộ dữ liệu demo đầy đủ có sẵn:
```bash
# Trên Windows PowerShell:
Get-Content ./database/seed_demo.sql -Encoding UTF8 | docker exec -i ptconnect-mysql mysql -uroot -proot123 --default-character-set=utf8mb4 ptconnect

# Trên Linux / macOS / Git Bash:
docker exec -i ptconnect-mysql mysql -uroot -proot123 ptconnect < database/seed_demo.sql
```

Hoặc sinh lại một bộ dữ liệu hoàn toàn mới bằng script Python:
```bash
python frontend/tools/generate_data.py
```
*Script sẽ tự động tạo hơn 30 học viên, 8 huấn luyện viên, 180 khung giờ tập, hợp đồng, thanh toán ví và nạp trực tiếp vào container MySQL `ptconnect-mysql`.*

---

## Luồng nghiệm thu kiểm thử hoàn chỉnh (10 bước)

1. **Duyệt PT:** Admin đăng nhập (`admin@ptconnect.vn`), vào mục Quản trị để duyệt hồ sơ PT mới (`pt.hoangnam@ptconnect.vn`) từ trạng thái `PENDING` sang `VERIFIED`.
2. **Tạo lịch & khóa học:** PT đăng nhập, cấu hình khóa học thể hình và thêm các khung giờ rảnh (Availability Slots).
3. **Tìm kiếm PT:** Học viên đăng nhập, tra cứu PT theo bộ lọc chuyên môn, khu vực, xem đánh giá sao và lịch rảnh.
4. **Học thử (Trial Booking):** Học viên đặt lịch học thử → Trạng thái `PENDING` → PT vào xác nhận → `CONFIRMED`.
5. **Nạp tiền & Mua khóa học:** Học viên nạp tiền vào ví điện tử, thực hiện thanh toán khóa học trọn gói.
6. **Hợp đồng điện tử:** Hệ thống tự động sinh mã giao dịch và xuất file hợp đồng điện tử PDF có giá trị lưu trữ. Học viên tải và xem PDF trực tiếp trên web.
7. **Đặt ca theo gói:** Học viên đặt lịch các buổi tập theo khóa đã mua → Hệ thống tự động trừ số buổi còn lại (`remaining_sessions`).
8. **Điểm danh hai phía bằng OTP:** Khi ca tập diễn ra, hai bên nhập mã xác thực OTP ngẫu nhiên để hoàn thành ca tập → Chuyển trạng thái sang `COMPLETED`.
9. **Đánh giá & Kích hoạt Trigger:** Học viên viết đánh giá 5 sao → MySQL Trigger tự động tính lại `average_rating` và tăng `total_reviews` trên hồ sơ PT ngay lập tức.
10. **Dashboard thống kê:** Admin xem báo cáo trực quan hóa với Plotly (Tỷ lệ hoàn thành ca tập, doanh thu sàn, phân bổ trạng thái booking theo thời gian thực).

---

## Các lệnh Docker quản trị & Vận hành hữu ích

* **Xem log toàn bộ hệ thống theo thời gian thực:**
  ```bash
  docker compose logs -f
  ```
* **Xem log riêng của từng dịch vụ:**
  ```bash
  # Xem log Backend Spring Boot:
  docker compose logs -f backend

  # Xem log Frontend Streamlit:
  docker compose logs -f frontend

  # Xem log Database MySQL:
  docker compose logs -f mysql
  ```
* **Tạm dừng hệ thống (giữ nguyên dữ liệu):**
  ```bash
  docker compose stop
  ```
* **Khởi động lại hệ thống sau khi tạm dừng:**
  ```bash
  docker compose start
  ```
* **Tắt và dọn dẹp các container:**
  ```bash
  docker compose down
  ```
* **Xóa sạch và reset toàn bộ database về trạng thái ban đầu:**
  ```bash
  docker compose down -v
  docker compose up -d --build
  ```

---

## Xử lý sự cố thường gặp (Troubleshooting & FAQs)

### 1. Lỗi `docker: Cannot connect to the Docker daemon` hoặc `error during connect`
* **Nguyên nhân:** Ứng dụng Docker Desktop chưa được mở hoặc dịch vụ Docker daemon đang trong quá trình khởi động.
* **Cách khắc phục:** Mở ứng dụng **Docker Desktop**, chờ 15-30 giây cho đến khi biểu tượng góc dưới chuyển sang màu xanh **Engine running**, sau đó chạy lại lệnh terminal.

### 2. Lỗi xung đột cổng mạng (Port is already allocated / Bind failed)
* **Xung đột cổng 3307 (MySQL):** Nếu trên máy tính của bạn đã có một dịch vụ MySQL khác chiếm cổng 3307, mở file `docker-compose.yml`, tìm dòng `- "3307:3306"` và sửa thành `- "3308:3306"`.
* **Xung đột cổng 8080 (Backend):** Nếu cổng 8080 bị phần mềm khác (như Tomcat, Jenkins) sử dụng, sửa thành `- "8081:8080"` trong `docker-compose.yml`.
* **Xung đột cổng 8501 (Frontend):** Sửa thành `- "8502:8501"` trong `docker-compose.yml`.

### 3. Lỗi `WSL 2 installation is incomplete` trên Windows
* **Cách khắc phục:** Mở PowerShell với quyền Administrator và chạy lệnh:
  ```powershell
  wsl --update
  wsl --shutdown
  ```
  Sau đó khởi động lại Docker Desktop.

### 4. Muốn cập nhật code mới vào container
Nếu bạn vừa chỉnh sửa code frontend hoặc backend và muốn build lại image:
```bash
# Build và restart riêng frontend:
docker compose up -d --build frontend

# Build và restart riêng backend:
docker compose up -d --build backend
```