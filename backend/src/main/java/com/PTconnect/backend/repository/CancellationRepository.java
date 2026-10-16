package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Cancellation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface CancellationRepository extends JpaRepository<Cancellation, Long> {

    Optional<Cancellation> findByBookingId(Long bookingId);

    boolean existsByBookingId(Long bookingId);
}
