from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List
import streamlit as st
from api.client import ApiException
from api.pt_api import PTApi
from api.booking_api import BookingApi
from api.auth_api import AuthApi
from components.course_card import render_course_card, format_currency_vnd
from components.slot_card import render_slot_card
from components.booking_table import render_booking_table
from components.avatar_uploader import render_avatar_management, normalize_avatar_url


# =============================================================================
# MODAL DIALOGS (CẤP MODULE ĐỂ TRÁNH LỖI RERUN LOOP TRONG CLASS METHOD)
# =============================================================================

@st.dialog("Xác nhận mở khung giờ")
def confirm_create_slot_dialog(dt_start_iso: str, dt_end_iso: str, slot_label: str):
    st.warning("Bạn chắc chắn muốn mở khung giờ này không?")
    st.markdown(f"Khung giờ: **{slot_label}**")
    if st.button("Xác nhận", type="primary", use_container_width=True):
        try:
            PTApi.create_slot(dt_start_iso, dt_end_iso)
            st.success(f"Mở khung giờ rảnh {slot_label} thành công!")
            st.rerun()
        except ApiException as e:
            st.error(f"Lỗi mở slot [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"Lỗi ngoại lệ: {str(ex)}")


# =============================================================================
# CÁC LỚP BIÊN THÀNH PHẦN (SUB-VIEWS THEO SƠ ĐỒ PHÂN TÍCH BCE)
# =============================================================================

class PTBookingApprovalView:
    """Sơ đồ 8: Quản lý & Phê duyệt lịch ca tập."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Quản Lý & Phê Duyệt Lịch Ca Tập")
        col_filter, col_refresh = st.columns([4, 1])
        with col_filter:
            filter_choice = st.selectbox(
                "Lọc theo trạng thái:",
                ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED", "ALL"],
                format_func=lambda x: {
                    "PENDING": "Chờ duyệt (PENDING - Ưu tiên)",
                    "CONFIRMED": "Đã xác nhận / Sắp tới (CONFIRMED)",
                    "COMPLETED": "Đã hoàn thành (COMPLETED)",
                    "CANCELLED": "Đã từ chối / Đã hủy (CANCELLED)",
                    "ALL": "Tất cả trạng thái"
                }.get(x, x),
                index=0
            )
        with col_refresh:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Làm mới", key="btn_refresh_pt_bookings", use_container_width=True):
                st.rerun()

        # Gọi API lấy danh sách booking của PT
        pt_bookings: List[Dict[str, Any]] = []
        try:
            status_param = None if filter_choice == "ALL" else filter_choice
            pt_bookings = BookingApi.get_pt_bookings(status=status_param)
        except ApiException as e:
            st.error(f"Lỗi tải danh sách booking [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"Lỗi: {str(ex)}")

        def handle_confirm_booking(b_id: int):
            try:
                BookingApi.confirm_booking(b_id)
                st.success(f"Đã phê duyệt thành công ca tập #{b_id}!")
                st.rerun()
            except ApiException as err:
                st.error(f"Phê duyệt thất bại [{err.status_code}]: {err.message}")
            except Exception as ex:
                st.error(f"Lỗi: {str(ex)}")

        def handle_reject_booking(b_id: int, reason: str):
            try:
                BookingApi.reject_booking(b_id, reason)
                st.success(f"Đã từ chối ca tập #{b_id}. Khung giờ và số buổi tập đã được hoàn lại cho học viên.")
                st.rerun()
            except ApiException as err:
                st.error(f"Từ chối thất bại [{err.status_code}]: {err.message}")
            except Exception as ex:
                st.error(f"Lỗi: {str(ex)}")

        render_booking_table(
            bookings=pt_bookings,
            is_pt_view=True,
            on_confirm=handle_confirm_booking,
            on_reject=handle_reject_booking
        )


class ManageSlotView:
    """Sơ đồ 9: Tạo và quản lý khung giờ rảnh mới."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Quản Lý Khung Giờ Rảnh")
        with st.expander("Thêm Khung Giờ Rảnh Mới", expanded=True):
            with st.form("form_create_slot"):
                st.markdown("**Chọn ngày và khoảng thời gian khả dụng:**")
                col_d, col_st, col_et = st.columns(3)

                time_options = [
                    f"{h:02d}:{m:02d}"
                    for h in range(5, 24)
                    for m in (0, 15, 30, 45)
                ]

                with col_d:
                    s_date = st.date_input("Ngày rảnh:", min_value=date.today(), value=date.today() + timedelta(days=1), key="slot_date_input")
                with col_st:
                    def_start_idx = time_options.index("09:00") if "09:00" in time_options else 0
                    s_start_str = st.selectbox("Giờ bắt đầu:", options=time_options, index=def_start_idx, key="slot_start_select")
                with col_et:
                    def_end_idx = time_options.index("10:30") if "10:30" in time_options else 0
                    s_end_str = st.selectbox("Giờ kết thúc:", options=time_options, index=def_end_idx, key="slot_end_select")

                btn_add_slot = st.form_submit_button("Mở Khung Giờ", type="primary", use_container_width=True)

                if btn_add_slot:
                    s_start_time = datetime.strptime(s_start_str, "%H:%M").time()
                    s_end_time = datetime.strptime(s_end_str, "%H:%M").time()
                    dt_start = datetime.combine(s_date, s_start_time)
                    dt_end = datetime.combine(s_date, s_end_time)

                    if dt_end <= dt_start:
                        st.error("Giờ kết thúc phải sau giờ bắt đầu!")
                    elif dt_start < datetime.now():
                        st.error("Không thể mở khung giờ trong quá khứ!")
                    else:
                        slot_label = f"{s_start_str} - {s_end_str} ({s_date.strftime('%d/%m/%Y')})"
                        confirm_create_slot_dialog(dt_start.isoformat(), dt_end.isoformat(), slot_label)

        # Danh sách slots của PT
        all_slots: List[Dict[str, Any]] = []
        try:
            all_slots = PTApi.get_slots()
        except Exception:
            pass

        if not all_slots:
            st.info("Bạn chưa mở khung giờ rảnh nào. Hãy bấm 'Thêm Khung Giờ Rảnh Mới' ở trên để mở lịch nhé!")
        else:
            for slot_item in all_slots:
                render_slot_card(slot_item)


