"""
floating_chat_widget.py
Thành phần Nút Chat Trực Tuyến Nổi (Floating Chat Widget)
Khớp với hình ảnh 2: Nút tròn màu xanh biển ở góc dưới bên phải màn hình.
Giao diện tối giản xanh - trắng, không hiển thị trạng thái online/offline.
Dữ liệu lưu trữ tối giản vào đúng 1 bảng duy nhất (chat_messages).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import streamlit as st
from db_repository import db_repo


def _sanitize_chat_text(text: str) -> str:
    """Tự động chuẩn hóa và khắc phục lỗi font chữ (mojibake) tiếng Việt nếu có."""
    if not text:
        return ""
    try:
        if any(marker in text for marker in ("Ã", "á»", "áº", "Ä", "Æ")):
            return text.encode("latin1").decode("utf-8")
    except Exception:
        pass
    return text


def close_live_chat_dialog():
    """Đóng hộp thoại trò chuyện trực tiếp khi người dùng bấm X hoặc đóng."""
    st.session_state["live_chat_is_open"] = False


def handle_send_chat_message(sender_id: int, receiver_id: int, input_key: str):
    """Callback gửi tin nhắn trực tiếp không làm giật hay đóng mở lại khung chat."""
    text = st.session_state.get(input_key, "")
    if text and text.strip():
        db_repo.send_direct_chat_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=text.strip(),
        )


@st.dialog("Hộp Thoại Trò Chuyện Trực Tiếp (Live Chat)", width="large", on_dismiss=close_live_chat_dialog)
def open_live_chat_dialog(current_user: Dict[str, Any], initial_pt_id: Optional[int] = None):
    """
    Hộp thoại trò chuyện trực tiếp 2 chiều giữa Học viên và Huấn luyện viên.
    Phong cách tối giản Xanh - Trắng, không hiển thị trạng thái online/offline.
    """
    user_id = current_user.get("id")
    user_role = current_user.get("role", "STUDENT")

    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px; border-bottom: 1.5px solid #e2e8f0; margin-bottom: 14px;">
            <div>
                <h3 style="margin: 0; color: #0284c7; font-weight: 800; font-size: 1.3rem;">
                    💬 Trò Chuyện Trực Tuyến 1-1
                </h3>
                <p style="margin: 2px 0 0 0; color: #64748b; font-size: 0.85rem;">
                    Kênh nhắn tin trao đổi trực tiếp giữa Học viên và Huấn luyện viên
                </p>
            </div>
            <div>
                <span style="background: #e0f2fe; color: #0284c7; border: 1px solid #bae6fd; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">
                    Kết Nối Trực Tiếp
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. CHỌN ĐỐI TÁC TRÒ CHUYỆN (PARTNER SELECTION)
    partner_user_id = None
    partner_name = "Đối tác"
    partner_avatar = None
    partner_subtitle = ""

    if user_role == "STUDENT":
        # Học viên chọn PT để trò chuyện
        pts = db_repo.get_all_pts_for_recommendation()
        if not pts:
            st.warning("Hiện chưa có Huấn luyện viên nào trong hệ thống.")
            return

        # Thống kê tin nhắn để ưu tiên PT đã có trao đổi
        pt_msg_stats = {}
        try:
            with db_repo.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT p.user_id, MAX(cm.created_at) AS last_msg_time,
                               COUNT(CASE WHEN cm.receiver_id = %s AND cm.is_read = FALSE THEN 1 END) AS unread_count
                        FROM pt_profiles p
                        JOIN chat_messages cm ON (cm.sender_id = p.user_id AND cm.receiver_id = %s)
                                              OR (cm.sender_id = %s AND cm.receiver_id = p.user_id)
                        GROUP BY p.user_id;
                        """,
                        (user_id, user_id, user_id),
                    )
                    pt_msg_stats = {row["user_id"]: row for row in cur.fetchall()}
        except Exception:
            pt_msg_stats = {}

        # Sắp xếp: PT có tin nhắn lên đầu
        pts = sorted(
            pts,
            key=lambda p: (
                0 if p.get("user_id") in pt_msg_stats else 1,
                -(pt_msg_stats[p.get("user_id")]["last_msg_time"].timestamp() if p.get("user_id") in pt_msg_stats and pt_msg_stats[p.get("user_id")]["last_msg_time"] else 0),
            )
        )

        pt_map = {}
        for p in pts:
            p_uid = p.get("user_id")
            p_name = p.get("fullName", "Huấn luyện viên")
            spec_val = p.get("specialty") or p.get("specialties")
            specialty_text = f" ({spec_val})" if spec_val else ""
            stat = pt_msg_stats.get(p_uid)
            if stat and stat.get("unread_count", 0) > 0:
                unread_badge = f"[{stat['unread_count']} tin mới] "
            elif stat:
                unread_badge = "[Đã kết nối] "
            else:
                unread_badge = ""
            label = f"{unread_badge}{p_name} - {p.get('experienceYears', 0)} năm kinh nghiệm{specialty_text}"
            pt_map[p_uid] = (label, p)

        default_idx = 0
        target_uid = None
        if initial_pt_id:
            match_pt = next((p for p in pts if p.get("id") == initial_pt_id), None)
            if match_pt:
                target_uid = match_pt.get("user_id")

        if target_uid and target_uid in pt_map:
            if st.session_state.get("live_chat_just_opened_target"):
                st.session_state["chat_select_partner_pt"] = target_uid
                st.session_state["live_chat_just_opened_target"] = False
            default_idx = list(pt_map.keys()).index(target_uid)
        elif "active_chat_pt_uid" in st.session_state and st.session_state["active_chat_pt_uid"] in pt_map:
            default_idx = list(pt_map.keys()).index(st.session_state["active_chat_pt_uid"])

        chosen_uid = st.selectbox(
            "Chọn Huấn luyện viên để nhắn tin:",
            options=list(pt_map.keys()),
            format_func=lambda uid: pt_map[uid][0],
            index=default_idx,
            key="chat_select_partner_pt",
        )
        st.session_state["active_chat_pt_uid"] = chosen_uid

        partner_user_id = chosen_uid
        chosen_data = pt_map[chosen_uid][1]
        partner_name = chosen_data.get("fullName", "Huấn luyện viên")
        partner_avatar = chosen_data.get("avatarUrl")
        spec_info = chosen_data.get("specialty") or chosen_data.get("specialties") or "Thể hình & Thể lực"
        partner_subtitle = f"{chosen_data.get('experienceYears', 0)} năm KN • {spec_info}"

    else:
        # PT chọn Học viên để trả lời tư vấn: Ưu tiên học viên có tin nhắn mới nhất lên đầu
        with db_repo.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        u.id, 
                        u.full_name, 
                        u.avatar_url, 
                        u.phone,
                        u.email,
                        MAX(cm.created_at) AS last_msg_time,
                        COUNT(CASE WHEN cm.receiver_id = %s AND cm.is_read = FALSE THEN 1 END) AS unread_count,
                        (
                            SELECT content 
                            FROM chat_messages 
                            WHERE (sender_id = u.id AND receiver_id = %s) 
                               OR (sender_id = %s AND receiver_id = u.id) 
                            ORDER BY id DESC LIMIT 1
                        ) AS last_content
                    FROM users u
                    LEFT JOIN chat_messages cm 
                           ON (cm.sender_id = u.id AND cm.receiver_id = %s) 
                           OR (cm.sender_id = %s AND cm.receiver_id = u.id)
                    WHERE u.role = 'STUDENT'
                    GROUP BY u.id, u.full_name, u.avatar_url, u.phone, u.email
                    ORDER BY 
                        (CASE WHEN MAX(cm.created_at) IS NOT NULL THEN 0 ELSE 1 END) ASC,
                        last_msg_time DESC,
                        u.id DESC;
                    """,
                    (user_id, user_id, user_id, user_id, user_id),
                )
                student_list = cur.fetchall()

        if not student_list:
            st.info("Hiện chưa có học viên nào trong hệ thống.")
            return

        st_map = {}
        for s in student_list:
            s_uid = s.get("id")
            s_name = s.get("full_name") or s.get("email") or "Học viên"
            unread = s.get("unread_count") or 0
            last_content = s.get("last_content")
            last_time = s.get("last_msg_time")

            if unread > 0:
                time_str = last_time.strftime("%H:%M") if isinstance(last_time, datetime) else str(last_time)[11:16]
                snippet = f" - '{last_content[:24]}...'" if last_content else ""
                label = f"[{unread} tin nhắn mới] {s_name}{snippet} ({time_str})"
            elif last_content:
                time_str = last_time.strftime("%H:%M") if isinstance(last_time, datetime) else str(last_time)[11:16]
                snippet = f" - '{last_content[:24]}...'" if last_content else ""
                label = f"{s_name}{snippet} ({time_str})"
            else:
                contact_info = s.get("phone") or s.get("email") or "Chưa có liên hệ"
                label = f"{s_name} ({contact_info})"

            st_map[s_uid] = (label, s)

        # Mặc định chọn học viên đầu tiên (học viên có tin nhắn mới nhất)
        default_st_idx = 0
        if "chat_select_student_partner" in st.session_state and st.session_state["chat_select_student_partner"] in st_map:
            default_st_idx = list(st_map.keys()).index(st.session_state["chat_select_student_partner"])

        chosen_st_uid = st.selectbox(
            "Chọn Học viên để trả lời tư vấn:",
            options=list(st_map.keys()),
            format_func=lambda suid: st_map[suid][0],
            index=default_st_idx,
            key="chat_select_student_partner",
        )
        partner_user_id = chosen_st_uid
        chosen_s_data = st_map[chosen_st_uid][1]
        partner_name = chosen_s_data.get("full_name") or chosen_s_data.get("email") or "Học viên"
        partner_avatar = chosen_s_data.get("avatar_url")
        partner_subtitle = f"Email: {chosen_s_data.get('email', 'N/A')} • SĐT: {chosen_s_data.get('phone', 'N/A')}"

    # 2. THÔNG TIN ĐỐI TÁC (TỐI GIẢN XANH - TRẮNG)
    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <img src="{partner_avatar or 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + partner_name}" style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #0284c7; background: #ffffff;" />
                <div>
                    <strong style="color: #0f172a; font-size: 1.05rem;">{partner_name}</strong>
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 500;">
                        {partner_subtitle}
                    </div>
                </div>
            </div>
            <div>
                <span style="background: #ffffff; color: #0284c7; border: 1.5px solid #0284c7; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 6px;">
                    1-1 Trực Tiếp
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. DANH SÁCH TIN NHẮN (KHÔNG BỊ LỖI RAW HTML)
    messages = db_repo.get_direct_chat_messages(user_id, partner_user_id)

    with st.container(height=320):
        if not messages:
            st.info("Chưa có tin nhắn nào giữa hai bạn. Hãy nhập câu hỏi hoặc lời chào bên dưới để bắt đầu trao đổi!")
        else:
            for msg in messages:
                is_me = (msg.get("sender_id") == user_id)
                content = _sanitize_chat_text(msg.get("content", ""))
                raw_time = msg.get("created_at")
                if isinstance(raw_time, datetime):
                    time_str = raw_time.strftime("%H:%M")
                else:
                    time_str = str(raw_time)[:16] if raw_time else ""

                if is_me:
                    bubble_html = (
                        f'<div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">'
                        f'<div style="background: #0284c7; color: #ffffff; padding: 9px 14px; border-radius: 14px 14px 2px 14px; max-width: 75%; box-shadow: 0 2px 6px rgba(2, 132, 199, 0.25);">'
                        f'<div style="font-size: 0.92rem; line-height: 1.45; word-break: break-word;">{content}</div>'
                        f'<div style="font-size: 0.7rem; color: #e0f2fe; text-align: right; margin-top: 3px;">{time_str} • Tôi</div>'
                        f'</div></div>'
                    )
                else:
                    bubble_html = (
                        f'<div style="display: flex; justify-content: flex-start; margin-bottom: 8px;">'
                        f'<div style="background: #f1f5f9; color: #0f172a; padding: 9px 14px; border-radius: 14px 14px 14px 2px; max-width: 75%; border: 1px solid #e2e8f0;">'
                        f'<div style="font-size: 0.74rem; color: #0284c7; font-weight: 700; margin-bottom: 2px;">{partner_name}</div>'
                        f'<div style="font-size: 0.92rem; line-height: 1.45; word-break: break-word;">{content}</div>'
                        f'<div style="font-size: 0.7rem; color: #94a3b8; text-align: right; margin-top: 3px;">{time_str}</div>'
                        f'</div></div>'
                    )
                st.markdown(bubble_html, unsafe_allow_html=True)

    input_box_key = f"chat_text_input_{partner_user_id}"

    # 4. Ô NHẬP TIN NHẮN & NÚT GỬI (DÙNG ON_CLICK CALLBACK ĐỂ KHÔNG BỊ TẮT / BẬT LẠI KHUNG CHAT)
    with st.form(key=f"chat_form_{partner_user_id}", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            st.text_input(
                "Nhập tin nhắn:",
                placeholder="Nhập nội dung trao đổi trực tiếp (nhấn Enter để gửi)...",
                label_visibility="collapsed",
                key=input_box_key,
            )
        with col_btn:
            st.form_submit_button(
                "Gửi",
                type="primary",
                use_container_width=True,
                on_click=handle_send_chat_message,
                args=(user_id, partner_user_id, input_box_key),
            )

    col_close, _ = st.columns([1, 4])
    with col_close:
        if st.button("Đóng chat", key=f"btn_close_chat_dialog_{partner_user_id}", use_container_width=True):
            close_live_chat_dialog()
            st.rerun()


def render_floating_chat_widget(user: Dict[str, Any]):
    """
    Hiển thị nút tròn chat nổi cố định tại góc dưới bên phải màn hình (Bottom-Right Floating Bubble).
    Thiết kế siêu to, màu sắc Gradient Đa Sắc Rực Rỡ (Hồng Neon - Tím Đậm - Xanh Biển - Cyan Ngọc).
    Hoàn toàn không dùng màu trắng đơn điệu, hiệu ứng sóng hào quang nổi bật tuyệt đẹp.
    """
    if not user:
        return

    # 1. Inject CSS cho nút chat tròn nổi (Kích thước 82px, Gradient 4 màu neon cực kỳ bắt mắt)
    st.markdown(
        """
        <style>
        @keyframes chatPulseGlowRainbow {
            0% {
                box-shadow: 0 10px 30px rgba(249, 115, 22, 0.6), 0 0 0 0 rgba(2, 132, 199, 0.7);
            }
            60% {
                box-shadow: 0 10px 30px rgba(249, 115, 22, 0.6), 0 0 0 22px rgba(2, 132, 199, 0);
            }
            100% {
                box-shadow: 0 10px 30px rgba(249, 115, 22, 0.6), 0 0 0 0 rgba(2, 132, 199, 0);
            }
        }
        .st-key-btn_floating_live_chat,
        div[class*="st-key-btn_floating_live_chat"],
        div:has(> div > button[key="btn_floating_live_chat"]),
        div:has(> button[key="btn_floating_live_chat"]) {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 999999 !important;
            width: 82px !important;
            height: 82px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
            display: block !important;
        }
        .st-key-btn_floating_live_chat .stButton,
        .st-key-btn_floating_live_chat div[data-testid="stButton"],
        div[class*="st-key-btn_floating_live_chat"] div {
            width: 82px !important;
            height: 82px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }
        .st-key-btn_floating_live_chat button,
        div[class*="st-key-btn_floating_live_chat"] button,
        button[key="btn_floating_live_chat"] {
            position: relative !important;
            width: 82px !important;
            height: 82px !important;
            min-width: 82px !important;
            min-height: 82px !important;
            max-width: 82px !important;
            max-height: 82px !important;
            border-radius: 50% !important;
            /* Phối màu Gradient 3 màu thể thao bắt mắt: Cam San Hô -> Cam Cháy -> Xanh Coban */
            background: linear-gradient(135deg, #f97316 0%, #ea580c 45%, #0284c7 100%) !important;
            border: 3.5px solid #ffffff !important;
            box-shadow: 0 10px 30px rgba(249, 115, 22, 0.55), 0 0 25px rgba(2, 132, 199, 0.45) !important;
            animation: chatPulseGlowRainbow 2.8s infinite !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            margin: 0 !important;
            cursor: pointer !important;
            transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }
        .st-key-btn_floating_live_chat button [data-testid="stMarkdownContainer"],
        div[class*="st-key-btn_floating_live_chat"] button [data-testid="stMarkdownContainer"] {
            display: none !important;
        }
        .st-key-btn_floating_live_chat button::after,
        div[class*="st-key-btn_floating_live_chat"] button::after {
            content: "" !important;
            display: block !important;
            width: 46px !important;
            height: 46px !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
            background-size: contain !important;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ffffff'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12c0 1.85.5 3.58 1.38 5.08L2.05 21.95c-.15.42.22.84.66.75l4.98-1.07C9.13 22.42 10.53 22.8 12 22.8c5.52 0 10-4.48 10-10s-4.48-10-10-10zm-4 11a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm4 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm4 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z'/%3E%3C/svg%3E") !important;
            filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.35)) !important;
        }
        .st-key-btn_floating_live_chat button:hover,
        div[class*="st-key-btn_floating_live_chat"] button:hover {
            transform: scale(1.15) translateY(-5px) rotate(4deg) !important;
            background: linear-gradient(135deg, #ff0844 0%, #ff4e50 40%, #8a2387 80%, #00f2fe 100%) !important;
            box-shadow: 0 18px 45px rgba(255, 0, 127, 0.8), 0 0 30px rgba(0, 242, 254, 0.7) !important;
        }
        .st-key-btn_floating_live_chat button:active,
        div[class*="st-key-btn_floating_live_chat"] button:active {
            transform: scale(0.94) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 2. Inject JS DOM Enforcer để ép style trực tiếp lên element button nếu browser có cache CSS
    st.components.v1.html(
        """
        <script>
        function applyFloatingChatStyle() {
            try {
                const parentDoc = window.parent.document;
                const container = parentDoc.querySelector('.st-key-btn_floating_live_chat');
                if (container) {
                    container.style.position = 'fixed';
                    container.style.bottom = '30px';
                    container.style.right = '30px';
                    container.style.zIndex = '999999';
                    container.style.width = '82px';
                    container.style.height = '82px';
                    
                    const btn = container.querySelector('button');
                    if (btn) {
                        btn.style.width = '82px';
                        btn.style.height = '82px';
                        btn.style.minWidth = '82px';
                        btn.style.minHeight = '82px';
                        btn.style.borderRadius = '50%';
                        btn.style.background = 'linear-gradient(135deg, #ff007f 0%, #7928ca 35%, #0070f3 70%, #00dfd8 100%)';
                        btn.style.border = '3.5px solid #ffffff';
                        btn.style.boxShadow = '0 10px 30px rgba(255, 0, 127, 0.6), 0 0 25px rgba(0, 223, 216, 0.5)';
                        btn.style.cursor = 'pointer';
                        
                        const textCont = btn.querySelector('[data-testid="stMarkdownContainer"]');
                        if (textCont) textCont.style.display = 'none';
                    }
                }
            } catch(e) {}
        }
        setInterval(applyFloatingChatStyle, 300);
        applyFloatingChatStyle();
        </script>
        """,
        height=0,
        width=0,
    )

    if st.button("💬", key="btn_floating_live_chat", type="primary", help="Trò chuyện trực tuyến 1-1 với Huấn luyện viên"):
        st.session_state["live_chat_is_open"] = True
        st.session_state["live_chat_target_pt_id"] = None
        st.rerun()

    if st.session_state.get("live_chat_is_open"):
        open_live_chat_dialog(
            user,
            initial_pt_id=st.session_state.get("live_chat_target_pt_id")
        )
