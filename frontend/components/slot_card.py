from typing import Any, Callable, Dict, Optional
from datetime import datetime
import streamlit as st


def format_slot_datetime(dt_str: str) -> str:
    """Format datetime string to Vietnamese readable format."""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", ""))
        return dt.strftime("%d/%m/%Y lúc %H:%M")
    except Exception:
        return dt_str


def render_slot_card(
    slot: Dict[str, Any],
    on_delete: Optional[Callable[[Dict[str, Any]], None]] = None
) -> None:
    """Component hiển thị một khung giờ rảnh (Slot) của PT."""
    slot_id = slot.get("id")
    start_time = slot.get("startTime", "")
    end_time = slot.get("endTime", "")
    status = slot.get("status", "AVAILABLE")

    status_config = {
        "AVAILABLE": {"bg": "#e8f5e9", "color": "#2e7d32", "label": "Đang trống (AVAILABLE)", "can_delete": True},
        "BOOKED": {"bg": "#e3f2fd", "color": "#1565c0", "label": "Đã có học viên đặt (BOOKED)", "can_delete": False},
        "LOCKED": {"bg": "#fff3e0", "color": "#e65100", "label": "Đã khóa (LOCKED)", "can_delete": False},
    }

    cfg = status_config.get(status, {"bg": "#f5f5f5", "color": "#757575", "label": status, "can_delete": False})

    with st.container(border=True):
        c_time, c_badge, c_action = st.columns([4, 3, 2])
        with c_time:
            st.markdown(f"**Bắt đầu:** `{format_slot_datetime(start_time)}`")
            st.markdown(f"**Kết thúc:** `{format_slot_datetime(end_time)}`")
        with c_badge:
            st.markdown(
                f"""
                <div style="margin-top: 10px;">
                    <span style="background-color: {cfg['bg']}; color: {cfg['color']}; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                        {cfg['label']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_action:
            if on_delete and cfg["can_delete"]:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                if st.button("Xóa", key=f"btn_delete_slot_{slot_id}", use_container_width=True):
                    on_delete(slot)
