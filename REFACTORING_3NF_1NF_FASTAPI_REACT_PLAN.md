Written for: Antigravity (the coding agent that will apply the changes) and the PT-Connect team.

# KẾ HOẠCH ĐỒNG BỘ CHUẨN HÓA CSDL (1NF & 3NF) CHO `backend-py/` (FastAPI) VÀ `frontend-react/` (React + Vite)

> Tài liệu thực thi cho Antigravity. Làm theo đúng thứ tự từ §2 đến §5. Mỗi bước ghi rõ file, đoạn code cũ, đoạn code mới và cách kiểm tra.
>
> **Đầu vào đã đọc:**
> - `REFACTORING_3NF_1NF_SYNC_GUIDE.md` và `REFACTORING_CHANGE_REPORT.md`. Hai file này viết cho Java và Streamlit, nên tài liệu này chuyển chúng sang FastAPI và React.
> - Diff đang staged của `database/init.sql`, `database/trigger.sql`, `database/seed_demo.sql`.
> - Toàn bộ `backend-py/app`, `backend-py/tests` và `frontend-react/src`.

---

## 0. TÓM TẮT

### 0.1 Thay đổi ở CSDL (đã có sẵn trong `database/`)

| # | Thay đổi | Ảnh hưởng tới code |
|---|---|---|
| 1 | Cột `pt_profiles.certificate_urls JSON` đổi thành `certificate_url VARCHAR(500)` (1NF) | ORM, DTO request/response, handler đăng ký, service cập nhật hồ sơ |
| 2 | Bỏ `reviews.student_id` và `reviews.pt_id`, chỉ giữ `booking_id` (khóa ngoại `ON DELETE CASCADE`) (3NF) | Model `Review`, repository (query phải JOIN `bookings`), service tạo review, DTO `ReviewResponse` |
| 3 | 3 trigger tính rating giờ lấy `pt_id` qua `bookings`. Thêm view `v_pt_rating_statistics` | Không cần sửa code. Chỉ cần đối chiếu dữ liệu (tùy chọn, §2.10) |

### 0.2 Nguyên tắc tương thích ngược

- JSON trả về giữ đủ các key cũ:
  - review: `studentId`, `studentName`, `studentAvatarUrl`, `ptId`
  - hồ sơ PT: `certificateUrls`
- Thêm key mới `certificateUrl`. Hai key chứng chỉ luôn mang **cùng một giá trị chuỗi**.
- Request nhận được cả `certificateUrl` lẫn `certificateUrls`. `certificateUrls` có thể là chuỗi, chuỗi JSON `'["..."]'` hoặc mảng `["..."]`.

### 0.3 Thống kê thay đổi

| Phần | Sửa | Tạo mới |
|---|---|---|
| `backend-py/` | 10 file, cùng test | 1 file |
| `frontend-react/` | 7 file | 5 file: `lib/certificate.ts`, `components/StarRating.tsx`, `components/ReviewModal.tsx`, `components/ReviewList.tsx`, `components/PtProfileForm.tsx` |

### 0.4 Phát hiện quan trọng về React

`frontend-react` **hiện chưa có** các phần sau:
- form hồ sơ chuyên môn khi đăng ký PT
- tab sửa hồ sơ PT
- hiển thị chứng chỉ ở màn duyệt Admin
- giao diện gửi và xem đánh giá

Vì vậy phần React (§4) là **bổ sung tính năng để ngang bằng Streamlit** trên schema mới, không chỉ đổi tên trường.

---

## 1. HIỆN TRẠNG VÀ LƯU Ý TRƯỚC KHI SỬA

1. **`docker-compose.yml` vẫn build `./backend` (Java) và `./frontend` (Streamlit).**
   - `backend-py` và `frontend-react` đang chạy riêng. Vite proxy `/api` tới `http://localhost:8080` (`frontend-react/vite.config.ts`).
   - Khi test, chạy `backend-py` ở cổng 8080 và trỏ vào MySQL của compose (cổng host 3307).
2. **Cần tạo lại volume MySQL.** File trong `docker-entrypoint-initdb.d` chỉ chạy khi volume rỗng: `docker compose down -v && docker compose up -d mysql`.
   - `seed_demo.sql` **không** nằm trong initdb, nên phải nạp tay (§5.1).
   - Trong seed, bảng `bookings` được nạp trước `reviews`, nên trigger tính lại rating đúng.
3. **Hai file SQLite cũ** `backend-py/ptconnect.db` và `backend-py/test.db` mang schema cũ. Xóa đi, vì test đã dùng `sqlite:///:memory:` (`tests/conftest.py`).
4. **Test dùng SQLite với `Base.metadata.create_all`, nên không có trigger.** Test đơn vị không thấy `average_rating` thay đổi. Phần này kiểm ở bước tích hợp với MySQL (§5).
5. **Dữ liệu chứng chỉ cũ:**
   - Với cột JSON cũ, SQLAlchemy trả về `list`, nên API cũ có thể trả `certificateUrls: ["..."]` dạng **mảng**.
   - API mới trả **chuỗi**.
   - Phía React phải đọc phòng thủ được cả hai dạng (§4.2).

---

## 2. BACKEND `backend-py/` (FastAPI + SQLAlchemy 2)

### 2.1 `app/models/pt_profile.py`: chuẩn 1NF

**Sửa import:**
```python
# CŨ
from typing import TYPE_CHECKING, Any
from sqlalchemy import JSON, FetchedValue, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# MỚI
from typing import TYPE_CHECKING
from sqlalchemy import FetchedValue, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
```

**Sửa cột** (dòng 27):
```python
# CŨ
    certificate_urls: Mapped[Any | None] = mapped_column(JSON, nullable=True)

# MỚI
    certificate_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Bí danh tương thích ngược: code cũ đọc/ghi profile.certificate_urls vẫn chạy,
    # và PTProfile(certificate_urls=...) vẫn hợp lệ. Cả hai trỏ vào cùng cột certificate_url.
    certificate_urls = synonym("certificate_url")
```

> Dùng `synonym` thay vì `@property` vì `synonym` dùng được trong constructor và trong query (`PTProfile.certificate_urls == ...`).

### 2.2 `app/models/review.py`: chuẩn 3NF

Thay toàn bộ file:
```python
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import FetchedValue, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.pt_profile import PTProfile
    from app.models.user import User


class Review(Base):
    """Bảng reviews theo chuẩn 3NF: chỉ còn booking_id.
    Học viên và PT được suy ra qua booking (booking.student, booking.pt)."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(server_default=FetchedValue())

    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")

    # ---- Thuộc tính dẫn xuất (read-only), giữ API cũ của model cho code nội bộ ----
    @property
    def student(self) -> "User | None":
        return self.booking.student if self.booking is not None else None

    @property
    def student_id(self) -> int | None:
        return self.booking.student_id if self.booking is not None else None

    @property
    def pt(self) -> "PTProfile | None":
        return self.booking.pt if self.booking is not None else None

    @property
    def pt_id(self) -> int | None:
        return self.booking.pt_id if self.booking is not None else None
```

**Lưu ý:**
- **Không truyền** `student_id` hoặc `pt_id` vào `Review(...)` nữa, vì sẽ gây `TypeError: 'student_id' is an invalid keyword argument`.
- Không dùng hai thuộc tính này trong `.filter()`. Muốn lọc thì phải JOIN `Booking` (§2.3).

