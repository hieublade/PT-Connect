from typing import Any, Dict, List
import streamlit as st
from api.admin_api import AdminApi
from api.dispute_api import DisputeApi
from api.pt_api import PTApi
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


# =============================================================================
# CÁC LỚP BIÊN THÀNH PHẦN (SUB-VIEWS THEO SƠ ĐỒ PHÂN TÍCH BCE)
# =============================================================================

class PTPendingApprovalView:
    """Sơ đồ 15: Phê duyệt hồ sơ Huấn luyện viên (Admin)."""

    def __init__(self, parent: "AdminDashboardView"):
        self.parent = parent

    def render(self):
        st.subheader("Danh Sách Huấn Luyện Viên Đang Chờ Phê Duyệt")

        if not self.parent.pending_pts:
            st.success("Hiện không có hồ sơ Huấn luyện viên nào đang chờ phê duyệt. Tất cả hồ sơ đã được xử lý!")
        else:
            for pt_item in self.parent.pending_pts:
                p_id = pt_item.get("id")
                p_name = pt_item.get("fullName", "Chưa có tên")
                p_email = pt_item.get("email", "")
                p_phone = pt_item.get("phone", "")
                p_exp = pt_item.get("experienceYears", 0)
                p_loc = pt_item.get("availableLocations", "Chưa cập nhật")
                p_pricing = pt_item.get("locationPricingNote", "Không có phụ thu")
                p_bio = pt_item.get("bio", "Chưa có giới thiệu")
                p_certs = pt_item.get("certificateUrl") or pt_item.get("certificateUrls") or "Chưa cập nhật"
                if isinstance(p_certs, str) and p_certs.startswith('["') and p_certs.endswith('"]'):
                    p_certs = p_certs[2:-2]

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
                    if isinstance(p_certs, str) and p_certs.startswith("http"):
                        st.markdown(f"**Chứng chỉ / Bằng cấp:** [{p_certs}]({p_certs})")
                    else:
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


class UserManagementView:
    """Sơ đồ 14: Quản lý người dùng & Khóa/Mở khóa tài khoản (Admin)."""

    def __init__(self, parent: "AdminDashboardView"):
        self.parent = parent

    def render(self):
        st.subheader("Quản Lý Người Dùng & Trạng Thái Hoạt Động")

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

                is_self = (u_email == self.parent.current_user_email)
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


class AdminStatisticsView:
    """Sơ đồ 13: Xem thống kê & phân tích dữ liệu nền tảng (Admin)."""

    def __init__(self, parent: "AdminDashboardView"):
        self.parent = parent

    def render(self):
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


# =============================================================================
# LỚP BIÊN CHÍNH: AdminDashboardView
# =============================================================================


