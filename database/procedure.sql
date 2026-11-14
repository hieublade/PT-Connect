USE `ptconnect`;

DELIMITER $$

-- =====================================================================
-- 1. HÀM VÀ THỦ TỤC HỖ TRỢ (HELPERS)
-- =====================================================================

-- Mục đích: Tính số giờ còn lại từ một mốc thời gian (p_at_time) đến khi ca tập bắt đầu (p_slot_start).
DROP FUNCTION IF EXISTS `fn_hours_before`$$
CREATE FUNCTION `fn_hours_before`(
    `p_slot_start` DATETIME,
    `p_at_time` DATETIME
) RETURNS DECIMAL(7,2)
DETERMINISTIC
NO SQL
BEGIN
    IF `p_slot_start` IS NULL OR `p_at_time` IS NULL THEN
        RETURN 0.00;
    END IF;
    RETURN ROUND(TIMESTAMPDIFF(MINUTE, `p_at_time`, `p_slot_start`) / 60.0, 2);
END$$

-- Mục đích: Tính giá trị tiền tương ứng của 1 buổi tập (final_price / total_sessions) từ hợp đồng gói tập.
DROP FUNCTION IF EXISTS `fn_session_fee`$$
CREATE FUNCTION `fn_session_fee`(
    `p_enrollment_id` BIGINT
) RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE `v_final_price` DECIMAL(12,2);
    DECLARE `v_total_sessions` INT;

    IF `p_enrollment_id` IS NULL THEN
        RETURN 0.00;
    END IF;

    SELECT `final_price`, `total_sessions`
    INTO `v_final_price`, `v_total_sessions`
    FROM `enrollments`
    WHERE `id` = `p_enrollment_id`;

    IF `v_total_sessions` IS NULL OR `v_total_sessions` <= 0 THEN
        RETURN 0.00;
    END IF;

    RETURN ROUND(`v_final_price` / `v_total_sessions`, 2);
END$$

-- Mục đích: Trừ 1 buổi tập khả dụng (remaining_sessions) của hợp đồng khi học viên hoàn thành ca tập; tự động chuyển sang COMPLETED nếu hết buổi.
DROP PROCEDURE IF EXISTS `sp_consume_session`$$
CREATE PROCEDURE `sp_consume_session`(
    IN `p_enrollment_id` BIGINT
)
BEGIN
    UPDATE `enrollments`
    SET `status` = IF(`status` = 'ACTIVE' AND `remaining_sessions` <= 1, 'COMPLETED', `status`),
        `remaining_sessions` = GREATEST(0, `remaining_sessions` - 1)
    WHERE `id` = `p_enrollment_id`;
END$$

-- Mục đích: Tính toán lại điểm đánh giá trung bình và tổng số lượng review của PT, cập nhật vào bảng pt_profiles.
DROP PROCEDURE IF EXISTS `sp_recalc_pt_rating`$$
CREATE PROCEDURE `sp_recalc_pt_rating`(
    IN `p_pt_id` BIGINT
)
BEGIN
    DECLARE `v_lock_id` BIGINT;
    DECLARE `v_total` INT DEFAULT 0;
    DECLARE `v_avg` DECIMAL(5,2) DEFAULT 0.00;

    SELECT `id` INTO `v_lock_id` FROM `pt_profiles` WHERE `id` = `p_pt_id` FOR UPDATE;

    SELECT COUNT(r.`id`), COALESCE(ROUND(AVG(r.`rating`), 2), 0.00)
    INTO `v_total`, `v_avg`
    FROM `reviews` r
    JOIN `bookings` b ON r.`booking_id` = b.`id`
    JOIN `availability_slots` s ON b.`slot_id` = s.`id`
    WHERE s.`pt_id` = `p_pt_id`
    FOR SHARE OF r;

    UPDATE `pt_profiles`
    SET `average_rating` = `v_avg`,
        `total_reviews` = `v_total`
    WHERE `id` = `p_pt_id`;
END$$

-- =====================================================================
-- 2. QUYẾT TOÁN TÀI CHÍNH VÍ (WALLET SETTLEMENT)
-- =====================================================================

