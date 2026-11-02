# PT-Connect Backend Migration Plan: Spring Boot → FastAPI

**Goal:** replace `backend/` (Java 17, Spring Boot, JPA, Spring Security, JJWT, OpenPDF) with a Python FastAPI service. The Streamlit frontend, the MySQL schema (`database/init.sql`, `trigger.sql`) and the seed data stay unchanged.

**Compatibility target:** for every request the frontend sends, the new backend returns the same HTTP status, the same JSON shape (key names, types, nullability, date formats), the same Vietnamese messages, and leaves the database in the same state.

**Sources read:**
- every file under `backend/src` (main and test)
- `database/*.sql`, `docker-compose.yml`
- `frontend/api/*`, plus the pages and components that consume the API
- `PTConnect_Scenario_Muc1.md` (16 scenarios, SC-01 to SC-16)
- `pt-connect-usecase-2.3.md` (PT use cases)

---

## 0. Key decisions (summary)

| Topic | Decision | Why |
|---|---|---|
| Database | Keep MySQL 8 and the existing `init.sql` / `trigger.sql`. No data migration. Alembic is only for future changes (start from an empty baseline). | Java already uses `ddl-auto: none`. The DB owns generated columns, triggers and CHECKs. |
| ORM style | SQLAlchemy 2.0 **sync** sessions + PyMySQL. FastAPI runs `def` endpoints in a threadpool. | It is the closest match to JPA `@Transactional` + `SELECT … FOR UPDATE`. It avoids async lazy-load pitfalls. The load is small (one Streamlit client). |
| Response envelope | Rebuild `ApiResponse` exactly: `{timestamp, status, message, data}`. | The frontend unwraps `body["data"]` when both `status` and `data` exist (`frontend/api/client.py:57-63`). |
| JSON naming | Pydantic v2 models with `alias_generator=to_camel`, `populate_by_name=True`. Always serialize by alias and include `null`s. | Jackson writes camelCase and includes nulls by default. |
| Money | `Decimal` internally, `ROUND_HALF_UP` to 2 places. **Serialize as a JSON number**, not a string. | Pydantic v2 serializes `Decimal` as a string by default. Jackson writes `BigDecimal` as a number. |
| Datetimes | Naive local time `Asia/Ho_Chi_Minh`, serialized as `YYYY-MM-DDTHH:MM:SS`. Dates as `YYYY-MM-DD`. | Same as `LocalDateTime` / `LocalDate`. The frontend calls `datetime.fromisoformat` and `strptime("%Y-%m-%d")`. |
| JWT | PyJWT, **same secret, same algorithm (HS384, see §2.5), same claims**. | Tokens work across both backends, so shadow testing and rollback need no re-login. |
| Passwords | `bcrypt` library. Accept both `$2a$` (Spring) and `$2b$` (seed generator) hashes. | Existing users keep their passwords. |
| Contract PDF | `fpdf2`, same text and layout, with an embedded DejaVu TTF. | OpenPDF currently uses Helvetica, so Vietnamese diacritics in names are lost. |
| OTP store | Same semantics (6 digits, 30-minute TTL, keyed by bookingId) behind an `OtpStore` interface. Phase 1 uses an in-process implementation with **a single uvicorn worker**; Redis is an option later. | Java keeps OTPs in a `ConcurrentHashMap`. With several workers the OTPs would split across processes and break check-in. |
| Behaviour policy | **Bug-for-bug compatible by default.** Any intentional change is listed in the deviation register (§5) and needs sign-off. | "100% compatible" is only testable if differences are explicit. |

---

## 1. Analysis of the current Java backend

### 1.1 Size and layering

About 11k lines of Java under `com.PTconnect.backend`:

| Layer | Content | Notes |
|---|---|---|
| `controller/` (13) | 60 endpoints, all under `/api/v1` | Controllers are thin: they get the email from `SecurityUtils`, call one service method, and wrap the result in `ApiResponse`. |
| `service/` + `service/impl/` (14 + 14) | Interface plus implementation for Auth, User, PTProfile, PTCourse, PTSlot, PT (facade), Booking, Enrollment, Wallet, Attendance, Review, WorkoutPlan, AdminPT, AdminStatistics | All business rules live here. Mutations use `@Transactional`. |
| `policy/` (7) | Cancellation Strategy plus Factory (`Student`, `Pt`, `Admin` policies, `BaseCancellationPolicy`) | Pure functions, easy to port and unit-test. |
| `handler/` (3) | Registration strategy (`StudentRegistrationHandler`, `PtRegistrationHandler`) | A PT registration creates a `pt_profiles` row with status PENDING. |
| `entity/` (16 + 15 enums) | JPA entities with domain methods (`Booking.confirm/cancel/complete`, `Enrollment.consume/restoreSession`, `Wallet.credit/debit/debitPenalty`, `PTProfile.approve/reject`) | `users` uses single-table inheritance with discriminator `role` (Student / PT / Admin). |
| `repository/` (15) | Spring Data repositories | 3 pessimistic locks (`findByIdWithLock` on slot, booking, enrollment), a few JPQL queries, no native SQL. |
| `dto/request` (18), `dto/response` (21) | Bean Validation annotations with Vietnamese messages | These define the wire contract. |
| `config/` | `SecurityConfig`, `JwtFilter`, `JwtUtil` | Path-based role rules, stateless JWT, custom 403 body. |
| `exception/` | 5 custom exceptions + `GlobalExceptionHandler` | Maps exceptions to status codes (§1.4). |
| `util/` | `ApiResponse`, `SecurityUtils`, `OtpUtil`, `ContractPdfGenerator` | |

### 1.2 Database-side behaviour the port must respect (not in Java)

- `bookings.active_slot_id`:
  - It is a STORED generated column: `IF(status IN (PENDING,CONFIRMED,COMPLETED), slot_id, NULL)`.
  - It has a UNIQUE index, which is the final double-booking guard.
  - A violation must map to **409** with "Khung giờ này vừa có người khác đặt trước, vui lòng chọn khung giờ khác".
- `pt_profiles.average_rating` and `total_reviews` are maintained by the triggers `trg_reviews_after_insert/update/delete`.
- `created_at` / `updated_at` are DB defaults with `ON UPDATE CURRENT_TIMESTAMP`.
- CHECK constraints:
  - booking: TRIAL ⇔ `enrollment_id IS NULL`
  - `0 <= remaining_sessions <= total_sessions`
  - `amount > 0`
  - `rating 1..5`
  - `hours_before_session decimal(5,2)`
- UNIQUE constraints: `(pt_id, start_time)` on slots, `email`, `phone`, `reviews.booking_id`, `attendance.booking_id`, `cancellations.booking_id`.
- Foreign key convention: `bookings.pt_id`, `courses.pt_id`, `enrollments.pt_id` and `availability_slots.pt_id` all point to **`pt_profiles.id`**, not `users.id`. Wallets are keyed by `users.id`.

### 1.3 Security model (`config/SecurityConfig.java`)

Stateless JWT. The filter reads `Authorization: Bearer`, loads the user by email (`sub`), and **takes the role from the DB, not from the token**. Rules are first-match, top to bottom:

