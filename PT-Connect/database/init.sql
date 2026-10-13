-- =====================================================================
-- CSDL hệ thống PT Marketplace (bản đã sửa)
-- Yêu cầu: MySQL 8.0.16+ (để CHECK constraint có hiệu lực)
-- =====================================================================
CREATE DATABASE IF NOT EXISTS pt_marketplace;
USE pt_marketplace;

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- 1. TABLES
-- ---------------------------------------------------------------------

CREATE TABLE `users` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,pt_profilespt_profilesadminsadminstrainerstrainersusersusers
  `full_name` varchar(100) NOT NULL,
  `email` varchar(150) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) UNIQUE NOT NULL,
  `role` ENUM ('STUDENT', 'PT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
  `status` ENUM ('ACTIVE', 'PENDING', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
  `avatar_url` varchar(500) COMMENT 'URL ảnh đại diện qua CDN công khai',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='1. Quản lý tài khoản và định danh người dùng';

CREATE TABLE `pt_profiles` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `bio` text,
  `experience_years` integer NOT NULL DEFAULT 0,
  `available_locations` text NOT NULL COMMENT 'Mô tả các địa điểm PT có thể nhận dạy (vd: Cali Cầu Giấy, FitZone Thanh Xuân, hoặc tại nhà học viên)',
  `location_pricing_note` text COMMENT 'Mô tả chính sách điều chỉnh giá (vd: Tại phòng tập giá chuẩn; tại nhà học viên phụ thu 20%)',
  `certificate_urls` json COMMENT 'Mảng JSON danh sách URL chứng chỉ (S3 Private/Presigned),pt có thể có nhiều chứng chỉ nên dùng json để định dạng',
  `average_rating` decimal(3,2) NOT NULL DEFAULT 0,
  `total_reviews` integer NOT NULL DEFAULT 0,
  `verification_status` ENUM ('PENDING', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `chk_pt_experience` CHECK (`experience_years` >= 0),
  CONSTRAINT `chk_pt_rating` CHECK (`average_rating` BETWEEN 0 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='2. Hồ sơ năng lực của PT & khu vực nhận dạy';

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='3. Ví điện tử nội bộ phục vụ thanh toán khóa học và xử lý đền bù';

CREATE TABLE `courses` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text,
  `total_sessions` integer NOT NULL COMMENT 'Số buổi cố định của khóa (vd: 12, 24, 36 buổi)',
  `validity_days` integer NOT NULL COMMENT 'Hạn sử dụng khóa tập (ngày)',
  `base_price` decimal(12,2) NOT NULL COMMENT 'Giá gốc chuẩn của khóa tập',
  `status` ENUM ('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_course_sessions` CHECK (`total_sessions` > 0),
  CONSTRAINT `chk_course_validity` CHECK (`validity_days` > 0),
  CONSTRAINT `chk_course_price` CHECK (`base_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='4. Khóa học huấn luyện cố định (Không bán lẻ từng buổi)';

CREATE TABLE `enrollments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `student_id` bigint NOT NULL,
  `course_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `training_location` varchar(255) NOT NULL COMMENT 'Địa điểm tập luyện CỐ ĐỊNH duy nhất được chốt trong hợp đồng',
  `final_price` decimal(12,2) NOT NULL COMMENT 'Giá chốt thực tế của khóa tập theo địa điểm đã chọn',
  `total_sessions` integer NOT NULL,
  `remaining_sessions` integer NOT NULL COMMENT 'Kho buổi tập khả dụng còn lại chưa dùng',
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `contract_url` varchar(500) NOT NULL COMMENT 'URL file hợp đồng điện tử PDF (S3 Private/Presigned)',
  `status` ENUM ('ACTIVE', 'EXPIRED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_enroll_sessions` CHECK (`remaining_sessions` >= 0 AND `remaining_sessions` <= `total_sessions`),
  CONSTRAINT `chk_enroll_dates` CHECK (`end_date` >= `start_date`),
  CONSTRAINT `chk_enroll_price` CHECK (`final_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='5. Hợp đồng khóa tập đã ký và kho buổi tập khả dụng';

CREATE TABLE `availability_slots` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `status` ENUM ('AVAILABLE', 'BOOKED', 'LOCKED') NOT NULL DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_slot_pt_start` (`pt_id`, `start_time`),
  CONSTRAINT `chk_slot_time` CHECK (`end_time` > `start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='6. Khung giờ rảnh làm việc của PT';

CREATE TABLE `bookings` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_type` ENUM ('TRIAL', 'PACKAGE') NOT NULL DEFAULT 'PACKAGE' COMMENT 'TRIAL: Tập thử 0đ; PACKAGE: Trừ từ khóa trong ENROLLMENTS',
  `enrollment_id` bigint COMMENT 'NULL nếu là TRIAL; Bắt buộc có nếu là PACKAGE (Địa điểm tự động theo training_location)',
  `student_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `slot_id` bigint NOT NULL COMMENT 'Slot được đặt. Chống đặt trùng bằng active_slot_id',
  `session_fee` decimal(12,2) NOT NULL COMMENT 'Giá trị quy đổi 1 buổi = final_price / total_sessions (TRIAL = 0)',
  `status` ENUM ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
  `student_note` varchar(255),
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  -- Chỉ có giá trị khi booking còn hiệu lực; booking đã hủy sẽ trả slot lại cho người khác đặt
  `active_slot_id` bigint GENERATED ALWAYS AS (
    IF(`status` IN ('PENDING', 'CONFIRMED', 'COMPLETED'), `slot_id`, NULL)
  ) STORED,
  UNIQUE KEY `uq_active_slot` (`active_slot_id`),
  CONSTRAINT `chk_booking_type_enroll` CHECK (
    (`booking_type` = 'TRIAL' AND `enrollment_id` IS NULL) OR
    (`booking_type` = 'PACKAGE' AND `enrollment_id` IS NOT NULL)
  ),
  CONSTRAINT `chk_booking_fee` CHECK (`session_fee` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='7. Đơn đặt lịch ca tập (Học thử hoặc trừ buổi từ hợp đồng)';

CREATE TABLE `reviews` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL COMMENT 'Mỗi ca tập chỉ đánh giá 1 lần',
  `student_id` bigint NOT NULL,
  `pt_id` bigint NOT NULL,
  `rating` smallint NOT NULL COMMENT 'Đánh giá từ 1 đến 5 sao',
  `comment` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='8. Đánh giá nhận xét của học viên sau khi ca tập hoàn thành';

CREATE TABLE `cancellations` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `cancelled_by_id` bigint NOT NULL,
  `cancelled_by_role` ENUM ('STUDENT', 'PT', 'ADMIN') NOT NULL,
  `reason` varchar(500) NOT NULL,
  `cancelled_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hours_before_session` decimal(5,2) NOT NULL COMMENT 'Số giờ từ lúc hủy đến lúc bắt đầu buổi tập',
  `refund_amount` decimal(12,2) NOT NULL DEFAULT 0 COMMENT 'Quy đổi hoàn tiền hoặc khôi phục 1 buổi vào remaining_sessions',
  `compensation_amount` decimal(12,2) NOT NULL DEFAULT 0 COMMENT 'Tiền đền bù thiệt hại cho bên bị hủy ca',
  `penalty_amount` decimal(12,2) NOT NULL DEFAULT 0 COMMENT 'Tiền phạt bên vi phạm',
  `evidence_url` varchar(500) COMMENT 'URL chứng từ bất khả kháng (Private S3)',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='9. Giáo án huấn luyện cá nhân hóa theo hợp đồng khóa tập';

CREATE TABLE `workouts` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `plan_id` bigint NOT NULL,
  `exercise_name` varchar(150) NOT NULL,
  `target_muscle` varchar(100),
  `sets` integer NOT NULL DEFAULT 3,
  `reps` integer NOT NULL DEFAULT 10,
  `weight_kg` decimal(5,2),
  `rest_seconds` integer NOT NULL DEFAULT 60,
  `video_demo_url` varchar(500) COMMENT 'URL video/ảnh kỹ thuật động tác qua CDN',
  CONSTRAINT `chk_workout_values` CHECK (`sets` > 0 AND `reps` > 0 AND `rest_seconds` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='10. Chi tiết từng bài tập trong giáo án';

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='11. Điểm danh, chấm công xác thực hai phía';

CREATE TABLE `payments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `wallet_id` bigint NOT NULL,
  `enrollment_id` bigint COMMENT 'Giao dịch thanh toán mua khóa học',
  `amount` decimal(14,2) NOT NULL,
  `payment_type` ENUM ('TOPUP', 'PURCHASE_PACKAGE', 'COMPENSATION', 'REFUND') NOT NULL,
  `payment_method` ENUM ('WALLET', 'BANK_TRANSFER', 'CREDIT_CARD', 'CASH') NOT NULL,
  `status` ENUM ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
  `transaction_ref` varchar(100) UNIQUE,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_payment_amount` CHECK (`amount` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='12. Giao dịch tài chính (Mua khóa học, hoàn tiền, đền bù)';

-- ---------------------------------------------------------------------
-- 2. INDEXES
-- ---------------------------------------------------------------------

CREATE INDEX `idx_slots_pt_time` ON `availability_slots` (`pt_id`, `start_time`, `status`);

-- ---------------------------------------------------------------------
-- 3. FOREIGN KEYS (khóa ngoại nằm ở bảng con, trỏ về bảng cha)
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
-- 4. SAMPLE DATA (đúng thứ tự phụ thuộc, không cần tắt FOREIGN_KEY_CHECKS)
-- ---------------------------------------------------------------------

INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `status`) VALUES
  (1, 'Nguyen Van A', 'student.a@ptconnect.vn', '$2a$10$placeholderhash', '0900000001', 'STUDENT', 'ACTIVE'),
  (2, 'Tran Thi B',   'student.b@ptconnect.vn', '$2a$10$placeholderhash', '0900000002', 'STUDENT', 'ACTIVE'),
  (3, 'Le Hoang C',   'pt.hoangc@ptconnect.vn', '$2a$10$placeholderhash', '0900000003', 'PT',      'ACTIVE'),
  (4, 'Pham Minh D',  'pt.minhd@ptconnect.vn',  '$2a$10$placeholderhash', '0900000004', 'PT',      'ACTIVE'),
  (5, 'Admin System', 'admin@ptconnect.vn',     '$2a$10$placeholderhash', '0900000005', 'ADMIN',   'ACTIVE');

INSERT INTO `pt_profiles` (`id`, `user_id`, `experience_years`, `available_locations`, `location_pricing_note`, `average_rating`, `verification_status`) VALUES
  (1, 3, 5, 'Phòng Cali Cầu Giấy; FitZone Thanh Xuân; Nhận dạy tại nhà học viên',
   'Tập tại phòng Cali giá chuẩn; Dạy tại nhà học viên phụ thu 20% tiền đi lại', 4.9, 'VERIFIED'),
  (2, 4, 3, 'Studio cá nhân tại Thanh Xuân; Nhận dạy quanh khu vực Đống Đa',
   'Tập tại Studio cá nhân giá chuẩn; Khác địa điểm thỏa thuận thêm phí di chuyển', 4.8, 'VERIFIED');

INSERT INTO `wallets` (`id`, `user_id`) VALUES
  (1, 1),
  (2, 2),
  (3, 3),
  (4, 4);

INSERT INTO `courses` (`id`, `pt_id`, `title`, `total_sessions`, `validity_days`, `base_price`) VALUES
  (1, 1, 'Gói Giảm Mỡ Chuyên Sâu 12 Tuần', 36, 90, 10800000),
  (2, 2, 'Gói Tăng Cơ Cơ Bản 24 Buổi',     24, 60, 6000000);

INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `pt_id`, `training_location`, `final_price`,
  `total_sessions`, `remaining_sessions`, `start_date`, `end_date`, `contract_url`, `status`) VALUES
  (1, 2, 1, 1, 'Cali Fitness Cầu Giấy', 10800000, 36, 35, '2026-10-01', '2026-12-30',
   'https://storage.ptconnect.vn/contracts/enrollment_1_signed.pdf', 'ACTIVE');

INSERT INTO `availability_slots` (`id`, `pt_id`, `start_time`, `end_time`, `status`) VALUES
  (1, 1, '2026-10-15 08:00:00', '2026-10-15 09:00:00', 'BOOKED'),
  (2, 1, '2026-10-15 09:30:00', '2026-10-15 10:30:00', 'BOOKED'),
  (3, 1, '2026-10-15 17:00:00', '2026-10-15 18:00:00', 'AVAILABLE');

INSERT INTO `bookings` (`id`, `booking_type`, `enrollment_id`, `student_id`, `pt_id`, `slot_id`, `session_fee`, `status`) VALUES
  (1, 'PACKAGE', 1,    2, 1, 1, 300000, 'CONFIRMED'),
  (2, 'TRIAL',   NULL, 1, 1, 2, 0,      'CONFIRMED');