### 2.3 `app/repositories/review_repo.py`: query JOIN qua `bookings`

Thay toàn bộ file:
```python
from sqlalchemy.orm import Session, selectinload

from app.models.booking import Booking
from app.models.pt_profile import PTProfile
from app.models.review import Review


def _with_relations(query):
    # Nạp sẵn booking -> student và booking -> pt -> user để tránh N+1 khi map DTO
    return query.options(
        selectinload(Review.booking).selectinload(Booking.student),
        selectinload(Review.booking).selectinload(Booking.pt).selectinload(PTProfile.pt),
    )


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: int) -> Review | None:
        return _with_relations(self.db.query(Review)).filter(Review.id == review_id).first()

    def find_by_booking_id(self, booking_id: int) -> Review | None:
        return _with_relations(self.db.query(Review)).filter(Review.booking_id == booking_id).first()

    def exists_by_booking_id(self, booking_id: int) -> bool:
        return self.db.query(Review.id).filter(Review.booking_id == booking_id).first() is not None

    def find_by_pt_id(self, pt_id: int) -> list[Review]:
        # Tương đương JPA findByBookingPtIdOrderByCreatedAtDesc
        return (
            _with_relations(self.db.query(Review))
            .join(Review.booking)
            .filter(Booking.pt_id == pt_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .all()
        )

    def find_by_student_id(self, student_id: int) -> list[Review]:
        # Tương đương JPA findByBookingStudentIdOrderByCreatedAtDesc
        return (
            _with_relations(self.db.query(Review))
            .join(Review.booking)
            .filter(Booking.student_id == student_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .all()
        )

    def save(self, review: Review) -> Review:
        self.db.add(review)
        self.db.flush()
        return review
```

> `Review.id.desc()` là khóa phụ để thứ tự ổn định khi `created_at` trùng nhau (seed có nhiều review cùng giờ). Thứ tự chính theo `created_at` không đổi.

### 2.4 `app/services/review_service.py`: bỏ gán `student_id` và `pt_id`

Chỉ sửa khối tạo review (khoảng dòng 42–52):
```python
# CŨ
        review = Review(
            booking_id=booking.id,
            student_id=student.id,
            pt_id=booking.pt_id,
            rating=request.rating,
            comment=request.comment.strip() if request.comment else None,
        )

        saved = self.review_repo.save(review)
        self.db.commit()
        self.db.refresh(saved)
        return ReviewResponse.from_entity(saved)

# MỚI
        review = Review(
            booking=booking,  # gán quan hệ để DTO resolve được student/pt ngay, không cần query lại
            rating=request.rating,
            comment=request.comment.strip() if request.comment else None,
        )

        saved = self.review_repo.save(review)
        self.db.commit()
        # Trigger MySQL đã cập nhật pt_profiles.average_rating/total_reviews;
        # nạp lại review kèm quan hệ để trả về created_at thật và thông tin student/pt
        saved = self.review_repo.get_by_id(saved.id)
        return ReviewResponse.from_entity(saved)
```

**Giữ nguyên:**
- `get_reviews_by_pt_id`, `get_my_reviews`, `get_review_by_booking_id`
- các kiểm tra quyền, trạng thái COMPLETED và review trùng
- chuỗi thông báo tiếng Việt

**Tùy chọn:** thay `find_by_booking_id(booking.id) is not None` bằng `exists_by_booking_id(booking.id)` cho nhẹ hơn.

**Nếu cache phiên bị cũ:** khi một request khác đọc `PTProfile` ngay sau khi tạo review, gọi thêm `self.db.expire_all()` sau `commit()`. Với cấu hình hiện tại (mỗi request một session) thì không cần.

### 2.5 `app/schemas/responses/review.py`: DTO Adapter lấy dữ liệu qua booking

Thay `from_entity`:
```python
    @classmethod
    def from_entity(cls, review: Review | None) -> "ReviewResponse | None":
        if review is None:
            return None

        booking = review.booking
        student = booking.student if booking is not None else None
        pt_profile = booking.pt if booking is not None else None

        return cls(
            id=review.id,
            booking_id=booking.id if booking is not None else review.booking_id,
            student_id=student.id if student is not None else (booking.student_id if booking else None),
            student_name=student.full_name if student is not None else None,
            student_avatar_url=student.avatar_url if student is not None else None,
            pt_id=pt_profile.id if pt_profile is not None else (booking.pt_id if booking else None),
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )
```

Các field của class giữ nguyên: `id, bookingId, studentId, studentName, studentAvatarUrl, ptId, rating, comment, createdAt`. JSON không mất key nào.

**Tùy chọn (không phá tương thích):** thêm `pt_name: str | None = None`, gán từ `pt_profile.pt.full_name` nếu có, để React hiển thị "Đánh giá cho HLV X". Thêm key mới là an toàn vì client cũ bỏ qua key thừa.

### 2.6 File mới `app/schemas/certificate.py`: hàm làm sạch URL dùng chung

```python
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
```

> Hàm này chắc chắn hơn bản Java (`substring(2, len-2)`): nó xử lý được mảng nhiều phần tử, khoảng trắng và mảng rỗng.

### 2.7 DTO request: nhận cả `certificateUrl` và `certificateUrls`

#### 2.7.1 `app/schemas/requests/auth.py` (`RegisterRequest`)

```python
# thêm import
from typing import Any
from pydantic import field_validator, model_validator
from app.schemas.certificate import MAX_CERT_URL_LEN, clean_certificate_url

class RegisterRequest(CamelModel):
    ...
    location_pricing_note: str | None = None
    # CŨ: certificate_urls: str | None = None
    certificate_url: str | None = None          # key mới: "certificateUrl"
    certificate_urls: Any | None = None         # key cũ: "certificateUrls" (chuỗi, chuỗi JSON hoặc mảng)

    @model_validator(mode="after")
    def _normalize_certificate(self) -> "RegisterRequest":
        cleaned = clean_certificate_url(self.certificate_url) or clean_certificate_url(self.certificate_urls)
        if cleaned is not None and len(cleaned) > MAX_CERT_URL_LEN:
            raise ValueError("URL chứng chỉ không được vượt quá 500 ký tự")
        self.certificate_url = cleaned
        self.certificate_urls = cleaned
        return self

    @property
    def clean_certificate_url(self) -> str | None:
        return self.certificate_url
```

**Lưu ý:**
- `certificateUrl` được ưu tiên hơn `certificateUrls`, giống `getCleanCertificateUrl()` của bản Java.
- Lỗi do `model_validator` sinh ra có `loc` rỗng. Hãy chạy thử để xem `core/handlers.py` trả message dạng `"certificateUrl: URL chứng chỉ không được vượt quá 500 ký tự"` hay chỉ phần message, rồi viết test theo đúng kết quả đó.
- Nếu handler cần tên field, chuyển kiểm tra độ dài vào `field_validator("certificate_url", "certificate_urls")` với `mode="after"`.

#### 2.7.2 `app/schemas/requests/pt.py` (`UpdatePTProfileRequest`)

Làm y hệt §2.7.1:
- thay `certificate_urls: str | None = None` bằng cặp field mới
- thêm `_normalize_certificate`
- thêm property `clean_certificate_url`

### 2.8 Service và handler ghi dữ liệu