-- Mục đích: Quyết toán tiền ví nội bộ (hoàn tiền, phạt, bồi thường); trừ tiền tối đa theo số dư khả dụng thực tế để chống âm ví và tạo giao dịch thanh toán thành công.
DROP PROCEDURE IF EXISTS `sp_wallet_settle`$$
CREATE PROCEDURE `sp_wallet_settle`(
    IN  `p_user_id`        BIGINT,
    IN  `p_amount`         DECIMAL(14,2),
    IN  `p_payment_type`   VARCHAR(20),
    IN  `p_enrollment_id`  BIGINT,
    IN  `p_txn_ref`        VARCHAR(100),
    IN  `p_reason`         VARCHAR(255),
    OUT `p_applied_amount` DECIMAL(14,2),
    OUT `p_status_code`    INT
)
proc_label: BEGIN
    DECLARE `v_wallet_id` BIGINT;
    DECLARE `v_balance` DECIMAL(14,2);
    DECLARE `v_locked` DECIMAL(14,2);

    SET `p_applied_amount` = 0.00;
    SET `p_status_code` = 0;

    IF `p_user_id` IS NULL THEN
        SET `p_status_code` = 2;
        LEAVE proc_label;
    END IF;

    IF `p_amount` IS NULL OR `p_amount` <= 0 THEN
        LEAVE proc_label;
    END IF;

    IF `p_payment_type` IS NULL OR `p_payment_type` NOT IN ('COMPENSATION', 'REFUND', 'PENALTY') THEN
        SET `p_status_code` = 3;
        LEAVE proc_label;
    END IF;

    SELECT `id`, `balance`, `locked_balance`
    INTO `v_wallet_id`, `v_balance`, `v_locked`
    FROM `wallets`
    WHERE `user_id` = `p_user_id`
    FOR UPDATE;

    IF `v_wallet_id` IS NULL THEN
        SET `p_status_code` = 2;
        LEAVE proc_label;
    END IF;

    IF `p_payment_type` = 'PENALTY' THEN
        SET `p_applied_amount` = LEAST(`p_amount`, `v_balance` - `v_locked`);
        IF `p_applied_amount` > 0 THEN
            UPDATE `wallets`
            SET `balance` = `balance` - `p_applied_amount`
            WHERE `id` = `v_wallet_id`;

            INSERT INTO `payments` (
                `wallet_id`, `enrollment_id`, `amount`, `payment_type`,
                `payment_method`, `status`, `transaction_ref`, `created_at`
            ) VALUES (
                `v_wallet_id`, `p_enrollment_id`, `p_applied_amount`, 'PENALTY',
                'WALLET', 'SUCCESS', `p_txn_ref`, NOW()
            );
        END IF;
    ELSE
        SET `p_applied_amount` = `p_amount`;
        UPDATE `wallets`
        SET `balance` = `balance` + `p_applied_amount`
        WHERE `id` = `v_wallet_id`;

        INSERT INTO `payments` (
            `wallet_id`, `enrollment_id`, `amount`, `payment_type`,
            `payment_method`, `status`, `transaction_ref`, `created_at`
        ) VALUES (
            `v_wallet_id`, `p_enrollment_id`, `p_applied_amount`, `p_payment_type`,
            'WALLET', 'SUCCESS', `p_txn_ref`, NOW()
        );
    END IF;
END$$

-- =====================================================================
-- 3. NGHIỆP VỤ ĐẶT LỊCH TẬP (BOOKING)
-- =====================================================================

