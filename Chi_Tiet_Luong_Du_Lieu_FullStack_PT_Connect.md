# BÁO CÁO CÁC LUỒNG DỮ LIỆU FULL-STACK DẠNG KHỐI NGANG (HORIZONTAL DIAGRAMS)
### PHÙ HỢP CHÈN BÁO CÁO WORD & SLIDE BẢO VỆ ĐỒ ÁN (TỶ LỆ KHUNG HÌNH CHỮ NHẬT NGANG)

Để thuận tiện nhất cho việc chèn vào báo cáo văn bản Word (khổ giấy A4 dọc) và trình chiếu slide thuyết trình mà **không bị dài thượt theo chiều dọc hay làm tràn trang giấy**, 3 luồng nghiệp vụ cốt lõi đã được thiết kế lại theo **khung hình chữ nhật ngang (Horizontal Landscape)**:
* Chiều rộng trải dài vừa khít bề ngang trang in (1300px - 1800px).
* Chiều cao gọn gàng (300px - 600px), chỉ chiếm 1/3 trang giấy, giữ nguyên font chữ to và rõ nét.
* Mỗi sơ đồ chỉ từ **5 đến 6 khối chính**, đánh số thứ tự mũi tên từ ① đến ⑩.

---

## 1. KHỐI LUỒNG 1: ĐĂNG NHẬP, XÁC THỰC BCRYPT & CẤP PHÁT JWT TOKEN

### 🖼️ Sơ đồ Khối Ngang (Tỷ lệ 1347 x 396 px):
![Sơ đồ Ngang Luồng 1 - Đăng nhập và Cấp phát Token](/home/thanhvv17@fsoft.fpt.vn/.gemini/antigravity/brain/b43761e0-b861-42f5-a427-285947f6e803/so_do_ngang_1_dang_nhap.png)

```mermaid
flowchart LR
    classDef feStyle fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1;
    classDef routeStyle fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#BF360C;
    classDef servStyle fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20;
    classDef coreStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#4A148C;
    classDef dbStyle fill:#ECEFF1,stroke:#37474F,stroke-width:2px,color:#263238;

    UI["🖥️ 1. Streamlit Form<br/><b>login_view.py:75</b><br/><i>email & password</i>"]:::feStyle
    API["🚪 2. FastAPI Router<br/><b>routes/auth.py:27</b><br/><i>LoginRequest DTO</i>"]:::routeStyle
    SERV["⚙️ 3. AuthService<br/><b>auth_service.py:70</b><br/><i>login(request)</i>"]:::servStyle
    DB[("🛢️ 4. MySQL users<br/><b>user_repo.py:15</b><br/><code>SELECT * WHERE email=?</code>")]:::dbStyle
    SEC["🛡️ 5. Core Bcrypt & JWT<br/><b>core/security.py</b><br/><i>verify() & create_token()</i>"]:::coreStyle
    SESS["💾 6. Lưu Session State<br/><b>login_view.py:76</b><br/><i>st.session_state['token']</i>"]:::feStyle

    UI -->|"① POST JSON"| API
    API -->|"② Validate DTO"| SERV
    SERV -->|"③ Tìm user"| DB
    DB -.->|"④ Trả Entity User"| SERV
    SERV -->|"⑤ Check pass & sinh JWT"| SEC
    SEC -.->|"⑥ Token HMAC-SHA384"| SERV
    SERV -.->|"⑦ AuthResponse"| API
    API -.->|"⑧ HTTP 200 OK"| SESS
    SESS -.->|"⑨ Điều hướng"| UI
```

---

## 2. KHỐI LUỒNG 2: GỬI REQUEST KÈM BEARER TOKEN & KIỂM TRA ĐA TẦNG

### 🎯 Tình huống:
Huấn luyện viên mở màn hình xem danh sách ca tập chờ duyệt (`GET /api/v1/pt/bookings?status=PENDING`).

### 🖼️ Sơ đồ Khối Ngang (Tỷ lệ 1841 x 318 px):
![Sơ đồ Ngang Luồng 2 - Xác thực Token và Phân quyền](/home/thanhvv17@fsoft.fpt.vn/.gemini/antigravity/brain/b43761e0-b861-42f5-a427-285947f6e803/so_do_ngang_2_xac_thuc_token.png)

