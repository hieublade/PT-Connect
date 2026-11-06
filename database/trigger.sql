-- =====================================================================
-- Trigger tự động cập nhật điểm đánh giá trung bình và tổng lượt review cho PT
-- Yêu cầu: MySQL 8.0.16+
-- Toàn vẹn học viên trong hợp đồng do khóa ngoại ghép fk_booking_enroll_student đảm nhận (BCNF đợt 2)
-- =====================================================================

USE ptconnect;

DROP TRIGGER IF EXISTS `trg_reviews_after_insert`;
DROP TRIGGER IF EXISTS `trg_reviews_after_update`;
DROP TRIGGER IF EXISTS `trg_reviews_after_delete`;
-- Trigger vá lỗi cũ đã được thay bằng khóa ngoại ghép; xóa khỏi các DB đã tạo trước đợt 2
DROP TRIGGER IF EXISTS `trg_bookings_check_student_integrity`;

DELIMITER $$

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
    UPDATE `pt_profiles`
    SET 
      `average_rating` = (
        SELECT ROUND(COALESCE(AVG(r.rating), 0), 2)
        FROM `reviews` r
        JOIN `bookings` b ON r.`booking_id` = b.`id`
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      ),
      `total_reviews` = (
        SELECT COUNT(*) 
        FROM `reviews` r 
        JOIN `bookings` b ON r.`booking_id` = b.`id` 
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      )
    WHERE `id` = v_pt_id;
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
    UPDATE `pt_profiles`
    SET 
      `average_rating` = (
        SELECT ROUND(COALESCE(AVG(r.rating), 0), 2)
        FROM `reviews` r
        JOIN `bookings` b ON r.`booking_id` = b.`id`
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      ),
      `total_reviews` = (
        SELECT COUNT(*) 
        FROM `reviews` r 
        JOIN `bookings` b ON r.`booking_id` = b.`id` 
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      )
    WHERE `id` = v_pt_id;
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
    UPDATE `pt_profiles`
    SET 
      `average_rating` = (
        SELECT ROUND(COALESCE(AVG(r.rating), 0), 2)
        FROM `reviews` r
        JOIN `bookings` b ON r.`booking_id` = b.`id`
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      ),
      `total_reviews` = (
        SELECT COUNT(*) 
        FROM `reviews` r 
        JOIN `bookings` b ON r.`booking_id` = b.`id` 
        JOIN `availability_slots` s ON b.`slot_id` = s.`id`
        WHERE s.`pt_id` = v_pt_id
      )
    WHERE `id` = v_pt_id;
  END IF;
END$$

DELIMITER ;
