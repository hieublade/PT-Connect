import os
import time
from pathlib import Path
from typing import Any, Dict
import streamlit as st
from api.auth_api import AuthApi
from api.client import ApiException

AVATAR_STATIC_DIR = Path("static/avatars")
AVATAR_UPLOADS_DIR = Path("static/uploads/avatars")


def ensure_avatar_dir():
    """Đảm bảo thư mục lưu trữ avatar tĩnh tồn tại."""
    AVATAR_STATIC_DIR.mkdir(parents=True, exist_ok=True)
    AVATAR_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_local_avatar_file(avatar_url: str | None) -> Path | None:
    """Kiểm tra nếu avatar_url tương ứng file cục bộ trên đĩa và trả về file path."""
    if not avatar_url:
        return None
    url_str = str(avatar_url).strip()
    
    # 1. Trích xuất tên file
    filename = Path(url_str).name
    if not filename:
        return None

    # 2. Tìm kiếm trong static/uploads/avatars
    p1 = AVATAR_UPLOADS_DIR / filename
    if p1.exists():
        return p1

    # 3. Tìm kiếm trong static/avatars
    p2 = AVATAR_STATIC_DIR / filename
    if p2.exists():
        return p2

    # 4. Tìm kiếm tương đối từ thư mục hiện tại
    cleaned = url_str.lstrip("/").replace("app/", "")
    p3 = Path(cleaned)
    if p3.exists():
        return p3

    return None


def get_avatar_image_bytes(avatar_url: str | None) -> bytes | None:
    """Tải bytes của ảnh từ file cục bộ hoặc URL để truyền trực tiếp vào st.image đảm bảo hiển thị 100% không lỗi mạng."""
    if not avatar_url:
        return None
    local_p = get_local_avatar_file(avatar_url)
    if local_p and local_p.exists():
        try:
            return local_p.read_bytes()
        except Exception:
            pass

    import requests
    from api.client import api_client
    target_url = avatar_url
    if avatar_url.startswith("/static/"):
        target_url = f"{api_client.base_url}{avatar_url}"

    try:
        res = requests.get(target_url, timeout=5)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None


def normalize_avatar_url(avatar_url: str | None) -> str | None:
    """Chuẩn hóa avatar_url để Streamlit hoặc client hiển thị chính xác."""
    if not avatar_url:
        return None
    url = str(avatar_url).strip()
    if url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/"):
        return url
    if url.startswith("/app/static/"):
        return url
    if url.startswith("/static/"):
        return f"/app{url}"
    if url.startswith("static/"):
        return f"/app/{url}"
    return url


