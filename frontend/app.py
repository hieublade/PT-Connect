import streamlit as st
from api.auth_api import AuthApi, clear_auth_session, get_current_user, is_authenticated
from modules.login_view import LoginView
from modules.student_home_view import StudentHomeView
from modules.pt_home_view import PTHomeView
from modules.admin_dashboard_view import AdminDashboardView

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="PT Connect - Nền tảng kết nối Huấn luyện viên cá nhân",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS giao diện hiện đại và chuyên nghiệp
st.markdown(
    """
    <style>
    /* Khoảng cách lề trên và dưới */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    /* Bo góc và hiệu ứng nút bấm */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Huy hiệu vai trò người dùng (Role Badge) */
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .role-student { background-color: #e3f2fd; color: #1565c0; }
    .role-pt { background-color: #fff3e0; color: #e65100; }
    .role-admin { background-color: #f3e5f5; color: #6a1b9a; }
    </style>
    """,
    unsafe_allow_html=True
)


def render_sidebar(user: dict):
    """Hiển thị sidebar chứa thông tin cá nhân và nút Đăng xuất."""
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.2rem;">
                <div>
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #FF4B4B;">PT Connect</h3>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        role = user.get("role", "STUDENT")
        full_name = user.get("fullName", "Người dùng")
        email = user.get("email", "")
        status = user.get("status", "ACTIVE")

        badge_class = {
            "STUDENT": "role-student",
            "PT": "role-pt",
            "ADMIN": "role-admin"
        }.get(role, "role-student")

        role_display = {
            "STUDENT": "Học viên",
            "PT": "Huấn luyện viên",
            "ADMIN": "Quản trị viên"
        }.get(role, role)

        with st.container(border=True):
            st.markdown(f"**{full_name}**")
            st.caption(email)
            st.markdown(f'<span class="role-badge {badge_class}">{role_display}</span>', unsafe_allow_html=True)
            st.caption(f"Trạng thái: `{status}`")

        st.markdown("---")

        # Nút đăng xuất tài khoản
        if st.button("Đăng xuất", use_container_width=True, type="secondary"):
            clear_auth_session()
            st.toast("Đã đăng xuất thành công!")
            st.rerun()


def main():
    """Điều hướng trang chính dựa trên trạng thái đăng nhập và vai trò (Role-based Routing) thông qua các Boundary Views."""

    # 0. Tự động khôi phục phiên đăng nhập từ URL query_params khi F5 / tải lại trang
    if not is_authenticated():
        saved_token = None
        try:
            saved_token = st.query_params.get("session_token")
        except Exception:
            saved_token = None

        if saved_token:
            st.session_state["token"] = saved_token
            try:
                user_info = AuthApi.get_me()
                if user_info and isinstance(user_info, dict) and user_info.get("id"):
                    st.session_state["user"] = user_info
                    st.session_state["logged_in"] = True
                else:
                    clear_auth_session()
            except Exception:
                clear_auth_session()

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

    # Đảm bảo session_token luôn được đồng bộ trên URL query_params để chống mất phiên khi F5
    if st.session_state.get("token"):
        try:
            if st.query_params.get("session_token") != st.session_state["token"]:
                st.query_params["session_token"] = st.session_state["token"]
        except Exception:
            pass

    # Hiển thị Sidebar
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


if __name__ == "__main__":
    main()
