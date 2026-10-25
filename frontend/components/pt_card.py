from typing import Any, Callable, Dict, Optional
import streamlit as st
from components.avatar_uploader import normalize_avatar_url


def format_currency_vnd(amount: Any) -> str:
    """Định dạng số tiền sang chuẩn hiển thị VND."""
    try:
        val = float(amount)
        return f"{val:,.0f} ₫".replace(",", ".")
    except (ValueError, TypeError):
        return f"{amount} ₫"


def render_pt_card(
    pt: Dict[str, Any],
    on_select: Optional[Callable[[Dict[str, Any]], None]] = None
) -> None:
    """
    Component hiển thị Thẻ Huấn Luyện Viên (PT Card) dạng lưới đẹp mắt,
    dành cho Học viên theo chuẩn thiết kế Milestone 5.
    """
    pt_id = pt.get("id")
    full_name = pt.get("fullName", "Huấn luyện viên")
    bio = pt.get("bio") or "Huấn luyện viên chuyên nghiệp tận tâm, đồng hành cùng bạn đạt mục tiêu hình thể."
    exp_years = pt.get("experienceYears", 0)
    locations = pt.get("availableLocations", "Chưa cập nhật khu vực")
    pricing_note = pt.get("locationPricingNote")
    rating = pt.get("averageRating", 0.0)
    total_reviews = pt.get("totalReviews", 0)
    lowest_price = pt.get("lowestPrice")
    avatar_url = normalize_avatar_url(pt.get("avatarUrl")) or "https://api.dicebear.com/7.x/avataaars/svg?seed=" + full_name.replace(" ", "")

    with st.container(border=True):
        col_avatar, col_info = st.columns([1, 3])

        with col_avatar:
            st.image(avatar_url, width=90)
            st.markdown(
                """
                <div style="text-align: center; margin-top: 4px;">
                    <span style="background-color: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                        Đã xác thực
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_info:
            st.markdown(f"#### {full_name}")

            # Rating display
            rating_val = float(rating) if rating is not None else 0.0
            st.markdown(
                f"<span style='color: #f57c00; font-weight: 600;'>Đánh giá: {rating_val:.1f}/5</span> "
                f"<span style='color: #616161; font-size: 0.85rem;'>({total_reviews} đánh giá)</span> "
                f"• <span style='color: #1976d2; font-weight: 500;'>{exp_years} năm KN</span>",
                unsafe_allow_html=True
            )

            # Bio snippet
            snippet = bio[:120] + "..." if len(bio) > 120 else bio
            st.caption(snippet)

        st.markdown(
            f"""
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #37474f;">
                <b>Khu vực:</b> {locations}
            </div>
            """,
            unsafe_allow_html=True
        )

        c_price, c_btn = st.columns([3, 2])
        with c_price:
            if lowest_price:
                st.markdown(f"**Giá chỉ từ:** <span style='color: #d32f2f; font-weight: 700; font-size: 1.1rem;'>{format_currency_vnd(lowest_price)}</span>", unsafe_allow_html=True)
            else:
                st.markdown("**Giá:** <span style='color: #757575;'>Liên hệ xem khóa</span>", unsafe_allow_html=True)

        with c_btn:
            btn_key = f"btn_select_pt_{pt_id}"
            if st.button("Xem Chi Tiết", key=btn_key, use_container_width=True, type="primary"):
                if on_select:
                    on_select(pt)
                else:
                    st.session_state["selected_pt_id"] = pt_id
                    st.session_state["student_active_tab"] = "Chi Tiết & Mua Khóa"
                st.rerun()