#### 2.8.1 `app/services/registration/pt_handler.py` (dòng 37)
```python
# CŨ
            certificate_urls=request.certificate_urls,
# MỚI
            certificate_url=request.clean_certificate_url,
```

#### 2.8.2 `app/services/pt_profile_service.py` (`update_profile`, dòng 83–84)
```python
# CŨ
        if request.certificate_urls is not None:
            profile.certificate_urls = request.certificate_urls
# MỚI
        if request.clean_certificate_url is not None:
            profile.certificate_url = request.clean_certificate_url
```

> **Hành vi giữ nguyên như bản Java:** gửi rỗng hoặc không gửi thì **không xóa** chứng chỉ cũ.
>
> Nếu team muốn cho phép xóa, cần quyết định riêng: dùng `"certificateUrl" in request.model_fields_set` để phân biệt "không gửi" với "gửi rỗng".

### 2.9 DTO response: trả cả `certificateUrl` và bí danh `certificateUrls`

Trong file `app/schemas/responses/pt.py`, sửa 2 class.

**`PTProfileResponse`** (khoảng dòng 22 và 64):
```python
# field — CŨ
    certificate_urls: Any | None = None
# field — MỚI
    certificate_url: str | None = None
    certificate_urls: str | None = None   # alias tương thích ngược, luôn bằng certificate_url

# from_entity — CŨ
            certificate_urls=profile.certificate_urls,
# from_entity — MỚI
            certificate_url=clean_certificate_url(profile.certificate_url),
            certificate_urls=clean_certificate_url(profile.certificate_url),
```

**`PendingPTResponse`** (khoảng dòng 210 và 246): sửa giống hệt.

**Import:** thêm `from app.schemas.certificate import clean_certificate_url`. Bỏ `Any` khỏi import nếu không còn dùng.

> Gọi `clean_certificate_url` cả khi đọc, để phòng trường hợp DB còn sót dữ liệu dạng `'["..."]'` (ví dụ ai đó chạy `ALTER` thay vì nạp lại seed).

**`PTPublicDTO`** (danh sách và chi tiết PT công khai): bản Java không trả chứng chỉ, nên **mặc định giữ nguyên**. Nếu team muốn trang chi tiết PT phía học viên hiện link chứng chỉ, thêm 2 field như trên. Đây là key mới nên vẫn an toàn.

**Không cần sửa:**
- `average_rating` và `total_reviews` vẫn đọc từ `pt_profiles` (trigger cập nhật).
- `PTProfileResponse` đã ép giá trị `null` về `0.0` và `0`.

### 2.10 (Tùy chọn) Đối chiếu view `v_pt_rating_statistics`

**Không map view vào ORM.** Nếu map, `Base.metadata.create_all` trên SQLite sẽ tạo ra một bảng giả trùng tên. Nếu cần kiểm tra trigger, thêm hàm vào `app/repositories/pt_profile_repo.py`:
```python
from sqlalchemy import text

    def find_rating_mismatches(self) -> list[dict]:
        """Trả các PT có rating lưu (trigger) lệch với rating tính từ view 3NF. Chỉ dùng cho MySQL."""
        rows = self.db.execute(text("""
            SELECT p.id, p.average_rating, p.total_reviews,
                   v.calculated_average_rating, v.calculated_total_reviews
            FROM pt_profiles p
            JOIN v_pt_rating_statistics v ON v.pt_profile_id = p.id
            WHERE p.average_rating <> v.calculated_average_rating
               OR p.total_reviews  <> v.calculated_total_reviews
        """)).mappings().all()
        return [dict(r) for r in rows]
```

Dùng hàm này trong test tích hợp (§5.2). **Không thêm endpoint mới.**

### 2.11 Kết nối CSDL và seed

| Hạng mục | Cần làm |
|---|---|
| `app/db/session.py`, `app/core/config.py` | **Không đổi** (`mysql+pymysql://…/ptconnect`) |
| Seed | `backend-py` không có code seed riêng; seed lấy từ `database/seed_demo.sql` (đã cập nhật). Không cần sửa. |
| `backend-py/ptconnect.db`, `backend-py/test.db` | **Xóa** (schema cũ, không dùng). Thêm `*.db` vào `backend-py/.gitignore` nếu chưa có. |
| `backend-py/uploads/contracts/*.pdf` | Không liên quan, giữ nguyên |

### 2.12 Test backend cần sửa và thêm

**Sửa test cũ** (`tests/unit/test_models.py`, `tests/unit/test_booking_wallet_enrollment.py`):
- Grep và bỏ mọi chỗ tạo `Review(student_id=..., pt_id=...)`.
- Bỏ chỗ tạo `PTProfile(certificate_urls=[...])` với giá trị kiểu list. `PTProfile(certificate_urls="...")` dạng chuỗi vẫn chạy nhờ `synonym`.
- Trong test luồng tại `test_booking_wallet_enrollment.py:149-160`, thêm:
```python
    assert review.booking_id == booking.id
    assert review.student_id == booking.student_id          # resolve qua booking
    assert review.student_name == "<tên học viên trong fixture>"
    assert review.pt_id == booking.pt_id
```

**File mới `tests/unit/test_certificate_and_review_3nf.py`:**
```python
import pytest
from app.schemas.certificate import clean_certificate_url
from app.schemas.requests.auth import RegisterRequest
from app.schemas.requests.pt import UpdatePTProfileRequest


@pytest.mark.parametrize("raw,expected", [
    ("https://a/c.pdf", "https://a/c.pdf"),
    ('["https://a/c.pdf"]', "https://a/c.pdf"),
    (["https://a/1.pdf", "https://a/2.pdf"], "https://a/1.pdf"),
    ("  https://a/c.pdf  ", "https://a/c.pdf"),
    ("", None), ("   ", None), (None, None), ([], None), ("[]", None),
])
def test_clean_certificate_url(raw, expected):
    assert clean_certificate_url(raw) == expected


def _reg(**kw):
    base = dict(fullName="PT A", email="pt@a.vn", password="123456", phone="0900", role="PT")
    return RegisterRequest(**base, **kw)


def test_register_accepts_new_key():
    assert _reg(certificateUrl="https://x/1.pdf").clean_certificate_url == "https://x/1.pdf"


def test_register_accepts_legacy_json_string_key():
    assert _reg(certificateUrls='["https://x/1.pdf"]').clean_certificate_url == "https://x/1.pdf"


def test_new_key_wins_over_legacy_key():
    r = _reg(certificateUrl="https://new", certificateUrls='["https://old"]')
    assert r.clean_certificate_url == "https://new"


def test_update_profile_accepts_legacy_array():
    r = UpdatePTProfileRequest(availableLocations="HN", certificateUrls=["https://x/1.pdf"])
    assert r.clean_certificate_url == "https://x/1.pdf"


def test_pt_profile_response_returns_both_keys(db_session):
    # Tạo PT + profile với certificate_url, gọi PTProfileResponse.from_entity(...).model_dump(by_alias=True)
    # assert dump["certificateUrl"] == dump["certificateUrls"] == "https://x/1.pdf"
    ...


def test_reviews_by_pt_resolve_through_booking(db_session):
    # Tạo booking COMPLETED (student S, PT P) + Review(booking=...) rồi gọi
    # ReviewRepository(db_session).find_by_pt_id(P.id) và find_by_student_id(S.id)
    # assert len == 1, và ReviewResponse.from_entity(...) có studentId/studentName/ptId đúng
    ...
```

