# BÁO CÁO TRIỂN KHAI ĐỒNG BỘ CHUẨN HÓA CSDL (1NF & 3NF)
## CHO FASTAPI (backend-py), REACT (frontend-react) VÀ BIỂU ĐỒ LỚP (VISUAL PARADIGM)
*(FULL-STACK IMPLEMENTATION & SYNCHRONIZATION REPORT)*

---

* **Dự án:** PT-Connect - Nền tảng kết nối Huấn luyện viên & Học viên thể hình
* **Nhánh Git:** `feature/refactor-database-fastapi-react`
* **Thời gian hoàn thành:** 05/11/2026
* **Tác giả:** Thư ký AI (Antigravity) phối hợp cùng Mr. Vũ Viết Thành (B24DCCN539)

---

## 1. TỔNG QUAN CÁC NGUYÊN TẮC THIẾT KẾ ĐÃ ÁP DỤNG

### 1.1. Chuẩn hóa 1NF (Bảng `pt_profiles`):
- **Cơ sở dữ liệu:** Cột `certificate_urls JSON` được thay thế bằng `certificate_url VARCHAR(500)`. Mỗi bản ghi lưu 1 URL chứng chỉ hành nghề chính thức.
- **Backend (FastAPI):**
  - Model `PTProfile`: ánh xạ cột `certificate_url = Column(String(500))` và định nghĩa `certificate_urls = synonym("certificate_url")` để tương thích ngược 100%.
  - Schemas (`RegisterRequest`, `UpdatePTProfileRequest`): tiếp nhận cả 2 trường `certificateUrl` và `certificateUrls` (hỗ trợ cả chuỗi thô, chuỗi JSON `["..."]` và mảng URL), tự động làm sạch qua `clean_certificate_url()`.
  - Responses (`PTProfileResponse`, `PendingPTResponse`): trả về đồng thời `certificateUrl` và alias `certificateUrls` với cùng giá trị chuỗi đơn sạch.
- **Frontend (React):**
  - Xây dựng module `src/lib/certificate.ts` (`resolveCertificateUrl`) đọc dữ liệu phòng thủ (Defensive Fallback).
  - Giao diện đăng ký PT (`LoginPage.tsx`) và form cập nhật hồ sơ (`PtProfileForm.tsx`) gửi trực tiếp chuỗi URL sạch, không bao bọc mảng.
  - Giao diện phê duyệt Admin (`AdminPage.tsx`) hiển thị đường link chứng chỉ bấm được (`<a>`).

### 1.2. Chuẩn hóa 3NF (Bảng `reviews`):
- **Cơ sở dữ liệu:** Bảng `reviews` đã xóa bỏ hoàn toàn 2 cột dư thừa `student_id` và `pt_id`, chỉ giữ lại `booking_id` làm khóa ngoại duy nhất (`ON DELETE CASCADE`).
- **Backend (FastAPI):**
  - Model `Review`: bỏ cột và foreign keys của `student_id`, `pt_id`. Bổ sung các read-only properties (`student`, `pt`, `student_id`, `pt_id`) truy xuất thông qua quan hệ `review.booking`.
  - Repository (`ReviewRepository`): truy vấn `find_by_pt_id` và `find_by_student_id` thực hiện JOIN qua bảng `Booking`, kết hợp `selectinload` để tránh truy vấn N+1.
  - Service (`ReviewService`): tạo review mới chỉ gán quan hệ `booking`, rating và comment.
  - DTO (`ReviewResponse`): trích xuất thông tin `studentId`, `studentName`, `studentAvatarUrl`, `ptId` thông qua `review.booking`. JSON trả về cho client giữ nguyên 100% cấu trúc cũ.
- **Frontend (React):**
  - Xây dựng component `StarRating.tsx` (chọn và hiển thị số sao).
  - Xây dựng `ReviewModal.tsx` cho phép học viên gửi đánh giá cho ca tập `COMPLETED`.
  - Xây dựng `ReviewList.tsx` hiển thị danh sách đánh giá kèm tên, avatar và bình luận học viên.
  - Cập nhật `BookingTable.tsx` hiển thị nút "★ Đánh giá" đối với ca tập đã hoàn thành.

