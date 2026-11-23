package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    @Query("""
           SELECT r FROM Review r
           JOIN FETCH r.booking b
           JOIN FETCH b.slot s
           JOIN FETCH s.pt p
           JOIN FETCH b.student st
           WHERE s.pt.id = :ptId AND (r.status = 'PUBLISHED' OR r.status IS NULL)
           ORDER BY r.createdAt DESC
           """)
    List<Review> findPublishedByPtIdOrderByCreatedAtDesc(@Param("ptId") Long ptId);

    @Query("""
           SELECT r FROM Review r
           JOIN FETCH r.booking b
           JOIN FETCH b.slot s
           JOIN FETCH s.pt p
           JOIN FETCH b.student st
           WHERE s.pt.id = :ptId
           ORDER BY r.createdAt DESC
           """)
    List<Review> findAllByPtIdOrderByCreatedAtDesc(@Param("ptId") Long ptId);

    @Query("""
           SELECT r FROM Review r
           JOIN FETCH r.booking b
           JOIN FETCH b.slot s
           JOIN FETCH s.pt p
           JOIN FETCH b.student st
           WHERE b.student.id = :studentId
           ORDER BY r.createdAt DESC
           """)
    List<Review> findByBookingStudentIdOrderByCreatedAtDesc(@Param("studentId") Long studentId);

    @Query("""
           SELECT r FROM Review r
           JOIN FETCH r.booking b
           JOIN FETCH b.slot s
           JOIN FETCH s.pt p
           JOIN FETCH b.student st
           WHERE r.rating <= 3 OR r.status IN ('FLAGGED', 'APPEALED', 'EVIDENCE_REQUESTED', 'REMOVED')
           ORDER BY r.createdAt DESC
           """)
    List<Review> findAllRequiringModeration();

    @Query("""
           SELECT ROUND(COALESCE(AVG(r.rating), 5.0), 2)
           FROM Review r
           JOIN r.booking b
           JOIN b.slot s
           WHERE s.pt.id = :ptId AND (r.status = 'PUBLISHED' OR r.status IS NULL)
           """)
    Double calculateAverageRatingForPt(@Param("ptId") Long ptId);

    @Query("""
           SELECT COUNT(r)
           FROM Review r
           JOIN r.booking b
           JOIN b.slot s
           WHERE s.pt.id = :ptId AND (r.status = 'PUBLISHED' OR r.status IS NULL)
           """)
    Long countPublishedReviewsForPt(@Param("ptId") Long ptId);

    Optional<Review> findByBookingId(Long bookingId);

    boolean existsByBookingId(Long bookingId);
}

