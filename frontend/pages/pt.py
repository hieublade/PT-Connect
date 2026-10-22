from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List
import streamlit as st
from api.client import ApiException
from api.pt_api import PTApi
from api.booking_api import BookingApi
from api.auth_api import AuthApi
from components.course_card import render_course_card
from components.slot_card import render_slot_card
from components.booking_table import render_booking_table
from components.avatar_uploader import render_avatar_management


def render_pt_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Huấn luyện viên cá nhân (PT Dashboard - Milestone 6)."""

    full_name = user.get("fullName", "Huấn luyện viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")
    avatar_url = user.get("avatarUrl")

    # Header chào mừng Huấn luyện viên
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #e65100 0%, #f57c00 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(230, 81, 0, 0.25);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    {"<img src='" + avatar_url + "' style='width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 3px solid white;' />" if avatar_url else "<div style='width: 64px; height: 64px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 2rem;'>🏋️</div>"}
                    <div>
                        <h2 style="margin: 0; color: white; font-weight: 700;">🏋️ Bảng Điều Khiển Huấn Luyện Viên (PT)</h2>
                        <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                            Xin chào, <strong>{full_name}</strong>! Quản lý hồ sơ, lịch rảnh và duyệt các yêu cầu đặt lịch (Booking).
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Lấy thông tin chi tiết hồ sơ PT từ Backend
    profile_data: Dict[str, Any] = {}
    try:
        profile_res = PTApi.get_profile()
        profile_data = profile_res if isinstance(profile_res, dict) else {}
    except Exception:
        profile_data = {}

    verification_status = profile_data.get("verificationStatus", "PENDING")

    # Banner thông báo trạng thái phê duyệt
    if status == "SUSPENDED":
        st.error(
            """
            ⛔ **Tài khoản đang bị tạm ngưng (SUSPENDED):**
            Vui lòng liên hệ với bộ phận Quản trị viên hệ thống để được hỗ trợ kiểm tra và mở khóa tài khoản.
            """,
            icon="🚫"
        )
        return
    elif verification_status == "PENDING" or status == "PENDING":
        st.warning(
            """
            ⏳ **Hồ sơ Huấn luyện viên đang chờ Admin phê duyệt (PENDING):**
            Hồ sơ và bằng cấp của bạn đang được ban quản trị xét duyệt. Bạn vẫn có thể hoàn thiện thông tin hồ sơ và chuẩn bị khóa học.
            """,
            icon="⚠️"
        )
    elif verification_status == "REJECTED":
        st.error(
            """
            ❌ **Hồ sơ chưa được phê duyệt (REJECTED):**
            Vui lòng kiểm tra lại thông tin chứng chỉ hoặc liên hệ Admin để cập nhật lại hồ sơ.
            """,
            icon="⚠️"
        )
    else:
        st.success("✅ Hồ sơ của bạn đã được xác minh thành công (`VERIFIED`). Sẵn sàng nhận học viên!", icon="🎉")

    # Phân chia các Tab chức năng theo Milestone 6
    tab_overview, tab_bookings, tab_slots, tab_courses, tab_profile = st.tabs([
        "📊 Tổng Quan",
        "📋 Duyệt Booking & Lịch Dạy",
        "⏰ Khung Giờ Rảnh (Slots)",
        "📚 Quản Lý Khóa Học",
        "👤 Hồ Sơ & Avatar"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: TỔNG QUAN
    # -------------------------------------------------------------------------
    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        avg_rating = profile_data.get("averageRating", 0)
        total_rev = profile_data.get("totalReviews", 0)
        exp_years = profile_data.get("experienceYears", 0)

        # Lấy số lượng khóa học, slots và bookings
        courses_list: List[Dict[str, Any]] = []
        slots_list: List[Dict[str, Any]] = []
        pending_bookings: List[Dict[str, Any]] = []
        try:
            courses_list = PTApi.get_courses()
            slots_list = PTApi.get_slots()
            pending_bookings = BookingApi.get_pt_bookings(status="PENDING")
        except Exception:
            pass

        with c1:
            st.metric(label="⏳ Ca tập chờ duyệt", value=f"{len(pending_bookings)} ca", delta="Cần xử lý" if pending_bookings else None)
        with c2:
            available_slots = [s for s in slots_list if s.get("status") == "AVAILABLE"]
            st.metric(label="⏰ Khung giờ trống", value=f"{len(available_slots)} slot")
        with c3:
            st.metric(label="📚 Khóa học của tôi", value=f"{len(courses_list)} khóa")
        with c4:
            st.metric(label="⭐ Đánh giá", value=f"{avg_rating:.1f}/5.0", delta=f"{total_rev} lượt review")

        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 📌 Lộ Trình Triển Khai Hệ Thống")
            st.caption("• **Milestone 4:** Quản lý hồ sơ PT, tạo khóa học và mở khung giờ rảnh (AVAILABLE).")
            st.caption("• **Milestone 5:** Học viên tìm kiếm và đăng ký mua khóa học của bạn.")
            st.caption("• **Milestone 6:** Nhận yêu cầu đặt lịch (Booking) và phê duyệt / từ chối buổi tập; cập nhật avatar.")
            st.caption("• **Milestone 7:** Điểm danh học viên bằng mã OTP và nhận đánh giá sao.")

    # -------------------------------------------------------------------------
    # TAB 2: DUYỆT BOOKING & LỊCH DẠY (MILESTONE 6)
    # -------------------------------------------------------------------------
    with tab_bookings:
        st.subheader("📋 Quản Lý & Phê Duyệt Lịch Ca Tập (Milestone 6)")
        st.caption("Phê duyệt hoặc từ chối các đơn đặt lịch của học viên theo gói hoặc học thử.")

        col_filter, col_refresh = st.columns([4, 1])
        with col_filter:
            filter_choice = st.selectbox(
                "Lọc theo trạng thái:",
                ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED", "ALL"],
                format_func=lambda x: {
                    "PENDING": "⏳ Chờ duyệt (PENDING - Ưu tiên)",
                    "CONFIRMED": "✅ Đã xác nhận / Sắp tới (CONFIRMED)",
                    "COMPLETED": "🎉 Đã hoàn thành (COMPLETED)",
                    "CANCELLED": "❌ Đã từ chối / Đã hủy (CANCELLED)",
                    "ALL": "📌 Tất cả trạng thái"
                }.get(x, x),
                index=0
            )
        with col_refresh:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Làm mới", key="btn_refresh_pt_bookings", use_container_width=True):
                st.rerun()

        # Gọi API lấy danh sách booking của PT
        pt_bookings: List[Dict[str, Any]] = []
        try:
            status_param = None if filter_choice == "ALL" else filter_choice
            pt_bookings = BookingApi.get_pt_bookings(status=status_param)
        except ApiException as e:
            st.error(f"❌ Lỗi tải danh sách booking [{e.status_code}]: {e.message}")
        except Exception as ex:
            st.error(f"❌ Lỗi: {str(ex)}")

        def handle_confirm_booking(b_id: int):
            try:
                BookingApi.confirm_booking(b_id)
                st.success(f"✅ Đã phê duyệt thành công ca tập #{b_id}!")
                st.rerun()
            except ApiException as err:
                st.error(f"❌ Phê duyệt thất bại [{err.status_code}]: {err.message}")
            except Exception as ex:
                st.error(f"❌ Lỗi: {str(ex)}")

        def handle_reject_booking(b_id: int, reason: str):
            try:
                BookingApi.reject_booking(b_id, reason)
                st.success(f"✅ Đã từ chối ca tập #{b_id}. Khung giờ và số buổi tập đã được hoàn lại cho học viên.")
                st.rerun()
            except ApiException as err:
                st.error(f"❌ Từ chối thất bại [{err.status_code}]: {err.message}")
            except Exception as ex:
                st.error(f"❌ Lỗi: {str(ex)}")

        render_booking_table(
            bookings=pt_bookings,
            is_pt_view=True,
            on_confirm=handle_confirm_booking,
            on_reject=handle_reject_booking
        )

    # -------------------------------------------------------------------------
    # TAB 3: KHUNG GIỜ RẢNH (SLOTS)
    # -------------------------------------------------------------------------
    with tab_slots:
        st.subheader("⏰ Quản Lý Khung Giờ Rảnh (Availability Slots)")
        st.caption("Mở các khung giờ trống để học viên có thể đăng ký đặt lịch tập luyện.")

        with st.expander("➕ Thêm Khung Giờ Rảnh Mới", expanded=False):
            with st.form("form_create_slot"):
                st.markdown("**Chọn ngày và khoảng thời gian khả dụng:**")
                col_d, col_st, col_et = st.columns(3)
                with col_d:
                    s_date = st.date_input("Ngày rảnh:", min_value=date.today(), value=date.today() + timedelta(days=1))
                with col_st:
                    s_start_time = st.time_input("Giờ bắt đầu:", value=time(9, 0))
                with col_et:
                    s_end_time = st.time_input("Giờ kết thúc:", value=time(10, 30))

                btn_add_slot = st.form_submit_button("🚀 Mở Khung Giờ", type="primary", use_container_width=True)

                if btn_add_slot:
                    dt_start = datetime.combine(s_date, s_start_time)
                    dt_end = datetime.combine(s_date, s_end_time)

                    if dt_end <= dt_start:
                        st.error("❌ Giờ kết thúc phải sau giờ bắt đầu!")
                    elif dt_start < datetime.now():
                        st.error("❌ Không thể mở khung giờ trong quá khứ!")
                    else:
                        slot_payload = {
                            "startTime": dt_start.isoformat(),
                            "endTime": dt_end.isoformat()
                        }
                        try:
                            PTApi.create_slot(slot_payload)
                            st.success("✅ Mở khung giờ rảnh thành công!")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Lỗi mở slot [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")

        # Danh sách slots của PT
        all_slots: List[Dict[str, Any]] = []
        try:
            all_slots = PTApi.get_slots()
        except Exception:
            pass

        if not all_slots:
            st.info("Bạn chưa mở khung giờ rảnh nào. Hãy bấm 'Thêm Khung Giờ Rảnh Mới' ở trên để mở lịch nhé!")
        else:
            def handle_delete_slot(s: Dict[str, Any]):
                s_id = s.get("id")
                try:
                    PTApi.delete_slot(s_id)
                    st.success(f"✅ Đã xóa khung giờ #{s_id} thành công!")
                    st.rerun()
                except ApiException as e:
                    st.error(f"❌ Lỗi xóa slot [{e.status_code}]: {e.message}")
                except Exception as ex:
                    st.error(f"❌ Lỗi: {str(ex)}")

            for slot_item in all_slots:
                render_slot_card(slot_item, on_delete=handle_delete_slot)

    # -------------------------------------------------------------------------
    # TAB 4: QUẢN LÝ KHÓA HỌC
    # -------------------------------------------------------------------------
    with tab_courses:
        st.subheader("📚 Danh Sách Khóa Học Cố Định")
        st.caption("Các gói khóa học huấn luyện trọn gói theo quy định của hệ thống.")

        with st.expander("➕ Thêm Khóa Học Mới", expanded=False):
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

                btn_add_course = st.form_submit_button("🚀 Tạo Khóa Học", type="primary", use_container_width=True)

                if btn_add_course:
                    if not c_title.strip():
                        st.error("❌ Tên khóa học không được để trống!")
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
                            st.success("✅ Tạo khóa học thành công!")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Lỗi tạo khóa học [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")

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
                    "basePrice": c.get("basePrice"),
                    "status": new_status
                }
                try:
                    PTApi.update_course(c_id, up_payload)
                    st.success(f"✅ Đã chuyển trạng thái khóa học sang {new_status}!")
                    st.rerun()
                except ApiException as e:
                    st.error(f"❌ Lỗi cập nhật: {e.message}")

            def handle_delete_course(c: Dict[str, Any]):
                c_id = c.get("id")
                try:
                    PTApi.delete_course(c_id)
                    st.success("✅ Đã xóa khóa học thành công!")
                    st.rerun()
                except ApiException as e:
                    st.error(f"❌ Lỗi xóa khóa học: {e.message}")

            for crs in all_courses:
                render_course_card(
                    crs,
                    show_actions=True,
                    on_toggle_status=handle_toggle_status,
                    on_delete=handle_delete_course
                )

    # -------------------------------------------------------------------------
    # TAB 5: HỒ SƠ CÁ NHÂN & CẬP NHẬT AVATAR (MILESTONE 6 - HIỆU)
    # -------------------------------------------------------------------------
    with tab_profile:
        st.subheader("👤 Cập Nhật Hồ Sơ Năng Lực & Ảnh Đại Diện")

        # Widget Quản lý & Tải lên Avatar (Milestone 6 - Hiệu)
        render_avatar_management(user, "PT")

        with st.form("form_update_profile"):
            st.markdown("### 📝 Thông Tin Hồ Sơ Năng Lực")
            f_bio = st.text_area(
                "Giới thiệu bản thân (Bio):",
                value=profile_data.get("bio") or "",
                placeholder="Ví dụ: Huấn luyện viên chuyên về tăng cơ, giảm mỡ với 5 năm kinh nghiệm...",
                height=120
            )

            col_exp, col_pricing = st.columns(2)
            with col_exp:
                f_exp = st.number_input(
                    "Số năm kinh nghiệm:",
                    min_value=0,
                    max_value=50,
                    value=int(profile_data.get("experienceYears") or 0)
                )
            with col_pricing:
                f_pricing_note = st.text_input(
                    "Chính sách phụ thu theo địa điểm:",
                    value=profile_data.get("locationPricingNote") or "",
                    placeholder="Ví dụ: Dạy tại nhà học viên phụ thu 20% tiền đi lại"
                )

            f_locations = st.text_area(
                "Địa điểm nhận dạy (phân cách bằng dấu chấm phẩy ';'):",
                value=profile_data.get("availableLocations") or "Phòng Cali Cầu Giấy; FitZone Thanh Xuân",
                placeholder="Cali Cầu Giấy; FitZone Thanh Xuân; Nhận dạy tại nhà",
                height=80
            )

            f_certificates = st.text_area(
                "Đường dẫn chứng chỉ / bằng cấp (JSON hoặc URLs):",
                value=profile_data.get("certificateUrls") or '["https://cdn.ptconnect.vn/certs/cert_hlv_cap1.pdf"]',
                placeholder='["https://example.com/cert1.pdf", "https://example.com/cert2.pdf"]',
                height=80
            )

            btn_save = st.form_submit_button("💾 Lưu Cập Nhật Hồ Sơ", type="primary", use_container_width=True)

            if btn_save:
                if not f_locations.strip():
                    st.error("❌ Địa điểm nhận dạy không được để trống!")
                else:
                    payload = {
                        "bio": f_bio.strip(),
                        "experienceYears": f_exp,
                        "availableLocations": f_locations.strip(),
                        "locationPricingNote": f_pricing_note.strip(),
                        "certificateUrls": f_certificates.strip()
                    }
                    try:
                        PTApi.update_profile(payload)
                        st.success("✅ Cập nhật hồ sơ Huấn luyện viên thành công!")
                        st.rerun()
                    except ApiException as e:
                        st.error(f"❌ Lỗi cập nhật hồ sơ [{e.status_code}]: {e.message}")
                    except Exception as ex:
                        st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")
