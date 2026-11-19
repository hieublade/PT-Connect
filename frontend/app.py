import streamlit as st
from api.auth_api import clear_auth_session, get_current_user, is_authenticated
from modules.login_view import LoginView
from modules.student_home_view import StudentHomeView
from modules.pt_home_view import PTHomeView
from modules.admin_dashboard_view import AdminDashboardView
from components.floating_chat_widget import render_floating_chat_widget

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="PT Connect - Nền tảng kết nối Huấn luyện viên cá nhân",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS giao diện tối giản Xanh - Trắng hiện đại
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Phông chữ chuẩn toàn hệ thống & bảo tồn biểu tượng Material Icons của Streamlit */
    html, body, p, h1, h2, h3, h4, h5, h6, input, textarea, select {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }
    [data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined, [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    }

    /* Nền tổng thể mềm mại, sáng sủa */
    .stApp {
        background-color: #f8fafc;
    }

    /* Khoảng cách lề trên và dưới */
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3.5rem;
    }

    /* =========================================================================
       1. THANH BÊN TRÁI (SIDEBAR) MÀU XANH NƯỚC BIỂN NỔI BẬT THEO YÊU CẦU
       ========================================================================= */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0284c7 0%, #0369a1 100%) !important;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    /* Khung hồ sơ người dùng trong Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.16) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    /* Huy hiệu vai trò người dùng trong Sidebar: Chữ xanh biển đậm trên nền trắng */
    .sidebar-role-badge {
        display: inline-block !important;
        padding: 0.35rem 0.85rem !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        background: #ffffff !important;
        color: #0284c7 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
    }

    /* Nút Đăng xuất màu trắng CHỮ XANH BIỂN ĐẬM RÕ NÉT */
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] div.stButton > button p,
    section[data-testid="stSidebar"] div.stButton > button span {
        color: #0284c7 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #f0f9ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2) !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover p,
    section[data-testid="stSidebar"] div.stButton > button:hover span {
        color: #0369a1 !important;
    }

    /* =========================================================================
       2. THANH TAB ĐIỀU HƯỚNG TỐI GIẢN XANH - TRẮNG NỔI BẬT
       ========================================================================= */
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #f1f5f9 !important;
        padding: 6px 8px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 1.4rem !important;
    }
    div[data-baseweb="tab-highlight"] {
        display: none !important; /* Bỏ gạch chân đỏ mặc định của Streamlit */
    }
    button[data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #0284c7 !important;
        background-color: #ffffff !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span {
        color: #ffffff !important;
    }

    /* =========================================================================
       3. NÚT BẤM VÀ THẺ NỘI DUNG (MAIN CONTENT)
       ========================================================================= */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px -2px rgba(15, 23, 42, 0.05) !important;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.5) !important;
    }

    /* Kích thước hộp thoại xem video và live chat rộng rãi, rõ nét */
    div[data-testid="stDialog"] div[role="dialog"] {
        max-width: 920px !important;
        width: 85vw !important;
        border-radius: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def render_sidebar(user: dict):
    """Hiển thị sidebar màu xanh nước biển nổi bật chứa thông tin cá nhân và nút Đăng xuất."""
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.2rem;">
                <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">
                    PT Connect
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        role = user.get("role", "STUDENT")
        full_name = user.get("fullName", "Người dùng")
        email = user.get("email", "")
        status = user.get("status", "ACTIVE")

        role_display = {
            "STUDENT": "Học viên",
            "PT": "Huấn luyện viên",
            "ADMIN": "Quản trị viên"
        }.get(role, role)

        with st.container(border=True):
            st.markdown(f"<h3 style='margin: 0 0 4px 0; font-size: 1.2rem; font-weight: 700; color: #ffffff;'>{full_name}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 0.85rem; color: #e0f2fe; margin-bottom: 8px;'>{email}</div>", unsafe_allow_html=True)
            st.markdown(f'<span class="sidebar-role-badge">{role_display}</span>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size: 0.8rem; color: #bae6fd; margin-top: 8px;'>Trạng thái: <b>{status}</b></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Nút đăng xuất tài khoản
        if st.button("Đăng xuất", use_container_width=True, key="sidebar_logout_btn"):
            clear_auth_session()
            st.toast("Đã đăng xuất thành công!")
            st.rerun()


def main():
    """Điều hướng trang chính dựa trên trạng thái đăng nhập và vai trò (Role-based Routing) thông qua các Boundary Views."""

    # 1. Nếu chưa đăng nhập: Hiển thị màn hình Login / Register
    if not is_authenticated():
        LoginView().render()
        return

    # 2. Đã đăng nhập: Lấy thông tin người dùng từ Session State
    user = get_current_user()
    if not user:
        clear_auth_session()
        st.rerun()
        return

    # Hiển thị Sidebar màu xanh nước biển nổi bật
    render_sidebar(user)

    # 3. Điều hướng theo Role qua các Boundary Views trong modules/
    role = user.get("role")
    if role == "STUDENT":
        StudentHomeView(user).render()
    elif role == "PT":
        PTHomeView(user).render()
    elif role == "ADMIN":
        AdminDashboardView(user).render()
    else:
        st.error(f"Vai trò không xác định trong hệ thống: {role}")
        if st.button("Quay lại màn Đăng nhập"):
            clear_auth_session()
            st.rerun()

    # 4. Hiển thị Nút Chat Trực Tuyến Nổi (Floating Chat Bubble) ở góc dưới bên phải
    render_floating_chat_widget(user)


if __name__ == "__main__":
    main()
