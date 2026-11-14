USE `ptconnect`;

DROP TRIGGER IF EXISTS `trg_reviews_before_insert`;
DROP TRIGGER IF EXISTS `trg_reviews_before_update`;
DROP TRIGGER IF EXISTS `trg_reviews_after_insert`;
DROP TRIGGER IF EXISTS `trg_reviews_after_update`;
DROP TRIGGER IF EXISTS `trg_reviews_after_delete`;
DROP TRIGGER IF EXISTS `trg_wallets_audit_ledger`;
DROP TRIGGER IF EXISTS `trg_wallet_logs_prevent_update`;
DROP TRIGGER IF EXISTS `trg_wallet_logs_prevent_delete`;
DROP TRIGGER IF EXISTS `trg_bookings_check_student_integrity`;
DROP TRIGGER IF EXISTS `trg_bookings_before_insert`;
DROP TRIGGER IF EXISTS `trg_bookings_after_insert`;
DROP TRIGGER IF EXISTS `trg_bookings_before_update`;
DROP TRIGGER IF EXISTS `trg_bookings_after_cancel`;
DROP TRIGGER IF EXISTS `trg_bookings_after_update`;
DROP TRIGGER IF EXISTS `trg_payments_prevent_update`;
DROP TRIGGER IF EXISTS `trg_payments_before_update`;
DROP TRIGGER IF EXISTS `trg_payments_prevent_delete`;

DELIMITER $$

-- =====================================================================
-- 1. NHÓM ĐÁNH GIÁ (REVIEWS)
-- Mục đích: Kiểm soát đánh giá hợp lệ (chỉ đánh giá ca COMPLETED) và tự động đồng bộ rating của PT.
-- =====================================================================

CREATE TRIGGER `trg_reviews_before_insert`
BEFORE INSERT ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_status VARCHAR(20);

  SELECT `status` INTO v_status
  FROM `bookings`
  WHERE `id` = NEW.`booking_id`;

  IF v_status IS NULL OR v_status <> 'COMPLETED' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Chỉ được đánh giá ca tập đã hoàn thành (COMPLETED).';
  END IF;
END$$

CREATE TRIGGER `trg_reviews_before_update`
BEFORE UPDATE ON `reviews`
FOR EACH ROW
BEGIN
  IF NEW.`booking_id` <> OLD.`booking_id` THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Không được chuyển đánh giá sang ca tập khác.';
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;

  SELECT s.`pt_id` INTO v_pt_id
  FROM `bookings` b
  JOIN `availability_slots` s ON b.`slot_id` = s.`id`
  WHERE b.`id` = NEW.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    CALL `sp_recalc_pt_rating`(v_pt_id);
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_update`
AFTER UPDATE ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;

  SELECT s.`pt_id` INTO v_pt_id
  FROM `bookings` b
  JOIN `availability_slots` s ON b.`slot_id` = s.`id`
  WHERE b.`id` = NEW.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    CALL `sp_recalc_pt_rating`(v_pt_id);
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_delete`
AFTER DELETE ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;

  SELECT s.`pt_id` INTO v_pt_id
  FROM `bookings` b
  JOIN `availability_slots` s ON b.`slot_id` = s.`id`
  WHERE b.`id` = OLD.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    CALL `sp_recalc_pt_rating`(v_pt_id);
  END IF;
END$$

-- =====================================================================
-- 2. NHÓM VÍ & SỔ CÁI KIỂM TOÁN TÀI CHÍNH (WALLETS & AUDIT LOGS)
-- Mục đích: Tự động ghi chép biến động số dư ví vào sổ cái và ngăn chặn mọi hành vi sửa/xóa nhật ký tài chính.
-- =====================================================================

CREATE TRIGGER `trg_wallets_audit_ledger`
AFTER UPDATE ON `wallets`
FOR EACH ROW
BEGIN
  DECLARE v_action VARCHAR(30);

  IF OLD.`balance` <> NEW.`balance` OR OLD.`locked_balance` <> NEW.`locked_balance` THEN
    IF NEW.`balance` > OLD.`balance` THEN
      SET v_action = 'TOPUP';
    ELSE
      SET v_action = 'PAYMENT';
    END IF;

    INSERT INTO `wallet_audit_logs` (
      `wallet_id`,
      `old_balance`,
      `new_balance`,
      `old_locked_balance`,
      `new_locked_balance`,
      `action_type`,
      `reason`,
      `created_at`
    ) VALUES (
      NEW.`id`,
      OLD.`balance`,
      NEW.`balance`,
      OLD.`locked_balance`,
      NEW.`locked_balance`,
      v_action,
      CONCAT('Tự động ghi nhận biến động số dư (', v_action, ')'),
      NOW()
    );
  END IF;
END$$

CREATE TRIGGER `trg_wallet_logs_prevent_update`
BEFORE UPDATE ON `wallet_audit_logs`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = '[BẢO MẬT TÀI CHÍNH] wallet_audit_logs là sổ cái chỉ-thêm, nghiêm cấm sửa!';
END$$

CREATE TRIGGER `trg_wallet_logs_prevent_delete`
BEFORE DELETE ON `wallet_audit_logs`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = '[BẢO MẬT TÀI CHÍNH] wallet_audit_logs là sổ cái chỉ-thêm, nghiêm cấm xóa!';
END$$

