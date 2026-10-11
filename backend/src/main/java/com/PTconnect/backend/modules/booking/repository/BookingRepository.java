package com.PTconnect.backend.modules.booking.repository;

import com.PTconnect.backend.common.enums.BookingStatus;
import com.PTconnect.backend.modules.booking.entity.Booking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {
    List<Booking> findByStudentId(Long studentId);
    List<Booking> findBySlotPtProfileIdAndStatus(Long ptProfileId, BookingStatus status);
    Optional<Booking> findBySlotId(Long slotId);
}