| # | Pattern | Rule |
|---|---|---|
| 1 | `/api/v1/users/avatar`, `/api/v1/auth/me` | authenticated |
| 2 | `/auth/register`, `/auth/login`, `/public/**`, `/error` | permitAll |
| 3 | `GET /pt-profiles/**` | permitAll |
| 4 | `POST /bookings`, `/bookings/my` | STUDENT |
| 4 | `/pt/bookings/**` | PT |
| 4 | `/bookings/**` | authenticated |
| 5 | `/student/**` | STUDENT |
| 5 | `/pt/**` | PT |
| 5 | `/admin/**` | ADMIN |
| 6 | `/wallet/topup`, `POST /enrollments`, `/enrollments/my` | STUDENT |
| 6 | `/wallet/**`, `/enrollments/**`, `/users/**` | authenticated |
| 7 | `POST /reviews` | STUDENT |
| 7 | `/reviews/**` | **permitAll** |
| 7 | `/attendance/**` | authenticated |
| 8 | anything else | authenticated |

Two kinds of 401/403 response:

- **Security layer:**
  - 401 comes from `response.sendError(401, "Unauthorized")`, so the body is Spring's `/error` JSON (`timestamp, status, error, path`, maybe `message`). Capture the exact body from the running Java service (Phase 0).
  - 403 is a fixed JSON `{"status":403,"message":"Bạn không có quyền truy cập tài nguyên này","data":null}`. It has no `timestamp`.
- **Service layer:** `UnauthorizedException` produces a 401 with the normal `ApiResponse` envelope. For example, anonymous `GET /reviews/my` passes the security layer (`/reviews/**` is permitAll), then fails in `SecurityUtils` with "Chưa đăng nhập".

Other security facts:
- An invalid or expired token is silently ignored and the request is treated as anonymous.
- A suspended user with a still-valid token keeps passing the filter. Only `login` checks `SUSPENDED`.
- Several ownership checks live in services, not in the security config. Their status codes are inconsistent (§5).

### 1.4 Error mapping (`exception/GlobalExceptionHandler.java`)

| Exception | HTTP | Body `message` |
|---|---|---|
| `ResourceNotFoundException` | 404 | exception message |
| `BookingConflictException` | 409 | exception message |
| `DataIntegrityViolationException` | 409 | "Dữ liệu không hợp lệ hoặc vi phạm ràng buộc hệ thống!" (except the booking insert, which is caught in the service and gets its own message) |
| `InsufficientBalanceException`, `BadRequestException`, `IllegalArgumentException`, `IllegalStateException` | 400 | exception message |
| `UnauthorizedException` | 401 | exception message |
| `MethodArgumentNotValidException` (Bean Validation) | 400 | `"<field>: <message>"` for the **first** field error |
| any other `Exception` | 500 | `ex.getMessage()` |

Because of the catch-all, several framework errors probably come back as 500. This includes `AccessDeniedException` thrown by `EnrollmentServiceImpl.validateAccess`, and possibly malformed JSON, a bad enum value in a query or body, or a non-numeric path id. **Do not guess these: capture them from the Java service in Phase 0.**

### 1.5 Response quirks the frontend may depend on

- `POST /auth/register` returns HTTP **201**, but the body has `"status": 200`, because it uses `ApiResponse.success`.
- Other creates (`bookings`, `enrollments`, `pt/courses`, `pt/slots`, `reviews`, `workout-plans`, `workouts`) return 201 with body status 201.
- `POST /wallet/topup` returns 200.
- DELETE endpoints return 200 with `data: null`.
- `GET /public/health` and `GET /student/dashboard` return raw maps **without** the envelope.
- `GET /enrollments/{id}/contract` returns raw `application/pdf` bytes with `Content-Disposition` and `Cache-Control` headers.
- The `ApiResponse.timestamp` format is `yyyy-MM-dd'T'HH:mm:ss'Z'`. That is local time followed by a literal `Z`.
- `SlotResponse.startTime/endTime` use `yyyy-MM-dd'T'HH:mm:ss`. Other `LocalDateTime` fields use Jackson's default ISO output.
- `CreateSlotRequest` accepts `yyyy-MM-dd['T'][' ']HH:mm[:ss]`, so a space separator and missing seconds are both allowed.
- `PaymentMethod` parsing is lenient: VNPAY, MOMO, ZALOPAY, QR, null and any unknown value become `BANK_TRANSFER`.
- `AdminStatisticsResponse` uses the key `totalPts`.
- Right after an insert, Java does not re-read DB-default columns, so `createdAt` and `updatedAt` are often `null` in create responses.
- `PUT /pt/bookings/{id}/reject`, `PUT /bookings/{id}/cancel` and `PUT /pt/bookings/{id}/cancel` take an **optional** body without `@Valid`. A missing body falls back to a default reason. A blank reason is not rejected for reject.
- `POST /attendance/{id}/absent` takes `reason` as a **query parameter** with a default value.
- `/admin/bookings/page` and `/admin/payments/page` accept Spring `Pageable` (`page`, `size`, `sort`) and return a serialized Spring `Page`. The frontend does not use them, but keep them and match the shape you capture.

### 1.6 Business logic inventory (what must be ported 1:1)

- **Auth**
  - Register checks for a duplicate email, then a duplicate phone.
  - The role handler then runs: STUDENT is created ACTIVE; PT is created PENDING together with a PTProfile, with locations defaulting to "Chưa cập nhật địa điểm".
  - Both roles get a wallet with balance 0 VND, and the response returns a JWT.
  - Login checks the password before checking SUSPENDED. PENDING users can log in.
- **PT profile / course / slot**
  - The PT guard checks: role is PT, user is not SUSPENDED, and the profile exists.
  - A PENDING PT passes the guard.
  - Course rules:
    - Validation messages are listed in the DTOs.
    - A course can only be deleted if it has no enrollments; otherwise it can only be set INACTIVE.
  - Slot rules:
    - A slot cannot start in the past, must end after it starts, and must not overlap another slot of the same PT (any status).
    - A slot can only be deleted if it is AVAILABLE and has never been booked.
- **Public PT list**
  - Shows only VERIFIED and ACTIVE PTs, with an optional `LIKE` search on the name.
  - `lowestPrice` is the minimum `basePrice > 0` over the PT's ACTIVE courses.
  - `/pt-profiles/{id}` has no verification filter.
- **Booking**
  - Creation takes the slot lock, then:
    - checks the slot is AVAILABLE and in the future
    - checks the student has no overlapping booking
  - TRIAL bookings:
    - only once per PT, ever; cancelled trials count too
    - fee 0
  - PACKAGE bookings:
    - lock the enrollment
    - check ownership, same PT, ACTIVE, not expired, slot date ≤ endDate, remaining > 0
    - consume one session
    - `fee = finalPrice / totalSessions` (HALF_UP)
  - The slot becomes BOOKED, and a UNIQUE conflict maps to 409.
- **Confirm / reject / cancel**
  - Confirm requires PENDING.
  - Reject uses the PT policy.
  - Student and PT cancel apply the policy table, then restore the session, move money between wallets and insert a `cancellations` row.
