from typing import Any, Dict, List
import streamlit as st
from api.admin_api import AdminApi
from api.client import ApiException


def render_admin_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Quản trị viên (Admin Dashboard - Milestone 4)."""

    full_name = user.get("fullName", "Quản trị viên")
    email = user.get("email", "")

    # Header chào mừng Admin
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: white; font-weight: 700;">👑 Bảng Điều Khiển Quản Trị Viên (Admin)</h2>
            <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                Hệ thống giám sát, phân quyền và phê duyệt hồ sơ Huấn luyện viên nền tảng PT Connect
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Lấy dữ liệu PT đang chờ duyệt
    pending_pts: List[Dict[str, Any]] = []
    try:
        pending_pts = AdminApi.get_pending_pts()
    except Exception:
        pending_pts = []

    # Lấy tổng số user
    all_users: List[Dict[str, Any]] = []
    try:
        all_users = AdminApi.get_users()
    except Exception:
        all_users = []

    # Thẻ tóm tắt thông số
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="🛡️ Cấp độ quyền", value="SUPER_ADMIN", help="Toàn quyền quản trị hệ thống")
    with c2:
        st.metric(label="⏳ PT chờ xét duyệt", value=f"{len(pending_pts)} hồ sơ")
    with c3:
        st.metric(label="👥 Tổng người dùng", value=f"{len(all_users)} tài khoản")

    st.markdown("---")

    # Các phân hệ chức năng Admin
    tab_pending, tab_users, tab_upcoming = st.tabs([
        f"⏳ Phê Duyệt Huấn Luyện Viên ({len(pending_pts)})",
        "👥 Quản Lý Người Dùng",
        "🚀 Lộ Trình Sắp Tới"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PHÊ DUYỆT HUẤN LUYỆN VIÊN (MILESTONE 4)
    # -------------------------------------------------------------------------
    with tab_pending:
        st.subheader("📋 Danh Sách Huấn Luyện Viên Đang Chờ Phê Duyệt")
        st.caption("Xem xét thông tin năng lực, kinh nghiệm và chứng chỉ trước khi cấp quyền nhận học viên cho PT.")

        if not pending_pts:
            st.success("🎉 Hiện không có hồ sơ Huấn luyện viên nào đang chờ phê duyệt. Tất cả hồ sơ đã được xử lý!")
        else:
            for pt_item in pending_pts:
                p_id = pt_item.get("id")
                p_name = pt_item.get("fullName", "Chưa có tên")
                p_email = pt_item.get("email", "")
                p_phone = pt_item.get("phone", "")
                p_exp = pt_item.get("experienceYears", 0)
                p_loc = pt_item.get("availableLocations", "Chưa cập nhật")
                p_pricing = pt_item.get("locationPricingNote", "Không có phụ thu")
                p_bio = pt_item.get("bio", "Chưa có giới thiệu")
                p_certs = pt_item.get("certificateUrls", "[]")

                with st.container(border=True):
                    col_top_info, col_status = st.columns([4, 2])
                    with col_top_info:
                        st.markdown(f"### 🏋️ {p_name}")
                        st.markdown(f"**Email:** `{p_email}` | **SĐT:** `{p_phone}`")
                    with col_status:
                        st.markdown(
                            """
                            <div style="text-align: right; margin-top: 5px;">
                                <span style="background-color: #fff3e0; color: #e65100; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">
                                    ⏳ CHỜ DUYỆT (PENDING)
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown(f"**📝 Giới thiệu:** {p_bio}")
                    st.markdown(f"**🎖️ Kinh nghiệm:** `{p_exp} năm`")
                    st.markdown(f"**📍 Khu vực nhận dạy:** {p_loc}")
                    st.markdown(f"**💵 Chính sách phụ thu:** {p_pricing}")
                    st.markdown(f"**📜 Chứng chỉ / Bằng cấp:** `{p_certs}`")

                    st.markdown("---")
                    btn_col1, btn_col2, _ = st.columns([2, 2, 4])
                    with btn_col1:
                        if st.button("✅ Phê Duyệt Hồ Sơ", key=f"btn_approve_{p_id}", type="primary", use_container_width=True):
                            try:
                                AdminApi.approve_pt(p_id)
                                st.success(f"🎉 Đã phê duyệt hồ sơ của HLV {p_name}! Tài khoản đã được kích hoạt ACTIVE.")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"❌ Lỗi phê duyệt [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"❌ Lỗi: {str(ex)}")

                    with btn_col2:
                        if st.button("❌ Từ Chối Hồ Sơ", key=f"btn_reject_{p_id}", use_container_width=True):
                            try:
                                AdminApi.reject_pt(p_id)
                                st.warning(f"⚠️ Đã từ chối hồ sơ của HLV {p_name} (chuyển sang REJECTED).")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"❌ Lỗi từ chối [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"❌ Lỗi: {str(ex)}")

    # -------------------------------------------------------------------------
    # TAB 2: QUẢN LÝ NGƯỜI DÙNG
    # -------------------------------------------------------------------------
    with tab_users:
        st.subheader("👥 Danh Sách Người Dùng Hệ Thống")

        filter_role = st.selectbox(
            "Lọc theo vai trò (Role):",
            ["Tất cả", "STUDENT", "PT", "ADMIN"],
            index=0
        )

        role_query = None if filter_role == "Tất cả" else filter_role
        try:
            users_list = AdminApi.get_users(role=role_query)
            if not users_list:
                st.info("Không tìm thấy người dùng nào phù hợp.")
            else:
                st.dataframe(users_list, use_container_width=True)
        except ApiException as e:
            st.error(f"❌ Lỗi API [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"❌ Lỗi: {str(ex)}")

    # -------------------------------------------------------------------------
    # TAB 3: LỘ TRÌNH QUẢN TRỊ SẮP TỚI
    # -------------------------------------------------------------------------
    with tab_upcoming:
        st.subheader("🚀 Các Phân Hệ Quản Trị Ở Các Milestone Kế Tiếp")
        c_m5, c_m8 = st.columns(2)
        with c_m5:
            with st.container(border=True):
                st.markdown("#### 👥 Quản Lý Học Viên & Khóa Học (Milestone 5)")
                st.caption("Xem thông tin hợp đồng khóa tập giữa Student và PT, dòng tiền thanh toán qua ví nội bộ.")
        with c_m8:
            with st.container(border=True):
                st.markdown("#### 📊 Dashboard Thống Kê Nâng Cao (Milestone 8)")
                st.caption("Biểu đồ tương tác Plotly & Pandas: Tỷ lệ hoàn thành booking, doanh thu theo tháng, Top PT đánh giá cao nhất.")
