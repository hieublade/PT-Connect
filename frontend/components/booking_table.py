from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import streamlit as st
from api.booking_api import BookingApi
from api.client import ApiException


def format_booking_datetime(dt_str: Optional[str]) -> str:
    """Định dạng chuỗi datetime ISO sang kiểu ngày giờ Việt Nam."""
    if not dt_str:
        return "N/A"
    try:
        clean_str = dt_str.replace("Z", "")
        dt = datetime.fromisoformat(clean_str)
        return dt.strftime("%d/%m/%Y lúc %H:%M")
    except Exception:
        return str(dt_str)


def format_session_fee(fee: Any) -> str:
    """Format học phí ca tập VND."""
    try:
        val = float(fee) if fee is not None else 0.0
        return f"{val:,.0f} đ".replace(",", ".")
    except Exception:
        return "0 đ"


def render_booking_status_badge(status: str) -> str:
    """Tạo HTML badge trạng thái booking có màu sắc trực quan."""
    config = {
        "PENDING": {
            "bg": "#fff8e1",
            "border": "#ffe082",
            "color": "#b78103",
            "icon": "⏳",
            "label": "Chờ Huấn luyện viên duyệt"
        },
        "CONFIRMED": {
            "bg": "#e8f5e9",
            "border": "#a5d6a7",
            "color": "#2e7d32",
            "icon": "✅",
            "label": "Đã xác nhận (Sắp tới)"
        },
        "COMPLETED": {
            "bg": "#e3f2fd",
            "border": "#90caf9",
            "color": "#1565c0",
            "icon": "🎉",
            "label": "Đã hoàn thành"
        },
        "CANCELLED": {
            "bg": "#ffebee",
            "border": "#ef9a9a",
            "color": "#c62828",
            "icon": "❌",
            "label": "Đã hủy"
        }
    }
    cfg = config.get(status, {
        "bg": "#f5f5f5",
        "border": "#e0e0e0",
        "color": "#616161",
        "icon": "📌",
        "label": status
    })

    return f"""
    <span style="
        background-color: {cfg['bg']};
        border: 1px solid {cfg['border']};
        color: {cfg['color']};
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    ">
        {cfg['icon']} {cfg['label']}
    </span>
    """


