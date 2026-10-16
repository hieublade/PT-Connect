package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Attendance;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AttendanceRepository extends JpaRepository<Attendance, Long> {

    Optional<Attendance> findByBookingId(Long bookingId);

    boolean existsByBookingId(Long bookingId);
}