class AdminWalletManagementView:
    """Quản lý Ví Doanh Thu Sàn & Rút Tiền của Quản trị viên (Admin)."""

    def __init__(self, parent: "AdminDashboardView"):
        self.parent = parent

    def render(self):
        st.subheader("Ví Doanh Thu Sàn & Quản Lý Rút Tiền")
        st.info(
            "**Quy định số dư ví Quản trị viên:** Khác với Huấn luyện viên (bắt buộc duy trì số dư ký quỹ đảm bảo thực hiện hợp đồng) "
            "và Học viên, Quản trị viên không có bất kỳ ràng buộc nào về số dư tối thiểu. "
            "Quản trị viên có toàn quyền rút toàn bộ 100% doanh thu về 0 đ bất kỳ lúc nào."
        )

        admin_wallet = {}
        try:
            admin_wallet = AdminApi.get_admin_wallet()
        except Exception as ex:
            st.error(f"Lỗi tải dữ liệu ví Admin: {str(ex)}")

        balance = float(admin_wallet.get("balance", 0.0) or 0.0)
        total_platform_fee = float(admin_wallet.get("totalPlatformFee", 0.0) or 0.0)
        total_withdrawn = float(admin_wallet.get("totalWithdrawn", 0.0) or 0.0)
        transactions = admin_wallet.get("transactions", [])

        # Chỉ số tổng quan ví Admin
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(
                label="Số Dư Khả Dụng (Có Thể Rút)",
                value=f"{balance:,.0f} đ",
                help="Toàn bộ số dư doanh thu phí hoa hồng 10% nền tảng có thể rút ngay lập tức"
            )
        with c2:
            st.metric(
                label="Ràng Buộc Số Dư Tối Thiểu",
                value="0 đ",
                delta="Không hạn chế",
                help="Admin không bị giam vốn hay ràng buộc cọc ký quỹ"
            )
        with c3:
            st.metric(
                label="Tổng Doanh Thu Phí Sàn",
                value=f"{total_platform_fee:,.0f} đ",
                help="Tổng 10% phí dịch vụ tích lũy từ các ca tập hoàn thành"
            )
        with c4:
            st.metric(
                label="Tổng Tiền Đã Rút",
                value=f"{total_withdrawn:,.0f} đ",
                help="Tổng các khoản đã giải ngân về tài khoản ngân hàng"
            )

        st.markdown("---")

        tab_withdraw, tab_history = st.tabs(["Lập Lệnh Rút Tiền Về Ngân Hàng", "Lịch Sử Giao Dịch Ví Admin"])

        with tab_withdraw:
            st.markdown("#### Yêu Cầu Rút Doanh Thu Về Tài Khoản Ngân Hàng")
            if balance <= 0:
                st.warning("Số dư ví hiện tại là 0 đ. Hiện không có doanh thu để thực hiện rút tiền.")
            else:
                st.caption(f"Số dư tối đa có thể rút ngay: **{balance:,.0f} đ** (Có thể rút sạch về 0 đ).")
                with st.form("form_admin_withdraw"):
                    withdraw_amount = st.number_input(
                        "Số tiền muốn rút (VNĐ) (*):",
                        min_value=10000.0,
                        max_value=float(balance),
                        value=float(balance),
                        step=500000.0,
                        format="%.0f"
                    )

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        bank_name = st.selectbox(
                            "Ngân hàng thụ hưởng (*):",
                            [
                                "Vietcombank (VCB)",
                                "Techcombank (TCB)",
                                "MB Bank (Quân Đội)",
                                "BIDV (Đầu tư và Phát triển)",
                                "VietinBank (Công Thương)",
                                "VPBank (Việt Nam Thịnh Vượng)",
                                "ACB (Á Châu)",
                                "TPBank (Tiên Phong)",
                                "Sacombank (Sài Gòn Thương Tín)"
                            ]
                        )
                        account_number = st.text_input(
                            "Số tài khoản thụ hưởng (*):",
                            value="190367889988",
                            placeholder="Nhập số tài khoản ngân hàng..."
                        )

                    with col_b2:
                        account_holder = st.text_input(
                            "Tên chủ tài khoản (*):",
                            value="CONG TY CO PHAN NEN TANG PT CONNECT",
                            placeholder="VIẾT HOA KHÔNG DẤU..."
                        )
                        withdraw_note = st.text_input(
                            "Nội dung chuyển khoản / Ghi chú:",
                            value="Rut doanh thu phi san PT Connect ve tai khoan cong ty",
                            placeholder="Ghi chú kế toán..."
                        )

                    btn_submit_withdraw = st.form_submit_button("Xác Nhận Rút Tiền Về Ngân Hàng", type="primary", use_container_width=True)

                    if btn_submit_withdraw:
                        if not account_number.strip():
                            st.warning("Vui lòng nhập số tài khoản ngân hàng thụ hưởng!")
                        elif not account_holder.strip():
                            st.warning("Vui lòng nhập tên chủ tài khoản thụ hưởng!")
                        elif withdraw_amount > balance:
                            st.error("Số tiền rút không được vượt quá số dư ví hiện có!")
                        else:
                            try:
                                res = AdminApi.withdraw_admin_wallet(
                                    amount=float(withdraw_amount),
                                    bank_name=bank_name,
                                    account_number=account_number.strip(),
                                    account_holder=account_holder.strip(),
                                    note=withdraw_note.strip()
                                )
                                st.success(f"Đã rút thành công {withdraw_amount:,.0f} đ về tài khoản {bank_name} - {account_number.strip()}!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Lỗi khi thực hiện rút tiền: {str(ex)}")

        with tab_history:
            st.markdown("#### Lịch Sử Biến Động Số Dư & Giao Dịch Ví Admin")
            if not transactions:
                st.info("Chưa có giao dịch phát sinh nào trong ví Quản trị viên.")
            else:
                import pandas as pd
                df_tx = pd.DataFrame(transactions)
                df_tx["Loại giao dịch"] = df_tx["paymentType"].map({
                    "PLATFORM_FEE": "Thu phí sàn 10%",
                    "WITHDRAWAL": "Rút tiền về ngân hàng",
                    "TOPUP": "Nạp tiền"
                }).fillna(df_tx["paymentType"])
                df_tx["Số tiền (đ)"] = df_tx.apply(
                    lambda r: f"-{r['amount']:,.0f}" if r["paymentType"] == "WITHDRAWAL" else f"+{r['amount']:,.0f}",
                    axis=1
                )
                df_tx["Phương thức"] = df_tx["paymentMethod"]
                df_tx["Mã giao dịch"] = df_tx["transactionRef"]
                df_tx["Trạng thái"] = df_tx["status"]
                df_tx["Thời gian"] = df_tx["createdAt"]
                show_cols = ["Mã giao dịch", "Loại giao dịch", "Số tiền (đ)", "Phương thức", "Trạng thái", "Thời gian"]
                st.dataframe(df_tx[show_cols], use_container_width=True)


