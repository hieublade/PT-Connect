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

    /**
     * Lấy danh sách đánh giá công khai của PT (Chỉ lấy trạng thái PUBLISHED).
     */
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

    /**
     * Lấy toàn bộ đánh giá của PT (Dành cho chính PT xem để phản biện đánh giá xấu).
     */
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

    /**
     * Lấy danh sách đánh giá do học viên tạo.
     */
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

    /**
     * Lấy danh sách đánh giá cần kiểm duyệt dành cho Quản trị viên (Admin).
     * Bao gồm tất cả đánh giá 1-3 sao hoặc có trạng thái FLAGGED, APPEALED, EVIDENCE_REQUESTED.
     */
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

    /**
     * Tính điểm trung bình đánh giá hợp lệ của PT (chỉ tính đánh giá PUBLISHED).
     */
    @Query("""
           SELECT ROUND(COALESCE(AVG(r.rating), 5.0), 2)
           FROM Review r
           JOIN r.booking b
           JOIN b.slot s
           WHERE s.pt.id = :ptId AND (r.status = 'PUBLISHED' OR r.status IS NULL)
           """)
    Double calculateAverageRatingForPt(@Param("ptId") Long ptId);

    /**
     * Đếm tổng số đánh giá hợp lệ của PT.
     */
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
