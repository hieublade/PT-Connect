import streamlit as st


def render_policy_tab():
    """Hiển thị trang Chính Sách & Quy Định Sử Dụng dành cho Học viên và Huấn luyện viên."""
    st.subheader("Chính Sách & Quy Định Nền Tảng PT-Connect")
    st.info(
        "Chính sách dưới đây quy định quyền lợi, nghĩa vụ và cơ chế bảo vệ công bằng giữa "
        "**Học viên** và **Huấn luyện viên cá nhân (PT)** trong suốt quá trình đặt lịch, "
        "tập luyện, thanh toán và giải quyết tranh chấp trên hệ thống PT-Connect."
    )

    tab_student, tab_pt, tab_general = st.tabs([
        "Chính Sách Học Viên",
        "Chính Sách Huấn Luyện Viên (PT)",
        "Quy Định Chung: Ví, Điểm Danh & Khiếu Nại"
    ])

    with tab_student:
        with st.container(border=True):
            st.markdown(
                r"""
### 1. Quy định Đặt lịch & Học thử
* **Học thử miễn phí (TRIAL):**
  * Mỗi học viên chỉ được quyền đặt học thử miễn phí **duy nhất 1 lần** với mỗi Huấn luyện viên.
  * Chi phí buổi học thử là **0 đ** và không yêu cầu mua gói hợp đồng trước.
* **Đặt lịch theo gói hợp đồng (PACKAGE):**
  * Học viên cần có hợp đồng đang hoạt động (`ACTIVE`) với đúng Huấn luyện viên đó, và ngày diễn ra ca tập phải nằm trong thời hạn hiệu lực của hợp đồng.
  * Hợp đồng thuộc quyền sở hữu riêng của từng tài khoản học viên, không thể dùng chung hoặc chuyển nhượng sang tài khoản khác.
  * **Tạm trừ giữ chỗ:** Ngay khi gửi yêu cầu đặt ca, hệ thống sẽ trừ trước **1 buổi tập** trong hợp đồng. Nếu ca tập bị PT từ chối hoặc được hủy hợp lệ theo chính sách, buổi tập sẽ được hoàn trả lại ngay lập tức.
  * **Chống trùng lịch & Giới hạn đặt chờ:** Học viên không thể đặt 2 ca tập trùng khung giờ nhau (kể cả với các PT khác nhau). Mỗi học viên chỉ được giữ tối đa **2 ca đang chờ duyệt (`PENDING`)** cùng một thời điểm.

---

### 2. Chính sách Hủy lịch dành cho Học viên
Mốc thời gian áp dụng là **24 giờ** tính từ thời điểm bấm hủy đến giờ bắt đầu ca tập:

| Trường hợp | Hoàn buổi tập? | Mức phạt Học viên | Bồi thường cho PT | Phí nền tảng |
| :--- | :--- | :--- | :--- | :--- |
| **Ca đang chờ duyệt (`PENDING`)** | Hoàn 1 buổi vào hợp đồng | **0 đ** (Miễn phí) | 0 đ | 0 đ |
| **Ca đã duyệt, hủy trước $\ge$ 24 giờ** | Hoàn 1 buổi vào hợp đồng | **Phạt 50%** giá trị ca tập (trừ ví) | Nhận bồi thường bằng số tiền phạt thực thu | 0 đ |
| **Ca đã duyệt, hủy sát giờ (< 24 giờ) hoặc Vắng mặt (No-Show)** | **Mất buổi** (Không hoàn) | Không thu thêm (đã trừ buổi) | Nhận **90%** thù lao ca tập | **10%** phí dịch vụ |

> * **Hủy trước $\ge$ 24 giờ:** Học viên được giữ lại quyền sử dụng buổi tập đó cho lần sau, nhưng chịu phí phạt 50% giá trị ca tập để bù đắp chi phí cơ hội cho PT.
> * **Hủy sát giờ (< 24 giờ) hoặc No-Show:** Buổi tập được tính như đã diễn ra và thanh toán đầy đủ thù lao cho PT (90%) cùng phí nền tảng (10%).

---

### 3. Quyền lợi Điểm danh, Khiếu nại & Đánh giá
* Học viên xác nhận tham gia buổi tập bằng **mã OTP 6 chữ số** do PT cung cấp tại phòng tập.
* Có quyền gửi khiếu nại trong vòng **48 giờ** sau khi ca tập hoàn thành hoặc bị hủy (mỗi ca tối đa 1 lần).
* Có quyền đánh giá PT từ **1 đến 5 sao** kèm nhận xét sau mỗi buổi tập hoàn thành.
"""
            )

    with tab_pt:
        with st.container(border=True):
            st.markdown(
                r"""
### 1. Quy định Tiếp nhận, Duyệt & Từ chối lịch tập
* **Trạng thái chờ duyệt (`PENDING`):** Mọi lịch đặt mới của học viên đều cần PT xác nhận trước khi diễn ra.
* **Xác nhận lịch (`CONFIRMED`):** PT chỉ có thể xác nhận các ca tập có thời gian bắt đầu ở tương lai; không thể xác nhận ca tập đã quá giờ bắt đầu.
* **Từ chối lịch:** Nếu bận hoặc không phù hợp, PT có quyền từ chối ca đang chờ duyệt. Hệ thống sẽ hoàn lại 1 buổi tập cho học viên, giải phóng khung giờ và **không phạt** PT.
* **Tự động hủy lịch treo quá hạn (4 giờ):** Nếu ca tập chờ duyệt quá **4 giờ** mà PT chưa phản hồi, hệ thống sẽ tự động hủy ca, mở lại khung giờ và hoàn buổi tập cho học viên mà không áp dụng mức phạt.

---

### 2. Chính sách Hủy lịch dành cho Huấn luyện viên
Mốc thời gian áp dụng là **24 giờ** tính từ thời điểm bấm hủy đến giờ bắt đầu ca tập:

| Trường hợp | Hoàn buổi cho Học viên? | Mức phạt Huấn luyện viên | Bồi thường cho Học viên |
| :--- | :--- | :--- | :--- |
| **Từ chối ca chờ duyệt (`PENDING`)** | Hoàn 1 buổi vào hợp đồng | **0 đ** (Không phạt) | 0 đ |
| **Hủy ca đã duyệt trước $\ge$ 24 giờ** | Hoàn 1 buổi vào hợp đồng | **0 đ** (Không phạt) | 0 đ |
| **Hủy ca đã duyệt sát giờ (< 24 giờ)** | Hoàn 1 buổi vào hợp đồng | **Phạt 100%** giá trị ca tập (trừ ví PT) | Nhận bồi thường bằng số tiền phạt thực thu từ ví PT |

> * **Lưu ý:** Nếu PT hủy sát giờ (< 24 giờ) mà số dư khả dụng trong ví không đủ nộp phạt 100%, phần còn thiếu sẽ được ghi nhận thành **Nợ phạt** và tự động cấn trừ vào các khoản thu hoặc lần nạp tiền tiếp theo.

---

### 3. Quy định Điểm danh, Thu nhập & Ký quỹ
* **Khung giờ điểm danh:** PT được phép mở phiên điểm danh từ **15 phút trước giờ bắt đầu** cho đến tối đa **2 giờ sau khi ca tập kết thúc**. Nếu mở muộn quá **15 phút** sau giờ bắt đầu, ca tập sẽ bị ghi nhận trạng thái **Trễ giờ (`LATE`)**.
* **Báo vắng mặt (No-Show):** Sau **15 phút** kể từ giờ bắt đầu mà học viên không có mặt và không liên hệ, PT có quyền báo vắng mặt để hoàn tất ca tập và nhận thù lao theo quy định.
* **Chia sẻ doanh thu:** PT nhận **90% giá trị mỗi ca tập** hoàn thành vào ví cá nhân; nền tảng thu **10% phí dịch vụ**.
* **Ký quỹ cam kết hợp đồng:** Sàn yêu cầu duy trì một khoản **tiền ký quỹ tạm khóa** trên ví PT để bảo đảm cam kết giảng dạy; khoản tiền này không thể rút về ngân hàng cho đến khi các hợp đồng liên quan kết thúc.
"""
            )

    with tab_general:
        with st.container(border=True):
            st.markdown(
                r"""
### 1. Cơ chế Điểm danh 2 chiều (OTP 6 số)
* Khi bắt đầu buổi tập, PT mở phiên điểm danh để tạo **mã OTP 6 chữ số** (có hiệu lực trong **30 phút**).
* Học viên nhập mã OTP trên ứng dụng để xác nhận có mặt, sau đó PT bấm xác nhận hoàn thành buổi tập.
* Khi cả hai bên xác nhận thành công, ca tập chuyển sang trạng thái **Hoàn thành (`COMPLETED`)** và hệ thống tự động quyết toán 90% thù lao cho PT, 10% phí sàn.
* Khi hợp đồng đã sử dụng hết số buổi (`0` buổi còn lại) và không còn ca tập đang mở, hợp đồng tự động chuyển sang trạng thái hoàn tất.

---

### 2. Cơ chế Ví điện tử, Chống âm ví & Nợ phạt
* **Công thức Số dư khả dụng** (áp dụng thống nhất cho Học viên và PT):
  $$\text{Số dư khả dụng} = \max(0,\ \text{Tổng số dư} - \text{Tiền ký quỹ đang khóa} - \text{Nợ phạt chưa thanh toán})$$
* **Chống âm ví & Ghi nhận nợ phạt:** Khi phát sinh tiền phạt lớn hơn số dư khả dụng hiện có, hệ thống chỉ trừ tối đa số dư khả dụng về `0 đ` (không làm âm số dư ví). Phần tiền thiếu được ghi nhận thành **Nợ phạt**.
* **Hệ quả & Tự động cấn trừ:** Tài khoản đang có nợ phạt sẽ bị giữ lại phần tiền tương ứng khi rút tiền. Người dùng có thể bấm thanh toán nợ thủ công hoặc hệ thống sẽ **tự động cấn trừ nợ phạt** ngay khi nạp tiền mới hoặc nhận thù lao ca dạy mới.
* **Tính minh bạch:** Mọi biến động số dư và lịch sử thanh toán được lưu trữ dưới dạng nhật ký kiểm toán bất biến, không thể chỉnh sửa hay xóa bỏ.

---

### 3. Hủy lịch do Bất khả kháng (Force Majeure)
* Áp dụng cho các sự cố khách quan có bằng chứng xác thực (phòng tập mất điện, thiên tai, dịch bệnh, sự cố y tế...).
* Quản trị viên sẽ hỗ trợ hủy ca, **hoàn lại 1 buổi tập** cho học viên, giải phóng khung giờ và **không phạt** bất kỳ bên nào.

---

### 4. Chính sách Khiếu nại & Trọng tài (SLA 48 giờ)
* **Điều kiện tiếp nhận:** Chỉ áp dụng với ca tập ở trạng thái **Hoàn thành (`COMPLETED`)** hoặc **Đã hủy (`CANCELLED`)**, gửi trong vòng tối đa **48 giờ** kể từ khi ca tập kết thúc hoặc bị hủy. Mỗi ca chỉ được khiếu nại **1 lần**.
* **Quyền phản biện:** Bên bị khiếu nại có **48 giờ** để gửi giải trình và bằng chứng đối chứng.
* **Các mức phán quyết của Quản trị viên:**
  1. **Chấp thuận khiếu nại Học viên:** Hoàn trả 1 buổi tập vào hợp đồng cho học viên.
  2. **Bảo vệ PT:** Giữ nguyên kết quả ca tập và quyết toán thù lao cho PT.
  3. **Hòa giải bất khả kháng:** Hoàn 1 buổi cho học viên, không phạt bên nào.
  4. **Hủy hợp đồng do lỗi PT:** Hủy hợp đồng, hoàn tiền toàn bộ các buổi chưa tập cho học viên và hủy các ca tương lai.
  5. **Hủy hợp đồng do lỗi Học viên:** Hủy hợp đồng, thanh toán 90% giá trị các buổi chưa tập cho PT và hủy các ca tương lai.
  6. **Bác bỏ khiếu nại:** Giữ nguyên hiện trạng nếu đơn khiếu nại thiếu căn cứ.

---

### 5. Chính sách Đánh giá & Uy tín
* Chỉ học viên đã hoàn thành thực tế buổi tập (`COMPLETED`) mới có quyền đánh giá PT theo thang điểm **1 – 5 sao** kèm nhận xét.
* Điểm trung bình và tổng số lượt đánh giá trên hồ sơ PT được hệ thống tự động cập nhật theo thời gian thực.
"""
            )
