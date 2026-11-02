# 🎯 TÀI LIỆU ĐẶC TẢ DI TRÚ FRONTEND: STREAMLIT ➔ REACT
### (Bảo Toàn 100% Nội Dung Nút Bấm, Tên Lớp & Bảng Màu Thương Hiệu - Tối Ưu Bố Cục Hiện Đại)

---

## 1. Nguyên Tắc Cốt Lõi (Guiding Principles)

1. **Bảo toàn 100% Nội dung & Nhãn nút bấm (Exact Button Texts)**:
   - Không thay đổi câu chữ, giữ nguyên toàn bộ nhãn hành động người dùng đã quen thuộc (VD: `"Xem Chi Tiết"`, `"Mở Khung Giờ"`, `"Nhận mã OTP điểm danh"`, `"Xác nhận điểm danh"`, `"Tải hợp đồng PDF"`, `"Nạp tiền"`, `"Phê duyệt"`, `"Từ chối"`...).
2. **Bảo toàn Tên các Lớp & Component (Preserve Component & Class Names)**:
   - Giữ nguyên cấu trúc định danh: `PtCard`, `CourseCard`, `SlotCard`, `BookingTable`, `AvatarUploader`, `StudentPage`, `PtPage`, `AdminPage`, `AuthApi`, `StudentApi`, `PtApi`, `AdminApi`.
3. **Bảo tồn Bảng Màu Thương Hiệu Hiện Tại (Keep Existing Brand Tone & Colors)**:
   - **Primary Action (Brand PT-Connect)**: Coral Red `#FF4B4B` (hover `#E03E3E`) cho toàn bộ nút chính (Primary CTA).
   - **Học viên (Student Profile / Banner)**: Xanh đại dương `#1565c0` / `#0d47a1` & badge `#e3f2fd`.
   - **Huấn luyện viên (PT Profile / Banner)**: Cam nhiệt huyết `#e65100` / `#ef6c00` & badge `#fff3e0`.
   - **Quản trị viên (Admin Profile / Banner)**: Tím quyền lực `#6a1b9a` / `#4a148c` & badge `#f3e5f5`.
   - **Trạng thái (Badges)**:
     - `VERIFIED` / `AVAILABLE` / `ACTIVE`: Xanh lá `#2e7d32` / nền `#e8f5e9`.
     - `BOOKED` / `CONFIRMED`: Xanh dương `#1565c0` / nền `#e3f2fd`.
     - `PENDING` / `LOCKED`: Cam `#e65100` / nền `#fff3e0`.
     - `CANCELLED` / `REJECTED`: Đỏ `#c62828` / nền `#ffebee`.
4. **Hiện đại hóa Bố cục (Layout Restructuring)**:
   - Tối ưu không gian dọc: Thu nhỏ Banner chào mừng thành Hero Card thanh thoát, đưa các nút bấm và bộ lọc quan trọng lên ngay trên nếp gấp màn hình (above-the-fold).
   - Thay đổi bố cục lưới: Thẻ PT từ 2 cột dọc $\rightarrow$ Responsive Grid 3-4 cột trên Desktop, 1 cột trên Mobile.
   - Quản lý lịch: Chuyển đổi từ dropdown từng slot $\rightarrow$ Weekly Interactive Slot Grid mượt mà.

---

## 2. Đặc Tả Từng Component & Đối Chiếu Với Giao Diện Cũ

