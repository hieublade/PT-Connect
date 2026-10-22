from typing import Any, Callable, Dict, Optional
import streamlit as st


def format_currency_vnd(amount: Any) -> str:
    """Định dạng số tiền sang chuẩn hiển thị VND."""
    try:
        val = float(amount)
        return f"{val:,.0f} ₫".replace(",", ".")
    except (ValueError, TypeError):
        return f"{amount} ₫"


def render_course_card(
    course: Dict[str, Any],
    on_edit: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_toggle_status: Optional[Callable[[Dict[str, Any]], None]] = None,
    on_delete: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_actions: bool = True,
    **kwargs: Any
) -> None:
    """Component hiển thị thẻ khóa học (Course Card) trực quan."""
    course_id = course.get("id")
    title = course.get("title", "Khóa học chưa đặt tên")
    description = course.get("description", "Chưa có mô tả chi tiết.")
    total_sessions = course.get("totalSessions", 0)
    validity_days = course.get("validityDays", 0)
    base_price = course.get("basePrice", 0)
    status = course.get("status", "ACTIVE")

    is_active = (status == "ACTIVE")
    badge_bg = "#e8f5e9" if is_active else "#f5f5f5"
    badge_color = "#2e7d32" if is_active else "#757575"
    badge_text = "🟢 Đang bán (ACTIVE)" if is_active else "⚪ Đã ngưng bán (INACTIVE)"

    with st.container(border=True):
        col_title, col_badge = st.columns([3, 2])
        with col_title:
            st.markdown(f"### 🏋️ {title}")
        with col_badge:
            st.markdown(
                f"""
                <div style="text-align: right;">
                    <span style="background-color: {badge_bg}; color: {badge_color}; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                        {badge_text}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        if description:
            st.write(description)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="💰 Học phí trọn gói", value=format_currency_vnd(base_price))
        with c2:
            st.metric(label="🔢 Tổng số buổi", value=f"{total_sessions} buổi")
        with c3:
            st.metric(label="⏳ Thời hạn khóa", value=f"{validity_days} ngày")

        if show_actions and (on_edit or on_toggle_status or on_delete):
            btn1, btn2, btn3 = st.columns([2, 2, 2])
            if on_edit:
                with btn1:
                    if st.button("✏️ Chỉnh sửa", key=f"btn_edit_course_{course_id}", use_container_width=True):
                        on_edit(course)
            if on_toggle_status:
                with btn2:
                    toggle_label = "⏸️ Ngưng bán" if is_active else "▶️ Mở bán lại"
                    if st.button(toggle_label, key=f"btn_toggle_course_{course_id}", use_container_width=True):
                        on_toggle_status(course)
            if on_delete:
                with btn3:
                    if st.button("🗑️ Xóa", key=f"btn_del_course_{course_id}", use_container_width=True):
                        on_delete(course)
