"""
PT-Connect: Bộ kiểm thử tích hợp tự động cho Milestone 6: Luồng Booking – Trái tim hệ thống
Phụ trách theo phân công: Thành & Thắng
Bao gồm:
  1. Student đặt slot AVAILABLE dạng PACKAGE (Output 1):
     - Giao dịch @Transactional
     - Bản ghi bookings trạng thái PENDING
     - Slot chuyển sang BOOKED
     - Enrollment remaining_sessions giảm đúng 1 buổi
  2. Student đặt lịch học thử TRIAL (Output 1):
     - Không cần enrollment_id
     - sessionFee = 0
     - Slot chuyển sang BOOKED
  3. Kiểm tra chặn học thử lần 2 với cùng PT:
     - Trả về 400 Bad Request
  4. Chặn đặt lịch với hợp đồng không hợp lệ (sai học viên / sai PT):
     - Trả về 400 Bad Request
  5. Chứng minh chống đặt trùng lịch (Output 4):
     - Hai request đồng thời vào cùng 1 slot qua ThreadPoolExecutor
     - Đúng 1 request thành công (201 Created)
     - Request còn lại nhận 409 Conflict
  6. PT Dashboard xem danh sách booking PENDING (Output 2):
     - GET /api/v1/pt/bookings?status=PENDING
  7. PT phê duyệt đơn đặt lịch Confirm (Output 3):
     - PUT /api/v1/pt/bookings/{id}/confirm -> 200 OK, status = CONFIRMED
  8. PT từ chối đơn đặt lịch Reject (Output 3):
     - PUT /api/v1/pt/bookings/{id}/reject -> 200 OK, status = CANCELLED
     - Slot tự động phục hồi về AVAILABLE
     - Hoàn lại 1 buổi tập vào enrollment.remaining_sessions
     - Ghi nhận bản ghi vào bảng cancellations
  9. Cập nhật ảnh đại diện người dùng Avatar (Output 5 - Hiệu):
     - PUT /api/v1/users/avatar cho Student và PT
     - Xác thực qua GET /api/v1/auth/me
  10. Kiểm tra phân quyền RBAC và bảo mật (Hưng):
     - Chặn Student gọi API của PT -> 403 Forbidden
     - Chặn người dùng chưa đăng nhập -> 401 Unauthorized
"""

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pytest
import requests

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8080").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
AUTH_ME_URL = f"{BASE_URL}/api/v1/auth/me"
USERS_AVATAR_URL = f"{BASE_URL}/api/v1/users/avatar"
PT_PROFILES_URL = f"{BASE_URL}/api/v1/pt-profiles"
PT_SLOTS_URL = f"{BASE_URL}/api/v1/pt/slots"
WALLET_TOPUP_URL = f"{BASE_URL}/api/v1/wallet/topup"
ENROLLMENTS_URL = f"{BASE_URL}/api/v1/enrollments"
MY_ENROLLMENTS_URL = f"{BASE_URL}/api/v1/enrollments/my"
BOOKINGS_URL = f"{BASE_URL}/api/v1/bookings"
MY_BOOKINGS_URL = f"{BASE_URL}/api/v1/bookings/my"
PT_BOOKINGS_URL = f"{BASE_URL}/api/v1/pt/bookings"

DEMO_PASSWORD = "Password123@"
STUDENT_DEMO_EMAIL = "student.a@ptconnect.vn"
PT_DEMO_EMAIL = "pt.hoangc@ptconnect.vn"


def generate_unique_credentials(role_prefix="student"):
    """Tạo thông tin định danh ngẫu nhiên."""
    unique_suffix = f"{int(time.time() * 1000) % 100000000}{uuid.uuid4().hex[:4]}"
    test_email = f"{role_prefix}_{unique_suffix}@ptconnect-m6.vn"
    test_phone = f"09{unique_suffix[-8:]}"
    return test_email, test_phone


def get_token(email: str, password: str = DEMO_PASSWORD) -> str:
    """Đăng nhập và lấy Bearer token."""
    res = requests.post(LOGIN_URL, json={"email": email, "password": password})
    if res.status_code != 200:
        pytest.fail(f"Không thể đăng nhập tài khoản {email}: {res.text}")
    return res.json()["data"]["token"]


