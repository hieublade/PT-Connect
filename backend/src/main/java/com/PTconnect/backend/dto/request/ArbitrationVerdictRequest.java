package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ArbitrationVerdictRequest {

    @NotBlank(message = "Loại phán quyết không được để trống")
    private String verdictType; // REFUND_STUDENT, PAID_PT, FORCE_MAJEURE, CANCEL_CONTRACT_REFUND_STUDENT, CANCEL_CONTRACT_PAID_PT, DISMISS

    private String customNote;

    /**
     * Lý do & Căn cứ phán quyết chi tiết của Hội đồng Trọng tài gửi cho cả 2 bên
     */
    private String verdictReason;

    /**
     * Tùy chọn bỏ qua thời hạn 48 giờ (dành cho Admin khi kiểm thử hoặc trường hợp khẩn cấp)
     */
    private Boolean bypass48hWaiting;
}
