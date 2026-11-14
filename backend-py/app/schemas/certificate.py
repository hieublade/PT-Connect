import json
from typing import Any

MAX_CERT_URL_LEN = 500


def clean_certificate_url(raw: Any) -> str | None:
    """Chuẩn hóa mọi dạng đầu vào cũ/mới về 1 URL đơn trị (1NF).

    Chấp nhận:
      - "https://a/cert.pdf"                     -> "https://a/cert.pdf"
      - '["https://a/cert.pdf"]' (chuỗi JSON cũ) -> "https://a/cert.pdf"
      - ["https://a/1.pdf", "https://a/2.pdf"]   -> "https://a/1.pdf"   (lấy phần tử đầu tiên khác rỗng)
      - None / "" / "   " / [] / '[]'            -> None
    """
    if raw is None:
        return None
    if isinstance(raw, (list, tuple)):
        for item in raw:
            cleaned = clean_certificate_url(item)
            if cleaned:
                return cleaned
        return None

    s = str(raw).strip()
    if not s:
        return None
    if s.startswith("[") and s.endswith("]"):
        try:
            return clean_certificate_url(json.loads(s))
        except ValueError:
            s = s[1:-1].strip().strip('"').strip("'").strip()
            return s or None
    return s.strip('"').strip() or None