### 1.3. Đồng bộ Biểu đồ lớp (Visual Paradigm XML):
- Đã đồng bộ toàn bộ 16 thực thể lõi theo bản vẽ chuẩn mới (`entity classes design.xml`), trong đó:
  - Lớp `Review` chỉ còn liên kết tới `Booking` (`Booking -> Review: 1 to 0..1`), loại bỏ quan hệ dư thừa tới `User` và `PTProfile`.
  - Lớp `PTProfile` cập nhật thuộc tính `certificateUrl: String`.
  - Lớp `Enrollment` được bổ sung quan hệ tới `Course` và `User`.
- Hợp nhất 5 lớp biên (Boundary Views: `PTHomeView`, `ManageSlotView`, `ManageCourseView`, `ManageWorkoutPlanView`, `ManagePTProfileView`) và 5 Biểu đồ lớp phân tích 4 Use Case PT.
- Xuất file kết quả: `PT_Analysis_Class_Diagram_Updated.xml`.

---

## 2. DANH SÁCH TỆP TIN THAY ĐỔI & TẠO MỚI

| STT | Đường dẫn tệp tin | Tầng | Trạng thái |
| :---: | :--- | :--- | :--- |
| 1 | `backend-py/app/schemas/certificate.py` | Backend Schemas | Tạo mới |
| 2 | `backend-py/app/models/pt_profile.py` | Backend Model | Cập nhật (1NF + synonym) |
| 3 | `backend-py/app/models/review.py` | Backend Model | Cập nhật (3NF) |
| 4 | `backend-py/app/repositories/review_repo.py` | Backend Repository | Cập nhật (JOIN booking) |
| 5 | `backend-py/app/services/review_service.py` | Backend Service | Cập nhật |
| 6 | `backend-py/app/schemas/responses/review.py` | Backend DTO | Cập nhật |
| 7 | `backend-py/app/schemas/requests/auth.py` | Backend DTO | Cập nhật |
| 8 | `backend-py/app/schemas/requests/pt.py` | Backend DTO | Cập nhật |
| 9 | `backend-py/app/services/registration/pt_handler.py` | Backend Handler | Cập nhật |
| 10 | `backend-py/app/services/pt_profile_service.py` | Backend Service | Cập nhật |
| 11 | `backend-py/app/schemas/responses/pt.py` | Backend DTO | Cập nhật |
| 12 | `backend-py/tests/unit/test_schemas.py` | Backend Test | Bổ sung unit tests |
| 13 | `frontend-react/src/types/api.ts` | Frontend Types | Cập nhật |
| 14 | `frontend-react/src/lib/certificate.ts` | Frontend Lib | Tạo mới |
| 15 | `frontend-react/src/components/StarRating.tsx` | Frontend Component | Tạo mới |
| 16 | `frontend-react/src/components/ReviewModal.tsx` | Frontend Component | Tạo mới |
| 17 | `frontend-react/src/components/ReviewList.tsx` | Frontend Component | Tạo mới |
| 18 | `frontend-react/src/components/PtProfileForm.tsx` | Frontend Component | Tạo mới |
| 19 | `frontend-react/src/components/BookingTable.tsx` | Frontend Component | Cập nhật |
| 20 | `frontend-react/src/components/PtCard.tsx` | Frontend Component | Cập nhật |
| 21 | `frontend-react/src/pages/LoginPage.tsx` | Frontend Page | Cập nhật |
| 22 | `frontend-react/src/pages/PtPage.tsx` | Frontend Page | Cập nhật |
| 23 | `frontend-react/src/pages/AdminPage.tsx` | Frontend Page | Cập nhật |
| 24 | `frontend-react/src/pages/StudentPage.tsx` | Frontend Page | Cập nhật |
| 25 | `PT_Analysis_Class_Diagram_Updated.xml` | Biểu đồ lớp | Tạo mới |

---

## 3. KẾT QUẢ KIỂM THỬ (VERIFICATION)

1. **Kiểm thử đơn vị Backend (Pytest):**
   - Lệnh: `cd backend-py && .venv/bin/pytest`
   - Kết quả: **50 passed, 0 failed** (100% test suites passed).
2. **Kiểm thử biên dịch Frontend (Vite/TypeScript):**
   - Lệnh: `cd frontend-react && npm run build`
   - Kết quả: **tsc -b && vite build hoàn tất trong 2.37s**, 0 lỗi TypeScript, sinh bundle production thành công.
3. **Kiểm thử tính toàn vẹn XML:**
   - 21 Lớp (16 entities + 5 Boundary views) được load thành công.
   - 6 Biểu đồ lớp phân tích hiển thị đầy đủ các mối quan hệ.
