from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import streamlit as st


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
    """Hiển thị một thẻ booking ca tập chi tiết."""
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

        # Hành động của Huấn luyện viên khi booking đang PENDING
        if is_pt_view and status == "PENDING":
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