Hai test có `...` cần dựng fixture bằng các helper sẵn có trong `tests/unit/test_booking_wallet_enrollment.py`.

**Lệnh kiểm tra:**
```bash
cd backend-py && rm -f ptconnect.db test.db && ruff check app tests && pytest -q
```

---

## 3. CHECKLIST BACKEND THEO FILE

| # | File | Thay đổi | Xong |
|---|---|---|---|
| B1 | `app/models/pt_profile.py` | Cột `certificate_url String(500)` + `synonym("certificate_url")`; bỏ import `JSON`, `Any` | ☐ |
| B2 | `app/models/review.py` | Bỏ cột và quan hệ `student_id`, `pt_id`; khóa ngoại `ondelete=CASCADE`; thêm 4 `@property` | ☐ |
| B3 | `app/repositories/review_repo.py` | `find_by_pt_id` và `find_by_student_id` JOIN `Booking`; eager load `booking.student`, `booking.pt.pt`; thêm `exists_by_booking_id` | ☐ |
| B4 | `app/services/review_service.py` | `Review(booking=…, rating, comment)`; nạp lại sau commit | ☐ |
| B5 | `app/schemas/responses/review.py` | `from_entity` lấy dữ liệu qua `booking` | ☐ |
| B6 | `app/schemas/certificate.py` (mới) | `clean_certificate_url`, `MAX_CERT_URL_LEN` | ☐ |
| B7 | `app/schemas/requests/auth.py` | `certificate_url` + `certificate_urls: Any`, `model_validator`, property `clean_certificate_url` | ☐ |
| B8 | `app/schemas/requests/pt.py` | Như B7, cho `UpdatePTProfileRequest` | ☐ |
| B9 | `app/services/registration/pt_handler.py` | `certificate_url=request.clean_certificate_url` | ☐ |
| B10 | `app/services/pt_profile_service.py` | Ghi `profile.certificate_url` khi có giá trị sạch | ☐ |
| B11 | `app/schemas/responses/pt.py` | `PTProfileResponse`, `PendingPTResponse` trả cả `certificateUrl` và `certificateUrls` (chuỗi) | ☐ |
| B12 | `app/repositories/pt_profile_repo.py` | (Tùy chọn) `find_rating_mismatches()` | ☐ |
| B13 | `tests/…` | Sửa test cũ; thêm `test_certificate_and_review_3nf.py`; xóa `*.db` | ☐ |

**Không cần sửa:**
- `app/api/v1/routes/*.py`: path, method, status code và message giữ nguyên.
- `models/booking.py`: quan hệ `review` vẫn đúng.
- `booking_repo.py`: `selectinload(Booking.review)` vẫn đúng.
- `admin_pt_service.py`: dùng `PendingPTResponse`, đã sửa ở B11.
- `db/session.py`, `core/*`.

---

## 4. FRONTEND `frontend-react/` (React 18 + Vite + TS)

**Client** (`src/lib/axios.ts`):
- Interceptor tự bóc trường `data` khỏi envelope và ném `Error(message)` khi có lỗi.
- Với `GET /reviews/booking/{id}` khi chưa có review, interceptor trả `null`. Đây là hành vi đúng.

### 4.1 `src/types/api.ts`

```ts
export interface PtProfile {
  ...
  locationPricingNote?: string;
  // CŨ: certificateUrls?: string[];
  certificateUrl?: string | null;                 // trường chuẩn 1NF
  certificateUrls?: string | string[] | null;     // alias cũ: có thể là chuỗi, '["..."]' hoặc mảng (dữ liệu cũ)
  averageRating: number;
  totalReviews: number;
  ...
  userStatus?: UserStatus;
  createdAt?: string;
}

export interface Review {
  id: number;
  bookingId: number;
  studentId?: number | null;
  studentName?: string | null;
  studentAvatarUrl?: string | null;
  ptId?: number | null;
  ptName?: string | null;        // chỉ có nếu backend bật tùy chọn ở §2.5
  rating: number;                // 1..5
  comment?: string | null;
  createdAt?: string | null;
}

export interface CreateReviewPayload {
  bookingId: number;
  rating: number;
  comment?: string;
}

export interface UpdatePtProfilePayload {
  bio?: string;
  experienceYears?: number;
  availableLocations: string;    // bắt buộc (backend báo 400 nếu rỗng)
  locationPricingNote?: string;
  certificateUrl?: string;
}
```

Bổ sung vào `Booking` nếu chưa có (BookingTable cần):
```ts
  sessionFee?: number;
  trainingLocation?: string;
  cancellationReason?: string;
  cancelledByRole?: string;
```

### 4.2 File mới `src/lib/certificate.ts`: đọc chứng chỉ phòng thủ (bản React của `clean_certificate_url`)

```ts
type CertSource = { certificateUrl?: string | null; certificateUrls?: string | string[] | null };

const cleanOne = (raw: unknown): string | null => {
  if (raw == null) return null;
  if (Array.isArray(raw)) {
    for (const item of raw) {
      const c = cleanOne(item);
      if (c) return c;
    }
    return null;
  }
  let s = String(raw).trim();
  if (!s) return null;
  if (s.startsWith('[') && s.endsWith(']')) {
    try {
      return cleanOne(JSON.parse(s));
    } catch {
      s = s.slice(1, -1).trim().replace(/^["']|["']$/g, '').trim();
      return s || null;
    }
  }
  return s.replace(/^"|"$/g, '').trim() || null;
};

/** Ưu tiên certificateUrl, fallback certificateUrls (chuỗi / chuỗi JSON / mảng). */
export const resolveCertificateUrl = (src?: CertSource | null): string | null =>
  src ? cleanOne(src.certificateUrl) ?? cleanOne(src.certificateUrls) : null;

export const isHttpUrl = (s?: string | null): boolean => !!s && /^https?:\/\//i.test(s.trim());

export const CERT_URL_MAX = 500;
```

### 4.3 File mới `src/components/StarRating.tsx`

```tsx
import React from 'react';
import { Star } from 'lucide-react';

interface Props {
  value: number;
  onChange?: (v: number) => void;   // không truyền = chế độ chỉ đọc
  size?: number;
}

export const StarRating: React.FC<Props> = ({ value, onChange, size = 18 }) => (
  <div className="inline-flex items-center gap-0.5" role={onChange ? 'radiogroup' : undefined}>
    {[1, 2, 3, 4, 5].map((n) => (
      <button
        key={n}
        type="button"
        disabled={!onChange}
        onClick={() => onChange?.(n)}
        aria-label={`${n} sao`}
        className={onChange ? 'cursor-pointer' : 'cursor-default'}
      >
        <Star
          width={size}
          height={size}
          className={n <= value ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}
        />
      </button>
    ))}
  </div>
);
```

> Kiểm tra `lucide-react` có trong `package.json`. Các page hiện đã import icon từ thư viện này, nên nhiều khả năng đã có.

### 4.4 File mới `src/components/ReviewModal.tsx`: học viên gửi đánh giá

