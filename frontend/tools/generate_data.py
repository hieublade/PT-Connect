#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sinh dữ liệu mẫu toàn diện cho nền tảng PT Connect (Milestone 8 - Output 4).
Tuân thủ toàn bộ các ràng buộc CHECK, UNIQUE, FK, BCNF và Trigger trong database/init.sql & trigger.sql.

Dữ liệu bao phủ mọi ngóc ngách chức năng:
- 1 Quản trị viên (ADMIN)
- 8 Huấn luyện viên (PT): 5 VERIFIED, 2 PENDING (để test duyệt hồ sơ Admin), 1 SUSPENDED
- 30 Học viên (STUDENT): Học viên chính (student.a@ptconnect.vn) có dữ liệu mẫu chi tiết nhất
- 15 Khóa học đa dạng (Giảm mỡ, Tăng cơ, Pilates, Boxing, Nhập môn)
- 400+ Khung giờ rảnh (Availability Slots) trải đều từ tháng 8/2026 đến tháng 1/2027
- 40+ Hợp đồng (Enrollments) với các gói còn hạn đến 2027 để test đặt lịch thoải mái
- 180+ Ca đặt lịch (Bookings) với đầy đủ 4 trạng thái:
    + PENDING (để PT test duyệt lịch)
    + CONFIRMED (để theo dõi lịch sắp tới)
    + COMPLETED (để test xem lịch sử, điểm danh và viết review)
    + CANCELLED (để test chính sách hoàn/phạt hủy lịch)
