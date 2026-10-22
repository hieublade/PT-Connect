from typing import Any, Dict, List, Optional
from datetime import datetime
import streamlit as st
from api.student_api import StudentApi
from api.booking_api import BookingApi
from api.auth_api import AuthApi
from api.client import ApiException
from components.pt_card import render_pt_card, format_currency_vnd
from components.booking_table import render_booking_table, format_booking_datetime


def render_student_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Học viên (Student Dashboard) - Hoàn thiện theo Milestone 6."""

    full_name = user.get("fullName", "Học viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")
    avatar_url = user.get("avatarUrl")

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

    # Header chào mừng tích hợp Avatar người dùng (Milestone 6)
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(25, 118, 210, 0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    {"<img src='" + avatar_url + "' style='width: 68px; height: 68px; border-radius: 50%; object-fit: cover; border: 3px solid white;' />" if avatar_url else "<div style='width: 68px; height: 68px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 2.2rem;'>👤</div>"}
                    <div>
                        <h2 style="margin: 0; color: white; font-weight: 700;">👋 Chào mừng bạn, {full_name}!</h2>
                        <p style="margin: 0.4rem 0 0 0; opacity: 0.92; font-size: 1.05rem;">
                            Không gian rèn luyện, đặt lịch Huấn luyện viên & quản lý hợp đồng tập luyện tại PT Connect
                        </p>
                    </div>
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

    # Các hằng số định danh Tab điều hướng (Milestone 6)
    NAV_EXPLORE = "🔍 Khám Phá PT"
    NAV_DETAIL = "🏋️ Chi Tiết & Mua Khóa"
    NAV_BOOKING = "📅 Đặt Lịch Tập"
    NAV_MY_SCHEDULE = "🗓️ Lịch Của Tôi"
    NAV_COURSES = f"📜 Khóa Của Tôi ({len(my_enrollments)})"
    NAV_WALLET = "💳 Ví Tiền"
    NAV_PROFILE = "👤 Hồ Sơ & Avatar"

    nav_tabs = [NAV_EXPLORE, NAV_DETAIL, NAV_BOOKING, NAV_MY_SCHEDULE, NAV_COURSES, NAV_WALLET, NAV_PROFILE]

    if "student_active_tab" not in st.session_state:
        st.session_state["student_active_tab"] = NAV_EXPLORE

    # Thanh điều hướng dạng Tab Bar tương tác mượt mà
    cols = st.columns(len(nav_tabs))
    for col, tab_name in zip(cols, nav_tabs):
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

            def handle_pt_selection(p):
                st.session_state["selected_pt_id"] = p.get("id")
                st.session_state["student_active_tab"] = NAV_DETAIL
                st.rerun()

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
    # TAB 2: CHI TIẾT HUẤN LUYỆN VIÊN & MUA KHÓA HỌC (MILESTONE 5)
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
    # TAB 3: ĐẶT LỊCH TẬP (MILESTONE 6 - HIỆU & HUY)
    # -------------------------------------------------------------------------
    elif active_tab == NAV_BOOKING:
        st.subheader("📅 Đặt Lịch Tập Cùng Huấn Luyện Viên (Milestone 6)")
        st.caption("Hệ thống bảo vệ giao dịch chống đặt trùng (409 Conflict) với khóa bi quan PESSIMISTIC_WRITE.")

        booking_type_choice = st.radio(
            "Hình thức đặt lịch:",
            ["📜 Đặt theo Gói Khóa Học (PACKAGE)", "🎁 Buổi Học Thử Miễn Phí (TRIAL)"],
            horizontal=True
        )

        is_trial = "TRIAL" in booking_type_choice

        if not is_trial:
            # 1. ĐẶT THEO GÓI HỢP ĐỒNG (PACKAGE)
            valid_enrollments = [
                e for e in my_enrollments
                if e.get("status") == "ACTIVE" and e.get("remainingSessions", 0) > 0
            ]

            if not valid_enrollments:
                st.warning(
                    """
                    ⚠️ **Bạn chưa có hợp đồng khóa học nào còn buổi tập khả dụng!**
                    Vui lòng chuyển sang Tab **Khám Phá PT** hoặc **Chi Tiết & Mua Khóa** để đăng ký khóa học,
                    hoặc chọn hình thức **Buổi Học Thử Miễn Phí (TRIAL)** ở trên.
                    """
                )
            else:
                enroll_map = {
                    e["id"]: f"Hợp đồng #{e['id']} - {e.get('courseTitle', 'Khóa học')} (HLV: {e.get('ptName')} - Còn {e.get('remainingSessions')} buổi)"
                    for e in valid_enrollments
                }

                chosen_enroll_id = st.selectbox(
                    "Chọn hợp đồng sử dụng cho ca tập:",
                    options=list(enroll_map.keys()),
                    format_func=lambda x: enroll_map.get(x, str(x))
                )

                chosen_enroll = next(e for e in valid_enrollments if e["id"] == chosen_enroll_id)
                pt_id = chosen_enroll.get("ptId")

                # Lấy danh sách slot AVAILABLE của PT này
                slots: List[Dict[str, Any]] = []
                try:
                    slots = StudentApi.get_pt_slots(pt_id)
                except Exception as ex:
                    st.error(f"❌ Lỗi tải khung giờ trống của HLV: {str(ex)}")

                if not slots:
                    st.info(f"Huấn luyện viên **{chosen_enroll.get('ptName')}** hiện chưa mở khung giờ trống nào trong tương lai. Vui lòng liên hệ HLV để mở thêm lịch.")
                else:
                    slot_map = {
                        s["id"]: f"Slot #{s['id']} | {format_booking_datetime(s.get('startTime'))} ➔ {format_booking_datetime(s.get('endTime'))}"
                        for s in slots
                    }

                    chosen_slot_id = st.selectbox(
                        "Chọn khung giờ tập luyện khả dụng:",
                        options=list(slot_map.keys()),
                        format_func=lambda x: slot_map.get(x, str(x))
                    )

                    student_note = st.text_area(
                        "Ghi chú cho Huấn luyện viên (tùy chọn):",
                        placeholder="Ví dụ: Mong muốn tập trung bài Squat và Deadlift, hoặc thể trạng hơi mệt mỏi...",
                        max_chars=255
                    )

                    with st.container(border=True):
                        st.markdown("#### 📋 Xác Nhận Chi Tiết Đặt Lịch")
                        st.markdown(f"- **Hợp đồng:** `{chosen_enroll.get('courseTitle')}` (Mã: PTC-HD-{chosen_enroll_id:06d})")
                        st.markdown(f"- **Huấn luyện viên:** `{chosen_enroll.get('ptName')}`")
                        st.markdown(f"- **Địa điểm tập:** `{chosen_enroll.get('trainingLocation')}`")
                        st.markdown(f"- **Số buổi tập còn lại sau ca này:** `{chosen_enroll.get('remainingSessions') - 1} buổi`")

                        if st.button("🚀 Xác Nhận Đặt Lịch Ca Tập", type="primary", use_container_width=True):
                            with st.spinner("Đang thực hiện kiểm tra slot và trừ 1 buổi tập..."):
                                try:
                                    bk_res = BookingApi.create_booking(
                                        slot_id=chosen_slot_id,
                                        booking_type="PACKAGE",
                                        enrollment_id=chosen_enroll_id,
                                        student_note=student_note.strip() if student_note else None
                                    )
                                    st.success(f"🎉 Đặt lịch ca tập thành công (Mã đơn: #{bk_res.get('id')})! Ca tập đang chờ HLV phê duyệt.")
                                    st.session_state["student_active_tab"] = NAV_MY_SCHEDULE
                                    st.balloons()
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"❌ Không thể đặt lịch [{e.status_code}]: {e.message}")
                                except Exception as ex:
                                    st.error(f"❌ Lỗi hệ thống: {str(ex)}")

        else:
            # 2. ĐẶT BUỔI HỌC THỬ MIỄN PHÍ (TRIAL)
            st.info("💡 **Chính sách học thử:** Mỗi học viên được đặt 01 buổi học thử miễn phí với mỗi Huấn luyện viên.")

            all_pts = []
            try:
                all_pts = StudentApi.get_pt_profiles()
            except Exception:
                all_pts = []

            if not all_pts:
                st.warning("Hiện chưa có Huấn luyện viên nào khả dụng.")
            else:
                pt_map = {p["id"]: f"{p['fullName']} (⭐ {float(p.get('averageRating', 0)):.1f} - {p.get('experienceYears', 0)} năm KN)" for p in all_pts}
                chosen_pt_id = st.selectbox(
                    "Chọn Huấn luyện viên bạn muốn học thử:",
                    options=list(pt_map.keys()),
                    format_func=lambda x: pt_map.get(x, str(x))
                )

                chosen_pt = next(p for p in all_pts if p["id"] == chosen_pt_id)

                slots: List[Dict[str, Any]] = []
                try:
                    slots = StudentApi.get_pt_slots(chosen_pt_id)
                except Exception as ex:
                    st.error(f"❌ Lỗi: {str(ex)}")

                if not slots:
                    st.info(f"Huấn luyện viên **{chosen_pt.get('fullName')}** chưa mở khung giờ trống nào.")
                else:
                    slot_map = {
                        s["id"]: f"Slot #{s['id']} | {format_booking_datetime(s.get('startTime'))} ➔ {format_booking_datetime(s.get('endTime'))}"
                        for s in slots
                    }

                    chosen_slot_id = st.selectbox(
                        "Chọn khung giờ học thử:",
                        options=list(slot_map.keys()),
                        format_func=lambda x: slot_map.get(x, str(x))
                    )

                    student_note = st.text_area(
                        "Mục tiêu buổi học thử (tùy chọn):",
                        placeholder="Ví dụ: Đánh giá thể lực, tư vấn lộ trình tăng cơ giảm mỡ...",
                        max_chars=255,
                        key="trial_student_note"
                    )

                    with st.container(border=True):
                        st.markdown("#### 🎁 Chi Tiết Buổi Học Thử (TRIAL)")
                        st.markdown(f"- **Huấn luyện viên:** `{chosen_pt.get('fullName')}`")
                        st.markdown(f"- **Khu vực hoạt động:** `{chosen_pt.get('availableLocations')}`")
                        st.markdown(f"- **Chi phí:** `0 đ (Miễn phí)`")

                        if st.button("🚀 Đặt Buổi Học Thử Ngay", type="primary", use_container_width=True):
                            with st.spinner("Đang gửi yêu cầu đặt lịch học thử..."):
                                try:
                                    bk_res = BookingApi.create_booking(
                                        slot_id=chosen_slot_id,
                                        booking_type="TRIAL",
                                        enrollment_id=None,
                                        student_note=student_note.strip() if student_note else None
                                    )
                                    st.success(f"🎉 Đặt buổi học thử thành công (Mã đơn: #{bk_res.get('id')})! Đang chờ HLV phê duyệt.")
                                    st.session_state["student_active_tab"] = NAV_MY_SCHEDULE
                                    st.balloons()
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"❌ Không thể đặt học thử [{e.status_code}]: {e.message}")
                                except Exception as ex:
                                    st.error(f"❌ Lỗi: {str(ex)}")

    # -------------------------------------------------------------------------
    # TAB 4: LỊCH CỦA TÔI (MILESTONE 6 - HIỆU)
    # -------------------------------------------------------------------------
    elif active_tab == NAV_MY_SCHEDULE:
        st.subheader("🗓️ Lịch Tập Luyện Của Tôi (Milestone 6)")
        st.caption("Theo dõi tiến độ duyệt lịch, các ca tập sắp diễn ra và lịch sử tập luyện.")

        col_st_filter, col_st_refresh = st.columns([4, 1])
        with col_st_filter:
            status_filter = st.selectbox(
                "Lọc ca tập theo trạng thái:",
                ["ALL", "PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"],
                format_func=lambda x: {
                    "ALL": "📌 Tất cả ca tập",
                    "PENDING": "⏳ Chờ HLV duyệt (PENDING)",
                    "CONFIRMED": "✅ Đã xác nhận / Sắp tới (CONFIRMED)",
                    "COMPLETED": "🎉 Đã hoàn thành (COMPLETED)",
                    "CANCELLED": "❌ Đã hủy (CANCELLED)"
                }.get(x, x),
                index=0
            )
        with col_st_refresh:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Làm mới", key="btn_refresh_my_schedule", use_container_width=True):
                st.rerun()

        my_bookings: List[Dict[str, Any]] = []
        try:
            st_param = None if status_filter == "ALL" else status_filter
            my_bookings = BookingApi.get_my_bookings(status=st_param)
        except ApiException as e:
            st.error(f"❌ Lỗi tải lịch tập [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"❌ Lỗi: {str(ex)}")

        render_booking_table(
            bookings=my_bookings,
            is_pt_view=False
        )

    # -------------------------------------------------------------------------
    # TAB 5: KHÓA HỌC CỦA TÔI & TẢI HỢP ĐỒNG PDF (MILESTONE 5)
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
                        prog = (rem_s / total_s) if total_s > 0 else 0
                        st.markdown(f"**Số buổi còn lại:** `{rem_s} / {total_s} buổi`")
                        st.progress(prog)

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

                    col_bk_action, col_dl = st.columns([2, 1])
                    with col_bk_action:
                        if rem_s > 0 and e_status == "ACTIVE":
                            if st.button(f"📅 Đặt lịch tập cho gói này", key=f"btn_book_from_enroll_{e_id}", type="primary"):
                                st.session_state["student_active_tab"] = NAV_BOOKING
                                st.rerun()
                    with col_dl:
                        try:
                            pdf_bytes = StudentApi.download_contract(e_id)
                            st.download_button(
                                label="📄 Tải Hợp Đồng PDF",
                                data=pdf_bytes,
                                file_name=f"HopDong_PTConnect_{e_id}.pdf",
                                mime="application/pdf",
                                key=f"dl_contract_btn_{e_id}",
                                use_container_width=True
                            )
                        except Exception as dl_err:
                            st.caption(f"*(Chưa tải được hợp đồng: {str(dl_err)})*")

    # -------------------------------------------------------------------------
    # TAB 6: VÍ TIỀN & NẠP TIỀN (MILESTONE 5)
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
                st.caption("🔒 *Lưu ý: Tiền trong ví chỉ dùng trong môi trường giả lập nền tảng PT Connect.*")

        with col_w_topup:
            with st.container(border=True):
                st.markdown("#### ⚡ Nạp Tiền Vào Ví")

                st.markdown("**Chọn nhanh mệnh giá:**")
                q_cols = st.columns(4)
                if "quick_topup_amount" not in st.session_state:
                    st.session_state["quick_topup_amount"] = 2000000.0

                quick_amounts = [1000000.0, 2000000.0, 5000000.0, 10000000.0]
                for idx, amt in enumerate(quick_amounts):
                    with q_cols[idx]:
                        if st.button(f"{int(amt/1000000)}Tr", key=f"q_amt_{int(amt)}", use_container_width=True):
                            st.session_state["quick_topup_amount"] = amt

                entered_amount = st.number_input(
                    "Hoặc nhập số tiền tùy chọn (VND):",
                    min_value=10000.0,
                    max_value=100000000.0,
                    step=100000.0,
                    value=float(st.session_state["quick_topup_amount"]),
                    key="student_topup_amount_input"
                )

                method_code = st.selectbox(
                    "Phương thức nạp mô phỏng:",
                    options=["VNPAY", "MOMO", "BANK_TRANSFER"],
                    format_func=lambda x: {"VNPAY": "Cổng VNPAY QR", "MOMO": "Ví điện tử MoMo", "BANK_TRANSFER": "Chuyển khoản ngân hàng"}.get(x, x)
                )

                if st.button("🚀 Nạp Tiền Ngay", type="primary", use_container_width=True):
                    with st.spinner("Đang xử lý nạp tiền vào ví..."):
                        try:
                            topup_res = StudentApi.topup_wallet(amount=entered_amount, payment_method=method_code)
                            st.success(f"✅ Nạp thành công {format_currency_vnd(entered_amount)}! Mã GD: {topup_res.get('transactionRef')}")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Nạp tiền thất bại [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi: {str(ex)}")

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
    # TAB 7: HỒ SƠ CÁ NHÂN & CẬP NHẬT AVATAR (MILESTONE 6 - HIỆU)
    # -------------------------------------------------------------------------
    elif active_tab == NAV_PROFILE:
        st.subheader("👤 Hồ Sơ Cá Nhân & Ảnh Đại Diện (Milestone 6)")
        st.caption("Cập nhật ảnh đại diện để đồng bộ trên toàn bộ hệ thống đặt lịch.")

        with st.container(border=True):
            st.markdown("### 🖼️ Ảnh Đại Diện (Avatar)")
            col_av_view, col_av_form = st.columns([1, 3])
            with col_av_view:
                if avatar_url:
                    st.image(avatar_url, width=120, caption="Ảnh đại diện hiện tại")
                else:
                    st.markdown(
                        """
                        <div style="width: 120px; height: 120px; border-radius: 50%; background: #e3f2fd; display: flex; align-items: center; justify-content: center; font-size: 3rem; border: 3px solid #1976d2;">
                            👤
                        </div>
                        <div style="font-size: 0.8rem; color: #888; text-align: center; margin-top: 6px;">Chưa có ảnh</div>
                        """,
                        unsafe_allow_html=True
                    )
            with col_av_form:
                new_avatar_val = st.text_input(
                    "Đường dẫn URL ảnh đại diện (CDN / Web):",
                    value=avatar_url or "",
                    placeholder="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde",
                    key="input_student_avatar_url"
                )
                col_sub_av, col_sample_av = st.columns([2, 3])
                with col_sub_av:
                    if st.button("💾 Cập Nhật Avatar", key="btn_update_student_avatar", type="primary", use_container_width=True):
                        if not new_avatar_val.strip():
                            st.error("❌ Vui lòng nhập đường dẫn URL ảnh đại diện!")
                        else:
                            try:
                                AuthApi.update_avatar(new_avatar_val.strip())
                                st.success("✅ Cập nhật ảnh đại diện thành công!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"❌ Cập nhật thất bại [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"❌ Lỗi: {str(ex)}")
                with col_sample_av:
                    if st.button("✨ Dùng ảnh mẫu Học viên", key="btn_sample_student_avatar", use_container_width=True):
                        sample_url = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop"
                        try:
                            AuthApi.update_avatar(sample_url)
                            st.success("✅ Đã áp dụng ảnh mẫu thành công!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ Lỗi: {str(ex)}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 📋 Thông Tin Tài Khoản")
            c_info_a, c_info_b = st.columns(2)
            with c_info_a:
                st.markdown(f"**Họ và tên:** {full_name}")
                st.markdown(f"**Địa chỉ Email:** `{email}`")
            with c_info_b:
                st.markdown(f"**Số điện thoại:** `{phone}`")
                st.markdown(f"**Vai trò hệ thống:** `Học viên (STUDENT)`")
                st.markdown(f"**Trạng thái tài khoản:** `🟢 {status}`")
