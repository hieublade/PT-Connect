package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    List<Review> findByPtIdOrderByCreatedAtDesc(Long ptId);

    List<Review> findByStudentIdOrderByCreatedAtDesc(Long studentId);

    Optional<Review> findByBookingId(Long bookingId);

    boolean existsByBookingId(Long bookingId);
}
