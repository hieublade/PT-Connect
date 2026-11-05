package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.BookingType;
import jakarta.persistence.LockModeType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {

    List<Booking> findByStudentIdOrderByCreatedAtDesc(Long studentId);

    List<Booking> findByStudentIdAndStatusOrderByCreatedAtDesc(Long studentId, BookingStatus status);

    @Query("SELECT b FROM Booking b WHERE b.slot.pt.id = :ptId ORDER BY b.createdAt DESC")
    List<Booking> findByPtIdOrderByCreatedAtDesc(@Param("ptId") Long ptId);

    @Query("SELECT b FROM Booking b WHERE b.slot.pt.id = :ptId AND b.status = :status ORDER BY b.createdAt DESC")
    List<Booking> findByPtIdAndStatusOrderByCreatedAtDesc(@Param("ptId") Long ptId, @Param("status") BookingStatus status);

    Optional<Booking> findBySlotId(Long slotId);

    // Kiểm tra học thử: mỗi Student chỉ được 1 buổi thử với mỗi PT
    @Query("SELECT COUNT(b) > 0 FROM Booking b WHERE b.student.id = :studentId AND b.slot.pt.id = :ptId AND b.bookingType = :type")
    boolean existsByStudentIdAndPtIdAndBookingType(@Param("studentId") Long studentId, @Param("ptId") Long ptId, @Param("type") BookingType type);

    // Khóa dòng cho chống đặt trùng / xử lý đồng thời
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT b FROM Booking b WHERE b.id = :id")
    Optional<Booking> findByIdWithLock(@Param("id") Long id);

    boolean existsByEnrollmentIdAndStatusIn(Long enrollmentId, List<BookingStatus> statuses);

    // Kiểm tra trùng giờ tập của Student
    @Query("SELECT COUNT(b) > 0 FROM Booking b " +
           "WHERE b.student.id = :studentId " +
           "AND b.status IN :statuses " +
           "AND b.slot.startTime < :endTime " +
           "AND b.slot.endTime > :startTime")
    boolean existsOverlappingBookingForStudent(
            @Param("studentId") Long studentId,
            @Param("statuses") List<BookingStatus> statuses,
            @Param("startTime") LocalDateTime startTime,
            @Param("endTime") LocalDateTime endTime
    );

    List<Booking> findAllByOrderByCreatedAtDesc();

    @Query("""
           SELECT b, c FROM Booking b 
           LEFT JOIN Cancellation c ON c.booking.id = b.id 
           ORDER BY b.createdAt DESC
           """)
    List<Object[]> findBookingsWithCancellation();

    @Query("""
           SELECT b, c FROM Booking b 
           LEFT JOIN Cancellation c ON c.booking.id = b.id 
           ORDER BY b.createdAt DESC
           """)
    Page<Object[]> findBookingsWithCancellation(Pageable pageable);
}

