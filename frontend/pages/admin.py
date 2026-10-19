from typing import Any, Dict
import streamlit as st
from api.client import ApiException, api_client


def render_admin_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Quản trị viên (Admin Dashboard)."""

    full_name = user.get("fullName", "Quản trị viên")
    email = user.get("email", "")
    role = user.get("role", "ADMIN")

    # Header chào mừng Admin
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: white; font-weight: 700;">👑 Bảng điều khiển Quản trị viên (Admin)</h2>
            <p style="margin: 0.4rem 0 0 0; opacity: 0.9; font-size: 1.05rem;">
                Hệ thống giám sát, phân quyền và quản lý nền tảng PT Connect
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Thẻ tóm tắt thông số
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="🛡️ Cấp độ quyền", value="SUPER_ADMIN", help="Toàn quyền quản trị hệ thống")
    with c2:
        st.metric(label="⏳ PT chờ xét duyệt", value="0 hồ sơ")
    with c3:
        st.metric(label="👥 Tổng người dùng", value="5 tài khoản (Seed)")

    st.markdown("---")

    # Kiểm tra gọi API Backend với quyền Admin
    st.subheader("🔗 Kiểm tra quyền truy cập Backend (Admin Authorization Test)")
    st.caption("Bấm nút bên dưới để gửi request đến Backend kèm Bearer Token của Admin:")

    if st.button("📡 Gọi GET /api/v1/users (Danh sách tài khoản hệ thống)", type="primary"):
        with st.spinner("Đang gửi yêu cầu xác thực tới Backend..."):
            try:
                users_data = api_client.get("/api/v1/users")
                st.success("✅ Xác thực quyền Admin thành công! Backend đã trả về dữ liệu danh sách người dùng:")
                if isinstance(users_data, list):
                    st.dataframe(users_data, use_container_width=True)
                else:
                    st.json(users_data)
            except ApiException as e:
                st.error(f"❌ Lỗi API [{e.status_code}]: {e.message}")
            except Exception as ex:
                st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")

    st.markdown("---")

    # Các tính năng quản trị dự kiến
    st.subheader("🚀 Các phân hệ quản trị sắp tới")
    f1, f2, f3 = st.columns(3)
    with f1:
        with st.container(border=True):
            st.markdown("#### ⏳ Phê Duyệt Huấn Luyện Viên")
            st.caption("Xem danh sách PT PENDING, kiểm tra chứng chỉ bằng cấp và bấm Duyệt/Từ chối.")
            st.caption("*(Dự kiến: Milestone 4)*")
    with f2:
        with st.container(border=True):
            st.markdown("#### 👥 Quản Lý Người Dùng")
            st.caption("Xem danh sách toàn bộ Student/PT, khóa hoặc mở khóa tài khoản (SUSPENDED).")
            st.caption("*(Dự kiến: Milestone 5 & 8)*")
    with f3:
        with st.container(border=True):
            st.markdown("#### 📊 Thống Kê & Phân Tích")
            st.caption("Báo cáo doanh thu bán khóa, số lượng booking bằng biểu đồ trực quan Plotly.")
            st.caption("*(Dự kiến: Milestone 8)*")