### 2.1 Component: `PtCard` (Thẻ Huấn Luyện Viên)
* **File nguồn cũ**: `frontend/components/pt_card.py` (Ảnh: `03_student_explore_pts.png`)
* **Tên Component React**: `export const PtCard: React.FC<PtCardProps>`
* **Bố cục mới**:
  - Dạng Card bo góc tròn `rounded-xl`, đổ bóng mềm `shadow-sm hover:shadow-md`, viền `border border-slate-200`.
  - Hàng trên: Avatar tròn $\varnothing 72\text{px}$, bên cạnh là Tên PT (`h4`), huy hiệu xanh lá `"Đã xác thực"`, số sao `"Đánh giá: X/5 (N đánh giá)"`, và `"N năm KN"`.
  - Hàng giữa: Snippet giới thiệu (bio) tối đa 2 dòng + Khu vực dạy kèm icon địa điểm.
  - Hàng chân trang (Footer): Cột trái hiển thị **"Giá chỉ từ: 3.600.000 ₫"**, Cột phải chứa nút bấm chính màu `#FF4B4B`:
    * **Nút bấm**: `<Button className="bg-[#FF4B4B] hover:bg-[#E03E3E] text-white">Xem Chi Tiết</Button>`

### 2.2 Component: `CourseCard` (Thẻ Khóa Học)
* **File nguồn cũ**: `frontend/components/course_card.py` (Ảnh: `13_pt_courses.png`, `04_student_pt_details.png`)
* **Tên Component React**: `export const CourseCard: React.FC<CourseCardProps>`
* **Bố cục mới**:
  - Tiêu đề khóa học to bản, góc phải là badge `"Đang bán (ACTIVE)"` hoặc `"Đã ngưng bán (INACTIVE)"`.
  - 3 thông số metric dạng pill/box ngang: `"Học phí trọn gói"` (VND), `"Tổng số buổi"` (buổi), `"Thời hạn khóa"` (ngày).
  - Dành cho Học viên: Nút CTA lớn **`"Đăng ký khóa học"`** (hoặc `"Đăng ký & Ký hợp đồng"`).
  - Dành cho PT (Quản lý khóa): Hàng nút quản trị giữ nguyên 100% nhãn:
    * **Nút 1**: `<Button variant="outline">Chỉnh sửa</Button>`
    * **Nút 2**: `<Button variant="outline">Ngưng bán</Button>` (hoặc `"Mở bán lại"`)
    * **Nút 3**: `<Button variant="destructive">Xóa</Button>`

### 2.3 Component: `SlotCard` & `SlotSchedulerGrid` (Khung Giờ Rảnh)
* **File nguồn cũ**: `frontend/components/slot_card.py` (Ảnh: `12_pt_slots.png`)
* **Tên Component React**: `export const SlotCard: React.FC<SlotCardProps>` & `export const SlotSchedulerGrid`
* **Cải tiến bố cục**:
  - *Cũ*: Form đơn lẻ từng slot, mất thời gian chọn ngày + giờ + bấm mở.
  - *Mới*: **Weekly Time Grid**: Bảng chia theo 7 ngày trong tuần và các khung giờ chuẩn (07:00, 08:30, 10:00, 14:00, 16:00, 17:30, 19:00).
  - Trạng thái trực quan:
    * Xanh lá: `"Đang trống (AVAILABLE)"` kèm nút **`"Xóa"`**
    * Xanh dương: `"Đã có học viên đặt (BOOKED)"`
    * Cam: `"Đã khóa (LOCKED)"`
  - Vẫn giữ nút bấm gốc: **`"Mở Khung Giờ"`** để mở ca tập nhanh hoặc hàng loạt.

### 2.4 Component: `BookingTable` (Bảng Quản Lý Ca Tập & Lịch Trình)
* **File nguồn cũ**: `frontend/components/booking_table.py` (Ảnh: `06_student_my_schedule.png`, `11_pt_bookings.png`)
* **Tên Component React**: `export const BookingTable: React.FC<BookingTableProps>`
* **Bố cục mới**:
  - Sử dụng `shadcn/ui` DataTable responsive, có thanh tìm kiếm và lọc trạng thái tab (`Tất cả`, `Chờ duyệt`, `Đã xác nhận`, `Hoàn thành`, `Đã hủy`).
  - Toàn bộ nút hành động nghiệp vụ giữ nguyên chuẩn:
    * Đối với PT: **`"Duyệt ca tập"`**, **`"Từ chối ca tập"`**, **`"Xác nhận điểm danh"`** (khi nhập OTP).
    * Đối với Học viên: **`"Nhận mã OTP điểm danh"`**, **`"Hủy ca tập"`**, **`"Đánh giá buổi tập"`**.