def create_new_student_with_enrollment(pt_id: int, course_id: int, deposit_amount: float = 50000000.0):
    """
    Tạo học viên mới, nạp tiền vào ví và mua 1 khóa học
    để sở hữu hợp đồng tập luyện (Enrollment) hợp lệ.
    """
    email, phone = generate_unique_credentials("student")
    reg_payload = {
        "fullName": "Student Test M6",
        "email": email,
        "password": DEMO_PASSWORD,
        "phone": phone,
        "role": "STUDENT"
    }
    r = requests.post(REGISTER_URL, json=reg_payload)
    assert r.status_code == 201, f"Tạo student thất bại: {r.text}"
    token = r.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Nạp tiền vào ví
    topup_r = requests.post(WALLET_TOPUP_URL, json={"amount": deposit_amount, "paymentMethod": "BANK_TRANSFER"}, headers=headers)
    assert topup_r.status_code == 200, f"Nạp tiền ví thất bại: {topup_r.text}"

    # Mua khóa học
    buy_payload = {
        "courseId": course_id,
        "trainingLocation": "Cali Fitness Cầu Giấy",
        "paymentMethod": "WALLET"
    }
    enroll_r = requests.post(ENROLLMENTS_URL, json=buy_payload, headers=headers)
    assert enroll_r.status_code == 201, f"Mua khóa học thất bại: {enroll_r.text}"
    enrollment = enroll_r.json()["data"]

    return {
        "email": email,
        "token": token,
        "headers": headers,
        "enrollment": enrollment
    }


_base_day_offset = int(time.time()) % 3000 + 50
_slot_counter = 0


def create_future_pt_slot(pt_headers, hours_offset=None):
    """PT tạo một khung giờ trống (AVAILABLE) trong tương lai không bị chồng lấn."""
    global _slot_counter
    last_res = None
    for _ in range(20):
        _slot_counter += 1
        start_dt = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=_base_day_offset + _slot_counter, hours=9)
        end_dt = start_dt + timedelta(hours=1, minutes=30)

        payload = {
            "startTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "endTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S")
        }
        last_res = requests.post(PT_SLOTS_URL, json=payload, headers=pt_headers)
        if last_res.status_code == 201:
            return last_res.json()["data"]

    assert False, f"PT tạo slot thất bại sau nhiều lần thử: {last_res.text if last_res else 'No response'}"