- **Cancellation policies** (24h threshold; hours = floor(minutes) / 60, scale 2):
  - Student:
    - TRIAL → nothing happens.
    - PENDING → the session is restored.
    - CONFIRMED, cancelled ≥ 24h before → the session is restored.
    - CONFIRMED, cancelled < 24h before → the session is lost and 50% of the fee goes to the PT wallet.
  - PT:
    - PACKAGE → the session is always restored.
    - PACKAGE cancelled < 24h before → 20% of the fee is paid to the student and 20% is taken from the PT wallet (the balance can go negative). The penalty payment row has type `REFUND`.
  - Admin: preview only.
- **Wallet**
  - Top-up rules:
    - no payment gateway
    - minimum 10,000 (DTO)
    - ref `TXN_TOPUP_yyyyMMdd_XXXXXXXX`
  - Debit is blocked if `balance - amount < lockedBalance`.
  - A FROZEN wallet blocks every operation.
- **Enrollment**
  - Purchase checks:
    - the course is ACTIVE
    - there is no other ACTIVE enrollment of the same course with sessions remaining
    - `trainingLocation` is not blank
  - It then:
    - uses `finalPrice = basePrice` and `endDate = today + validityDays`
    - debits the wallet and writes a PURCHASE_PACKAGE payment row
    - sets `contractUrl = /api/v1/enrollments/{id}/contract`
    - writes the PDF to `uploads/contracts/contract_{id}.pdf` (failures are swallowed)
  - Access is limited to the owning student, the owning PT, or ADMIN.
- **Attendance**
  - Start:
    - only the owning PT can start, only for a CONFIRMED booking
    - no earlier than 15 minutes before the start
    - status LATE if more than 15 minutes after the start
    - generates the OTP and upserts the row
  - Student check-in validates the OTP.
  - PT confirm needs no OTP. When both sides have confirmed, the session completes:
    - the booking becomes COMPLETED and the OTP is cleared
    - the enrollment becomes COMPLETED if `remaining == 0` and it has no other open bookings
  - `absent` marks ABSENT and still completes the session.
- **Review**
  - Only the owning student can review, only a COMPLETED booking, and only once.
  - The DB triggers update the rating.
- **Workout plan**
  - Only the owning PT can create a plan.
  - Dates default to the enrollment's dates, then to today + 4 weeks.
  - The start date cannot be after the end date.
  - A workout must belong to its plan.
- **Admin**
  - Approve sets VERIFIED and the user ACTIVE. Reject sets REJECTED and the user PENDING. There are no state preconditions.
  - User status can be set freely.
  - Stats:
    - `totalRevenue` = sum of `PURCHASE_PACKAGE` payments with status SUCCESS
    - booking analytics come from a LEFT JOIN with cancellations; `cancelledBy` defaults to "STUDENT"

### 1.7 Endpoint inventory (the compatibility checklist, 60 endpoints)

Legend: S = STUDENT, P = PT, A = ADMIN, auth = any logged-in user, open = permitAll. ✔FE = called by the frontend.

| # | Method & path | Access | Success | FE |
|---|---|---|---|---|
| 1 | POST `/api/v1/auth/register` | open | 201 (body status 200) | ✔ |
| 2 | POST `/api/v1/auth/login` | open | 200 | ✔ |
| 3 | GET `/api/v1/auth/me` | auth | 200 | (wrapper only) |
| 4 | GET `/api/v1/users/{id}` | auth | 200 | |
| 5 | PUT `/api/v1/users/avatar` | auth | 200 | ✔ |
| 6 | GET `/api/v1/public/health` | open | 200 raw map | |
| 7 | GET `/api/v1/student/dashboard` | S | 200 raw map | |
| 8 | GET `/api/v1/pt-profiles?name=` | open | 200 | ✔ |
| 9 | GET `/api/v1/pt-profiles/{id}` | open | 200 | ✔ |
| 10 | GET `/api/v1/pt-profiles/{id}/courses` | open | 200 | ✔ |
| 11 | GET `/api/v1/pt-profiles/{id}/slots` | open | 200 | ✔ |
| 12 | GET `/api/v1/pt/profile` | P | 200 | ✔ |
| 13 | PUT `/api/v1/pt/profile` | P | 200 | ✔ |
| 14 | POST `/api/v1/pt/courses` | P | 201 | ✔ |
| 15 | GET `/api/v1/pt/courses` | P | 200 | ✔ |
| 16 | PUT `/api/v1/pt/courses/{id}` | P | 200 | ✔ |
| 17 | DELETE `/api/v1/pt/courses/{id}` | P | 200 | ✔ |
| 18 | POST `/api/v1/pt/slots` | P | 201 | ✔ |
| 19 | GET `/api/v1/pt/slots` | P | 200 | ✔ |
| 20 | DELETE `/api/v1/pt/slots/{id}` | P | 200 | ✔ |
| 21 | POST `/api/v1/bookings` | S | 201 | ✔ |
| 22 | GET `/api/v1/bookings/my?status=` | S | 200 | ✔ |
| 23 | GET `/api/v1/bookings/{id}` | auth | 200 | (wrapper only) |
| 24 | PUT `/api/v1/bookings/{id}/cancel` | auth | 200 | ✔ |
| 25 | GET `/api/v1/bookings/{id}/cancel-preview` | auth | 200 | ✔ |
| 26 | GET `/api/v1/pt/bookings?status=` | P | 200 | ✔ |
| 27 | PUT `/api/v1/pt/bookings/{id}/confirm` | P | 200 | ✔ |
| 28 | PUT `/api/v1/pt/bookings/{id}/reject` | P | 200 | ✔ |
| 29 | PUT `/api/v1/pt/bookings/{id}/cancel` | P | 200 | ✔ |
| 30 | GET `/api/v1/wallet` | auth | 200 | ✔ |
| 31 | POST `/api/v1/wallet/topup` | S | 200 | ✔ |
| 32 | POST `/api/v1/enrollments` | S | 201 | ✔ |
| 33 | GET `/api/v1/enrollments/my` | S | 200 | ✔ |
| 34 | GET `/api/v1/enrollments/{id}` | auth | 200 | |
| 35 | GET `/api/v1/enrollments/{id}/contract` | auth | 200 PDF | ✔ |
| 36 | GET `/api/v1/pt/enrollments` | P | 200 | ✔ |
| 37 | POST `/api/v1/pt/workout-plans` | P | 201 | ✔ |
| 38 | POST `/api/v1/pt/workout-plans/{id}/workouts` | P | 201 | ✔ |
| 39 | GET `/api/v1/enrollments/{id}/workout-plans` | auth | 200 | ✔ |
| 40 | GET `/api/v1/pt/workout-plans` | P | 200 | ✔ |
| 41 | DELETE `/api/v1/pt/workout-plans/{id}` | P | 200 | ✔ |
| 42 | DELETE `/api/v1/pt/workout-plans/{planId}/workouts/{workoutId}` | P | 200 | ✔ |
| 43 | POST `/api/v1/attendance/{bookingId}/start` | auth | 200 | ✔ |
| 44 | POST `/api/v1/attendance/{bookingId}/student-checkin` | auth | 200 | ✔ |
| 45 | POST `/api/v1/attendance/{bookingId}/pt-confirm` | auth | 200 | ✔ |
| 46 | POST `/api/v1/attendance/{bookingId}/absent?reason=` | auth | 200 | ✔ |
| 47 | GET `/api/v1/attendance/{bookingId}` | auth | 200 | (wrapper only) |
| 48 | POST `/api/v1/reviews` | S | 201 | ✔ |
| 49 | GET `/api/v1/reviews/pt/{ptId}` | open | 200 | ✔ |
| 50 | GET `/api/v1/reviews/my` | open → 401 in service | 200 | |
| 51 | GET `/api/v1/reviews/booking/{bookingId}` | open | 200 (data may be null) | ✔ |
| 52 | GET `/api/v1/admin/users?role=` | A | 200 | ✔ |
| 53 | PUT `/api/v1/admin/users/{id}/status` | A | 200 | ✔ |
| 54 | GET `/api/v1/admin/pt/pending` | A | 200 | ✔ |
| 55 | PUT `/api/v1/admin/pt/{id}/approve` | A | 200 | ✔ |
| 56 | PUT `/api/v1/admin/pt/{id}/reject` | A | 200 | ✔ |
| 57 | GET `/api/v1/admin/statistics` | A | 200 | ✔ |
| 58 | GET `/api/v1/admin/bookings` | A | 200 | ✔ |
| 59 | GET `/api/v1/admin/bookings/page` | A | 200 Page | |
| 60 | GET `/api/v1/admin/payments` (+ `/payments/page`) | A | 200 | ✔ (list only) |