- Điểm danh (Attendance) đầy đủ cho các ca COMPLETED (QR_CODE, OTP, GEO_LOCATION)
- Đánh giá (Reviews) phong phú từ 3 đến 5 sao
- Lịch sử hủy ca (Cancellations) kèm lý do và số tiền hoàn
- Giao dịch tài chính (Payments) gồm Nạp tiền, Mua khóa, Hoàn tiền, Bồi thường
- Giáo án & Bài tập (Workout Plans & Workouts) có thứ tự exercise_order chuẩn xác 1..N
"""

import os
import sys
import random
import subprocess
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SEED = 42
random.seed(SEED)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILES = [
    os.path.join(PROJECT_ROOT, "database", "seed_demo.sql"),
    os.path.join(PROJECT_ROOT, "backend-py", "database", "seed_demo.sql")
]

# Danh sách họ tên Việt Nam thực tế
VN_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
VN_MIDDLE_NAMES = ["Văn", "Thị", "Hải", "Đức", "Minh", "Thu", "Ngọc", "Thanh", "Hoàng", "Quốc", "Phương", "Bảo"]
VN_FIRST_NAMES = ["Nam", "Anh", "Tuấn", "Hùng", "Hà", "Linh", "Trang", "Mai", "Hương", "Huy", "Dũng", "Khoa", "Hiếu", "Thành", "Phương", "Trí", "Đạt", "Sơn", "Tùng", "Long"]


def generate_vietnamese_name():
    return f"{random.choice(VN_LAST_NAMES)} {random.choice(VN_MIDDLE_NAMES)} {random.choice(VN_FIRST_NAMES)}"


def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "1" if val else "0"
    s = str(val).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"


def main():
    print(f"Bắt đầu sinh dữ liệu mẫu toàn diện PT Connect (Seed: {SEED})...")

    password_plain = "Password123@"
    password_hash = "$2b$10$97NHtEb/u6D3YO6v3GWpfuhQFZkJ.CsF1eCCorUvtDzBafzxRbx92"
    print(f"Mật khẩu mặc định toàn hệ thống: '{password_plain}' -> BCrypt: {password_hash}")

    sql_lines = []
    sql_lines.append("-- =====================================================================")
    sql_lines.append("-- DỮ LIỆU MẪU CHẠY DEMO HỆ THỐNG PT CONNECT (Đầy đủ chức năng mọi phân hệ)")
    sql_lines.append(f"-- Sinh tự động ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Seed: {SEED})")
    sql_lines.append("-- Mật khẩu đăng nhập mặc định cho TẤT CẢ tài khoản: Password123@")
    sql_lines.append("-- =====================================================================")
    sql_lines.append("USE ptconnect;")
    sql_lines.append("SET NAMES utf8mb4;")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_lines.append("")
    sql_lines.append("-- XÓA DỮ LIỆU CŨ ĐỂ ĐẢM BẢO TÍNH TOÀN VẸN KHI CHẠY LẠI DEMO")
    sql_lines.append("TRUNCATE TABLE `attendance`;")
    sql_lines.append("TRUNCATE TABLE `booking_disputes`;")
    sql_lines.append("TRUNCATE TABLE `cancellations`;")
    sql_lines.append("TRUNCATE TABLE `reviews`;")
    sql_lines.append("TRUNCATE TABLE `workouts`;")
    sql_lines.append("TRUNCATE TABLE `workout_plans`;")
    sql_lines.append("TRUNCATE TABLE `bookings`;")
    sql_lines.append("TRUNCATE TABLE `availability_slots`;")
    sql_lines.append("TRUNCATE TABLE `payments`;")
    sql_lines.append("TRUNCATE TABLE `wallet_audit_logs`;")
    sql_lines.append("TRUNCATE TABLE `enrollments`;")
    sql_lines.append("TRUNCATE TABLE `courses`;")
    sql_lines.append("TRUNCATE TABLE `wallets`;")
    sql_lines.append("TRUNCATE TABLE `pt_locations`;")
    sql_lines.append("TRUNCATE TABLE `pt_profiles`;")
    sql_lines.append("TRUNCATE TABLE `users`;")
    sql_lines.append("")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_lines.append("")

    # =========================================================================
    # 1. USERS & WALLETS & PT PROFILES
    # =========================================================================
    users = []
    wallets = []
    pt_profiles = []
    user_id_seq = 1

    # 1.1 Admin Hệ Thống (Có ví tích lũy phí dịch vụ nền tảng 10%)
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
    wallets.append({"id": user_id_seq, "user_id": user_id_seq, "balance": 28500000.0, "locked_balance": 0.0})
    user_id_seq += 1

    # 1.2 Huấn luyện viên (PT)
    pt_configs = [
        ("Lê Hoàng Cường", "pt.hoangc@ptconnect.vn", "0900000003", 6, "VERIFIED", "ACTIVE",
         "HLV Thể hình chuyên nghiệp & Giảm mỡ chuyên sâu. Đạt chứng chỉ NASM CPT quốc tế.",
         "Phòng Cali Cầu Giấy; FitZone Thanh Xuân", "Dạy tại nhà phụ thu 20% tiền đi lại"),
        ("Phạm Minh Dũng", "pt.minhd@ptconnect.vn", "0900000004", 4, "VERIFIED", "ACTIVE",
         "Chuyên gia Calisthenics và Phục hồi cơ xương khớp, cân chỉnh cột sống.",
         "Studio cá nhân tại Thanh Xuân; Khu vực Đống Đa", "Khác địa điểm thỏa thuận thêm phí"),
        ("Trần Quốc Bảo", "pt.quocbao@ptconnect.vn", "0900000005", 5, "VERIFIED", "ACTIVE",
         "Cựu vận động viên điền kinh, chuyên Kickboxing, Cardio cường độ cao HIIT.",
         "Phòng tập Elite Fitness Tây Hồ; Cầu Giấy", "Giá chuẩn theo hợp đồng"),
        ("Nguyễn Thu Hà", "pt.thuha@ptconnect.vn", "0900000006", 3, "VERIFIED", "ACTIVE",
         "Chuyên gia Yoga & Pilates chỉnh dáng nữ giới, săn chắc vùng bụng và mông đùi.",
         "Phòng tập Yoga Plus Ba Đình; Cầu Giấy", "Kèm tại nhà phụ thu 50k/buổi"),
        ("Đỗ Tuấn Kiệt", "pt.tuankiet@ptconnect.vn", "0900000007", 7, "VERIFIED", "ACTIVE",
         "Master Trainer Powerlifting, tăng cơ Hypertrophy & dinh dưỡng thi đấu thể hình.",
         "Fit24 Hai Bà Trưng; Times City", "Không phụ thu địa điểm chỉ định"),
        ("Vũ Hoàng Nam", "pt.hoangnam@ptconnect.vn", "0900000008", 2, "PENDING", "PENDING",
         "HLV Fitness trẻ nhiệt huyết, chuyên giảm cân cấp tốc cho dân văn phòng.",
         "Khu vực Hoàng Mai; Hà Đông", "Chờ ban quản trị xét duyệt hồ sơ"),
        ("Đặng Thúy Nga", "pt.thuynga@ptconnect.vn", "0900000009", 1, "PENDING", "PENDING",
         "Huấn luyện viên Aerobic & Group X năng động, cải thiện sự dẻo dai.",
         "Khu vực Nam Từ Liêm", "Chờ kiểm tra bằng cấp chứng chỉ"),
        ("Bùi Văn Quyết", "pt.vanquyet@ptconnect.vn", "0900000010", 3, "REJECTED", "SUSPENDED",
         "Hồ sơ chứng chỉ chưa đạt chuẩn theo quy định hệ thống.",
         "Khu vực Bắc Từ Liêm", "Tài khoản bị tạm ngưng")
    ]

    pt_id_seq = 1
    pt_profile_map = {}

    for name, email, phone, exp, verif, status, bio, locs, note in pt_configs:
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
        # PT có số dư và phần ký quỹ bảo chứng hợp đồng (locked_balance)
        pt_balance = 8500000.0 if status == "ACTIVE" else 0.0
        pt_locked = 1500000.0 if status == "ACTIVE" else 0.0
        wallets.append({"id": u_id, "user_id": u_id, "balance": pt_balance, "locked_balance": pt_locked})

        pt_obj = {
            "id": pt_id_seq,
            "user_id": u_id,
            "experience_years": exp,
            "available_locations": locs,
            "location_pricing_note": note,
            "certificate_url": "https://storage.ptconnect.vn/certs/cert_nasam.jpg",
            "average_rating": 0.0,
            "total_reviews": 0,
            "verification_status": verif,
            "name": name,
            "active": (verif == "VERIFIED" and status == "ACTIVE")
        }
        pt_profiles.append(pt_obj)
        pt_profile_map[pt_id_seq] = pt_obj
        pt_id_seq += 1

    # 1.3 Học viên (STUDENT)
    student_users = []
    for i in range(1, 31):
        u_id = user_id_seq
        user_id_seq += 1
        if i == 1:
            s_name = "Nguyễn Văn A"
            s_email = "student.a@ptconnect.vn"
            s_phone = "0900000001"
            s_balance = 13200000.0  # Số dư khớp chuẩn với lịch sử thanh toán payments
        else:
            s_name = generate_vietnamese_name()
            s_email = f"student_{i:02d}@ptconnect.vn"
            s_phone = f"091{i:07d}"
            s_balance = float(random.choice([3000000, 5000000, 8000000, 12000000, 15000000, 20000000, 25000000]))

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
        wallets.append({"id": u_id, "user_id": u_id, "balance": s_balance, "locked_balance": 0.0})

    # =========================================================================
    # 2. COURSES (Khóa học của 5 PT VERIFIED)
    # =========================================================================
    active_pts = [p for p in pt_profiles if p["active"]]
    courses = []
    course_id_seq = 1

    course_library = {
        1: [  # HLV Lê Hoàng Cường
            ("Khóa Khởi Động Nhập Môn 12 Buổi", "Dành cho người mới bắt đầu làm quen với phòng gym và thể lực nền tảng.", 12, 90, 3600000.0),
            ("Gói Giảm Mỡ Chuyên Sâu 12 Tuần", "Lộ trình đốt mỡ toàn diện kết hợp dinh dưỡng macro khoa học.", 36, 120, 10800000.0),
            ("Gói Tăng Cơ Thể Hình 24 Buổi", "Tăng kích thước sợi cơ Hypertrophy & tối ưu form tạ chuẩn.", 24, 90, 7200000.0),
        ],
        2: [  # HLV Phạm Minh Dũng
            ("Gói Calisthenics & Thể Hình Tự Thân 24 Buổi", "Làm chủ cơ thể với xà đơn, xà kép và các chuyển động cơ bản.", 24, 90, 7200000.0),
            ("Gói Phục Hồi Cột Sống & Cân Chỉnh Dáng 16 Buổi", "Khắc phục đau mỏi vai gáy, gù lưng và lệch hông cho văn phòng.", 16, 60, 5600000.0),
        ],
        3: [  # HLV Trần Quốc Bảo
            ("Gói Boxing Thể Lực & Xả Stress 16 Buổi", "Luyện tập phản xạ tốc độ cao, đốt calo tối đa mỗi buổi tập.", 16, 60, 5600000.0),
            ("Khóa Thể Lực Cardio Cường Độ Cao HIIT 12 Buổi", "Tăng dung tích phổi, sức bền tim mạch và giảm mỡ tốc hành.", 12, 60, 4200000.0),
        ],
        4: [  # HLV Nguyễn Thu Hà
            ("Gói Pilates Chỉnh Dáng & Cột Sống 20 Buổi", "Cải thiện tư thế lưng gù, siết eo bụng thon gọn nữ tính.", 20, 90, 8000000.0),
            ("Khóa Yoga Phục Hồi & Dẻo Dai Khớp 12 Buổi", "Giải phóng căng cứng cơ xương khớp, xua tan áp lực công việc.", 12, 60, 4500000.0),
        ],
        5: [  # HLV Đỗ Tuấn Kiệt
            ("Khóa Powerlifting Chuyên Sâu Squat-Bench-Deadlift 24 Buổi", "Tối đa hóa sức mạnh tổng thể và kỹ thuật nâng tạ đỉnh cao.", 24, 90, 8400000.0),
            ("Gói Hypertrophy Tăng Cơ Cắt Nét 36 Buổi", "Giáo án cá nhân hóa tăng cơ nạc tối đa và siết mỡ thi đấu.", 36, 120, 12600000.0),
        ]
    }

    for pt_id, c_list in course_library.items():
        pt_obj = pt_profile_map[pt_id]
        pt_short_name = pt_obj["name"].split()[-1]
        for t_title, t_desc, t_sessions, t_validity, t_price in c_list:
            courses.append({
                "id": course_id_seq,
                "pt_id": pt_id,
                "title": f"{t_title} - HLV {pt_short_name}",
                "description": t_desc,
                "total_sessions": t_sessions,
                "validity_days": t_validity,
                "base_price": t_price,
                "status": "ACTIVE"
            })
            course_id_seq += 1

    # Map course_id -> course_obj
    course_lookup = {c["id"]: c for c in courses}

    # =========================================================================
    # 3. ENROLLMENTS & PAYMENTS (Hợp đồng & Lịch sử giao dịch tài chính)
    # =========================================================================
    enrollments = []
    payments = []
    enrollment_id_seq = 1
    payment_id_seq = 1

    # 3.1 Dành riêng cho Học viên chính (Student A - id 10):
    # Khóa 1: Đang học với HLV Lê Hoàng Cường (Course 1)
    e1_id = enrollment_id_seq
    enrollment_id_seq += 1
    enrollments.append({
        "id": e1_id,
        "student_id": 10,
        "course_id": 1,
        "pt_id": 1,
        "training_location": "FitZone Thanh Xuân",
        "final_price": 3600000.0,
        "total_sessions": 12,
        "remaining_sessions": 7,
        "start_date": "2026-10-15",
        "end_date": "2027-01-30",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000001.pdf",
        "status": "ACTIVE"
    })

    # Khóa 2: Đang học với HLV Nguyễn Thu Hà (Course 8 - Pilates)
    e2_id = enrollment_id_seq
    enrollment_id_seq += 1
    enrollments.append({
        "id": e2_id,
        "student_id": 10,
        "course_id": 8,
        "pt_id": 4,
        "training_location": "Phòng tập Yoga Plus Ba Đình",
        "final_price": 8000000.0,
        "total_sessions": 20,
        "remaining_sessions": 18,
        "start_date": "2026-11-01",
        "end_date": "2027-02-28",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000002.pdf",
        "status": "ACTIVE"
    })

    # Khóa 3: Đã hoàn thành trong quá khứ với HLV Trần Quốc Bảo (Course 6 - Boxing)
    e3_id = enrollment_id_seq
    enrollment_id_seq += 1
    enrollments.append({
        "id": e3_id,
        "student_id": 10,
        "course_id": 6,
        "pt_id": 3,
        "training_location": "Phòng tập Elite Fitness Tây Hồ",
        "final_price": 5600000.0,
        "total_sessions": 16,
        "remaining_sessions": 0,
        "start_date": "2026-08-01",
        "end_date": "2026-09-30",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000003.pdf",
        "status": "COMPLETED"
    })

    # Lịch sử nạp/mua/hoàn ví của Student A
    student_a_payments = [
        (10, None, 20000000.0, "TOPUP", "BANK_TRANSFER", "SUCCESS", "TXN_TOPUP_2026_00001", "2026-08-01 09:00:00"),
        (10, e3_id, 5600000.0, "PURCHASE_PACKAGE", "WALLET", "SUCCESS", "TXN_BUY_2026_00002", "2026-08-01 09:30:00"),
        (10, None, 10000000.0, "TOPUP", "BANK_TRANSFER", "SUCCESS", "TXN_TOPUP_2026_00003", "2026-10-14 15:00:00"),
        (10, e1_id, 3600000.0, "PURCHASE_PACKAGE", "WALLET", "SUCCESS", "TXN_BUY_2026_00004", "2026-10-15 10:00:00"),
        (10, e2_id, 8000000.0, "PURCHASE_PACKAGE", "WALLET", "SUCCESS", "TXN_BUY_2026_00005", "2026-11-01 08:30:00"),
        (10, None, 300000.0, "REFUND", "WALLET", "SUCCESS", "TXN_REFUND_2026_00006", "2026-11-08 19:30:00"),
        (10, None, 100000.0, "COMPENSATION", "WALLET", "SUCCESS", "TXN_COMP_2026_00007", "2026-11-10 14:00:00"),
    ]
    for w_id, enr_id, amt, p_type, p_method, p_stat, p_ref, p_created in student_a_payments:
        payments.append({
            "id": payment_id_seq,
            "wallet_id": w_id,
            "enrollment_id": enr_id,
            "amount": amt,
            "payment_type": p_type,
            "payment_method": p_method,
            "status": p_stat,
            "transaction_ref": p_ref,
            "created_at": p_created
        })
        payment_id_seq += 1

    # 3.2 Hợp đồng của các học viên khác (student_users[1:25])
    for student in student_users[1:25]:
        chosen_courses = random.sample(courses, k=random.choice([1, 2]))
        for crs in chosen_courses:
            e_id = enrollment_id_seq
            enrollment_id_seq += 1

            # Hợp đồng mở từ tháng 9 - 11/2026, hạn kéo dài tới tháng 1 - 3/2027
            start_d = datetime(2026, 9, 1) + timedelta(days=random.randint(0, 65))
            end_d = start_d + timedelta(days=crs["validity_days"] + 30)

            price = crs["base_price"]
            tot_sessions = crs["total_sessions"]
            rem_sessions = random.randint(tot_sessions // 2, tot_sessions)

            enrollments.append({
                "id": e_id,
                "student_id": student["id"],
                "course_id": crs["id"],
                "pt_id": crs["pt_id"],
                "training_location": random.choice(["Cali Fitness Cầu Giấy", "FitZone Thanh Xuân", "Elite Fitness Tây Hồ", "Tập tại nhà học viên"]),
                "final_price": price,
                "total_sessions": tot_sessions,
                "remaining_sessions": rem_sessions,
                "start_date": start_d.strftime("%Y-%m-%d"),
                "end_date": end_d.strftime("%Y-%m-%d"),
                "contract_url": f"https://storage.ptconnect.vn/contracts/ptc_hd_{e_id:06d}.pdf",
                "status": "ACTIVE"
            })

            # Thanh toán TOPUP
            payments.append({
                "id": payment_id_seq,
                "wallet_id": student["id"],
                "enrollment_id": None,
                "amount": price + 2000000.0,
                "payment_type": "TOPUP",
                "payment_method": "BANK_TRANSFER",
                "status": "SUCCESS",
                "transaction_ref": f"TXN_TOPUP_{payment_id_seq:05d}",
                "created_at": (start_d - timedelta(days=1)).strftime("%Y-%m-%d 10:00:00")
            })
            payment_id_seq += 1

            # Thanh toán Mua khóa học
            payments.append({
                "id": payment_id_seq,
                "wallet_id": student["id"],
                "enrollment_id": e_id,
                "amount": price,
                "payment_type": "PURCHASE_PACKAGE",
                "payment_method": "WALLET",
                "status": "SUCCESS",
                "transaction_ref": f"TXN_BUY_{payment_id_seq:05d}",
                "created_at": start_d.strftime("%Y-%m-%d 10:30:00")
            })
            payment_id_seq += 1

    # Thu phí hoa hồng nền tảng 10% vào ví Quản trị viên (wallet_id = 1, user_id = 1)
    for p_buy in [p for p in payments if p["payment_type"] == "PURCHASE_PACKAGE"][:8]:
        admin_fee = round(p_buy["amount"] * 0.10, 2)
        payments.append({
            "id": payment_id_seq,
            "wallet_id": 1,
            "enrollment_id": p_buy["enrollment_id"],
            "amount": admin_fee,
            "payment_type": "PLATFORM_FEE",
            "payment_method": "WALLET",
            "status": "SUCCESS",
            "transaction_ref": f"TXN_PFEE_{payment_id_seq:05d}",
            "created_at": p_buy["created_at"]
        })
        payment_id_seq += 1

    # 2 giao dịch rút tiền mẫu của Admin để hiển thị trên tab lịch sử rút tiền
    payments.append({
        "id": payment_id_seq,
        "wallet_id": 1,
        "enrollment_id": None,
        "amount": 5000000.0,
        "payment_type": "WITHDRAWAL",
        "payment_method": "BANK_TRANSFER",
        "status": "SUCCESS",
        "transaction_ref": "TXN_ADM_WD_20261020_001",
        "created_at": "2026-10-20 14:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": 1,
        "enrollment_id": None,
        "amount": 10000000.0,
        "payment_type": "WITHDRAWAL",
        "payment_method": "BANK_TRANSFER",
        "status": "SUCCESS",
        "transaction_ref": "TXN_ADM_WD_20261101_002",
        "created_at": "2026-11-01 10:30:00"
    })
    payment_id_seq += 1

    # Khoản tích lũy phí dịch vụ các quý trước để số dư ví khớp chính xác 28.500.000 đ
    current_fee_sum = sum(p["amount"] for p in payments if p["wallet_id"] == 1 and p["payment_type"] == "PLATFORM_FEE")
    needed_topup = 28500000.0 + 15000000.0 - current_fee_sum
    if needed_topup > 0:
        payments.append({
            "id": payment_id_seq,
            "wallet_id": 1,
            "enrollment_id": None,
            "amount": needed_topup,
            "payment_type": "TOPUP",
            "payment_method": "BANK_TRANSFER",
            "status": "SUCCESS",
            "transaction_ref": "TXN_ADM_INIT_FEE_2026",
            "created_at": "2026-10-01 08:00:00"
        })
        payment_id_seq += 1

    enrollment_lookup = {e["id"]: e for e in enrollments}

    # =========================================================================
    # 4. AVAILABILITY SLOTS (Trải rộng từ 01/08/2026 đến 15/01/2027)
    # =========================================================================
    slots = []
    slot_id_seq = 1
    pt_slot_schedule = {}  # pt_id -> list of slot_objs

    standard_hours = [
        (7, 0, 8, 0),
        (8, 30, 9, 30),
        (10, 0, 11, 0),
        (14, 0, 15, 0),
        (16, 0, 17, 0),
        (17, 30, 18, 30),
        (19, 0, 20, 0)
    ]

    base_start = datetime(2026, 8, 1)
    # Sinh slots trong 160 ngày (đến tháng 1/2027)
    for pt in active_pts:
        pt_id = pt["id"]
        pt_slot_schedule[pt_id] = []
        for day_idx in range(0, 160, 2):
            cur_day = base_start + timedelta(days=day_idx)
            chosen_hours = random.sample(standard_hours, k=random.choice([2, 3]))
            for sh, sm, eh, em in chosen_hours:
                st_time = cur_day.replace(hour=sh, minute=sm, second=0)
                en_time = cur_day.replace(hour=eh, minute=em, second=0)

                s_obj = {
                    "id": slot_id_seq,
                    "pt_id": pt_id,
                    "start_time": st_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": en_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "AVAILABLE",
                    "start_dt": st_time
                }
                slots.append(s_obj)
                pt_slot_schedule[pt_id].append(s_obj)
                slot_id_seq += 1

    slot_lookup = {s["id"]: s for s in slots}

    # =========================================================================
    # 5. BOOKINGS, REVIEWS, CANCELLATIONS, ATTENDANCE
    # Mốc chuẩn hóa thời gian: NOW = 14/11/2026
    # =========================================================================
    bookings = []
    reviews = []
    cancellations = []
    attendance = []

    booking_id_seq = 1
    review_id_seq = 1
    cancel_id_seq = 1
    attendance_id_seq = 1

    used_slot_ids = set()
    NOW_PIVOT = datetime(2026, 11, 14, 9, 0, 0)

    # 5.1 Xếp ca tập chi tiết cho Học viên chính (Student A - id 10)
    # Lấy các slot phù hợp của HLV 1 (Cường) và HLV 4 (Hà)
    pt1_slots = pt_slot_schedule[1]
    pt4_slots = pt_slot_schedule[4]

    # Ca 1: SẮP TỚI (CONFIRMED) - Ngày mai 15/11/2026 với HLV Cường
    s_tomm = next((s for s in pt1_slots if s["start_dt"] >= datetime(2026, 11, 15) and s["id"] not in used_slot_ids), pt1_slots[50])
    used_slot_ids.add(s_tomm["id"])
    s_tomm["status"] = "BOOKED"
    b_conf = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1_id,
        "student_id": 10,
        "slot_id": s_tomm["id"],
        "session_fee": 300000.0,
        "status": "CONFIRMED",
        "student_note": "Tập bài ngực và tay sau theo lộ trình",
        "created_at": "2026-11-12 10:00:00"
    }
    bookings.append(b_conf)
    booking_id_seq += 1

    # Ca 2: ĐANG CHỜ DUYỆT (PENDING) - Ngày 17/11/2026 với HLV Hà
    s_pend = next((s for s in pt4_slots if s["start_dt"] >= datetime(2026, 11, 16) and s["id"] not in used_slot_ids), pt4_slots[52])
    used_slot_ids.add(s_pend["id"])
    s_pend["status"] = "BOOKED"
    b_pend = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e2_id,
        "student_id": 10,
        "slot_id": s_pend["id"],
        "session_fee": 400000.0,
        "status": "PENDING",
        "student_note": "Học viên nhờ HLV hướng dẫn thêm bài giãn cơ lưng",
        "created_at": "2026-11-13 14:00:00"
    }
    bookings.append(b_pend)
    booking_id_seq += 1

    # Ca 2b: ĐANG CHỜ HLV CƯỜNG DUYỆT (PENDING) - Để PT Cường test tab Duyệt lịch / Từ chối ca
    s_pt1_pend1 = next((s for s in pt1_slots if s["start_dt"] >= datetime(2026, 11, 16) and s["id"] not in used_slot_ids), pt1_slots[55])
    used_slot_ids.add(s_pt1_pend1["id"])
    s_pt1_pend1["status"] = "BOOKED"
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1_id,
        "student_id": 10,
        "slot_id": s_pt1_pend1["id"],
        "session_fee": 300000.0,
        "status": "PENDING",
        "student_note": "Học viên Nguyễn Văn A nhờ HLV kiểm tra chỉ số InBody và chỉnh form Bench Press",
        "created_at": "2026-11-13 15:30:00"
    })
    booking_id_seq += 1

    s_pt1_pend2 = next((s for s in pt1_slots if s["start_dt"] >= datetime(2026, 11, 17) and s["id"] not in used_slot_ids), pt1_slots[56])
    used_slot_ids.add(s_pt1_pend2["id"])
    s_pt1_pend2["status"] = "BOOKED"
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "TRIAL",
        "enrollment_id": None,
        "student_id": 11,
        "slot_id": s_pt1_pend2["id"],
        "session_fee": 0.0,
        "status": "PENDING",
        "student_note": "Học viên An Vũ đăng ký học thử buổi đầu tiên",
        "created_at": "2026-11-13 16:00:00"
    })
    booking_id_seq += 1

    # Ca 3: VỪA HOÀN THÀNH HÔM QUA (COMPLETED - CHƯA ĐÁNH GIÁ ĐỂ TEST NÚT REVIEW)
    s_yesterday = next((s for s in pt1_slots if s["start_dt"] <= datetime(2026, 11, 13, 23, 59) and s["start_dt"] >= datetime(2026, 11, 12) and s["id"] not in used_slot_ids), pt1_slots[40])
    used_slot_ids.add(s_yesterday["id"])
    s_yesterday["status"] = "BOOKED"
    b_done_noreview = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1_id,
        "student_id": 10,
        "slot_id": s_yesterday["id"],
        "session_fee": 300000.0,
        "status": "COMPLETED",
        "student_note": "Buổi tập tạ chân đùi Squat",
        "created_at": "2026-11-10 09:00:00"
    }
    bookings.append(b_done_noreview)
    attendance.append({
        "id": attendance_id_seq,
        "booking_id": b_done_noreview["id"],
        "check_in_time": s_yesterday["start_time"],
        "check_out_time": s_yesterday["end_time"],
        "verification_method": "QR_CODE",
        "student_confirmed": True,
        "pt_confirmed": True,
        "status": "PRESENT"
    })
    attendance_id_seq += 1
    booking_id_seq += 1

    # Ca 4: HOÀN THÀNH TRONG QUÁ KHỨ (ĐÃ ĐÁNH GIÁ 5 SAO) - HLV Cường
    s_past1 = next((s for s in pt1_slots if s["start_dt"] <= datetime(2026, 11, 5) and s["start_dt"] >= datetime(2026, 10, 25) and s["id"] not in used_slot_ids), pt1_slots[30])
    used_slot_ids.add(s_past1["id"])
    s_past1["status"] = "BOOKED"
    b_done_rev1 = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1_id,
        "student_id": 10,
        "slot_id": s_past1["id"],
        "session_fee": 300000.0,
        "status": "COMPLETED",
        "student_note": "Khởi động nhập môn gym",
        "created_at": "2026-10-28 11:00:00"
    }
    bookings.append(b_done_rev1)
    reviews.append({
        "id": review_id_seq,
        "booking_id": b_done_rev1["id"],
        "student_id": 10,
        "pt_id": 1,
        "rating": 5,
        "comment": "Huấn luyện viên Cường rất nhiệt tình, hướng dẫn siết cơ bụng và chỉnh form Squat cực kỳ chuẩn xác!",
        "created_at": "2026-10-30 16:00:00"
    })
    review_id_seq += 1
    attendance.append({
        "id": attendance_id_seq,
        "booking_id": b_done_rev1["id"],
        "check_in_time": s_past1["start_time"],
        "check_out_time": s_past1["end_time"],
        "verification_method": "OTP",
        "student_confirmed": True,
        "pt_confirmed": True,
        "status": "PRESENT"
    })
    attendance_id_seq += 1
    booking_id_seq += 1

    # Ca 5: HOÀN THÀNH TRONG QUÁ KHỨ (ĐÃ ĐÁNH GIÁ 5 SAO) - HLV Hà
    s_past2 = next((s for s in pt4_slots if s["start_dt"] <= datetime(2026, 11, 8) and s["start_dt"] >= datetime(2026, 11, 1) and s["id"] not in used_slot_ids), pt4_slots[35])
    used_slot_ids.add(s_past2["id"])
    s_past2["status"] = "BOOKED"
    b_done_rev2 = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e2_id,
        "student_id": 10,
        "slot_id": s_past2["id"],
        "session_fee": 400000.0,
        "status": "COMPLETED",
        "student_note": "Buổi Pilates thon gọn eo",
        "created_at": "2026-11-03 08:00:00"
    }
    bookings.append(b_done_rev2)
    reviews.append({
        "id": review_id_seq,
        "booking_id": b_done_rev2["id"],
        "student_id": 10,
        "pt_id": 4,
        "rating": 5,
        "comment": "Cô Hà dạy Pilates rất nhẹ nhàng và dễ hiểu. Sau 1 buổi tập thấy các khớp được thư giãn rõ rệt.",
        "created_at": "2026-11-05 12:00:00"
    })
    review_id_seq += 1
    attendance.append({
        "id": attendance_id_seq,
        "booking_id": b_done_rev2["id"],
        "check_in_time": s_past2["start_time"],
        "check_out_time": s_past2["end_time"],
        "verification_method": "GEO_LOCATION",
        "student_confirmed": True,
        "pt_confirmed": True,
        "status": "PRESENT"
    })
    attendance_id_seq += 1
    booking_id_seq += 1

    # Ca 6: ĐÃ HỦY (CANCELLED) - Trong quá khứ gần (08/11/2026)
    s_past3 = next((s for s in pt1_slots if datetime(2026, 11, 1) <= s["start_dt"] <= datetime(2026, 11, 8) and s["id"] not in used_slot_ids), pt1_slots[38])
    if not s_past3:
        s_past3 = pt1_slots[38]
    b_canc = {
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1_id,
        "student_id": 10,
        "slot_id": s_past3["id"],
        "session_fee": 300000.0,
        "status": "CANCELLED",
        "student_note": "Hủy do bận việc công ty",
        "created_at": "2026-11-06 10:00:00"
    }
    bookings.append(b_canc)
    cancellations.append({
        "id": cancel_id_seq,
        "booking_id": b_canc["id"],
        "cancelled_by_id": 10,
        "cancelled_by_role": "STUDENT",
        "reason": "Bận việc đột xuất tại công ty không kịp đến phòng tập",
        "cancelled_at": "2026-11-07 12:00:00",
        "hours_before_session": 31.0,
        "refund_amount": 300000.0,
        "compensation_amount": 0.0,
        "penalty_amount": 0.0,
        "status": "PROCESSED"
    })
    cancel_id_seq += 1
    booking_id_seq += 1

    # 5.2 Tạo Bookings cho các học viên khác & các HLV để test toàn bộ giao diện
    review_comments = [
        "Huấn luyện viên rất nhiệt tình và chỉ dẫn chuẩn form!",
        "Buổi tập rất hiệu quả, cơ bắp được kích hoạt tối đa.",
        "PT tận tâm, luôn theo sát và động viên học viên trong từng set tập.",
        "Rất hài lòng với lộ trình huấn luyện cá nhân hóa rõ ràng.",
        "PT đến đúng giờ, phòng tập sạch sẽ và bài tập không nhàm chán.",
        "Sau 1 tháng tập luyện cảm thấy thể lực và vóc dáng cải thiện thấy rõ.",
        "Chỉ dẫn chi tiết chế độ ăn uống bổ trợ rất hữu ích.",
        "HLV chuyên môn cao, giải thích cặn kẽ cơ chế vận động từng nhóm cơ."
    ]

    cancel_reasons = [
        "Bận việc đột xuất tại công ty",
        "Thời tiết mưa bão ngập đường không di chuyển được",
        "Bị cảm sốt nhẹ cần nghỉ ngơi hồi phục",
        "Trùng lịch công tác đột xuất cuối tuần",
        "Có việc gia đình phát sinh gấp"
    ]

    # Duyệt qua các hợp đồng khác
    for enroll in enrollments[3:]:
        pt_id = enroll["pt_id"]
        stud_id = enroll["student_id"]
        session_fee = round(enroll["final_price"] / enroll["total_sessions"], 2)

        avail_slots = [s for s in pt_slot_schedule.get(pt_id, []) if s["id"] not in used_slot_ids]
        if not avail_slots:
            continue

        num_sessions = min(len(avail_slots), random.randint(3, 6))
        chosen_slots = random.sample(avail_slots, k=num_sessions)

        for s in chosen_slots:
            b_id = booking_id_seq
            booking_id_seq += 1

            slot_dt = s["start_dt"]

            # Phân loại trạng thái theo mốc NOW_PIVOT (14/11/2026)
            if slot_dt < NOW_PIVOT - timedelta(days=1):
                # Quá khứ: 85% COMPLETED, 15% CANCELLED
                status = "COMPLETED" if random.random() < 0.85 else "CANCELLED"
            elif slot_dt <= NOW_PIVOT + timedelta(days=1):
                # Hôm nay / ngày mai: 60% CONFIRMED, 40% PENDING
                status = "CONFIRMED" if random.random() < 0.6 else "PENDING"
            else:
                # Tương lai: 50% CONFIRMED, 50% PENDING (để PT vào luôn có ca PENDING để duyệt)
                status = "PENDING" if random.random() < 0.5 else "CONFIRMED"

            if status != "CANCELLED":
                used_slot_ids.add(s["id"])
                s["status"] = "BOOKED"
                enroll["remaining_sessions"] = max(0, enroll["remaining_sessions"] - 1)

            b_obj = {
                "id": b_id,
                "booking_type": "PACKAGE",
                "enrollment_id": enroll["id"],
                "student_id": stud_id,
                "slot_id": s["id"],
                "session_fee": session_fee,
                "status": status,
                "student_note": random.choice(["Học viên tập đúng giờ", "Nhờ HLV mang dây kháng lực", "Đã khởi động trước 10 phút", None]),
                "created_at": (slot_dt - timedelta(days=random.randint(1, 4))).strftime("%Y-%m-%d %H:%M:%S")
            }
            bookings.append(b_obj)

            # Nếu COMPLETED: 80% có review, 100% có attendance
            if status == "COMPLETED":
                if random.random() < 0.8:
                    reviews.append({
                        "id": review_id_seq,
                        "booking_id": b_id,
                        "student_id": stud_id,
                        "pt_id": pt_id,
                        "rating": random.choice([4, 5, 5, 5, 4, 5, 3]),
                        "comment": random.choice(review_comments),
                        "created_at": (slot_dt + timedelta(hours=random.randint(1, 5))).strftime("%Y-%m-%d %H:%M:%S")
                    })
                    review_id_seq += 1

                # Điểm danh ca tập
                attendance.append({
                    "id": attendance_id_seq,
                    "booking_id": b_id,
                    "check_in_time": s["start_time"],
                    "check_out_time": s["end_time"],
                    "verification_method": random.choice(["QR_CODE", "OTP", "GEO_LOCATION"]),
                    "student_confirmed": True,
                    "pt_confirmed": True,
                    "status": "PRESENT" if random.random() < 0.9 else "LATE"
                })
                attendance_id_seq += 1

            # Nếu CANCELLED: ghi nhận lịch sử hủy
            if status == "CANCELLED":
                canceller_role = random.choice(["STUDENT", "PT"])
                canceller_id = stud_id if canceller_role == "STUDENT" else pt_profile_map[pt_id]["user_id"]
                cancellations.append({
                    "id": cancel_id_seq,
                    "booking_id": b_id,
                    "cancelled_by_id": canceller_id,
                    "cancelled_by_role": canceller_role,
                    "reason": random.choice(cancel_reasons),
                    "cancelled_at": (slot_dt - timedelta(hours=random.randint(10, 48))).strftime("%Y-%m-%d %H:%M:%S"),
                    "hours_before_session": float(random.randint(10, 48)),
                    "refund_amount": session_fee if canceller_role == "STUDENT" else 0.0,
                    "compensation_amount": 0.0,
                    "penalty_amount": 0.0,
                    "status": "PROCESSED"
                })
                cancel_id_seq += 1

    # 5.3 Thêm một số ca học thử (TRIAL) cho các học viên mới
    for student in student_users[20:28]:
        for pt in random.sample(active_pts, k=1):
            avail_s = [s for s in pt_slot_schedule.get(pt["id"], []) if s["id"] not in used_slot_ids]
            if not avail_s:
                continue
            s = avail_s[0]
            used_slot_ids.add(s["id"])
            s["status"] = "BOOKED"

            b_id = booking_id_seq
            booking_id_seq += 1

            slot_dt = s["start_dt"]
            status = "COMPLETED" if slot_dt < NOW_PIVOT else "CONFIRMED"

            bookings.append({
                "id": b_id,
                "booking_type": "TRIAL",
                "enrollment_id": None,
                "student_id": student["id"],
                "pt_id": pt["id"],
                "slot_id": s["id"],
                "session_fee": 0.0,
                "status": status,
                "student_note": "Đăng ký buổi tập thử đánh giá thể lực miễn phí",
                "created_at": (slot_dt - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            })

            if status == "COMPLETED":
                attendance.append({
                    "id": attendance_id_seq,
                    "booking_id": b_id,
                    "check_in_time": s["start_time"],
                    "check_out_time": s["end_time"],
                    "verification_method": "QR_CODE",
                    "student_confirmed": True,
                    "pt_confirmed": True,
                    "status": "PRESENT"
                })
                attendance_id_seq += 1

    # =========================================================================
    # 6. WORKOUT PLANS & WORKOUTS (Giáo án & Bài tập)
    # Tuân thủ BCNF và exercise_order (1..N)
    # =========================================================================
    workout_plans = []
    workouts = []
    plan_id_seq = 1
    workout_id_seq = 1

    exercise_catalog = [
        ("Barbell Squat", "Cơ đùi trước & Mông", 4, 10, 50.0, 90),
        ("Bench Press", "Cơ ngực & Tay sau", 4, 8, 45.0, 90),
        ("Romanian Deadlift", "Cơ đùi sau & Lưng dưới", 3, 10, 40.0, 75),
        ("Lat Pulldown", "Cơ lưng xô", 4, 12, 35.0, 60),
        ("Dumbbell Shoulder Press", "Cơ vai", 3, 10, 12.0, 60),
        ("Plank Siết Core", "Cơ bụng & Trọng tâm", 3, 1, 0.0, 60),
        ("Walking Lunges", "Cơ mông & Đùi", 3, 12, 10.0, 60),
        ("Cable Bicep Curl", "Cơ tay trước", 3, 12, 15.0, 45),
        ("Leg Extension", "Cơ đùi trước", 4, 12, 30.0, 60),
        ("Pilates Roll Up", "Cơ bụng & Giãn cột sống", 3, 10, 0.0, 45),
        ("Boxing 1-2 Combo Punch", "Phản xạ vai & Tim mạch", 4, 20, 0.0, 60)
    ]

    # Gán giáo án cho 15 hợp đồng đầu tiên (bao gồm cả 2 khóa active của Student A)
    for enroll in enrollments[:15]:
        p_id = plan_id_seq
        plan_id_seq += 1

        wp_title = f"Giáo án rèn luyện thể lực cá nhân hóa HD #{enroll['id']:04d}"
        if enroll["student_id"] == 10:
            if enroll["course_id"] == 1:
                wp_title = "Giáo án Thể lực & Nhập môn Gym chuẩn Form (Nguyễn Văn A)"
            elif enroll["course_id"] == 8:
                wp_title = "Lộ trình Pilates Phục hồi Cột sống & Siết eo (Nguyễn Văn A)"

        workout_plans.append({
            "id": p_id,
            "enrollment_id": enroll["id"],
            "pt_id": enroll["pt_id"],
            "title": wp_title,
            "goal": "Tăng cường sức bền, phát triển khối cơ nạc và đốt mỡ thừa",
            "start_date": enroll["start_date"],
            "end_date": enroll["end_date"]
        })

        # Gán từ 4 - 6 bài tập với exercise_order từ 1..N
        chosen_ex = random.sample(exercise_catalog, k=random.randint(4, 6))
        for order_idx, (ex_name, muscle, sets, reps, weight, rest) in enumerate(chosen_ex, start=1):
            workouts.append({
                "id": workout_id_seq,
                "plan_id": p_id,
                "exercise_order": order_idx,
                "exercise_name": ex_name,
                "target_muscle": muscle,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight,
                "rest_seconds": rest,
                "video_demo_url": f"https://storage.ptconnect.vn/videos/{ex_name.lower().replace(' ', '_')}.mp4"
            })
            workout_id_seq += 1

    # =========================================================================
    # 7. TẠO CÁC CÂU LỆNH SQL INSERT THEO THỨ TỰ BẢO TOÀN KHÓA NGOẠI
    # =========================================================================

    # 1. users
    sql_lines.append("-- 1. USERS")
    sql_lines.append("INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `status`, `avatar_url`) VALUES")
    u_vals = [f"  ({u['id']}, {escape_sql(u['full_name'])}, {escape_sql(u['email'])}, {escape_sql(u['password_hash'])}, {escape_sql(u['phone'])}, {escape_sql(u['role'])}, {escape_sql(u['status'])}, {escape_sql(u['avatar_url'])})" for u in users]
    sql_lines.append(",\n".join(u_vals) + ";\n")

    # 2. pt_profiles
    sql_lines.append("-- 2. PT PROFILES")
    sql_lines.append("INSERT INTO `pt_profiles` (`id`, `user_id`, `experience_years`, `location_pricing_note`, `certificate_url`, `average_rating`, `total_reviews`, `verification_status`) VALUES")
    pt_vals = [f"  ({p['id']}, {p['user_id']}, {p['experience_years']}, {escape_sql(p['location_pricing_note'])}, {escape_sql(p['certificate_url'])}, {p['average_rating']}, {p['total_reviews']}, {escape_sql(p['verification_status'])})" for p in pt_profiles]
    sql_lines.append(",\n".join(pt_vals) + ";\n")

    # 2b. pt_locations (BCNF)
    sql_lines.append("-- 2b. PT LOCATIONS (BCNF)")
    sql_lines.append("INSERT INTO `pt_locations` (`pt_id`, `location_name`) VALUES")
    loc_vals = []
    for p in pt_profiles:
        raw_locs = p.get("available_locations", "")
        if raw_locs:
            for l in raw_locs.split(";"):
                l_clean = l.strip()
                if l_clean:
                    loc_vals.append(f"  ({p['id']}, {escape_sql(l_clean)})")
    sql_lines.append(",\n".join(loc_vals) + ";\n")

    # 3. wallets
    sql_lines.append("-- 3. WALLETS")
    sql_lines.append("INSERT INTO `wallets` (`id`, `user_id`, `balance`, `locked_balance`, `currency`, `status`) VALUES")
    w_vals = [f"  ({w['id']}, {w['user_id']}, {w['balance']:.2f}, {w['locked_balance']:.2f}, 'VND', 'ACTIVE')" for w in wallets]
    sql_lines.append(",\n".join(w_vals) + ";\n")

    # 4. courses
    sql_lines.append("-- 4. COURSES")
    sql_lines.append("INSERT INTO `courses` (`id`, `pt_id`, `title`, `description`, `total_sessions`, `validity_days`, `base_price`, `status`) VALUES")
    c_vals = [f"  ({c['id']}, {c['pt_id']}, {escape_sql(c['title'])}, {escape_sql(c['description'])}, {c['total_sessions']}, {c['validity_days']}, {c['base_price']:.2f}, {escape_sql(c['status'])})" for c in courses]
    sql_lines.append(",\n".join(c_vals) + ";\n")

    # 5. enrollments
    sql_lines.append("-- 5. ENROLLMENTS (BCNF: pt_id derived via courses.pt_id)")
    sql_lines.append("INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `training_location`, `final_price`, `total_sessions`, `remaining_sessions`, `start_date`, `end_date`, `contract_url`, `status`) VALUES")
    e_vals = [f"  ({e['id']}, {e['student_id']}, {e['course_id']}, {escape_sql(e['training_location'])}, {e['final_price']:.2f}, {e['total_sessions']}, {e['remaining_sessions']}, {escape_sql(e['start_date'])}, {escape_sql(e['end_date'])}, {escape_sql(e['contract_url'])}, {escape_sql(e['status'])})" for e in enrollments]
    sql_lines.append(",\n".join(e_vals) + ";\n")

    # 6. availability_slots (Khởi tạo AVAILABLE để trigger trg_bookings_before_insert kiểm tra hợp lệ)
    sql_lines.append("-- 6. AVAILABILITY SLOTS")
    sql_lines.append("INSERT INTO `availability_slots` (`id`, `pt_id`, `start_time`, `end_time`, `status`) VALUES")
    s_vals = [f"  ({s['id']}, {s['pt_id']}, {escape_sql(s['start_time'])}, {escape_sql(s['end_time'])}, 'AVAILABLE')" for s in slots]
    sql_lines.append(",\n".join(s_vals) + ";\n")

    # 7. bookings
    sql_lines.append("-- 7. BOOKINGS (Trigger trg_bookings_after_insert sẽ tự động cập nhật slot sang BOOKED)")
    sql_lines.append("INSERT INTO `bookings` (`id`, `booking_type`, `enrollment_id`, `student_id`, `slot_id`, `session_fee`, `status`, `student_note`, `created_at`) VALUES")
    b_vals = [f"  ({b['id']}, {escape_sql(b['booking_type'])}, {escape_sql(b['enrollment_id'])}, {b['student_id']}, {b['slot_id']}, {b['session_fee']:.2f}, {escape_sql(b['status'])}, {escape_sql(b['student_note'])}, {escape_sql(b['created_at'])})" for b in bookings]
    sql_lines.append(",\n".join(b_vals) + ";\n")

    # 8. attendance
    if attendance:
        sql_lines.append("-- 8. ATTENDANCE (Điểm danh ca tập COMPLETED)")
        sql_lines.append("INSERT INTO `attendance` (`id`, `booking_id`, `check_in_time`, `check_out_time`, `verification_method`, `student_confirmed`, `pt_confirmed`, `status`) VALUES")
        att_vals = [f"  ({a['id']}, {a['booking_id']}, {escape_sql(a['check_in_time'])}, {escape_sql(a['check_out_time'])}, {escape_sql(a['verification_method'])}, {1 if a['student_confirmed'] else 0}, {1 if a['pt_confirmed'] else 0}, {escape_sql(a['status'])})" for a in attendance]
        sql_lines.append(",\n".join(att_vals) + ";\n")

    # 9. reviews
    if reviews:
        sql_lines.append("-- 9. REVIEWS")
        sql_lines.append("INSERT INTO `reviews` (`id`, `booking_id`, `rating`, `comment`, `created_at`) VALUES")
        r_vals = [f"  ({r['id']}, {r['booking_id']}, {r['rating']}, {escape_sql(r['comment'])}, {escape_sql(r['created_at'])})" for r in reviews]
        sql_lines.append(",\n".join(r_vals) + ";\n")

    # 10. cancellations
    if cancellations:
        # Giả lập 1 ca phạt bị thâm hụt số dư để test hiển thị số dư 0đ + nợ tiền phạt
        cancellations[0]["penalty_shortfall"] = 200000.0
        cancellations[0]["penalty_amount"] = 200000.0
        sql_lines.append("-- 10. CANCELLATIONS")
        sql_lines.append("INSERT INTO `cancellations` (`id`, `booking_id`, `cancelled_by_id`, `cancelled_by_role`, `reason`, `cancelled_at`, `hours_before_session`, `refund_amount`, `compensation_amount`, `penalty_amount`, `penalty_shortfall`, `status`) VALUES")
        cn_vals = [f"  ({cn['id']}, {cn['booking_id']}, {escape_sql(cn['cancelled_by_id'])}, {escape_sql(cn['cancelled_by_role'])}, {escape_sql(cn['reason'])}, {escape_sql(cn['cancelled_at'])}, {cn['hours_before_session']}, {cn['refund_amount']:.2f}, {cn['compensation_amount']:.2f}, {cn['penalty_amount']:.2f}, {cn.get('penalty_shortfall', 0.0):.2f}, {escape_sql(cn['status'])})" for cn in cancellations]
        sql_lines.append(",\n".join(cn_vals) + ";\n")

    # 10b. booking_disputes (Khiếu nại & Tranh chấp ca tập)
    disputes = [
        {
            "id": 1,
            "booking_id": 1,
            "sender_id": 10,
            "sender_role": "STUDENT",
            "dispute_type": "WRONG_ABSENT",
            "reason": "Em có mặt tại phòng tập đúng giờ nhưng PT điểm danh vắng mặt nhầm. Em gửi kèm ảnh chụp check-in tại quầy lễ tân lúc 14h00.",
            "evidence_url": "/static/uploads/evidence_checkin_gym.jpg",
            "counter_evidence_url": None,
            "counter_argument": None,
            "status": "PENDING",
            "admin_notes": None,
            "deadline_at": (NOW_PIVOT + timedelta(hours=36)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "created_at": (NOW_PIVOT - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 2,
            "booking_id": 2,
            "sender_id": 11,
            "sender_role": "STUDENT",
            "dispute_type": "PT_NO_SHOW",
            "reason": "HLV không đến điểm hẹn và không thông báo trước.",
            "evidence_url": "/static/uploads/evidence_chat.jpg",
            "counter_evidence_url": "/static/uploads/counter_evidence_pt.jpg",
            "counter_argument": "Tôi bị hỏng xe trên đường đến và đã nhắn tin thông báo trước 15 phút, sẵn sàng bù ca vào ngày mai.",
            "status": "EVIDENCE_REQUESTED",
            "admin_notes": "Admin đã nhận phản biện từ HLV, đang tiến hành đối chiếu đối chứng camera phòng tập.",
            "deadline_at": (NOW_PIVOT + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "created_at": (NOW_PIVOT - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 3,
            "booking_id": 3,
            "sender_id": 12,
            "sender_role": "STUDENT",
            "dispute_type": "CONTRACT_TERMINATION",
            "reason": "HLV không đến muộn và thay đổi lịch không báo trước. Đề nghị chấm dứt hợp đồng và hoàn tiền các buổi còn lại.",
            "evidence_url": "/static/uploads/evidence_schedule_logs.jpg",
            "counter_evidence_url": None,
            "counter_argument": "Tôi đồng ý chấm dứt hợp đồng do thời gian tới tôi chuyển công tác, nhờ Admin hỗ trợ hoàn tiền các buổi còn lại cho học viên.",
            "status": "PENDING",
            "admin_notes": "Admin đang xem xét yêu cầu chấm dứt hợp đồng của học viên và ý kiến đồng thuận từ HLV.",
            "deadline_at": (NOW_PIVOT + timedelta(hours=18)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "created_at": (NOW_PIVOT - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 4,
            "booking_id": 4,
            "sender_id": 2,
            "sender_role": "PT",
            "dispute_type": "STUDENT_NO_SHOW",
            "reason": "Học viên không đến nhưng phản ánh sai sự thật rằng HLV vắng mặt.",
            "evidence_url": "/static/uploads/pt_checkin.jpg",
            "counter_evidence_url": None,
            "counter_argument": None,
            "status": "PENDING",
            "admin_notes": None,
            "deadline_at": (NOW_PIVOT + timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "created_at": (NOW_PIVOT - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 5,
            "booking_id": 5,
            "sender_id": 10,
            "sender_role": "STUDENT",
            "dispute_type": "ATTITUDE_QUALITY",
            "reason": "HLV thái độ gắt gỏng và tự ý kết thúc buổi tập sớm 20 phút mà không có lý do chính đáng.",
            "evidence_url": "/static/uploads/evidence_chat.jpg",
            "counter_evidence_url": None,
            "counter_argument": "Tôi đã giải thích với học viên do có ca tập đột xuất, tôi nhận sai sót.",
            "status": "RESOLVED_REFUND",
            "admin_notes": "Admin đã xác minh vi phạm kỷ luật của HLV. Đã chấp thuận khiếu nại và hoàn trả 1 buổi tập vào hợp đồng học viên.",
            "deadline_at": None,
            "resolved_at": (NOW_PIVOT - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": (NOW_PIVOT - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 6,
            "booking_id": 6,
            "sender_id": 13,
            "sender_role": "STUDENT",
            "dispute_type": "STUDENT_NO_SHOW",
            "reason": "Học viên phản ánh HLV không xuất hiện tại phòng tập lúc 18h00.",
            "evidence_url": "/static/uploads/evidence_checkin_gym.jpg",
            "counter_evidence_url": "/static/uploads/counter_evidence_pt.jpg",
            "counter_argument": "Camera phòng tập chứng minh tôi đã có mặt từ 17h50 đến 18h30 tại sảnh chính nhưng học viên không đến.",
            "status": "REJECTED",
            "admin_notes": "Admin đã đối chiếu dữ liệu camera và nhật ký ra vào phòng tập. Bác bỏ khiếu nại của học viên do HLV có mặt đúng giờ.",
            "deadline_at": None,
            "resolved_at": (NOW_PIVOT - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": (NOW_PIVOT - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    sql_lines.append("-- 10b. BOOKING DISPUTES")
    sql_lines.append("INSERT INTO `booking_disputes` (`id`, `booking_id`, `sender_id`, `sender_role`, `dispute_type`, `reason`, `evidence_url`, `counter_evidence_url`, `counter_argument`, `status`, `admin_notes`, `deadline_at`, `resolved_at`, `created_at`) VALUES")
    disp_vals = [f"  ({d['id']}, {d['booking_id']}, {d['sender_id']}, '{d['sender_role']}', '{d['dispute_type']}', {escape_sql(d['reason'])}, {escape_sql(d['evidence_url'])}, {escape_sql(d['counter_evidence_url'])}, {escape_sql(d['counter_argument'])}, '{d['status']}', {escape_sql(d['admin_notes'])}, {escape_sql(d['deadline_at'])}, {escape_sql(d['resolved_at'])}, '{d['created_at']}')" for d in disputes]
    sql_lines.append(",\n".join(disp_vals) + ";\n")

    # 11. payments
    if payments:
        sql_lines.append("-- 11. PAYMENTS")
        sql_lines.append("INSERT INTO `payments` (`id`, `wallet_id`, `enrollment_id`, `amount`, `payment_type`, `payment_method`, `status`, `transaction_ref`, `created_at`) VALUES")
        pay_vals = [f"  ({p['id']}, {p['wallet_id']}, {escape_sql(p['enrollment_id'])}, {p['amount']:.2f}, {escape_sql(p['payment_type'])}, {escape_sql(p['payment_method'])}, {escape_sql(p['status'])}, {escape_sql(p['transaction_ref'])}, {escape_sql(p['created_at'])})" for p in payments]
        sql_lines.append(",\n".join(pay_vals) + ";\n")

    # 11b. wallet_audit_logs (Sổ cái kiểm toán biến động số dư)
    sql_lines.append("-- 11b. WALLET AUDIT LOGS (Nhật ký biến động tài chính)")
    sql_lines.append("INSERT INTO `wallet_audit_logs` (`id`, `wallet_id`, `old_balance`, `new_balance`, `old_locked_balance`, `new_locked_balance`, `action_type`, `reason`, `created_at`) VALUES")
    wal_records = [
        (1, 10, 0.0, 20000000.0, 0.0, 0.0, "TOPUP", "Nạp tiền ví điện tử qua chuyển khoản ngân hàng", "2026-08-01 09:00:00"),
        (2, 10, 20000000.0, 14400000.0, 0.0, 0.0, "PAYMENT", "Thanh toán mua Gói Boxing Thể Lực - HLV Bảo", "2026-08-01 09:30:00"),
        (3, 10, 14400000.0, 24400000.0, 0.0, 0.0, "TOPUP", "Nạp thêm tiền ví điện tử", "2026-10-14 15:00:00"),
        (4, 10, 24400000.0, 20800000.0, 0.0, 0.0, "PAYMENT", "Thanh toán mua Khóa Khởi Động Nhập Môn - HLV Cường", "2026-10-15 10:00:00"),
        (5, 10, 20800000.0, 12800000.0, 0.0, 0.0, "PAYMENT", "Thanh toán mua Gói Pilates Chỉnh Dáng - HLV Hà", "2026-11-01 08:30:00"),
        (6, 10, 12800000.0, 13100000.0, 0.0, 0.0, "REFUND", "Hoàn tiền ca tập hủy trước 24h", "2026-11-08 19:30:00"),
        (7, 10, 13100000.0, 13200000.0, 0.0, 0.0, "COMPENSATION", "Nhận bồi thường HLV hủy ca gấp", "2026-11-10 14:00:00"),
    ]
    wal_vals = [f"  ({aid}, {wid}, {old_b:.2f}, {new_b:.2f}, {old_l:.2f}, {new_l:.2f}, '{act}', {escape_sql(rsn)}, '{c_at}')" for aid, wid, old_b, new_b, old_l, new_l, act, rsn, c_at in wal_records]
    sql_lines.append(",\n".join(wal_vals) + ";\n")

    # 12. workout_plans
    if workout_plans:
        sql_lines.append("-- 12. WORKOUT PLANS (BCNF: pt_id derived via enrollments -> courses.pt_id)")
        sql_lines.append("INSERT INTO `workout_plans` (`id`, `enrollment_id`, `title`, `goal`, `start_date`, `end_date`) VALUES")
        wp_vals = [f"  ({wp['id']}, {wp['enrollment_id']}, {escape_sql(wp['title'])}, {escape_sql(wp['goal'])}, {escape_sql(wp['start_date'])}, {escape_sql(wp['end_date'])})" for wp in workout_plans]
        sql_lines.append(",\n".join(wp_vals) + ";\n")

    # 13. workouts
    if workouts:
        sql_lines.append("-- 13. WORKOUTS (exercise_order là discriminator/partial key của thực thể yếu)")
        sql_lines.append("INSERT INTO `workouts` (`id`, `plan_id`, `exercise_order`, `exercise_name`, `target_muscle`, `sets`, `reps`, `weight_kg`, `rest_seconds`, `video_demo_url`) VALUES")
        wo_vals = [f"  ({wo['id']}, {wo['plan_id']}, {wo['exercise_order']}, {escape_sql(wo['exercise_name'])}, {escape_sql(wo['target_muscle'])}, {wo['sets']}, {wo['reps']}, {wo['weight_kg']:.2f}, {wo['rest_seconds']}, {escape_sql(wo['video_demo_url'])})" for wo in workouts]
        sql_lines.append(",\n".join(wo_vals) + ";\n")

    # 14. Đồng bộ chỉ số đánh giá của PT
    sql_lines.append("-- 14. ĐỒNG BỘ CHỈ SỐ ĐÁNH GIÁ CỦA PT THEO REVIEWS THỰC TẾ")
    sql_lines.append("UPDATE `pt_profiles` p")
    sql_lines.append("SET")
    sql_lines.append("  `average_rating` = COALESCE((")
    sql_lines.append("    SELECT ROUND(AVG(r.`rating`), 2)")
    sql_lines.append("    FROM `reviews` r")
    sql_lines.append("    JOIN `bookings` b ON r.`booking_id` = b.`id`")
    sql_lines.append("    JOIN `availability_slots` s ON b.`slot_id` = s.`id`")
    sql_lines.append("    WHERE s.`pt_id` = p.`id`")
    sql_lines.append("  ), 0),")
    sql_lines.append("  `total_reviews` = (")
    sql_lines.append("    SELECT COUNT(*)")
    sql_lines.append("    FROM `reviews` r")
    sql_lines.append("    JOIN `bookings` b ON r.`booking_id` = b.`id`")
    sql_lines.append("    JOIN `availability_slots` s ON b.`slot_id` = s.`id`")
    sql_lines.append("    WHERE s.`pt_id` = p.`id`")
    sql_lines.append("  );")
    sql_lines.append("")
    sql_lines.append("-- HOÀN TẤT DỮ LIỆU SEED DEMO.")

    full_sql_content = "\n".join(sql_lines)
    for out_path in OUTPUT_FILES:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_sql_content)
        print(f"-> Đã ghi file seed tại: {out_path}")

    print("\nTHỐNG KÊ DỮ LIỆU ĐÃ SINH:")
    print(f"   * Users: {len(users)} (1 Admin, {len(pt_profiles)} PT, {len(student_users)} Students)")
    print(f"   * Wallets: {len(wallets)}")
    print(f"   * Courses: {len(courses)}")
    print(f"   * Slots: {len(slots)} (Có các khung giờ rảnh kéo dài đến tháng 1/2027)")
    print(f"   * Enrollments: {len(enrollments)}")
    print(f"   * Bookings: {len(bookings)} (Package: {len([b for b in bookings if b['booking_type'] == 'PACKAGE'])}, Trial: {len([b for b in bookings if b['booking_type'] == 'TRIAL'])})")
    print(f"   * Attendance: {len(attendance)} bản ghi điểm danh")
    print(f"   * Reviews: {len(reviews)} đánh giá")
    print(f"   * Cancellations: {len(cancellations)} ca hủy kèm lý do")
    print(f"   * Payments: {len(payments)} giao dịch nạp/mua/hoàn")
    print(f"   * Workout Plans: {len(workout_plans)} giáo án ({len(workouts)} bài tập)")

    # Tự động nạp vào MySQL container
    print("\nĐang tự động nạp dữ liệu mẫu vào MySQL container...")
    res_cp = subprocess.run([
        "docker", "cp", OUTPUT_FILES[0], "ptconnect-mysql:/tmp/seed_demo.sql"
    ], capture_output=True, text=True)

    if res_cp.returncode == 0:
        res_sql = subprocess.run([
            "docker", "exec", "ptconnect-mysql", "mysql", "-uroot", "-proot123",
            "--default-character-set=utf8mb4", "ptconnect", "-e", "source /tmp/seed_demo.sql;"
        ], capture_output=True, text=True)
        if res_sql.returncode == 0:
            print("==> NẠP DỮ LIỆU THÀNH CÔNG VÀO MYSQL (100% Font Tiếng Việt UTF-8 chuẩn xác)!")
        else:
            print(f"Lỗi thực thi SQL: {res_sql.stderr}")
    else:
        print(f"Lỗi sao chép file vào container: {res_cp.stderr}")


if __name__ == "__main__":
    main()
