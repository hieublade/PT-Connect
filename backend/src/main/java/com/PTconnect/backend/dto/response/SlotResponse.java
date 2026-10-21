package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SlotResponse {

    private Long id;
    private Long ptId;
    private String ptName;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime startTime;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime endTime;

    private SlotStatus status;
    private LocalDateTime createdAt;

    public static SlotResponse fromEntity(AvailabilitySlot slot) {
        if (slot == null) {
            return null;
        }

        Long ptId = null;
        String ptName = null;
        if (slot.getPt() != null) {
            ptId = slot.getPt().getId();
            if (slot.getPt().getPt() != null) {
                ptName = slot.getPt().getPt().getFullName();
            }
        }

        return SlotResponse.builder()
                .id(slot.getId())
                .ptId(ptId)
                .ptName(ptName)
                .startTime(slot.getStartTime())
                .endTime(slot.getEndTime())
                .status(slot.getStatus())
                .createdAt(slot.getCreatedAt())
                .build();
    }
}