```mermaid
flowchart LR
    classDef feStyle fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1;
    classDef coreStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#4A148C;
    classDef routeStyle fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#BF360C;
    classDef servStyle fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20;
    classDef dbStyle fill:#ECEFF1,stroke:#37474F,stroke-width:2px,color:#263238;

    FE["🌐 1. Streamlit Client<br/><b>api/client.py:44</b><br/><i>Header: Bearer token</i>"]:::feStyle
    CORE["🛡️ 2. Core Security & RBAC<br/><b>core/deps.py & security.py</b><br/><i>jwt.decode() & check Role</i>"]:::coreStyle
    ROUTER["📬 3. FastAPI Router<br/><b>routes/bookings.py:99</b><br/><i>Inject current_user: User</i>"]:::routeStyle
    SERV["⚙️ 4. BookingService<br/><b>booking_service.py:165</b><br/><i>get_pt_bookings()</i>"]:::servStyle
    DB[("🛢️ 5. MySQL Database<br/><b>booking_repo.py:45</b><br/><code>SELECT bookings JOIN slots</code>")]:::dbStyle
    UI["🖥️ 6. Giao diện PT<br/><b>pt_dashboard_view.py</b><br/><i>Render bảng danh sách</i>"]:::feStyle

    FE -->|"① Gửi Bearer Token"| CORE
    CORE -->|"② Token & Role hợp lệ"| ROUTER
    ROUTER -->|"③ Gọi Service"| SERV
    SERV -->|"④ Query SQL JOIN"| DB
    DB -.->|"⑤ Trả kết quả bookings"| SERV
    SERV -.->|"⑥ BookingResponse"| ROUTER
    ROUTER -.->|"⑦ HTTP 200 OK JSON"| UI
    UI -.->|"⑧ Người dùng thao tác"| FE
```

---

## 3. KHỐI LUỒNG 3: ĐIỂM DANH OTP CHỐNG GIAN LẬN & GIAO DỊCH CSDL

### 🎯 Tình huống:
Huấn luyện viên bấm bắt đầu ca tập $\rightarrow$ Bộ nhớ RAM Thread-safe sinh OTP $\rightarrow$ Học viên nhập OTP $\rightarrow$ Hoàn tất ca tập trong MySQL.

### 🖼️ Sơ đồ Khối Ngang (Tỷ lệ 1358 x 616 px):
![Sơ đồ Ngang Luồng 3 - Điểm danh OTP chống gian lận](/home/thanhvv17@fsoft.fpt.vn/.gemini/antigravity/brain/b43761e0-b861-42f5-a427-285947f6e803/so_do_ngang_3_diem_danh_otp.png)

```mermaid
flowchart LR
    classDef feStyle fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1;
    classDef routeStyle fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#BF360C;
    classDef servStyle fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20;
    classDef otpStyle fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,color:#880E4F;
    classDef dbStyle fill:#ECEFF1,stroke:#37474F,stroke-width:2px,color:#263238;

    PT["💪 1. PT Bấm Bắt Đầu<br/><b>Streamlit PT View</b><br/><i>Mở ca tập #15</i>"]:::feStyle
    ROUTE["🚪 2. Attendance Router<br/><b>routes/attendance.py</b><br/><i>POST /start & /checkin</i>"]:::routeStyle
    SERV["⚙️ 3. AttendanceService<br/><b>attendance_service.py</b><br/><i>Điều phối điểm danh</i>"]:::servStyle
    OTP["🔒 4. RAM OTP Store<br/><b>app/otp/store.py</b><br/><i>threading.Lock() sinh/hủy mã</i>"]:::otpStyle
    DB[("🛢️ 5. MySQL Database<br/><b>Giao dịch DB</b><br/><code>UPDATE bookings & attendance</code>")]:::dbStyle
    STU["👤 6. Học Viên Xác Nhận<br/><b>Streamlit Student View</b><br/><i>Nhập OTP 839201 chốt ca</i>"]:::feStyle

    PT -->|"① Mở ca tập"| ROUTE
    ROUTE -->|"② Gọi Service"| SERV
    SERV -->|"③ Sinh mã OTP 6 số"| OTP
    OTP -.->|"④ Mã '839201'"| SERV
    SERV -.->|"⑤ Trả mã OTP"| PT
    PT -.->|"⑥ Đọc mã OTP"| STU
    STU -->|"⑦ Gửi OTP điểm danh"| ROUTE
    SERV -->|"⑧ Đối chiếu & xóa OTP"| OTP
    SERV -->|"⑨ Ghi nhận hoàn tất"| DB
    SERV -.->|"⑩ HTTP 200: Hoàn tất"| STU
```