### 1.8 What the frontend actually relies on (`frontend/api/client.py` and pages)

- **Envelope and lists:**
  - On 2xx, if the body has both `status` and `data`, the client returns `data`.
  - Every list endpoint must return `data` as a **plain JSON array**. The wrappers do `res if isinstance(res, list) else []`, so a paged object would quietly show as empty.
- **Errors:**
  - The client reads `body["message"]`, then `body["error"]`, and shows `[{status_code}]: {message}`.
  - FastAPI's default `{"detail": …}` would lose every message. All errors must use the envelope.
- **Auth retry on 404:** a **404 on auth endpoints** makes the client retry the legacy paths `/auth/login` and others. Never return 404 from login.
- **Values that must never be null:**
  - `averageRating` / `totalReviews` (the client calls `float(...)` and `f"{x:.1f}"`)
  - `id` (formatted with `:06d`)
  - `remainingSessions` / `totalSessions` (used in arithmetic)
  - `paymentType` and `status` on every payment row (analytics `groupby`)
  - `endDate` must be a pure date string.
- **Avatar URL:** `avatarUrl` can be relative (`/app/static/avatars/x.jpg`), so do not validate it as a URL.
- **Contract PDF:** it is fetched eagerly for **every enrollment on each render** of "My Courses", with a 15s client timeout. The 15s limit leaves little room for slow PDF generation.
- **Other client facts:** client timeouts are 10s; `BACKEND_URL` defaults to `http://backend:8080`. The new service must listen on **8080** under the compose service name `backend`.
- **Existing frontend test:** `frontend/tests/test_frontend_auth.py` is fully mocked. Keep it green, and reuse its fixtures as the envelope and 401 contract examples.

---

## 2. Target FastAPI architecture

### 2.1 Directory layout

```text
PT-Connect/
└── backend-py/                         # built side by side with backend/ until cutover
    ├── pyproject.toml                  # fastapi, uvicorn, sqlalchemy>=2, pymysql, cryptography,
    │                                   # pydantic>=2, pydantic-settings, pyjwt, bcrypt, fpdf2
    ├── Dockerfile                      # python:3.12-slim, TZ=Asia/Ho_Chi_Minh, uvicorn --workers 1 --port 8080
    ├── assets/fonts/DejaVuSans*.ttf
    ├── app/
    │   ├── main.py                     # create_app(): routers, exception handlers, CORS, redirect_slashes=False
    │   ├── core/
    │   │   ├── config.py               # Settings: DB_*, JWT_SECRET, JWT_EXPIRATION (same env names as Java)
    │   │   ├── security.py             # JwtService (encode/decode, HS384), PasswordHasher (bcrypt)
    │   │   ├── deps.py                 # get_db, get_optional_user, get_current_user, require_roles(...)
    │   │   ├── exceptions.py           # AppError subclasses: NotFound, BadRequest, Conflict, Unauthorized, ...
    │   │   ├── handlers.py             # exception → ApiResponse JSON (mirror of GlobalExceptionHandler)
    │   │   ├── responses.py            # ApiResponse model + ok()/created() helpers
    │   │   └── clock.py                # now_local() / today_local(); injectable for tests
    │   ├── db/
    │   │   ├── base.py                 # DeclarativeBase
    │   │   └── session.py              # engine (pool_pre_ping), SessionLocal(autoflush=True, expire_on_commit=False)
    │   ├── models/                     # one file per table; enums.py holds the 15 Python Enums
    │   │   ├── user.py                 # User (polymorphic_on=role), Student, PT, Admin
    │   │   ├── pt_profile.py  course.py  availability_slot.py  booking.py  enrollment.py
    │   │   ├── wallet.py  payment.py  cancellation.py  attendance.py  review.py
    │   │   └── workout_plan.py  workout.py
    │   ├── schemas/
    │   │   ├── base.py                 # CamelModel, Money, LocalDateTime, LocalDate, SlotDateTime types
    │   │   ├── requests/               # one file per Java request DTO, same field names and messages
    │   │   └── responses/              # one file per Java response DTO
    │   ├── repositories/               # query functions incl. *_for_update() (= findByIdWithLock)
    │   ├── services/                   # auth, user, pt_profile, pt_course, pt_slot, booking, enrollment,
    │   │                               # wallet, attendance, review, workout_plan, admin_pt, admin_statistics
    │   ├── services/registration/      # student_handler.py, pt_handler.py (strategy, like handler/)
    │   ├── policies/                   # base.py, student.py, pt.py, admin.py, factory.py
    │   ├── otp/                        # OtpStore protocol, InMemoryOtpStore (TTL 30 min)
    │   ├── pdf/contract.py             # ContractPdfGenerator (fpdf2)
    │   └── api/v1/
    │       ├── router.py               # include_router(...) for all modules
    │       └── routes/                 # auth, users, public, student, pt_profiles, pt, bookings,
    │                                   # enrollments, wallet, workout_plans, attendance, reviews, admin
    └── tests/
        ├── unit/                       # policies, domain methods, schemas, jwt
        ├── integration/                # services + routes on real MySQL (testcontainers)
        ├── contract/                   # golden-master replay vs recorded Java responses
        └── e2e/                        # SC-01..SC-16 through the real frontend
```

### 2.2 Java → Python mapping

