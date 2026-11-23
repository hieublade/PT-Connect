package com.PTconnect.backend.dto.response;

import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CancelPreviewResponse {

    private Long bookingId;
    private String cancelledByRole;
    private BigDecimal hoursBeforeSession;
    private boolean restoreSession;
    private BigDecimal refundAmount;
    private BigDecimal compensationAmount;
    private BigDecimal penaltyAmount;
    private String explanation;
}

