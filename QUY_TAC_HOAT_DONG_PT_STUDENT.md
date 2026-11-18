# 📜 QUY CHUẨN HOẠT ĐỘNG & BỘ QUY TẮC ỨNG XỬ NỀN TẢNG PT-CONNECT
> **Áp dụng cho:** Học viên (Student) & Huấn luyện viên cá nhân (Personal Trainer - PT)  
> **Phiên bản:** 2.0 (Đồng bộ hóa 100% cùng logic kiểm soát tự động của Hệ thống Spring Boot & React)

---

## 📌 MỤC LỤC
1. [Quy tắc Vàng: Mốc thời gian 24 giờ & Chính sách Hủy lịch](#1-quy-tắc-vàng-mốc-thời-gian-24-giờ--chính-sách-hủy-lịch)
2. [Quy chuẩn Điểm danh hai chiều qua mã OTP & Báo vắng (No-Show)](#2-quy-chuẩn-điểm-danh-hai-chiều-qua-mã-otp--báo-vắng-no-show)
3. [Quy chế Học thử (Trial) & Hợp đồng khóa học điện tử](#3-quy-chế-học-thử-trial--hợp-đồng-khóa-học-điện-tử)
4. [Bộ quy tắc ứng xử & Đạo đức nghề nghiệp (Code of Conduct)](#4-bộ-quy-tắc-ứng-xử--đạo-đức-nghề-nghiệp-code-of-conduct)
5. [Cơ chế Trọng tài 48 Giờ & Khung chế tài xử lý vi phạm](#5-cơ-chế-trọng-tài-48-giờ--khung-chế-tài-xử-lý-vi-phạm)

---

## 1. QUY TẮC VÀNG: MỐC THỜI GIAN 24 GIỜ & CHÍNH SÁCH HỦY LỊCH

Thời gian và lịch trình của Huấn luyện viên cũng như Học viên đều cần được tôn trọng tối đa. Hệ thống PTConnect tự động áp dụng công thức đối soát theo mốc **24 giờ trước thời điểm bắt đầu ca tập**:

$$\Delta t = \text{Thời điểm diễn ra ca tập} - \text{Thời điểm bấm Hủy}$$

### 1.1. Bảng ma trận đối soát xử lý Hủy ca tập tự động

| Bên thực hiện hủy | Trạng thái ca tập | Mốc thời gian hủy | Số buổi hợp đồng | Chế tài tài chính & Bồi thường ví |
| :--- | :--- | :--- | :--- | :--- |
| 🏃 **Học viên** | `PENDING` (Chờ HLV duyệt) | Bất kỳ lúc nào | **✓ Hoàn 1 buổi** | **Không mất phí, không phạt.** |
| 🏃 **Học viên** | `CONFIRMED` (Đã duyệt) | Trước $\ge 24$ giờ | **✓ Hoàn 1 buổi** | **Phạt 50% tiền buổi:** Trừ ví học viên và đền bù 50% cho HLV vì đã duyệt và giữ chỗ. |
| 🏃 **Học viên** | `CONFIRMED` (Đã duyệt) | Sát giờ $< 24$ giờ | **✕ MẤT BUỔI (Không hoàn)** | **HLV hưởng 100% tiền buổi:** Chuyển vào ví HLV (sàn trích 10% phí điều phối). |
| 🏋️ **Huấn luyện viên** | `PENDING` (Từ chối nhận ca) | Bất kỳ lúc nào | **✓ Hoàn 1 buổi** | **Không phạt.** Slot được giải phóng về `AVAILABLE`. |
| 🏋️ **Huấn luyện viên** | `CONFIRMED` (Đã duyệt) | Trước $\ge 24$ giờ | **✓ Hoàn 1 buổi** | **Không phạt hay bồi thường.** Học viên nhận lại buổi để đặt lại. |
| 🏋️ **Huấn luyện viên** | `CONFIRMED` (Đã duyệt) | Sát giờ $< 24$ giờ | **✓ Hoàn 1 buổi** | **Phạt 100% tiền buổi:** Trừ trực tiếp ví HLV, đồng thời **đền bù 100% tiền buổi** vào ví Học viên. |
| 🛡️ **Quản trị viên** | Bất kỳ trạng thái | Trường hợp bất khả kháng | **✓ Khôi phục buổi** | **Không phạt đôi bên** (cần cung cấp tài liệu chứng minh). |

> 💡 **Ví dụ minh họa cụ thể:**  
> Giả sử buổi tập có học phí **300.000 ₫**, diễn ra vào lúc **18:00 Thứ Bảy**:
> - Nếu **Học viên** hủy lúc 10:00 Thứ Sáu (trước 32 tiếng $\ge 24h$): Học viên được hoàn 1 buổi vào gói, nhưng ví bị trừ **150.000 ₫ (50%)** đền bù cho PT.
> - Nếu **Học viên** hủy lúc 15:00 Thứ Bảy (trước 3 tiếng $< 24h$): Học viên **bị mất hẳn 1 buổi tập**, 300.000 ₫ được thanh toán cho PT.
> - Nếu **PT** bận việc đột xuất và hủy lúc 16:00 Thứ Bảy ($< 24h$): Học viên nhận lại 1 buổi tập + nhận thêm **300.000 ₫ tiền đền bù** vào ví. PT bị hệ thống phạt trừ **300.000 ₫**.

---

## 2. QUY CHUẨN ĐIỂM DANH HAI CHIỀU QUA MÃ OTP & BÁO VẮNG (NO-SHOW)

Để bảo đảm tính minh bạch, loại bỏ việc gian lận chấm công buổi tập giữa đôi bên:

### 2.1. Quy trình điểm danh 3 bước chuẩn tại phòng tập
1. **Bước 1 (Học viên lấy OTP):** Khi đến phòng tập và gặp PT, Học viên truy cập mục **"Lịch Của Tôi"** → bấm **"Lấy OTP Điểm Danh"**. Hệ thống sinh mã OTP 6 chữ số có hiệu lực trong **15 phút**.
2. **Bước 2 (PT xác thực OTP):** Huấn luyện viên mở màn hình quản lý ca tập → nhập mã OTP do Học viên cung cấp → bấm **"Xác nhận OTP"**.
3. **Bước 3 (Giải ngân):** Ca tập lập tức chuyển trạng thái sang **`COMPLETED`**. Tiền thù lao buổi học tự động mở khóa và cộng vào ví khả dụng của PT (sau khi trừ 10% phí vận hành sàn).

### 2.2. Xử lý trường hợp Học viên vắng mặt (No-Show)
- Nếu sau **30 phút** kể từ thời điểm ca tập bắt đầu mà Học viên không có mặt và không đưa ra lý do chính đáng:
  - Huấn luyện viên có quyền bấm **"Đánh dấu Học viên Vắng mặt" (No-Show)**.
  - Ca tập chuyển sang `COMPLETED`, học viên bị trừ 1 buổi tập và HLV vẫn được hưởng thù lao buổi dạy đó.

### 2.3. Các hành vi nghiêm cấm khi điểm danh
- ❌ **Tuyệt đối nghiêm cấm việc đọc/gửi mã OTP từ xa** qua điện thoại, Zalo, Facebook Messenger khi chưa gặp mặt tại phòng tập.
- ❌ Nghiêm cấm Huấn luyện viên yêu cầu học viên đọc OTP trước giờ tập để "chấm công khống".
- ⚠️ *Mọi hành vi thông đồng gian lận OTP sẽ bị hệ thống phát hiện qua định vị, địa chỉ IP và lịch sử đối soát; tài khoản vi phạm sẽ bị khóa tối thiểu 14 ngày.*

---

## 3. QUY CHẾ HỌC THỬ (TRIAL) & HỢP ĐỒNG KHÓA HỌC ĐIỆN TỬ

### 3.1. Quy định ca tập thử (Single Trial Rule)
- Mỗi Học viên chỉ được đăng ký **học thử tối đa 1 lần duy nhất với mỗi Huấn luyện viên**.
- Học phí ca tập thử là **0 ₫**.
- Nghiêm cấm tạo nhiều tài khoản phụ (Clone) với cùng một số điện thoại/thiết bị để liên tục học thử miễn phí.

### 3.2. Hợp đồng khóa học điện tử (PDF)
- Khi học viên thanh toán mua gói tập, hệ thống tự động sinh **Hợp đồng điện tử có mã đối soát ngân quỹ**, lưu giữ tại mục "Khóa Của Tôi".
- Hợp đồng quy định rõ:
  - Thông tin hai bên (Họ tên, SĐT, Email, Bằng cấp của PT).
  - Tên gói tập, tổng số buổi và thời hạn ngày bắt đầu - ngày kết thúc.
  - Địa điểm tập luyện cam kết cố định.
- Học viên chỉ được đặt lịch tập khi hợp đồng ở trạng thái **`ACTIVE`**, chưa hết hạn và số buổi khả dụng **$> 0$**.

---

## 4. BỘ QUY TẮC ỨNG XỬ & ĐẠO ĐỨC NGHỀ NGHIỆP (CODE OF CONDUCT)

### 4.1. Đối với Học viên (Student)
- ⏰ **Đúng giờ:** Có mặt trước giờ tập từ 5 – 10 phút để làm quen máy móc và khởi động.
- 👟 **Trang phục:** Mặc đồ thể thao gọn gàng, mang giày tập sạch sẽ theo nội quy phòng gym.
- 🤝 **Tôn trọng:** Hợp tác với HLV, thông báo trung thực về tiền sử bệnh lý, chấn thương cơ xương khớp.
- ⭐ **Đánh giá khách quan:** Nhận xét, chấm sao trung thực sau mỗi buổi tập, không dùng ngôn từ xúc phạm danh dự.

### 4.2. Đối với Huấn luyện viên (PT)
- 💼 **Tác phong chuyên nghiệp:** Có mặt trước ít nhất 10 phút, trang phục thể thao chỉn chu.
- 📋 **Giáo án cá nhân hóa:** Thiết kế bài tập khoa học, điều chỉnh mức tạ và kỹ thuật an toàn theo từng thể trạng.
- 🛡️ **Đạo đức nghề nghiệp:** Nghiêm cấm mọi hành vi xúc phạm, quấy rối bằng lời nói hay hành động cơ thể. Luôn giữ khoảng cách và hành vi sư phạm mẫu mực.
- ⚡ **Phê duyệt lịch nhanh chóng:** Phản hồi duyệt hoặc từ chối yêu cầu đặt lịch của học viên trong vòng tối đa **12 giờ**.

### 4.3. ĐIỀU CẤM KỴ: GIAO DỊCH NGẦM NGOÀI HỆ THỐNG
- PTConnect áp dụng cơ chế ví ký quỹ thông minh để bảo vệ 100% dòng tiền của học viên và thù lao của PT.
- **Nếu đôi bên tự ý chuyển khoản cá nhân ngoài nền tảng:**
  - Hệ thống **từ chối hoàn toàn trách nhiệm bảo hộ, hòa giải và đền bù** khi có tranh chấp, quỵt tiền hay bùng lịch.
  - Huấn luyện viên bị khóa tài khoản vĩnh viễn và bị thu hồi toàn bộ số dư ký quỹ vi phạm.

---

## 5. CƠ CHẾ TRỌNG TÀI 48 GIỜ & KHUNG CHẾ TÀI XỬ LÝ VI PHẠM

Khi phát sinh sự cố (HLV không đến, hủy lịch sai quy định, thái độ thiếu chuẩn mực):
1. **Khởi tạo khiếu nại:** Bấm nút **"Khiếu nại"** trực tiếp tại dòng ca tập tương ứng trên giao diện.
2. **Cung cấp chứng cứ:** Nêu rõ lý do, tải lên hình ảnh bằng chứng (ảnh chụp tin nhắn, biên bản đối chất...).
3. **Phán quyết trong 48 giờ:** Ban Quản Trị độc lập sẽ đối soát lịch sử log hệ thống, liên hệ hai bên và ban hành phán quyết:
   - Hoàn trả 100% học phí buổi học vào ví của bên bị hại.
   - Áp dụng các mức chế tài xử lý:
     - **Mức 1 (Nhắc nhở):** Cảnh cáo bằng văn bản qua hệ thống.
     - **Mức 2 (Phạt tài chính):** Trừ tiền cọc/ví theo đúng chính sách đã công bố.
     - **Mức 3 (Đình chỉ có thời hạn):** Khóa tài khoản tạm thời (`SUSPENDED`) từ 7 đến 30 ngày.
     - **Mức 4 (Cấm vĩnh viễn):** Khóa tài khoản vĩnh viễn, đưa vào danh sách đen của nền tảng.