| Spring | FastAPI / Python |
|---|---|
| `@RestController` + `@RequestMapping` | `APIRouter(prefix=...)` per controller file |
| `@PathVariable Long id` | `id: int` path param. **Declare `/bookings/my` before `/bookings/{id}`** (same for `/enrollments/my`); Starlette matches routes in declaration order. |
| `@RequestParam(required=false) BookingStatus status` | `status: BookingStatus \| None = Query(None)` |
| `@Valid @RequestBody X` | `body: XRequest`. Validation errors are mapped to 400 `"field: message"` (§2.4). |
| `@RequestBody(required=false)` without `@Valid` | `body: XRequest \| None = Body(None)`, using a model **without** field validators |
| `Pageable` | `page: int = 0, size: int = 20, sort: str \| None` → `PageParams`, returning the captured Spring Page JSON shape |
| `Authentication` + `SecurityUtils.getCurrentUserEmail` | `current_user: User = Depends(get_current_user)` |
| `SecurityConfig` path rules | `require_roles("PT")` dependency on each router or route, plus a routing table test (§4.3) |
| `@Service` + interface | Plain classes in `services/`, built per request with `Depends` (they take a `Session`). Drop the `IxxxService` interfaces. |
| `@Transactional` | The service method owns the unit of work: `with db.begin():` (or explicit `commit()` / `rollback()` in the request-scoped session) |
| `@Transactional(readOnly=true)` | No commit. |
| `@Lock(PESSIMISTIC_WRITE)` | `select(...).with_for_update()` |
| JPA entities + Lombok | SQLAlchemy `Mapped[...]` models. Domain methods (`confirm()`, `consume_session()`, `debit()`, …) stay **on the model** with the same exceptions and messages. |
| `@Inheritance(SINGLE_TABLE)` + `@DiscriminatorColumn("role")` | `__mapper_args__ = {"polymorphic_on": role, "polymorphic_identity": "STUDENT"}` on `User` subclasses |
| `insertable=false, updatable=false` DB columns | `server_default=FetchedValue()`, `Computed(...)` for `active_slot_id`, `FetchedValue` for rating columns, `db.refresh(obj)` where a response needs them |
| `Optional<T>.orElseThrow(...)` | `repo.get(...) or raise NotFound("…")` |
| Jackson DTO mapping (`fromEntity`) | `XResponse.from_entity(entity)` classmethods (explicit, no `from_attributes` magic, to keep null behaviour identical) |
| `BigDecimal.setScale(2, HALF_UP)` | `Decimal.quantize(Decimal("0.01"), ROUND_HALF_UP)` |
| `LocalDateTime.now()` | `clock.now_local()` (naive, VN time). Mockable in tests, which matters for the 24h, 15-minute and expiry rules. |
| `OtpUtil` (`ConcurrentHashMap`) | `InMemoryOtpStore` (dict + `threading.Lock`), app-scoped singleton |
| OpenPDF `ContractPdfGenerator` | `fpdf2` `ContractPdfGenerator`, same output path `uploads/contracts/contract_{id}.pdf` |
| H2 test DB | Real MySQL 8 via testcontainers, loading `init.sql` + `trigger.sql`. SQLite or H2 cannot run the generated column, the triggers, the CHECKs or `FOR UPDATE`. |

### 2.3 Pydantic conventions (`schemas/base.py`)

```python
class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True,
                              extra="ignore")          # Jackson ignores unknown fields too

Money = Annotated[Decimal, PlainSerializer(lambda v: float(v) if v is not None else None,
                                           return_type=float | None, when_used="json")]
LocalDateTime = Annotated[datetime, PlainSerializer(lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") if v else None,
                                                    when_used="json")]
# SlotDateTime input: accept "YYYY-MM-DD[T| ]HH:MM[:SS]" via BeforeValidator (CreateSlotRequest)
# PaymentMethodIn: BeforeValidator mirroring PaymentMethod.fromString (VNPAY/MOMO/ZALOPAY/QR/None/unknown → BANK_TRANSFER)
```

- Routes return `JSONResponse(ApiResponse(...).model_dump(mode="json", by_alias=True))` through a helper, so `None` values are kept and aliases are always used.
- Enums are `class BookingStatus(str, Enum)` and serialize as their names, the same as Jackson.
- **Money check:** Jackson writes `500000.00`; `float()` gives `500000.0`. Both are JSON numbers and the frontend only calls `float()`. Accept this, and normalize numbers in the golden-master diff.

### 2.4 Validation and error handling (`core/handlers.py`)