class ManageCourseView:
    """Sơ đồ 10: Thêm và quản lý khóa học mới."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Danh Sách Khóa Học Cố Định")

        with st.expander("Thêm Khóa Học Mới", expanded=False):
            with st.form("form_create_course"):
                c_title = st.text_input("Tên khóa học (*):", placeholder="Ví dụ: Gói Giảm Mỡ Cấp Tốc 12 Buổi")
                c_desc = st.text_area("Mô tả chi tiết:", placeholder="Mô tả nội dung giáo trình, mục tiêu đạt được...")

                col_ses, col_val, col_pr = st.columns(3)
                with col_ses:
                    c_sessions = st.number_input("Số buổi tập (*):", min_value=1, max_value=200, value=12)
                with col_val:
                    c_validity = st.number_input("Hạn sử dụng (ngày) (*):", min_value=1, max_value=365, value=30)
                with col_pr:
                    c_price = st.number_input("Học phí trọn gói (VND) (*):", min_value=0.0, step=100000.0, value=3600000.0)

                btn_add_course = st.form_submit_button("Tạo Khóa Học", type="primary", use_container_width=True)

                if btn_add_course:
                    if not c_title.strip():
                        st.error("Tên khóa học không được để trống!")
                    else:
                        c_payload = {
                            "title": c_title.strip(),
                            "description": c_desc.strip(),
                            "totalSessions": int(c_sessions),
                            "validityDays": int(c_validity),
                            "basePrice": float(c_price)
                        }
                        try:
                            PTApi.create_course(c_payload)
                            st.success("Tạo khóa học thành công!")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"Lỗi tạo khóa học [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"Lỗi ngoại lệ: {str(ex)}")

        all_courses: List[Dict[str, Any]] = []
        try:
            all_courses = PTApi.get_courses()
        except Exception:
            pass

        if not all_courses:
            st.info("Bạn chưa tạo khóa học nào. Hãy bấm 'Thêm Khóa Học Mới' để thiết lập gói tập đầu tiên!")
        else:
            def handle_toggle_status(c: Dict[str, Any]):
                c_id = c.get("id")
                cur_status = c.get("status", "ACTIVE")
                new_status = "INACTIVE" if cur_status == "ACTIVE" else "ACTIVE"
                up_payload = {
                    "title": c.get("title"),
                    "description": c.get("description"),
                    "totalSessions": int(c.get("totalSessions", 1)),
                    "validityDays": int(c.get("validityDays", 30)),
                    "basePrice": float(c.get("basePrice", 0)),
                    "status": new_status
                }
                try:
                    PTApi.update_course(c_id, up_payload)
                    st.success(f"Đã chuyển trạng thái khóa học sang {new_status}!")
                    st.rerun()
                except ApiException as e:
                    st.error(f"Lỗi cập nhật: {e.message}")

            def handle_delete_course(c: Dict[str, Any]):
                c_id = c.get("id")
                try:
                    PTApi.delete_course(c_id)
                    st.success("Đã xóa khóa học thành công!")
                    st.rerun()
                except ApiException as e:
                    st.error(f"Lỗi xóa khóa học: {e.message}")

            for crs in all_courses:
                render_course_card(
                    crs,
                    show_actions=True,
                    on_toggle_status=handle_toggle_status,
                    on_delete=handle_delete_course
                )


class ManageWorkoutPlanView:
    """Sơ đồ 11: Tạo giáo án mới và quản lý bài tập cho học viên."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Quản Lý Giáo Án & Bài Tập Huấn Luyện")
        pt_enrollments: List[Dict[str, Any]] = []
        has_enroll_err = False
        try:
            pt_enrollments = PTApi.get_enrollments()
        except ApiException as e:
            has_enroll_err = True
            st.error(f"Lỗi tải danh sách hợp đồng học viên [{e.status_code}]: {e.message}")
        except Exception as ex:
            has_enroll_err = True
            st.error(f"Không thể kết nối đến máy chủ để lấy hợp đồng: {str(ex)}")

        # 1. Soạn Giáo Án Mới
        with st.expander("Soạn Giáo Án Mới Cho Học Viên", expanded=False):
            if has_enroll_err:
                st.warning("Đã xảy ra lỗi kết nối khi tải danh sách hợp đồng. Vui lòng kiểm tra lại dịch vụ Backend hoặc thử lại sau.")
            elif not pt_enrollments:
                st.info("Bạn chưa có học viên nào ký hợp đồng khóa học. Khi học viên mua khóa, danh sách hợp đồng sẽ xuất hiện tại đây để bạn soạn giáo án!")
            else:
                enroll_options = {
                    e["id"]: f"Hợp đồng #{e['id']} — Học viên: {e.get('studentName', 'Học viên')} | Khóa: {e.get('courseTitle', 'Khóa học')} (Còn {e.get('remainingSessions')}/{e.get('totalSessions')} buổi)"
                    for e in pt_enrollments
                }

                chosen_eid = st.selectbox(
                    "Chọn hợp đồng học viên cần soạn giáo án:",
                    options=list(enroll_options.keys()),
                    format_func=lambda x: enroll_options.get(x, str(x)),
                    key="select_enroll_for_plan"
                )

                chosen_e = next((e for e in pt_enrollments if e["id"] == chosen_eid), pt_enrollments[0])

                with st.container(border=True):
                    st.markdown(
                        f"**Học viên:** `{chosen_e.get('studentName')}` (`{chosen_e.get('studentEmail')}`) | "
                        f"**Địa điểm:** `{chosen_e.get('trainingLocation')}` | "
                        f"**Thời hạn hợp đồng:** từ `{chosen_e.get('startDate')}` đến `{chosen_e.get('endDate')}`"
                    )

                with st.form("form_create_workout_plan"):
                    plan_title = st.text_input(
                        "Tiêu đề giáo án (*):",
                        value=f"Giáo án rèn luyện - {chosen_e.get('studentName')}",
                        placeholder="Ví dụ: Lộ trình giảm mỡ 4 tuần đầu"
                    )
                    plan_goal = st.text_input(
                        "Mục tiêu giáo án (Goal):",
                        value=f"Rèn luyện thể lực và hoàn thành khóa {chosen_e.get('courseTitle')}",
                        placeholder="Ví dụ: Giảm 3kg mỡ, tăng sức bền tim mạch..."
                    )

                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        plan_start_date = st.date_input("Ngày bắt đầu giáo án:", value=date.today())
                    with col_d2:
                        plan_end_date = st.date_input("Ngày kết thúc giáo án:", value=date.today() + timedelta(days=30))

                    if st.form_submit_button("Tạo Giáo Án", type="primary"):
                        if not plan_title.strip():
                            st.error("Vui lòng nhập tiêu đề giáo án!")
                        elif plan_start_date > plan_end_date:
                            st.error("Ngày bắt đầu giáo án không thể sau ngày kết thúc!")
                        else:
                            try:
                                payload = {
                                    "enrollmentId": int(chosen_eid),
                                    "title": plan_title.strip(),
                                    "goal": plan_goal.strip() if plan_goal else None,
                                    "startDate": plan_start_date.isoformat(),
                                    "endDate": plan_end_date.isoformat()
                                }
                                PTApi.create_workout_plan(payload)
                                st.success(f"Đã tạo thành công giáo án: {plan_title}!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi tạo giáo án [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

        # 2. Danh Sách Giáo Án Đã Tạo
        st.markdown("#### Danh Sách Giáo Án Đã Tạo")
        plans: List[Dict[str, Any]] = []
        has_plan_err = False
        try:
            plans = PTApi.get_workout_plans()
        except ApiException as e:
            has_plan_err = True
            st.error(f"Lỗi tải danh sách giáo án [{e.status_code}]: {e.message}")
        except Exception as ex:
            has_plan_err = True
            st.error(f"Lỗi kết nối khi tải danh sách giáo án: {str(ex)}")

        if has_plan_err:
            st.warning("Đã xảy ra lỗi khi tải danh sách giáo án.")
        elif not plans:
            st.info("Chưa có giáo án nào được tạo. Hãy nhấn vào 'Soạn Giáo Án Mới Cho Học Viên' ở trên để bắt đầu thiết kế bài tập!")
        else:
            for p in plans:
                plan_id = p.get("id")
                p_title = p.get("title", "Giáo án")
                p_enroll_id = p.get("enrollmentId")
                p_student_name = p.get("studentName", "Học viên")
                p_goal = p.get("goal", "")
                p_start = p.get("startDate", "")
                p_end = p.get("endDate", "")
                p_workouts = p.get("workouts", [])

                with st.container(border=True):
                    col_p_title, col_p_actions = st.columns([3, 1])
                    with col_p_title:
                        st.markdown(f"### {p_title}")
                        st.markdown(f"**Học viên:** `{p_student_name}` | **Mã Hợp Đồng:** `#{p_enroll_id}` | **Thời hạn:** từ `{p_start}` đến `{p_end}`")
                        if p_goal:
                            st.caption(f"**Mục tiêu:** {p_goal}")
                    with col_p_actions:
                        st.markdown(f"<div style='text-align: right; color: #1565c0; font-weight: 600; font-size: 1.05rem; margin-bottom: 6px;'>{len(p_workouts)} bài tập</div>", unsafe_allow_html=True)
                        if st.button("Xóa Giáo Án", key=f"btn_del_plan_{plan_id}", type="secondary", use_container_width=True, help="Xóa toàn bộ giáo án này"):
                            try:
                                PTApi.delete_workout_plan(plan_id)
                                st.success("Đã xóa giáo án thành công!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi xóa giáo án [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

                    # Danh sách bài tập hiện tại
                    if p_workouts:
                        st.markdown("**Danh sách bài tập chi tiết:**")
                        for idx, w in enumerate(p_workouts, 1):
                            w_id = w.get("id")
                            col_w_info, col_w_del = st.columns([5, 1])
                            with col_w_info:
                                weight_txt = f" • **Tạ:** `{w.get('weightKg')} kg`" if w.get("weightKg") else ""
                                muscle_txt = f" *(Cơ: {w.get('targetMuscle')})*" if w.get("targetMuscle") else ""
                                video_txt = f" • [Video demo]({w.get('videoDemoUrl')})" if w.get("videoDemoUrl") else ""
                                st.markdown(
                                    f"**{idx}. {w.get('exerciseName')}**{muscle_txt}: "
                                    f"`{w.get('sets', 3)} sets` × `{w.get('reps', 10)} reps`"
                                    f"{weight_txt} • Nghỉ: `{w.get('restSeconds', 60)}s`{video_txt}"
                                )
                            with col_w_del:
                                if st.button("Xóa", key=f"btn_del_wo_{plan_id}_{w_id}", help=f"Xóa bài tập '{w.get('exerciseName')}'", use_container_width=True):
                                    try:
                                        PTApi.delete_workout(plan_id, w_id)
                                        st.success(f"Đã xóa bài tập '{w.get('exerciseName')}'!")
                                        st.rerun()
                                    except ApiException as e:
                                        st.error(f"Lỗi xóa bài tập [{e.status_code}]: {e.message}")
                                    except Exception as ex:
                                        st.error(f"Lỗi: {str(ex)}")

                    # Form thêm bài tập vào giáo án này
                    with st.expander(f"Thêm Bài Tập Vào Giáo Án #{plan_id}", expanded=False):
                        with st.form(f"form_add_workout_{plan_id}"):
                            w_name = st.text_input("Tên bài tập (*):", placeholder="Ví dụ: Barbell Squat, Bench Press, Dumbbell Lunges...", key=f"ex_name_{plan_id}")
                            w_muscle = st.text_input("Nhóm cơ tác động:", placeholder="Ví dụ: Cơ đùi & Mông, Ngực, Vai...", key=f"muscle_{plan_id}")

                            col_w1, col_w2, col_w3, col_w4 = st.columns(4)
                            with col_w1:
                                w_sets = st.number_input("Số sets:", min_value=1, value=3, step=1, key=f"sets_{plan_id}")
                            with col_w2:
                                w_reps = st.number_input("Số reps/set:", min_value=1, value=10, step=1, key=f"reps_{plan_id}")
                            with col_w3:
                                w_weight = st.number_input("Mức tạ (kg):", min_value=0.0, value=20.0, step=2.5, key=f"weight_{plan_id}")
                            with col_w4:
                                w_rest = st.number_input("Nghỉ giữa hiệp (giây):", min_value=0, value=60, step=15, key=f"rest_{plan_id}")

                            w_video = st.text_input("Link video demo kỹ thuật (tùy chọn):", placeholder="https://storage.ptconnect.vn/videos/demo.mp4", key=f"video_{plan_id}")

                            if st.form_submit_button("Thêm Bài Tập Này", type="primary"):
                                if not w_name.strip():
                                    st.error("Vui lòng nhập tên bài tập!")
                                else:
                                    try:
                                        payload = {
                                            "exerciseName": w_name.strip(),
                                            "targetMuscle": w_muscle.strip() if w_muscle else None,
                                            "sets": int(w_sets),
                                            "reps": int(w_reps),
                                            "weightKg": float(w_weight) if w_weight > 0 else None,
                                            "restSeconds": int(w_rest),
                                            "videoDemoUrl": w_video.strip() if w_video else None
                                        }
                                        PTApi.add_workout(plan_id, payload)
                                        st.success(f"Đã thêm bài tập {w_name} vào giáo án!")
                                        st.rerun()
                                    except ApiException as e:
                                        st.error(f"Lỗi thêm bài tập [{e.status_code}]: {e.message}")
                                    except Exception as ex:
                                        st.error(f"Lỗi: {str(ex)}")


class ManagePTProfileView:
    """Sơ đồ 12: Cập nhật hồ sơ năng lực và ảnh đại diện Huấn luyện viên."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Cập Nhật Hồ Sơ Năng Lực & Ảnh Đại Diện")

        # Widget Quản lý & Tải lên Avatar (Milestone 6 - Hiệu)
        render_avatar_management(self.parent.user, "PT")

        with st.form("form_update_profile"):
            st.markdown("### Thông Tin Hồ Sơ Năng Lực")
            f_bio = st.text_area(
                "Giới thiệu bản thân (Bio):",
                value=self.parent.profile_data.get("bio") or "",
                placeholder="Ví dụ: Huấn luyện viên chuyên về tăng cơ, giảm mỡ với 5 năm kinh nghiệm...",
                height=120
            )

            col_exp, col_pricing = st.columns(2)
            with col_exp:
                f_exp = st.number_input(
                    "Số năm kinh nghiệm:",
                    min_value=0,
                    max_value=50,
                    value=int(self.parent.profile_data.get("experienceYears") or 0)
                )
            with col_pricing:
                f_pricing_note = st.text_input(
                    "Chính sách phụ thu theo địa điểm:",
                    value=self.parent.profile_data.get("locationPricingNote") or "",
                    placeholder="Ví dụ: Dạy tại nhà học viên phụ thu 20% tiền đi lại"
                )

            f_locations = st.text_area(
                "Địa điểm nhận dạy (phân cách bằng dấu chấm phẩy ';'):",
                value=self.parent.profile_data.get("availableLocations") or "Phòng Cali Cầu Giấy; FitZone Thanh Xuân",
                placeholder="Cali Cầu Giấy; FitZone Thanh Xuân; Nhận dạy tại nhà",
                height=80
            )

            current_cert = self.parent.profile_data.get("certificateUrl") or self.parent.profile_data.get("certificateUrls") or ""
            if current_cert.startswith('["') and current_cert.endswith('"]'):
                current_cert = current_cert[2:-2]

            f_certificates = st.text_input(
                "Đường dẫn chứng chỉ / bằng cấp chuyên môn (URL):",
                value=current_cert,
                placeholder="https://storage.ptconnect.vn/certs/cert_nasam.jpg"
            )

            btn_save = st.form_submit_button("Lưu Cập Nhật Hồ Sơ", type="primary", use_container_width=True)

            if btn_save:
                if not f_locations.strip():
                    st.error("Địa điểm nhận dạy không được để trống!")
                else:
                    payload = {
                        "bio": f_bio.strip(),
                        "experienceYears": f_exp,
                        "availableLocations": f_locations.strip(),
                        "locationPricingNote": f_pricing_note.strip(),
                        "certificateUrl": f_certificates.strip(),
                        "certificateUrls": f_certificates.strip()
                    }
                    try:
                        PTApi.update_profile(payload)
                        st.success("Cập nhật hồ sơ Huấn luyện viên thành công!")
                        st.rerun()
                    except ApiException as e:
                        st.error(f"Lỗi cập nhật hồ sơ [{e.status_code}]: {e.message}")
                    except Exception as ex:
                        st.error(f"Lỗi ngoại lệ: {str(ex)}")


# =============================================================================
# LỚP BIÊN QUẢN LÝ VÍ & THU NHẬP (BCE PATTERN)
# =============================================================================

class PTWalletView:
    """Lớp biên quản lý Ví điện tử, Nạp tiền mô phỏng & Rút tiền thu nhập cho PT."""

    def __init__(self, parent: "PTHomeView"):
        self.parent = parent

    def render(self):
        st.subheader("Ví Điện Tử & Quản Lý Thu Nhập Huấn Luyện Viên")
        st.caption("Quản lý dòng tiền thu lao dạy học, nạp tiền bù phạt vi phạm và rút tiền về tài khoản ngân hàng.")

        wallet_data: Dict[str, Any] = {}
        try:
            wallet_data = PTApi.get_wallet()
        except Exception as e:
            st.error(f"Không thể tải thông tin ví: {str(e)}")
            wallet_data = {}

        balance = float(wallet_data.get("balance", 0) or 0)
        locked_balance = float(wallet_data.get("lockedBalance", 0) or 0)
        available_balance = max(0.0, balance - locked_balance)
        wallet_status = wallet_data.get("status", "ACTIVE")
        transactions = wallet_data.get("transactions", [])

        if balance < 0:
            st.warning(
                f"⚠️ **Tài khoản đang ghi nợ phạt {format_currency_vnd(abs(balance))}** do hủy ca tập sát giờ (< 24h). "
                f"Bạn có thể nạp tiền ngay bên dưới để xóa nợ, hoặc hệ thống sẽ tự động khấu trừ vào thu nhập ca tập tiếp theo."
            )

        col_left, col_right = st.columns([1, 1], gap="medium")

        # CỘT TRÁI: THÔNG TIN SỐ DƯ & NẠP TIỀN
        with col_left:
            with st.container(border=True):
                st.markdown("#### 💰 Số Dư & Nạp Tiền")
                st.markdown(f"**Chủ tài khoản:** {self.parent.full_name}")
                st.markdown(f"**Trạng thái ví:** `{wallet_status}`")

                if balance < 0:
                    badge_bg = "#ffebee"
                    badge_border = "#c62828"
                    label_color = "#b71c1c"
                    status_text = "Đang nợ phạt vi phạm"
                else:
                    badge_bg = "#e8f5e9"
                    badge_border = "#2e7d32"
                    label_color = "#1b5e20"
                    status_text = "Khả dụng"

                st.markdown(
                    f"""
                    <div style="background: {badge_bg}; padding: 1.2rem; border-radius: 10px; margin: 0.8rem 0; border-left: 5px solid {badge_border};">
                        <span style="font-size: 0.9rem; color: {label_color}; font-weight: 600;">SỐ DƯ HIỆN TẠI ({status_text}):</span>
                        <div style="font-size: 1.8rem; font-weight: 800; color: {badge_border}; margin-top: 4px;">
                            {format_currency_vnd(balance)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("##### Nạp tiền vào ví (Mô phỏng):")
                st.caption("Chọn nhanh số tiền cần nạp:")
                q_cols = st.columns(4)
                if "pt_topup_amount_input" not in st.session_state:
                    st.session_state["pt_topup_amount_input"] = 1000000.0

                def handle_pt_quick_amount(amt_val: float):
                    st.session_state["pt_topup_amount_input"] = float(amt_val)

                for idx, amt in enumerate([500000.0, 1000000.0, 2000000.0, 5000000.0]):
                    with q_cols[idx]:
                        label = f"{int(amt/1000)}K" if amt < 1000000 else f"{int(amt/1000000)}Tr"
                        st.button(
                            label,
                            key=f"pt_qamt_{int(amt)}",
                            on_click=handle_pt_quick_amount,
                            args=(amt,),
                            use_container_width=True
                        )

                entered_topup = st.number_input(
                    "Hoặc nhập số tiền tùy chọn (VND):",
                    min_value=10000.0,
                    max_value=100000000.0,
                    step=100000.0,
                    key="pt_topup_amount_input"
                )

                topup_method = st.selectbox(
                    "Phương thức nạp mô phỏng:",
                    options=["BANK_TRANSFER", "CREDIT_CARD", "CASH"],
                    format_func=lambda x: {
                        "BANK_TRANSFER": "Chuyển khoản VietQR / MoMo",
                        "CREDIT_CARD": "Thẻ tín dụng / Ghi nợ quốc tế (Visa, Mastercard)",
                        "CASH": "Nộp tiền mặt tại trung tâm"
                    }.get(x, x),
                    key="pt_topup_payment_method"
                )

                if st.button("➕ Nạp Tiền Vào Ví Ngay", type="primary", use_container_width=True, key="btn_pt_topup"):
                    with st.spinner("Đang xử lý nạp tiền..."):
                        try:
                            res = PTApi.topup_wallet(amount=entered_topup, payment_method=topup_method)
                            st.success(f"Nạp thành công {format_currency_vnd(entered_topup)}! Mã GD: {res.get('transactionRef')}")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"Lỗi nạp tiền [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"Lỗi ngoại lệ: {str(ex)}")

        # CỘT PHẢI: RÚT TIỀN THU NHẬP VỀ NGÂN HÀNG
        with col_right:
            with st.container(border=True):
                st.markdown("#### 🏦 Rút Tiền Về Ngân Hàng")

                if balance <= 0:
                    st.info("💡 Bạn cần có số dư khả dụng dương (> 0 ₫) và không nợ phạt để thực hiện rút tiền.")
                else:
                    st.markdown(f"**Số dư khả dụng để rút:** `{format_currency_vnd(available_balance)}`")

                    withdraw_amt = st.number_input(
                        "Số tiền muốn rút (tối thiểu 50,000 VND):",
                        min_value=50000.0,
                        max_value=max(50000.0, available_balance),
                        value=min(max(50000.0, available_balance), available_balance),
                        step=50000.0,
                        key="pt_withdraw_amount_input"
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
                        key="pt_withdraw_bank"
                    )
                    clean_bank_name = selected_bank.split(" (")[0]

                    acc_number = st.text_input(
                        "Số tài khoản nhận tiền:",
                        value="0123456789",
                        key="pt_withdraw_acc_num",
                        help="Nhập số tài khoản ngân hàng chính chủ của bạn"
                    )

                    acc_name = st.text_input(
                        "Tên chủ tài khoản (In hoa không dấu):",
                        value=self.parent.full_name.upper(),
                        key="pt_withdraw_acc_name"
                    )

                    st.caption("ℹ️ *Hệ thống mô phỏng lệnh chuyển khoản liên ngân hàng 24/7 tức thì.*")

                    if st.button("💸 Xác Nhận Rút Tiền Ngay", type="primary", use_container_width=True, key="btn_pt_withdraw"):
                        if not acc_number.strip():
                            st.error("Vui lòng nhập số tài khoản nhận tiền.")
                        elif not acc_name.strip():
                            st.error("Vui lòng nhập tên chủ tài khoản.")
                        elif withdraw_amt > available_balance:
                            st.error(f"Số tiền rút ({format_currency_vnd(withdraw_amt)}) vượt quá số dư khả dụng.")
                        else:
                            with st.spinner("Đang thực hiện chuyển khoản..."):
                                try:
                                    res = PTApi.withdraw_wallet(
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
                                    st.error(f"Lỗi ngoại lệ: {str(ex)}")

        # BẢNG LỊCH SỬ GIAO DỊCH TÀI CHÍNH
        st.markdown("---")
        st.subheader("📜 Lịch Sử Giao Dịch Ví Điện Tử")

        if not transactions:
            st.info("Chưa có giao dịch phát sinh nào trong ví.")
        else:
            table_data = []
            for t in transactions:
                t_type = t.get("paymentType", "")
                t_ref = t.get("transactionRef", "")
                amt = float(t.get("amount", 0) or 0)

                if "WITHDRAW" in str(t_ref):
                    type_label = "RÚT TIỀN"
                    amt_str = f"-{format_currency_vnd(amt)}"
                elif "PENALTY" in str(t_ref) or (t_type == "REFUND" and "WITHDRAW" not in str(t_ref)):
                    type_label = "PHẠT HỦY CA (<24H)"
                    amt_str = f"-{format_currency_vnd(amt)}"
                elif t_type == "TOPUP":
                    type_label = "NẠP TIỀN"
                    amt_str = f"+{format_currency_vnd(amt)}"
                elif t_type == "COMPENSATION":
                    type_label = "ĐỀN BÙ CA TẬP"
                    amt_str = f"+{format_currency_vnd(amt)}"
                else:
                    type_label = t_type
                    amt_str = f"{format_currency_vnd(amt)}"

                table_data.append({
                    "Mã Giao Dịch": t_ref,
                    "Loại Giao Dịch": type_label,
                    "Số Tiền": amt_str,
                    "Phương Thức": t.get("paymentMethod", ""),
                    "Trạng Thái": t.get("status", ""),
                    "Thời Gian": t.get("createdAt", "")[:19].replace("T", " ") if t.get("createdAt") else ""
                })

            st.dataframe(table_data, use_container_width=True)


# =============================================================================
# LỚP BIÊN CHÍNH: PTHomeView
# =============================================================================

class PTHomeView:
    """Lớp biên chính dành cho Huấn luyện viên cá nhân (PT Dashboard BCE Boundary View)."""

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.full_name = user.get("fullName", "Huấn luyện viên")
        self.email = user.get("email", "")
        self.phone = user.get("phone", "Chưa cập nhật")
        self.status = user.get("status", "ACTIVE")
        self.avatar_url = normalize_avatar_url(user.get("avatarUrl"))

        # Dữ liệu profile PT tải từ Backend
        self.profile_data: Dict[str, Any] = {}
        self._load_profile_data()

        # Khởi tạo các sub-views
        self.booking_approval_view = PTBookingApprovalView(self)
        self.slot_view = ManageSlotView(self)
        self.course_view = ManageCourseView(self)
        self.workout_plan_view = ManageWorkoutPlanView(self)
        self.wallet_view = PTWalletView(self)
        self.profile_view = ManagePTProfileView(self)

    def _load_profile_data(self):
        try:
            profile_res = PTApi.get_profile()
            self.profile_data = profile_res if isinstance(profile_res, dict) else {}
        except Exception:
            self.profile_data = {}

    def render_overview_tab(self):
        """Render Tab 1: Tổng quan số liệu, số dư ví và review."""
        c1, c2, c3, c4, c5 = st.columns(5)
        avg_rating = self.profile_data.get("averageRating", 0)
        total_rev = self.profile_data.get("totalReviews", 0)

        # Lấy số lượng khóa học, slots, bookings và thông tin ví PT
        courses_list: List[Dict[str, Any]] = []
        slots_list: List[Dict[str, Any]] = []
        pending_bookings: List[Dict[str, Any]] = []
        wallet_data: Dict[str, Any] = {}
        try:
            courses_list = PTApi.get_courses()
            slots_list = PTApi.get_slots()
            pending_bookings = BookingApi.get_pt_bookings(status="PENDING")
            wallet_data = PTApi.get_wallet()
        except Exception:
            pass

        wallet_balance = float(wallet_data.get("balance", 0) or 0)

        with c1:
            st.metric(label="Ca tập chờ duyệt", value=f"{len(pending_bookings)} ca", delta="Cần xử lý" if pending_bookings else None)
        with c2:
            available_slots = [s for s in slots_list if s.get("status") == "AVAILABLE"]
            st.metric(label="Khung giờ trống", value=f"{len(available_slots)} slot")
        with c3:
            st.metric(label="Khóa học của tôi", value=f"{len(courses_list)} khóa")
        with c4:
            st.metric(label="Đánh giá", value=f"{avg_rating:.1f}/5.0", delta=f"{total_rev} lượt review")
        with c5:
            if wallet_balance < 0:
                st.metric(
                    label="Số dư ví (Ghi nợ)",
                    value=format_currency_vnd(wallet_balance),
                    delta="Đang nợ phạt",
                    delta_color="inverse",
                    help="Số dư âm do bị phạt khi hủy ca tập sát giờ (< 24h). Khoản này sẽ được cấn trừ tự động."
                )
            elif wallet_balance > 0:
                st.metric(
                    label="Số dư ví PT",
                    value=format_currency_vnd(wallet_balance),
                    delta="Khả dụng",
                    help="Số dư khả dụng trong ví điện tử của PT"
                )
            else:
                st.metric(
                    label="Số dư ví PT",
                    value="0 ₫",
                    help="Số dư trong ví điện tử của PT"
                )

        if wallet_balance < 0:
            st.warning(
                f"Tài khoản hiện đang ghi nợ **{format_currency_vnd(abs(wallet_balance))}** tiền phạt vi phạm do hủy ca tập sát giờ (< 24h). "
                f"Khoản nợ này sẽ được cấn trừ tự động vào ví khi có giao dịch tiếp theo."
            )

        # Hiển thị lịch sử biến động ví và tiền phạt nếu có
        transactions = wallet_data.get("transactions", [])
        if transactions:
            with st.expander("Lịch sử biến động ví & Chi tiết các khoản phạt"):
                for txn in transactions:
                    t_type = txn.get("paymentType", "")
                    t_amt = txn.get("amount", 0)
                    t_ref = txn.get("transactionRef", "")
                    t_time = txn.get("createdAt", "")

                    if "WITHDRAW" in str(t_ref):
                        type_badge = "Rút tiền về tài khoản ngân hàng"
                        amt_display = f"-{format_currency_vnd(t_amt)}"
                        card_bg = "#fff3e0"
                        border_color = "#e65100"
                    elif "PENALTY" in str(t_ref) or (t_type == "REFUND" and "WITHDRAW" not in str(t_ref)):
                        type_badge = "Phạt hủy ca tập sát giờ (< 24h)"
                        amt_display = f"-{format_currency_vnd(t_amt)}"
                        card_bg = "#ffebee"
                        border_color = "#c62828"
                    elif t_type == "TOPUP":
                        type_badge = "Nạp tiền vào ví điện tử"
                        amt_display = f"+{format_currency_vnd(t_amt)}"
                        card_bg = "#e3f2fd"
                        border_color = "#1565c0"
                    elif t_type == "COMPENSATION" or "COMP" in str(t_ref):
                        type_badge = "Được đền bù (Học viên hủy sát giờ < 24h)"
                        amt_display = f"+{format_currency_vnd(t_amt)}"
                        card_bg = "#e8f5e9"
                        border_color = "#2e7d32"
                    else:
                        type_badge = t_type
                        amt_display = format_currency_vnd(t_amt)
                        card_bg = "#f5f5f5"
                        border_color = "#9e9e9e"

                    st.markdown(
                        f"""
                        <div style="background: {card_bg}; border-left: 4px solid {border_color}; padding: 8px 12px; border-radius: 4px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 600; font-size: 0.95rem;">{type_badge}</div>
                                <div style="font-size: 0.8rem; color: #555;">Mã GD: <code>{t_ref}</code> | Thời gian: {t_time}</div>
                            </div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: {border_color};">{amt_display}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")
        with st.container(border=True):
            st.markdown("### Đánh Giá Gần Đây Từ Học Viên")
            pt_id = self.profile_data.get("id")
            pt_reviews = BookingApi.get_pt_reviews(pt_id) if pt_id else []
            if not pt_reviews:
                st.info("Chưa có lượt đánh giá nào từ học viên. Các buổi tập hoàn tất sẽ được học viên gửi đánh giá tại đây.")
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

    def render(self):
        """Hiển thị toàn bộ Bảng điều khiển Huấn luyện viên."""
        # Header chào mừng Huấn luyện viên
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #e65100 0%, #f57c00 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(230, 81, 0, 0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        {"<img src='" + self.avatar_url + "' style='width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 3px solid white;' />" if self.avatar_url else "<div style='width: 64px; height: 64px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; color: white;'>PT</div>"}
                        <div>
                            <h2 style="margin: 0; color: white; font-weight: 700;">Bảng Điều Khiển Huấn Luyện Viên (PT)</h2>
                            <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                                Xin chào, <strong>{self.full_name}</strong>! Quản lý hồ sơ, lịch rảnh và duyệt các yêu cầu đặt lịch (Booking).
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        verification_status = self.profile_data.get("verificationStatus", "PENDING")

        # Banner thông báo trạng thái phê duyệt
        if self.status == "SUSPENDED":
            st.error(
                """
                **Tài khoản đang bị tạm ngưng (SUSPENDED):**
                Vui lòng liên hệ với bộ phận Quản trị viên hệ thống để được hỗ trợ kiểm tra và mở khóa tài khoản.
                """
            )
            return
        elif verification_status == "PENDING" or self.status == "PENDING":
            st.warning(
                """
                **Hồ sơ Huấn luyện viên đang chờ Admin phê duyệt (PENDING):**
                Hồ sơ và bằng cấp của bạn đang được ban quản trị xét duyệt. Bạn vẫn có thể hoàn thiện thông tin hồ sơ và chuẩn bị khóa học.
                """
            )
        elif verification_status == "REJECTED":
            st.error(
                """
                **Hồ sơ chưa được phê duyệt (REJECTED):**
                Vui lòng kiểm tra lại thông tin chứng chỉ hoặc liên hệ Admin để cập nhật lại hồ sơ.
                """
            )
        else:
            st.success("Hồ sơ của bạn đã được xác minh thành công (`VERIFIED`). Sẵn sàng nhận học viên!")

        # Phân chia các Tab chức năng
        tab_overview, tab_bookings, tab_slots, tab_courses, tab_workout_plans, tab_wallet, tab_profile = st.tabs([
            "Tổng Quan",
            "Duyệt lịch",
            "Khung Giờ",
            "Quản Lý Khóa",
            "Giáo Án",
            "Ví & Thu nhập",
            "Hồ Sơ"
        ])

        with tab_overview:
            self.render_overview_tab()

        with tab_bookings:
            self.booking_approval_view.render()

        with tab_slots:
            self.slot_view.render()

        with tab_courses:
            self.course_view.render()

        with tab_workout_plans:
            self.workout_plan_view.render()

        with tab_wallet:
            self.wallet_view.render()

        with tab_profile:
            self.profile_view.render()

