CREATE DATABASE IF NOT EXISTS ptconnect;
USE ptconnect;
SET NAMES utf8mb4;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `booking_disputes`, `attendance`, `payments`, `cancellations`, `reviews`, `bookings`,
  `availability_slots`, `workouts`, `workout_plans`, `wallet_audit_logs`, `enrollments`,
  `courses`, `wallets`, `pt_locations`, `pt_profiles`, `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- 1. BẢNG DỮ LIỆU CHÍNH (TABLES)
-- =====================================================================

CREATE TABLE `users` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(150) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) UNIQUE NOT NULL,
  `role` ENUM ('STUDENT', 'PT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
  `status` ENUM ('ACTIVE', 'PENDING', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
  `avatar_url` varchar(500),
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `pt_profiles` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `bio` text,
  `experience_years` integer NOT NULL DEFAULT 0,
  `location_pricing_note` text,
  `certificate_url` varchar(500),
  `average_rating` decimal(3,2) NOT NULL DEFAULT 0,
  `total_reviews` integer NOT NULL DEFAULT 0,
  `verification_status` ENUM ('PENDING', 'VERIFIED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `chk_pt_experience` CHECK (`experience_years` >= 0),
  CONSTRAINT `chk_pt_rating` CHECK (`average_rating` BETWEEN 0 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `pt_locations` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `location_name` varchar(255) NOT NULL,
  UNIQUE KEY `uq_pt_location` (`pt_id`, `location_name`),
  CONSTRAINT `fk_pt_locations_profile` FOREIGN KEY (`pt_id`) 
      REFERENCES `pt_profiles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `wallets` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `balance` decimal(14,2) NOT NULL DEFAULT 0,
  `locked_balance` decimal(14,2) NOT NULL DEFAULT 0,
  `currency` varchar(10) NOT NULL DEFAULT 'VND',
  `status` ENUM ('ACTIVE', 'FROZEN') NOT NULL DEFAULT 'ACTIVE',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `chk_wallet_balance` CHECK (`balance` >= 0),
  CONSTRAINT `chk_wallet_locked` CHECK (`locked_balance` >= 0),
  CONSTRAINT `chk_wallet_locked_le_balance` CHECK (`locked_balance` <= `balance`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `wallet_audit_logs` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `wallet_id` bigint NOT NULL,
  `old_balance` decimal(14,2) NOT NULL,
  `new_balance` decimal(14,2) NOT NULL,
  `old_locked_balance` decimal(14,2) NOT NULL,
  `new_locked_balance` decimal(14,2) NOT NULL,
  `action_type` ENUM ('TOPUP', 'PAYMENT', 'REFUND', 'COMPENSATION', 'PENALTY') NOT NULL,
  `reason` varchar(255) NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `courses` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text,
  `total_sessions` integer NOT NULL,
  `validity_days` integer NOT NULL,
  `base_price` decimal(12,2) NOT NULL,
  `status` ENUM ('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_course_sessions` CHECK (`total_sessions` > 0),
  CONSTRAINT `chk_course_validity` CHECK (`validity_days` > 0),
  CONSTRAINT `chk_course_price` CHECK (`base_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `enrollments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `student_id` bigint NOT NULL,
  `course_id` bigint NOT NULL,
  `training_location` varchar(255) NOT NULL,
  `final_price` decimal(12,2) NOT NULL,
  `total_sessions` integer NOT NULL,
  `remaining_sessions` integer NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `contract_url` varchar(500) NOT NULL,
  `status` ENUM ('ACTIVE', 'EXPIRED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_enroll_student` (`id`, `student_id`),
  CONSTRAINT `chk_enroll_sessions` CHECK (`remaining_sessions` >= 0 AND `remaining_sessions` <= `total_sessions`),
  CONSTRAINT `chk_enroll_dates` CHECK (`end_date` >= `start_date`),
  CONSTRAINT `chk_enroll_price` CHECK (`final_price` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `availability_slots` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `pt_id` bigint NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `status` ENUM ('AVAILABLE', 'BOOKED', 'LOCKED') NOT NULL DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_slot_pt_start` (`pt_id`, `start_time`),
  CONSTRAINT `chk_slot_time` CHECK (`end_time` > `start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `bookings` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_type` ENUM ('TRIAL', 'PACKAGE') NOT NULL DEFAULT 'PACKAGE',
  `enrollment_id` bigint,
  `student_id` bigint NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `reviews` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `rating` smallint NOT NULL,
  `comment` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_review_rating` CHECK (`rating` BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `cancellations` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `cancelled_by_id` bigint NULL,
  `cancelled_by_role` ENUM ('STUDENT', 'PT', 'ADMIN', 'SYSTEM') NOT NULL DEFAULT 'STUDENT',
  `reason` varchar(500) NOT NULL,
  `cancelled_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `hours_before_session` decimal(7,2) NOT NULL,
  `refund_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `compensation_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `penalty_amount` decimal(12,2) NOT NULL DEFAULT 0,
  `penalty_shortfall` decimal(12,2) NOT NULL DEFAULT 0,
  `evidence_url` varchar(500),
  `status` ENUM ('PROCESSED', 'DISPUTED', 'RESOLVED') NOT NULL DEFAULT 'PROCESSED',
  CONSTRAINT `chk_cancel_amounts` CHECK (
    `refund_amount` >= 0 AND `compensation_amount` >= 0 AND `penalty_amount` >= 0 AND `penalty_shortfall` >= 0
  ),
  CONSTRAINT `chk_cancel_actor` CHECK (
    (`cancelled_by_role` = 'SYSTEM' AND `cancelled_by_id` IS NULL) OR
    (`cancelled_by_role` IN ('STUDENT', 'PT', 'ADMIN') AND `cancelled_by_id` IS NOT NULL)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `workout_plans` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `enrollment_id` bigint NOT NULL,
  `title` varchar(150) NOT NULL,
  `goal` varchar(255),
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_plan_dates` CHECK (`end_date` >= `start_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `workouts` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `plan_id` bigint NOT NULL,
  `exercise_order` integer NOT NULL DEFAULT 1,
  `exercise_name` varchar(150) NOT NULL,
  `target_muscle` varchar(100),
  `sets` integer NOT NULL DEFAULT 3,
  `reps` integer NOT NULL DEFAULT 10,
  `weight_kg` decimal(5,2),
  `rest_seconds` integer NOT NULL DEFAULT 60,
  `video_demo_url` varchar(500),
  UNIQUE KEY `uq_plan_exercise_order` (`plan_id`, `exercise_order`),
  CONSTRAINT `chk_workout_order` CHECK (`exercise_order` > 0),
  CONSTRAINT `chk_workout_values` CHECK (`sets` > 0 AND `reps` > 0 AND `rest_seconds` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `attendance` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint UNIQUE NOT NULL,
  `check_in_time` datetime NULL,
  `check_out_time` datetime,
  `verification_method` ENUM ('QR_CODE', 'OTP', 'GEO_LOCATION') NOT NULL,
  `student_confirmed` boolean NOT NULL DEFAULT false,
  `pt_confirmed` boolean NOT NULL DEFAULT false,
  `status` ENUM ('PRESENT', 'ABSENT', 'LATE') NOT NULL DEFAULT 'PRESENT',
  CONSTRAINT `chk_attendance_time` CHECK (`check_out_time` IS NULL OR `check_in_time` IS NULL OR `check_out_time` >= `check_in_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `payments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `wallet_id` bigint NOT NULL,
  `enrollment_id` bigint,
  `amount` decimal(14,2) NOT NULL,
  `payment_type` ENUM ('TOPUP', 'PURCHASE_PACKAGE', 'COMPENSATION', 'REFUND', 'PENALTY', 'PLATFORM_FEE', 'WITHDRAWAL') NOT NULL,
  `payment_method` ENUM ('WALLET', 'BANK_TRANSFER', 'CREDIT_CARD', 'CASH') NOT NULL,
  `status` ENUM ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
  `transaction_ref` varchar(100) UNIQUE,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `chk_payment_amount` CHECK (`amount` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `booking_disputes` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `booking_id` bigint NOT NULL,
  `sender_id` bigint NOT NULL,
  `sender_role` ENUM ('STUDENT', 'PT') NOT NULL,
  `dispute_type` ENUM ('WRONG_ABSENT', 'PT_NO_SHOW', 'STUDENT_NO_SHOW', 'ATTITUDE_QUALITY', 'CONTRACT_TERMINATION', 'OTHER') NOT NULL DEFAULT 'WRONG_ABSENT',
  `reason` text NOT NULL,
  `evidence_url` varchar(500),
  `counter_evidence_url` varchar(500),
  `counter_argument` text,
  `status` ENUM ('PENDING', 'EVIDENCE_REQUESTED', 'RESOLVED_REFUND', 'REJECTED') NOT NULL DEFAULT 'PENDING',
  `admin_notes` text,
  `deadline_at` timestamp NULL,
  `resolved_at` timestamp NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- 2. CHỈ MỤC TỐI ƯU TRUY VẤN (INDEXES)
-- =====================================================================

CREATE INDEX `idx_slots_pt_time` ON `availability_slots` (`pt_id`, `start_time`, `status`);
CREATE INDEX `idx_bookings_student` ON `bookings` (`student_id`, `status`);
CREATE INDEX `idx_bookings_enroll_status` ON `bookings` (`enrollment_id`, `status`);
CREATE INDEX `idx_wal_audit_wallet` ON `wallet_audit_logs` (`wallet_id`);
CREATE INDEX `idx_wal_audit_created` ON `wallet_audit_logs` (`created_at`);
CREATE INDEX `idx_disputes_booking` ON `booking_disputes` (`booking_id`);
CREATE INDEX `idx_disputes_sender` ON `booking_disputes` (`sender_id`, `status`);

-- =====================================================================
-- 3. RÀNG BUỘC KHÓA NGOẠI (FOREIGN KEYS)
-- =====================================================================

ALTER TABLE `pt_profiles`        ADD FOREIGN KEY (`user_id`)         REFERENCES `users` (`id`);
ALTER TABLE `wallets`            ADD FOREIGN KEY (`user_id`)         REFERENCES `users` (`id`);
ALTER TABLE `courses`            ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `enrollments`        ADD FOREIGN KEY (`student_id`)      REFERENCES `users` (`id`);
ALTER TABLE `enrollments`        ADD FOREIGN KEY (`course_id`)       REFERENCES `courses` (`id`);
ALTER TABLE `availability_slots` ADD FOREIGN KEY (`pt_id`)           REFERENCES `pt_profiles` (`id`);
ALTER TABLE `bookings`           ADD CONSTRAINT `fk_booking_enroll_student` FOREIGN KEY (`enrollment_id`, `student_id`) REFERENCES `enrollments` (`id`, `student_id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`student_id`)      REFERENCES `users` (`id`);
ALTER TABLE `bookings`           ADD FOREIGN KEY (`slot_id`)         REFERENCES `availability_slots` (`id`);
ALTER TABLE `reviews`            ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `cancellations`      ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `cancellations`      ADD FOREIGN KEY (`cancelled_by_id`) REFERENCES `users` (`id`);
ALTER TABLE `workout_plans`      ADD FOREIGN KEY (`enrollment_id`)   REFERENCES `enrollments` (`id`);
ALTER TABLE `workouts`           ADD FOREIGN KEY (`plan_id`)         REFERENCES `workout_plans` (`id`);
ALTER TABLE `attendance`         ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `payments`           ADD FOREIGN KEY (`wallet_id`)       REFERENCES `wallets` (`id`);
ALTER TABLE `payments`           ADD FOREIGN KEY (`enrollment_id`)   REFERENCES `enrollments` (`id`);
ALTER TABLE `wallet_audit_logs` ADD FOREIGN KEY (`wallet_id`)       REFERENCES `wallets` (`id`) ON DELETE RESTRICT;
ALTER TABLE `booking_disputes`   ADD FOREIGN KEY (`booking_id`)      REFERENCES `bookings` (`id`);
ALTER TABLE `booking_disputes`   ADD FOREIGN KEY (`sender_id`)       REFERENCES `users` (`id`);