```tsx
import React, { useState } from 'react';
import api from '../lib/axios';
import { Booking, CreateReviewPayload, Review } from '../types/api';
import { StarRating } from './StarRating';

interface Props {
  booking: Booking;
  onClose: () => void;
  onSubmitted: (review: Review) => void;
}

export const ReviewModal: React.FC<Props> = ({ booking, onClose, onSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload: CreateReviewPayload = {
        bookingId: booking.id,
        rating,
        comment: comment.trim() || undefined,
      };
      const created = (await api.post('/reviews', payload)) as unknown as Review;
      onSubmitted(created);
    } catch (e: any) {
      // Ví dụ: "Ca tập này đã được đánh giá trước đó..." / "Chỉ có thể đánh giá ca tập đã hoàn thành (COMPLETED)"
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        <h4 className="text-lg font-bold text-slate-900">Đánh giá ca tập #{booking.id}</h4>
        <p className="text-xs text-slate-500 mt-1">HLV: {booking.ptName ?? '—'}</p>
        <div className="my-4">
          <StarRating value={rating} onChange={setRating} size={28} />
        </div>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={4}
          placeholder="Chia sẻ cảm nhận của bạn về buổi tập..."
          className="w-full p-3 border border-slate-300 rounded-xl text-sm focus:ring-1 focus:ring-[#FF4B4B] outline-none"
        />
        {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        <div className="flex gap-2 mt-4">
          <button onClick={onClose} className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600">
            Hủy
          </button>
          <button
            onClick={submit}
            disabled={submitting}
            className="flex-1 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-60 text-white rounded-lg text-sm font-semibold"
          >
            {submitting ? 'Đang gửi...' : 'Gửi đánh giá'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

### 4.5 File mới `src/components/ReviewList.tsx`: xem đánh giá của một PT

```tsx
import React, { useEffect, useState } from 'react';
import api from '../lib/axios';
import { getAvatarUrl } from '../lib/avatar';
import { Review } from '../types/api';
import { StarRating } from './StarRating';

interface Props {
  ptProfileId: number;   // = pt_profiles.id (KHÔNG phải users.id)
  reloadKey?: number;    // tăng lên để buộc tải lại sau khi có review mới
}

