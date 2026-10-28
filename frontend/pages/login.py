import json
import re
import streamlit as st
from api.auth_api import AuthApi, save_auth_session
from api.client import ApiException


def is_valid_email(email: str) -> bool:
    """Kiểm tra tính hợp lệ cơ bản của định dạng email."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip())) if email else False


def render_login_page():
    """Hiển thị giao diện Đăng nhập và Đăng ký tài khoản (Milestone 3)."""

    # Container trung tâm
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        # Tiêu đề và biểu tượng thương hiệu
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.6rem; margin-bottom: 0.3rem;">PT Connect</h1>
                <p style="color: #6c757d; font-size: 1.05rem; margin-top: 0;">
                    Nền tảng kết nối Học viên & Huấn luyện viên cá nhân chuyên nghiệp
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Tab Đăng nhập và Đăng ký
        tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng ký tài khoản"])

        # =====================================================================
        # TAB 1: ĐĂNG NHẬP (LOGIN)
        # =====================================================================
        with tab_login:
            st.markdown("#### Đăng nhập vào hệ thống")
            st.caption("Nhập email và mật khẩu của bạn để tiếp tục.")

            with st.form("form_login", clear_on_submit=False):
                email = st.text_input(
                    "Email đăng nhập",
                    placeholder="example@ptconnect.vn"
                )
                password = st.text_input(
                    "Mật khẩu",
                    type="password",
                    placeholder="Nhập mật khẩu của bạn"
                )

                submit_login = st.form_submit_button(
                    "Đăng nhập",
                    use_container_width=True,
                    type="primary"
                )

                if submit_login:
                    if not email.strip():
                        st.error("Vui lòng nhập địa chỉ Email.")
                    elif not password:
                        st.error("Vui lòng nhập Mật khẩu.")
                    else:
                        with st.spinner("Đang xác thực thông tin..."):
                            try:
                                auth_data = AuthApi.login(email=email.strip(), password=password)
                                save_auth_session(auth_data)
                                user = auth_data.get("user", {})
                                full_name = user.get("fullName", email)
                                role = user.get("role", "STUDENT")

                                st.toast(f"Đăng nhập thành công! Chào mừng {full_name} ({role}).")
                                st.rerun()
                            except ApiException as e:
                                if e.message and not e.message.startswith("Máy chủ phản hồi"):
                                    st.error(e.message)
                                elif e.status_code == 401:
                                    st.error("Email hoặc mật khẩu không chính xác.")
                                elif e.status_code == 403:
                                    st.error("Tài khoản của bạn hiện đang bị khóa hoặc chưa được cấp quyền truy cập.")
                                else:
                                    st.error(f"{e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi kết nối: {str(ex)}")

        # =====================================================================
        # TAB 2: ĐĂNG KÝ (REGISTER)
        # =====================================================================
        with tab_register:
            st.markdown("#### Tạo tài khoản mới")
            st.caption("Chọn đúng vai trò của bạn để trải nghiệm hệ thống tốt nhất.")

            role_choice = st.radio(
                "Bạn muốn đăng ký với vai trò gì?",
                options=["STUDENT", "PT"],
                format_func=lambda x: "Học viên (Student)" if x == "STUDENT" else "Huấn luyện viên cá nhân (PT)",
                horizontal=True
            )

            with st.form("form_register", clear_on_submit=False):
                col_name, col_phone = st.columns(2)
                with col_name:
                    reg_name = st.text_input("Họ và tên *", placeholder="Nguyễn Văn A")
                with col_phone:
                    reg_phone = st.text_input("Số điện thoại *", placeholder="0901234567")

                reg_email = st.text_input("Email đăng ký *", placeholder="user@ptconnect.vn")

                col_pwd, col_confirm = st.columns(2)
                with col_pwd:
                    reg_pwd = st.text_input("Mật khẩu (tối thiểu 6 ký tự) *", type="password")
                with col_confirm:
                    reg_confirm = st.text_input("Xác nhận mật khẩu *", type="password")

                # Các trường mở rộng dành riêng cho Huấn luyện viên (PT)
                reg_exp = 0
                reg_locations = ""
                reg_pricing = ""
                reg_bio = ""
                reg_certs = ""

                if role_choice == "PT":
                    st.markdown("---")
                    st.markdown("##### Thông tin hồ sơ Huấn luyện viên (PT)")
                    reg_exp = st.number_input(
                        "Số năm kinh nghiệm *",
                        min_value=0,
                        max_value=50,
                        value=2,
                        step=1
                    )
                    reg_locations = st.text_area(
                        "Khu vực / Phòng tập nhận dạy *",
                        placeholder="Ví dụ: Phòng tập Cali Landmark 72, Quận Cầu Giấy, Hà Nội..."
                    )
                    reg_pricing = st.text_input(
                        "Chính sách phụ thu địa điểm (tùy chọn)",
                        placeholder="Ví dụ: Dạy tại nhà phụ thu thêm 50.000đ phí xăng xe..."
                    )
                    reg_bio = st.text_area(
                        "Giới thiệu bản thân (Bio)",
                        placeholder="Kinh nghiệm huấn luyện, chứng chỉ, phong cách rèn luyện..."
                    )
                    reg_certs = st.text_input(
                        "Đường dẫn chứng chỉ / Bằng cấp (tùy chọn)",
                        placeholder="https://example.com/certificate-pt.pdf"
                    )
                    st.info("**Lưu ý:** Hồ sơ Huấn luyện viên mới đăng ký sẽ ở trạng thái **PENDING** và cần được Quản trị viên (Admin) duyệt trước khi mở bán khóa học.")

                submit_register = st.form_submit_button(
                    "Hoàn tất đăng ký",
                    use_container_width=True,
                    type="primary"
                )

                if submit_register:
                    # Client-side validation
                    if not reg_name.strip():
                        st.error("Vui lòng nhập Họ và tên.")
                    elif not reg_phone.strip():
                        st.error("Vui lòng nhập Số điện thoại.")
                    elif not is_valid_email(reg_email):
                        st.error("Địa chỉ Email không đúng định dạng.")
                    elif len(reg_pwd) < 6:
                        st.error("Mật khẩu phải có độ dài tối thiểu 6 ký tự.")
                    elif reg_pwd != reg_confirm:
                        st.error("Mật khẩu xác nhận không trùng khớp.")
                    elif role_choice == "PT" and not reg_locations.strip():
                        st.error("Huấn luyện viên vui lòng nhập Khu vực nhận dạy.")
                    else:
                        payload = {
                            "fullName": reg_name.strip(),
                            "email": reg_email.strip(),
                            "password": reg_pwd,
                            "phone": reg_phone.strip(),
                            "role": role_choice,
                            "bio": reg_bio.strip() if reg_bio else None,
                            "experienceYears": int(reg_exp) if role_choice == "PT" else None,
                            "availableLocations": reg_locations.strip() if role_choice == "PT" else None,
                            "locationPricingNote": reg_pricing.strip() if reg_pricing else None,
                            "certificateUrls": (
                                reg_certs.strip()
                                if reg_certs.strip().startswith("[") and reg_certs.strip().endswith("]")
                                else json.dumps([reg_certs.strip()])
                            ) if reg_certs and reg_certs.strip() else None
                        }

                        with st.spinner("Đang tạo tài khoản và kích hoạt dịch vụ..."):
                            try:
                                auth_data = AuthApi.register(payload)
                                save_auth_session(auth_data)
                                if role_choice == "PT":
                                    st.toast("Đăng ký Huấn luyện viên thành công! Hồ sơ đang chờ Admin duyệt.")
                                else:
                                    st.toast("Đăng ký tài khoản thành công! Ví điện tử 0đ đã được kích hoạt.")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"{e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi đăng ký: {str(ex)}")
