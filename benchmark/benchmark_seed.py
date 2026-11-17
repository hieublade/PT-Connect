"""
benchmark/benchmark_seed.py
Script bom du lieu mau quy mo lon (100k - 300k ban ghi) vao MySQL phuc vu do luong hieu nang.
Su dung ky thuat Batch Insert voi SET FOREIGN_KEY_CHECKS = 0 de dat toc do toi da.
"""

import sys
import os
import random
from datetime import datetime, timedelta
import pymysql

def get_connection(host="127.0.0.1", port=3307, user="root", password="root123", database="ptconnect"):
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        autocommit=False,
    )

def seed_benchmark_data(host="127.0.0.1", port=3307, user="root", password="root123", database="ptconnect"):
    print(f"Ket noi toi MySQL tai {host}:{port}, database='{database}'...")
    conn = get_connection(host, port, user, password, database)
    cursor = conn.cursor()

    try:
        print("Tat kiem tra khoa ngoai va toi uu che do ghi bulk insert...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SET UNIQUE_CHECKS = 0;")
        cursor.execute("SET sql_log_bin = 0;")

        locations = ["Quận 1", "Quận 3", "Quận 7", "Bình Thạnh", "Cầu Giấy", "Đống Đa", "Thanh Xuân", "Hải Châu", "Sơn Trà"]

        # 1. USERS & WALLETS (20,000 users: 5,000 PTs + 15,000 Students)
        print("1. Dang chen 20,000 Users va Wallets...")
        user_rows = []
        wallet_rows = []
        
        for i in range(1, 20001):
            role = "PT" if i <= 5000 else "STUDENT"
            user_rows.append((
                i, f"Nguoi Dung {i}", f"user{i}@benchmark.vn", "$2b$12$e/e.examplehashnotforlogin123",
                f"090{i:07d}", role, "ACTIVE", datetime(2026, 1, 1) + timedelta(minutes=i)
            ))
            wallet_rows.append((
                i, i, 5000000.00, 0.00, "VND", "ACTIVE"
            ))

            if len(user_rows) >= 5000:
                cursor.executemany("""
                    INSERT IGNORE INTO users (id, full_name, email, password_hash, phone, role, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, user_rows)
                cursor.executemany("""
                    INSERT IGNORE INTO wallets (id, user_id, balance, locked_balance, currency, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, wallet_rows)
                conn.commit()
                user_rows = []
                wallet_rows = []

        if user_rows:
            cursor.executemany("""
                INSERT IGNORE INTO users (id, full_name, email, password_hash, phone, role, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, user_rows)
            cursor.executemany("""
                INSERT IGNORE INTO wallets (id, user_id, balance, locked_balance, currency, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, wallet_rows)
            conn.commit()
            user_rows = []
            wallet_rows = []

        # 2. PT_PROFILES & PT_LOCATIONS (5,000 PTs & ~12,500 locations)
        print("2. Dang chen 5,000 PT Profiles va 12,500 PT Locations...")
        profile_rows = []
        loc_rows = []
        for i in range(1, 5001):
            avg_rating = round(random.uniform(3.5, 5.0), 2)
            total_revs = random.randint(10, 500)
            bio_dist = random.choice(locations)
            profile_rows.append((
                i, i, f"HLV the hinh chuyen nghiep khu vuc {bio_dist}, chuyen tang co giam mo.",
                3 + (i % 12), "https://example.com/certificate.pdf", avg_rating, total_revs, "VERIFIED"
            ))
            chosen_locs = random.sample(locations, k=random.randint(2, 3))
            for loc in chosen_locs:
                loc_rows.append((i, loc))

            if len(profile_rows) >= 2000:
                cursor.executemany("""
                    INSERT IGNORE INTO pt_profiles (id, user_id, bio, experience_years, certificate_url, average_rating, total_reviews, verification_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, profile_rows)
                cursor.executemany("""
                    INSERT IGNORE INTO pt_locations (pt_id, location_name)
                    VALUES (%s, %s)
                """, loc_rows)
                conn.commit()
                profile_rows = []
                loc_rows = []

        if profile_rows:
            cursor.executemany("""
                INSERT IGNORE INTO pt_profiles (id, user_id, bio, experience_years, certificate_url, average_rating, total_reviews, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, profile_rows)
            cursor.executemany("""
                INSERT IGNORE INTO pt_locations (pt_id, location_name)
                VALUES (%s, %s)
            """, loc_rows)
            conn.commit()
            profile_rows = []
            loc_rows = []

        # 3. AVAILABILITY_SLOTS (150,000 slots)
        print("3. Dang chen 150,000 Availability Slots...")
        slot_batch = []
        base_time = datetime(2026, 11, 1, 6, 0, 0)
        slot_id = 1
        for pt_id in range(1, 1001):
            # 1,000 PTs dau tien, moi nguoi co 150 slots trong thang 11/2026
            for day in range(30):
                for hour in [7, 9, 14, 17, 19]:
                    st = base_time + timedelta(days=day, hours=hour)
                    et = st + timedelta(hours=1)
                    slot_batch.append((slot_id, pt_id, st, et, "BOOKED"))
                    slot_id += 1
                    if len(slot_batch) >= 10000:
                        cursor.executemany("""
                            INSERT IGNORE INTO availability_slots (id, pt_id, start_time, end_time, status)
                            VALUES (%s, %s, %s, %s, %s)
                        """, slot_batch)
                        conn.commit()
                        slot_batch = []

        if slot_batch:
            cursor.executemany("""
                INSERT IGNORE INTO availability_slots (id, pt_id, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, %s)
            """, slot_batch)
            conn.commit()
            slot_batch = []

        # 4. BOOKINGS (150,000 bookings: 60,000 cho student_id = 100 phuc vu deep paging)
        print("4. Dang chen 150,000 Bookings (sinh 60,000 bookings cho student_id = 100 de do deep paging)...")
        booking_batch = []
        statuses = ["COMPLETED", "CONFIRMED", "CANCELLED"]
        
        # 60,000 bookings cho rieng student_id = 100 de test LIMIT 20 OFFSET 50000
        for b_id in range(1, 60001):
            s_id = (b_id % 140000) + 1
            booking_batch.append((
                b_id, 100, s_id, None, "PACKAGE", "COMPLETED", 300000.00,
                base_time + timedelta(minutes=b_id)
            ))
            if len(booking_batch) >= 10000:
                cursor.executemany("""
                    INSERT IGNORE INTO bookings (id, student_id, slot_id, enrollment_id, booking_type, status, session_fee, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, booking_batch)
                conn.commit()
                booking_batch = []

        # Cac bookings con lai cho cac student khac (60,001 den 150,000)
        for b_id in range(60001, 150001):
            student_id = random.randint(5001, 20000)
            s_id = (b_id % 140000) + 1
            st_choice = random.choice(statuses)
            booking_batch.append((
                b_id, student_id, s_id, None, "PACKAGE", st_choice, 300000.00,
                base_time + timedelta(minutes=b_id)
            ))
            if len(booking_batch) >= 10000:
                cursor.executemany("""
                    INSERT IGNORE INTO bookings (id, student_id, slot_id, enrollment_id, booking_type, status, session_fee, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, booking_batch)
                conn.commit()
                booking_batch = []

        if booking_batch:
            cursor.executemany("""
                INSERT IGNORE INTO bookings (id, student_id, slot_id, enrollment_id, booking_type, status, session_fee, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, booking_batch)
            conn.commit()
            booking_batch = []

        # 5. PAYMENTS (250,000 payments: 30,000 payments cho wallet_id = 20)
        print("5. Dang chen 250,000 Payments (30,000 payments cho wallet_id = 20 de test tong hop)...")
        pay_batch = []
        pay_types = ["COMPENSATION", "PLATFORM_FEE", "PENALTY", "PURCHASE_PACKAGE", "TOPUP"]
        
        # Wallet 20 co 30,000 payments
        for p_id in range(1, 30001):
            ptype = pay_types[p_id % 3]  # COMPENSATION, PLATFORM_FEE, PENALTY
            amt = random.choice([270000.00, 50000.00, 100000.00, 300000.00])
            created = datetime(2026, 11, 1) + timedelta(minutes=p_id)
            pay_batch.append((
                p_id, 20, None, amt, ptype, "WALLET", "SUCCESS", f"TXN-BENCH-{p_id}", created
            ))
            if len(pay_batch) >= 10000:
                cursor.executemany("""
                    INSERT IGNORE INTO payments (id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, pay_batch)
                conn.commit()
                pay_batch = []

        # Cac payments con lai (30,001 den 250,000)
        for p_id in range(30001, 250001):
            w_id = random.randint(1, 20000)
            ptype = random.choice(pay_types)
            amt = random.choice([50000.00, 150000.00, 300000.00, 500000.00, 1000000.00])
            created = datetime(2026, 11, 1) + timedelta(minutes=(p_id % 40000))
            pay_batch.append((
                p_id, w_id, None, amt, ptype, "WALLET", "SUCCESS", f"TXN-BENCH-{p_id}", created
            ))
            if len(pay_batch) >= 10000:
                cursor.executemany("""
                    INSERT IGNORE INTO payments (id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, pay_batch)
                conn.commit()
                pay_batch = []

        if pay_batch:
            cursor.executemany("""
                INSERT IGNORE INTO payments (id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, pay_batch)
            conn.commit()
            pay_batch = []

        # 6. BOOKING_DISPUTES (50,000 disputes)
        print("6. Dang chen 50,000 Booking Disputes...")
        dispute_batch = []
        d_statuses = ["PENDING", "EVIDENCE_REQUESTED", "RESOLVED_REFUND", "REJECTED"]
        d_types = ["WRONG_ABSENT", "PT_NO_SHOW", "STUDENT_NO_SHOW", "ATTITUDE_QUALITY"]
        for d_id in range(1, 50001):
            b_id = (d_id % 140000) + 1
            u_id = random.randint(5001, 20000)
            dst = random.choice(d_statuses)
            dtype = random.choice(d_types)
            s_role = "STUDENT" if d_id % 2 == 0 else "PT"
            deadline = datetime(2026, 11, 1) + timedelta(hours=random.randint(1, 720))
            created = datetime(2026, 11, 1) + timedelta(hours=d_id % 700)
            dispute_batch.append((
                d_id, b_id, u_id, s_role, dtype, "Hoc vien khieu nai chat luong ca tap hoac phong tap",
                dst, deadline, created
            ))
            if len(dispute_batch) >= 10000:
                cursor.executemany("""
                    INSERT IGNORE INTO booking_disputes (id, booking_id, sender_id, sender_role, dispute_type, reason, status, deadline_at, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, dispute_batch)
                conn.commit()
                dispute_batch = []

        if dispute_batch:
            cursor.executemany("""
                INSERT IGNORE INTO booking_disputes (id, booking_id, sender_id, sender_role, dispute_type, reason, status, deadline_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, dispute_batch)
            conn.commit()
            dispute_batch = []

        # Bat lai kiem tra rang buoc
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute("SET UNIQUE_CHECKS = 1;")
        conn.commit()
        print("Hoan tat bom toan bo du lieu mau benchmark thanh cong!")

    except Exception as e:
        conn.rollback()
        print(f"Loi trong qua trinh bom du lieu: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 3307
    u = sys.argv[3] if len(sys.argv) > 3 else "root"
    pwd = sys.argv[4] if len(sys.argv) > 4 else "root123"
    db = sys.argv[5] if len(sys.argv) > 5 else "ptconnect"
    seed_benchmark_data(h, p, u, pwd, db)
