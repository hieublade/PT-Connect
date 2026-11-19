from typing import Any, Callable, Dict, Optional
import streamlit as st
from components.avatar_uploader import normalize_avatar_url, get_display_avatar


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
    Component hiển thị Thẻ Huấn Luyện Viên (PT Card) dạng lưới,
    phong cách tối giản Xanh - Trắng, không hiển thị trạng thái online/offline.
    """
    pt_id = pt.get("id")
    full_name = pt.get("fullName", "Huấn luyện viên")
    bio = pt.get("bio") or "Huấn luyện viên chuyên nghiệp tận tâm, đồng hành cùng bạn đạt mục tiêu hình thể."
    exp_years = pt.get("experienceYears", 0)
    locations = pt.get("availableLocations", "Chưa cập nhật khu vực")
    rating = pt.get("averageRating", 0.0)
    total_reviews = pt.get("totalReviews", 0)
    lowest_price = pt.get("lowestPrice")
    match_pct = pt.get("match_percentage")
    avatar_display = get_display_avatar(pt.get("avatarUrl") or pt.get("avatar_url"), default_seed=full_name)

    with st.container(border=True):
        col_avatar, col_info = st.columns([1, 3])

        with col_avatar:
            st.image(avatar_display, width=90)
            st.markdown(
                """
                <div style="text-align: center; margin-top: 4px;">
                    <span style="background-color: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; padding: 2px 8px; border-radius: 12px; font-size: 0.74rem; font-weight: 700;">
                        Đã xác thực
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_info:
            if match_pct is not None:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 2px;">
                        <span style="background: #0284c7; color: #ffffff; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.76rem;">
                            Độ phù hợp: {float(match_pct):.1f}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(f"<h4 style='margin: 0 0 4px 0; color: #0f172a; font-weight: 700;'>{full_name}</h4>", unsafe_allow_html=True)

            # Rating display
            rating_val = float(rating) if rating is not None else 0.0
            st.markdown(
                f"<span style='color: #d97706; font-weight: 600;'>Đánh giá: {rating_val:.1f}/5</span> "
                f"<span style='color: #64748b; font-size: 0.85rem;'>({total_reviews} đánh giá)</span> "
                f"• <span style='color: #0284c7; font-weight: 600;'>{exp_years} năm kinh nghiệm</span>",
                unsafe_allow_html=True
            )

            # Bio snippet
            snippet = bio[:120] + "..." if len(bio) > 120 else bio
            st.caption(snippet)

        st.markdown(
            f"""
            <div style="margin-top: 0.4rem; font-size: 0.88rem; color: #334155; background: #f8fafc; padding: 6px 10px; border-radius: 8px; border-left: 3px solid #0284c7;">
                <b style="color: #0284c7;">Khu vực:</b> {locations}
            </div>
            """,
            unsafe_allow_html=True
        )

        c_price, c_btn = st.columns([3, 2])
        with c_price:
            if lowest_price:
                st.markdown(f"**Giá chỉ từ:** <span style='color: #0284c7; font-weight: 800; font-size: 1.1rem;'>{format_currency_vnd(lowest_price)}</span>", unsafe_allow_html=True)
            else:
                st.markdown("**Giá:** <span style='color: #64748b;'>Liên hệ xem khóa</span>", unsafe_allow_html=True)

        with c_btn:
            btn_key = f"btn_select_pt_{pt_id}"

            def _on_pt_card_click(target_id=pt_id, target_pt=pt):
                st.session_state["selected_pt_id"] = target_id
                st.session_state["student_pt_select_box"] = target_id
                st.session_state["student_home_tabs"] = "Chi Tiết"
                st.session_state["switch_to_tab"] = "Chi Tiết"
                if on_select:
                    try:
                        on_select(target_pt)
                    except Exception:
                        pass

            st.button(
                "Xem Chi Tiết",
                key=btn_key,
                use_container_width=True,
                type="primary",
                on_click=_on_pt_card_click
            )
