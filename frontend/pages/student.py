from typing import Any, Dict
import streamlit as st


def render_student_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Học viên (Student Home)."""

    full_name = user.get("fullName", "Học viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")

    # Header chào mừng
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: white; font-weight: 700;">👋 Chào mừng bạn, {full_name}!</h2>
            <p style="margin: 0.4rem 0 0 0; opacity: 0.9; font-size: 1.05rem;">
                Không gian rèn luyện cá nhân của bạn tại PT Connect
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Thẻ thống kê tổng quan
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="💳 Số dư Ví mô phỏng", value="0 ₫", help="Ví điện tử được kích hoạt tự động theo Milestone 3")
    with c2:
        st.metric(label="🏋️ Khóa học đang tham gia", value="0 khóa")
    with c3:
        st.metric(label="📅 Lịch tập sắp tới", value="0 buổi")

    st.markdown("---")

    # Thông tin tài khoản
    st.subheader("📋 Thông tin tài khoản Học viên")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        with st.container(border=True):
            st.markdown(f"**Họ và tên:** {full_name}")
            st.markdown(f"**Email:** `{email}`")
            st.markdown(f"**Số điện thoại:** `{phone}`")
    with col_info2:
        with st.container(border=True):
            st.markdown(f"**Vai trò:** `STUDENT` (Học viên)")
            st.markdown(f"**Trạng thái:** `{status}`")
            st.markdown("**Bảo mật:** JWT Authentication Bearer")

    st.markdown("---")

    # Giới thiệu các chức năng sắp tới
    st.subheader("🚀 Các tính năng đang chuẩn bị triển khai cho Học viên")
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        with st.container(border=True):
            st.markdown("#### 🔍 Tìm & Xem PT")
            st.caption("Khám phá danh sách các Huấn luyện viên chuyên nghiệp, xem hồ sơ, kinh nghiệm và chứng chỉ.")
            st.caption("*(Dự kiến: Milestone 5)*")
    with col_feat2:
        with st.container(border=True):
            st.markdown("#### 💳 Mua Khóa Học")
            st.caption("Nạp tiền vào ví mô phỏng, chọn gói tập phù hợp và nhận hợp đồng điện tử.")
            st.caption("*(Dự kiến: Milestone 5)*")
    with col_feat3:
        with st.container(border=True):
            st.markdown("#### 📅 Đặt Lịch & Điểm Danh")
            st.caption("Chọn slot giờ rảnh của PT, đặt buổi tập học thử hoặc theo khóa và điểm danh qua OTP.")
            st.caption("*(Dự kiến: Milestone 6 & 7)*")