-- Mục đích: Đặt ca tập mới (TRIAL hoặc PACKAGE); kiểm tra toàn vẹn slot, chống trùng lịch học viên, chống vượt số buổi gói tập và xử lý xung đột đồng thời.
DROP PROCEDURE IF EXISTS `sp_book_session`$$
CREATE PROCEDURE `sp_book_session`(
    IN `p_student_id` BIGINT,
    IN `p_slot_id` BIGINT,
    IN `p_enrollment_id` BIGINT,
    IN `p_booking_type` VARCHAR(20),
    IN `p_student_note` VARCHAR(255),
    OUT `p_booking_id` BIGINT,
    OUT `p_status_code` INT,
    OUT `p_message` VARCHAR(255)
)
proc_label: BEGIN
    DECLARE `v_student_role` VARCHAR(20);
    DECLARE `v_student_status` VARCHAR(20);

    DECLARE `v_slot_pt_id` BIGINT;
    DECLARE `v_slot_start` DATETIME;
    DECLARE `v_slot_end` DATETIME;
    DECLARE `v_slot_status` VARCHAR(20);

    DECLARE `v_enroll_student_id` BIGINT;
    DECLARE `v_enroll_remaining` INT;
    DECLARE `v_enroll_status` VARCHAR(20);
    DECLARE `v_enroll_start_date` DATE;
    DECLARE `v_enroll_end_date` DATE;
    DECLARE `v_course_pt_id` BIGINT;

    DECLARE `v_session_fee` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_overlap_count` INT DEFAULT 0;
    DECLARE `v_trial_count` INT DEFAULT 0;
    DECLARE `v_active_bookings_count` INT DEFAULT 0;

    DECLARE `v_errno` INT DEFAULT 0;
    DECLARE `v_errmsg` VARCHAR(512) DEFAULT '';

    DECLARE EXIT HANDLER FOR 1062
    BEGIN
        ROLLBACK;
        SET `p_booking_id` = NULL;
        SET `p_status_code` = 1;
        SET `p_message` = 'Khung giờ vừa được người khác đặt, vui lòng chọn khung giờ khác.';
    END;

    DECLARE EXIT HANDLER FOR 1213, 1205
    BEGIN
        ROLLBACK;
        SET `p_booking_id` = NULL;
        SET `p_status_code` = 98;
        SET `p_message` = 'Hệ thống đang bận (xung đột khóa), vui lòng thử lại.';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 `v_errno` = MYSQL_ERRNO, `v_errmsg` = MESSAGE_TEXT;
        ROLLBACK;
        SET `p_booking_id` = NULL;
        SET `p_status_code` = 99;
        SET `p_message` = LEFT(CONCAT('Lỗi CSDL #', `v_errno`, ': ', `v_errmsg`), 255);
    END;

    SET `p_booking_id` = NULL;
    SET `p_status_code` = 0;
    SET `p_message` = 'Thành công';

    IF `p_booking_type` IS NULL OR `p_booking_type` NOT IN ('TRIAL', 'PACKAGE') THEN
        SET `p_status_code` = 10;
        SET `p_message` = 'Loại ca tập không hợp lệ (chỉ nhận TRIAL hoặc PACKAGE).';
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    SELECT `role`, `status`
    INTO `v_student_role`, `v_student_status`
    FROM `users`
    WHERE `id` = `p_student_id`;

    IF `v_student_role` IS NULL OR `v_student_role` <> 'STUDENT' OR `v_student_status` <> 'ACTIVE' THEN
        ROLLBACK;
        SET `p_status_code` = 11;
        SET `p_message` = 'Học viên không tồn tại hoặc tài khoản không hoạt động.';
        LEAVE proc_label;
    END IF;

    SELECT `pt_id`, `start_time`, `end_time`, `status`
    INTO `v_slot_pt_id`, `v_slot_start`, `v_slot_end`, `v_slot_status`
    FROM `availability_slots`
    WHERE `id` = `p_slot_id`
    FOR UPDATE;

    IF `v_slot_status` IS NULL OR `v_slot_status` <> 'AVAILABLE' THEN
        ROLLBACK;
        SET `p_status_code` = 1;
        SET `p_message` = 'Khung giờ này đã được đặt hoặc không khả dụng.';
        LEAVE proc_label;
    END IF;

    IF `v_slot_start` < NOW() THEN
        ROLLBACK;
        SET `p_status_code` = 2;
        SET `p_message` = 'Không thể đặt khung giờ trong quá khứ.';
        LEAVE proc_label;
    END IF;

    SELECT COUNT(*)
    INTO `v_overlap_count`
    FROM `bookings` b
    JOIN `availability_slots` s ON b.`slot_id` = s.`id`
    WHERE b.`student_id` = `p_student_id`
      AND b.`status` IN ('PENDING', 'CONFIRMED')
      AND s.`start_time` < `v_slot_end`
      AND s.`end_time` > `v_slot_start`;

    IF `v_overlap_count` > 0 THEN
        ROLLBACK;
        SET `p_status_code` = 3;
        SET `p_message` = 'Bạn đã có một ca tập khác trùng khung giờ này.';
        LEAVE proc_label;
    END IF;

    IF `p_booking_type` = 'TRIAL' THEN
        SELECT COUNT(*)
        INTO `v_trial_count`
        FROM `bookings` b
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE b.`student_id` = `p_student_id`
          AND s.`pt_id` = `v_slot_pt_id`
          AND b.`booking_type` = 'TRIAL'
          AND b.`status` <> 'CANCELLED';

        IF `v_trial_count` > 0 THEN
            ROLLBACK;
            SET `p_status_code` = 4;
            SET `p_message` = 'Mỗi học viên chỉ được học thử 1 lần với PT này.';
            LEAVE proc_label;
        END IF;

        SET `v_session_fee` = 0.00;
        SET `p_enrollment_id` = NULL;
    ELSE
        IF `p_enrollment_id` IS NULL THEN
            ROLLBACK;
            SET `p_status_code` = 5;
            SET `p_message` = 'Đặt ca theo gói phải chỉ định mã hợp đồng (enrollment_id).';
            LEAVE proc_label;
        END IF;

        SELECT e.`student_id`, e.`remaining_sessions`, e.`status`, e.`start_date`, e.`end_date`, c.`pt_id`
        INTO `v_enroll_student_id`, `v_enroll_remaining`, `v_enroll_status`, `v_enroll_start_date`, `v_enroll_end_date`, `v_course_pt_id`
        FROM `enrollments` e
        JOIN `courses` c ON e.`course_id` = c.`id`
        WHERE e.`id` = `p_enrollment_id`
        FOR UPDATE OF e;

        IF `v_enroll_status` IS NULL OR `v_enroll_status` <> 'ACTIVE' THEN
            ROLLBACK;
            SET `p_status_code` = 6;
            SET `p_message` = 'Hợp đồng không hợp lệ hoặc không ở trạng thái ACTIVE.';
            LEAVE proc_label;
        END IF;

        IF `v_enroll_student_id` <> `p_student_id` THEN
            ROLLBACK;
            SET `p_status_code` = 7;
            SET `p_message` = 'Hợp đồng này không thuộc về học viên.';
            LEAVE proc_label;
        END IF;

        IF `v_course_pt_id` <> `v_slot_pt_id` THEN
            ROLLBACK;
            SET `p_status_code` = 8;
            SET `p_message` = 'Hợp đồng này không phải với PT của khung giờ được chọn.';
            LEAVE proc_label;
        END IF;

        IF DATE(`v_slot_start`) < `v_enroll_start_date` OR DATE(`v_slot_start`) > `v_enroll_end_date` THEN
            ROLLBACK;
            SET `p_status_code` = 12;
            SET `p_message` = 'Ca tập nằm ngoài thời hạn hiệu lực của hợp đồng.';
            LEAVE proc_label;
        END IF;

        SELECT COUNT(*)
        INTO `v_active_bookings_count`
        FROM `bookings`
        WHERE `enrollment_id` = `p_enrollment_id`
          AND `status` IN ('PENDING', 'CONFIRMED')
        FOR SHARE;

        IF `v_enroll_remaining` - `v_active_bookings_count` < 1 THEN
            ROLLBACK;
            SET `p_status_code` = 9;
            SET `p_message` = 'Hợp đồng không còn đủ buổi khả dụng để đặt thêm ca.';
            LEAVE proc_label;
        END IF;

        SET `v_session_fee` = `fn_session_fee`(`p_enrollment_id`);
    END IF;

    INSERT INTO `bookings` (
        `booking_type`,
        `enrollment_id`,
        `student_id`,
        `slot_id`,
        `session_fee`,
        `status`,
        `student_note`,
        `created_at`
    ) VALUES (
        `p_booking_type`,
        `p_enrollment_id`,
        `p_student_id`,
        `p_slot_id`,
        `v_session_fee`,
        'PENDING',
        `p_student_note`,
        NOW()
    );

    SET `p_booking_id` = LAST_INSERT_ID();

    COMMIT;
END$$

-- =====================================================================
-- 4. NGHIỆP VỤ HỦY LỊCH VÀ PHẠT / HOÀN TIỀN (CANCELLATION)
-- =====================================================================

-- Mục đích: Hủy ca tập theo chính sách giờ hủy; khóa an toàn chống Deadlock 1213, giải quyết tiền phạt/bồi thường (Phantom Money fix qua penalty_shortfall), hoàn trả buổi tập hoặc ghi nhận doanh thu cho PT.
DROP PROCEDURE IF EXISTS `sp_cancel_booking`$$
CREATE PROCEDURE `sp_cancel_booking`(
    IN `p_booking_id` BIGINT,
    IN `p_cancelled_by_id` BIGINT,
    IN `p_reason` VARCHAR(500),
    OUT `p_status_code` INT,
    OUT `p_message` VARCHAR(255)
)
proc_label: BEGIN
    DECLARE `v_booking_status` VARCHAR(20);
    DECLARE `v_booking_type` VARCHAR(20);
    DECLARE `v_enrollment_id` BIGINT;
    DECLARE `v_student_id` BIGINT;
    DECLARE `v_slot_id` BIGINT;
    DECLARE `v_session_fee` DECIMAL(12,2);
    DECLARE `v_slot_start` DATETIME;
    DECLARE `v_pt_user_id` BIGINT;
    DECLARE `v_actor_role` VARCHAR(20);
    DECLARE `v_hours_before` DECIMAL(7,2);

    DECLARE `v_refund` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_comp` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_pen` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_comp_due` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_pen_due` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_shortfall` DECIMAL(12,2) DEFAULT 0.00;
    DECLARE `v_lock_id` BIGINT;
    DECLARE `v_comp_user_id` BIGINT;
    DECLARE `v_pen_user_id` BIGINT;
    DECLARE `v_applied` DECIMAL(14,2) DEFAULT 0.00;
    DECLARE `v_settle_code` INT DEFAULT 0;

    DECLARE `v_errno` INT DEFAULT 0;
    DECLARE `v_errmsg` VARCHAR(512) DEFAULT '';

    DECLARE EXIT HANDLER FOR 1213, 1205
    BEGIN
        ROLLBACK;
        SET `p_status_code` = 98;
        SET `p_message` = 'Hệ thống đang bận (xung đột khóa), vui lòng thử lại.';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 `v_errno` = MYSQL_ERRNO, `v_errmsg` = MESSAGE_TEXT;
        ROLLBACK;
        SET `p_status_code` = 99;
        SET `p_message` = LEFT(CONCAT('Lỗi CSDL #', `v_errno`, ': ', `v_errmsg`), 255);
    END;

    SET `p_status_code` = 0;
    SET `p_message` = 'Hủy ca thành công.';

    IF `p_reason` IS NULL OR CHAR_LENGTH(TRIM(`p_reason`)) = 0 THEN
        SET `p_status_code` = 5;
        SET `p_message` = 'Phải nhập lý do hủy ca.';
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    SELECT `enrollment_id` INTO `v_enrollment_id`
    FROM `bookings`
    WHERE `id` = `p_booking_id`;

    IF `v_enrollment_id` IS NOT NULL THEN
        SELECT `id` INTO `v_lock_id`
        FROM `enrollments`
        WHERE `id` = `v_enrollment_id`
        FOR UPDATE;
    END IF;

    SELECT b.`status`, b.`booking_type`, b.`enrollment_id`, b.`student_id`, b.`slot_id`, b.`session_fee`,
           s.`start_time`, p.`user_id`
    INTO `v_booking_status`, `v_booking_type`, `v_enrollment_id`, `v_student_id`, `v_slot_id`, `v_session_fee`,
         `v_slot_start`, `v_pt_user_id`
    FROM `bookings` b
    JOIN `availability_slots` s ON b.`slot_id` = s.`id`
    JOIN `pt_profiles` p ON s.`pt_id` = p.`id`
    WHERE b.`id` = `p_booking_id`
    FOR UPDATE OF b;

    IF `v_booking_status` IS NULL THEN
        ROLLBACK;
        SET `p_status_code` = 1;
        SET `p_message` = 'Ca tập không tồn tại.';
        LEAVE proc_label;
    END IF;

    IF `v_booking_status` IN ('COMPLETED', 'CANCELLED') THEN
        ROLLBACK;
        SET `p_status_code` = 2;
        SET `p_message` = 'Ca tập đã hoàn thành hoặc đã bị hủy trước đó.';
        LEAVE proc_label;
    END IF;

    IF `p_cancelled_by_id` IS NULL THEN
        SET `v_actor_role` = 'SYSTEM';
    ELSE
        SELECT `role`
        INTO `v_actor_role`
        FROM `users`
        WHERE `id` = `p_cancelled_by_id`;

        IF `v_actor_role` IS NULL THEN
            ROLLBACK;
            SET `p_status_code` = 3;
            SET `p_message` = 'Người thực hiện hủy không tồn tại.';
            LEAVE proc_label;
        END IF;

        IF (`v_actor_role` = 'STUDENT' AND `p_cancelled_by_id` <> `v_student_id`)
           OR (`v_actor_role` = 'PT' AND `p_cancelled_by_id` <> `v_pt_user_id`) THEN
            ROLLBACK;
            SET `p_status_code` = 4;
            SET `p_message` = 'Bạn không có quyền hủy ca tập này.';
            LEAVE proc_label;
        END IF;
    END IF;

    SET `v_hours_before` = `fn_hours_before`(`v_slot_start`, NOW());

    IF `v_hours_before` <= 0 AND `v_actor_role` IN ('STUDENT', 'PT') THEN
        ROLLBACK;
        SET `p_status_code` = 6;
        SET `p_message` = 'Ca tập đã bắt đầu, chỉ Admin/Hệ thống mới được hủy.';
        LEAVE proc_label;
    END IF;

    IF `v_booking_status` = 'CONFIRMED' THEN
        IF `v_hours_before` >= 24.0 THEN
            IF `v_actor_role` = 'STUDENT' THEN
                -- Học viên hủy trước >= 24h: Hoàn 1 buổi, phạt học viên 50%, đền bù PT 50%
                SET `v_pen_user_id` = `v_student_id`;
                SET `v_pen_due` = ROUND(`v_session_fee` * 0.5, 2);
                SET `v_comp_due` = ROUND(`v_session_fee` * 0.5, 2);
                SET `v_comp_user_id` = `v_pt_user_id`;
            END IF;
            -- PT hủy trước >= 24h: Hoàn 1 buổi, không phạt
        ELSE
            -- Hủy sát giờ < 24h
            IF `v_actor_role` = 'STUDENT' THEN
                -- Học viên hủy sát giờ: Mất buổi, PT hưởng 90% thù lao, Sàn thu 10%
                IF `v_booking_type` = 'PACKAGE' AND `v_enrollment_id` IS NOT NULL THEN
                    CALL `sp_consume_session`(`v_enrollment_id`);
                END IF;
                SET `v_comp_due` = ROUND(`v_session_fee` * 0.9, 2);
                SET `v_comp_user_id` = `v_pt_user_id`;
                SET `v_comp` = `v_comp_due`;
            ELSEIF `v_actor_role` = 'PT' THEN
                -- PT hủy sát giờ: Hoàn 1 buổi, phạt PT 100%, đền bù học viên 100%
                SET `v_pen_user_id` = `v_pt_user_id`;
                SET `v_pen_due` = ROUND(`v_session_fee` * 1.0, 2);
                SET `v_comp_due` = ROUND(`v_session_fee` * 1.0, 2);
                SET `v_comp_user_id` = `v_student_id`;
            END IF;
        END IF;
    END IF;

    UPDATE `bookings`
    SET `status` = 'CANCELLED'
    WHERE `id` = `p_booking_id`;

    IF `v_pen_due` > 0 THEN
        CALL `sp_wallet_settle`(
            `v_pen_user_id`, `v_pen_due`, 'PENALTY', `v_enrollment_id`,
            CONCAT('CXL-', `p_booking_id`, '-PEN'),
            IF(`v_actor_role` = 'STUDENT', CONCAT('Phạt học viên hủy báo trước ca #', `p_booking_id`), CONCAT('Phạt PT hủy sát giờ ca #', `p_booking_id`)),
            `v_applied`, `v_settle_code`
        );
        IF `v_settle_code` <> 0 THEN
            ROLLBACK;
            SET `p_status_code` = 10;
            SET `p_message` = 'Không tìm thấy ví người hủy để thu tiền phạt.';
            LEAVE proc_label;
        END IF;
        SET `v_pen` = `v_applied`;
        SET `v_shortfall` = `v_pen_due` - `v_applied`;
        SET `v_comp` = LEAST(`v_comp_due`, `v_applied`);
    END IF;

    IF `v_comp` > 0 THEN
        CALL `sp_wallet_settle`(
            `v_comp_user_id`, `v_comp`, 'COMPENSATION', `v_enrollment_id`,
            CONCAT('CXL-', `p_booking_id`, '-COMP'),
            CONCAT('Đền bù hủy ca #', `p_booking_id`),
            `v_applied`, `v_settle_code`
        );
        IF `v_settle_code` <> 0 THEN
            ROLLBACK;
            SET `p_status_code` = 10;
            SET `p_message` = 'Không tìm thấy ví để quyết toán tiền đền bù.';
            LEAVE proc_label;
        END IF;
    END IF;

    -- Thu 10% phí dịch vụ sàn nếu học viên hủy sát giờ (< 24h)
    IF `v_booking_status` = 'CONFIRMED' AND `v_hours_before` < 24.0 AND `v_actor_role` = 'STUDENT' AND `v_session_fee` > 0 THEN
        CALL `sp_wallet_settle`(
            1, ROUND(`v_session_fee` * 0.1, 2), 'PLATFORM_FEE', `v_enrollment_id`,
            CONCAT('CXL-', `p_booking_id`, '-PFEE'),
            CONCAT('Phí sàn hủy sát giờ ca #', `p_booking_id`),
            `v_applied`, `v_settle_code`
        );
    END IF;

    INSERT INTO `cancellations` (
        `booking_id`,
        `cancelled_by_id`,
        `cancelled_by_role`,
        `reason`,
        `hours_before_session`,
        `refund_amount`,
        `compensation_amount`,
        `penalty_amount`,
        `penalty_shortfall`,
        `status`,
        `cancelled_at`
    ) VALUES (
        `p_booking_id`,
        `p_cancelled_by_id`,
        `v_actor_role`,
        `p_reason`,
        `v_hours_before`,
        `v_refund`,
        `v_comp`,
        `v_pen`,
        `v_shortfall`,
        'PROCESSED',
        NOW()
    );

    COMMIT;