def render_booking_card(
    booking: Dict[str, Any],
    is_pt_view: bool = False,
    on_confirm: Optional[Callable[[int], None]] = None,
    on_reject: Optional[Callable[[int, str], None]] = None
) -> None:
    """Hiển thị một thẻ booking ca tập chi tiết với đầy đủ hành động Milestone 6 & 7."""
    booking_id = booking.get("id")
    status = booking.get("status", "PENDING")
    booking_type = booking.get("bookingType", "PACKAGE")
    start_time = booking.get("startTime")
    end_time = booking.get("endTime")
    session_fee = booking.get("sessionFee", 0)
    student_note = booking.get("studentNote")
    location = booking.get("trainingLocation", "Chưa xác định")
    course_title = booking.get("courseTitle")

    student_name = booking.get("studentName", "Học viên")
    student_phone = booking.get("studentPhone", "")
    pt_name = booking.get("ptName", "Huấn luyện viên")
    pt_phone = booking.get("ptPhone", "")

    cancellation_reason = booking.get("cancellationReason")
    cancelled_by_role = booking.get("cancelledByRole")
    cancelled_at = booking.get("cancelledAt")

    with st.container(border=True):
        c_head1, c_head2 = st.columns([3, 2])
        with c_head1:
            type_label = "🎁 Học thử miễn phí (TRIAL)" if booking_type == "TRIAL" else "📜 Theo gói khóa học (PACKAGE)"
            st.markdown(
                f"<div style='font-size: 0.85rem; color: #666; margin-bottom: 4px;'>"
                f"Mã ca: <strong>#{booking_id}</strong> &bull; {type_label}"
                f"</div>",
                unsafe_allow_html=True
            )
            if is_pt_view:
                st.markdown(f"#### 👤 Học viên: **{student_name}** (`{student_phone}`)")
            else:
                st.markdown(f"#### 🏋️ HLV: **{pt_name}** (`{pt_phone}`)")
        with c_head2:
            st.markdown(
                f"<div style='text-align: right;'>{render_booking_status_badge(status)}</div>",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        col_time, col_loc, col_course = st.columns(3)
        with col_time:
            st.markdown(f"⏰ **Bắt đầu:** {format_booking_datetime(start_time)}")
            st.markdown(f"🏁 **Kết thúc:** {format_booking_datetime(end_time)}")
        with col_loc:
            st.markdown(f"📍 **Địa điểm:** {location}")
            st.markdown(f"💵 **Giá trị ca:** {format_session_fee(session_fee)}")
        with col_course:
            if course_title:
                st.markdown(f"📚 **Khóa học:** {course_title}")
            else:
                st.markdown("📚 **Khóa học:** Buổi học thử đầu tiên")

        if student_note:
            st.info(f"📝 **Ghi chú từ học viên:** {student_note}", icon="💬")

        if status == "CANCELLED" and cancellation_reason:
            st.error(
                f"❌ **Lý do hủy lịch ({cancelled_by_role}):** {cancellation_reason} "
                f"(Thời điểm: {format_booking_datetime(cancelled_at)})",
                icon="⚠️"
            )

        # =====================================================================
        # HÀNH ĐỘNG DÀNH CHO HUẤN LUYỆN VIÊN (PT VIEW)
        # =====================================================================
        if is_pt_view:
            if status == "PENDING":
                st.markdown("---")
                c_btn1, c_btn2 = st.columns([1, 1])
                with c_btn1:
                    if st.button("✅ Xác Nhận (Confirm)", key=f"btn_confirm_bk_{booking_id}", type="primary", use_container_width=True):
                        if on_confirm:
                            on_confirm(booking_id)
                with c_btn2:
                    with st.popover("❌ Từ Chối (Reject)", use_container_width=True):
                        st.markdown("**Nhập lý do từ chối ca tập:**")
                        reason_input = st.text_input(
                            "Lý do:",
                            value="Huấn luyện viên bận lịch đột xuất",
                            key=f"reject_reason_{booking_id}"
                        )
                        if st.button("Xác nhận từ chối", key=f"submit_reject_{booking_id}", type="primary"):
                            if on_reject:
                                on_reject(booking_id, reason_input)

            elif status == "CONFIRMED":
                st.markdown("---")
                st.markdown("##### ⚡ Thao Tác Ca Tập (Milestone 7)")
                col_pt_act1, col_pt_act2, col_pt_act3 = st.columns([2, 2, 1.5])

                # 1. PT Bắt đầu điểm danh & Hiển thị mã OTP
                with col_pt_act1:
                    otp_state_key = f"pt_otp_show_{booking_id}"
                    with st.popover("🎯 Điểm Danh & Mã OTP", use_container_width=True):
                        st.markdown(f"**Quản lý điểm danh ca #{booking_id}:**")
                        if st.button("🚀 Bắt đầu buổi tập (Mở OTP)", key=f"btn_start_att_{booking_id}", type="primary", use_container_width=True):
                            try:
                                att_res = BookingApi.start_attendance(booking_id)
                                st.session_state[otp_state_key] = att_res
                                st.success("Đã mở điểm danh và sinh mã OTP thành công!")
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

                        if otp_state_key in st.session_state and st.session_state[otp_state_key]:
                            res = st.session_state[otp_state_key]
                            otp = res.get("otpCode", "------")
                            st.markdown(
                                f"""
                                <div style="text-align: center; background: #e3f2fd; border: 2px dashed #1976d2; padding: 12px; border-radius: 8px; margin: 10px 0;">
                                    <div style="font-size: 0.85rem; color: #0d47a1;">MÃ OTP CHO HỌC VIÊN:</div>
                                    <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: 8px; color: #1565c0;">{otp}</div>
                                    <div style="font-size: 0.75rem; color: #555;">Hiệu lực trong 30 phút</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown("---")
                        if st.button("✅ Hoàn tất buổi tập (PT Xác nhận)", key=f"btn_pt_conf_{booking_id}", type="secondary", use_container_width=True):
                            try:
                                BookingApi.pt_confirm_attendance(booking_id)
                                st.success("Huấn luyện viên đã xác nhận hoàn tất buổi tập!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")

                # 2. Đánh dấu vắng mặt (ABSENT)
                with col_pt_act2:
                    with st.popover("⚠️ Báo Vắng (ABSENT)", use_container_width=True):
                        st.markdown("**Đánh dấu học viên vắng mặt:**")
                        st.caption("Buổi tập vẫn được tính và chuyển trạng thái sang COMPLETED theo quy chế.")
                        absent_reason = st.text_input("Lý do vắng:", value="Học viên không có mặt tại buổi tập", key=f"absent_reason_{booking_id}")
                        if st.button("Xác nhận học viên vắng", key=f"submit_absent_{booking_id}", type="primary"):
                            try:
                                BookingApi.mark_absent(booking_id, absent_reason)
                                st.success("Đã ghi nhận vắng mặt và hoàn tất ca tập!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")

                # 3. Hủy ca tập (theo chính sách)
                with col_pt_act3:
                    with st.popover("❌ Hủy ca tập", use_container_width=True):
                        st.markdown("**Chính sách hủy ca tập (Phía HLV):**")
                        st.caption("• Hủy trước >= 24h: Hoàn 1 buổi, không phạt.")
                        st.caption("• Hủy sát giờ < 24h: Hoàn 1 buổi, đền bù 20% cho học viên & phạt 20% trừ ví PT.")
                        try:
                            preview = BookingApi.preview_cancel_booking(booking_id)
                            st.info(f"💡 Dự kiến: {preview.get('explanation')}")
                        except Exception:
                            pass

                        pt_cancel_reason = st.text_area("Lý do hủy:", value="Huấn luyện viên có việc đột xuất", key=f"pt_cancel_reason_{booking_id}")
                        if st.button("Xác nhận hủy", key=f"submit_pt_cancel_{booking_id}", type="primary"):
                            try:
                                BookingApi.cancel_booking(booking_id, pt_cancel_reason, is_pt=True)
                                st.success("Đã hủy ca tập theo chính sách!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")

            elif status == "COMPLETED":
                # Milestone 7: Hiển thị nhận xét từ học viên nếu học viên đã đánh giá
                existing_review = BookingApi.get_booking_review(booking_id)
                st.markdown("---")
                if existing_review and isinstance(existing_review, dict) and existing_review.get("id"):
                    rating_val = existing_review.get("rating", 5)
                    stars_str = "⭐" * rating_val
                    comment_text = existing_review.get("comment") or "Không có nhận xét"
                    st.markdown(
                        f"""
                        <div style="background: #f1f8e9; border: 1px solid #c5e1a5; padding: 10px 14px; border-radius: 8px;">
                            <div style="font-weight: 700; color: #33691e;">⭐ Đánh giá từ Học viên: {stars_str} ({rating_val}/5 sao)</div>
                            <div style="color: #424242; margin-top: 4px; font-style: italic;">"{comment_text}"</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("ℹ️ Buổi tập đã hoàn tất. Đang chờ học viên gửi đánh giá & nhận xét.")

        # =====================================================================
        # HÀNH ĐỘNG DÀNH CHO HỌC VIÊN (STUDENT VIEW)
        # =====================================================================
        else:
            if status in ["PENDING", "CONFIRMED"]:
                st.markdown("---")
                col_st_act1, col_st_act2 = st.columns([1, 1])

                # 1. Điểm danh bằng OTP (Khi CONFIRMED)
                with col_st_act1:
                    if status == "CONFIRMED":
                        with st.popover("🔑 Điểm Danh Bằng OTP", use_container_width=True):
                            st.markdown(f"**Điểm danh ca tập #{booking_id}:**")
                            st.caption("Nhập mã OTP 6 số do Huấn luyện viên cung cấp tại phòng tập để xác nhận bạn đã có mặt.")
                            otp_input = st.text_input("Mã OTP (6 số):", max_chars=6, key=f"st_otp_in_{booking_id}", placeholder="Ví dụ: 123456")
                            if st.button("🚀 Xác Nhận Có Mặt", key=f"btn_st_checkin_{booking_id}", type="primary", use_container_width=True):
                                if not otp_input or len(otp_input) != 6:
                                    st.warning("Vui lòng nhập đúng 6 chữ số OTP!")
                                else:
                                    try:
                                        BookingApi.student_checkin(booking_id, otp_input.strip())
                                        st.success("🎉 Điểm danh thành công! Đang chờ HLV bấm hoàn tất buổi tập.")
                                        st.rerun()
                                    except ApiException as e:
                                        st.error(f"❌ Lỗi [{e.status_code}]: {e.message}")
                                    except Exception as ex:
                                        st.error(f"❌ Lỗi: {str(ex)}")
                    else:
                        st.caption("⏳ Ca tập đang chờ HLV duyệt.")

                # 2. Hủy lịch có chính sách hoàn tiền / đền bù (Milestone 7)
                with col_st_act2:
                    with st.popover("❌ Hủy Đặt Lịch Ca Tập", use_container_width=True):
                        st.markdown("**Chính sách hủy ca tập (Học viên):**")
                        st.caption("• PENDING hoặc CONFIRMED trước >= 24h: Hoàn lại 1 buổi tập.")
                        st.caption("• Hủy sát giờ < 24h: Mất buổi tập, đền bù 50% học phí ca cho HLV.")

                        try:
                            preview = BookingApi.preview_cancel_booking(booking_id)
                            st.warning(f"📋 **Quyền lợi:** {preview.get('explanation')}")
                        except Exception:
                            pass

                        st_cancel_reason = st.text_area("Lý do hủy:", value="Tôi bận việc cá nhân đột xuất", key=f"st_cancel_reason_{booking_id}")
                        if st.button("Xác Nhận Hủy Lịch", key=f"submit_st_cancel_{booking_id}", type="primary"):
                            try:
                                BookingApi.cancel_booking(booking_id, st_cancel_reason, is_pt=False)
                                st.success("Đã hủy ca tập theo chính sách bồi thường!")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")

            elif status == "COMPLETED":
                # Đánh giá & nhận xét Huấn luyện viên (Milestone 7)
                st.markdown("---")
                existing_review = BookingApi.get_booking_review(booking_id)

                if existing_review and isinstance(existing_review, dict) and existing_review.get("id"):
                    rating_val = existing_review.get("rating", 5)
                    stars_str = "⭐" * rating_val
                    comment_text = existing_review.get("comment") or "Không có nhận xét"
                    st.markdown(
                        f"""
                        <div style="background: #fffde7; border: 1px solid #fff59d; padding: 10px 14px; border-radius: 8px;">
                            <div style="font-weight: 700; color: #f57f17;">Đánh giá của bạn: {stars_str} ({rating_val}/5 sao)</div>
                            <div style="color: #424242; margin-top: 4px; font-style: italic;">"{comment_text}"</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    with st.popover("⭐ Đánh Giá Huấn Luyện Viên", use_container_width=True):
                        st.markdown(f"**Đánh giá chất lượng ca tập #{booking_id}:**")
                        st.caption("Phản hồi của bạn giúp Huấn luyện viên nâng cao chất lượng và hỗ trợ các học viên khác.")

                        rating_choice = st.slider("Số sao đánh giá:", min_value=1, max_value=5, value=5, step=1, key=f"rate_stars_{booking_id}")
                        review_comment = st.text_area("Nhận xét (tùy chọn):", placeholder="Huấn luyện viên rất nhiệt tình, kỹ thuật chuẩn...", key=f"rate_cmt_{booking_id}")

                        if st.button("Gửi Đánh Giá Ngay", key=f"submit_rate_{booking_id}", type="primary", use_container_width=True):
                            try:
                                BookingApi.create_review(booking_id, rating_choice, review_comment.strip() if review_comment else None)
                                st.success("🎉 Đã gửi đánh giá thành công! Điểm trung bình HLV đã được tự động cập nhật.")
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Lỗi [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi: {str(ex)}")


def render_booking_table(
    bookings: List[Dict[str, Any]],
    is_pt_view: bool = False,
    on_confirm: Optional[Callable[[int], None]] = None,
    on_reject: Optional[Callable[[int, str], None]] = None
) -> None:
    """Hiển thị danh sách các booking ca tập."""
    if not bookings:
        msg = "Chưa có đơn đặt lịch ca tập nào." if not is_pt_view else "Chưa có học viên nào đặt lịch trong mục này."
        st.info(f"ℹ️ {msg}")
        return

    for bk in bookings:
        render_booking_card(
            booking=bk,
            is_pt_view=is_pt_view,
            on_confirm=on_confirm,
            on_reject=on_reject
        )