export const ReviewList: React.FC<Props> = ({ ptProfileId, reloadKey = 0 }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .get(`/reviews/pt/${ptProfileId}`)
      .then((data: any) => { if (!cancelled) setReviews(Array.isArray(data) ? data : []); })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [ptProfileId, reloadKey]);

  if (loading) return <p className="text-sm text-slate-500">Đang tải đánh giá...</p>;
  if (error) return <p className="text-sm text-red-600">Không tải được đánh giá: {error}</p>;
  if (reviews.length === 0) return <p className="text-sm text-slate-500">Huấn luyện viên chưa có đánh giá nào.</p>;

  return (
    <ul className="space-y-3">
      {reviews.map((r) => (
        <li key={r.id} className="bg-white p-4 rounded-xl border border-slate-200 flex gap-3">
          <img
            src={getAvatarUrl(r.studentName ?? 'Học viên', r.studentAvatarUrl ?? undefined)}
            alt={r.studentName ?? 'Học viên'}
            className="w-10 h-10 rounded-full object-cover border border-slate-200"
          />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900">{r.studentName ?? 'Học viên ẩn danh'}</span>
              <span className="text-xs text-slate-400">{r.createdAt ? r.createdAt.slice(0, 10) : ''}</span>
            </div>
            <StarRating value={r.rating} size={14} />
            {r.comment && <p className="text-sm text-slate-600 mt-1">{r.comment}</p>}
          </div>
        </li>
      ))}
    </ul>
  );
};
```

> Kiểm tra chữ ký `getAvatarUrl(name, url?)` trong `src/lib/avatar.ts`. Các page hiện gọi `getAvatarUrl(pt.fullName, pt.avatarUrl)`, nên nhiều khả năng khớp.

### 4.6 File mới `src/components/PtProfileForm.tsx`: PT xem và sửa hồ sơ chuyên môn

```tsx
import React, { useEffect, useState } from 'react';
import api from '../lib/axios';
import { PtProfile, UpdatePtProfilePayload } from '../types/api';
import { CERT_URL_MAX, isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
import { ReviewList } from './ReviewList';

interface Props {
  onSaved?: (msg: string) => void;
}

export const PtProfileForm: React.FC<Props> = ({ onSaved }) => {
  const [profile, setProfile] = useState<PtProfile | null>(null);
  const [form, setForm] = useState<UpdatePtProfilePayload>({ availableLocations: '' });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const p = (await api.get('/pt/profile')) as unknown as PtProfile;
    setProfile(p);
    setForm({
      bio: p.bio ?? '',
      experienceYears: p.experienceYears ?? 0,
      availableLocations: p.availableLocations ?? '',
      locationPricingNote: p.locationPricingNote ?? '',
      certificateUrl: resolveCertificateUrl(p) ?? '',
    });
  };

  useEffect(() => { load().catch((e) => setError(e.message)); }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!form.availableLocations.trim()) return setError('Địa điểm nhận dạy không được để trống!');
    if ((form.experienceYears ?? 0) < 0) return setError('Số năm kinh nghiệm phải lớn hơn hoặc bằng 0');
    const cert = (form.certificateUrl ?? '').trim();
    if (cert && !isHttpUrl(cert)) return setError('Đường dẫn chứng chỉ phải bắt đầu bằng http:// hoặc https://');
    if (cert.length > CERT_URL_MAX) return setError('URL chứng chỉ không được vượt quá 500 ký tự');

    setSaving(true);
    try {
      await api.put('/pt/profile', {
        bio: form.bio?.trim() || undefined,
        experienceYears: Number(form.experienceYears ?? 0),
        availableLocations: form.availableLocations.trim(),
        locationPricingNote: form.locationPricingNote?.trim() || undefined,
        certificateUrl: cert || undefined,   // key mới, chuỗi đơn (1NF)
      });
      await load();
      onSaved?.('Đã cập nhật hồ sơ chuyên môn!');
    } catch (err: any) {
      setError(`Lỗi cập nhật hồ sơ: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!profile) return <p className="text-sm text-slate-500">{error ?? 'Đang tải hồ sơ...'}</p>;

  const input = 'w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm outline-none focus:border-[#FF4B4B]';
  const certNow = resolveCertificateUrl(profile);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <form onSubmit={save} className="bg-white p-6 rounded-xl border border-slate-200 space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Hồ Sơ Chuyên Môn</h3>
        <p className="text-xs text-slate-500">
          Trạng thái xét duyệt: <b>{profile.verificationStatus}</b> • Đánh giá: {(profile.averageRating ?? 0).toFixed(1)}/5 ({profile.totalReviews ?? 0} lượt)
        </p>
        <textarea
          className="w-full p-3 border border-slate-300 rounded-lg text-sm"
          rows={3}
          placeholder="Giới thiệu bản thân"
          value={form.bio ?? ''}
          onChange={(e) => setForm({ ...form, bio: e.target.value })}
        />
        <input
          className={input}
          type="number"
          min={0}
          max={50}
          value={form.experienceYears ?? 0}
          onChange={(e) => setForm({ ...form, experienceYears: Number(e.target.value) })}
        />
        <input
          className={input}
          placeholder="Địa điểm nhận dạy (phân tách bằng ;)"
          value={form.availableLocations}
          onChange={(e) => setForm({ ...form, availableLocations: e.target.value })}
        />
        <input
          className={input}
          placeholder="Ghi chú giá theo địa điểm"
          value={form.locationPricingNote ?? ''}
          onChange={(e) => setForm({ ...form, locationPricingNote: e.target.value })}
        />
        <input
          className={input}
          type="url"
          maxLength={CERT_URL_MAX}
          placeholder="https://storage.ptconnect.vn/certs/cert_nasam.jpg"
          value={form.certificateUrl ?? ''}
          onChange={(e) => setForm({ ...form, certificateUrl: e.target.value })}
        />
        {certNow && isHttpUrl(certNow) && (
          <a href={certNow} target="_blank" rel="noreferrer" className="text-xs text-blue-600 underline">
            Xem chứng chỉ hiện tại
          </a>
        )}
        {error && <p className="text-xs text-red-600">{error}</p>}
        <button
          disabled={saving}
          className="px-5 py-2 bg-[#FF4B4B] text-white rounded-lg text-sm font-semibold disabled:opacity-60"
        >
          {saving ? 'Đang lưu...' : 'Lưu hồ sơ'}
        </button>
      </form>
      <div>
        <h3 className="text-lg font-bold text-slate-900 mb-3">Đánh Giá Từ Học Viên</h3>
        <ReviewList ptProfileId={profile.id} />
      </div>
    </div>
  );
};
```

> **Xóa chứng chỉ:** ô rỗng được gửi thành `undefined`, nên backend giữ link cũ (§2.8.2), giống hành vi Java. Nếu muốn có nút "Xóa chứng chỉ" thì phải quyết định thêm ở backend.

### 4.7 `src/pages/LoginPage.tsx`: form đăng ký PT gửi `certificateUrl`

**State mới** (sau dòng 25):
```tsx
  const [regBio, setRegBio] = useState('');
  const [regExperience, setRegExperience] = useState<number>(0);
  const [regLocations, setRegLocations] = useState('');
  const [regPricingNote, setRegPricingNote] = useState('');
  const [regCertificateUrl, setRegCertificateUrl] = useState('');
```

**`handleRegister`** (dòng 60–66), thay phần payload:
```tsx
      const cert = regCertificateUrl.trim();
      if (regRole === 'PT' && cert && !/^https?:\/\//i.test(cert)) {
        setError('Đường dẫn chứng chỉ phải bắt đầu bằng http:// hoặc https://');
        setLoading(false);
        return;
      }
      const payload: Record<string, unknown> = {
        fullName: regFullName.trim(),
        email: regEmail.trim(),
        phone: regPhone.trim(),
        password: regPassword,
        role: regRole,
      };
      if (regRole === 'PT') {
        Object.assign(payload, {
          bio: regBio.trim() || undefined,
          experienceYears: Number(regExperience) || 0,
          availableLocations: regLocations.trim() || undefined,   // rỗng -> backend gán "Chưa cập nhật địa điểm"
          locationPricingNote: regPricingNote.trim() || undefined,
          certificateUrl: cert || undefined,                      // 1NF: chuỗi đơn, KHÔNG bọc JSON.stringify([...])
        });
      }
      await api.post('/auth/register', payload);
```

**JSX:** đặt ngay sau khối chọn vai trò (sau dòng ~252); khối này chỉ hiện khi chọn PT:
```tsx
              {regRole === 'PT' && (
                <div className="space-y-3 p-3 rounded-lg border border-amber-200 bg-amber-50/40">
                  <p className="text-xs font-semibold text-amber-800">
                    Hồ sơ chuyên môn HLV (sẽ được Admin xét duyệt)
                  </p>
                  <textarea
                    rows={2}
                    value={regBio}
                    onChange={(e) => setRegBio(e.target.value)}
                    placeholder="Giới thiệu ngắn"
                    className="w-full p-2.5 bg-white border border-slate-300 rounded-lg text-sm"
                  />
                  <input
                    type="number"
                    min={0}
                    max={50}
                    value={regExperience}
                    onChange={(e) => setRegExperience(Number(e.target.value))}
                    placeholder="Số năm kinh nghiệm"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm"
                  />
                  <input
                    value={regLocations}
                    onChange={(e) => setRegLocations(e.target.value)}
                    placeholder="Khu vực nhận dạy (VD: Cầu Giấy; Đống Đa)"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm"
                  />
                  <input
                    value={regPricingNote}
                    onChange={(e) => setRegPricingNote(e.target.value)}
                    placeholder="Ghi chú giá theo địa điểm"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm"
                  />
                  <input
                    type="url"
                    maxLength={500}
                    value={regCertificateUrl}
                    onChange={(e) => setRegCertificateUrl(e.target.value)}
                    placeholder="Link chứng chỉ hành nghề (https://...)"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              )}
```

> Để giao diện đồng bộ, copy nguyên `className` dài của ô "Họ và tên" vào các input mới.

### 4.8 `src/pages/PtPage.tsx`: tab "Hồ sơ" (tab 5)

**Import:**
```tsx
import { PtProfileForm } from '../components/PtProfileForm';
```

**Thay khối `activeTab === 5`** (dòng ~375–383):
```tsx
        {/* TAB 5: HỒ SƠ */}
        {activeTab === 5 && (
          <div className="space-y-6">
            <PtProfileForm onSaved={showToast} />
            <AvatarUploader
              currentUrl={user.avatarUrl}
              onUpload={async (url) => {
                await api.put('/users/avatar', { avatarUrl: url });   // SỬA: backend chỉ có PUT /users/avatar
                showToast('Đã lưu ảnh đại diện!');
              }}
            />
          </div>
        )}
```

### 4.9 `src/pages/AdminPage.tsx`: duyệt hồ sơ PT, hiển thị chứng chỉ

**Import:**
```tsx
import { isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
```

**Trong card PT chờ duyệt**, ngay sau khối "Khu vực / Kinh nghiệm" (dòng ~194):
```tsx
                      {pt.locationPricingNote && (
                        <div className="text-xs text-slate-500 mt-1"><b>Ghi chú giá:</b> {pt.locationPricingNote}</div>
                      )}
                      {(() => {
                        const cert = resolveCertificateUrl(pt);
                        return (
                          <div className="text-xs text-slate-600 mt-2">
                            <b>Chứng chỉ / Bằng cấp:</b>{' '}
                            {cert ? (
                              isHttpUrl(cert) ? (
                                <a href={cert} target="_blank" rel="noreferrer" className="text-blue-600 underline break-all">{cert}</a>
                              ) : (
                                <code className="bg-slate-100 px-1 rounded break-all">{cert}</code>
                              )
                            ) : (
                              <span className="italic text-slate-400">Chưa cập nhật</span>
                            )}
                          </div>
                        );
                      })()}
```

`handleRejectPt` đang gửi body `{ reason }`. Backend bỏ qua body này nên không lỗi; có thể giữ nguyên hoặc bỏ body cho gọn.

### 4.10 `src/pages/StudentPage.tsx`: chi tiết PT, gửi và xem đánh giá

**Import và state:**
```tsx
import { ReviewList } from '../components/ReviewList';
import { ReviewModal } from '../components/ReviewModal';
import { Booking, Review } from '../types/api';   // gộp vào import types sẵn có

  const [reviewBooking, setReviewBooking] = useState<Booking | null>(null);
  const [reviewedBookingIds, setReviewedBookingIds] = useState<Set<number>>(new Set());
  const [reviewReloadKey, setReviewReloadKey] = useState(0);
```

**Tải danh sách ca đã đánh giá.** Chỉ cần 1 request, không gọi `/reviews/booking/{id}` cho từng ca. Gọi hàm này cùng chỗ với `loadBookings()` (khoảng dòng 100):
```tsx
  const loadMyReviews = async () => {
    try {
      const data: any = await api.get('/reviews/my');
      setReviewedBookingIds(new Set((Array.isArray(data) ? data : []).map((r: Review) => r.bookingId)));
    } catch {
      setReviewedBookingIds(new Set());
    }
  };
```

**Tab 1, chi tiết PT** (dòng 361): chống `null` và thêm danh sách đánh giá:
```tsx
                  <span><b>Đánh giá:</b> {(selectedPt.averageRating ?? 0).toFixed(1)}/5 ⭐ ({selectedPt.totalReviews ?? 0} lượt)</span>
```

Đặt sau khối "Các Khóa Học Huấn Luyện Cố Định":
```tsx
            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-4">Đánh Giá Từ Học Viên</h4>
              <ReviewList ptProfileId={selectedPt.id} reloadKey={reviewReloadKey} />
            </div>
```

**Tab 3, lịch tập** (khoảng dòng 418), truyền thêm prop cho `BookingTable`:
```tsx
            <BookingTable
              ...props hiện có...
              reviewedBookingIds={reviewedBookingIds}
              onReview={(b) => setReviewBooking(b)}
            />
```

**Modal**, đặt cuối component, cạnh các modal khác:
```tsx
      {reviewBooking && (
        <ReviewModal
          booking={reviewBooking}
          onClose={() => setReviewBooking(null)}
          onSubmitted={() => {
            setReviewBooking(null);
            setReviewedBookingIds((prev) => new Set(prev).add(reviewBooking.id));
            setReviewReloadKey((k) => k + 1);
            loadPts();   // tên hàm tải danh sách PT thực tế (dòng ~66): averageRating/totalReviews do trigger cập nhật
            showToast?.('Gửi đánh giá thành công! Cảm ơn bạn đã phản hồi.');
          }}
        />
      )}
```

**Lưu ý:**
- **Tên hàm tải PT và hàm toast:** `loadPts` và `showToast` là tên giả định. Đổi theo tên thực tế trong trang. Nếu trang chưa có hàm toast, dùng cơ chế toast sẵn có hoặc `alert`.
- **`selectedPt.id` là `pt_profiles.id`.** Đây đúng là id mà `GET /reviews/pt/{ptId}` cần, vì backend lọc theo `booking.pt_id`, tức `pt_profiles.id`.

### 4.11 `src/components/BookingTable.tsx`: nút "Đánh giá" cho ca COMPLETED

**Props:**
```tsx
interface BookingTableProps {
  ...
  onReview?: (booking: Booking) => void;
  reviewedBookingIds?: Set<number>;
}
// thêm vào destructuring: onReview, reviewedBookingIds,
```

**Trong cột thao tác**, cạnh các khối `b.status === 'CONFIRMED'` và `'PENDING'` (dòng ~120–160):
```tsx
                              {b.status === 'COMPLETED' && onReview && (
                                reviewedBookingIds?.has(b.id) ? (
                                  <span className="text-xs text-emerald-700 font-semibold">✓ Đã đánh giá</span>
                                ) : (
                                  <button
                                    onClick={() => onReview(b)}
                                    className="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-white rounded-md text-xs font-semibold"
                                  >
                                    ★ Đánh giá
                                  </button>
                                )
                              )}
```

Trang PT không truyền `onReview`, nên nút không hiện ở phía PT.

### 4.12 `src/components/PtCard.tsx`: danh sách PT

Không bắt buộc sửa theo schema. Tuy vậy dòng 48 đang hiện `'5.0'` khi `averageRating` bằng 0, tức PT chưa có đánh giá nào lại hiện 5 sao. Sau chuẩn hóa, seed để rating 0.0 cho tới khi trigger chạy, nên lỗi này dễ lộ ra hơn. **Nên sửa:**
```tsx
            <span>{pt.totalReviews ? (pt.averageRating ?? 0).toFixed(1) : 'Mới'}/5</span>
```

> Nếu sửa thì chữ "/5" cạnh chữ "Mới" bị thừa. Nên tách hiển thị thành hai trường hợp.

### 4.13 Checklist frontend

| # | File | Thay đổi | Xong |
|---|---|---|---|
| F1 | `src/types/api.ts` | `certificateUrl`, `certificateUrls: string \| string[] \| null`; thêm `Review`, `CreateReviewPayload`, `UpdatePtProfilePayload`; bổ sung field cho `Booking` | ☐ |
| F2 | `src/lib/certificate.ts` (mới) | `resolveCertificateUrl`, `isHttpUrl`, `CERT_URL_MAX` | ☐ |
| F3 | `src/components/StarRating.tsx` (mới) | Hiển thị và chọn sao | ☐ |
| F4 | `src/components/ReviewModal.tsx` (mới) | `POST /reviews` | ☐ |
| F5 | `src/components/ReviewList.tsx` (mới) | `GET /reviews/pt/{ptProfileId}` | ☐ |
| F6 | `src/components/PtProfileForm.tsx` (mới) | `GET` và `PUT /pt/profile` với `certificateUrl`; kèm `ReviewList` | ☐ |
| F7 | `src/pages/LoginPage.tsx` | Thêm field hồ sơ PT khi đăng ký; gửi `certificateUrl` | ☐ |
| F8 | `src/pages/PtPage.tsx` | Tab 5 dùng `PtProfileForm`; sửa path avatar thành `/users/avatar` | ☐ |
| F9 | `src/pages/AdminPage.tsx` | Hiện link chứng chỉ và ghi chú giá trên card chờ duyệt | ☐ |
| F10 | `src/pages/StudentPage.tsx` | `ReviewList` ở chi tiết PT; `ReviewModal`; tải `/reviews/my`; chống `null` cho rating | ☐ |
| F11 | `src/components/BookingTable.tsx` | Prop `onReview` và `reviewedBookingIds`; nút "Đánh giá" | ☐ |
| F12 | `src/components/PtCard.tsx` | (Nên làm) không hiện 5.0 khi PT chưa có review | ☐ |

**Lệnh kiểm tra:**
```bash
cd frontend-react && npx tsc --noEmit && npm run build
```

### 4.14 Lỗi có sẵn ngoài phạm vi chuẩn hóa

Các lỗi dưới đây **không do 1NF/3NF gây ra**. Chúng làm hỏng các luồng dẫn tới ca COMPLETED (điều kiện để được đánh giá). Danh sách đã đối chiếu với route của `backend-py`; nên mở task riêng hoặc sửa luôn.

| Vị trí React | Đang gọi | Backend thực tế |
|---|---|---|
| `PtPage.tsx:92` | `POST /pt/bookings/{id}/approve` | `PUT /pt/bookings/{id}/confirm` |
| `PtPage.tsx:102` | `POST /pt/bookings/{id}/reject` | `PUT /pt/bookings/{id}/reject` |
| `PtPage.tsx:113` | `POST /attendance/bookings/{id}/otp/verify` | 3 bước:<br>1. PT mở phiên: `POST /attendance/{id}/start` (trả `otpCode`)<br>2. Học viên nhập OTP: `POST /attendance/{id}/student-checkin` với body `{otpCode}`<br>3. PT hoàn tất: `POST /attendance/{id}/pt-confirm` |
| `StudentPage.tsx:149` | `POST /attendance/bookings/{id}/otp/generate` | Học viên **không** sinh OTP. Đổi thành ô nhập OTP rồi gọi `student-checkin` |
| `PtPage.tsx:349` | `PUT /pt/courses/{id}/toggle-status` | `PUT /pt/courses/{id}` với đủ body và `status: ACTIVE/INACTIVE` |
| `PtPage.tsx:379`, `StudentPage.tsx:726` | `PUT /users/me/avatar` | `PUT /users/avatar` (PtPage đã sửa ở §4.8; StudentPage sửa tương tự) |

Seed đã có sẵn nhiều booking COMPLETED, nên **vẫn test được luồng đánh giá ngay** mà không cần sửa các lỗi trên trước.

---

## 5. KIỂM THỬ TÍCH HỢP (MySQL THẬT) VÀ NGHIỆM THU

### 5.1 Dựng lại môi trường

```bash
cd PT-Connect
docker compose down -v
docker compose up -d mysql                       # nạp init.sql + trigger.sql mới
docker exec -i ptconnect-mysql mysql -uroot -proot123 ptconnect < database/seed_demo.sql

cd backend-py && rm -f ptconnect.db test.db
DB_HOST=127.0.0.1 DB_PORT=3307 uvicorn app.main:app --port 8080 --workers 1

cd ../frontend-react && npm run dev               # Vite proxy /api -> :8080
```

> Nếu backend Java trong compose đang chiếm cổng 8080, dừng nó trước: `docker compose stop backend`.

### 5.2 Kiểm tra dữ liệu (SQL)

```sql
-- 1NF: cột mới có, cột cũ không còn
SHOW COLUMNS FROM pt_profiles LIKE 'certificate_url%';   -- chỉ 1 dòng: certificate_url varchar(500)
-- 3NF: reviews chỉ còn 5 cột
SHOW COLUMNS FROM reviews;                                -- id, booking_id, rating, comment, created_at
-- Trigger và view khớp nhau (kết quả phải RỖNG)
SELECT p.id FROM pt_profiles p JOIN v_pt_rating_statistics v ON v.pt_profile_id = p.id
WHERE p.average_rating <> v.calculated_average_rating OR p.total_reviews <> v.calculated_total_reviews;
```

### 5.3 Kiểm tra API (curl)

```bash
TOKEN_S=$(curl -s localhost:8080/api/v1/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"student.a@ptconnect.vn","password":"Password123@"}' | jq -r .data.token)

curl -s localhost:8080/api/v1/reviews/pt/1 | jq '.data[0] | keys'
#  -> phải có: bookingId, comment, createdAt, id, ptId, rating, studentAvatarUrl, studentId, studentName

curl -s localhost:8080/api/v1/reviews/my -H "Authorization: Bearer $TOKEN_S" | jq '.data | length'

# Tìm 1 ca COMPLETED chưa review của student.a rồi gửi review
curl -s localhost:8080/api/v1/bookings/my?status=COMPLETED -H "Authorization: Bearer $TOKEN_S" | jq '[.data[].id]'
curl -s -X POST localhost:8080/api/v1/reviews -H "Authorization: Bearer $TOKEN_S" -H 'Content-Type: application/json' \
  -d '{"bookingId": <ID>, "rating": 5, "comment": "Test 3NF"}' | jq '.status, .data.studentName, .data.ptId'
#  -> 201, tên học viên, id PT; gửi lần 2 -> 400 "Ca tập này đã được đánh giá trước đó..."

# Đăng ký PT bằng key cũ dạng JSON-string -> lưu URL sạch
curl -s -X POST localhost:8080/api/v1/auth/register -H 'Content-Type: application/json' -d '{
  "fullName":"PT Test","email":"pt.test3nf@ptconnect.vn","password":"123456","phone":"0999000111","role":"PT",
  "availableLocations":"Cầu Giấy","certificateUrls":"[\"https://cdn.ptconnect.vn/certs/x.pdf\"]"}' | jq .status

TOKEN_A=$(curl -s localhost:8080/api/v1/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"admin@ptconnect.vn","password":"Password123@"}' | jq -r .data.token)
curl -s localhost:8080/api/v1/admin/pt/pending -H "Authorization: Bearer $TOKEN_A" \
  | jq '.data[] | select(.email=="pt.test3nf@ptconnect.vn") | {certificateUrl, certificateUrls}'
#  -> cả hai = "https://cdn.ptconnect.vn/certs/x.pdf"
```

### 5.4 Nghiệm thu giao diện React (checklist của guide, áp cho React)

| # | Tài khoản | Thao tác | Kỳ vọng |
|---|---|---|---|
| 1 | Khách | Tab Đăng ký → chọn "Huấn luyện viên" → nhập hồ sơ và link chứng chỉ → Đăng ký | Thành công; tài khoản ở trạng thái PENDING |
| 2 | `admin@ptconnect.vn` | Tab Phê duyệt | Card của PT mới có link chứng chỉ bấm được. PT seed `pt.hoangnam` và `pt.thuynga` hiện link `cert_nasam.jpg`. Nút Duyệt và Từ chối hoạt động bình thường |
| 3 | `pt.hoangc@ptconnect.vn` | Tab Hồ sơ → sửa số năm kinh nghiệm và link chứng chỉ → Lưu | Có toast thành công; tải lại trang vẫn thấy giá trị mới; khối "Đánh giá từ học viên" có danh sách review kèm tên học viên |
| 4 | `pt.hoangc` | Xóa trống ô "Địa điểm" → Lưu | Báo "Địa điểm nhận dạy không được để trống!" |
| 5 | `student.a@ptconnect.vn` | Khám phá PT → mở chi tiết HLV | Điểm sao và số lượt khớp với kết quả SQL ở §5.2; danh sách đánh giá có tên và avatar học viên |
| 6 | `student.a` | Lịch tập → lọc COMPLETED → "★ Đánh giá" → chọn 5 sao → Gửi | Có toast thành công; nút đổi thành "✓ Đã đánh giá"; điểm sao và số lượt của PT thay đổi (trigger) |
| 7 | `student.a` | Gửi lại đánh giá cho cùng ca (qua curl) | Trả 400, message tiếng Việt báo đánh giá trùng |

**Mật khẩu:** guide ghi `Password123@`. Nếu đăng nhập thất bại thì thử `Password123!`, vì tài liệu cũ ghi `Password123!`, còn hash trong seed do `bcrypt` trong `generate_data.py` tạo ra.

### 5.5 Thứ tự commit đề xuất

1. `refactor(db): normalize pt_profiles.certificate_url (1NF) and reviews via booking (3NF) + rating view` (các file `database/*` đang staged)
2. `refactor(backend-py): map 1NF/3NF schema with DTO adapters and certificate aliases` (B1–B13)
3. `feat(frontend-react): PT profile form, certificate display, review submit/list on normalized API` (F1–F12)
4. (Riêng) `fix(frontend-react): align booking/attendance/course/avatar endpoints with backend-py` (§4.14)
