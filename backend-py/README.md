# PT-Connect Backend (Python FastAPI)

This repository contains the complete 1:1 migration of the PT-Connect backend from Java 17 Spring Boot to Python 3.12 FastAPI.

## Architecture

- **Web Framework:** FastAPI (with `redirect_slashes=False`)
- **ORM & Database:** SQLAlchemy 2.0 (mapped models matching MySQL `database/init.sql`)
- **Driver:** PyMySQL + Cryptography
- **Security:** PyJWT (HS384 matching JJWT key derivation), BCrypt (passwords `$2a$` and `$2b$`)
- **Validation & Serialization:** Pydantic 2 with `CamelModel` for automatic camelCase wire compatibility and `Money` float serialization
- **PDF Generation:** FPDF2 with UTF-8 DejaVu Sans font for personal training contracts
- **OTP Store:** `InMemoryOtpStore` with thread lock and 30-minute expiration

## All 60 Endpoints Implemented

1. **Auth & Profile (1–6):**
   - `POST /api/v1/auth/register`
   - `POST /api/v1/auth/login`
   - `GET /api/v1/auth/me`
   - `GET /api/v1/users/{id}`
   - `PUT /api/v1/users/avatar`
   - `GET /api/v1/public/health`
2. **Student & PT Catalogue (7–20):**
   - `GET /api/v1/student/dashboard`
   - `GET /api/v1/pt-profiles?name=`
   - `GET /api/v1/pt-profiles/{id}`
   - `GET /api/v1/pt-profiles/{id}/courses`
   - `GET /api/v1/pt-profiles/{id}/slots`
   - `GET /api/v1/pt/profile`
   - `PUT /api/v1/pt/profile`
   - `POST /api/v1/pt/courses`
   - `GET /api/v1/pt/courses`
   - `PUT /api/v1/pt/courses/{id}`
   - `DELETE /api/v1/pt/courses/{id}`
   - `POST /api/v1/pt/slots`
   - `GET /api/v1/pt/slots`
   - `DELETE /api/v1/pt/slots/{id}`
3. **Bookings (21–29):**
   - `POST /api/v1/bookings`
   - `GET /api/v1/bookings/my?status=`
   - `GET /api/v1/bookings/{id}`
   - `PUT /api/v1/bookings/{id}/cancel`
   - `GET /api/v1/bookings/{id}/cancel-preview`
   - `GET /api/v1/pt/bookings?status=`
   - `PUT /api/v1/pt/bookings/{id}/confirm`
   - `PUT /api/v1/pt/bookings/{id}/reject`
   - `PUT /api/v1/pt/bookings/{id}/cancel`
4. **Wallet & Enrollments (30–36):**
   - `GET /api/v1/wallet`
   - `POST /api/v1/wallet/topup`
   - `POST /api/v1/enrollments`
   - `GET /api/v1/enrollments/my`
   - `GET /api/v1/enrollments/{id}`
   - `GET /api/v1/enrollments/{id}/contract`
   - `GET /api/v1/pt/enrollments`
5. **Workout Plans (37–42):**
   - `POST /api/v1/pt/workout-plans`
   - `POST /api/v1/pt/workout-plans/{id}/workouts`
   - `GET /api/v1/enrollments/{id}/workout-plans`
   - `GET /api/v1/pt/workout-plans`
   - `DELETE /api/v1/pt/workout-plans/{id}`
   - `DELETE /api/v1/pt/workout-plans/{planId}/workouts/{workoutId}`
6. **Attendance & Reviews (43–51):**
   - `POST /api/v1/attendance/{bookingId}/start`
   - `POST /api/v1/attendance/{bookingId}/student-checkin`
   - `POST /api/v1/attendance/{bookingId}/pt-confirm`
   - `POST /api/v1/attendance/{bookingId}/absent?reason=`
   - `GET /api/v1/attendance/{bookingId}`
   - `POST /api/v1/reviews`
   - `GET /api/v1/reviews/pt/{ptId}`
   - `GET /api/v1/reviews/my`
   - `GET /api/v1/reviews/booking/{bookingId}`
7. **Admin Management & Analytics (52–60):**
   - `GET /api/v1/admin/users?role=`
   - `PUT /api/v1/admin/users/{id}/status`
   - `GET /api/v1/admin/pt/pending`
   - `PUT /api/v1/admin/pt/{id}/approve`
   - `PUT /api/v1/admin/pt/{id}/reject`
   - `GET /api/v1/admin/statistics`
   - `GET /api/v1/admin/bookings`
   - `GET /api/v1/admin/bookings/page`
   - `GET /api/v1/admin/payments`
   - `GET /api/v1/admin/payments/page`

## Running Tests

```bash
pytest -v
```

## Running Linter

```bash
ruff check .
```