END$$

-- =====================================================================
-- 5. NẠP TIỀN VÀO VÍ (WALLET TOPUP)
-- =====================================================================

-- Mục đích: Nạp tiền vào ví của người dùng; hỗ trợ cơ chế Idempotent (chống nạp trùng tiền khi gửi lại cùng mã giao dịch txn_ref) và ghi nhận thanh toán.
DROP PROCEDURE IF EXISTS `sp_topup_wallet`$$
CREATE PROCEDURE `sp_topup_wallet`(
    IN `p_user_id` BIGINT,
    IN `p_amount` DECIMAL(14,2),
    IN `p_payment_method` VARCHAR(20),
    IN `p_txn_ref` VARCHAR(100),
    OUT `p_new_balance` DECIMAL(14,2),
    OUT `p_status_code` INT,
    OUT `p_message` VARCHAR(255)
)
proc_label: BEGIN
    DECLARE `v_wallet_id` BIGINT;
    DECLARE `v_current_bal` DECIMAL(14,2);
    DECLARE `v_wallet_status` VARCHAR(20);
    DECLARE `v_existing_amount` DECIMAL(14,2);

    DECLARE `v_errno` INT DEFAULT 0;
    DECLARE `v_errmsg` VARCHAR(512) DEFAULT '';

    DECLARE EXIT HANDLER FOR 1062
    BEGIN
        ROLLBACK;
        SET `p_new_balance` = NULL;
        SET `p_status_code` = 5;
        SET `p_message` = 'Mã giao dịch đã được xử lý trước đó (trùng transaction_ref).';
    END;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        GET DIAGNOSTICS CONDITION 1 `v_errno` = MYSQL_ERRNO, `v_errmsg` = MESSAGE_TEXT;
        ROLLBACK;
        SET `p_new_balance` = NULL;
        SET `p_status_code` = 99;
        SET `p_message` = LEFT(CONCAT('Lỗi nạp tiền ví #', `v_errno`, ': ', `v_errmsg`), 255);
    END;

    SET `p_new_balance` = NULL;
    SET `p_status_code` = 0;
    SET `p_message` = 'Nạp tiền thành công.';

    IF `p_amount` IS NULL OR `p_amount` <= 0 THEN
        SET `p_status_code` = 1;
        SET `p_message` = 'Số tiền nạp phải lớn hơn 0.';
        LEAVE proc_label;
    END IF;

    IF `p_payment_method` IS NULL OR `p_payment_method` NOT IN ('BANK_TRANSFER', 'CREDIT_CARD', 'CASH') THEN
        SET `p_status_code` = 3;
        SET `p_message` = 'Phương thức nạp tiền không hợp lệ.';
        LEAVE proc_label;
    END IF;

    IF `p_txn_ref` IS NULL OR CHAR_LENGTH(TRIM(`p_txn_ref`)) = 0 THEN
        SET `p_status_code` = 4;
        SET `p_message` = 'Thiếu mã giao dịch (transaction_ref).';
        LEAVE proc_label;
    END IF;

    START TRANSACTION;

    SELECT `amount` INTO `v_existing_amount`
    FROM `payments`
    WHERE `transaction_ref` = `p_txn_ref`
      AND `payment_type` = 'TOPUP'
      AND `status` = 'SUCCESS'
    LIMIT 1;

    IF `v_existing_amount` IS NOT NULL THEN
        SELECT `balance` INTO `p_new_balance`
        FROM `wallets`
        WHERE `user_id` = `p_user_id`;

        COMMIT;
        SET `p_status_code` = 0;
        SET `p_message` = 'Giao dịch nạp tiền đã được ghi nhận trước đó (idempotent replay).';
        LEAVE proc_label;
    END IF;

    SELECT `id`, `balance`, `status`
    INTO `v_wallet_id`, `v_current_bal`, `v_wallet_status`
    FROM `wallets`
    WHERE `user_id` = `p_user_id`
    FOR UPDATE;

    IF `v_wallet_id` IS NULL THEN
        ROLLBACK;
        SET `p_status_code` = 2;
        SET `p_message` = 'Không tìm thấy ví người dùng.';
        LEAVE proc_label;
    END IF;

    IF `v_wallet_status` <> 'ACTIVE' THEN
        ROLLBACK;
        SET `p_status_code` = 6;
        SET `p_message` = 'Ví đang bị đóng băng (FROZEN), không thể nạp tiền.';
        LEAVE proc_label;
    END IF;

    UPDATE `wallets`
    SET `balance` = `balance` + `p_amount`
    WHERE `id` = `v_wallet_id`;

    SET `p_new_balance` = `v_current_bal` + `p_amount`;

    INSERT INTO `payments` (
        `wallet_id`,
        `amount`,
        `payment_type`,
        `payment_method`,
        `status`,
        `transaction_ref`,
        `created_at`
    ) VALUES (
        `v_wallet_id`,
        `p_amount`,
        'TOPUP',
        `p_payment_method`,
        'SUCCESS',
        `p_txn_ref`,
        NOW()
    );

    COMMIT;