class AdminDisputeManagementView:
    """Quản lý Khiếu nại và Giải quyết Tranh chấp (Milestone 8 Upgrade)."""

    def __init__(self, parent: "AdminDashboardView"):
        self.parent = parent

    def render(self):
        st.subheader("Hội Đồng Trọng Tài & Giải Quyết Tranh Chấp")
        st.info(
            "**Quy định trọng tài công bằng:** Admin phải chờ đủ **48 giờ** để bên bị khiếu nại nộp văn bản phản biện và bằng chứng đối chứng "
            "trước khi ra phán quyết cuối cùng (trừ khi đối phương đã gửi phản biện hoặc quá hạn 48h). Mọi phán quyết đều phải nêu rõ lý do gửi cho cả hai bên."
        )

        disputes: List[Dict[str, Any]] = []
        try:
            disputes = DisputeApi.list_disputes()
        except Exception as ex:
            st.error(f"Lỗi tải danh sách khiếu nại: {str(ex)}")

        if not disputes:
            st.info("Hiện không có khiếu nại tranh chấp nào trên hệ thống.")
            return

        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            status_filter = st.selectbox(
                "Lọc theo trạng thái hồ sơ:",
                ["Tất cả", "Chờ xử lý (PENDING)", "Đang chờ bổ sung bằng chứng (EVIDENCE_REQUESTED)", "Đã chấp thuận hoàn buổi (RESOLVED_REFUND)", "Đã bác bỏ (REJECTED)"]
            )

        filter_map = {
            "Chờ xử lý (PENDING)": "PENDING",
            "Đang chờ bổ sung bằng chứng (EVIDENCE_REQUESTED)": "EVIDENCE_REQUESTED",
            "Đã chấp thuận hoàn buổi (RESOLVED_REFUND)": "RESOLVED_REFUND",
            "Đã bác bỏ (REJECTED)": "REJECTED"
        }
        filtered_disputes = disputes
        if status_filter in filter_map:
            filtered_disputes = [d for d in disputes if d.get("status") == filter_map[status_filter]]

        st.markdown(f"**Tổng số khiếu nại:** `{len(filtered_disputes)}` hồ sơ")

        for d in filtered_disputes:
            d_id = d.get("id")
            d_bk_id = d.get("bookingId")
            d_type = d.get("disputeType")
            d_status = d.get("status")
            d_reason = d.get("reason")
            d_sender = d.get("senderName") or "Người dùng"
            d_sender_role = d.get("senderRole")
            d_evidence = d.get("evidenceUrl")
            d_counter_arg = d.get("counterArgument")
            d_counter_ev = d.get("counterEvidenceUrl")
            d_deadline = d.get("deadlineAt")
            d_notes = d.get("adminNotes")
            d_student_name = d.get("studentName") or "Học viên"
            d_pt_name = d.get("ptName") or "HLV"

            status_color = "#e65100" if d_status in ("PENDING", "EVIDENCE_REQUESTED") else ("#2e7d32" if d_status == "RESOLVED_REFUND" else "#c62828")

            with st.container(border=True):
                head1, head2 = st.columns([3, 1.5])
                with head1:
                    st.markdown(f"#### Khiếu nại #{d_id} • Ca tập #{d_bk_id}")
                    st.markdown(f"**Bên gửi khiếu nại:** `{d_sender}` ({d_sender_role}) • **Học viên:** `{d_student_name}` • **HLV:** `{d_pt_name}`")
                with head2:
                    st.markdown(
                        f"<div style='text-align: right; background: {status_color}22; color: {status_color}; padding: 6px 12px; border-radius: 8px; font-weight: 700;'>"
                        f"{d_status}</div>",
                        unsafe_allow_html=True
                    )

                st.markdown(f"**Loại khiếu nại:** `{d_type}`")
                st.markdown(f"**Nội dung phản ánh:** {d_reason}")
                if d_evidence:
                    st.markdown(f"**Ảnh bằng chứng bên khiếu nại:** [Xem ảnh bằng chứng]({d_evidence})")

                st.markdown("---")
                if d_counter_arg:
                    st.success(f"**Phản biện từ bên bị khiếu nại:** {d_counter_arg}")
                    if d_counter_ev:
                        st.markdown(f"**Ảnh bằng chứng đối chứng:** [Xem ảnh đối chứng]({d_counter_ev})")
                else:
                    if d_deadline:
                        st.warning(f"**Chưa có phản biện từ đối phương.** Thời hạn 48 giờ kết thúc lúc: `{d_deadline}`")

                if d_notes:
                    st.info(f"**Lý do phán quyết của Admin đã gửi cho hai bên:** {d_notes}")

                # Các hành động của Admin nếu khiếu nại đang mở
                if d_status in ("PENDING", "EVIDENCE_REQUESTED"):
                    st.markdown("##### Thao Tác Phán Quyết Của Ban Quản Trị")
                    act_col1, act_col2 = st.columns([1, 1])

                    with act_col1:
                        with st.popover("Yêu Cầu Thêm Bằng Chứng (Hạn 48h)", use_container_width=True):
                            st.markdown(f"**Gửi yêu cầu bổ sung bằng chứng cho Khiếu nại #{d_id}:**")
                            st.caption("Thời hạn 48 giờ sẽ được áp dụng để các bên bổ sung tài liệu.")
                            req_notes = st.text_area("Yêu cầu cụ thể:", placeholder="Cần cung cấp ảnh check-in phòng tập hoặc tin nhắn trao đổi...", key=f"req_n_{d_id}")
                            if st.button("Gửi Yêu Cầu Bổ Sung", key=f"btn_send_req_{d_id}", type="primary"):
                                if not req_notes or len(req_notes.strip()) < 5:
                                    st.warning("Vui lòng ghi rõ nội dung cần bổ sung!")
                                else:
                                    try:
                                        DisputeApi.request_evidence(d_id, req_notes.strip())
                                        st.success("Đã gửi yêu cầu bổ sung bằng chứng thành công!")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Lỗi: {str(ex)}")

                    with act_col2:
                        with st.popover("Đưa Ra Phán Quyết Trọng Tài", use_container_width=True):
                            st.markdown(f"**Phán quyết cuối cùng cho Khiếu nại #{d_id}:**")
                            action_choice = st.radio(
                                "Quyết định của Trọng tài:",
                                [
                                    ("RESOLVED_REFUND", "Chấp thuận khiếu nại & Hoàn trả 1 buổi tập cho học viên"),
                                    ("CONTRACT_TERMINATION", "Chấp thuận hủy hợp đồng & Hoàn tiền toàn bộ các buổi còn lại"),
                                    ("REJECTED", "Bác bỏ khiếu nại (Giữ nguyên trạng thái)")
                                ],
                                format_func=lambda x: x[1],
                                key=f"act_choice_{d_id}"
                            )
                            verdict_notes = st.text_area(
                                "Lý do phán quyết gửi cho CẢ HAI BÊN (bắt buộc):",
                                placeholder="Nêu rõ căn cứ bằng chứng và điều khoản giải quyết tranh chấp...",
                                key=f"verdict_notes_{d_id}"
                            )
                            if st.button("Xác Nhận Phán Quyết Trọng Tài", key=f"btn_verdict_{d_id}", type="primary"):
                                if not verdict_notes or len(verdict_notes.strip()) < 5:
                                    st.warning("Vui lòng nhập lý do phán quyết ít nhất 5 ký tự để gửi giải trình cho cả 2 bên!")
                                else:
                                    try:
                                        DisputeApi.resolve_dispute(d_id, action_choice[0], verdict_notes.strip())
                                        st.success("Đã hoàn tất phán quyết tranh chấp và gửi kết luận cho các bên!")
                                        st.rerun()
                                    except Exception as ex:
                                        st.error(f"Lỗi: {str(ex)}")