class TestMilestone6BookingFlow:
    """Bộ kiểm thử tích hợp đầy đủ cho Milestone 6: Luồng Booking – Trái tim hệ thống."""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Khởi tạo tài nguyên kiểm thử."""
        self.pt_token = get_token(PT_DEMO_EMAIL)
        self.pt_headers = {"Authorization": f"Bearer {self.pt_token}"}

        # Lấy thông tin PT Profile và khóa học đầu tiên
        r_pt = requests.get(f"{BASE_URL}/api/v1/pt/profile", headers=self.pt_headers)
        assert r_pt.status_code == 200
        self.pt_profile = r_pt.json()["data"]
        self.pt_id = self.pt_profile["id"]

        r_courses = requests.get(f"{BASE_URL}/api/v1/pt/courses", headers=self.pt_headers)
        assert r_courses.status_code == 200
        courses = r_courses.json()["data"]
        assert len(courses) > 0, "PT cần có ít nhất 1 khóa học mẫu"
        self.course = courses[0]
        self.course_id = self.course["id"]

    def test_01_create_package_booking_success(self):
        """
        Output 1: POST /api/v1/bookings chạy thành công khối @Transactional:
        - Tạo bản ghi bookings trạng thái PENDING
        - Slot chuyển thành BOOKED
        - Enrollment remaining_sessions giảm đúng 1 buổi
        """
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)
        enrollment_id = student_data["enrollment"]["id"]
        initial_remaining = student_data["enrollment"]["remainingSessions"]

        # PT tạo 1 slot trống
        slot = create_future_pt_slot(self.pt_headers, hours_offset=50)
        slot_id = slot["id"]

        # Học viên đặt lịch PACKAGE
        book_payload = {
            "slotId": slot_id,
            "bookingType": "PACKAGE",
            "enrollmentId": enrollment_id,
            "studentNote": "Muốn tập trung vào bài Squat và Core"
        }
        res = requests.post(BOOKINGS_URL, json=book_payload, headers=student_data["headers"])
        assert res.status_code == 201, f"Đặt lịch PACKAGE thất bại: {res.text}"
        data = res.json()["data"]

        # 1. Kiểm tra đơn đặt lịch
        assert data["id"] is not None
        assert data["status"] == "PENDING", "Booking mới phải ở trạng thái PENDING"
        assert data["bookingType"] == "PACKAGE"
        assert data["slotId"] == slot_id
        assert data["enrollmentId"] == enrollment_id
        assert data["studentNote"] == "Muốn tập trung vào bài Squat và Core"

        # 2. Kiểm tra slot đã chuyển sang BOOKED
        res_slots = requests.get(f"{PT_PROFILES_URL}/{self.pt_id}/slots", headers=student_data["headers"])
        available_slots = res_slots.json()["data"]
        assert not any(s["id"] == slot_id for s in available_slots), "Slot đã BOOKED không được xuất hiện trong danh sách AVAILABLE"

        # 3. Kiểm tra số buổi trong hợp đồng bị giảm đúng 1
        res_my_enrolls = requests.get(MY_ENROLLMENTS_URL, headers=student_data["headers"])
        my_enrolls = res_my_enrolls.json()["data"]
        target_enroll = next(e for e in my_enrolls if e["id"] == enrollment_id)
        assert target_enroll["remainingSessions"] == initial_remaining - 1, "remaining_sessions phải giảm đúng 1"

    def test_02_create_trial_booking_success(self):
        """
        Output 1 (TRIAL): Học viên đặt lịch học thử:
        - Không cần enrollment_id
        - sessionFee = 0
        - Trạng thái PENDING, slot chuyển thành BOOKED
        """
        email, phone = generate_unique_credentials("student_trial")
        r = requests.post(REGISTER_URL, json={
            "fullName": "Student Trial Test",
            "email": email,
            "password": DEMO_PASSWORD,
            "phone": phone,
            "role": "STUDENT"
        })
        token = r.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        slot = create_future_pt_slot(self.pt_headers, hours_offset=52)
        slot_id = slot["id"]

        trial_payload = {
            "slotId": slot_id,
            "bookingType": "TRIAL",
            "studentNote": "Tôi muốn học thử buổi đầu tiên"
        }
        res = requests.post(BOOKINGS_URL, json=trial_payload, headers=headers)
        assert res.status_code == 201, f"Đặt lịch TRIAL thất bại: {res.text}"
        data = res.json()["data"]

        assert data["bookingType"] == "TRIAL"
        assert data["status"] == "PENDING"
        assert float(data["sessionFee"]) == 0.0, "Buổi học thử có học phí 0 đ"
        assert data["enrollmentId"] is None

    def test_03_trial_booking_second_time_rejected(self):
        """
        Kiểm tra nghiệp vụ: Mỗi học viên chỉ được học thử 1 lần với mỗi PT.
        Lần 2 sẽ bị từ chối 400 Bad Request.
        """
        email, phone = generate_unique_credentials("student_trial_dup")
        r = requests.post(REGISTER_URL, json={
            "fullName": "Student Trial Dup",
            "email": email,
            "password": DEMO_PASSWORD,
            "phone": phone,
            "role": "STUDENT"
        })
        token = r.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Lần 1: Thành công
        slot1 = create_future_pt_slot(self.pt_headers, hours_offset=55)
        res1 = requests.post(BOOKINGS_URL, json={"slotId": slot1["id"], "bookingType": "TRIAL"}, headers=headers)
        assert res1.status_code == 201

        # Lần 2: Thất bại với cùng PT
        slot2 = create_future_pt_slot(self.pt_headers, hours_offset=56)
        res2 = requests.post(BOOKINGS_URL, json={"slotId": slot2["id"], "bookingType": "TRIAL"}, headers=headers)
        assert res2.status_code == 400, f"Học thử lần 2 phải bị từ chối 400: {res2.text}"
        assert "học thử 1 lần" in res2.json()["message"]

    def test_04_booking_with_invalid_enrollment_rejected(self):
        """Kiểm tra ngoại lệ: Đặt lịch với hợp đồng không thuộc về mình -> 400 Bad Request."""
        st1 = create_new_student_with_enrollment(self.pt_id, self.course_id)
        st2 = create_new_student_with_enrollment(self.pt_id, self.course_id)

        slot = create_future_pt_slot(self.pt_headers, hours_offset=58)

        # st1 dùng hợp đồng của st2
        hack_payload = {
            "slotId": slot["id"],
            "bookingType": "PACKAGE",
            "enrollmentId": st2["enrollment"]["id"]
        }
        res = requests.post(BOOKINGS_URL, json=hack_payload, headers=st1["headers"])
        assert res.status_code == 400
        assert "không thuộc về bạn" in res.json()["message"]

    def test_05_concurrent_double_booking_anti_conflict_proof(self):
        """
        Output 4: Chứng minh chống đặt trùng:
        Hai request cùng lúc vào 1 slot, chỉ một request thành công (201 Created),
        request còn lại nhận 409 Conflict.
        """
        st_a = create_new_student_with_enrollment(self.pt_id, self.course_id)
        st_b = create_new_student_with_enrollment(self.pt_id, self.course_id)

        target_slot = create_future_pt_slot(self.pt_headers, hours_offset=60)
        target_slot_id = target_slot["id"]

        def attempt_book(student_data):
            payload = {
                "slotId": target_slot_id,
                "bookingType": "PACKAGE",
                "enrollmentId": student_data["enrollment"]["id"],
                "studentNote": f"Concurrent booking by {student_data['email']}"
            }
            return requests.post(BOOKINGS_URL, json=payload, headers=student_data["headers"])

        # Bắn 2 request đồng thời vào 1 slot duy nhất
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(attempt_book, st_a)
            future_b = executor.submit(attempt_book, st_b)

            res_a = future_a.result()
            res_b = future_b.result()

        status_codes = [res_a.status_code, res_b.status_code]

        # Kiểm chứng: Phải có đúng 1 mã 201 (Thành công) và 1 mã 409 (Conflict)
        assert 201 in status_codes, f"Phải có 1 request thành công 201: {status_codes}"
        assert 409 in status_codes, f"Request còn lại phải nhận 409 Conflict chống đặt trùng: {status_codes}"

    def test_06_pt_view_pending_bookings(self):
        """
        Output 2: Giao diện PT Dashboard hiển thị danh sách booking đang PENDING.
        GET /api/v1/pt/bookings?status=PENDING
        """
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)
        slot = create_future_pt_slot(self.pt_headers, hours_offset=62)

        # Học viên đặt lịch
        r_book = requests.post(BOOKINGS_URL, json={
            "slotId": slot["id"],
            "bookingType": "PACKAGE",
            "enrollmentId": student_data["enrollment"]["id"]
        }, headers=student_data["headers"])
        assert r_book.status_code == 201
        created_booking_id = r_book.json()["data"]["id"]

        # PT lấy danh sách booking PENDING
        res_pt = requests.get(f"{PT_BOOKINGS_URL}?status=PENDING", headers=self.pt_headers)
        assert res_pt.status_code == 200
        pending_list = res_pt.json()["data"]
        assert isinstance(pending_list, list)

        # Kiểm tra booking vừa tạo có trong danh sách và đầy đủ thông tin ghép
        matched = next((b for b in pending_list if b["id"] == created_booking_id), None)
        assert matched is not None, "Booking vừa tạo phải xuất hiện trong danh sách PENDING của PT"
        assert matched["studentName"] is not None
        assert matched["studentPhone"] is not None
        assert matched["status"] == "PENDING"
        assert matched["courseTitle"] == self.course["title"]

    def test_07_pt_confirm_booking_success(self):
        """
        Output 3 (Confirm): PT bấm Confirm -> booking CONFIRMED.
        PUT /api/v1/pt/bookings/{id}/confirm
        """
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)
        slot = create_future_pt_slot(self.pt_headers, hours_offset=64)

        r_book = requests.post(BOOKINGS_URL, json={
            "slotId": slot["id"],
            "bookingType": "PACKAGE",
            "enrollmentId": student_data["enrollment"]["id"]
        }, headers=student_data["headers"])
        booking_id = r_book.json()["data"]["id"]

        # PT Confirm
        res_confirm = requests.put(f"{PT_BOOKINGS_URL}/{booking_id}/confirm", headers=self.pt_headers)
        assert res_confirm.status_code == 200, f"PT confirm thất bại: {res_confirm.text}"
        data = res_confirm.json()["data"]
        assert data["id"] == booking_id
        assert data["status"] == "CONFIRMED"

        # Học viên kiểm tra lại qua GET /bookings/my
        res_my = requests.get(MY_BOOKINGS_URL, headers=student_data["headers"])
        my_list = res_my.json()["data"]
        my_booking = next(b for b in my_list if b["id"] == booking_id)
        assert my_booking["status"] == "CONFIRMED"

    def test_08_pt_reject_booking_and_restore_session_and_slot(self):
        """
        Output 3 (Reject): PT bấm Reject:
        - Booking thành CANCELLED
        - Slot tự động về AVAILABLE
        - remaining_sessions được hoàn lại cho học viên
        - Có bản ghi cancellations kèm lý do
        """
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)
        enrollment_id = student_data["enrollment"]["id"]
        initial_remaining = student_data["enrollment"]["remainingSessions"]

        slot = create_future_pt_slot(self.pt_headers, hours_offset=66)
        slot_id = slot["id"]

        # Đặt lịch: remainingSessions giảm 1
        r_book = requests.post(BOOKINGS_URL, json={
            "slotId": slot_id,
            "bookingType": "PACKAGE",
            "enrollmentId": enrollment_id
        }, headers=student_data["headers"])
        booking_id = r_book.json()["data"]["id"]

        # PT Reject kèm lý do
        reject_reason = "PT có lịch tập huấn đột xuất của Liên đoàn Thể hình"
        res_reject = requests.put(
            f"{PT_BOOKINGS_URL}/{booking_id}/reject",
            json={"reason": reject_reason},
            headers=self.pt_headers
        )
        assert res_reject.status_code == 200, f"PT reject thất bại: {res_reject.text}"
        data = res_reject.json()["data"]

        # 1. Booking chuyển sang CANCELLED
        assert data["id"] == booking_id
        assert data["status"] == "CANCELLED"
        assert data["cancellationReason"] == reject_reason
        assert data["cancelledByRole"] == "PT"

        # 2. Slot tự động trả về AVAILABLE (xuất hiện lại trong GET /slots)
        res_slots = requests.get(f"{PT_PROFILES_URL}/{self.pt_id}/slots", headers=student_data["headers"])
        avail_slots = res_slots.json()["data"]
        assert any(s["id"] == slot_id for s in avail_slots), "Slot phải tự động phục hồi về AVAILABLE sau khi bị Reject"

        # 3. remaining_sessions được hoàn lại
        res_my_enrolls = requests.get(MY_ENROLLMENTS_URL, headers=student_data["headers"])
        target_enroll = next(e for e in res_my_enrolls.json()["data"] if e["id"] == enrollment_id)
        assert target_enroll["remainingSessions"] == initial_remaining, "remaining_sessions phải được hoàn lại nguyên vẹn"

    def test_09_user_avatar_update_student_and_pt(self):
        """
        Output 5 (Avatar - Hiệu):
        Học viên và PT cập nhật ảnh đại diện thành công qua PUT /api/v1/users/avatar
        Hiển thị chuẩn xác trên hồ sơ GET /api/v1/auth/me
        """
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)
        new_student_avatar = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=400"

        # 1. Student đổi Avatar
        res_stu_av = requests.put(
            USERS_AVATAR_URL,
            json={"avatarUrl": new_student_avatar},
            headers=student_data["headers"]
        )
        assert res_stu_av.status_code == 200, f"Cập nhật avatar student thất bại: {res_stu_av.text}"
        assert res_stu_av.json()["data"]["avatarUrl"] == new_student_avatar

        # Kiểm tra GET /auth/me của Student
        me_stu = requests.get(AUTH_ME_URL, headers=student_data["headers"]).json()["data"]
        assert me_stu["avatarUrl"] == new_student_avatar

        # 2. PT đổi Avatar
        new_pt_avatar = "https://images.unsplash.com/photo-1567013127542-490d757e51fc?w=400"
        res_pt_av = requests.put(
            USERS_AVATAR_URL,
            json={"avatarUrl": new_pt_avatar},
            headers=self.pt_headers
        )
        assert res_pt_av.status_code == 200, f"Cập nhật avatar PT thất bại: {res_pt_av.text}"
        assert res_pt_av.json()["data"]["avatarUrl"] == new_pt_avatar

        # Kiểm tra GET /auth/me của PT
        me_pt = requests.get(AUTH_ME_URL, headers=self.pt_headers).json()["data"]
        assert me_pt["avatarUrl"] == new_pt_avatar

    def test_10_security_rbac_booking_endpoints(self):
        """Kiểm tra ma trận phân quyền RBAC và chống truy cập trái phép."""
        student_data = create_new_student_with_enrollment(self.pt_id, self.course_id)

        # 1. Student cố tình gọi API Confirm của PT -> 403 Forbidden
        res_hack_confirm = requests.put(f"{PT_BOOKINGS_URL}/1/confirm", headers=student_data["headers"])
        assert res_hack_confirm.status_code == 403, "Student không được gọi API PT"

        # 2. Không có token gọi POST /bookings -> 401 Unauthorized
        res_unauth_book = requests.post(BOOKINGS_URL, json={"slotId": 1})
        assert res_unauth_book.status_code == 401

        # 3. Không có token gọi PUT /users/avatar -> 401 Unauthorized
        res_unauth_av = requests.put(USERS_AVATAR_URL, json={"avatarUrl": "https://example.com/a.jpg"})
        assert res_unauth_av.status_code == 401