def get_display_avatar(avatar_url: str | None, default_seed: str = "User"):
    """
    Hàm chuẩn hóa hình ảnh đại diện:
    - Nếu là file cục bộ tồn tại trên đĩa (uploads/avatars/...), trả về bytes hoặc Image để st.image render trực tiếp.
    - Nếu là URL bên ngoài (Dicebear, SVG, CDN), trả về URL.
    - Nếu None/rỗng, trả về Dicebear URL mặc định.
    """
    if not avatar_url:
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={default_seed.replace(' ', '')}"
    
    # Kiểm tra file cục bộ
    local_p = get_local_avatar_file(avatar_url)
    if local_p and local_p.exists():
        try:
            return local_p.read_bytes()
        except Exception:
            pass

    # Nếu là link nội bộ /static/
    if str(avatar_url).startswith("/static/") or str(avatar_url).startswith("/app/static/"):
        b = get_avatar_image_bytes(avatar_url)
        if b:
            return b

    return avatar_url


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
        st.markdown("### Ảnh Đại Diện (Avatar)")
        col_preview, col_controls = st.columns([1, 2.8])

        with col_preview:
            # 1. Nếu là file tĩnh cục bộ
            local_p = get_local_avatar_file(avatar_url)
            if local_p:
                st.image(str(local_p), width=130, caption="Ảnh đại diện hiện tại")
            # 2. Nếu là ảnh SVG (như Dicebear API)
            elif avatar_url and (".svg" in avatar_url or "dicebear" in avatar_url):
                try:
                    import requests
                    res = requests.get(avatar_url, timeout=5)
                    if res.status_code == 200:
                        st.markdown(
                            f'<div style="width: 130px; height: 130px; border-radius: 50%; overflow: hidden; margin: 0 auto;">{res.text}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.image(avatar_url, width=130, caption="Ảnh đại diện hiện tại")
                except Exception:
                    st.image(avatar_url, width=130, caption="Ảnh đại diện hiện tại")
            # 3. Nếu là ảnh tĩnh upload từ backend (/static/...)
            elif avatar_url and avatar_url.startswith("/static/"):
                img_bytes = get_avatar_image_bytes(avatar_url)
                if img_bytes:
                    try:
                        st.image(img_bytes, width=130, caption="Ảnh đại diện hiện tại")
                    except Exception:
                        st.warning("Không thể hiển thị ảnh đại diện")
                else:
                    st.warning("Không thể tải ảnh từ máy chủ")
            # 4. Các URL ảnh thông thường khác (PNG, JPG từ mạng)
            elif avatar_url:
                try:
                    st.image(avatar_url, width=130, caption="Ảnh đại diện hiện tại")
                except Exception:
                    st.warning("Không thể tải trước ảnh từ URL hiện tại")
            else:
                default_text = "PT" if user_role == "PT" else "USER"
                st.markdown(
                    f"""
                    <div style="width: 130px; height: 130px; border-radius: 50%; background: #e3f2fd; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: #1976d2; border: none; margin: 0 auto;">
                        {default_text}
                    </div>
                    <div style="font-size: 0.85rem; color: #888; text-align: center; margin-top: 8px;">Chưa cài đặt avatar</div>
                    """,
                    unsafe_allow_html=True
                )

        with col_controls:
            choice = st.radio(
                "Chọn cách tải ảnh của bạn:",
                [
                    "Tải file từ máy tính của bạn",
                    "Dán đường link ảnh từ Internet"
                ],
                horizontal=True,
                key=f"avatar_choice_{user_role}"
            )

            # PHƯƠNG THỨC 1: TẢI TỆP TRỰC TIẾP TỪ MÁY TÍNH
            if choice == "Tải file từ máy tính của bạn":
                st.caption("Hỗ trợ định dạng: `.jpg`, `.jpeg`, `.png`, `.webp`. Dung lượng tối đa 10MB.")
                uploaded_file = st.file_uploader(
                    "Bấm Browse để chọn ảnh từ máy:",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"file_uploader_{user_role}"
                )

                if uploaded_file is not None:
                    col_file_prev, col_file_btn = st.columns([1, 2])
                    with col_file_prev:
                        try:
                            st.image(uploaded_file, width=100, caption="Ảnh vừa chọn")
                        except Exception:
                            st.error("Tệp không hợp lệ!")
                    with col_file_btn:
                        st.markdown(f"**Tệp:** `{uploaded_file.name}` ({round(uploaded_file.size / 1024, 1)} KB)")
                        if st.button("Lưu Ảnh Tải Lên Làm Avatar", key=f"btn_save_uploaded_{user_role}", type="primary"):
                            try:
                                try:
                                    AuthApi.upload_avatar_file(uploaded_file.getvalue(), uploaded_file.name)
                                except Exception:
                                    ext = os.path.splitext(uploaded_file.name)[1].lower() or ".jpg"
                                    safe_filename = f"avatar_{user_id}_{int(time.time())}{ext}"
                                    target_path = AVATAR_STATIC_DIR / safe_filename
                                    target_path.write_bytes(uploaded_file.getbuffer())

                                    # Tạo đường link tĩnh phục vụ bởi Streamlit
                                    final_avatar_url = f"/app/static/avatars/{safe_filename}"
                                    AuthApi.update_avatar(final_avatar_url)

                                st.success("Đã cập nhật ảnh đại diện từ máy tính thành công!")
                                time.sleep(0.5)
                                st.rerun()
                            except ApiException as e:
                                st.error(f"Cập nhật thất bại [{e.status_code}]: {e.message}")
                            except Exception as ex:
                                st.error(f"Lỗi xử lý tệp: {str(ex)}")

            # PHƯƠNG THỨC 2: DÁN ĐƯỜNG LINK ẢNH TỪ WEB
            else:
                st.caption("Dán link ảnh trực tiếp từ Facebook, Imgur, Postimages.org, GitHub hoặc bất kỳ CDN nào.")
                new_url = st.text_input(
                    "Đường dẫn URL ảnh:",
                    value=avatar_url or "",
                    placeholder="https://i.imgur.com/example.jpg",
                    key=f"input_url_{user_role}"
                )
                if st.button("Lưu Đường Link Ảnh", key=f"btn_save_url_{user_role}", type="primary"):
                    clean_url = new_url.strip()
                    if not clean_url:
                        st.error("Vui lòng nhập link ảnh hợp lệ!")
                    elif not (clean_url.startswith("http://") or clean_url.startswith("https://")):
                        st.error("Đường dẫn phải bắt đầu bằng http:// hoặc https://")
                    else:
                        try:
                            AuthApi.update_avatar(clean_url)
                            st.success("Đã lưu đường link ảnh đại diện thành công!")
                            time.sleep(0.5)
                            st.rerun()
                        except ApiException as e:
                            st.error(f"Cập nhật thất bại [{e.status_code}]: {e.message}")
                        except Exception as ex:
                            st.error(f"Lỗi: {str(ex)}")
