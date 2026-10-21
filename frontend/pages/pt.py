from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List
import streamlit as st
from api.client import ApiException
from api.pt_api import PTApi
from components.course_card import render_course_card
from components.slot_card import render_slot_card


def render_pt_page(user: Dict[str, Any]):
    """Giao diện chính dành cho Huấn luyện viên cá nhân (PT Dashboard - Milestone 4)."""

    full_name = user.get("fullName", "Huấn luyện viên")
    email = user.get("email", "")
    phone = user.get("phone", "Chưa cập nhật")
    status = user.get("status", "ACTIVE")

    # Header chào mừng Huấn luyện viên
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #e65100 0%, #f57c00 100%); padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0; color: white; font-weight: 700;">🏋️ Bảng Điều Khiển Huấn Luyện Viên (PT)</h2>
            <p style="margin: 0.4rem 0 0 0; opacity: 0.95; font-size: 1.05rem;">
                Xin chào, <strong>{full_name}</strong>! Quản lý hồ sơ năng lực, các khóa học cố định và lịch rảnh của bạn.
            </p>
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

    # Phân chia các Tab chức năng theo Milestone 4
    tab_overview, tab_profile, tab_courses, tab_slots = st.tabs([
        "📊 Tổng Quan",
        "👤 Hồ Sơ Cá Nhân",
        "📚 Quản Lý Khóa Học",
        "⏰ Khung Giờ Rảnh (Slots)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: TỔNG QUAN
    # -------------------------------------------------------------------------
    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        avg_rating = profile_data.get("averageRating", 0)
        total_rev = profile_data.get("totalReviews", 0)
        exp_years = profile_data.get("experienceYears", 0)

        # Lấy số lượng khóa học và slots
        courses_list: List[Dict[str, Any]] = []
        slots_list: List[Dict[str, Any]] = []
        try:
            courses_list = PTApi.get_courses()
            slots_list = PTApi.get_slots()
        except Exception:
            pass

        with c1:
            st.metric(label="📚 Khóa học của tôi", value=f"{len(courses_list)} khóa")
        with c2:
            available_slots = [s for s in slots_list if s.get("status") == "AVAILABLE"]
            st.metric(label="⏰ Khung giờ trống", value=f"{len(available_slots)} slot")
        with c3:
            st.metric(label="⭐ Điểm đánh giá", value=f"{avg_rating} / 5.0")
        with c4:
            st.metric(label="📝 Lượt đánh giá", value=f"{total_rev} lượt")

        st.markdown("---")

        col_info, col_next = st.columns(2)
        with col_info:
            with st.container(border=True):
                st.markdown("#### 📋 Thông tin tài khoản")
                st.markdown(f"**Họ và tên:** {full_name}")
                st.markdown(f"**Email:** `{email}`")
                st.markdown(f"**Số điện thoại:** `{phone}`")
                st.markdown(f"**Kinh nghiệm:** {exp_years} năm")
                st.markdown(f"**Trạng thái xác minh:** `{verification_status}`")
        with col_next:
            with st.container(border=True):
                st.markdown("#### 🚀 Lộ trình tính năng tiếp theo")
                st.caption("• **Milestone 5:** Học viên tìm kiếm và đăng ký mua khóa học của bạn.")
                st.caption("• **Milestone 6:** Nhận yêu cầu đặt lịch (Booking) và phê duyệt / từ chối buổi tập.")
                st.caption("• **Milestone 7:** Điểm danh học viên bằng mã OTP và nhận đánh giá sao.")

    # -------------------------------------------------------------------------
    # TAB 2: HỒ SƠ CÁ NHÂN
    # -------------------------------------------------------------------------
    with tab_profile:
        st.subheader("👤 Cập nhật Hồ sơ Năng lực")
        st.caption("Thông tin này sẽ hiển thị trực tiếp cho Học viên khi tìm kiếm PT ở Milestone 5.")

        with st.form("form_update_profile"):
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

    # -------------------------------------------------------------------------
    # TAB 3: QUẢN LÝ KHÓA HỌC
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
                            st.success("🎉 Tạo khóa học mới thành công!")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Lỗi tạo khóa học [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")

        # Hiển thị danh sách khóa học
        try:
            courses = PTApi.get_courses()
            if not courses:
                st.info("Chưa có khóa học nào được tạo. Hãy bấm vào 'Thêm Khóa Học Mới' ở trên để khởi tạo!")
            else:
                for c in courses:
                    def handle_toggle(course_item):
                        new_status = "INACTIVE" if course_item.get("status") == "ACTIVE" else "ACTIVE"
                        try:
                            PTApi.update_course(course_item["id"], {
                                "title": course_item["title"],
                                "description": course_item.get("description", ""),
                                "totalSessions": course_item["totalSessions"],
                                "validityDays": course_item["validityDays"],
                                "basePrice": course_item["basePrice"],
                                "status": new_status
                            })
                            st.success(f"Đã chuyển trạng thái khóa học sang {new_status}!")
                            st.rerun()
                        except Exception as err:
                            st.error(f"Lỗi: {str(err)}")

                    def handle_delete(course_item):
                        try:
                            PTApi.delete_course(course_item["id"])
                            st.success("Đã xóa khóa học thành công!")
                            st.rerun()
                        except ApiException as err:
                            st.error(f"❌ Không thể xóa [{err.status_code}]: {err.message}")
                        except Exception as err:
                            st.error(f"Lỗi: {str(err)}")

                    render_course_card(c, on_toggle_status=handle_toggle, on_delete=handle_delete)
        except Exception as e:
            st.error(f"Lỗi tải danh sách khóa học: {str(e)}")

    # -------------------------------------------------------------------------
    # TAB 4: KHUNG GIỜ RẢNH (SLOTS)
    # -------------------------------------------------------------------------
    with tab_slots:
        st.subheader("⏰ Quản Lý Khung Giờ Rảnh (Availability Slots)")
        st.caption("Tạo các khung giờ trống để học viên có thể chủ động đặt lịch tập buổi ở Milestone 6.")

        with st.expander("➕ Mở Khung Giờ Mới", expanded=False):
            with st.form("form_create_slot"):
                tomorrow = date.today() + timedelta(days=1)
                s_date = st.date_input("Chọn ngày:", value=tomorrow, min_value=date.today())

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    s_start = st.time_input("Giờ bắt đầu:", value=time(9, 0))
                with col_t2:
                    s_end = st.time_input("Giờ kết thúc:", value=time(10, 0))

                btn_add_slot = st.form_submit_button("📅 Thêm Khung Giờ", type="primary", use_container_width=True)

                if btn_add_slot:
                    start_dt = datetime.combine(s_date, s_start)
                    end_dt = datetime.combine(s_date, s_end)

                    now = datetime.now()
                    if start_dt <= now:
                        st.error("❌ Thời gian bắt đầu slot không được ở trong quá khứ!")
                    elif end_dt <= start_dt:
                        st.error("❌ Thời gian kết thúc slot phải sau thời gian bắt đầu!")
                    else:
                        start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:00")
                        end_iso = end_dt.strftime("%Y-%m-%dT%H:%M:00")
                        try:
                            PTApi.create_slot(start_iso, end_iso)
                            st.success("🎉 Tạo khung giờ rảnh thành công!")
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Lỗi tạo khung giờ [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi ngoại lệ: {str(ex)}")

        # Hiển thị danh sách slots
        try:
            slots = PTApi.get_slots()
            if not slots:
                st.info("Chưa có khung giờ rảnh nào được tạo. Hãy bấm 'Mở Khung Giờ Mới' ở trên!")
            else:
                # Bộ lọc trạng thái
                slot_filter = st.radio(
                    "Lọc khung giờ:",
                    ["Tất cả", "🟢 Đang trống (AVAILABLE)", "🔵 Đã đặt (BOOKED)"],
                    horizontal=True
                )

                filtered_slots = slots
                if slot_filter == "🟢 Đang trống (AVAILABLE)":
                    filtered_slots = [s for s in slots if s.get("status") == "AVAILABLE"]
                elif slot_filter == "🔵 Đã đặt (BOOKED)":
                    filtered_slots = [s for s in slots if s.get("status") == "BOOKED"]

                st.write(f"Hiển thị **{len(filtered_slots)}** khung giờ:")

                for slot in filtered_slots:
                    def handle_delete_slot(s_item):
                        try:
                            PTApi.delete_slot(s_item["id"])
                            st.success("Đã xóa khung giờ rảnh thành công!")
                            st.rerun()
                        except ApiException as err:
                            st.error(f"❌ Lỗi [{err.status_code}]: {err.message}")
                        except Exception as err:
                            st.error(f"Lỗi: {str(err)}")

                    render_slot_card(slot, on_delete=handle_delete_slot)
        except Exception as e:
            st.error(f"Lỗi tải danh sách khung giờ: {str(e)}")
