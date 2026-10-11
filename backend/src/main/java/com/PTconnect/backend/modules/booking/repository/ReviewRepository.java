package com.PTconnect.backend.modules.booking.repository;

import com.PTconnect.backend.modules.booking.entity.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {
    Optional<Review> findByBookingId(Long bookingId);
    List<Review> findByPtProfileId(Long ptProfileId);
    List<Review> findByStudentId(Long studentId);
}
