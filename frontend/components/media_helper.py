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

STATIC_UPLOADS_DIR = Path("static/uploads")


def normalize_media_url(url: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa đường dẫn hình ảnh để trình duyệt mở trực tiếp mà không bị lỗi trang trắng của Streamlit SPA.
    - '/static/uploads/abc.png' -> '/app/static/uploads/abc.png'
    - 'static/uploads/abc.png'  -> '/app/static/uploads/abc.png'
    """
    if not url:
        return None
    url = str(url).strip()
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
    return url


def get_local_media_path(url: Optional[str]) -> Optional[Path]:
    """Trả về Path cục bộ trên disk nếu file tồn tại trong thư mục static/uploads."""
    if not url:
        return None
    filename = Path(url).name
    candidate = STATIC_UPLOADS_DIR / filename
    if candidate.exists():
        return candidate
    return None


def render_evidence_viewer(evidence_url: Optional[str], caption: str = "Ảnh bằng chứng đối chứng", width: int = 400):
    """
    Hiển thị hình ảnh bằng chứng trực quan ngay trong giao diện Streamlit,
    kèm nút bấm mở ảnh full kích thước trong tab mới (không bị lỗi màn hình trắng).
    """
    if not evidence_url:
        return

    clean_url = normalize_media_url(evidence_url)
    local_path = get_local_media_path(evidence_url)

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
