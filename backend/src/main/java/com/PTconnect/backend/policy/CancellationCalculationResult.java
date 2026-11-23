package com.PTconnect.backend.policy;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CancellationCalculationResult {

    private boolean restoreSession;

    @Builder.Default
    private BigDecimal refundAmount = BigDecimal.ZERO;

    @Builder.Default
    private BigDecimal compensationAmount = BigDecimal.ZERO;

    @Builder.Default
    private BigDecimal penaltyAmount = BigDecimal.ZERO;

    @Builder.Default
    private BigDecimal hoursBeforeSession = BigDecimal.ZERO;

    private String explanation;
}

