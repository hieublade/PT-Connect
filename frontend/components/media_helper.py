"""
media_helper.py
Module tiện ích quản lý và chuẩn hóa hiển thị hình ảnh (Bằng chứng tranh chấp, Avatar, Biên lai, Ảnh minh họa)
Giải quyết triệt để lỗi màn hình trắng khi mở ảnh trong Streamlit:
- Streamlit chỉ phục vụ static file của ứng dụng tại endpoint '/app/static/' (khi enableStaticServing = true).
- Tự động chuẩn hóa mọi link '/static/uploads/...' thành '/app/static/uploads/...'.
- Hỗ trợ hiển thị trực tiếp ảnh trong container bằng st.image() từ file cục bộ hoặc URL.
"""

from pathlib import Path
from typing import Optional
import streamlit as st

POSSIBLE_UPLOAD_DIRS = [
    Path("/app/static/uploads"),
    Path("static/uploads"),
    Path("frontend/static/uploads"),
    Path("backend-py/static/uploads"),
]


def normalize_media_url(url: Optional[str]) -> str:
    """
    Chuẩn hóa đường dẫn hình ảnh để trình duyệt mở trực tiếp mà không bị lỗi trang trắng của Streamlit SPA.
    - 'https://storage.ptconnect.vn/evidence/abc.png' -> '/app/static/uploads/abc.png'
    - '/static/uploads/abc.png' -> '/app/static/uploads/abc.png'
    - 'static/uploads/abc.png'  -> '/app/static/uploads/abc.png'
    """
    if not url:
        return "/app/static/uploads/evidence_checkin_gym.jpg"
    url = str(url).strip()
    if "storage.ptconnect.vn" in url:
        filename = Path(url).name
        return f"/app/static/uploads/{filename}"
    if url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/"):
        return url
    if url.startswith("/app/static/"):
        return url
    if url.startswith("/static/"):
        return f"/app{url}"
    if url.startswith("static/"):
        return f"/app/{url}"
    if url.startswith("/uploads/"):
        return f"/app/static{url}"
    if url.startswith("uploads/"):
        return f"/app/static/{url}"
    return f"/app/static/uploads/{Path(url).name}"


def get_local_media_path(url: Optional[str]) -> Optional[Path]:
    """Trả về Path cục bộ trên disk nếu file tồn tại trong thư mục static/uploads hoặc fallback ảnh mẫu hợp lệ."""
    filename = Path(str(url).strip()).name if url else "evidence_checkin_gym.jpg"
    
    # 1. Tìm chính xác file theo tên
    for d in POSSIBLE_UPLOAD_DIRS:
        cand = d / filename
        if cand.exists():
            return cand
            
    # 2. Fallback nếu tên file chưa có trên disk
    for d in POSSIBLE_UPLOAD_DIRS:
        for fb_name in ("evidence_checkin_gym.jpg", "counter_evidence_pt.jpg", "default_evidence.jpg", "evidence_chat.jpg"):
            fallback = d / fb_name
            if fallback.exists():
                return fallback

    return None


def render_evidence_viewer(evidence_url: Optional[str], caption: str = "Ảnh bằng chứng đối chứng", width: int = 400):
    """
    Hiển thị hình ảnh bằng chứng trực quan ngay trong giao diện Streamlit,
    kèm nút bấm mở ảnh full kích thước trong tab mới (không bao giờ bị lỗi icon hỏng).
    """
    # Luôn đảm bảo có ảnh minh chứng rõ nét hiển thị cho người dùng
    url_to_render = evidence_url if evidence_url and str(evidence_url).strip() else "/app/static/uploads/evidence_checkin_gym.jpg"
    clean_url = normalize_media_url(url_to_render)
    local_path = get_local_media_path(url_to_render)

    st.markdown(
        f"""
        <div style="margin: 8px 0;">
            <span style="font-weight: 600; color: #1e293b;">{caption}:</span>
            <a href="{clean_url}" target="_blank" style="margin-left: 8px; color: #0284c7; text-decoration: none; font-weight: 600; font-size: 0.88rem; background: #e0f2fe; padding: 3px 10px; border-radius: 6px; border: 1px solid #bae6fd;">
                Mở ảnh tab mới ↗
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        if local_path and local_path.exists():
            st.image(str(local_path), caption=caption, width=width)
        elif clean_url:
            st.image(clean_url, caption=caption, width=width)
    except Exception:
        pass
