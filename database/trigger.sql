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
  UPDATE `pt_profiles`
  SET 
    `average_rating` = (
      SELECT ROUND(COALESCE(AVG(rating), 0), 2)
      FROM `reviews`
      WHERE `pt_id` = NEW.`pt_id`
    ),
    `total_reviews` = (
      SELECT COUNT(*)
      FROM `reviews`
      WHERE `pt_id` = NEW.`pt_id`
    )
  WHERE `id` = NEW.`pt_id`;
END$$

DELIMITER ;
