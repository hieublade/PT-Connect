USE `ptconnect`;

-- =====================================================================
-- 1. VIEW ĐỐI SOÁT TÀI CHÍNH VÍ (RECONCILIATION VIEW)
-- Mục đích: Đối soát số dư ví thực tế với tổng giá trị các giao dịch thành công (tìm chênh lệch tài chính nếu có).
-- =====================================================================
CREATE OR REPLACE VIEW `v_wallet_reconciliation` AS
SELECT
    w.`id` AS `wallet_id`,
    w.`user_id`,
    u.`full_name`,
    u.`role`,
    w.`balance` AS `current_balance`,
    w.`locked_balance`,
    COALESCE(l.`ledger_balance`, 0.00) AS `calculated_ledger_balance`,
    ROUND(w.`balance` - COALESCE(l.`ledger_balance`, 0.00), 2) AS `discrepancy`
FROM `wallets` w
JOIN `users` u ON w.`user_id` = u.`id`
LEFT JOIN (
    SELECT
        p.`wallet_id`,
        SUM(
            CASE
                WHEN p.`status` <> 'SUCCESS' THEN 0
                WHEN p.`payment_type` IN ('TOPUP', 'COMPENSATION', 'REFUND', 'EARNING', 'PLATFORM_FEE') THEN p.`amount`
                WHEN p.`payment_type` = 'PURCHASE_PACKAGE' AND p.`payment_method` = 'WALLET' THEN -p.`amount`
                WHEN p.`payment_type` IN ('PENALTY', 'WITHDRAWAL') THEN -p.`amount`
                ELSE 0
            END
        ) AS `ledger_balance`
    FROM `payments` p
    GROUP BY p.`wallet_id`
) l ON l.`wallet_id` = w.`id`;

-- =====================================================================
-- 2. VIEW CHI TIẾT HỦY LỊCH (CANCELLATION DETAILS)
-- Mục đích: Tổng hợp chi tiết các ca hủy tập kèm thông tin học viên, PT, chính sách hoàn tiền, bồi thường và nợ phạt.
-- =====================================================================
CREATE OR REPLACE VIEW `v_cancellations_detail` AS
SELECT
    c.`id` AS `cancellation_id`,
    c.`booking_id`,
    b.`booking_type`,
    b.`status` AS `booking_status`,
    b.`session_fee`,
    b.`student_id`,
    u_stu.`full_name` AS `student_name`,
    s.`pt_id`,
    u_pt.`full_name` AS `pt_name`,
    s.`start_time` AS `session_start_time`,
    c.`cancelled_at`,
    ROUND(TIMESTAMPDIFF(MINUTE, c.`cancelled_at`, s.`start_time`) / 60.0, 2) AS `hours_before_session`,
    CASE
        WHEN c.`cancelled_by_id` IS NULL THEN 'SYSTEM'
        WHEN c.`cancelled_by_id` = b.`student_id` THEN 'STUDENT'
        WHEN c.`cancelled_by_id` = u_pt.`id` THEN 'PT'
        ELSE COALESCE(u_actor.`role`, 'STUDENT')
    END AS `cancelled_by_role`,
    c.`cancelled_by_id`,
    COALESCE(u_actor.`full_name`, 'Hệ thống tự động') AS `cancelled_by_name`,
    COALESCE((SELECT amount FROM payments WHERE transaction_ref = CONCAT('CXL-', c.`booking_id`, '-REF') LIMIT 1), 0.00) AS `refund_amount`,
    COALESCE((SELECT amount FROM payments WHERE transaction_ref = CONCAT('CXL-', c.`booking_id`, '-COMP') LIMIT 1), 0.00) AS `compensation_amount`,
    COALESCE((SELECT amount FROM payments WHERE transaction_ref = CONCAT('CXL-', c.`booking_id`, '-PEN') LIMIT 1), 0.00) AS `penalty_amount`,
    0.00 AS `penalty_shortfall`,
    c.`reason`,
    c.`status` AS `cancellation_status`
FROM `cancellations` c
JOIN `bookings` b ON c.`booking_id` = b.`id`
JOIN `availability_slots` s ON b.`pt_id` = s.`pt_id` AND b.`slot_start_time` = s.`start_time`
JOIN `pt_profiles` p ON s.`pt_id` = p.`id`
JOIN `users` u_stu ON b.`student_id` = u_stu.`id`
JOIN `users` u_pt ON p.`user_id` = u_pt.`id`
LEFT JOIN `users` u_actor ON c.`cancelled_by_id` = u_actor.`id`;

-- =====================================================================
-- 3. VIEW THỐNG KÊ ĐÁNH GIÁ CỦA PT (PT RATING STATISTICS - BCNF)
-- Mục đích: Tính toán động điểm rating và tổng số đánh giá của từng PT từ dữ liệu review thực tế.
-- =====================================================================
CREATE OR REPLACE VIEW `v_pt_rating_statistics` AS
SELECT
    p.`id` AS `pt_profile_id`,
    p.`user_id`,
    u.`full_name` AS `pt_name`,
    COUNT(r.`id`) AS `total_reviews`,
    ROUND(COALESCE(AVG(r.`rating`), 0.00), 2) AS `average_rating`
FROM `pt_profiles` p
JOIN `users` u ON p.`user_id` = u.`id`
LEFT JOIN `availability_slots` s ON p.`id` = s.`pt_id`
LEFT JOIN `bookings` b ON s.`pt_id` = b.`pt_id` AND s.`start_time` = b.`slot_start_time`
LEFT JOIN `reviews` r ON b.`id` = r.`booking_id`
GROUP BY p.`id`, p.`user_id`, u.`full_name`;