END$$

-- =====================================================================
-- 6. HẾT HẠN GÓI HỌC (BATCH JOB EXPIRATION)
-- =====================================================================

-- Mục đích: Quét định kỳ toàn bộ hợp đồng gói tập đã qua ngày end_date; tự động cập nhật trạng thái sang COMPLETED (nếu hết buổi) hoặc EXPIRED (nếu còn buổi chưa tập hết).
DROP PROCEDURE IF EXISTS `sp_expire_enrollments`$$
CREATE PROCEDURE `sp_expire_enrollments`(
    OUT `p_expired_count` INT
)
BEGIN
    DECLARE `v_done` INT DEFAULT 0;
    DECLARE `v_enroll_id` BIGINT;
    DECLARE `cur_expired` CURSOR FOR
        SELECT `id`
        FROM `enrollments`
        WHERE `status` = 'ACTIVE'
          AND `end_date` < CURDATE();
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET `v_done` = 1;

    SET `p_expired_count` = 0;

    OPEN `cur_expired`;
    read_loop: LOOP
        FETCH `cur_expired` INTO `v_enroll_id`;
        IF `v_done` = 1 THEN
            LEAVE read_loop;
        END IF;

        UPDATE `enrollments`
        SET `status` = IF(`remaining_sessions` = 0, 'COMPLETED', 'EXPIRED')
        WHERE `id` = `v_enroll_id`
          AND `status` = 'ACTIVE';

        SET `p_expired_count` = `p_expired_count` + ROW_COUNT();
    END LOOP;
    CLOSE `cur_expired`;
