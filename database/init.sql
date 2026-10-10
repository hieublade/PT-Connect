SET NAMES utf8mb4;

-- 1. XÓA BẢNG CŨ 
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS availability_slots;
DROP TABLE IF EXISTS pt_profiles;
DROP TABLE IF EXISTS users;

-- 2. TẠO CÁC BẢNG 

-- Mục 6.2: Bảng users
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    role ENUM('STUDENT', 'PT', 'ADMIN') NOT NULL DEFAULT 'STUDENT',
    status ENUM('PENDING', 'ACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mục 6.3: Bảng pt_profiles (Quan hệ 1-1 với users -> UNIQUE user_id)
CREATE TABLE pt_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    specialization VARCHAR(255) NOT NULL,
    price_per_session DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    bio TEXT,
    experience INT NOT NULL DEFAULT 0,
    avatar VARCHAR(255),
    average_rating DECIMAL(3, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pt_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mục 6.4: Bảng availability_slots (Quan hệ N-1 với pt_profiles)
CREATE TABLE availability_slots (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pt_id BIGINT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status ENUM('AVAILABLE', 'BOOKED') NOT NULL DEFAULT 'AVAILABLE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_slot_pt FOREIGN KEY (pt_id) REFERENCES pt_profiles(id) ON DELETE CASCADE,
    CONSTRAINT chk_slot_time CHECK (end_time > start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mục 6.5: Bảng bookings (1 slot chỉ có 1 booking -> UNIQUE slot_id)
CREATE TABLE bookings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    student_id BIGINT NOT NULL,
    slot_id BIGINT NOT NULL UNIQUE,
    note VARCHAR(255),
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_booking_slot FOREIGN KEY (slot_id) REFERENCES availability_slots(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mục 6.6: Bảng reviews (1 booking có tối đa 1 review -> UNIQUE booking_id)
CREATE TABLE reviews (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT NOT NULL UNIQUE,
    student_id BIGINT NOT NULL,
    pt_id BIGINT NOT NULL,
    rating INT NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_pt FOREIGN KEY (pt_id) REFERENCES pt_profiles(id) ON DELETE CASCADE,
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mục 7.5: TRIGGER cập nhật average_rating
DELIMITER $$
CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE pt_profiles
    SET average_rating = (
        SELECT ROUND(AVG(rating), 2)
        FROM reviews
        WHERE pt_id = NEW.pt_id
    )
    WHERE id = NEW.pt_id;
END$$
DELIMITER ;

-- 3. DỮ LIỆU MỒI (SEED DATA)
INSERT INTO users (id, full_name, email, password, phone, role, status) VALUES
(1, 'Hệ thống Quản Trị', 'admin@ptconnect.vn', '$2a$10$wN1xG7jKqXWvR6p5u2vNyeoB/ePq9z1eA6f4L9gT2eD3wY1mH7r.S', '0900000001', 'ADMIN', 'ACTIVE'),
(2, 'Nguyễn Văn Hùng (Coach Hùng)', 'hung.pt@gmail.com', '$2a$10$wN1xG7jKqXWvR6p5u2vNyeoB/ePq9z1eA6f4L9gT2eD3wY1mH7r.S', '0912345678', 'PT', 'ACTIVE'),
(3, 'Trần Thị Mai (Coach Mai)', 'mai.pt@gmail.com', '$2a$10$wN1xG7jKqXWvR6p5u2vNyeoB/ePq9z1eA6f4L9gT2eD3wY1mH7r.S', '0923456789', 'PT', 'ACTIVE'),
(4, 'Lê Văn An (Học viên)', 'an.student@gmail.com', '$2a$10$wN1xG7jKqXWvR6p5u2vNyeoB/ePq9z1eA6f4L9gT2eD3wY1mH7r.S', '0934567890', 'STUDENT', 'ACTIVE'),
(5, 'Phạm Quỳnh Hoa (Học viên)', 'hoa.student@gmail.com', '$2a$10$wN1xG7jKqXWvR6p5u2vNyeoB/ePq9z1eA6f4L9gT2eD3wY1mH7r.S', '0945678901', 'STUDENT', 'ACTIVE');

INSERT INTO pt_profiles (id, user_id, specialization, price_per_session, bio, experience, avatar, average_rating) VALUES
(1, 2, 'Tăng cơ, Giảm mỡ cấp tốc, Thể hình chuyên nghiệp', 350000.00, '5 năm kinh nghiệm huấn luyện tại các phòng tập chuẩn quốc tế.', 5, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48', 5.00),
(2, 3, 'Yoga trị liệu, Pilates & Dinh dưỡng điều chỉnh vóc dáng', 400000.00, 'Chứng chỉ Pilates & Yoga Alliance 500h, tận tâm chu đáo.', 4, 'https://images.unsplash.com/photo-1518611012118-696072aa579a', 0.00);

INSERT INTO availability_slots (id, pt_id, start_time, end_time, status) VALUES
(1, 1, '2026-10-15 08:00:00', '2026-10-15 09:30:00', 'BOOKED'),
(2, 1, '2026-10-15 10:00:00', '2026-10-15 11:30:00', 'AVAILABLE'),
(3, 1, '2026-10-16 14:00:00', '2026-10-16 15:30:00', 'AVAILABLE'),
(4, 2, '2026-10-15 07:30:00', '2026-10-15 09:00:00', 'AVAILABLE'),
(5, 2, '2026-10-15 09:30:00', '2026-10-15 11:00:00', 'AVAILABLE');

INSERT INTO bookings (id, student_id, slot_id, note, status) VALUES
(1, 4, 1, 'Em muốn tập trung cải thiện kỹ thuật Deadlift', 'COMPLETED');

INSERT INTO reviews (id, booking_id, student_id, pt_id, rating, comment) VALUES
(1, 1, 4, 1, 5, 'Coach Hùng hướng dẫn rất nhiệt tình, sửa form cực kỳ chi tiết!');