### 2.5 Component: `AvatarUploader` (Tải & Chuẩn Hóa Ảnh Đại Diện)
* **File nguồn cũ**: `frontend/components/avatar_uploader.py` (Ảnh: `09_student_profile.png`, `15_pt_profile.png`)
* **Tên Component React**: `export const AvatarUploader: React.FC<AvatarUploaderProps>`
* **Bố cục mới**:
  - Vùng kéo thả drag-and-drop ảnh (hỗ trợ JPG, PNG, WEBP), hiển thị xem trước tròn ngay tức thì mà không cần reload trang.
  - Nút bấm: **`"Cập nhật ảnh đại diện"`**, **`"Xóa ảnh"`**.

---

## 3. Tái Thiết Kế 3 Cổng Người Dùng (Role Dashboards)

### 3.1 Cổng Học Viên (`StudentDashboard`)
* **Tông màu**: Navy Blue Gradient (`bg-gradient-to-r from-blue-700 to-indigo-800`), nút hành động màu Coral Red `#FF4B4B`.
* **Bố cục Tabs**: Giữ nguyên danh mục 7 tab nhưng chuyển thành thanh Navigation bar cố định:
  1. `Khám Phá PT`: Bộ lọc (Tìm theo tên, Khoảng giá slider, Chuyên môn) + Lưới `PtCard` 3-4 cột.
  2. `Chi Tiết PT`: Profile, ảnh chứng chỉ, đánh giá & danh sách `CourseCard`.
  3. `Đặt Lịch`: Chọn khóa học $\rightarrow$ Chọn khung giờ trên lịch tuần $\rightarrow$ Bấm nút **`"Đặt Lịch Ngay"`**.
  4. `Lịch Của Tôi`: Bảng ca tập, nút **`"Nhận mã OTP điểm danh"`** mở Dialog đếm ngược 60 giây.
  5. `Khóa Của Tôi`: Danh sách hợp đồng đang hiệu lực, tiến độ buổi tập, nút **`"Tải hợp đồng PDF"`**.
  6. `Ví Tiền`: Card thẻ ví số dư khả dụng, nút **`"Nạp tiền vào ví"`**, bảng lịch sử nạp/trừ tiền.
  7. `Hồ Sơ`: Cập nhật họ tên, số điện thoại, avatar.

### 3.2 Cổng Huấn Luyện Viên (`PtDashboard`)
* **Tông màu**: Warm Orange Gradient (`bg-gradient-to-r from-orange-600 to-amber-700`), nút hành động `#FF4B4B`.
* **Bố cục Tabs (6 tab)**:
  1. `Tổng Quan`: 4 KPI Cards gọn gàng (Ca tập chờ duyệt, Khung giờ trống, Khóa học của tôi, Điểm đánh giá) + Danh sách nhận xét gần đây.
  2. `Duyệt Lịch`: Bảng yêu cầu đặt lịch, nút **`"Duyệt ca tập"`**, **`"Từ chối ca tập"`**, ô nhập OTP hoàn thành ca.
  3. `Khung Giờ`: Bảng lịch tuần trực quan (SlotSchedulerGrid) + nút **`"Mở Khung Giờ"`**.
  4. `Quản Lý Khóa`: Danh sách `CourseCard` + nút **`"Tạo khóa học mới"`**.
  5. `Giáo Án`: Quản lý bài tập theo từng học viên, nút **`"Thêm bài tập"`**.
  6. `Hồ Sơ`: Cập nhật bio, kinh nghiệm, địa điểm dạy, chứng chỉ.

