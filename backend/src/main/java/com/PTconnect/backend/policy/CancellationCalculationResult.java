package com.PTconnect.backend.policy;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;

/**
 * Kết quả tính toán chính sách hủy lịch (Milestone 7).
 * Thể hiện tính đóng gói dữ liệu và đa hình từ CancellationPolicy.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CancellationCalculationResult {

    /**
     * Có khôi phục lại 1 buổi tập vào hợp đồng (remainingSessions + 1) hay không.
     */
    private boolean restoreSession;

    /**
     * Số tiền hoàn lại (thường bằng sessionFee nếu được khôi phục buổi).
     */
    @Builder.Default
    private BigDecimal refundAmount = BigDecimal.ZERO;

    /**
     * Số tiền đền bù (cộng vào ví người bị ảnh hưởng).
     */
    @Builder.Default
    private BigDecimal compensationAmount = BigDecimal.ZERO;

    /**
     * Số tiền phạt (trừ vào ví người hủy ca).
     */
    @Builder.Default
    private BigDecimal penaltyAmount = BigDecimal.ZERO;

    /**
     * Số giờ trước khi ca tập bắt đầu.
     */
    @Builder.Default
    private BigDecimal hoursBeforeSession = BigDecimal.ZERO;

    /**
     * Diễn giải chi tiết chính sách áp dụng.
     */
    private String explanation;
}
