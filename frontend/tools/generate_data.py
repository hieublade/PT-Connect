#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sinh dữ liệu mẫu hợp lệ cho nền tảng PT Connect (Milestone 8 - Output 4).
Tuân thủ toàn bộ các ràng buộc CHECK, UNIQUE, FK và Trigger trong database/init.sql.

Dữ liệu sinh ra:
- 1 Quản trị viên (ADMIN)
- ~8 Huấn luyện viên (PT) với các trạng thái khác nhau (VERIFIED, PENDING, REJECTED)
- ~30 Học viên (STUDENT) với ví tiền và số dư hợp lệ
- ~15 Khóa học huấn luyện
- ~180 Khung giờ rảnh (Availability Slots) trải đều 3 tháng
- ~35 Hợp đồng khóa học (Enrollments)
- ~150 Ca đặt lịch (Bookings) với đầy đủ trạng thái (COMPLETED, CONFIRMED, PENDING, CANCELLED)
- Reviews gắn với ca tập hoàn thành (Trigger tự tính average_rating)
- Cancellations ghi nhận lý do và chính sách đền bù
- Payments (Giao dịch Nạp ví & Mua khóa học)
- Workout Plans & Workouts (Giáo án & Bài tập)

Mật khẩu mặc định của toàn bộ tài khoản demo: Password123!
"""

import os
import sys
import random
from datetime import datetime, timedelta
import bcrypt
from faker import Faker

# Khắc phục lỗi hiển thị tiếng Việt trên console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cố định Seed để đảm bảo kết quả sinh dữ liệu tái lập được nhiều lần
SEED = 42
random.seed(SEED)
fake = Faker("vi_VN")
fake.seed_instance(SEED)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "database", "seed_demo.sql")


def escape_sql(val):
    """Xử lý ký tự đặc biệt khi format chuỗi SQL."""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "1" if val else "0"
    s = str(val).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def main():
    print(f"🚀 Bắt đầu sinh dữ liệu mẫu PT Connect (Seed: {SEED})...")

    # Sinh mã băm mật khẩu chuẩn BCrypt cho "Password123@" (Khớp hoàn toàn với giao diện Đăng nhập nhanh)
    password_plain = "Password123@"
    password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt(10)).decode("utf-8")
    print(f"🔑 Mật khẩu mặc định: '{password_plain}' -> BCrypt: {password_hash}")

    sql_lines = []
    sql_lines.append("-- =====================================================================")
    sql_lines.append("-- DỮ LIỆU MẪU CHẠY DEMO HỆ THỐNG PT CONNECT (Milestone 8 - Data Generator)")
    sql_lines.append(f"-- Sinh tự động ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Seed: {SEED})")
    sql_lines.append("-- Mật khẩu đăng nhập mặc định cho TẤT CẢ tài khoản: Password123@")
    sql_lines.append("-- =====================================================================")
    sql_lines.append("USE ptconnect;")
    sql_lines.append("SET NAMES utf8mb4;")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_lines.append("")
    sql_lines.append("-- XÓA DỮ LIỆU CŨ ĐỂ ĐẢM BẢO TÍNH TOÀN VẸN KHI CHẠY LẠI DEMO")
    sql_lines.append("TRUNCATE TABLE `attendance`;")
    sql_lines.append("TRUNCATE TABLE `cancellations`;")
    sql_lines.append("TRUNCATE TABLE `reviews`;")
    sql_lines.append("TRUNCATE TABLE `workouts`;")
    sql_lines.append("TRUNCATE TABLE `workout_plans`;")
    sql_lines.append("TRUNCATE TABLE `bookings`;")
    sql_lines.append("TRUNCATE TABLE `availability_slots`;")
    sql_lines.append("TRUNCATE TABLE `payments`;")
    sql_lines.append("TRUNCATE TABLE `enrollments`;")
    sql_lines.append("TRUNCATE TABLE `courses`;")
    sql_lines.append("TRUNCATE TABLE `wallets`;")
    sql_lines.append("TRUNCATE TABLE `pt_profiles`;")
    sql_lines.append("TRUNCATE TABLE `users`;")
    sql_lines.append("")

    # 1. USERS & WALLETS & PT PROFILES
    users = []
    wallets = []
    pt_profiles = []

    user_id_seq = 1

    # 1.1 Admin
    users.append({
        "id": user_id_seq,
        "full_name": "Quản Trị Viên Hệ Thống",
        "email": "admin@ptconnect.vn",
        "password_hash": password_hash,
        "phone": "0900000000",
        "role": "ADMIN",
        "status": "ACTIVE",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=AdminSystem"
    })
    wallets.append({"id": user_id_seq, "user_id": user_id_seq, "balance": 0.0, "locked_balance": 0.0})
    user_id_seq += 1

    # 1.2 8 Huấn luyện viên (PT)
    pt_data_configs = [
        ("Lê Hoàng Cường", "pt.hoangc@ptconnect.vn", "0900000003", 6, "VERIFIED", "ACTIVE",
         "HLV Thể hình chuyên nghiệp & Giảm mỡ chuyên sâu", "Phòng Cali Cầu Giấy; FitZone Thanh Xuân", "Dạy tại nhà phụ thu 20% tiền đi lại"),
        ("Phạm Minh Dũng", "pt.minhd@ptconnect.vn", "0900000004", 4, "VERIFIED", "ACTIVE",
         "Chuyên gia Calisthenics và Phục hồi cơ xương khớp", "Studio cá nhân tại Thanh Xuân; Khu vực Đống Đa", "Khác địa điểm thỏa thuận thêm phí"),
        ("Trần Quốc Bảo", "pt.quocbao@ptconnect.vn", "0900000005", 5, "VERIFIED", "ACTIVE",
         "Cựu vận động viên điền kinh, chuyên Kickboxing & Cardio", "Phòng tập Elite Fitness Tây Hồ; Cầu Giấy", "Giá chuẩn theo hợp đồng"),
        ("Nguyễn Thu Hà", "pt.thuha@ptconnect.vn", "0900000006", 3, "VERIFIED", "ACTIVE",
         "Chuyên gia Yoga & Pilates chỉnh dáng nữ giới", "Phòng tập Yoga Plus Ba Đình; Cầu Giấy", "Kèm tại nhà phụ thu 50k/buổi"),
        ("Đỗ Tuấn Kiệt", "pt.tuankiet@ptconnect.vn", "0900000007", 7, "VERIFIED", "ACTIVE",
         "Master Trainer Powerlifting, tăng cơ hypertrophy", "Fit24 Hai Bà Trưng; Times City", "Không phụ thu địa điểm chỉ định"),
        ("Vũ Hoàng Nam", "pt.hoangnam@ptconnect.vn", "0900000008", 2, "PENDING", "PENDING",
         "HLV Fitness trẻ nhiệt huyết, chuyên giảm cân cấp tốc", "Khu vực Hoàng Mai; Hà Đông", "Chờ ban quản trị xét duyệt hồ sơ"),
        ("Đặng Thúy Nga", "pt.thuynga@ptconnect.vn", "0900000009", 1, "PENDING", "PENDING",
         "Huấn luyện viên Aerobic & Group X năng động", "Khu vực Nam Từ Liêm", "Chờ kiểm tra bằng cấp"),
        ("Bùi Văn Quyết", "pt.vanquyet@ptconnect.vn", "0900000010", 3, "REJECTED", "SUSPENDED",
         "Hồ sơ chứng chỉ chưa đạt chuẩn theo quy định hệ thống", "Khu vực Bắc Từ Liêm", "Tài khoản bị tạm ngưng"),
    ]

    pt_id_seq = 1
    pt_profile_map = {}  # pt_id -> pt dict

    for name, email, phone, exp, verif, status, bio, locs, note in pt_data_configs:
        u_id = user_id_seq
        user_id_seq += 1

        users.append({
            "id": u_id,
            "full_name": name,
            "email": email,
            "password_hash": password_hash,
            "phone": phone,
            "role": "PT",
            "status": status,
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"
        })
        wallets.append({"id": u_id, "user_id": u_id, "balance": 0.0, "locked_balance": 0.0})

        pt_profile = {
            "id": pt_id_seq,
            "user_id": u_id,
            "experience_years": exp,
            "available_locations": locs,
            "location_pricing_note": note,
            "certificate_urls": '["https://storage.ptconnect.vn/certs/cert_nasam.jpg", "https://storage.ptconnect.vn/certs/cert_firstaid.jpg"]',
            "average_rating": 0.0,  # Sẽ được cập nhật tự động bởi trigger khi có reviews
            "total_reviews": 0,
            "verification_status": verif,
            "name": name,
            "active": (verif == "VERIFIED" and status == "ACTIVE")
        }
        pt_profiles.append(pt_profile)
        pt_profile_map[pt_id_seq] = pt_profile
        pt_id_seq += 1

    # 1.3 30 Học viên (STUDENT)
    student_users = []
    for i in range(1, 31):
        u_id = user_id_seq
        user_id_seq += 1
        if i == 1:
            s_name = "Nguyễn Văn A"
            s_email = "student.a@ptconnect.vn"
            s_phone = "0900000001"
        else:
            s_name = fake.name()
            s_email = f"student_{i:02d}@ptconnect.vn"
            s_phone = f"091{i:07d}"

        # Số dư ví ngẫu nhiên từ 3 triệu đến 25 triệu VND
        balance = float(random.choice([3000000, 5000000, 8000000, 12000000, 15000000, 20000000, 25000000]))

        u_data = {
            "id": u_id,
            "full_name": s_name,
            "email": s_email,
            "password_hash": password_hash,
            "phone": s_phone,
            "role": "STUDENT",
            "status": "ACTIVE",
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed=student_{i}"
        }
        users.append(u_data)
        student_users.append(u_data)
        wallets.append({"id": u_id, "user_id": u_id, "balance": balance, "locked_balance": 0.0})

    # 2. COURSES (Khóa học của các PT đã VERIFIED & ACTIVE)
    active_pts = [p for p in pt_profiles if p["active"]]
    courses = []
    course_id_seq = 1

    course_templates = [
        ("Gói Giảm Mỡ Chuyên Sâu 12 Tuần", "Lộ trình đốt mỡ toàn diện kết hợp dinh dưỡng macro", 36, 90, 10800000.0),
        ("Gói Tăng Cơ Thể Hình 24 Buổi", "Tăng kích thước sợi cơ Hypertrophy & cải thiện form tạ", 24, 60, 7200000.0),
        ("Khóa Khởi Động Nhập Môn 12 Buổi", "Dành cho người mới bắt đầu làm quen với phòng gym và thể lực nền tảng", 12, 30, 3600000.0),
        ("Gói Pilates Chỉnh Dáng & Cột Sống", "Cải thiện tư thế lưng gù, cổ rùa và thon gọn eo bụng", 20, 60, 8000000.0),
        ("Gói Boxing Thể Lực & Xả Stress", "Luyện tập phản xạ tốc độ cao, đốt calo tối đa mỗi buổi tập", 16, 45, 5600000.0)
    ]

    for pt in active_pts:
        # Mỗi PT mở từ 2 - 3 khóa học
        selected_templates = random.sample(course_templates, k=random.randint(2, 3))
        for t_title, t_desc, t_sessions, t_validity, t_price in selected_templates:
            courses.append({
                "id": course_id_seq,
                "pt_id": pt["id"],
                "title": f"{t_title} - HLV {pt['name'].split()[-1]}",
                "description": t_desc,
                "total_sessions": t_sessions,
                "validity_days": t_validity,
                "base_price": t_price,
                "status": "ACTIVE"
            })
            course_id_seq += 1

    # 3. ENROLLMENTS & PAYMENTS (Hợp đồng mua khóa & Giao dịch tài chính)
    enrollments = []
    payments = []
    enrollment_id_seq = 1
    payment_id_seq = 1

    # Mỗi học viên mua từ 1 đến 2 hợp đồng khóa học
    for student in student_users[:25]:
        chosen_courses = random.sample(courses, k=random.choice([1, 1, 2]))
        for crs in chosen_courses:
            e_id = enrollment_id_seq
            enrollment_id_seq += 1

            start_d = datetime(2026, 8, 1) + timedelta(days=random.randint(0, 60))
            end_d = start_d + timedelta(days=crs["validity_days"])

            price = crs["base_price"]
            tot_sessions = crs["total_sessions"]

            enrollments.append({
                "id": e_id,
                "student_id": student["id"],
                "course_id": crs["id"],
                "pt_id": crs["pt_id"],
                "training_location": random.choice(["Cali Fitness Cầu Giấy", "FitZone Thanh Xuân", "Elite Fitness Tây Hồ", "Tập tại nhà học viên"]),
                "final_price": price,
                "total_sessions": tot_sessions,
                "remaining_sessions": tot_sessions,  # Sẽ trừ dần sau khi xếp booking
                "start_date": start_d.strftime("%Y-%m-%d"),
                "end_date": end_d.strftime("%Y-%m-%d"),
                "contract_url": f"https://storage.ptconnect.vn/contracts/ptc_hd_{e_id:06d}.pdf",
                "status": "ACTIVE"
            })

            # Thanh toán TOPUP trước khi mua
            wallet_id = student["id"]  # id ví khớp id user
            payments.append({
                "id": payment_id_seq,
                "wallet_id": wallet_id,
                "enrollment_id": None,
                "amount": price + 2000000.0,
                "payment_type": "TOPUP",
                "payment_method": "BANK_TRANSFER",
                "status": "SUCCESS",
                "transaction_ref": f"TXN_TOPUP_{datetime.now().year}_{payment_id_seq:05d}",
                "created_at": (start_d - timedelta(days=1)).strftime("%Y-%m-%d 10:00:00")
            })
            payment_id_seq += 1

            # Thanh toán PURCHASE_PACKAGE
            payments.append({
                "id": payment_id_seq,
                "wallet_id": wallet_id,
                "enrollment_id": e_id,
                "amount": price,
                "payment_type": "PURCHASE_PACKAGE",
                "payment_method": "WALLET",
                "status": "SUCCESS",
                "transaction_ref": f"TXN_BUY_{datetime.now().year}_{payment_id_seq:05d}",
                "created_at": start_d.strftime("%Y-%m-%d 10:15:00")
            })
            payment_id_seq += 1

    # 4. AVAILABILITY SLOTS (~180 slots trải rộng từ tháng 8/2026 đến tháng 11/2026)
    slots = []
    slot_id_seq = 1
    slot_lookup = {}  # slot_id -> slot dict

    base_date = datetime(2026, 8, 1)
    # Khung giờ làm việc chuẩn trong ngày của PT
    working_hours = [
        (7, 0, 8, 0),
        (8, 30, 9, 30),
        (10, 0, 11, 0),
        (14, 0, 15, 0),
        (16, 0, 17, 0),
        (17, 30, 18, 30),
        (19, 0, 20, 0)
    ]

    for pt in active_pts:
        # Mỗi PT mở slot trong 80 ngày khác nhau
        for day_offset in range(0, 95, 2):
            cur_day = base_date + timedelta(days=day_offset)
            # Chọn 1-2 khung giờ trong ngày đó
            chosen_times = random.sample(working_hours, k=random.choice([1, 2]))
            for sh, sm, eh, em in chosen_times:
                st_time = cur_day.replace(hour=sh, minute=sm, second=0)
                en_time = cur_day.replace(hour=eh, minute=em, second=0)

                s_obj = {
                    "id": slot_id_seq,
                    "pt_id": pt["id"],
                    "start_time": st_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": en_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "AVAILABLE",
                    "start_dt": st_time
                }
                slots.append(s_obj)
                slot_lookup[slot_id_seq] = s_obj
                slot_id_seq += 1

    # 5. BOOKINGS, REVIEWS & CANCELLATIONS
    bookings = []
    reviews = []
    cancellations = []
    booking_id_seq = 1
    review_id_seq = 1
    cancel_id_seq = 1

    # Phân bổ booking từ danh sách hợp đồng (PACKAGE) và học thử (TRIAL)
    used_slot_ids = set()

    # Nhóm slots theo PT
    pt_available_slots = {}
    for s in slots:
        pt_available_slots.setdefault(s["pt_id"], []).append(s)

    # 5.1 Tạo Bookings theo Hợp đồng (PACKAGE)
    for enroll in enrollments:
        pt_id = enroll["pt_id"]
        stud_id = enroll["student_id"]
        session_fee = round(enroll["final_price"] / enroll["total_sessions"], 2)

        available_for_pt = [s for s in pt_available_slots.get(pt_id, []) if s["id"] not in used_slot_ids]
        if not available_for_pt:
            continue

        # Đặt từ 2 đến 6 buổi cho hợp đồng này
        num_sessions = min(len(available_for_pt), random.randint(2, 6))
        chosen_slots = random.sample(available_for_pt, k=num_sessions)

        for s in chosen_slots:
            b_id = booking_id_seq
            booking_id_seq += 1

            slot_dt = s["start_dt"]
            now_pivot = datetime(2026, 10, 20)

            # Xác định trạng thái booking tùy theo thời gian slot
            if slot_dt < now_pivot - timedelta(days=2):
                # Quá khứ: 80% COMPLETED, 20% CANCELLED
                status = "COMPLETED" if random.random() < 0.8 else "CANCELLED"
            else:
                # Hiện tại / Tương lai: 60% CONFIRMED, 40% PENDING
                status = "CONFIRMED" if random.random() < 0.6 else "PENDING"

            if status != "CANCELLED":
                used_slot_ids.add(s["id"])
                s["status"] = "BOOKED"
                enroll["remaining_sessions"] -= 1

            b_obj = {
                "id": b_id,
                "booking_type": "PACKAGE",
                "enrollment_id": enroll["id"],
                "student_id": stud_id,
                "pt_id": pt_id,
                "slot_id": s["id"],
                "session_fee": session_fee,
                "status": status,
                "student_note": random.choice(["Học viên tập đúng giờ", "Nhờ HLV hướng dẫn thêm bài khởi động", None]),
                "created_at": (slot_dt - timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d %H:%M:%S")
            }
            bookings.append(b_obj)

            # Nếu COMPLETED: 70% có review đánh giá
            if status == "COMPLETED" and random.random() < 0.7:
                reviews.append({
                    "id": review_id_seq,
                    "booking_id": b_id,
                    "student_id": stud_id,
                    "pt_id": pt_id,
                    "rating": random.choice([4, 5, 5, 5, 4, 3]),
                    "comment": random.choice([
                        "Huấn luyện viên rất nhiệt tình và chỉ dẫn chuẩn form!",
                        "Buổi tập rất hiệu quả, cơ bắp được kích hoạt tốt.",
                        "PT tận tâm, động viên học viên trong từng set tập.",
                        "Rất hài lòng với lộ trình huấn luyện cá nhân hóa.",
                        "PT đến đúng giờ, bài tập đa dạng không bị nhàm chán."
                    ]),
                    "created_at": (slot_dt + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                })
                review_id_seq += 1

            # Nếu CANCELLED: ghi nhận vào bảng cancellations
            if status == "CANCELLED":
                canceller_role = random.choice(["STUDENT", "PT"])
                canceller_id = stud_id if canceller_role == "STUDENT" else pt_id
                cancellations.append({
                    "id": cancel_id_seq,
                    "booking_id": b_id,
                    "cancelled_by_id": canceller_id,
                    "cancelled_by_role": canceller_role,
                    "reason": random.choice([
                        "Bận việc đột xuất tại công ty",
                        "Thời tiết mưa bão không di chuyển được",
                        "Bị đau cơ nhẹ cần nghỉ ngơi phục hồi",
                        "Lịch cá nhân bị trùng giờ họp"
                    ]),
                    "cancelled_at": (slot_dt - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S"),
                    "hours_before_session": 30.0,
                    "refund_amount": session_fee if canceller_role == "STUDENT" else 0.0,
                    "compensation_amount": 0.0,
                    "penalty_amount": 0.0,
                    "status": "PROCESSED"
                })
                cancel_id_seq += 1

    # 5.2 Tạo Bookings Học Thử Miễn Phí (TRIAL)
    for student in student_users[20:]:
        for pt in random.sample(active_pts, k=random.choice([1, 2])):
            available_for_pt = [s for s in pt_available_slots.get(pt["id"], []) if s["id"] not in used_slot_ids]
            if not available_for_pt:
                continue

            s = available_for_pt[0]
            used_slot_ids.add(s["id"])
            s["status"] = "BOOKED"

            b_id = booking_id_seq
            booking_id_seq += 1

            slot_dt = s["start_dt"]
            status = "COMPLETED" if slot_dt < datetime(2026, 10, 20) else "CONFIRMED"

            bookings.append({
                "id": b_id,
                "booking_type": "TRIAL",
                "enrollment_id": None,
                "student_id": student["id"],
                "pt_id": pt["id"],
                "slot_id": s["id"],
                "session_fee": 0.0,
                "status": status,
                "student_note": "Đăng ký buổi tập thử đánh giá thể lực",
                "created_at": (slot_dt - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            })

    # 6. WORKOUT PLANS & WORKOUTS (Giáo án & Bài tập)
    workout_plans = []
    workouts = []
    plan_id_seq = 1
    workout_id_seq = 1

    sample_exercises = [
        ("Barbell Squat", "Cơ đùi trước & Mông", 4, 10, 50.0, 90),
        ("Bench Press", "Cơ ngực & Tay sau", 4, 8, 45.0, 90),
        ("Romanian Deadlift", "Cơ đùi sau & Lưng dưới", 3, 10, 40.0, 75),
        ("Lat Pulldown", "Cơ lưng xô", 4, 12, 35.0, 60),
        ("Dumbbell Shoulder Press", "Cơ vai", 3, 10, 12.0, 60),
        ("Plank", "Cơ bụng & Core", 3, 1, 0.0, 60),
        ("Walking Lunges", "Cơ mông & Đùi", 3, 12, 10.0, 60)
    ]

    for enroll in enrollments[:15]:
        p_id = plan_id_seq
        plan_id_seq += 1

        workout_plans.append({
            "id": p_id,
            "enrollment_id": enroll["id"],
            "pt_id": enroll["pt_id"],
            "title": f"Giáo án rèn luyện thể lực HD #{enroll['id']}",
            "goal": "Tăng cường sức bền và giảm mỡ thừa",
            "start_date": enroll["start_date"],
            "end_date": enroll["end_date"]
        })

        # Giao từ 3 - 5 bài tập cho giáo án này
        chosen_ex = random.sample(sample_exercises, k=random.randint(3, 5))
        for ex_name, muscle, sets, reps, weight, rest in chosen_ex:
            workouts.append({
                "id": workout_id_seq,
                "plan_id": p_id,
                "exercise_name": ex_name,
                "target_muscle": muscle,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight,
                "rest_seconds": rest,
                "video_demo_url": f"https://storage.ptconnect.vn/videos/{ex_name.lower().replace(' ', '_')}.mp4"
            })
            workout_id_seq += 1

    # -------------------------------------------------------------------------
    # VIẾT CÁC LỆNH SQL INSERT VÀO FILE SEED_DEMO.SQL
    # -------------------------------------------------------------------------

    # 1. Bảng users
    sql_lines.append("-- 1. USERS")
    sql_lines.append("INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `status`, `avatar_url`) VALUES")
    u_vals = [f"  ({u['id']}, {escape_sql(u['full_name'])}, {escape_sql(u['email'])}, {escape_sql(u['password_hash'])}, {escape_sql(u['phone'])}, {escape_sql(u['role'])}, {escape_sql(u['status'])}, {escape_sql(u['avatar_url'])})" for u in users]
    sql_lines.append(",\n".join(u_vals) + ";\n")

    # 2. Bảng pt_profiles
    sql_lines.append("-- 2. PT PROFILES")
    sql_lines.append("INSERT INTO `pt_profiles` (`id`, `user_id`, `experience_years`, `available_locations`, `location_pricing_note`, `certificate_urls`, `average_rating`, `total_reviews`, `verification_status`) VALUES")
    pt_vals = [f"  ({p['id']}, {p['user_id']}, {p['experience_years']}, {escape_sql(p['available_locations'])}, {escape_sql(p['location_pricing_note'])}, {escape_sql(p['certificate_urls'])}, {p['average_rating']}, {p['total_reviews']}, {escape_sql(p['verification_status'])})" for p in pt_profiles]
    sql_lines.append(",\n".join(pt_vals) + ";\n")

    # 3. Bảng wallets
    sql_lines.append("-- 3. WALLETS")
    sql_lines.append("INSERT INTO `wallets` (`id`, `user_id`, `balance`, `locked_balance`, `currency`, `status`) VALUES")
    w_vals = [f"  ({w['id']}, {w['user_id']}, {w['balance']:.2f}, {w['locked_balance']:.2f}, 'VND', 'ACTIVE')" for w in wallets]
    sql_lines.append(",\n".join(w_vals) + ";\n")

    # 4. Bảng courses
    sql_lines.append("-- 4. COURSES")
    sql_lines.append("INSERT INTO `courses` (`id`, `pt_id`, `title`, `description`, `total_sessions`, `validity_days`, `base_price`, `status`) VALUES")
    c_vals = [f"  ({c['id']}, {c['pt_id']}, {escape_sql(c['title'])}, {escape_sql(c['description'])}, {c['total_sessions']}, {c['validity_days']}, {c['base_price']:.2f}, {escape_sql(c['status'])})" for c in courses]
    sql_lines.append(",\n".join(c_vals) + ";\n")

    # 5. Bảng enrollments
    sql_lines.append("-- 5. ENROLLMENTS")
    sql_lines.append("INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `pt_id`, `training_location`, `final_price`, `total_sessions`, `remaining_sessions`, `start_date`, `end_date`, `contract_url`, `status`) VALUES")
    e_vals = [f"  ({e['id']}, {e['student_id']}, {e['course_id']}, {e['pt_id']}, {escape_sql(e['training_location'])}, {e['final_price']:.2f}, {e['total_sessions']}, {e['remaining_sessions']}, {escape_sql(e['start_date'])}, {escape_sql(e['end_date'])}, {escape_sql(e['contract_url'])}, {escape_sql(e['status'])})" for e in enrollments]
    sql_lines.append(",\n".join(e_vals) + ";\n")

    # 6. Bảng availability_slots
    sql_lines.append("-- 6. AVAILABILITY SLOTS")
    sql_lines.append("INSERT INTO `availability_slots` (`id`, `pt_id`, `start_time`, `end_time`, `status`) VALUES")
    s_vals = [f"  ({s['id']}, {s['pt_id']}, {escape_sql(s['start_time'])}, {escape_sql(s['end_time'])}, {escape_sql(s['status'])})" for s in slots]
    sql_lines.append(",\n".join(s_vals) + ";\n")

    # 7. Bảng bookings
    sql_lines.append("-- 7. BOOKINGS")
    sql_lines.append("INSERT INTO `bookings` (`id`, `booking_type`, `enrollment_id`, `student_id`, `pt_id`, `slot_id`, `session_fee`, `status`, `student_note`, `created_at`) VALUES")
    b_vals = [f"  ({b['id']}, {escape_sql(b['booking_type'])}, {escape_sql(b['enrollment_id'])}, {b['student_id']}, {b['pt_id']}, {b['slot_id']}, {b['session_fee']:.2f}, {escape_sql(b['status'])}, {escape_sql(b['student_note'])}, {escape_sql(b['created_at'])})" for b in bookings]
    sql_lines.append(",\n".join(b_vals) + ";\n")

    # 8. Bảng reviews
    if reviews:
        sql_lines.append("-- 8. REVIEWS")
        sql_lines.append("INSERT INTO `reviews` (`id`, `booking_id`, `student_id`, `pt_id`, `rating`, `comment`, `created_at`) VALUES")
        r_vals = [f"  ({r['id']}, {r['booking_id']}, {r['student_id']}, {r['pt_id']}, {r['rating']}, {escape_sql(r['comment'])}, {escape_sql(r['created_at'])})" for r in reviews]
        sql_lines.append(",\n".join(r_vals) + ";\n")

    # 9. Bảng cancellations
    if cancellations:
        sql_lines.append("-- 9. CANCELLATIONS")
        sql_lines.append("INSERT INTO `cancellations` (`id`, `booking_id`, `cancelled_by_id`, `cancelled_by_role`, `reason`, `cancelled_at`, `hours_before_session`, `refund_amount`, `compensation_amount`, `penalty_amount`, `status`) VALUES")
        cn_vals = [f"  ({cn['id']}, {cn['booking_id']}, {escape_sql(cn['cancelled_by_id'])}, {escape_sql(cn['cancelled_by_role'])}, {escape_sql(cn['reason'])}, {escape_sql(cn['cancelled_at'])}, {cn['hours_before_session']}, {cn['refund_amount']:.2f}, {cn['compensation_amount']:.2f}, {cn['penalty_amount']:.2f}, {escape_sql(cn['status'])})" for cn in cancellations]
        sql_lines.append(",\n".join(cn_vals) + ";\n")

    # 10. Bảng payments
    if payments:
        sql_lines.append("-- 10. PAYMENTS")
        sql_lines.append("INSERT INTO `payments` (`id`, `wallet_id`, `enrollment_id`, `amount`, `payment_type`, `payment_method`, `status`, `transaction_ref`, `created_at`) VALUES")
        pay_vals = [f"  ({p['id']}, {p['wallet_id']}, {escape_sql(p['enrollment_id'])}, {p['amount']:.2f}, {escape_sql(p['payment_type'])}, {escape_sql(p['payment_method'])}, {escape_sql(p['status'])}, {escape_sql(p['transaction_ref'])}, {escape_sql(p['created_at'])})" for p in payments]
        sql_lines.append(",\n".join(pay_vals) + ";\n")

    # 11. Bảng workout_plans
    if workout_plans:
        sql_lines.append("-- 11. WORKOUT PLANS")
        sql_lines.append("INSERT INTO `workout_plans` (`id`, `enrollment_id`, `pt_id`, `title`, `goal`, `start_date`, `end_date`) VALUES")
        wp_vals = [f"  ({wp['id']}, {wp['enrollment_id']}, {wp['pt_id']}, {escape_sql(wp['title'])}, {escape_sql(wp['goal'])}, {escape_sql(wp['start_date'])}, {escape_sql(wp['end_date'])})" for wp in workout_plans]
        sql_lines.append(",\n".join(wp_vals) + ";\n")

    # 12. Bảng workouts
    if workouts:
        sql_lines.append("-- 12. WORKOUTS")
        sql_lines.append("INSERT INTO `workouts` (`id`, `plan_id`, `exercise_name`, `target_muscle`, `sets`, `reps`, `weight_kg`, `rest_seconds`, `video_demo_url`) VALUES")
        wo_vals = [f"  ({wo['id']}, {wo['plan_id']}, {escape_sql(wo['exercise_name'])}, {escape_sql(wo['target_muscle'])}, {wo['sets']}, {wo['reps']}, {wo['weight_kg']:.2f}, {wo['rest_seconds']}, {escape_sql(wo['video_demo_url'])})" for wo in workouts]
        sql_lines.append(",\n".join(wo_vals) + ";\n")

    sql_lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_lines.append("-- HOÀN TẤT DỮ LIỆU SEED DEMO.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))

    print(f"🎉 Đã sinh thành công file SQL seed demo tại: {OUTPUT_FILE}")
    print(f"📊 Thống kê dữ liệu đã sinh:")
    print(f"   - Users: {len(users)} (1 Admin, {len(pt_profiles)} PT, {len(student_users)} Students)")
    print(f"   - Courses: {len(courses)}")
    print(f"   - Slots: {len(slots)}")
    print(f"   - Enrollments: {len(enrollments)}")
    print(f"   - Bookings: {len(bookings)} (Package: {len([b for b in bookings if b['booking_type'] == 'PACKAGE'])}, Trial: {len([b for b in bookings if b['booking_type'] == 'TRIAL'])})")
    print(f"   - Reviews: {len(reviews)}")
    print(f"   - Payments: {len(payments)}")
    print(f"   - Workout Plans: {len(workout_plans)} plans ({len(workouts)} exercises)")

    if "--import" in sys.argv:
        print("\n📥 Đang tự động nạp dữ liệu vào MySQL container (bảo toàn 100% font tiếng Việt UTF-8)...")
        import subprocess
        res_cp = subprocess.run([
            "docker", "cp", OUTPUT_FILE, "ptconnect-mysql:/tmp/seed_demo.sql"
        ], capture_output=True, text=True)
        if res_cp.returncode == 0:
            res_sql = subprocess.run([
                "docker", "exec", "ptconnect-mysql", "mysql", "-uptuser", "-pptpassword",
                "--default-character-set=utf8mb4", "ptconnect", "-e", "source /tmp/seed_demo.sql;"
            ], capture_output=True, text=True)
            if res_sql.returncode == 0:
                print("✅ Nạp dữ liệu vào database thành công! Font tiếng Việt chuẩn xác 100%.")
            else:
                print(f"❌ Lỗi nạp SQL: {res_sql.stderr}")
        else:
            print(f"❌ Lỗi copy file vào container: {res_cp.stderr}")


if __name__ == "__main__":
    main()
