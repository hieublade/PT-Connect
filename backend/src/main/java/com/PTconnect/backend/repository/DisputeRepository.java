package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.DisputeCase;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DisputeRepository extends JpaRepository<DisputeCase, Long> {

    @Query("SELECT d FROM DisputeCase d " +
           "LEFT JOIN FETCH d.booking b " +
           "LEFT JOIN FETCH d.complainant c " +
           "LEFT JOIN FETCH d.defendant df " +
           "ORDER BY d.createdAt DESC")
    List<DisputeCase> findAllWithDetails();

    @Query("SELECT d FROM DisputeCase d " +
           "LEFT JOIN FETCH d.booking b " +
           "LEFT JOIN FETCH d.complainant c " +
           "LEFT JOIN FETCH d.defendant df " +
           "WHERE d.complainant.id = :userId OR d.defendant.id = :userId " +
           "ORDER BY d.createdAt DESC")
    List<DisputeCase> findByUserInvolved(@Param("userId") Long userId);

    List<DisputeCase> findByBookingId(Long bookingId);

    boolean existsByBookingIdAndStatus(Long bookingId, String status);
}
