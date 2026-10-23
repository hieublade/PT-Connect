package com.PTconnect.backend.dto.response;

import lombok.*;

import java.math.BigDecimal;

/**
 * DTO trả về kết quả xem trước số tiền hoàn/đền bù/phạt trước khi bấm xác nhận hủy (Milestone 7).
 */
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
