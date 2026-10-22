import os
import time
from pathlib import Path
from typing import Any, Dict
import streamlit as st
from api.auth_api import AuthApi
from api.client import ApiException

AVATAR_STATIC_DIR = Path("static/avatars")


def ensure_avatar_dir():
    """Đảm bảo thư mục lưu trữ avatar tĩnh tồn tại."""
    AVATAR_STATIC_DIR.mkdir(parents=True, exist_ok=True)


def get_local_avatar_file(avatar_url: str) -> Path | None:
    """Kiểm tra nếu avatar_url là đường dẫn tĩnh cục bộ và trả về file path."""
    if not avatar_url:
        return None
    if "app/static/avatars/" in avatar_url:
        fname = avatar_url.split("app/static/avatars/")[-1]
        p = AVATAR_STATIC_DIR / fname
        if p.exists():
            return p
    return None


def render_avatar_management(user: Dict[str, Any], user_role: str = "STUDENT") -> None:
    """
    Component quản lý và tải lên Avatar người dùng (Milestone 6 - Hiệu).
    Hỗ trợ 3 phương thức:
    1. Tải trực tiếp file ảnh từ máy tính (PNG, JPG, WEBP).
    2. Dán link ảnh từ mạng / CDN công khai (Imgur, Postimages, Facebook, GitHub, v.v.).
    3. Chọn nhanh ảnh mẫu phong cách thể thao / học viên.
    """
    ensure_avatar_dir()

    user_id = user.get("id") or user.get("userId") or "user"
    avatar_url = user.get("avatarUrl") or st.session_state.get("user", {}).get("avatarUrl")

    with st.container(border=True):
        st.markdown("### 🖼️ Ảnh Đại Diện (Avatar)")
        col_preview, col_controls = st.columns([1, 2.8])

        with col_preview:
            local_p = get_local_avatar_file(avatar_url)
            if local_p:
                st.image(str(local_p), width=130, caption="Ảnh đại diện hiện tại")
            elif avatar_url:
                try:
                    st.image(avatar_url, width=130, caption="Ảnh đại diện hiện tại")
                except Exception:
                    st.warning("⚠️ Không thể tải trước ảnh từ URL hiện tại")
            else:
                default_icon = "🏋️" if user_role == "PT" else "👤"
                st.markdown(
                    f"""
                    <div style="width: 130px; height: 130px; border-radius: 50%; background: #e3f2fd; display: flex; align-items: center; justify-content: center; font-size: 3.5rem; border: 3px solid #1976d2; margin: 0 auto;">
                        {default_icon}
                    </div>
                    <div style="font-size: 0.85rem; color: #888; text-align: center; margin-top: 8px;">Chưa cài đặt avatar</div>
                    """,
                    unsafe_allow_html=True
                )

        with col_controls:
            choice = st.radio(
                "Chọn cách tải ảnh của bạn:",
                [
                    "📤 Tải file từ máy tính của bạn",
                    "🔗 Dán đường link ảnh từ Internet",
                    "✨ Chọn ảnh mẫu có sẵn"
                ],
                horizontal=True,
                key=f"avatar_choice_{user_role}"
            )

            # PHƯƠNG THỨC 1: TẢI TỆP TRỰC TIẾP TỪ MÁY TÍNH
            if choice == "📤 Tải file từ máy tính của bạn":
                st.caption("Hỗ trợ định dạng: `.jpg`, `.jpeg`, `.png`, `.webp`. Dung lượng tối đa 10MB.")
                uploaded_file = st.file_uploader(
                    "Bấm Browse để chọn ảnh từ máy:",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"file_uploader_{user_role}"
                )

                if uploaded_file is not None:
                    col_file_prev, col_file_btn = st.columns([1, 2])
                    with col_file_prev:
                        st.image(uploaded_file, width=100, caption="Ảnh vừa chọn")
                    with col_file_btn:
                        st.markdown(f"**Tệp:** `{uploaded_file.name}` ({round(uploaded_file.size / 1024, 1)} KB)")
                        if st.button("💾 Lưu Ảnh Tải Lên Làm Avatar", key=f"btn_save_uploaded_{user_role}", type="primary"):
                            try:
                                ext = os.path.splitext(uploaded_file.name)[1].lower() or ".jpg"
                                safe_filename = f"avatar_{user_id}_{int(time.time())}{ext}"
                                target_path = AVATAR_STATIC_DIR / safe_filename
                                target_path.write_bytes(uploaded_file.getbuffer())

                                # Tạo đường link tĩnh phục vụ bởi Streamlit
                                final_avatar_url = f"http://localhost:8501/app/static/avatars/{safe_filename}"
                                AuthApi.update_avatar(final_avatar_url)

                                st.success("✅ Đã cập nhật ảnh đại diện từ máy tính thành công!")
                                time.sleep(0.5)
                                st.rerun()
                            except ApiException as e:
                                st.error(f"❌ Cập nhật thất bại [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"❌ Lỗi xử lý tệp: {str(ex)}")

            # PHƯƠNG THỨC 2: DÁN ĐƯỜNG LINK ẢNH TỪ WEB
            elif choice == "🔗 Dán đường link ảnh từ Internet":
                st.caption("Dán link ảnh trực tiếp từ Facebook, Imgur, Postimages.org, GitHub hoặc bất kỳ CDN nào.")
                new_url = st.text_input(
                    "Đường dẫn URL ảnh:",
                    value=avatar_url or "",
                    placeholder="https://i.imgur.com/example.jpg",
                    key=f"input_url_{user_role}"
                )
                if st.button("💾 Lưu Đường Link Ảnh", key=f"btn_save_url_{user_role}", type="primary"):
                    clean_url = new_url.strip()
                    if not clean_url:
                        st.error("❌ Vui lòng nhập link ảnh hợp lệ!")
                    elif not (clean_url.startswith("http://") or clean_url.startswith("https://")):
                        st.error("❌ Đường dẫn phải bắt đầu bằng http:// hoặc https://")
                    else:
                        try:
                            AuthApi.update_avatar(clean_url)
                            st.success("✅ Đã lưu đường link ảnh đại diện thành công!")
                            time.sleep(0.5)
                            st.rerun()
                        except ApiException as e:
                            st.error(f"❌ Cập nhật thất bại [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"❌ Lỗi: {str(ex)}")

            # PHƯƠNG THỨC 3: ẢNH MẪU CÓ SẴN
            else:
                st.caption("Hoặc bấm vào ảnh mẫu bất kỳ để thử nghiệm ngay lập tức:")
                if user_role == "PT":
                    sample_list = [
                        ("Huấn Luyện Viên 1", "https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=400&auto=format&fit=crop"),
                        ("Huấn Luyện Viên 2", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop"),
                        ("Huấn Luyện Viên 3", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop"),
                        ("Huấn Luyện Viên 4", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=400&auto=format&fit=crop")
                    ]
                else:
                    sample_list = [
                        ("Học Viên Năng Động", "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400&auto=format&fit=crop"),
                        ("Học Viên Nữ", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop"),
                        ("Học Viên Nam", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop"),
                        ("Học Viên Thể Thao", "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&auto=format&fit=crop")
                    ]

                s_cols = st.columns(4)
                for i, (label, s_url) in enumerate(sample_list):
                    with s_cols[i]:
                        st.image(s_url, width=80)
                        if st.button(f"Chọn", key=f"btn_sample_{user_role}_{i}", use_container_width=True):
                            try:
                                AuthApi.update_avatar(s_url)
                                st.success(f"✅ Đã chọn {label}!")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as ex:
                                st.error(f"❌ Lỗi: {str(ex)}")