- `AppError` subclasses carry `status_code` and `message`:
  - `NotFound` 404
  - `Conflict` 409
  - `BadRequest` 400 (also used for Java's `IllegalArgument` / `IllegalState` / `InsufficientBalance`)
  - `Unauthorized` 401
  - `ServerError` 500 (used for the Java paths that currently return 500, until a fix is approved)
- `RequestValidationError` → **400**, message `"<field>: <message>"`:
  - Take the first error.
  - `field` is the camelCase Java field name.
  - `message` is the Vietnamese text from the Java annotation.
  - Implementation: a custom `Field(..., json_schema_extra={"msg": ...})` or `field_validator`s that raise `PydanticCustomError("app", "<java message>")`. The handler uses `err["msg"]`, with Pydantic's default prefix stripped.
  - Java validates fields in an unspecified order and returns the first error. Tests should send **one invalid field at a time**.
- `sqlalchemy.exc.IntegrityError` → 409 "Dữ liệu không hợp lệ hoặc vi phạm ràng buộc hệ thống!" (generic), except where a service catches it first (booking insert).
- Missing or invalid token on a protected route → 401, with the **body captured from Spring** (§1.3).
- Wrong role → 403 `{"status":403,"message":"Bạn không có quyền truy cập tài nguyên này","data":null}`, plus the same warning log line as `LoggingAccessDeniedHandler`.
- Framework errors (malformed JSON, bad enum in a query, non-int path id) → replicate whatever Phase 0 captures from Java (probably 500 with Java's exception text; normalize the message in the diff).
- Catch-all `Exception` → 500 envelope with `str(exc)`.

### 2.5 JWT and auth (must interoperate with Java tokens)

- **Key:** `JwtUtil.getSigningKey()` first tries Base64-decoding `jwt.secret`. The default secret `404E6352…5970` (64 characters) is valid Base64, so it decodes to **48 bytes**, with a UTF-8 fallback and zero-padding to 32 bytes. With a 48-byte key, JJWT 0.12 `signWith(key)` chooses **HS384**.
  - Python:
    ```python
    key = b64decode(secret)  # except: secret.encode(); pad to 32
    alg = "HS512" if len(key) >= 64 else "HS384" if len(key) >= 48 else "HS256"
    ```
  - **Verify in Phase 0** by decoding the header of a token issued by Java.
- **Claims:** `sub` = email, `userId`, `role`, `fullName`, `iat`, `exp` (now + `JWT_EXPIRATION` ms, default 86,400,000 = 24h).
- **`get_optional_user`:**
  1. Parse the Bearer token. On any error → anonymous, and log `JWT validation failed`.
  2. Load the user by email; take the **role from the DB** (falling back to the token's role, then "STUDENT").
- **`get_current_user`:** anonymous → 401.
- **`require_roles(*roles)`:** wrong role → 403.
- Do **not** add a suspended-user check to the filter in the compatible phase (deviation register D4).
- **Passwords:** `bcrypt.checkpw(pw.encode(), hash.encode())`. It accepts `$2a$` and `$2b$`. New hashes use `bcrypt.hashpw(pw, bcrypt.gensalt(10))`, the same cost as Spring's default.
- **CORS:** same origin list as `SecurityConfig` (8501, 3000, 8080), credentials allowed. The frontend calls the backend from the server side, so CORS is a formality.

### 2.6 Transactions, locking, concurrency

- One `Session` per request (`Depends(get_db)`), with `autoflush=True` and `expire_on_commit=False`.
- **Mutating service methods own the transaction.** On any exception they roll back fully, the same as `rollbackFor=Exception`.
- Lock order stays the same as Java to avoid deadlocks:
  - `create_booking`: slot `FOR UPDATE`, then enrollment `FOR UPDATE`.
  - Cancel and attendance: booking `FOR UPDATE`.
- **Autoflush matters in `complete_session`.** The "other open bookings on this enrollment" query must see the current booking as COMPLETED, the same as Hibernate's flush-before-query. Keep `autoflush=True` (or call `db.flush()` explicitly).
- **Booking insert:**
  - `db.add(booking); db.flush()` inside `try`.
  - On `IntegrityError` whose message names `uq_active_slot` → `Conflict("Khung giờ này vừa có người khác đặt trước, vui lòng chọn khung giờ khác")`.
- **Contract PDF:** generate it after the debit and payment row, swallow and log any exception, then commit. Writing the file before commit matches Java, including the leftover-file-on-rollback quirk.
- **Lazy loading:** sync SQLAlchemy lazy-loads inside the session like Hibernate. Use `selectinload` / `joinedload` on list endpoints (`getMyBookings`, `getMyEnrollments`, the PT list with `lowestPrice`) to avoid the Java N+1. The output stays identical.

### 2.7 Deployment

- `docker-compose.yml`:
  - Phase 1–8: add `backend-py` on port 8081 next to `backend` for side-by-side testing.
  - At cutover: point the `backend` service at `./backend-py`, still on port 8080, with the same env names (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`, `JWT_EXPIRATION`, `TZ`) and the same `./backend/uploads:/app/uploads` volume (move it to `./backend-py/uploads`, or keep the path).
- Run `uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1`. A single worker is needed because of the in-memory OTP store; scale out only after D7.
- The healthcheck uses `GET /api/v1/public/health`.

---

## 3. Phased roadmap

Estimates assume one developer who knows FastAPI and SQLAlchemy. Phases 4–7 can run in parallel with two developers once Phases 1–3 are done (about 3–4 weeks instead of about 6).

### Phase 0 – Freeze the contract and capture golden data (3–4 days)

1. Build and run the **current Java backend** with MySQL and `seed_demo.sql` through docker compose.
   - Note: `pom.xml` says Spring Boot **4.0.8**, but the README says 3.3.4. Capture from the version that actually builds, because Jackson and Page serialization differ between Boot 3 and 4.
2. Write `tests/contract/scenarios/*.py`: a pytest + httpx recorder that, for each of the 60 endpoints, sends:
   - one happy-path request
   - **each error branch listed in §1.6 and §1.4**, one at a time
   - an anonymous request, a wrong-role request and a right-role request (from the §1.3 table)
3. For each request, record method, path, body, status, headers (content-type, content-disposition) and JSON body under `tests/contract/golden/`.
   - For mutating calls, also record a **DB snapshot diff**: the affected rows in `bookings`, `enrollments`, `wallets`, `payments`, `cancellations`, `availability_slots`, `attendance`, `reviews`, `pt_profiles`, `users`.
4. Settle the open questions by observation, and write the answers into this document:
   - the exact 401 body from the security layer
   - the result of `AccessDeniedException` (500?)
   - the result of malformed JSON, a bad enum, or a non-int id
   - the `Page` JSON shape
   - the JWT `alg` header
   - `LocalDateTime` fractional seconds in responses built from `now()` (attendance `checkInTime`, `expiresAt`)
5. Write the normalizer used by the diff:
   - mask `timestamp`, `token`, `transactionRef` suffix, `otpCode`, and `now()`-derived datetimes
   - treat numbers numerically (`500000.00 == 500000.0`)
   - optionally remap auto-increment ids
6. **Exit:** the golden set covers all 60 endpoints, every RBAC cell and every error message in the Java code (check with a grep of the exception messages).

### Phase 1 – Project skeleton and cross-cutting infrastructure (2–3 days)

- Set up `backend-py/`, `pyproject.toml`, ruff + mypy, Dockerfile and the compose service on 8081.
- `core/config.py`, `db/session.py`, `core/clock.py`, `core/responses.py`, `core/exceptions.py`, `core/handlers.py`.
- `schemas/base.py` (CamelModel, Money, LocalDateTime, SlotDateTime, PaymentMethodIn).
- `GET /api/v1/public/health`.
- **Exit:** the health endpoint matches the golden output; unit tests pass for Money/datetime serialization, the validation-error format and every exception mapping.

### Phase 2 – Data layer (2–3 days)

- All 13 models plus `enums.py`, mapped to the **existing** tables:
  - polymorphic `User`
  - `Computed` `active_slot_id`
  - fetched DB defaults
  - domain methods ported from `Booking`, `Enrollment`, `Wallet`, `AvailabilitySlot`, `PTProfile`, `User`, `Attendance`, with identical messages
- Repositories, including the three `*_for_update` functions and the JPQL queries:
  - `findOverlapping`
  - `existsOverlappingBookingForStudent`
  - `findBookingsWithCancellation`
  - `sumAmountByPaymentTypeAndStatus`
  - `searchVerifiedPTs`
  - …
- **Exit:**
  - A schema-conformance test reflects the MySQL testcontainer (built from `init.sql`) and checks that every mapped column exists with a compatible type. This replaces `BackendApplicationTests`.
  - Pytest versions of `BookingTest` and `EnrollmentTest` pass.

### Phase 3 – Security and Auth module (2–3 days)

- `core/security.py` (JWT HS384 and bcrypt), `deps.py` (`get_optional_user`, `get_current_user`, `require_roles`), the 403 logger.
- Registration handlers, `AuthService` (register, login, me), `UserService`, and the routes `/auth/*` and `/users/*`.
- **Exit:**
  - A token issued by Java is accepted by FastAPI and the other way round.
  - Seeded users log in with `Password123!`.
  - The full RBAC matrix test passes (§4.3).
  - The golden master passes for endpoints 1–5.
  - Ports of `AuthControllerTest`, `AuthServiceTest`, `UserRegistrationHandlerTest`, `UserControllerTest`, `RoleBasedAccessControlTest` and `SecurityDenialLogTest` pass.

### Phase 4 – PT catalogue modules (3–4 days)

- PTProfile (public list with `lowestPrice`, public detail, active courses, available slots; PT get and update), PTCourse, PTSlot, `/student/dashboard`, AdminPT (pending, approve, reject), AdminUsers (list, filter, status).
- Endpoints 7–20 and 52–56.
- **Exit:** the golden master passes; ports of `PTControllerTest`, `PTCourseServiceTest`, `PTSlotServiceTest`, `AdminPTServiceTest` and `AdminControllerTest` pass.

### Phase 5 – Money core: Wallet, Enrollment, Contract PDF (3–4 days)

- WalletService:
  - `get_wallet`, `topup`
  - `process_course_purchase`, `process_booking_compensation`, `process_booking_penalty` (payment type `REFUND`)
  - `transactionRef` format
- EnrollmentService:
  - purchase rules
  - `contractUrl` two-step update
  - access check with the status captured in Phase 0
  - PT list
- ContractPdfGenerator (fpdf2): same sections, same ASCII static text, `PTC-HD-%06d`, price `"%,.0f VND"`, DejaVu font for dynamic names, cached file, regenerate when missing.
- Endpoints 30–36.
- **Exit:**
  - The golden master passes, including the DB diffs (wallet balance, payment rows).
  - The PDF test checks: it opens, contains the contract number, the names, the price and the transaction ref, and is generated in under 1s.
  - The port of `WalletServiceTest` passes.

### Phase 6 – Booking, cancellation, attendance, review (5–6 days; the riskiest phase)

- `policies/`, line by line from Java:
  - hours computation: `floor(minutes) / 60`, quantized, threshold `>= 24.00`
  - the student, PT and admin tables
  - the explanation strings, word for word, because the frontend shows `explanation`
- BookingService: create (TRIAL and PACKAGE), my/PT lists with cancellation info, detail, confirm, reject, student and PT cancel, preview, `execute_cancellation` (wallet effects plus the `cancellations` row).
- AttendanceService plus `InMemoryOtpStore`: start (15-minute window, LATE), student check-in, PT confirm, absent, get, `complete_session` (enrollment completion).
- ReviewService. The triggers update the rating; refresh the profile when it is read.
- Endpoints 21–29 and 43–51.
- **Exit:**
  - The golden master passes, including every policy branch at hours 23.99, 24.00 and 24.01 using the injected clock.
  - Ports of `CancellationPolicyTest` (8 rows), `BookingServiceTest`, `AttendanceServiceTest` and `ReviewServiceTest` pass.
  - The concurrency tests pass (§4.5).

### Phase 7 – Workout plans and admin analytics (2 days)

- WorkoutPlanService (create with the date defaults, add workout, list by enrollment and by PT, delete plan and workout) and AdminStatisticsService (statistics, booking and payment analytics, both the list and Page variants).
- Endpoints 37–42 and 57–60.
- **Exit:** the golden master passes for all 60 endpoints.

### Phase 8 – Parity hardening and end-to-end (4–5 days)

- Run the frontend against `backend-py` and do the full SC-01 to SC-16 walkthrough (§4.6), both automated and manual.
- Shadow run (§4.4): replay recorded frontend traffic against both backends and diff the results.
- Non-functional checks:
  - p95 latency per endpoint is no worse than Java on seed data
  - the contract PDF stays well under the 15s client timeout
  - memory and CPU with one worker
- Write the deviation register sign-off (§5) and the operator README.

### Phase 9 – Cutover and rollback (1 day plus a watch period)

1. Freeze changes to the Java backend.
2. `docker compose stop backend`, switch the `backend` service build to `./backend-py` (port 8080), then `docker compose up -d backend`.
   - No DB migration is needed. JWTs stay valid. The only loss is OTPs that are open at the moment of the switch: PTs re-open the session.
3. Smoke test: login for all 3 roles, the PT list, a booking, an OTP check-in, a contract download, admin statistics.
4. **Rollback:** switch `build` back to `./backend` and restart. The schema is unchanged, so this is safe at any time.
5. After 1–2 stable weeks, archive `backend/` and update the README tech stack.

### Phase 10 (optional, after parity) – Approved fixes

Apply the deviations approved in §5, one at a time. Each one needs a frontend check and an updated golden file.

---

## 4. Test strategy for 100% frontend compatibility

Testing has six layers. The golden master (4.2) is the main compatibility check. The other layers catch what it cannot reach: time-dependent rules, concurrency, and the real UI.

### 4.1 Unit tests (fast, no DB)

- Policies: the 8-row table from `CancellationPolicyTest`, plus boundary hours (0, 23.99, 24.00, slot in the past → 0), TRIAL vs PACKAGE, null fee → 0, and the explanation strings.
- Domain methods: Booking/Enrollment state transitions and their errors (`BookingTest`, `EnrollmentTest`); wallet debit vs `lockedBalance`, frozen wallet, `debitPenalty` going negative.
- Schemas:
  - every request DTO rejects each invalid field with the exact Java message
  - `SlotDateTime` accepts all four input forms
  - `PaymentMethodIn` maps leniently
  - Money and datetime serialize correctly
- JWT: round trip; decoding a fixed Java-issued token; an expired or tampered token → anonymous.

### 4.2 Golden-master contract tests (core gate)

- **Setup:** the same docker MySQL image is rebuilt for each run from `init.sql` + `trigger.sql` + `seed_demo.sql`, and the clock is pinned (`FAKE_NOW` env, read by `core/clock.py`).
  - The Java side needs a fixed time as well. Run it with `-Duser.timezone` and pick scenario data relative to the seed dates, or use libfaketime in the Java container.
- **Run:** replay every recorded request against FastAPI and compare, after normalization:
  - HTTP status
  - `Content-Type`
  - the JSON body: key set, value types, null vs present, enum strings, Vietnamese `message` byte for byte, list order
  - DB row diffs
- **Pass criterion:** a 100% match except for entries in the deviation register. The suite runs in CI on every PR to `backend-py`.

### 4.3 Security matrix test

Build the matrix from the §1.3 table: 60 endpoints × {anonymous, STUDENT, PT, ADMIN, invalid token, expired token}.

- Assert the status: 401 or 403 from the security layer, or "passes security".
- Assert the exact body for 401 and 403.
- Assert the `[ACCESS DENIED] user='…' endpoint='…'` log line (port of `SecurityDenialLogTest`).
- Include the oddities:
  - `/reviews/my` anonymous → 401 envelope from the service
  - `GET /pt-profiles/**` open
  - `/attendance/**` open to any role, with ownership enforced in the service

### 4.4 Shadow / dual-run (optional but cheap)

- Both backends share the DB schema and the JWT key, so a small replay script can capture the HTTP traffic of a manual frontend session (log it through a reverse proxy such as mitmproxy in front of Java).
- Replay the GETs against both backends live; replay the mutations against two cloned DBs. Diff with the 4.2 normalizer.
- This finds requests the scripted golden set missed.

### 4.5 Concurrency and transactional integrity

- 10 parallel `POST /bookings` for the same slot from different students: exactly one 201; the rest 409 with one of the two Java conflict messages; one slot BOOKED; sessions consumed exactly once.
- Parallel cancel of the same booking: one succeeds, the other gets 400 "đã được hủy trước đó"; the wallet is credited once.
- A failure injected after the wallet debit in purchase → full rollback (no enrollment row, no payment row, balance unchanged).
- Lazy loading or autoflush errors under the threadpool (run with `pytest-xdist` against the API).

### 4.6 Frontend end-to-end on the 16 business scenarios

- The scenario document `PTConnect_Scenario_Muc1.md` (SC-01 to SC-16, main flows plus exception flows) **is the acceptance test suite**. It uses the seed data accounts: `student.a@ptconnect.vn`, `pt.minhd@ptconnect.vn`, `admin@ptconnect.vn`, …
- Automate with Playwright against Streamlit (`http://localhost:8501`, `BACKEND_URL=http://backend-py:8080`). At minimum, assert the visible messages and table values the document lists, for example:
  - SC-02: the balance is 22.000.000 đ after a top-up of 2.000.000; the frozen-wallet message "Ví của bạn đang bị khóa, không thể giao dịch".
  - SC-04: cancelling < 24h shows "Hủy sát giờ < 24h…".
  - SC-06: the insufficient-balance flow, and "đang theo học khóa này".
  - SC-08: opening the OTP too early is rejected (15-minute rule); the full OTP check-in leads to COMPLETED.
  - SC-09, SC-10, SC-12: the validation messages ("Giá khóa học không được âm", "Số năm kinh nghiệm phải lớn hơn hoặc bằng 0", …).
  - SC-13, SC-14: approve/reject and suspend/unsuspend.
  - SC-15: the 4 KPI cards and 5 charts render, with no KeyError from missing `paymentType` or `status`.
  - SC-16: register then log in; a STUDENT is created ACTIVE with a 0 đ wallet.
- Run the same E2E suite once against Java to confirm the suite itself is correct, then against FastAPI.
- Keep `frontend/tests/test_frontend_auth.py` green.

### 4.7 Ported Java test suite (traceability)

| Java test | Python equivalent |
|---|---|
| `CancellationPolicyTest` | `tests/unit/test_policies.py` |
| `BookingTest`, `EnrollmentTest` | `tests/unit/test_domain_*.py` |
| `RoleBasedAccessControlTest`, `SecurityDenialLogTest` | `tests/integration/test_security_matrix.py` |
| `Auth/Admin/User/PTControllerTest` | `tests/integration/routes/test_*.py` |
| `*ServiceTest` (8 files) | `tests/integration/services/test_*.py` (real MySQL, not mocks, so the DB rules are exercised) |
| `UserRegistrationHandlerTest` | `tests/unit/test_registration_handlers.py` |
| `BackendApplicationTests` | `tests/integration/test_schema_conformance.py` |

### 4.8 Definition of done (cutover gate)

- [ ] The golden master matches 100% on all 60 endpoints, excluding approved deviations.
- [ ] The security matrix is 100% green.
- [ ] Every ported Java test passes; line coverage of `services/` and `policies/` is at least 90%.
- [ ] The concurrency tests are green over 20 repeated runs.
- [ ] Playwright SC-01 to SC-16 is green on FastAPI, and was green on Java with the same suite.
- [ ] Java-issued JWTs and seeded bcrypt passwords work.
- [ ] The rollback procedure has been rehearsed once.

---

## 5. Deviation register (decide before Phase 8)

The default is **keep** (bug-for-bug). The "Fix later" items go to Phase 10, after cutover, each with its own frontend check.

| ID | Java behaviour | Default | Note |
|---|---|---|---|
| D1 | Contract access denied returns a probable **500** (`AccessDeniedException` hits the catch-all) | Keep (confirm in Phase 0) → fix to 403 later | The frontend only shows the message. |
| D2 | Ownership failures use mixed codes: 400 for booking and attendance; 401 for course, slot, workout and attendance read | Keep | Changing them changes the `[4xx]` prefix in UI messages. |
| D3 | `createdAt` / `updatedAt` are `null` in create responses | **Improve** (refresh and return real values) | No frontend code reads them after a create. A null → value change is low risk. Record it as an allowed diff. |
| D4 | A suspended user with a valid token keeps access until the token expires | Keep → fix later | Security improvement. |
| D5 | Contract PDF uses Helvetica, so diacritics in names are lost | **Improve** (DejaVu font) | Static text stays ASCII and identical. |
| D6 | `cancel-preview` has no ownership check and labels unrelated users STUDENT | Keep → fix later | |
| D7 | OTPs are in memory (lost on restart, single instance only) | Keep in memory with 1 worker → Redis or a DB table later | |
| D8 | `deleteSlot` returns 500 when a slot has more than one historic booking (non-unique result) | Keep → fix later | |
| D9 | `hours_before_session decimal(5,2)` overflows for cancellations more than about 41 days ahead | Keep | A schema change is out of scope. |
| D10 | Course price 0 can be created but cannot be bought | Keep | |
| D11 | `getTransactionRefByEnrollmentId` takes the first payment in undefined order (could be COMP/PENALTY) | **Improve** (prefer `PURCHASE_PACKAGE`) | Only affects the ref printed on a regenerated PDF. |
| D12 | N+1 queries on the PT list and booking lists | **Improve** (eager loading) | Same output. |
| D13 | Money values are JSON numbers with 2 decimals in Java and 1 or more in Python (`500000.0`) | Accept | The frontend uses `float()`. |

---

## 6. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Hidden Spring defaults (the 401 body, framework error codes, Page JSON, Boot 4 vs 3 Jackson) | UI messages differ | Phase 0 captures them from the real running jar; nothing is assumed. |
| Time-dependent rules (24h, 15 minutes, OTP 30 minutes, slot in the past, contract expiry) | Flaky or wrong parity | A single injectable clock (`core/clock.py`), naive VN time everywhere, `TZ=Asia/Ho_Chi_Minh` in the container. |
| Pydantic defaults (Decimal as a string, `detail` errors, 422) | Frontend crashes or shows empty data | `CamelModel`, `Money` and the global handlers come first (Phase 1), with unit tests. |
| Transaction and lock semantics differ from JPA | Double booking, lost money | `with_for_update`, the same lock order, autoflush on, the concurrency suite (4.5). |
| The JWT algorithm or key derivation does not match | Every user is logged out at cutover; no shadow testing | Phase 3 interop test against a Java-issued token. |
| Multiple uvicorn workers | OTP check-in fails at random | Pin `--workers 1` until D7 is fixed. |
| Route order (`/bookings/my` vs `/bookings/{id}`) | "my" parsed as an id → 400 or 500 | A routing test for every static segment, plus the golden master. |
| Contract PDF is regenerated on every "My Courses" render | Slow page, timeouts | Cache the file on disk as Java does; measure generation time in tests. |

---

## Appendix A – Suggested library versions

`python 3.12`, `fastapi 0.115+`, `uvicorn[standard]`, `sqlalchemy 2.0.x`, `pymysql` + `cryptography` (MySQL 8 `caching_sha2_password`), `pydantic 2.x`, `pydantic-settings`, `pyjwt 2.x`, `bcrypt 4.x`, `fpdf2 2.7+`.

Tests: `pytest`, `pytest-xdist`, `httpx`, `testcontainers[mysql]`, `freezegun` (or the injected clock), `playwright`, `pypdf` (PDF content assertions).

## Appendix B – Example: one route end to end

```python
# app/api/v1/routes/bookings.py
router = APIRouter(prefix="/api/v1")

@router.get("/bookings/my")                       # declared BEFORE /bookings/{id}
def get_my_bookings(status: BookingStatus | None = None,
                    user: User = Depends(require_roles("STUDENT")),
                    svc: BookingService = Depends()):
    return ok("Lấy danh sách lịch tập của tôi thành công", svc.get_my_bookings(user.email, status))

@router.post("/bookings", status_code=201)
def create_booking(body: CreateBookingRequest,
                   user: User = Depends(require_roles("STUDENT")),
                   svc: BookingService = Depends()):
    return created("Đặt lịch ca tập thành công (chờ Huấn luyện viên phê duyệt)",
                   svc.create_booking(user.email, body))

@router.put("/pt/bookings/{id}/reject")
def reject_booking(id: int, body: RejectBookingRequestLoose | None = Body(None),
                   user: User = Depends(require_roles("PT")),
                   svc: BookingService = Depends()):
    body = body or RejectBookingRequestLoose(reason="Huấn luyện viên bận đột xuất")
    return ok("Đã từ chối đơn đặt lịch và hoàn lại buổi tập", svc.reject_booking(user.email, id, body))
```
