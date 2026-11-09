from typing import Any, Dict, List, Optional
from datetime import datetime
import streamlit as st
from api.student_api import StudentApi
from api.booking_api import BookingApi
from api.auth_api import AuthApi
from api.client import ApiException
from components.pt_card import render_pt_card, format_currency_vnd
from components.booking_table import render_booking_table, format_booking_datetime
from components.avatar_uploader import render_avatar_management, normalize_avatar_url


# =============================================================================
# CÁC LỚP BIÊN THÀNH PHẦN (SUB-VIEWS THEO SƠ ĐỒ PHÂN TÍCH BCE)
# =============================================================================

class DiscoveryPTView:
    """Sơ đồ 1: Khám phá & Tìm kiếm Huấn Luyện Viên."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Tìm Kiếm & Khám Phá Huấn Luyện Viên (PT)")

        col_search, col_reset = st.columns([4, 1])
        with col_search:
            search_query = st.text_input(
                "Tìm kiếm theo tên Huấn luyện viên:",
                placeholder="Nhập tên PT (ví dụ: Le Hoang C, Pham Minh D...)",
                key="student_pt_search_input"
            )
        def reset_pt_search():
            st.session_state["student_pt_search_input"] = ""

        with col_reset:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.button("Làm mới", on_click=reset_pt_search, use_container_width=True)

        # Gọi API danh sách PT
        pt_list: List[Dict[str, Any]] = []
        try:
            pt_list = StudentApi.get_pt_profiles(name=search_query)
        except ApiException as e:
            st.error(f"Lỗi tải danh sách PT [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"Lỗi hệ thống: {str(ex)}")

        if not pt_list:
            st.info("Không tìm thấy Huấn luyện viên phù hợp với từ khóa tìm kiếm.")
        else:
            st.markdown(f"**Tìm thấy {len(pt_list)} Huấn luyện viên chuyên nghiệp:**")

            def handle_pt_selection(p):
                pt_id = p.get("id")
                st.session_state["selected_pt_id"] = pt_id
                st.session_state["student_pt_select_box"] = pt_id
                st.session_state["switch_to_tab_name"] = "Chi Tiết"
                st.toast(f"Đang mở hồ sơ chi tiết của Huấn luyện viên {p.get('fullName')}")

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


class ConfirmPurchaseCourseView:
    """Sơ đồ 6: Xác nhận thanh toán & Mua khóa học từ ví."""

    @staticmethod
    def render(course: Dict[str, Any], pt_profile: Dict[str, Any], wallet_balance: float, my_enrollments: List[Dict[str, Any]]):
        c_id = course.get("id")
        c_sessions = course.get("totalSessions", 0)
        c_price = course.get("basePrice", 0)

        with st.expander("Mua Gói Tập Này", expanded=False):
            existing_active_enroll = next(
                (e for e in my_enrollments if e.get("courseId") == c_id and e.get("status") == "ACTIVE" and e.get("remainingSessions", 0) > 0),
                None
            )

            if existing_active_enroll:
                rem_s = existing_active_enroll.get("remainingSessions", 0)
                tot_s = existing_active_enroll.get("totalSessions", c_sessions)
                st.warning(
                    f"⚠️ **Bạn đang theo học khóa này:** Hợp đồng hiện tại còn **{rem_s}/{tot_s} buổi** chưa hoàn thành. "
                    f"Theo quy định, bạn chỉ có thể đăng ký tiếp khóa học này sau khi đã tập xong toàn bộ {tot_s}/{tot_s} buổi."
                )
                st.button("Đang Theo Học (Không Thể Mua Trùng)", key=f"btn_confirm_buy_{c_id}", disabled=True)
            else:
                st.markdown(f"**Học phí thanh toán:** `{format_currency_vnd(c_price)}`")
                st.markdown(f"**Số dư ví hiện tại:** `{format_currency_vnd(wallet_balance)}`")

                has_enough_money = (float(wallet_balance) >= float(c_price))

                if not has_enough_money:
                    shortage = float(c_price) - float(wallet_balance)
                    st.error(f"Số dư ví không đủ! Cần thêm `{format_currency_vnd(shortage)}`. Vui lòng chuyển sang tab Ví Tiền để nạp thêm.")
                else:
                    st.success("Bạn đủ số dư ví để thanh toán gói tập này.")

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

                if st.button("Xác Nhận Thanh Toán & Ký Hợp Đồng", key=f"btn_confirm_buy_{c_id}", type="primary", disabled=not has_enough_money):
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
                                st.success(f"Chúc mừng bạn đã mua khóa học thành công! Mã hợp đồng: PTC-HD-{enroll_res.get('id'):06d}. Bạn có thể xem hợp đồng tại tab Khóa Của Tôi.")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Mua khóa học thất bại [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")


class PTDetailCourseView:
    """Sơ đồ 6: Danh sách gói khóa học của PT đang xem."""

    @staticmethod
    def render(pt_courses: List[Dict[str, Any]], pt_profile: Dict[str, Any], wallet_balance: float, my_enrollments: List[Dict[str, Any]]):
        st.markdown(f"#### Các Gói Tập & Khóa Học Đang Mở Bán ({len(pt_courses)})")
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
                        st.markdown(f"##### {c_title}")
                        if c_desc:
                            st.write(c_desc)
                        st.markdown(
                            f"**Số buổi:** `{c_sessions} buổi` • **Thời hạn:** `{c_validity} ngày` • **Học phí:** <span style='color: #d32f2f; font-weight: 700; font-size: 1.15rem;'>{format_currency_vnd(c_price)}</span>",
                            unsafe_allow_html=True
                        )

                    with col_c_buy:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        ConfirmPurchaseCourseView.render(course, pt_profile, wallet_balance, my_enrollments)


class PTDetailView:
    """Sơ đồ 1 & 6: Chi tiết Huấn luyện viên, Khóa học, Khung giờ và Đánh giá."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Hồ Sơ Chi Tiết & Đăng Ký Khóa Học")

        selected_pt_id = st.session_state.get("selected_pt_id")

        try:
            all_pts = StudentApi.get_pt_profiles()
        except Exception:
            all_pts = []

        if all_pts:
            pt_options = {p.get("id"): f"{p.get('fullName')} (Đánh giá: {float(p.get('averageRating', 0)):.1f}/5 - {p.get('experienceYears', 0)} năm KN)" for p in all_pts}
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
            st.info("Vui lòng chọn một Huấn luyện viên từ Tab **Khám Phá Huấn Luyện Viên** để xem hồ sơ và khóa học.")
        else:
            try:
                pt_profile = StudentApi.get_pt_profile(selected_pt_id)
                pt_courses = StudentApi.get_pt_courses(selected_pt_id)
                pt_slots = StudentApi.get_pt_slots(selected_pt_id)
                pt_reviews = BookingApi.get_pt_reviews(selected_pt_id)

                with st.container(border=True):
                    col_p1, col_p2 = st.columns([1, 3])
                    with col_p1:
                        avatar = normalize_avatar_url(pt_profile.get("avatarUrl")) or "https://api.dicebear.com/7.x/avataaars/svg?seed=" + pt_profile.get("fullName", "").replace(" ", "")
                        st.image(avatar, width=130)
                    with col_p2:
                        st.markdown(f"### {pt_profile.get('fullName')}")
                        st.markdown(
                            f"**Đánh giá:** `{float(pt_profile.get('averageRating', 0)):.1f} / 5.0` ({pt_profile.get('totalReviews', 0)} lượt đánh giá) "
                            f"• **Kinh nghiệm:** `{pt_profile.get('experienceYears', 0)} năm`"
                        )
                        st.markdown(f"**Giới thiệu:** {pt_profile.get('bio') or 'Chưa có tiểu sử.'}")
                        st.markdown(f"**Khu vực nhận dạy:** `{pt_profile.get('availableLocations')}`")
                        pt_phone = pt_profile.get("phone")
                        pt_email = pt_profile.get("email")
                        contacts = []
                        if pt_phone:
                            contacts.append(f"📞 **SĐT / Zalo:** `{pt_phone}`")
                        if pt_email:
                            contacts.append(f"✉️ **Email:** `{pt_email}`")
                        if contacts:
                            st.markdown(" • ".join(contacts))
                        if pt_profile.get("locationPricingNote"):
                            st.caption(f"*Chính sách giá/di chuyển:* {pt_profile.get('locationPricingNote')}")

                st.markdown("---")

                # DANH SÁCH KHÓA HỌC
                PTDetailCourseView.render(pt_courses, pt_profile, self.parent.wallet_balance, self.parent.my_enrollments)

                st.markdown("---")

                # LỊCH GIỜ RẢNH KHẢ DỤNG (SLOTS)
                st.markdown(f"#### Khung Giờ Rảnh Khả Dụng Trong Tương Lai ({len(pt_slots)})")
                st.caption("Chỉ hiển thị các slot ở trạng thái AVAILABLE và chưa bắt đầu.")
                if not pt_slots:
                    contact_parts = []
                    if pt_profile.get("phone"):
                        contact_parts.append(f"SĐT/Zalo: `{pt_profile.get('phone')}`")
                    if pt_profile.get("email"):
                        contact_parts.append(f"Email: `{pt_profile.get('email')}`")
                    contact_text = f" qua {' hoặc '.join(contact_parts)}" if contact_parts else ""
                    st.info(f"Huấn luyện viên hiện chưa mở khung giờ rảnh nào sắp tới. Vui lòng liên hệ HLV{contact_text} để mở lịch tập.")
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
                            "Trạng thái": "Sẵn sàng (AVAILABLE)"
                        })
                    st.dataframe(slots_data, use_container_width=True)

                st.markdown("---")

                # DANH SÁCH ĐÁNH GIÁ TỪ HỌC VIÊN
                st.markdown(f"#### Đánh Giá Từ Học Viên ({len(pt_reviews)})")
                st.caption("Nhận xét thực tế từ các học viên đã hoàn thành ca tập cùng Huấn luyện viên.")

                if not pt_reviews:
                    st.info("Chưa có lượt đánh giá nào cho Huấn luyện viên này.")
                else:
                    for rev in pt_reviews:
                        r_rating = rev.get("rating", 5)
                        r_comment = rev.get("comment", "Không có nhận xét")
                        r_student = rev.get("studentName", "Học viên")
                        st.markdown(
                            f"""
                            <div style="background: #f9fbe7; border-left: 4px solid #827717; padding: 10px 14px; border-radius: 4px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong>{r_student}</strong>
                                    <span>({r_rating}/5 sao)</span>
                                </div>
                                <div style="margin-top: 4px; color: #333;">{r_comment}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            except ApiException as e:
                st.error(f"Lỗi tải hồ sơ PT [{e.status_code}]: {e.message}")
            except Exception as ex:
                st.error(f"Lỗi: {str(ex)}")


class BookingPackageView:
    """Sơ đồ 5: Đặt lịch ca tập theo gói hợp đồng hoặc học thử."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Đặt Lịch Tập Cùng Huấn Luyện Viên")
        booking_type_choice = st.radio(
            "Hình thức đặt lịch:",
            ["Đặt theo Gói Khóa Học (PACKAGE)", "Buổi Học Thử Miễn Phí (TRIAL)"],
            horizontal=True
        )

        is_trial = "TRIAL" in booking_type_choice

        if not is_trial:
            # 1. ĐẶT THEO GÓI HỢP ĐỒNG (PACKAGE)
            valid_enrollments = [
                e for e in self.parent.my_enrollments
                if e.get("status") == "ACTIVE" and e.get("remainingSessions", 0) > 0
            ]

            if not valid_enrollments:
                st.warning(
                    """
                    **Bạn chưa có hợp đồng khóa học nào còn buổi tập khả dụng!**
                    Vui lòng chuyển sang Tab **Khám Phá PT** hoặc **Chi Tiết** để đăng ký khóa học,
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

                slots: List[Dict[str, Any]] = []
                try:
                    slots = StudentApi.get_pt_slots(pt_id)
                except Exception as ex:
                    st.error(f"Lỗi tải khung giờ trống của HLV: {str(ex)}")

                # Lọc khung giờ còn nằm trong thời hạn hợp đồng
                end_date_str = chosen_enroll.get("endDate")
                valid_slots = []
                for s in slots:
                    try:
                        s_date = datetime.fromisoformat(s.get("startTime", "")).date()
                        if end_date_str:
                            e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                            if s_date > e_date:
                                continue
                    except Exception:
                        pass
                    valid_slots.append(s)

                if not valid_slots:
                    pt_phone = None
                    pt_email = None
                    try:
                        p_info = StudentApi.get_pt_profile(pt_id)
                        pt_phone = p_info.get("phone")
                        pt_email = p_info.get("email")
                    except Exception:
                        pass
                    contact_parts = []
                    if pt_phone:
                        contact_parts.append(f"Hotline/Zalo: **{pt_phone}**")
                    if pt_email:
                        contact_parts.append(f"Email: **{pt_email}**")
                    contact_text = f" qua {' hoặc '.join(contact_parts)}" if contact_parts else ""
                    if slots and end_date_str:
                        st.warning(f"Các khung giờ hiện có của Huấn luyện viên đều diễn ra sau thời hạn kết thúc hợp đồng ({end_date_str}). Vui lòng liên hệ HLV{contact_text} để mở lịch trong thời hạn hợp đồng.")
                    else:
                        st.info(f"Huấn luyện viên **{chosen_enroll.get('ptName')}** hiện chưa mở khung giờ trống nào trong tương lai. Vui lòng liên hệ HLV{contact_text} để mở thêm lịch.")
                else:
                    slot_map = {
                        s["id"]: f"Slot #{s['id']} | {format_booking_datetime(s.get('startTime'))} - {format_booking_datetime(s.get('endTime'))}"
                        for s in valid_slots
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
                        st.markdown("#### Xác Nhận Chi Tiết Đặt Lịch")
                        st.markdown(f"- **Hợp đồng:** `{chosen_enroll.get('courseTitle')}` (Mã: PTC-HD-{chosen_enroll_id:06d})")
                        st.markdown(f"- **Huấn luyện viên:** `{chosen_enroll.get('ptName')}`")
                        st.markdown(f"- **Địa điểm tập:** `{chosen_enroll.get('trainingLocation')}`")
                        st.markdown(f"- **Số buổi tập còn lại sau ca này:** `{chosen_enroll.get('remainingSessions') - 1} buổi`")

                        if st.button("Xác Nhận Đặt Lịch Ca Tập", type="primary", use_container_width=True):
                            with st.spinner("Đang thực hiện kiểm tra slot và trừ 1 buổi tập..."):
                                try:
                                    bk_res = BookingApi.create_booking(
                                        slot_id=chosen_slot_id,
                                        booking_type="PACKAGE",
                                        enrollment_id=chosen_enroll_id,
                                        student_note=student_note.strip() if student_note else None
                                    )
                                    st.success(f"Đặt lịch ca tập thành công (Mã đơn: #{bk_res.get('id')})! Ca tập đang chờ HLV phê duyệt. Bạn có thể theo dõi tiến độ tại tab Lịch Của Tôi.")
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"Không thể đặt lịch [{e.status_code}]: {e.message}")
                                except Exception as ex:
                                    st.error(f"Lỗi hệ thống: {str(ex)}")

        else:
            # 2. ĐẶT BUỔI HỌC THỬ MIỄN PHÍ (TRIAL)
            st.info("**Chính sách học thử:** Mỗi học viên được đặt 01 buổi học thử miễn phí với mỗi Huấn luyện viên.")

            all_pts = []
            try:
                all_pts = StudentApi.get_pt_profiles()
            except Exception:
                all_pts = []

            if not all_pts:
                st.warning("Hiện chưa có Huấn luyện viên nào khả dụng.")
            else:
                pt_map = {p["id"]: f"{p['fullName']} ({float(p.get('averageRating', 0)):.1f} sao - {p.get('experienceYears', 0)} năm KN)" for p in all_pts}
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
                    st.error(f"Lỗi: {str(ex)}")

                if not slots:
                    contact_parts = []
                    if chosen_pt.get("phone"):
                        contact_parts.append(f"Hotline/Zalo: **{chosen_pt.get('phone')}**")
                    if chosen_pt.get("email"):
                        contact_parts.append(f"Email: **{chosen_pt.get('email')}**")
                    contact_text = f" qua {' hoặc '.join(contact_parts)}" if contact_parts else ""
                    st.info(f"Huấn luyện viên **{chosen_pt.get('fullName')}** chưa mở khung giờ trống nào. Vui lòng liên hệ HLV{contact_text} để được hỗ trợ mở lịch.")
                else:
                    slot_map = {
                        s["id"]: f"Slot #{s['id']} | {format_booking_datetime(s.get('startTime'))} - {format_booking_datetime(s.get('endTime'))}"
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
                        st.markdown("#### Chi Tiết Buổi Học Thử (TRIAL)")
                        st.markdown(f"- **Huấn luyện viên:** `{chosen_pt.get('fullName')}`")
                        st.markdown(f"- **Khu vực hoạt động:** `{chosen_pt.get('availableLocations')}`")
                        st.markdown(f"- **Chi phí:** `0 đ (Miễn phí)`")

                        if st.button("Đặt Buổi Học Thử Ngay", type="primary", use_container_width=True):
                            with st.spinner("Đang gửi yêu cầu đặt lịch học thử..."):
                                try:
                                    bk_res = BookingApi.create_booking(
                                        slot_id=chosen_slot_id,
                                        booking_type="TRIAL",
                                        enrollment_id=None,
                                        student_note=student_note.strip() if student_note else None
                                    )
                                    st.success(f"Đặt buổi học thử thành công (Mã đơn: #{bk_res.get('id')})! Đang chờ HLV phê duyệt. Bạn có thể theo dõi tiến độ tại tab Lịch Của Tôi.")
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"Không thể đặt học thử [{e.status_code}]: {e.message}")
                                except Exception as ex:
                                    st.error(f"Lỗi: {str(ex)}")


class MyScheduleView:
    """Sơ đồ 4: Quản lý lịch tập cá nhân của học viên."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Lịch Tập Luyện Của Tôi")

        col_st_filter, col_st_refresh = st.columns([4, 1])
        with col_st_filter:
            status_filter = st.selectbox(
                "Lọc ca tập theo trạng thái:",
                ["ALL", "PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"],
                format_func=lambda x: {
                    "ALL": "Tất cả ca tập",
                    "PENDING": "Chờ HLV duyệt (PENDING)",
                    "CONFIRMED": "Đã xác nhận / Sắp tới (CONFIRMED)",
                    "COMPLETED": "Đã hoàn thành (COMPLETED)",
                    "CANCELLED": "Đã hủy (CANCELLED)"
                }.get(x, x),
                index=0
            )
        with col_st_refresh:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Làm mới", key="btn_refresh_my_schedule", use_container_width=True):
                st.rerun()

        my_bookings: List[Dict[str, Any]] = []
        try:
            st_param = None if status_filter == "ALL" else status_filter
            my_bookings = BookingApi.get_my_bookings(status=st_param)
        except ApiException as e:
            st.error(f"Lỗi tải lịch tập [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"Lỗi: {str(ex)}")

        render_booking_table(
            bookings=my_bookings,
            is_pt_view=False
        )


class MyCourseView:
    """Sơ đồ 3: Quản lý khóa học đã mua, tải hợp đồng PDF và xem giáo án bài tập."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Danh Sách Gói Tập Đã Đăng Ký & Hợp Đồng")

        if not self.parent.my_enrollments:
            st.info("Bạn chưa đăng ký khóa học nào. Hãy khám phá và chọn Huấn luyện viên phù hợp ở tab Khám Phá PT nhé!")
        else:
            for enroll in self.parent.my_enrollments:
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
                        st.markdown(f"#### {c_title} • PTC-HD-{e_id:06d}")
                    with col_top_status:
                        st.markdown(f"<div style='text-align: right;'><b>Trạng thái:</b> <code>{e_status}</code></div>", unsafe_allow_html=True)

                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown(f"**Huấn luyện viên phụ trách:** `{pt_name}`")
                        st.markdown(f"**Địa điểm tập cố định:** `{loc}`")
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
                            pt_id = enroll.get("ptId")
                            if st.button(f"Đặt lịch tập cho gói này", key=f"btn_book_from_enroll_{e_id}", type="primary"):
                                st.session_state["selected_pt_id"] = pt_id
                                st.info("Đã chọn hợp đồng. Vui lòng chuyển sang tab Đặt Lịch Tập để chọn khung giờ.")
                    with col_dl:
                        try:
                            pdf_bytes = StudentApi.download_contract(e_id)
                            st.download_button(
                                label="Tải Hợp Đồng PDF",
                                data=pdf_bytes,
                                file_name=f"HopDong_PTConnect_{e_id}.pdf",
                                mime="application/pdf",
                                key=f"dl_contract_btn_{e_id}",
                                use_container_width=True
                            )
                        except Exception as dl_err:
                            st.caption(f"*(Chưa tải được hợp đồng: {str(dl_err)})*")

                    # GIÁO ÁN VÀ BÀI TẬP HUẤN LUYỆN
                    with st.expander("Xem Giáo Án & Bài Tập Của Khóa Học", expanded=False):
                        plans = []
                        try:
                            plans = StudentApi.get_workout_plans(e_id)
                        except Exception:
                            plans = []

                        if not plans:
                            st.info("Huấn luyện viên chưa tải lên giáo án cho khóa học này. Hãy liên hệ HLV để nhận lộ trình tập luyện!")
                        else:
                            for plan in plans:
                                st.markdown(f"##### {plan.get('title')}")
                                p_goal = plan.get("goal")
                                p_start = plan.get("startDate")
                                p_end = plan.get("endDate")
                                if p_goal:
                                    st.caption(f"**Mục tiêu:** {p_goal}")
                                if p_start and p_end:
                                    st.caption(f"**Thời hạn:** từ `{p_start}` đến `{p_end}`")

                                workouts = plan.get("workouts", [])
                                if not workouts:
                                    st.caption("*(Chưa có danh sách bài tập chi tiết)*")
                                else:
                                    workout_rows = []
                                    for w in workouts:
                                        workout_rows.append({
                                            "Tên bài tập": w.get("exerciseName"),
                                            "Nhóm cơ": w.get("targetMuscle") or "-",
                                            "Số Sets": w.get("sets", 3),
                                            "Số Reps": w.get("reps", 10),
                                            "Mức tạ": f"{w.get('weightKg')} kg" if w.get("weightKg") else "-",
                                            "Nghỉ giữa hiệp": f"{w.get('restSeconds', 60)} giây",
                                            "Video demo": w.get("videoDemoUrl") or ""
                                        })
                                    st.dataframe(workout_rows, use_container_width=True)


class WalletView:
    """Sơ đồ 2: Quản lý ví điện tử nội bộ, nạp tiền, rút tiền và lịch sử giao dịch."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Quản Lý Ví Điện Tử Nội Bộ (Nạp & Rút Tiền)")

        balance = float(self.parent.wallet_balance or 0)
        locked_balance = float(self.parent.wallet_data.get("lockedBalance", 0) or 0)
        available_balance = max(0.0, balance - locked_balance)
        wallet_status = self.parent.wallet_data.get("status", "ACTIVE")

        col_w_left, col_w_right = st.columns([1, 1], gap="medium")

        with col_w_left:
            with st.container(border=True):
                st.markdown("#### 💰 Số Dư & Nạp Tiền Vào Ví")
                st.markdown(f"**Chủ tài khoản:** {self.parent.full_name}")
                st.markdown(f"**Trạng thái ví:** `{wallet_status}`")
                st.markdown(
                    f"""
                    <div style="background: #e3f2fd; padding: 1.2rem; border-radius: 10px; margin: 0.8rem 0; border-left: 5px solid #1976d2;">
                        <span style="font-size: 0.95rem; color: #0d47a1; font-weight: 500;">Số Dư Khả Dụng:</span>
                        <div style="font-size: 1.8rem; font-weight: 800; color: #1565c0; margin-top: 4px;">
                            {format_currency_vnd(balance)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("**Chọn nhanh mệnh giá nạp:**")
                q_cols = st.columns(4)
                if "student_topup_amount_input" not in st.session_state:
                    st.session_state["student_topup_amount_input"] = 2000000.0

                def handle_quick_amount_click(amount_val: float):
                    st.session_state["student_topup_amount_input"] = float(amount_val)

                quick_amounts = [1000000.0, 2000000.0, 5000000.0, 10000000.0]
                for idx, amt in enumerate(quick_amounts):
                    with q_cols[idx]:
                        st.button(
                            f"{int(amt/1000000)}Tr",
                            key=f"q_amt_{int(amt)}",
                            on_click=handle_quick_amount_click,
                            args=(amt,),
                            use_container_width=True
                        )

                entered_amount = st.number_input(
                    "Hoặc nhập số tiền nạp tùy chọn (VND):",
                    min_value=10000.0,
                    max_value=100000000.0,
                    step=100000.0,
                    key="student_topup_amount_input"
                )

                method_code = st.selectbox(
                    "Phương thức nạp mô phỏng:",
                    options=["BANK_TRANSFER", "CREDIT_CARD", "CASH"],
                    format_func=lambda x: {
                        "BANK_TRANSFER": "Chuyển khoản ngân hàng (Quét mã VNPAY QR / MoMo / VietQR)",
                        "CREDIT_CARD": "Thẻ tín dụng / Ghi nợ quốc tế (Visa, Mastercard)",
                        "CASH": "Nạp tiền mặt tại quầy lễ tân"
                    }.get(x, x),
                    key="student_topup_payment_method"
                )

                if st.button("➕ Nạp Tiền Ngay", type="primary", use_container_width=True):
                    with st.spinner("Đang xử lý nạp tiền vào ví..."):
                        try:
                            topup_res = StudentApi.topup_wallet(amount=entered_amount, payment_method=method_code)
                            st.success(f"Nạp thành công {format_currency_vnd(entered_amount)}! Mã GD: {topup_res.get('transactionRef')}")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"Nạp tiền thất bại [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"Lỗi: {str(ex)}")

        with col_w_right:
            with st.container(border=True):
                st.markdown("#### 🏦 Rút Tiền Về Tài Khoản Ngân Hàng")
                st.caption("Rút lại số dư chưa sử dụng hoặc tiền hoàn/đền bù trong ví về tài khoản ngân hàng cá nhân.")

                if available_balance < 50000:
                    st.info(
                        f"Số dư khả dụng hiện tại là **{format_currency_vnd(available_balance)}**. "
                        f"Cần tối thiểu **50.000 ₫** để thực hiện lệnh rút tiền về ngân hàng."
                    )
                else:
                    st.markdown(f"**Số dư tối đa có thể rút:** `{format_currency_vnd(available_balance)}`")

                    withdraw_amt = st.number_input(
                        "Số tiền muốn rút (tối thiểu 50,000 VND):",
                        min_value=50000.0,
                        max_value=max(50000.0, available_balance),
                        value=min(500000.0, available_balance) if available_balance >= 500000.0 else available_balance,
                        step=50000.0,
                        key="student_withdraw_amount_input"
                    )

                    bank_list = [
                        "Vietcombank (VCB - Ngân hàng Ngoại thương)",
                        "Techcombank (TCB - Ngân hàng Kỹ thương)",
                        "MBBank (MB - Ngân hàng Quân đội)",
                        "VietinBank (CTG - Ngân hàng Công thương)",
                        "BIDV (Ngân hàng Đầu tư và Phát triển)",
                        "ACB (Ngân hàng Á Châu)",
                        "TPBank (Ngân hàng Tiên Phong)",
                        "VPBank (Ngân hàng Việt Nam Thịnh vượng)"
                    ]
                    selected_bank = st.selectbox(
                        "Chọn ngân hàng thụ hưởng:",
                        options=bank_list,
                        key="student_withdraw_bank"
                    )
                    clean_bank_name = selected_bank.split(" (")[0]

                    acc_number = st.text_input(
                        "Số tài khoản nhận tiền:",
                        value="0123456789",
                        key="student_withdraw_acc_num"
                    )

                    acc_name = st.text_input(
                        "Tên chủ tài khoản (In hoa không dấu):",
                        value=self.parent.full_name.upper(),
                        key="student_withdraw_acc_name"
                    )

                    st.caption("ℹ️ *Hệ thống mô phỏng lệnh chuyển khoản liên ngân hàng 24/7 tức thì.*")

                    if st.button("💸 Xác Nhận Rút Tiền", type="primary", use_container_width=True, key="btn_student_withdraw"):
                        if not acc_number.strip():
                            st.error("Vui lòng nhập số tài khoản nhận tiền.")
                        elif not acc_name.strip():
                            st.error("Vui lòng nhập tên chủ tài khoản.")
                        elif withdraw_amt > available_balance:
                            st.error(f"Số tiền rút ({format_currency_vnd(withdraw_amt)}) vượt quá số dư khả dụng.")
                        else:
                            with st.spinner("Đang thực hiện chuyển khoản..."):
                                try:
                                    res = StudentApi.withdraw_wallet(
                                        amount=withdraw_amt,
                                        bank_name=clean_bank_name,
                                        account_number=acc_number.strip(),
                                        account_name=acc_name.strip()
                                    )
                                    st.success(
                                        f"Rút thành công {format_currency_vnd(withdraw_amt)} về STK {acc_number.strip()} ({clean_bank_name})! Mã GD: {res.get('transactionRef')}"
                                    )
                                    st.rerun()
                                except ApiException as e:
                                    st.error(f"Lỗi rút tiền [{e.status_code}]: {e.message}")
                                except Exception as ex:
                                    st.error(f"Lỗi: {str(ex)}")

        st.markdown("---")
        st.subheader("Lịch Sử Giao Dịch Tài Chính")
        txns = self.parent.wallet_data.get("transactions", [])
        if not txns:
            st.info("Chưa có giao dịch tài chính nào phát sinh.")
        else:
            table_data = []
            for t in txns:
                txn_type = t.get("paymentType", "")
                t_ref = str(t.get("transactionRef", ""))
                amt = t.get("amount", 0)

                if "WITHDRAW" in t_ref:
                    type_badge = "RÚT TIỀN"
                    amt_str = f"-{format_currency_vnd(amt)}"
                elif txn_type == "TOPUP":
                    type_badge = "NẠP TIỀN"
                    amt_str = f"+{format_currency_vnd(amt)}"
                elif txn_type == "PURCHASE_PACKAGE":
                    type_badge = "MUA KHÓA"
                    amt_str = f"-{format_currency_vnd(amt)}"
                elif txn_type == "REFUND":
                    type_badge = "HOÀN TIỀN"
                    amt_str = f"+{format_currency_vnd(amt)}"
                elif txn_type == "COMPENSATION":
                    type_badge = "ĐỀN BÙ"
                    amt_str = f"+{format_currency_vnd(amt)}"
                else:
                    type_badge = txn_type
                    amt_str = f"{format_currency_vnd(amt)}"

                table_data.append({
                    "Mã Giao Dịch": t_ref,
                    "Loại GD": type_badge,
                    "Số Tiền": amt_str,
                    "Phương Thức": t.get("paymentMethod"),
                    "Trạng Thái": t.get("status"),
                    "Thời Gian": t.get("createdAt", "")[:19].replace("T", " ") if t.get("createdAt") else ""
                })
            st.dataframe(table_data, use_container_width=True)


class ProfileView:
    """Sơ đồ 7: Quản lý hồ sơ cá nhân và ảnh đại diện Avatar."""

    def __init__(self, parent: "StudentHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Hồ Sơ Cá Nhân & Ảnh Đại Diện")

        # Widget Quản lý & Tải lên Avatar
        render_avatar_management(self.parent.user, "STUDENT")

        with st.container(border=True):
            st.markdown("### Thông Tin Tài Khoản")
            c_info_a, c_info_b = st.columns(2)
            with c_info_a:
                st.markdown(f"**Họ và tên:** {self.parent.full_name}")
                st.markdown(f"**Địa chỉ Email:** `{self.parent.email}`")
            with c_info_b:
                st.markdown(f"**Số điện thoại:** `{self.parent.phone}`")
                st.markdown(f"**Vai trò hệ thống:** `Học viên (STUDENT)`")
                st.markdown(f"**Trạng thái tài khoản:** `{self.parent.status}`")


# =============================================================================
# LỚP BIÊN CHÍNH: StudentHomeView
# =============================================================================

class StudentHomeView:
    """Lớp biên chính dành cho Học viên (Student Dashboard BCE Boundary View)."""

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.full_name = user.get("fullName", "Học viên")
        self.email = user.get("email", "")
        self.phone = user.get("phone", "Chưa cập nhật")
        self.status = user.get("status", "ACTIVE")
        self.avatar_url = normalize_avatar_url(user.get("avatarUrl"))

        # Dữ liệu tải trước
        self.wallet_data: Dict[str, Any] = {}
        self.my_enrollments: List[Dict[str, Any]] = []
        self._load_preliminary_data()

        self.wallet_balance = self.wallet_data.get("balance", 0)
        self.total_remaining_sessions = sum(e.get("remainingSessions", 0) for e in self.my_enrollments)

        # Khởi tạo các sub-views
        self.discovery_view = DiscoveryPTView(self)
        self.detail_view = PTDetailView(self)
        self.booking_view = BookingPackageView(self)
        self.schedule_view = MyScheduleView(self)
        self.course_view = MyCourseView(self)
        self.wallet_view = WalletView(self)
        self.profile_view = ProfileView(self)

    def _load_preliminary_data(self):
        try:
            self.wallet_data = StudentApi.get_wallet()
        except Exception:
            self.wallet_data = {"balance": 0, "lockedBalance": 0, "status": "ACTIVE", "transactions": []}

        try:
            self.my_enrollments = StudentApi.get_my_enrollments()
        except Exception:
            self.my_enrollments = []

    def render(self):
        """Hiển thị toàn bộ Bảng điều khiển Học viên với Banner, Thống kê và 7 Tabs."""
        # Header chào mừng tích hợp Avatar người dùng (Milestone 6)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(25, 118, 210, 0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        {"<img src='" + self.avatar_url + "' style='width: 68px; height: 68px; border-radius: 50%; object-fit: cover; border: 3px solid white;' />" if self.avatar_url else "<div style='width: 68px; height: 68px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; color: white;'>USER</div>"}
                        <div>
                            <h2 style="margin: 0; color: white; font-weight: 700;">Chào mừng bạn, {self.full_name}!</h2>
                            <p style="margin: 0.4rem 0 0 0; opacity: 0.92; font-size: 1.05rem;">
                                Không gian rèn luyện, đặt lịch Huấn luyện viên & quản lý hợp đồng tập luyện tại PT Connect
                            </p>
                        </div>
                    </div>
                    <div style="text-align: right; background: rgba(255, 255, 255, 0.15); padding: 8px 16px; border-radius: 10px; margin-top: 8px;">
                        <div style="font-size: 0.85rem; opacity: 0.9;">Số dư ví khả dụng</div>
                        <div style="font-size: 1.3rem; font-weight: 700;">{format_currency_vnd(self.wallet_balance)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Thẻ thống kê tổng quan
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="Số dư Ví mô phỏng", value=format_currency_vnd(self.wallet_balance), help="Ví điện tử thanh toán khóa học nội bộ")
        with c2:
            st.metric(label="Gói tập đã đăng ký", value=f"{len(self.my_enrollments)} khóa")
        with c3:
            st.metric(label="Tổng buổi tập còn lại", value=f"{self.total_remaining_sessions} buổi")

        st.markdown("---")

        # Phân chia các Tab chức năng theo Milestone 6 & Milestone 8
        tab_explore, tab_detail, tab_booking, tab_my_schedule, tab_courses, tab_wallet, tab_profile = st.tabs([
            "Khám Phá PT",
            "Chi Tiết",
            "Đặt Lịch",
            "Lịch Của Tôi",
            f"Khóa Của Tôi ({len(self.my_enrollments)})",
            "Ví Tiền",
            "Hồ Sơ"
        ])

        target_tab_to_switch = st.session_state.pop("switch_to_tab_name", None)
        if target_tab_to_switch:
            import streamlit.components.v1 as components
            components.html(
                f"""
                <script>
                (function() {{
                    const myIframe = window.frameElement;
                    if (myIframe) {{
                        myIframe.style.display = 'none';
                        if (myIframe.parentElement) {{
                            myIframe.parentElement.style.display = 'none';
                        }}
                    }}

                    function clickTargetTab() {{
                        try {{
                            const parentDoc = window.parent.document;
                            if (!parentDoc) return false;
                            const tabs = Array.from(parentDoc.querySelectorAll('button[data-baseweb="tab"], div[data-testid="stTabs"] button'));
                            if (!tabs || tabs.length === 0) return false;
                            let targetTab = tabs.find(t => (t.innerText || t.textContent || "").includes("{target_tab_to_switch}"));
                            if (targetTab) {{
                                targetTab.click();
                                return true;
                            }}
                        }} catch (e) {{
                            console.error(e);
                        }}
                        return false;
                    }}

                    if (!clickTargetTab()) {{
                        let attempts = 0;
                        const intervalId = setInterval(function() {{
                            attempts++;
                            if (clickTargetTab() || attempts > 20) {{
                                clearInterval(intervalId);
                            }}
                        }}, 50);
                    }}
                }})();
                </script>
                """,
                height=0,
                width=0
            )

        with tab_explore:
            self.discovery_view.render()

        with tab_detail:
            self.detail_view.render()

        with tab_booking:
            self.booking_view.render()

        with tab_my_schedule:
            self.schedule_view.render()

        with tab_courses:
            self.course_view.render()

        with tab_wallet:
            self.wallet_view.render()

        with tab_profile:
            self.profile_view.render()

