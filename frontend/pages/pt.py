from typing import Any, Dict
import streamlit as st


def render_pt_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Huấn luyện viên cá nhân (PT Dashboard)."""

    full_name = user.get("fullName", "Huấn luyện viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")

    # Header chào mừng Huấn luyện viên
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #e65100 0%, #f57c00 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: white; font-weight: 700;">🏋️ Chào mừng Huấn luyện viên, {full_name}!</h2>
            <p style="margin: 0.4rem 0 0 0; opacity: 0.9; font-size: 1.05rem;">
                Bảng điều khiển quản lý lịch dạy và học viên của bạn tại PT Connect
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Kiểm tra trạng thái phê duyệt của PT theo Mục 3.2 Đặc tả
    if status == "PENDING":
        st.warning(
            """
            ⏳ **Hồ sơ Huấn luyện viên đang chờ phê duyệt (PENDING):**
            Tài khoản của bạn đã được đăng ký thành công và đang được Quản trị viên (Admin) xem xét chứng chỉ, bằng cấp.
            Trong thời gian này, bạn có thể xem lại thông tin cá nhân nhưng chưa thể tạo khóa học hoặc mở slot lịch dạy.
            """,
            icon="⚠️"
        )
    elif status == "SUSPENDED":
        st.error(
            """
            ⛔ **Tài khoản đang bị tạm ngưng (SUSPENDED):**
            Vui lòng liên hệ với bộ phận Quản trị viên hệ thống để được hỗ trợ kiểm tra và mở khóa tài khoản.
            """,
            icon="🚫"
        )
    else:
        st.success("✅ Hồ sơ của bạn đã được xác minh thành công (`VERIFIED`). Bạn đã sẵn sàng mở lớp dạy!", icon="🎉")

    # Thống kê nhanh
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📚 Khóa học của tôi", value="0 khóa")
    with c2:
        st.metric(label="⏰ Khung giờ rảnh (Slots)", value="0 slot")
    with c3:
        st.metric(label="👥 Học viên theo học", value="0 học viên")

    st.markdown("---")

    # Thông tin tài khoản PT
    st.subheader("📋 Thông tin Huấn luyện viên")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown(f"**Họ và tên:** {full_name}")
            st.markdown(f"**Email:** `{email}`")
            st.markdown(f"**Số điện thoại:** `{phone}`")
    with col2:
        with st.container(border=True):
            st.markdown(f"**Vai trò:** `PT` (Huấn luyện viên)")
            st.markdown(f"**Trạng thái tài khoản:** `{status}`")
            st.markdown(f"**Quyền truy cập:** {'Bị giới hạn (Chờ duyệt)' if status == 'PENDING' else 'Đầy đủ tính năng PT'}")

    st.markdown("---")

    # Các tính năng của PT
    st.subheader("🚀 Tính năng Huấn luyện viên")
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("#### 📝 Quản lý Khóa Học")
            st.caption("Thiết lập tên khóa, số buổi, thời hạn và học phí trọn gói.")
            st.caption("*(Dự kiến: Milestone 4)*")
    with f2:
        with st.container(border=True):
            st.markdown("#### ⏰ Mở Giờ Rảnh (Slot)")
            st.caption("Tạo khung giờ trống để học viên chủ động đặt lịch buổi tập.")
            st.caption("*(Dự kiến: Milestone 4)*")
    with f3:
        with st.container(border=True):
            st.markdown("#### 📅 Xác Nhận & Điểm Danh")
            st.caption("Xem booking chờ duyệt, phê duyệt lịch hẹn và điểm danh bằng mã OTP.")
            st.caption("*(Dự kiến: Milestone 6 & 7)*")
