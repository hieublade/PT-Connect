-- =====================================================================
-- CSDL hệ thống PT Marketplace (Bản đã sửa lỗi & tối ưu hoàn chỉnh)
-- Yêu cầu: MySQL 8.0.16+ 
-- =====================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. TABLES
-- ---------------------------------------------------------------------

CREATE TABLE `users` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(150) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) UNIQUE NOT NULL,
  `role` ENUM ('STUDENT', 'PT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
  `status` ENUM ('ACTIVE', 'PENDING', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
  `avatar_url` varchar(500) COMMENT 'URL ảnh đại diện qua CDN công khai',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Quản lý tài khoản và định danh người dùng';

CREATE TABLE `pt_profiles` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `bio` text,
  `experience_years` integer NOT NULL DEFAULT 0,
  `available_locations` text NOT NULL COMMENT 'Mô tả các địa điểm PT có thể nhận dạy',
  `location_pricing_note` text COMMENT 'Mô tả chính sách điều chỉnh giá',
  `certificate_urls` json COMMENT 'Mảng JSON danh sách URL chứng chỉ',
  `average_rating` decimal(3,2) NOT NULL DEFAULT 0,
  `total_reviews` integer NOT NULL DEFAULT 0,
  `verification_status` ENUM ('PENDING', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `chk_pt_experience` CHECK (`experience_years` >= 0),
  CONSTRAINT `chk_pt_rating` CHECK (`average_rating` BETWEEN 0 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Hồ sơ năng lực của PT & khu vực nhận dạy';

CREATE TABLE `wallets` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `balance` decimal(14,2) NOT NULL DEFAULT 0,
  `locked_balance` decimal(14,2) NOT NULL DEFAULT 0 COMMENT 'Số dư đóng băng tiền cọc giữ chỗ ca tập',
  `currency` varchar(10) NOT NULL DEFAULT 'VND',
  `status` ENUM ('ACTIVE', 'FROZEN') NOT NULL DEFAULT 'ACTIVE',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `chk_wallet_balance` CHECK (`balance` >= 0),
  CONSTRAINT `chk_wallet_locked` CHECK (`locked_balance` >= 0 AND `locked_balance` <= `balance`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Ví điện tử nội bộ phục vụ thanh toán khóa học và xử lý đền bù';

CREATE TABLE `courses` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text,
  `total_sessions` integer NOT NULL COMMENT 'Số buổi cố định của khóa',
  `validity_days` integer NOT NULL COMMENT 'Hạn sử dụng khóa tập (ngày)',
  `base_price` decimal(12,2) NOT NULL COMMENT 'Giá gốc chuẩn của khóa tập',
  `status` ENUM ('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_course_sessions` CHECK (`total_sessions` > 0),
  CONSTRAINT `chk_course_validity` CHECK (`validity_days` > 0),
  CONSTRAINT `chk_course_price` CHECK (`base_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Khóa học huấn luyện cố định';

CREATE TABLE `enrollments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `student_id` bigint NOT NULL,
  `course_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `training_location` varchar(255) NOT NULL COMMENT 'Địa điểm tập luyện CỐ ĐỊNH duy nhất',
  `final_price` decimal(12,2) NOT NULL COMMENT 'Giá chốt thực tế của khóa tập',
  `total_sessions` integer NOT NULL,
  `remaining_sessions` integer NOT NULL COMMENT 'Kho buổi tập khả dụng còn lại chưa dùng',
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `contract_url` varchar(500) NOT NULL COMMENT 'URL file hợp đồng điện tử PDF',
  `status` ENUM ('ACTIVE', 'EXPIRED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_enroll_sessions` CHECK (`remaining_sessions` >= 0 AND `remaining_sessions` <= `total_sessions`),
  CONSTRAINT `chk_enroll_dates` CHECK (`end_date` >= `start_date`),
  CONSTRAINT `chk_enroll_price` CHECK (`final_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Hợp đồng khóa tập đã ký và kho buổi tập khả dụng';

CREATE TABLE `availability_slots` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `status` ENUM ('AVAILABLE', 'BOOKED', 'LOCKED') NOT NULL DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_slot_pt_start` (`pt_id`, `start_time`),
  CONSTRAINT `chk_slot_time` CHECK (`end_time` > `start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Khung giờ rảnh làm việc của PT';

CREATE TABLE `bookings` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_type` ENUM ('TRIAL', 'PACKAGE') NOT NULL DEFAULT 'PACKAGE',
  `enrollment_id` bigint COMMENT 'NULL nếu là TRIAL; Bắt buộc có nếu là PACKAGE',
  `student_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `slot_id` bigint NOT NULL,
  `session_fee` decimal(12,2) NOT NULL,
  `status` ENUM ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
  `student_note` varchar(255),
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `active_slot_id` bigint GENERATED ALWAYS AS (
    IF(`status` IN ('PENDING', 'CONFIRMED', 'COMPLETED'), `slot_id`, NULL)
  ) STORED,
  UNIQUE KEY `uq_active_slot` (`active_slot_id`),
  CONSTRAINT `chk_booking_type_enroll` CHECK (
    (`booking_type` = 'TRIAL' AND `enrollment_id` IS NULL) OR
    (`booking_type` = 'PACKAGE' AND `enrollment_id` IS NOT NULL)
  ),
  CONSTRAINT `chk_booking_fee` CHECK (`session_fee` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Đơn đặt lịch ca tập';

CREATE TABLE `reviews` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `student_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `rating` smallint NOT NULL,
  `comment` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Đánh giá nhận xét của học viên';

CREATE TABLE `cancellations` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `cancelled_by_id` bigint NULL COMMENT 'Có thể NULL nếu do hệ thống tự động hủy',
  `cancelled_by_role` ENUM ('STUDENT', 'PT', 'ADMIN', 'SYSTEM') NOT NULL DEFAULT 'STUDENT',
  `reason` varchar(500) NOT NULL,
  `cancelled_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hours_before_session` decimal(5,2) NOT NULL,
  `refund_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `compensation_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `penalty_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `evidence_url` varchar(500),
  `status` ENUM ('PROCESSED', 'DISPUTED', 'RESOLVED') NOT NULL DEFAULT 'PROCESSED',
  CONSTRAINT `chk_cancel_amounts` CHECK (
    `refund_amount` >= 0 AND `compensation_amount` >= 0 AND `penalty_amount` >= 0
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng xử lý hủy lịch, phạt và chính sách đền bù';

CREATE TABLE `workout_plans` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `enrollment_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `title` varchar(150) NOT NULL,
  `goal` varchar(255),
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_plan_dates` CHECK (`end_date` >= `start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Giáo án huấn luyện cá nhân hóa';

CREATE TABLE `workouts` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `plan_id` bigint NOT NULL,
  `exercise_name` varchar(150) NOT NULL,
  `target_muscle` varchar(100),
  `sets` integer NOT NULL DEFAULT 3,
  `reps` integer NOT NULL DEFAULT 10,
  `weight_kg` decimal(5,2),
  `rest_seconds` integer NOT NULL DEFAULT 60,
  `video_demo_url` varchar(500),
  CONSTRAINT `chk_workout_values` CHECK (`sets` > 0 AND `reps` > 0 AND `rest_seconds` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chi tiết từng bài tập trong giáo án';

CREATE TABLE `attendance` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `check_in_time` datetime NOT NULL,
  `check_out_time` datetime,
  `verification_method` ENUM ('QR_CODE', 'OTP', 'GEO_LOCATION') NOT NULL,
  `student_confirmed` boolean NOT NULL DEFAULT false,
  `pt_confirmed` boolean NOT NULL DEFAULT false,
  `status` ENUM ('PRESENT', 'ABSENT', 'LATE') NOT NULL DEFAULT 'PRESENT',
  CONSTRAINT `chk_attendance_time` CHECK (`check_out_time` IS NULL OR `check_out_time` >= `check_in_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Điểm danh, chấm công xác thực hai phía';

CREATE TABLE `payments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `wallet_id` bigint NOT NULL,
  `enrollment_id` bigint COMMENT 'NULL nếu nạp tiền TOPUP',
  `amount` decimal(14,2) NOT NULL,
  `payment_type` ENUM ('TOPUP', 'PURCHASE_PACKAGE', 'COMPENSATION', 'REFUND') NOT NULL,
  `payment_method` ENUM ('WALLET', 'BANK_TRANSFER', 'CREDIT_CARD', 'CASH') NOT NULL,
  `status` ENUM ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
  `transaction_ref` varchar(100) UNIQUE,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_payment_amount` CHECK (`amount` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Giao dịch tài chính';

-- ---------------------------------------------------------------------
-- 2. INDEXES
-- ---------------------------------------------------------------------

CREATE INDEX `idx_slots_pt_time` ON `availability_slots` (`pt_id`, `start_time`, `status`);
CREATE INDEX `idx_bookings_student` ON `bookings` (`student_id`, `status`);
CREATE INDEX `idx_bookings_pt` ON `bookings` (`pt_id`, `status`);

-- ---------------------------------------------------------------------
-- 3. FOREIGN KEYS
-- ---------------------------------------------------------------------

ALTER TABLE `pt_profiles`        ADD FOREIGN KEY (`user_id`)         REFERENCES `users` (`id`);
ALTER TABLE `wallets`            ADD FOREIGN KEY (`user_id`)         REFERENCES `users` (`id`);
ALTER TABLE `courses`            ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `enrollments`        ADD FOREIGN KEY (`student_id`)      REFERENCES `users` (`id`);
ALTER TABLE `enrollments`        ADD FOREIGN KEY (`course_id`)       REFERENCES `courses` (`id`);
ALTER TABLE `enrollments`        ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `availability_slots` ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`enrollment_id`)   REFERENCES `enrollments` (`id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`student_id`)      REFERENCES `users` (`id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`slot_id`)         REFERENCES `availability_slots` (`id`);
ALTER TABLE `reviews`            ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `reviews`            ADD FOREIGN KEY (`student_id`)      REFERENCES `users` (`id`);
ALTER TABLE `reviews`            ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `cancellations`      ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `cancellations`      ADD FOREIGN KEY (`cancelled_by_id`) REFERENCES `users` (`id`);
ALTER TABLE `workout_plans`      ADD FOREIGN KEY (`enrollment_id`)   REFERENCES `enrollments` (`id`);
ALTER TABLE `workout_plans`      ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `workouts`           ADD FOREIGN KEY (`plan_id`)         REFERENCES `workout_plans` (`id`);
ALTER TABLE `attendance`         ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `payments`           ADD FOREIGN KEY (`wallet_id`)       REFERENCES `wallets` (`id`);
ALTER TABLE `payments`           ADD FOREIGN KEY (`enrollment_id`)   REFERENCES `enrollments` (`id`);

-- ---------------------------------------------------------------------
-- 4. SAMPLE DATA
-- ---------------------------------------------------------------------

INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `status`) VALUES
  (1, 'Nguyen Van A', 'student.a@ptconnect.vn', '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000001', 'STUDENT', 'ACTIVE'),
  (2, 'Tran Thi B',   'student.b@ptconnect.vn', '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000002', 'STUDENT', 'ACTIVE'),
  (3, 'Le Hoang C',   'pt.hoangc@ptconnect.vn', '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000003', 'PT',      'ACTIVE'),
  (4, 'Pham Minh D',  'pt.minhd@ptconnect.vn',  '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000004', 'PT',      'ACTIVE'),
  (5, 'Admin System', 'admin@ptconnect.vn',     '$2a$10$YtxtP0YdZ0Tm1vZ7lPA4reqqnz8OYXLITj7uAUgBSR3Dcz.xBWoFK', '0900000005', 'ADMIN',   'ACTIVE');

INSERT INTO `pt_profiles` (`id`, `user_id`, `experience_years`, `available_locations`, `location_pricing_note`, `average_rating`, `total_reviews`, `verification_status`) VALUES
  (1, 3, 5, 'Phòng Cali Cầu Giấy; FitZone Thanh Xuân; Nhận dạy tại nhà học viên',
   'Tập tại phòng Cali giá chuẩn; Dạy tại nhà học viên phụ thu 20% tiền đi lại', 4.90, 10, 'VERIFIED'),
  (2, 4, 3, 'Studio cá nhân tại Thanh Xuân; Nhận dạy quanh khu vực Đống Đa',
   'Tập tại Studio cá nhân giá chuẩn; Khác địa điểm thỏa thuận thêm phí di chuyển', 4.80, 5, 'VERIFIED');

INSERT INTO `wallets` (`id`, `user_id`, `balance`, `locked_balance`, `currency`, `status`) VALUES
  (1, 1, 5000000.00, 0, 'VND', 'ACTIVE'),
  (2, 2, 4200000.00, 0, 'VND', 'ACTIVE'),
  (3, 3, 0.00,       0, 'VND', 'ACTIVE'),
  (4, 4, 0.00,       0, 'VND', 'ACTIVE');

INSERT INTO `courses` (`id`, `pt_id`, `title`, `total_sessions`, `validity_days`, `base_price`) VALUES
  (1, 1, 'Gói Giảm Mỡ Chuyên Sâu 12 Tuần', 36, 90, 10800000),
  (2, 2, 'Gói Tăng Cơ Cơ Bản 24 Buổi',     24, 60, 6000000);

INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `pt_id`, `training_location`, `final_price`,
  `total_sessions`, `remaining_sessions`, `start_date`, `end_date`, `contract_url`, `status`) VALUES
  (1, 2, 1, 1, 'Cali Fitness Cầu Giấy', 10800000, 36, 35, '2026-10-01', '2026-12-30',
   'https://storage.ptconnect.vn/contracts/enrollment_1_signed.pdf', 'ACTIVE');

INSERT INTO `payments` (`id`, `wallet_id`, `enrollment_id`, `amount`, `payment_type`, `payment_method`, `status`, `transaction_ref`) VALUES
  (1, 2, NULL, 15000000.00, 'TOPUP',            'BANK_TRANSFER', 'SUCCESS', 'TXN_TOPUP_20261001_0001'),
  (2, 2, 1,    10800000.00, 'PURCHASE_PACKAGE', 'WALLET',        'SUCCESS', 'TXN_BUY_20261001_0001');

INSERT INTO `availability_slots` (`id`, `pt_id`, `start_time`, `end_time`, `status`) VALUES
  (1, 1, '2026-10-15 08:00:00', '2026-10-15 09:00:00', 'BOOKED'),
  (2, 1, '2026-10-15 09:30:00', '2026-10-15 10:30:00', 'BOOKED'),
  (3, 1, '2026-10-15 17:00:00', '2026-10-15 18:00:00', 'AVAILABLE');

INSERT INTO `bookings` (`id`, `booking_type`, `enrollment_id`, `student_id`, `pt_id`, `slot_id`, `session_fee`, `status`) VALUES
  (1, 'PACKAGE', 1,    2, 1, 1, 300000, 'CONFIRMED'),
  (2, 'TRIAL',   NULL, 1, 1, 2, 0,      'CONFIRMED');

-- ---------------------------------------------------------------------
-- 5. TRIGGERS
-- ---------------------------------------------------------------------

DELIMITER $$

CREATE TRIGGER `trg_reviews_after_insert`
AFTER INSERT ON `reviews`
FOR EACH ROW
BEGIN
  UPDATE `pt_profiles`
  SET `average_rating` = COALESCE((SELECT ROUND(AVG(`rating`), 2) FROM `reviews` WHERE `pt_id` = NEW.`pt_id`), 0),
      `total_reviews`  = (SELECT COUNT(*) FROM `reviews` WHERE `pt_id` = NEW.`pt_id`)
  WHERE `id` = NEW.`pt_id`;
END$$

CREATE TRIGGER `trg_reviews_after_update`
AFTER UPDATE ON `reviews`
FOR EACH ROW
BEGIN
  -- Cập nhật cho PT mới
  UPDATE `pt_profiles`
  SET `average_rating` = COALESCE((SELECT ROUND(AVG(`rating`), 2) FROM `reviews` WHERE `pt_id` = NEW.`pt_id`), 0),
      `total_reviews`  = (SELECT COUNT(*) FROM `reviews` WHERE `pt_id` = NEW.`pt_id`)
  WHERE `id` = NEW.`pt_id`;

  -- Cập nhật cho PT cũ nếu có đổi pt_id
  IF OLD.`pt_id` <> NEW.`pt_id` THEN
    UPDATE `pt_profiles`
    SET `average_rating` = COALESCE((SELECT ROUND(AVG(`rating`), 2) FROM `reviews` WHERE `pt_id` = OLD.`pt_id`), 0),
        `total_reviews`  = (SELECT COUNT(*) FROM `reviews` WHERE `pt_id` = OLD.`pt_id`)
    WHERE `id` = OLD.`pt_id`;
  END IF;
END$$

CREATE TRIGGER `trg_reviews_after_delete`
AFTER DELETE ON `reviews`
FOR EACH ROW
BEGIN
  UPDATE `pt_profiles`
  SET `average_rating` = COALESCE((SELECT ROUND(AVG(`rating`), 2) FROM `reviews` WHERE `pt_id` = OLD.`pt_id`), 0),
      `total_reviews`  = (SELECT COUNT(*) FROM `reviews` WHERE `pt_id` = OLD.`pt_id`)
  WHERE `id` = OLD.`pt_id`;
END$$

DELIMITER ;