-- =====================================================================
-- 3b. VIEW HỒ SƠ PT TỔNG HỢP BCNF (PT PROFILES VIEW)
-- Mục đích: Cung cấp đầy đủ thông tin hồ sơ PT cùng điểm đánh giá và tổng số đánh giá tính toán động.
-- =====================================================================
CREATE OR REPLACE VIEW `v_pt_profiles` AS
SELECT
    p.`id`,
    p.`user_id`,
    u.`full_name`,
    u.`email`,
    u.`phone`,
    u.`avatar_url`,
    p.`bio`,
    p.`specialty`,
    p.`experience_years`,
    p.`location_pricing_note`,
    p.`certificate_url`,
    p.`demo_video_url`,
    p.`verification_status`,
    p.`created_at`,
    p.`updated_at`,
    COUNT(r.`id`) AS `total_reviews`,
    ROUND(COALESCE(AVG(r.`rating`), 0.00), 2) AS `average_rating`
FROM `pt_profiles` p
JOIN `users` u ON p.`user_id` = u.`id`
LEFT JOIN `availability_slots` s ON p.`id` = s.`pt_id`
LEFT JOIN `bookings` b ON s.`pt_id` = b.`pt_id` AND s.`start_time` = b.`slot_start_time`
LEFT JOIN `reviews` r ON b.`id` = r.`booking_id`
GROUP BY p.`id`, p.`user_id`, u.`full_name`, u.`email`, u.`phone`, u.`avatar_url`,
         p.`bio`, p.`specialty`, p.`experience_years`, p.`location_pricing_note`,
         p.`certificate_url`, p.`demo_video_url`, p.`verification_status`,
         p.`created_at`, p.`updated_at`;

-- =====================================================================
-- 4. VIEW GÓI TẬP ĐANG HIỆU LỰC (STUDENT ACTIVE PACKAGES)
-- Mục đích: Thống kê số buổi còn lại và số buổi khả dụng thực tế (đã trừ các ca đang giữ chỗ) của từng học viên.
-- =====================================================================
CREATE OR REPLACE VIEW `v_student_active_packages` AS
SELECT
    e.`id` AS `enrollment_id`,
    e.`student_id`,
    u_stu.`full_name` AS `student_name`,
    c.`title` AS `course_title`,
    u_pt.`full_name` AS `pt_name`,
    e.`total_sessions`,
    e.`remaining_sessions`,
    COALESCE(rb.`reserved_sessions`, 0) AS `reserved_sessions`,
    GREATEST(e.`remaining_sessions` - COALESCE(rb.`reserved_sessions`, 0), 0) AS `available_sessions`,
    e.`start_date`,
    e.`end_date`,
    DATEDIFF(e.`end_date`, CURDATE()) AS `days_left`,
    e.`status`
FROM `enrollments` e
JOIN `courses` c ON e.`course_id` = c.`id`
JOIN `pt_profiles` p ON c.`pt_id` = p.`id`
JOIN `users` u_stu ON e.`student_id` = u_stu.`id`
JOIN `users` u_pt ON p.`user_id` = u_pt.`id`
LEFT JOIN (
    SELECT `enrollment_id`, COUNT(*) AS `reserved_sessions`
    FROM `bookings`
    WHERE `status` IN ('PENDING', 'CONFIRMED') AND `enrollment_id` IS NOT NULL
    GROUP BY `enrollment_id`
) rb ON rb.`enrollment_id` = e.`id`
WHERE e.`status` = 'ACTIVE'
  AND e.`end_date` >= CURDATE();

-- =====================================================================
-- 5. VIEW SỔ CÁI KIỂM TOÁN VÍ BCNF (WALLET AUDIT LOGS VIEW)
-- Mục đích: Hiển thị nhật ký biến động số dư ví kết hợp định danh người dùng và số tiền thay đổi (tính toán động).
-- =====================================================================
CREATE OR REPLACE VIEW `v_wallet_audit_logs` AS
SELECT
    l.`seq_no`,
    l.`wallet_id`,
    w.`user_id`,
    u.`full_name`,
    u.`email`,
    l.`old_balance`,
    l.`new_balance`,
    l.`old_locked_balance`,
    l.`new_locked_balance`,
    ROUND(l.`new_balance` - l.`old_balance`, 2) AS `changed_amount`,
    ROUND(l.`new_locked_balance` - l.`old_locked_balance`, 2) AS `changed_locked_amount`,
    l.`action_type`,
    l.`reason`,
    l.`created_at`
FROM `wallet_audit_logs` l
JOIN `wallets` w ON l.`wallet_id` = w.`id`
JOIN `users` u ON w.`user_id` = u.`id`;

-- =====================================================================
-- 6. VIEW KHIẾU NẠI VÀ THỜI HẠN XỬ LÝ (BOOKING DISPUTES VIEW - BCNF)
-- Mục đích: Tính toán động thời hạn xử lý 48h (deadline_at) từ created_at mà không cần lưu cột dẫn xuất vật lý.
-- =====================================================================
CREATE OR REPLACE VIEW `v_booking_disputes` AS
SELECT
    d.`id` AS `dispute_id`,
    d.`booking_id`,
    d.`sender_id`,
    u.`full_name` AS `sender_name`,
    u.`role` AS `sender_role`,
    d.`dispute_type`,
    d.`reason`,
    d.`evidence_url`,
    d.`counter_evidence_url`,
    d.`counter_argument`,
    d.`status`,
    d.`admin_notes`,
    d.`resolved_at`,
    d.`created_at`,
    d.`created_at` + INTERVAL 48 HOUR AS `deadline_at`,
    (NOW() >= d.`created_at` + INTERVAL 48 HOUR) AS `is_past_deadline`
FROM `booking_disputes` d
JOIN `users` u ON d.`sender_id` = u.`id`;