class AdminDashboardView:
    """Lớp biên chính dành cho Quản trị viên (Admin Dashboard BCE Boundary View)."""

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.full_name = user.get("fullName", "Quản trị viên")
        self.current_user_email = user.get("email", "")

        # Tải dữ liệu ban đầu
        self.stats_data: Dict[str, Any] = {}
        self.pending_pts: List[Dict[str, Any]] = []
        self._load_initial_data()

        # Khởi tạo các sub-views
        self.approval_view = PTPendingApprovalView(self)
        self.user_view = UserManagementView(self)
        self.dispute_view = AdminDisputeManagementView(self)
        self.stats_view = AdminStatisticsView(self)
        self.wallet_mgmt_view = AdminWalletManagementView(self)

    def _load_initial_data(self):
        try:
            self.stats_data = AdminApi.get_statistics()
        except Exception:
            self.stats_data = {}

        try:
            self.pending_pts = AdminApi.get_pending_pts()
        except Exception:
            self.pending_pts = []

    def render(self):
        """Hiển thị toàn bộ Bảng điều khiển Quản trị viên."""
        # Header chào mừng Admin
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(74, 20, 140, 0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h2 style="margin: 0; color: white; font-weight: 700;">Bảng Điều Khiển Quản Trị Viên (Admin)</h2>
                        <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                            Xin chào, <strong>{self.full_name}</strong>! Giám sát hệ thống, quản lý người dùng và phân tích dữ liệu toàn diện.
                        </p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        total_students = self.stats_data.get("totalStudents", 0)
        total_pts = self.stats_data.get("totalPts") if self.stats_data.get("totalPts") is not None else self.stats_data.get("totalPTs", 0)
        total_bookings = self.stats_data.get("totalBookings", 0)
        total_revenue = self.stats_data.get("totalRevenue", 0.0)

        # Lấy số dư ví Admin (doanh thu hoa hồng 10% nền tảng)
        admin_wallet_data = {}
        try:
            admin_wallet_data = PTApi.get_wallet()
        except Exception:
            admin_wallet_data = {}
        admin_balance = float(admin_wallet_data.get("balance", 0.0) or 0.0)

        # Thẻ số liệu thống kê tổng quan (Milestone 8 - Output 1)
        m1, m2, m3, m4, m5 = st.columns(5)
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
                delta=f"{len(self.pending_pts)} chờ duyệt" if self.pending_pts else "0 chờ duyệt",
                delta_color="normal" if not self.pending_pts else "inverse",
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
        with m5:
            st.metric(
                label="Ví Thu Phí Admin",
                value=f"{admin_balance:,.0f} đ",
                delta="10% phí nền tảng",
                help="Doanh thu phí hoa hồng 10% trích từ các ca tập hoàn thành nạp vào ví Quản trị viên (user_id = 1)"
            )

        st.markdown("---")

        # Đếm khiếu nại đang mở
        open_disputes_count = 0
        try:
            disps = DisputeApi.list_disputes()
            open_disputes_count = len([d for d in disps if d.get("status") in ("PENDING", "EVIDENCE_REQUESTED")])
        except Exception:
            open_disputes_count = 0

        # Các phân hệ chức năng Admin
        tab_pending, tab_users, tab_disputes, tab_analytics, tab_wallet = st.tabs([
            f"Phê Duyệt ({len(self.pending_pts)})",
            "Quản Lý Người Dùng",
            f"Giải Quyết Tranh Chấp ({open_disputes_count})",
            "Thống Kê",
            "Ví Doanh Thu Sàn"
        ])

        with tab_pending:
            self.approval_view.render()

        with tab_users:
            self.user_view.render()

        with tab_disputes:
            self.dispute_view.render()

        with tab_analytics:
            self.stats_view.render()

        with tab_wallet:
            self.wallet_mgmt_view.render()