-- =====================================================================
-- 3. NHÓM VÒNG ĐỜI CA TẬP (BOOKINGS)
-- Mục đích: Kiểm soát chuyển trạng thái booking, tự động khóa/mở khung giờ slot và tiêu thụ buổi tập khi hoàn thành.
-- =====================================================================

CREATE TRIGGER `trg_bookings_before_insert`
BEFORE INSERT ON `bookings`
FOR EACH ROW
BEGIN
  DECLARE v_slot_pt_id BIGINT;
  DECLARE v_slot_status VARCHAR(20);
  DECLARE v_course_pt_id BIGINT;

  SELECT `pt_id`, `status` INTO v_slot_pt_id, v_slot_status
  FROM `availability_slots`
  WHERE `id` = NEW.`slot_id`;

  IF NEW.`status` IN ('PENDING', 'CONFIRMED')
     AND v_slot_status IS NOT NULL AND v_slot_status <> 'AVAILABLE' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Khung giờ không ở trạng thái AVAILABLE, không thể đặt.';
  END IF;

  IF NEW.`booking_type` = 'PACKAGE' AND NEW.`enrollment_id` IS NOT NULL THEN
    SELECT c.`pt_id` INTO v_course_pt_id
    FROM `enrollments` e
    JOIN `courses` c ON e.`course_id` = c.`id`
    WHERE e.`id` = NEW.`enrollment_id`;

    IF v_course_pt_id IS NOT NULL AND v_slot_pt_id IS NOT NULL AND v_course_pt_id <> v_slot_pt_id THEN
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Hợp đồng không thuộc PT của khung giờ này.';
    END IF;
  END IF;
END$$

CREATE TRIGGER `trg_bookings_after_insert`
AFTER INSERT ON `bookings`
FOR EACH ROW
BEGIN
  IF NEW.`status` IN ('PENDING', 'CONFIRMED', 'COMPLETED') THEN
    UPDATE `availability_slots`
    SET `status` = 'BOOKED'
    WHERE `id` = NEW.`slot_id` AND `status` = 'AVAILABLE';
  END IF;
END$$

CREATE TRIGGER `trg_bookings_before_update`
BEFORE UPDATE ON `bookings`
FOR EACH ROW
BEGIN
  IF NEW.`slot_id` <> OLD.`slot_id`
     OR NEW.`student_id` <> OLD.`student_id`
     OR NEW.`booking_type` <> OLD.`booking_type`
     OR NOT (NEW.`enrollment_id` <=> OLD.`enrollment_id`)
     OR NEW.`session_fee` <> OLD.`session_fee` THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Không được sửa slot/học viên/hợp đồng/loại/phí của booking.';
  END IF;

  IF NEW.`status` <> OLD.`status` THEN
    IF NOT (
         (OLD.`status` = 'PENDING'   AND NEW.`status` IN ('CONFIRMED', 'CANCELLED'))
      OR (OLD.`status` = 'CONFIRMED' AND NEW.`status` IN ('COMPLETED', 'CANCELLED'))
    ) THEN
      SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Chuyển trạng thái booking không hợp lệ.';
    END IF;
  END IF;
END$$

CREATE TRIGGER `trg_bookings_after_update`
AFTER UPDATE ON `bookings`
FOR EACH ROW
BEGIN
  IF OLD.`status` <> NEW.`status` THEN
    IF NEW.`status` = 'CANCELLED' THEN
      UPDATE `availability_slots`
      SET `status` = 'AVAILABLE'
      WHERE `id` = NEW.`slot_id` AND `status` = 'BOOKED';

    ELSEIF NEW.`status` = 'COMPLETED'
           AND NEW.`booking_type` = 'PACKAGE' AND NEW.`enrollment_id` IS NOT NULL THEN
      CALL `sp_consume_session`(NEW.`enrollment_id`);
    END IF;
  END IF;
END$$

-- =====================================================================
-- 4. NHÓM BẢO VỆ GIAO DỊCH THANH TOÁN (PAYMENTS)
-- Mục đích: Đảm bảo bảng thanh toán là nhật ký chỉ-thêm (append-only), chỉ cho phép PENDING sang SUCCESS/FAILED đúng 1 lần.
-- =====================================================================

CREATE TRIGGER `trg_payments_before_update`
BEFORE UPDATE ON `payments`
FOR EACH ROW
BEGIN
  IF NOT (
        OLD.`status` = 'PENDING'
    AND NEW.`status` IN ('SUCCESS', 'FAILED')
    AND NEW.`id` = OLD.`id`
    AND NEW.`wallet_id` = OLD.`wallet_id`
    AND NEW.`enrollment_id` <=> OLD.`enrollment_id`
    AND NEW.`amount` = OLD.`amount`
    AND NEW.`payment_type` = OLD.`payment_type`
    AND NEW.`payment_method` = OLD.`payment_method`
    AND NEW.`transaction_ref` <=> OLD.`transaction_ref`
    AND NEW.`created_at` = OLD.`created_at`
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '[BẢO MẬT TÀI CHÍNH] payments chỉ-thêm; chỉ cho PENDING -> SUCCESS/FAILED!';
  END IF;
END$$

CREATE TRIGGER `trg_payments_prevent_delete`
BEFORE DELETE ON `payments`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = '[BẢO MẬT TÀI CHÍNH CSDL] Bảng payments là nhật ký giao dịch chỉ-thêm (append-only), nghiêm cấm xóa bỏ!';
END$$

DELIMITER ;
