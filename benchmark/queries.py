"""
benchmark/queries.py
Dinh nghia 6 cap truy van (Chua toi uu vs Da toi uu) va cac chi muc (Index) tuong ung.
Chuan hoa 100% theo enum va schema thuc te trong CSDL MySQL ptconnect.
"""

BENCHMARK_CASES = [
    {
        "id": 1,
        "role": "Học viên",
        "title": "Tìm kiếm & Lọc Huấn luyện viên theo Khu vực và Điểm đánh giá",
        "description": "Học viên tìm PT theo khu vực tập luyện và sắp xếp theo rating trung bình giảm dần.",
        "technique": "Tận dụng quan hệ chuẩn hóa BCNF (pt_locations) + B-Tree Index khử quét LIKE chuỗi và Filesort",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_pt_verified_rating ON pt_profiles (verification_status, average_rating DESC);",
            "CREATE INDEX idx_opt_loc_name_pt ON pt_locations (location_name, pt_id);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_pt_verified_rating ON pt_profiles;",
            "DROP INDEX idx_opt_loc_name_pt ON pt_locations;",
        ],
        "unoptimized_sql": """
            SELECT 
                p.id, u.full_name, p.bio, p.average_rating, p.total_reviews
            FROM pt_profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.verification_status = 'VERIFIED'
              AND p.bio LIKE '%Quận 1%'
            ORDER BY p.average_rating DESC
            LIMIT 20;
        """,
        "optimized_sql": """
            SELECT 
                p.id, u.full_name, p.bio, p.average_rating, p.total_reviews
            FROM pt_profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.verification_status = 'VERIFIED'
              AND EXISTS (
                  SELECT 1 FROM pt_locations loc 
                  WHERE loc.pt_id = p.id AND loc.location_name = 'Quận 1'
              )
            ORDER BY p.average_rating DESC
            LIMIT 20;
        """
    },
    {
        "id": 2,
        "role": "Học viên",
        "title": "Phân trang sâu Lịch sử Ca tập (Deep Paging OFFSET 50,000)",
        "description": "Học viên hoặc quản trị viên mở các trang lịch sử ca tập ở trang xa (trang 2,500).",
        "technique": "Kỹ thuật Deferred Join (Late Row Lookup) khử nạp thừa dòng dữ liệu lớn",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_booking_student_id ON bookings (student_id, id DESC);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_booking_student_id ON bookings;",
        ],
        "unoptimized_sql": """
            SELECT 
                b.id, b.status, b.session_fee, b.created_at,
                s.start_time, s.end_time
            FROM bookings b
            JOIN availability_slots s ON b.slot_id = s.id
            WHERE b.student_id = 100
            ORDER BY b.id DESC
            LIMIT 20 OFFSET 50000;
        """,
        "optimized_sql": """
            SELECT 
                b.id, b.status, b.session_fee, b.created_at,
                s.start_time, s.end_time
            FROM (
                SELECT id FROM bookings
                WHERE student_id = 100
                ORDER BY id DESC
                LIMIT 20 OFFSET 50000
            ) AS page
            JOIN bookings b ON b.id = page.id
            JOIN availability_slots s ON b.slot_id = s.id;
        """
    },
    {
        "id": 3,
        "role": "Huấn luyện viên",
        "title": "Thời khóa biểu & Lịch dạy theo tuần/tháng của PT",
        "description": "PT mở lịch làm việc tuần này để xem các ca dạy kèm thông tin học viên.",
        "technique": "Composite Index lọc dải thời gian liên bảng (Range Scan) khử hàm DATE() trên cột",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_booking_slot_status ON bookings (slot_id, status);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_booking_slot_status ON bookings;",
        ],
        "unoptimized_sql": """
            SELECT 
                s.id AS slot_id, s.start_time, s.end_time,
                b.id AS booking_id, b.status AS booking_status,
                u.full_name AS student_name
            FROM availability_slots s
            LEFT JOIN bookings b ON b.slot_id = s.id
            LEFT JOIN users u ON b.student_id = u.id
            WHERE s.pt_id = 20
              AND DATE(s.start_time) >= '2026-11-01'
              AND DATE(s.start_time) <= '2026-11-07'
            ORDER BY s.start_time ASC;
        """,
        "optimized_sql": """
            SELECT 
                s.id AS slot_id, s.start_time, s.end_time,
                b.id AS booking_id, b.status AS booking_status,
                u.full_name AS student_name
            FROM availability_slots s
            LEFT JOIN bookings b ON b.slot_id = s.id
            LEFT JOIN users u ON b.student_id = u.id
            WHERE s.pt_id = 20
              AND s.start_time >= '2026-11-01 00:00:00'
              AND s.start_time <= '2026-11-07 23:59:59'
            ORDER BY s.start_time ASC;
        """
    },
    {
        "id": 4,
        "role": "Huấn luyện viên",
        "title": "Bảng kê Thu nhập & Quyết toán ca dạy theo tháng",
        "description": "PT tổng hợp doanh thu bồi thường, phí sàn và tiền phạt phát sinh trong tháng.",
        "technique": "Single-Pass Conditional Aggregation (SUM CASE) thay thế Multiple Correlated Subqueries",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_pay_wallet_filter ON payments (wallet_id, status, created_at, payment_type, amount);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_pay_wallet_filter ON payments;",
        ],
        "unoptimized_sql": """
            SELECT 
                w.id AS wallet_id,
                (SELECT COALESCE(SUM(p1.amount), 0) FROM payments p1 
                 WHERE p1.wallet_id = w.id AND p1.payment_type = 'COMPENSATION' 
                   AND p1.status = 'SUCCESS' AND p1.created_at >= '2026-11-01 00:00:00') AS total_compensations,
                (SELECT COALESCE(SUM(p2.amount), 0) FROM payments p2 
                 WHERE p2.wallet_id = w.id AND p2.payment_type = 'PLATFORM_FEE' 
                   AND p2.status = 'SUCCESS' AND p2.created_at >= '2026-11-01 00:00:00') AS total_platform_fees,
                (SELECT COALESCE(SUM(p3.amount), 0) FROM payments p3 
                 WHERE p3.wallet_id = w.id AND p3.payment_type = 'PENALTY' 
                   AND p3.status = 'SUCCESS' AND p3.created_at >= '2026-11-01 00:00:00') AS total_penalties
            FROM wallets w
            WHERE w.user_id = 20;
        """,
        "optimized_sql": """
            SELECT 
                w.id AS wallet_id,
                SUM(CASE WHEN p.payment_type = 'COMPENSATION' THEN p.amount ELSE 0 END) AS total_compensations,
                SUM(CASE WHEN p.payment_type = 'PLATFORM_FEE' THEN p.amount ELSE 0 END) AS total_platform_fees,
                SUM(CASE WHEN p.payment_type = 'PENALTY' THEN p.amount ELSE 0 END) AS total_penalties
            FROM wallets w
            JOIN payments p ON p.wallet_id = w.id
            WHERE w.user_id = 20
              AND p.status = 'SUCCESS'
              AND p.created_at >= '2026-11-01 00:00:00'
            GROUP BY w.id;
        """
    },
    {
        "id": 5,
        "role": "Quản trị viên",
        "title": "Bảng điều khiển Tổng quan Doanh thu & Dòng tiền sàn theo tháng",
        "description": "Admin xem thống kê tổng tiền và số giao dịch phân loại theo loại thanh toán trong tháng.",
        "technique": "Khôi phục tính SARGability (bỏ hàm YEAR/MONTH trên cột) + Chỉ mục bao phủ (Covering Index)",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_payments_report ON payments (status, created_at, payment_type, amount);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_payments_report ON payments;",
        ],
        "unoptimized_sql": """
            SELECT 
                payment_type,
                COUNT(*) AS total_txns,
                SUM(amount) AS total_amount
            FROM payments
            WHERE status = 'SUCCESS'
              AND YEAR(created_at) = 2026
              AND MONTH(created_at) = 11
            GROUP BY payment_type;
        """,
        "optimized_sql": """
            SELECT 
                payment_type,
                COUNT(*) AS total_txns,
                SUM(amount) AS total_amount
            FROM payments
            WHERE status = 'SUCCESS'
              AND created_at >= '2026-11-01 00:00:00'
              AND created_at < '2026-12-01 00:00:00'
            GROUP BY payment_type;
        """
    },
    {
        "id": 6,
        "role": "Quản trị viên",
        "title": "Hàng đợi Xử lý Khiếu nại / Tranh chấp theo hạn chót SLA 48h",
        "description": "Admin lọc các đơn tranh chấp cần xử lý gấp và ưu tiên sắp xếp theo hạn chót.",
        "technique": "Composite Index có thứ tự sắp xếp triệt tiêu hoàn toàn Using filesort & temporary table",
        "indexes_to_create": [
            "CREATE INDEX idx_opt_dispute_sla ON booking_disputes (deadline_at ASC, status);",
        ],
        "indexes_to_drop": [
            "DROP INDEX idx_opt_dispute_sla ON booking_disputes;",
        ],
        "unoptimized_sql": """
            SELECT id, booking_id, sender_id, reason, status, deadline_at, created_at
            FROM booking_disputes
            WHERE status IN ('PENDING', 'EVIDENCE_REQUESTED')
            ORDER BY deadline_at ASC
            LIMIT 20;
        """,
        "optimized_sql": """
            SELECT id, booking_id, sender_id, reason, status, deadline_at, created_at
            FROM booking_disputes
            WHERE status IN ('PENDING', 'EVIDENCE_REQUESTED')
            ORDER BY deadline_at ASC
            LIMIT 20;
        """
    }
]
