-- =====================================================================
-- Trigger tự động cập nhật điểm đánh giá trung bình và tổng lượt review cho PT
-- Milestone 7: Điểm danh, Hủy lịch và Review + Trigger (Hạn chót: 01/11/2026)
-- Yêu cầu: MySQL 8.0.16+
-- =====================================================================

USE ptconnect;

DROP TRIGGER IF EXISTS `trg_reviews_after_insert`;

DELIMITER $$

CREATE TRIGGER `trg_reviews_after_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
  DECLARE v_pt_id BIGINT;
  SELECT `pt_id` INTO v_pt_id FROM `bookings` WHERE `id` = NEW.`booking_id`;

  IF v_pt_id IS NOT NULL THEN
    UPDATE `pt_profiles`
    SET 
      `average_rating` = (
        SELECT ROUND(COALESCE(AVG(r.rating), 0), 2)
        FROM `reviews` r
        JOIN `bookings` b ON r.`booking_id` = b.`id`
        WHERE b.`pt_id` = v_pt_id
      ),
      `total_reviews` = (
        SELECT COUNT(*)
        FROM `reviews` r
        JOIN `bookings` b ON r.`booking_id` = b.`id`
        WHERE b.`pt_id` = v_pt_id
      )
    WHERE `id` = v_pt_id;
  END IF;
END$$

DELIMITER ;
