package com.PTconnect.backend.modules.booking.repository;

import com.PTconnect.backend.common.enums.SlotStatus;
import com.PTconnect.backend.modules.booking.entity.AvailabilitySlot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface AvailabilitySlotRepository extends JpaRepository<AvailabilitySlot, Long> {
    List<AvailabilitySlot> findByPtProfileId(Long ptProfileId);
    List<AvailabilitySlot> findByPtProfileIdAndStatus(Long ptProfileId, SlotStatus status);
    boolean existsByPtProfileIdAndStartTimeLessThanAndEndTimeGreaterThan(Long ptProfileId, LocalDateTime end, LocalDateTime start);
}