END$$

-- =====================================================================
-- 7. GIẢI QUYẾT TRANH CHẤP & TỰ ĐỘNG HỦY CA PENDING QUÁ HẠN (DISPUTES & STALE PENDING)
-- =====================================================================

-- Mục đích: Quét tự động hủy các ca PENDING quá 4 tiếng chưa được PT xác nhận, giải phóng khung giờ rảnh (AVAILABLE) chống giữ chỗ ảo (Slot Hoarding).
DROP PROCEDURE IF EXISTS `sp_auto_cancel_stale_bookings`$$
CREATE PROCEDURE `sp_auto_cancel_stale_bookings`(
    OUT `p_cancelled_count` INT
)
BEGIN
    DECLARE `v_done` INT DEFAULT 0;
    DECLARE `v_bk_id` BIGINT;
    DECLARE `v_slot_id` BIGINT;
    DECLARE `cur_stale` CURSOR FOR
        SELECT `id`, `slot_id`
        FROM `bookings`
        WHERE `status` = 'PENDING'
          AND `created_at` < NOW() - INTERVAL 4 HOUR;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET `v_done` = 1;

    SET `p_cancelled_count` = 0;

    OPEN `cur_stale`;
    stale_loop: LOOP
        FETCH `cur_stale` INTO `v_bk_id`, `v_slot_id`;
        IF `v_done` = 1 THEN
            LEAVE stale_loop;
        END IF;

        UPDATE `bookings` SET `status` = 'CANCELLED' WHERE `id` = `v_bk_id`;
        UPDATE `availability_slots` SET `status` = 'AVAILABLE' WHERE `id` = `v_slot_id`;

        INSERT INTO `cancellations` (
            `booking_id`, `cancelled_by_id`, `cancelled_by_role`, `reason`,
            `hours_before_session`, `refund_amount`, `compensation_amount`,
            `penalty_amount`, `penalty_shortfall`, `status`
        ) VALUES (
            `v_bk_id`, NULL, 'SYSTEM', 'Hệ thống tự động hủy ca do PT không duyệt sau 4 giờ',
            4.00, 0.00, 0.00, 0.00, 0.00, 'PROCESSED'
        );

        SET `p_cancelled_count` = `p_cancelled_count` + 1;
    END LOOP;
    CLOSE `cur_stale`;
