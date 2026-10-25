from typing import Any, Dict, List
import streamlit as st
from api.admin_api import AdminApi
from api.client import ApiException
from analytics.stats import (
    prepare_bookings_df,
    prepare_payments_df,
    get_booking_status_counts,
    get_monthly_trends,
    get_top_pts,
    get_cancellation_analysis,
    get_popular_training_hours,
)
from analytics.charts import (
    plot_booking_status,
    plot_monthly_trends,
    plot_top_pts,
    plot_cancellation_reasons,
    plot_popular_hours,
)


def render_admin_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Quản trị viên (Admin Dashboard - Milestone 4 & Milestone 8)."""

    full_name = user.get("fullName", "Quản trị viên")
    current_user_email = user.get("email", "")

    # Header chào mừng Admin
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(74, 20, 140, 0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="margin: 0; color: white; font-weight: 700;">Bảng Điều Khiển Quản Trị Viên (Admin)</h2>
                    <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                        Xin chào, <strong>{full_name}</strong>! Giám sát hệ thống, quản lý người dùng và phân tích dữ liệu toàn diện.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Lấy dữ liệu tổng hợp từ API /api/v1/admin/statistics
    stats_data: Dict[str, Any] = {}
    try:
        stats_data = AdminApi.get_statistics()
    except Exception:
        stats_data = {}

    total_students = stats_data.get("totalStudents", 0)
    total_pts = stats_data.get("totalPts") if stats_data.get("totalPts") is not None else stats_data.get("totalPTs", 0)
    total_bookings = stats_data.get("totalBookings", 0)
    total_revenue = stats_data.get("totalRevenue", 0.0)

    # Lấy danh sách PT đang chờ duyệt
    pending_pts: List[Dict[str, Any]] = []
    try:
        pending_pts = AdminApi.get_pending_pts()
    except Exception:
        pending_pts = []

    # 2. Thẻ số liệu thống kê tổng quan (Milestone 8 - Output 1)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Tổng Học Viên",
            value=f"{total_students:,} người",
            help="Số tài khoản học viên (STUDENT) trên toàn hệ thống"
        )
    with m2:
        st.metric(
            label="Huấn Luyện Viên",
            value=f"{total_pts:,} PT",
            delta=f"{len(pending_pts)} chờ duyệt" if pending_pts else "0 chờ duyệt",
            delta_color="normal" if not pending_pts else "inverse",
            help="Tổng PT và số lượng hồ sơ đang chờ xét duyệt"
        )
    with m3:
        st.metric(
            label="Tổng Ca Đặt Lịch",
            value=f"{total_bookings:,} ca",
            help="Tổng số lượt đặt lịch luyện tập đã ghi nhận trên hệ thống"
        )
    with m4:
        st.metric(
            label="Tổng Doanh Thu",
            value=f"{total_revenue:,.0f} đ",
            help="Tổng doanh thu thực tế từ các đơn mua gói khóa học thành công"
        )

    st.markdown("---")

    # 3. Các phân hệ chức năng Admin
    tab_pending, tab_users, tab_analytics = st.tabs([
        f"Phê Duyệt PT ({len(pending_pts)})",
        "Quản Lý Người Dùng & Khóa Tài Khoản",
        "Phân Tích & Thống Kê"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PHÊ DUYỆT HUẤN LUYỆN VIÊN (MILESTONE 4)
    # -------------------------------------------------------------------------
    with tab_pending:
        st.subheader("Danh Sách Huấn Luyện Viên Đang Chờ Phê Duyệt")
        st.caption("Xem xét thông tin năng lực, kinh nghiệm và chứng chỉ trước khi cấp quyền nhận học viên cho PT.")

        if not pending_pts:
            st.success("Hiện không có hồ sơ Huấn luyện viên nào đang chờ phê duyệt. Tất cả hồ sơ đã được xử lý!")
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
                        st.markdown(f"### {p_name}")
                        st.markdown(f"**Email:** `{p_email}` | **SĐT:** `{p_phone}`")
                    with col_status:
                        st.markdown(
                            """
                            <div style="text-align: right; margin-top: 5px;">
                                <span style="background-color: #fff3e0; color: #e65100; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">
                                    CHỜ DUYỆT (PENDING)
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown(f"**Giới thiệu:** {p_bio}")
                    st.markdown(f"**Kinh nghiệm:** `{p_exp} năm`")
                    st.markdown(f"**Khu vực nhận dạy:** {p_loc}")
                    st.markdown(f"**Chính sách phụ thu:** {p_pricing}")
                    st.markdown(f"**Chứng chỉ / Bằng cấp:** `{p_certs}`")

                    st.markdown("---")
                    btn_col1, btn_col2, _ = st.columns([2, 2, 4])
                    with btn_col1:
                        if st.button("Phê Duyệt Hồ Sơ", key=f"btn_approve_{p_id}", type="primary", use_container_width=True):
                            try:
                                AdminApi.approve_pt(p_id)
                                st.success(f"Đã phê duyệt hồ sơ của HLV {p_name}! Tài khoản đã được kích hoạt ACTIVE.")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi phê duyệt [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

                    with btn_col2:
                        if st.button("Từ Chối Hồ Sơ", key=f"btn_reject_{p_id}", use_container_width=True):
                            try:
                                AdminApi.reject_pt(p_id)
                                st.warning(f"Đã từ chối hồ sơ của HLV {p_name} (chuyển sang REJECTED).")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi từ chối [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

    # -------------------------------------------------------------------------
    # TAB 2: QUẢN LÝ NGƯỜI DÙNG & KHÓA/MỞ KHÓA TÀI KHOẢN (MILESTONE 8)
    # -------------------------------------------------------------------------
    with tab_users:
        st.subheader("Quản Lý Người Dùng & Trạng Thái Hoạt Động")
        st.caption("Quản trị viên có quyền khóa (SUSPENDED) hoặc mở khóa (ACTIVE) tài khoản khi phát hiện vi phạm chính sách.")

        col_filter, col_refresh = st.columns([3, 1])
        with col_filter:
            filter_role = st.selectbox(
                "Lọc theo vai trò (Role):",
                ["Tất cả", "STUDENT", "PT", "ADMIN"],
                index=0
            )

        role_query = None if filter_role == "Tất cả" else filter_role
        users_list: List[Dict[str, Any]] = []
        try:
            users_list = AdminApi.get_users(role=role_query)
        except ApiException as e:
            st.error(f"Lỗi lấy danh sách người dùng [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"Lỗi: {str(ex)}")

        if not users_list:
            st.info("Không tìm thấy người dùng nào phù hợp.")
        else:
            st.write(f"Tìm thấy **{len(users_list)}** tài khoản:")

            for u in users_list:
                u_id = u.get("id")
                u_name = u.get("fullName", "Không tên")
                u_email = u.get("email", "")
                u_phone = u.get("phone", "Chưa có")
                u_role = u.get("role", "STUDENT")
                u_status = u.get("status", "ACTIVE")
                created_at = u.get("createdAt", "")

                is_self = (u_email == current_user_email)
                status_color = "#2e7d32" if u_status == "ACTIVE" else "#d32f2f" if u_status == "SUSPENDED" else "#f57c00"

                with st.container(border=True):
                    c_info, c_action = st.columns([4, 2])
                    with c_info:
                        st.markdown(
                            f"**{u_name}** (`ID: {u_id}`) — "
                            f"<span style='background: #e3f2fd; color: #1565c0; padding: 2px 8px; border-radius: 4px; font-weight: 600;'>{u_role}</span> "
                            f"<span style='background: {status_color}22; color: {status_color}; padding: 2px 8px; border-radius: 4px; font-weight: 600;'>{u_status}</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"Email: `{u_email}` | SĐT: `{u_phone}` | Ngày tạo: `{created_at}`")

                    with c_action:
                        if is_self:
                            st.caption("Tài khoản Admin hiện tại")
                        elif u_status == "ACTIVE":
                            if st.button("Khóa tài khoản", key=f"btn_lock_{u_id}", type="secondary", use_container_width=True):
                                try:
                                    AdminApi.update_user_status(u_id, "SUSPENDED")
                                    st.warning(f"Đã tạm ngưng (SUSPENDED) tài khoản {u_email}!")
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"Lỗi cập nhật trạng thái: {e.message}")
                                except Exception as ex:
                                    st.error(f"Lỗi: {str(ex)}")
                        elif u_status == "SUSPENDED":
                            if st.button("Mở khóa tài khoản", key=f"btn_unlock_{u_id}", type="primary", use_container_width=True):
                                try:
                                    AdminApi.update_user_status(u_id, "ACTIVE")
                                    st.success(f"Đã mở khóa (ACTIVE) thành công tài khoản {u_email}!")
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"Lỗi cập nhật trạng thái: {e.message}")
                                except Exception as ex:
                                    st.error(f"Lỗi: {str(ex)}")
                        else:
                            st.caption(f"Trạng thái: {u_status}")

    # TAB 3: PHÂN TÍCH DỮ LIỆU & BIỂU ĐỒ NỀN TẢNG
    with tab_analytics:
        st.subheader("Hệ Thống Phân Tích Dữ Liệu Nền Tảng")

        with st.spinner("Đang tải dữ liệu phân tích..."):
            bookings_raw: List[Dict[str, Any]] = []
            payments_raw: List[Dict[str, Any]] = []
            try:
                bookings_raw = AdminApi.get_bookings()
                payments_raw = AdminApi.get_payments()
            except Exception as e:
                st.error(f"Không thể tải dữ liệu phân tích: {str(e)}")

        # Xử lý dữ liệu bằng Pandas
        df_bookings = prepare_bookings_df(bookings_raw)
        df_payments = prepare_payments_df(payments_raw)

        # 1. Biểu đồ 1: Phân bố trạng thái booking
        st.markdown("### 1. Trạng Thái Các Ca Đặt Lịch (Booking Status)")
        df_status = get_booking_status_counts(df_bookings)
        fig_status = plot_booking_status(df_status)
        st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")

        # 2. Biểu đồ 2: Doanh thu bán khóa và ca đặt lịch theo tháng
        st.markdown("### 2. Xu Hướng Ca Tập & Doanh Thu Bán Khóa Theo Tháng")
        df_trends = get_monthly_trends(df_bookings, df_payments)
        fig_trends = plot_monthly_trends(df_trends)
        st.plotly_chart(fig_trends, use_container_width=True)

        st.markdown("---")

        # 3. Biểu đồ 3: Top Huấn luyện viên
        st.markdown("### 3. Top Huấn Luyện Viên Dẫn Đầu Hệ Thống")
        df_top_pts = get_top_pts(df_bookings, limit=10)
        fig_pts = plot_top_pts(df_top_pts)
        st.plotly_chart(fig_pts, use_container_width=True)

        st.markdown("---")

        # 4. Phân tích mở rộng: Khung giờ & Tỷ lệ hủy
        st.markdown("### 4. Phân Tích Mở Rộng: Khung Giờ & Ca Tập Bị Hủy")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            df_hourly = get_popular_training_hours(df_bookings)
            fig_hourly = plot_popular_hours(df_hourly)
            st.plotly_chart(fig_hourly, use_container_width=True)

        with col_c2:
            df_cancel = get_cancellation_analysis(df_bookings)
            fig_cancel = plot_cancellation_reasons(df_cancel)
            st.plotly_chart(fig_cancel, use_container_width=True)
