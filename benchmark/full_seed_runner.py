import sys
import os
import random
from datetime import datetime, timedelta
import pymysql

def run_seed():
    print("Ket noi toi MySQL port 3307...")
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="root123",
        database="ptconnect",
        autocommit=False,
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    try:
        print("Toi uu hoa he thong: Tat kiem tra khoa ngoai va che do ghi bulk...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SET UNIQUE_CHECKS = 0;")
        cursor.execute("SET sql_log_bin = 0;")

        locations = ["Quận 1", "Quận 3", "Quận 7", "Bình Thạnh", "Cầu Giấy", "Đống Đa", "Thanh Xuân", "Hải Châu", "Sơn Trà", "Tân Bình", "Hà Đông"]
        base_time = datetime(2026, 1, 1, 6, 0, 0)

        # 1. USERS & WALLETS (20,000)
        print("1/12 Dang chen 20,000 Users va Wallets...")
        user_rows = []
        wallet_rows = []
        for i in range(1, 20001):
            role = "PT" if i <= 5000 else "STUDENT"
            user_rows.append((
                i, f"Nguoi Dung {i}", f"user{i}@ptconnect.vn", "$2b$12$e/e.examplehashnotforlogin123",
                f"090{i:07d}", role, "ACTIVE", base_time + timedelta(minutes=i)
            ))
            wallet_rows.append((
                i, i, 5000000.00, 0.00, "VND", "ACTIVE"
            ))
            if len(user_rows) >= 5000:
                cursor.executemany("INSERT IGNORE INTO users (id, full_name, email, password_hash, phone, role, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", user_rows)
                cursor.executemany("INSERT IGNORE INTO wallets (id, user_id, balance, locked_balance, currency, status) VALUES (%s, %s, %s, %s, %s, %s)", wallet_rows)
                conn.commit()
                user_rows = []
                wallet_rows = []
        if user_rows:
            cursor.executemany("INSERT IGNORE INTO users (id, full_name, email, password_hash, phone, role, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", user_rows)
            cursor.executemany("INSERT IGNORE INTO wallets (id, user_id, balance, locked_balance, currency, status) VALUES (%s, %s, %s, %s, %s, %s)", wallet_rows)
            conn.commit()

        # 2. PT_PROFILES & PT_LOCATIONS (5,000 PTs & 42,505 locations)
        print("2/12 Dang chen PT Profiles va PT Locations...")
        profile_rows = []
        for i in range(1, 5001):
            avg_rating = round(random.uniform(3.5, 5.0), 2)
            profile_rows.append((
                i, i, f"HLV the hinh chuyen nghiep khu vuc {random.choice(locations)}, chuyen tang co giam mo.",
                3 + (i % 12), "https://example.com/cert.pdf", avg_rating, random.randint(10, 500), "VERIFIED"
            ))
            if len(profile_rows) >= 2500:
                cursor.executemany("INSERT IGNORE INTO pt_profiles (id, user_id, bio, experience_years, certificate_url, average_rating, total_reviews, verification_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", profile_rows)
                conn.commit()
                profile_rows = []
        if profile_rows:
            cursor.executemany("INSERT IGNORE INTO pt_profiles (id, user_id, bio, experience_years, certificate_url, average_rating, total_reviews, verification_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", profile_rows)
            conn.commit()

        loc_rows = []
        loc_id = 1
        for pt_id in range(1, 5001):
            chosen = random.sample(locations, k=random.randint(6, 10))
            for l in chosen:
                loc_rows.append((loc_id, pt_id, l))
                loc_id += 1
                if len(loc_rows) >= 10000:
                    cursor.executemany("INSERT IGNORE INTO pt_locations (id, pt_id, location_name) VALUES (%s, %s, %s)", loc_rows)
                    conn.commit()
                    loc_rows = []
        if loc_rows:
            cursor.executemany("INSERT IGNORE INTO pt_locations (id, pt_id, location_name) VALUES (%s, %s, %s)", loc_rows)
            conn.commit()

        # 3. COURSES (1,200) & ENROLLMENTS (15,000)
        print("3/12 Dang chen 1,200 Courses va 15,000 Enrollments...")
        course_rows = []
        for c_id in range(1, 1201):
            pt_id = (c_id % 5000) + 1
            course_rows.append((
                c_id, pt_id, f"Khoa Tap Toan Dien {c_id}", "Giao an ca nhan hoa giam mo tang co",
                12, 60, 3600000.00, "ACTIVE"
            ))
        cursor.executemany("INSERT IGNORE INTO courses (id, pt_id, title, description, total_sessions, validity_days, base_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", course_rows)
        conn.commit()

        enroll_rows = []
        for e_id in range(1, 15001):
            s_id = 5000 + (e_id % 15000) + 1
            c_id = (e_id % 1200) + 1
            enroll_rows.append((
                e_id, s_id, c_id, "Quan 1", 3600000.00, 12, 10,
                base_time.date(), (base_time + timedelta(days=60)).date(),
                "https://example.com/contract.pdf", "ACTIVE"
            ))
            if len(enroll_rows) >= 5000:
                cursor.executemany("INSERT IGNORE INTO enrollments (id, student_id, course_id, training_location, final_price, total_sessions, remaining_sessions, start_date, end_date, contract_url, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", enroll_rows)
                conn.commit()
                enroll_rows = []
        if enroll_rows:
            cursor.executemany("INSERT IGNORE INTO enrollments (id, student_id, course_id, training_location, final_price, total_sessions, remaining_sessions, start_date, end_date, contract_url, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", enroll_rows)
            conn.commit()

        # 4. AVAILABILITY_SLOTS (165,150)
        print("4/12 Dang chen 165,150 Availability Slots...")
        slot_rows = []
        for s_id in range(1, 165151):
            pt_id = (s_id % 5000) + 1
            st = base_time + timedelta(hours=(s_id % 2000))
            et = st + timedelta(hours=1)
            slot_rows.append((s_id, pt_id, st, et, "BOOKED"))
            if len(slot_rows) >= 15000:
                cursor.executemany("INSERT IGNORE INTO availability_slots (id, pt_id, start_time, end_time, status) VALUES (%s, %s, %s, %s, %s)", slot_rows)
                conn.commit()
                slot_rows = []
        if slot_rows:
            cursor.executemany("INSERT IGNORE INTO availability_slots (id, pt_id, start_time, end_time, status) VALUES (%s, %s, %s, %s, %s)", slot_rows)
            conn.commit()

        # 5. BOOKINGS (150,000)
        print("5/12 Dang chen 150,000 Bookings...")
        booking_rows = []
        statuses = ["COMPLETED", "CONFIRMED", "CANCELLED"]
        for b_id in range(1, 150001):
            s_id = 100 if b_id <= 60000 else 5000 + (b_id % 15000) + 1
            st_choice = "COMPLETED" if b_id <= 60000 else statuses[b_id % 3]
            booking_rows.append((
                b_id, s_id, b_id, None, "TRIAL", st_choice, 300000.00,
                base_time + timedelta(minutes=b_id)
            ))
            if len(booking_rows) >= 15000:
                cursor.executemany("INSERT IGNORE INTO bookings (id, student_id, slot_id, enrollment_id, booking_type, status, session_fee, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", booking_rows)
                conn.commit()
                booking_rows = []
        if booking_rows:
            cursor.executemany("INSERT IGNORE INTO bookings (id, student_id, slot_id, enrollment_id, booking_type, status, session_fee, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", booking_rows)
            conn.commit()

        # 6. PAYMENTS (250,000)
        print("6/12 Dang chen 250,000 Payments...")
        pay_rows = []
        pay_types = ["COMPENSATION", "PLATFORM_FEE", "PENALTY", "PURCHASE_PACKAGE", "TOPUP"]
        for p_id in range(1, 250001):
            w_id = 20 if p_id <= 30000 else (p_id % 20000) + 1
            ptype = pay_types[p_id % 5]
            amt = random.choice([50000.00, 150000.00, 300000.00, 500000.00])
            created = base_time + timedelta(minutes=(p_id % 50000))
            pay_rows.append((
                p_id, w_id, None, amt, ptype, "WALLET", "SUCCESS", f"TXN-{p_id}", created
            ))
            if len(pay_rows) >= 20000:
                cursor.executemany("INSERT IGNORE INTO payments (id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", pay_rows)
                conn.commit()
                pay_rows = []
        if pay_rows:
            cursor.executemany("INSERT IGNORE INTO payments (id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", pay_rows)
            conn.commit()

        # 7. BOOKING_DISPUTES (50,000)
        print("7/12 Dang chen 50,000 Booking Disputes...")
        disp_rows = []
        for d_id in range(1, 50001):
            disp_rows.append((
                d_id, d_id, 100, "WRONG_ABSENT", "Khieu nai vang mat khong ly do", "PENDING"
            ))
            if len(disp_rows) >= 10000:
                cursor.executemany("INSERT IGNORE INTO booking_disputes (id, booking_id, sender_id, dispute_type, reason, status) VALUES (%s, %s, %s, %s, %s, %s)", disp_rows)
                conn.commit()
                disp_rows = []
        if disp_rows:
            cursor.executemany("INSERT IGNORE INTO booking_disputes (id, booking_id, sender_id, dispute_type, reason, status) VALUES (%s, %s, %s, %s, %s, %s)", disp_rows)
            conn.commit()

        # 8. REVIEWS (45,000)
        print("8/12 Dang chen 45,000 Reviews...")
        rev_rows = []
        for r_id in range(1, 45001):
            rev_rows.append((r_id, r_id, random.randint(4, 5), "Buoi tap rat tot, PT nhiet tinh."))
            if len(rev_rows) >= 15000:
                cursor.executemany("INSERT IGNORE INTO reviews (id, booking_id, rating, comment) VALUES (%s, %s, %s, %s)", rev_rows)
                conn.commit()
                rev_rows = []
        if rev_rows:
            cursor.executemany("INSERT IGNORE INTO reviews (id, booking_id, rating, comment) VALUES (%s, %s, %s, %s)", rev_rows)
            conn.commit()

        # 9. ATTENDANCE (75,000)
        print("9/12 Dang chen 75,000 Attendance...")
        att_rows = []
        for a_id in range(1, 75001):
            st = base_time + timedelta(hours=a_id % 500)
            et = st + timedelta(minutes=55)
            att_rows.append((a_id, a_id, st, et, "QR_CODE", True, True, "PRESENT"))
            if len(att_rows) >= 15000:
                cursor.executemany("INSERT IGNORE INTO attendance (id, booking_id, check_in_time, check_out_time, verification_method, student_confirmed, pt_confirmed, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", att_rows)
                conn.commit()
                att_rows = []
        if att_rows:
            cursor.executemany("INSERT IGNORE INTO attendance (id, booking_id, check_in_time, check_out_time, verification_method, student_confirmed, pt_confirmed, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", att_rows)
            conn.commit()

        # 10. CANCELLATIONS (12,000)
        print("10/12 Dang chen 12,000 Cancellations...")
        canc_rows = []
        for c_id in range(1, 12001):
            b_id = 75000 + c_id
            canc_rows.append((
                c_id, b_id, 100, "STUDENT", "Ban viec dot xuat", base_time,
                26.5, 300000.00, 0.00, 0.00, 0.00, "PROCESSED"
            ))
            if len(canc_rows) >= 6000:
                cursor.executemany("INSERT IGNORE INTO cancellations (id, booking_id, cancelled_by_id, cancelled_by_role, reason, cancelled_at, hours_before_session, refund_amount, compensation_amount, penalty_amount, penalty_shortfall, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", canc_rows)
                conn.commit()
                canc_rows = []
        if canc_rows:
            cursor.executemany("INSERT IGNORE INTO cancellations (id, booking_id, cancelled_by_id, cancelled_by_role, reason, cancelled_at, hours_before_session, refund_amount, compensation_amount, penalty_amount, penalty_shortfall, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", canc_rows)
            conn.commit()

        # 11. WORKOUT_PLANS (8,000) & WORKOUTS (40,000)
        print("11/12 Dang chen 8,000 Plans va 40,000 Workouts...")
        plan_rows = []
        for pl_id in range(1, 8001):
            e_id = (pl_id % 15000) + 1
            plan_rows.append((
                pl_id, e_id, f"Giao an thang {pl_id}", "Tang co nguc va xô",
                base_time.date(), (base_time + timedelta(days=30)).date()
            ))
        cursor.executemany("INSERT IGNORE INTO workout_plans (id, enrollment_id, title, goal, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s)", plan_rows)
        conn.commit()

        wo_rows = []
        exercises = ["Bench Press", "Incline Dumbbell Press", "Barbell Squat", "Romanian Deadlift", "Pull Up"]
        muscles = ["Ngực", "Ngực trên", "Đùi trước", "Đùi sau", "Lưng xô"]
        w_id = 1
        for pl_id in range(1, 8001):
            for order in range(1, 6):
                wo_rows.append((
                    w_id, pl_id, order, exercises[order - 1], muscles[order - 1], 4, 10, 60.00, 90
                ))
                w_id += 1
                if len(wo_rows) >= 10000:
                    cursor.executemany("INSERT IGNORE INTO workouts (id, plan_id, exercise_order, exercise_name, target_muscle, sets, reps, weight_kg, rest_seconds) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", wo_rows)
                    conn.commit()
                    wo_rows = []
        if wo_rows:
            cursor.executemany("INSERT IGNORE INTO workouts (id, plan_id, exercise_order, exercise_name, target_muscle, sets, reps, weight_kg, rest_seconds) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", wo_rows)
            conn.commit()

        # 12. WALLET_AUDIT_LOGS (180,000)
        print("12/12 Dang chen 180,000 Wallet Audit Logs...")
        audit_rows = []
        for a_id in range(1, 180001):
            w_id = (a_id % 20000) + 1
            audit_rows.append((
                a_id, w_id, 4700000.00, 5000000.00, 0.00, 0.00, "TOPUP", "Nap tien thanh cong qua the"
            ))
            if len(audit_rows) >= 20000:
                cursor.executemany("INSERT IGNORE INTO wallet_audit_logs (id, wallet_id, old_balance, new_balance, old_locked_balance, new_locked_balance, action_type, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", audit_rows)
                conn.commit()
                audit_rows = []
        if audit_rows:
            cursor.executemany("INSERT IGNORE INTO wallet_audit_logs (id, wallet_id, old_balance, new_balance, old_locked_balance, new_locked_balance, action_type, reason) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", audit_rows)
            conn.commit()

        print("Dang cap nhat thong ke ANALYZE TABLE cho tat ca 16 bang...")
        cursor.execute("""
            ANALYZE TABLE 
                users, wallets, pt_profiles, pt_locations, courses, enrollments,
                availability_slots, bookings, reviews, cancellations, workout_plans,
                workouts, attendance, payments, wallet_audit_logs, booking_disputes;
        """)
        conn.commit()
        print("HOAN TAT BOM DU LIEU VA CAP NHAT THONG KE THANH CONG!")

    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute("SET UNIQUE_CHECKS = 1;")
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_seed()