END$$

-- Mục đích: Phân xử khiếu nại tranh chấp ca tập; nếu chấp thuận khiếu nại (RESOLVED_REFUND) thì hoàn trả +1 buổi tập vào gói học viên.
DROP PROCEDURE IF EXISTS `sp_resolve_booking_dispute`$$
CREATE PROCEDURE `sp_resolve_booking_dispute`(
    IN  `p_dispute_id`  BIGINT,
    IN  `p_action`      VARCHAR(30),
    IN  `p_admin_notes` TEXT,
    OUT `p_status_code` INT,
    OUT `p_message`     VARCHAR(255)
)
proc_label: BEGIN
    DECLARE `v_booking_id`    BIGINT;
    DECLARE `v_enrollment_id` BIGINT;

    SET `p_status_code` = 0;
    SET `p_message` = 'Thành công';

    SELECT `booking_id`
    INTO `v_booking_id`
    FROM `booking_disputes`
    WHERE `id` = `p_dispute_id`
    FOR UPDATE;

    IF `v_booking_id` IS NULL THEN
        SET `p_status_code` = 1;
        SET `p_message` = 'Không tìm thấy hồ sơ khiếu nại.';
        LEAVE proc_label;
    END IF;

    IF `p_action` = 'RESOLVED_REFUND' THEN
        SELECT `enrollment_id` INTO `v_enrollment_id`
        FROM `bookings` WHERE `id` = `v_booking_id`;

        IF `v_enrollment_id` IS NOT NULL THEN
            UPDATE `enrollments`
            SET `remaining_sessions` = `remaining_sessions` + 1,
                `status` = 'ACTIVE'
            WHERE `id` = `v_enrollment_id`;
        END IF;

        UPDATE `attendance`
        SET `status` = 'PRESENT'
        WHERE `booking_id` = `v_booking_id` AND `status` = 'ABSENT';

        UPDATE `booking_disputes`
        SET `status` = 'RESOLVED_REFUND',
            `admin_notes` = `p_admin_notes`,
            `resolved_at` = NOW()
        WHERE `id` = `p_dispute_id`;

        SET `p_message` = 'Đã chấp thuận khiếu nại và hoàn trả 1 buổi tập cho học viên.';

    ELSEIF `p_action` = 'REJECTED' THEN
        UPDATE `booking_disputes`
        SET `status` = 'REJECTED',
            `admin_notes` = `p_admin_notes`,
            `resolved_at` = NOW()
        WHERE `id` = `p_dispute_id`;

        SET `p_message` = 'Đã bác bỏ khiếu nại và gửi thông báo kết luận cho hai bên.';

    ELSEIF `p_action` = 'EVIDENCE_REQUESTED' THEN
        UPDATE `booking_disputes`
        SET `status` = 'EVIDENCE_REQUESTED',
            `admin_notes` = `p_admin_notes`,
            `deadline_at` = NOW() + INTERVAL 48 HOUR
        WHERE `id` = `p_dispute_id`;

        SET `p_message` = 'Đã yêu cầu bổ sung bằng chứng trong thời hạn 48 giờ.';
    ELSE
        SET `p_status_code` = 2;
        SET `p_message` = 'Hành động phân xử không hợp lệ.';
    END IF;
END$$

DELIMITER ;
