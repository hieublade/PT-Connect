package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {

    List<Booking> findByStudentIdOrderByCreatedAtDesc(Long studentId);

    List<Booking> findByStudentIdAndStatusOrderByCreatedAtDesc(Long studentId, BookingStatus status);

    List<Booking> findByPtIdOrderByCreatedAtDesc(Long ptId);

    List<Booking> findByPtIdAndStatusOrderByCreatedAtDesc(Long ptId, BookingStatus status);

    List<Booking> findByEnrollmentIdOrderByCreatedAtDesc(Long enrollmentId);

    Optional<Booking> findBySlotId(Long slotId);

    // Kiểm tra học thử: mỗi Student chỉ được 1 buổi thử với mỗi PT
    boolean existsByStudentIdAndPtIdAndBookingType(Long studentId, Long ptId, BookingType type);

    // Khóa dòng cho chống đặt trùng / xử lý đồng thời
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT b FROM Booking b WHERE b.id = :id")
    Optional<Booking> findByIdWithLock(@Param("id") Long id);

    boolean existsByEnrollmentIdAndStatusIn(Long enrollmentId, List<BookingStatus> statuses);

    List<Booking> findAllByOrderByCreatedAtDesc();
}
