from typing import Any, Dict, List, Optional
from datetime import datetime
import streamlit as st
from api.student_api import StudentApi
from api.client import ApiException
from components.pt_card import render_pt_card, format_currency_vnd


def render_student_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Học viên (Student Dashboard) - Hoàn thiện theo Milestone 5."""

    full_name = user.get("fullName", "Học viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")

    # Tải dữ liệu Ví & Danh sách hợp đồng
    wallet_data: Dict[str, Any] = {}
    my_enrollments: List[Dict[str, Any]] = []

    try:
        wallet_data = StudentApi.get_wallet()
    except Exception:
        wallet_data = {"balance": 0, "lockedBalance": 0, "status": "ACTIVE", "transactions": []}

    try:
        my_enrollments = StudentApi.get_my_enrollments()
    except Exception:
        my_enrollments = []

    wallet_balance = wallet_data.get("balance", 0)
    total_remaining_sessions = sum(e.get("remainingSessions", 0) for e in my_enrollments)

    # Header chào mừng
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(25, 118, 210, 0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <h2 style="margin: 0; color: white; font-weight: 700;">👋 Chào mừng bạn, {full_name}!</h2>
                    <p style="margin: 0.4rem 0 0 0; opacity: 0.92; font-size: 1.05rem;">
                        Không gian rèn luyện, đặt lịch Huấn luyện viên & quản lý hợp đồng tập luyện tại PT Connect
                    </p>
                </div>
                <div style="text-align: right; background: rgba(255, 255, 255, 0.15); padding: 8px 16px; border-radius: 10px; margin-top: 8px;">
                    <div style="font-size: 0.85rem; opacity: 0.9;">Số dư ví khả dụng</div>
                    <div style="font-size: 1.3rem; font-weight: 700;">{format_currency_vnd(wallet_balance)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Thẻ thống kê tổng quan
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="💳 Số dư Ví mô phỏng", value=format_currency_vnd(wallet_balance), help="Ví điện tử thanh toán khóa học nội bộ")
    with c2:
        st.metric(label="🏋️ Gói tập đã đăng ký", value=f"{len(my_enrollments)} khóa")
    with c3:
        st.metric(label="🔢 Tổng buổi tập còn lại", value=f"{total_remaining_sessions} buổi")

    st.markdown("---")

    # Các hằng số định danh Tab điều hướng
    NAV_EXPLORE = "🔍 Khám Phá PT"
    NAV_DETAIL = "🏋️ Chi Tiết & Mua Khóa"
    NAV_WALLET = "💳 Ví Tiền & Nạp Tiền"
    NAV_COURSES = f"📜 Khóa Của Tôi ({len(my_enrollments)})"

    nav_tabs = [NAV_EXPLORE, NAV_DETAIL, NAV_WALLET, NAV_COURSES]

    if "student_active_tab" not in st.session_state:
        st.session_state["student_active_tab"] = NAV_EXPLORE

    # Thanh điều hướng dạng Tab Bar tương tác mượt mà
    col_n1, col_n2, col_n3, col_n4 = st.columns(4)
    for col, tab_name in zip([col_n1, col_n2, col_n3, col_n4], nav_tabs):
        is_cur = (st.session_state["student_active_tab"] == tab_name)
        with col:
            if st.button(
                tab_name,
                key=f"nav_tab_{tab_name}",
                use_container_width=True,
                type="primary" if is_cur else "secondary"
            ):
                st.session_state["student_active_tab"] = tab_name
                st.rerun()

    active_tab = st.session_state["student_active_tab"]
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 1: KHÁM PHÁ & TÌM KIẾM HUẤN LUYỆN VIÊN (MILESTONE 5)
    # -------------------------------------------------------------------------
    if active_tab == NAV_EXPLORE:
        st.subheader("🔍 Tìm Kiếm & Khám Phá Huấn Luyện Viên (PT)")
        st.caption("Chỉ hiển thị các Huấn luyện viên đã được Admin phê duyệt (VERIFIED) và đang hoạt động (ACTIVE).")

        col_search, col_reset = st.columns([4, 1])
        with col_search:
            search_query = st.text_input(
                "Tìm kiếm theo tên Huấn luyện viên:",
                placeholder="Nhập tên PT (ví dụ: Le Hoang C, Pham Minh D...)",
                key="student_pt_search_input"
            )
        with col_reset:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Làm mới", use_container_width=True):
                st.session_state["student_pt_search_input"] = ""
                st.rerun()

        # Gọi API danh sách PT
        pt_list: List[Dict[str, Any]] = []
        try:
            pt_list = StudentApi.get_pt_profiles(name=search_query)
        except ApiException as e:
            st.error(f"❌ Lỗi tải danh sách PT [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"❌ Lỗi hệ thống: {str(ex)}")

        if not pt_list:
            st.info("ℹ️ Không tìm thấy Huấn luyện viên phù hợp với từ khóa tìm kiếm.")
        else:
            st.markdown(f"**Tìm thấy {len(pt_list)} Huấn luyện viên chuyên nghiệp:**")

            # Callback khi học viên bấm nút "Xem Chi Tiết" trên thẻ PT
            def handle_pt_selection(p):
                st.session_state["selected_pt_id"] = p.get("id")
                st.session_state["student_active_tab"] = NAV_DETAIL
                st.rerun()

            # Hiển thị dạng lưới 2 cột
            cols_per_row = 2
            for i in range(0, len(pt_list), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    idx = i + j
                    if idx < len(pt_list):
                        with row_cols[j]:
                            pt_item = pt_list[idx]
                            render_pt_card(
                                pt_item,
                                on_select=lambda p=pt_item: handle_pt_selection(p)
                            )

    # -------------------------------------------------------------------------
    # TAB 2: CHI TIẾT HUẤN LUYỆN VIÊN & MUA KHÓA HỌC
    # -------------------------------------------------------------------------
    elif active_tab == NAV_DETAIL:
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("⬅️ Quay lại danh sách", use_container_width=True):
                st.session_state["student_active_tab"] = NAV_EXPLORE
                st.rerun()
        with col_title:
            st.subheader("🏋️ Hồ Sơ Chi Tiết & Đăng Ký Khóa Học")

        selected_pt_id = st.session_state.get("selected_pt_id")

        # Lấy danh sách PT để người dùng có thể đổi nhanh
        try:
            all_pts = StudentApi.get_pt_profiles()
        except Exception:
            all_pts = []

        if all_pts:
            pt_options = {p.get("id"): f"{p.get('fullName')} (⭐ {float(p.get('averageRating', 0)):.1f} - {p.get('experienceYears', 0)} năm KN)" for p in all_pts}
            default_index = 0
            if selected_pt_id and selected_pt_id in pt_options:
                default_index = list(pt_options.keys()).index(selected_pt_id)
            else:
                selected_pt_id = list(pt_options.keys())[0]
                st.session_state["selected_pt_id"] = selected_pt_id

            chosen_id = st.selectbox(
                "Đang xem Huấn luyện viên:",
                options=list(pt_options.keys()),
                format_func=lambda x: pt_options.get(x, str(x)),
                index=default_index,
                key="student_pt_select_box"
            )
            if chosen_id != selected_pt_id:
                st.session_state["selected_pt_id"] = chosen_id
                st.rerun()

        if not selected_pt_id:
            st.info("👉 Vui lòng chọn một Huấn luyện viên từ Tab **Khám Phá Huấn Luyện Viên** để xem hồ sơ và khóa học.")
        else:
            try:
                pt_profile = StudentApi.get_pt_profile(selected_pt_id)
                pt_courses = StudentApi.get_pt_courses(selected_pt_id)
                pt_slots = StudentApi.get_pt_slots(selected_pt_id)

                # Hiển thị hồ sơ công khai (KHÔNG CÓ CHỨNG CHỈ NỘI BỘ THEO DTO PTPublicDTO)
                with st.container(border=True):
                    col_p1, col_p2 = st.columns([1, 3])
                    with col_p1:
                        avatar = pt_profile.get("avatarUrl") or "https://api.dicebear.com/7.x/avataaars/svg?seed=" + pt_profile.get("fullName", "").replace(" ", "")
                        st.image(avatar, width=130)
                    with col_p2:
                        st.markdown(f"### 🏅 {pt_profile.get('fullName')}")
                        st.markdown(
                            f"**Đánh giá:** ⭐ `{float(pt_profile.get('averageRating', 0)):.1f} / 5.0` ({pt_profile.get('totalReviews', 0)} lượt đánh giá) "
                            f"• **Kinh nghiệm:** `{pt_profile.get('experienceYears', 0)} năm`"
                        )
                        st.markdown(f"**Giới thiệu:** {pt_profile.get('bio') or 'Chưa có tiểu sử.'}")
                        st.markdown(f"**📍 Khu vực nhận dạy:** `{pt_profile.get('availableLocations')}`")
                        if pt_profile.get("locationPricingNote"):
                            st.caption(f"💡 *Chính sách giá/di chuyển:* {pt_profile.get('locationPricingNote')}")

                st.markdown("---")

                # DANH SÁCH KHÓA HỌC ĐANG MỞ BÁN
                st.markdown(f"#### 📦 Các Gói Tập & Khóa Học Đang Mở Bán ({len(pt_courses)})")
                if not pt_courses:
                    st.info("Huấn luyện viên này hiện chưa tạo khóa học nào.")
                else:
                    for course in pt_courses:
                        c_id = course.get("id")
                        c_title = course.get("title", "Khóa tập")
                        c_desc = course.get("description", "")
                        c_sessions = course.get("totalSessions", 0)
                        c_validity = course.get("validityDays", 0)
                        c_price = course.get("basePrice", 0)

                        with st.container(border=True):
                            col_c_info, col_c_buy = st.columns([3, 2])
                            with col_c_info:
                                st.markdown(f"##### 🏋️ {c_title}")
                                if c_desc:
                                    st.write(c_desc)
                                st.markdown(
                                    f"**Số buổi:** `{c_sessions} buổi` • **Thời hạn:** `{c_validity} ngày` • **Học phí:** <span style='color: #d32f2f; font-weight: 700; font-size: 1.15rem;'>{format_currency_vnd(c_price)}</span>",
                                    unsafe_allow_html=True
                                )

                            with col_c_buy:
                                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                                with st.expander(f"💳 Mua Gói Tập Này", expanded=False):
                                    st.markdown(f"**Học phí thanh toán:** `{format_currency_vnd(c_price)}`")
                                    st.markdown(f"**Số dư ví hiện tại:** `{format_currency_vnd(wallet_balance)}`")

                                    has_enough_money = (float(wallet_balance) >= float(c_price))

                                    if not has_enough_money:
                                        shortage = float(c_price) - float(wallet_balance)
                                        st.error(f"⚠️ Số dư ví không đủ! Cần thêm `{format_currency_vnd(shortage)}`.")
                                        if st.button("👉 Nạp tiền ngay vào ví", key=f"btn_go_wallet_{c_id}"):
                                            st.session_state["student_active_tab"] = NAV_WALLET
                                            st.rerun()
                                    else:
                                        st.success("✅ Bạn đủ số dư ví để thanh toán gói tập này.")

                                    # Chọn địa điểm tập luyện cố định
                                    loc_suggestions = [loc.strip() for loc in pt_profile.get("availableLocations", "").split(";") if loc.strip()]
                                    loc_options = loc_suggestions + ["Địa điểm khác (tự nhập)"]

                                    chosen_loc_type = st.selectbox(
                                        "Chọn địa điểm tập luyện cố định:",
                                        loc_options,
                                        key=f"loc_select_{c_id}"
                                    )

                                    if chosen_loc_type == "Địa điểm khác (tự nhập)":
                                        training_location = st.text_input(
                                            "Nhập địa điểm chi tiết:",
                                            placeholder="Ví dụ: Phòng tập FitZone số 12 Cầu Giấy",
                                            key=f"loc_custom_{c_id}"
                                        )
                                    else:
                                        training_location = chosen_loc_type

                                    if st.button("🚀 Xác Nhận Thanh Toán & Ký Hợp Đồng", key=f"btn_confirm_buy_{c_id}", type="primary", disabled=not has_enough_money):
                                        if not training_location or not training_location.strip():
                                            st.error("Vui lòng chọn hoặc nhập địa điểm tập luyện cố định.")
                                        else:
                                            with st.spinner("Đang thực hiện giao dịch nguyên tử trừ ví & sinh hợp đồng PDF..."):
                                                try:
                                                    enroll_res = StudentApi.purchase_course(
                                                        course_id=c_id,
                                                        training_location=training_location.strip(),
                                                        payment_method="WALLET"
                                                    )
                                                    st.success(f"🎉 Chúc mừng bạn đã mua khóa học thành công! Mã hợp đồng: PTC-HD-{enroll_res.get('id'):06d}")
                                                    st.session_state["student_active_tab"] = NAV_COURSES
                                                    st.balloons()
                                                    st.rerun()
                                                except ApiException as e:
                                                    st.error(f"❌ Mua khóa học thất bại [{e.status_code}]: {e.message}")
                                                except Exception as ex:
                                                    st.error(f"❌ Lỗi: {str(ex)}")

                st.markdown("---")

                # LỊCH GIỜ RẢNH KHẢ DỤNG (SLOTS)
                st.markdown(f"#### 📅 Khung Giờ Rảnh Khả Dụng Trong Tương Lai ({len(pt_slots)})")
                st.caption("Chỉ hiển thị các slot ở trạng thái AVAILABLE và chưa bắt đầu.")
                if not pt_slots:
                    st.info("Huấn luyện viên chưa mở khung giờ rảnh nào sắp tới.")
                else:
                    slots_data = []
                    for s in pt_slots:
                        try:
                            st_dt = datetime.fromisoformat(s.get("startTime", ""))
                            en_dt = datetime.fromisoformat(s.get("endTime", ""))
                            date_str = st_dt.strftime("%d/%m/%Y")
                            time_str = f"{st_dt.strftime('%H:%M')} - {en_dt.strftime('%H:%M')}"
                        except Exception:
                            date_str = s.get("startTime", "")
                            time_str = s.get("endTime", "")

                        slots_data.append({
                            "Mã Slot": s.get("id"),
                            "Ngày": date_str,
                            "Khung giờ": time_str,
                            "Trạng thái": "🟢 Sẵn sàng (AVAILABLE)"
                        })
                    st.dataframe(slots_data, use_container_width=True)

            except ApiException as e:
                st.error(f"❌ Lỗi tải hồ sơ PT [{e.status_code}]: {e.message}")
            except Exception as ex:
                st.error(f"❌ Lỗi: {str(ex)}")

    # -------------------------------------------------------------------------
    # TAB 3: VÍ TIỀN & NẠP TIỀN (MILESTONE 5)
    # -------------------------------------------------------------------------
    elif active_tab == NAV_WALLET:
        st.subheader("💳 Quản Lý Ví Điện Tử Nội Bộ & Nạp Tiền")
        st.caption("Ví điện tử nội bộ phục vụ thanh toán hợp đồng khóa học và xử lý đền bù minh bạch.")

        col_w_info, col_w_topup = st.columns([1, 1])

        with col_w_info:
            with st.container(border=True):
                st.markdown("#### 👛 Thông Tin Số Dư Ví")
                st.markdown(f"**Chủ tài khoản:** {full_name}")
                st.markdown(f"**Trạng thái ví:** `🟢 {wallet_data.get('status', 'ACTIVE')}`")
                st.markdown(
                    f"""
                    <div style="background: #e3f2fd; padding: 1.2rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid #1976d2;">
                        <span style="font-size: 0.95rem; color: #0d47a1; font-weight: 500;">Số Dư Khả Dụng:</span>
                        <div style="font-size: 1.8rem; font-weight: 800; color: #1565c0; margin-top: 4px;">
                            {format_currency_vnd(wallet_balance)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                locked = wallet_data.get("lockedBalance", 0)
                st.markdown(f"**Số dư đóng băng (Cọc giữ chỗ):** `{format_currency_vnd(locked)}`")

        with col_w_topup:
            with st.container(border=True):
                st.markdown("#### ⚡ Nạp Tiền Vào Ví (Mô Phỏng)")
                st.caption("Bấm chọn mệnh giá nạp nhanh hoặc nhập số tiền tùy ý bên dưới:")

                # Hàm callback cập nhật số tiền nạp trực tiếp vào session_state
                def set_topup_amount(amt: int):
                    st.session_state["student_topup_amount_input"] = amt

                if "student_topup_amount_input" not in st.session_state:
                    st.session_state["student_topup_amount_input"] = 1000000

                # 6 nút chọn mệnh giá nhanh hoạt động tức thì với on_click
                q1, q2, q3 = st.columns(3)
                with q1:
                    st.button("+500.000 ₫", key="btn_topup_500k", on_click=set_topup_amount, args=(500000,), use_container_width=True)
                with q2:
                    st.button("+1.000.000 ₫", key="btn_topup_1m", on_click=set_topup_amount, args=(1000000,), use_container_width=True)
                with q3:
                    st.button("+2.000.000 ₫", key="btn_topup_2m", on_click=set_topup_amount, args=(2000000,), use_container_width=True)

                q4, q5, q6 = st.columns(3)
                with q4:
                    st.button("+5.000.000 ₫", key="btn_topup_5m", on_click=set_topup_amount, args=(5000000,), use_container_width=True)
                with q5:
                    st.button("+10.000.000 ₫", key="btn_topup_10m", on_click=set_topup_amount, args=(10000000,), use_container_width=True)
                with q6:
                    st.button("+20.000.000 ₫", key="btn_topup_20m", on_click=set_topup_amount, args=(20000000,), use_container_width=True)

                st.number_input(
                    "Số tiền nạp (VND):",
                    min_value=10000,
                    step=50000,
                    key="student_topup_amount_input"
                )

                pay_method = st.selectbox(
                    "Phương thức nạp tiền:",
                    ["BANK_TRANSFER (Chuyển khoản)", "CREDIT_CARD (Thẻ quốc tế)", "WALLET"],
                    index=0
                )
                method_code = pay_method.split(" ")[0]

                if st.button("💳 Tiến Hành Nạp Tiền", type="primary", use_container_width=True):
                    entered_amount = float(st.session_state.get("student_topup_amount_input", 1000000))
                    with st.spinner("Đang xử lý nạp tiền vào ví..."):
                        try:
                            topup_res = StudentApi.topup_wallet(amount=entered_amount, payment_method=method_code)
                            st.success(f"✅ Nạp thành công {format_currency_vnd(entered_amount)}! Mã GD: {topup_res.get('transactionRef')}")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Nạp tiền thất bại [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi: {str(ex)}")

        # LỊCH SỬ GIAO DỊCH VÍ
        st.markdown("---")
        st.subheader("📜 Lịch Sử Giao Dịch Tài Chính")
        txns = wallet_data.get("transactions", [])
        if not txns:
            st.info("Chưa có giao dịch tài chính nào phát sinh.")
        else:
            table_data = []
            for t in txns:
                txn_type = t.get("paymentType", "")
                type_badge = "🟢 NẠP TIỀN" if txn_type == "TOPUP" else ("🔴 MUA KHÓA" if txn_type == "PURCHASE_PACKAGE" else txn_type)
                amt = t.get("amount", 0)
                amt_str = f"+{format_currency_vnd(amt)}" if txn_type in ["TOPUP", "REFUND", "COMPENSATION"] else f"-{format_currency_vnd(amt)}"
                table_data.append({
                    "Mã Giao Dịch": t.get("transactionRef"),
                    "Loại GD": type_badge,
                    "Số Tiền": amt_str,
                    "Phương Thức": t.get("paymentMethod"),
                    "Trạng Thái": t.get("status"),
                    "Thời Gian": t.get("createdAt", "")[:19].replace("T", " ") if t.get("createdAt") else ""
                })
            st.dataframe(table_data, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 4: KHÓA HỌC CỦA TÔI & TẢI HỢP ĐỒNG PDF (MILESTONE 5)
    # -------------------------------------------------------------------------
    elif active_tab == NAV_COURSES:
        st.subheader("📜 Danh Sách Gói Tập Đã Đăng Ký & Hợp Đồng")
        st.caption("Quản lý tiến độ buổi tập và tải hợp đồng dịch vụ đã ký điện tử.")

        if not my_enrollments:
            st.info("Bạn chưa đăng ký khóa học nào. Hãy khám phá và chọn Huấn luyện viên phù hợp ở Tab 1 nhé!")
            if st.button("🔍 Khám phá Huấn luyện viên ngay", type="primary"):
                st.session_state["student_active_tab"] = NAV_EXPLORE
                st.rerun()
        else:
            for enroll in my_enrollments:
                e_id = enroll.get("id")
                c_title = enroll.get("courseTitle", "Gói tập cá nhân")
                pt_name = enroll.get("ptName", "Huấn luyện viên")
                loc = enroll.get("trainingLocation", "Chưa xác định")
                price = enroll.get("finalPrice", 0)
                total_s = enroll.get("totalSessions", 0)
                rem_s = enroll.get("remainingSessions", 0)
                s_date = enroll.get("startDate", "")
                e_date = enroll.get("endDate", "")
                e_status = enroll.get("status", "ACTIVE")

                with st.container(border=True):
                    col_top_title, col_top_status = st.columns([3, 1])
                    with col_top_title:
                        st.markdown(f"#### 🏋️ {c_title} • PTC-HD-{e_id:06d}")
                    with col_top_status:
                        st.markdown(f"<div style='text-align: right;'><b>Trạng thái:</b> <code>{e_status}</code></div>", unsafe_allow_html=True)

                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown(f"**Huấn luyện viên phụ trách:** `{pt_name}`")
                        st.markdown(f"**📍 Địa điểm tập cố định:** `{loc}`")
                        st.markdown(f"**Học phí đã thanh toán:** `{format_currency_vnd(price)}`")

                    with c_info2:
                        st.markdown(f"**Thời hạn hợp đồng:** từ `{s_date}` đến `{e_date}`")
                        # Progress bar buổi tập
                        prog = (rem_s / total_s) if total_s > 0 else 0
                        st.markdown(f"**Số buổi còn lại:** `{rem_s} / {total_s} buổi`")
                        st.progress(prog)

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                    # Nút tải hợp đồng PDF
                    col_space, col_dl = st.columns([3, 1])
                    with col_dl:
                        try:
                            pdf_bytes = StudentApi.download_contract(e_id)
                            st.download_button(
                                label="📄 Tải Hợp Đồng PDF",
                                data=pdf_bytes,
                                file_name=f"HopDong_PTConnect_{e_id}.pdf",
                                mime="application/pdf",
                                key=f"dl_contract_btn_{e_id}",
                                use_container_width=True,
                                type="primary"
                            )
                        except Exception as dl_err:
                            st.caption(f"*(Chưa tải được hợp đồng: {str(dl_err)})*")
