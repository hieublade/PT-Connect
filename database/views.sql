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
                WHEN p.`payment_type` IN ('TOPUP', 'COMPENSATION', 'REFUND') THEN p.`amount`
                WHEN p.`payment_type` = 'PURCHASE_PACKAGE' AND p.`payment_method` = 'WALLET' THEN -p.`amount`
                WHEN p.`payment_type` = 'PENALTY' THEN -p.`amount`
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
    c.`hours_before_session`,
    c.`cancelled_by_role`,
    c.`cancelled_by_id`,
    u_actor.`full_name` AS `cancelled_by_name`,
    c.`refund_amount`,
    c.`compensation_amount`,
    c.`penalty_amount`,
    c.`penalty_shortfall`,
    c.`reason`,
    c.`status` AS `cancellation_status`
FROM `cancellations` c
JOIN `bookings` b ON c.`booking_id` = b.`id`
JOIN `availability_slots` s ON b.`slot_id` = s.`id`
JOIN `pt_profiles` p ON s.`pt_id` = p.`id`
JOIN `users` u_stu ON b.`student_id` = u_stu.`id`
JOIN `users` u_pt ON p.`user_id` = u_pt.`id`
LEFT JOIN `users` u_actor ON c.`cancelled_by_id` = u_actor.`id`;

-- =====================================================================
-- 3. VIEW THỐNG KÊ ĐÁNH GIÁ CỦA PT (PT RATING STATISTICS)
-- Mục đích: Kiểm tra tính nhất quán giữa điểm rating lưu trong bảng pt_profiles với dữ liệu review thực tế.
-- =====================================================================
CREATE OR REPLACE VIEW `v_pt_rating_statistics` AS
SELECT
    p.`id` AS `pt_profile_id`,
    p.`user_id`,
    u.`full_name` AS `pt_name`,
    p.`average_rating` AS `stored_average_rating`,
    p.`total_reviews` AS `stored_total_reviews`,
    COUNT(r.`id`) AS `calculated_total_reviews`,
    ROUND(COALESCE(AVG(r.`rating`), 0.00), 2) AS `calculated_average_rating`,
    (p.`total_reviews` = COUNT(r.`id`)
     AND p.`average_rating` = ROUND(COALESCE(AVG(r.`rating`), 0.00), 2)) AS `is_consistent`
FROM `pt_profiles` p
JOIN `users` u ON p.`user_id` = u.`id`
LEFT JOIN `availability_slots` s ON p.`id` = s.`pt_id`
LEFT JOIN `bookings` b ON s.`id` = b.`slot_id`
LEFT JOIN `reviews` r ON b.`id` = r.`booking_id`
GROUP BY p.`id`, p.`user_id`, u.`full_name`, p.`average_rating`, p.`total_reviews`;

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
    l.`id`,
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
