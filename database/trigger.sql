USE `ptconnect`;

-- Dọn dẹp sạch sẽ toàn bộ các trigger cũ
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
-- Mục đích: Kiểm soát đánh giá hợp lệ (chỉ được đánh giá ca COMPLETED).
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

-- =====================================================================
-- 2. NHÓM VÍ & SỔ CÁI KIỂM TOÁN TÀI CHÍNH (WALLETS & AUDIT LOGS)
-- Mục đích: Tự động ghi nhận biến động số dư ví vào sổ cái (Audit Ledger).
-- =====================================================================

CREATE TRIGGER `trg_wallets_audit_ledger`
AFTER UPDATE ON `wallets`
FOR EACH ROW
BEGIN
  DECLARE v_action VARCHAR(30);
  DECLARE v_seq_no INT;

  IF OLD.`balance` <> NEW.`balance` OR OLD.`locked_balance` <> NEW.`locked_balance` THEN
    IF NEW.`balance` > OLD.`balance` THEN
      SET v_action = 'TOPUP';
    ELSE
      SET v_action = 'PAYMENT';
    END IF;

    SELECT COALESCE(MAX(`seq_no`), 0) + 1 INTO v_seq_no
    FROM `wallet_audit_logs`
    WHERE `wallet_id` = NEW.`id`;

    INSERT INTO `wallet_audit_logs` (
      `wallet_id`,
      `seq_no`,
      `old_balance`,
      `new_balance`,
      `old_locked_balance`,
      `new_locked_balance`,
      `action_type`,
      `reason`,
      `created_at`
    ) VALUES (
      NEW.`id`,
      v_seq_no,
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

-- =====================================================================
-- 3. NHÓM ĐỒNG BỘ TRẠNG THÁI CA TẬP & KHUNG GIỜ (BOOKINGS & SLOTS)
-- Mục đích: Tự động khóa slot khi đặt lịch, nhả slot khi hủy, và đóng hợp đồng khi hoàn tất buổi cuối.
-- =====================================================================

CREATE TRIGGER `trg_bookings_after_insert`
AFTER INSERT ON `bookings`
FOR EACH ROW
BEGIN
  IF NEW.`status` IN ('PENDING', 'CONFIRMED', 'COMPLETED') THEN
    UPDATE `availability_slots`
    SET `status` = 'BOOKED'
    WHERE `pt_id` = NEW.`pt_id` AND `start_time` = NEW.`slot_start_time` AND `status` = 'AVAILABLE';
  END IF;
END$$

CREATE TRIGGER `trg_bookings_after_update`
AFTER UPDATE ON `bookings`
FOR EACH ROW
BEGIN
  IF OLD.`status` <> NEW.`status` THEN
    -- Khi ca tập bị hủy: tự động trả khung giờ về trạng thái khả dụng (AVAILABLE)
    IF NEW.`status` = 'CANCELLED' THEN
      UPDATE `availability_slots`
      SET `status` = 'AVAILABLE'
      WHERE `pt_id` = NEW.`pt_id` AND `start_time` = NEW.`slot_start_time` AND `status` = 'BOOKED';
    END IF;
    -- Lưu ý kiến trúc: Nghiệp vụ đóng hợp đồng khi hết buổi tập (COMPLETED) được quản lý tập trung và an toàn
    -- tại Application Layer (AttendanceService._complete_session) nhằm đảm bảo Single Source of Truth và tránh Deadlock.
  END IF;
END$$

DELIMITER ;