### 3.3 Cổng Quản Trị Viên (`AdminDashboard`)
* **Tông màu**: Royal Purple Gradient (`bg-gradient-to-r from-purple-800 to-indigo-900`), nút hành động `#FF4B4B`.
* **Bố cục Tabs (3 tab)**:
  1. `Phê Duyệt PT`: Danh sách PT nộp hồ sơ, xem chứng chỉ, nút **`"Phê duyệt"`**, **`"Từ chối"`**.
  2. `Quản Lý Người Dùng`: Bảng dữ liệu tìm kiếm người dùng, nút **`"Khóa tài khoản"`** / **`"Mở khóa tài khoản"`**.
  3. `Thống Kê`: Recharts biểu đồ cột doanh thu, tỷ lệ hoàn thành ca tập, bảng xếp hạng Top PT.

---

## 4. Bảng Tra Cứu Toàn Diện Nhãn Nút Bấm (Button Texts Consistency Table)

| Vị trí / Luồng | Nhãn Nút Bấm Streamlit Cũ | Nhãn Nút Bấm React Mới (100% Giữ Nguyên) | Màu Sắc / Biến Thể UI |
| :--- | :--- | :--- | :--- |
| **Auth** | `"Đăng nhập"` | `"Đăng nhập"` | Primary `#FF4B4B` |
| **Auth** | `"Tạo tài khoản"` | `"Tạo tài khoản"` | Primary `#FF4B4B` |
| **Sidebar / Header** | `"Đăng xuất"` | `"Đăng xuất"` | Outline / Ghost |
| **Student - PT Card** | `"Xem Chi Tiết"` | `"Xem Chi Tiết"` | Primary `#FF4B4B` |
| **Student - Search** | `"Làm mới"` | `"Làm mới"` | Secondary Outline |
| **Student - Course** | `"Đăng ký khóa học"` | `"Đăng ký khóa học"` | Primary `#FF4B4B` |
| **Student - Booking**| `"Đặt Lịch Ca Tập"` | `"Đặt Lịch Ca Tập"` | Primary `#FF4B4B` |
| **Student - OTP** | `"Nhận mã OTP điểm danh"` | `"Nhận mã OTP điểm danh"` | Emerald Green `#2e7d32` |
| **Student - Schedule**| `"Hủy ca tập"` | `"Hủy ca tập"` | Destructive Red |
| **Student - Schedule**| `"Đánh giá buổi tập"` | `"Đánh giá buổi tập"` | Amber Orange `#e65100` |
| **Student - Contract**| `"Tải hợp đồng PDF"` | `"Tải hợp đồng PDF"` | Blue Outline `#1565c0` |
| **Student - Wallet** | `"Nạp tiền vào ví"` | `"Nạp tiền vào ví"` | Primary `#FF4B4B` |
| **PT - Slot** | `"Mở Khung Giờ"` | `"Mở Khung Giờ"` | Primary `#FF4B4B` |
| **PT - Slot** | `"Xóa"` | `"Xóa"` | Destructive Outline |
| **PT - Booking** | `"Duyệt ca tập"` | `"Duyệt ca tập"` | Emerald Green `#2e7d32` |
| **PT - Booking** | `"Từ chối ca tập"` | `"Từ chối ca tập"` | Destructive Outline |
| **PT - Attendance** | `"Xác nhận điểm danh"` | `"Xác nhận điểm danh"` | Emerald Green `#2e7d32` |
| **PT - Course** | `"Chỉnh sửa"` | `"Chỉnh sửa"` | Secondary Outline |
| **PT - Course** | `"Ngưng bán"` / `"Mở bán lại"` | `"Ngưng bán"` / `"Mở bán lại"` | Amber / Green |
| **Admin - Review** | `"Phê duyệt"` | `"Phê duyệt"` | Emerald Green `#2e7d32` |
| **Admin - Review** | `"Từ chối"` | `"Từ chối"` | Destructive Red |
| **Admin - User** | `"Khóa tài khoản"` | `"Khóa tài khoản"` | Destructive Outline |
| **Admin - User** | `"Mở khóa tài khoản"` | `"Mở khóa tài khoản"` | Blue Outline |
