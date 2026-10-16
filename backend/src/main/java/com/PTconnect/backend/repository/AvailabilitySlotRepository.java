package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.enums.SlotStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AvailabilitySlotRepository extends JpaRepository<AvailabilitySlot, Long> {

    List<AvailabilitySlot> findByPtIdAndStatusAndStartTimeAfterOrderByStartTimeAsc(
            Long ptId, SlotStatus status, LocalDateTime now);

    List<AvailabilitySlot> findByPtIdOrderByStartTimeAsc(Long ptId);

    List<AvailabilitySlot> findByPtIdAndStatusOrderByStartTimeAsc(Long ptId, SlotStatus status);

    boolean existsByPtIdAndStartTime(Long ptId, LocalDateTime startTime);

    // Kiểm tra trùng/chồng thời gian khi tạo hoặc cập nhật slot
    @Query("SELECT s FROM AvailabilitySlot s WHERE s.pt.id = :ptId " +
           "AND (:excludeId IS NULL OR s.id != :excludeId) " +
           "AND s.startTime < :endTime AND s.endTime > :startTime")
    List<AvailabilitySlot> findOverlapping(@Param("ptId") Long ptId,
                                           @Param("startTime") LocalDateTime startTime,
                                           @Param("endTime") LocalDateTime endTime,
                                           @Param("excludeId") Long excludeId);
}
