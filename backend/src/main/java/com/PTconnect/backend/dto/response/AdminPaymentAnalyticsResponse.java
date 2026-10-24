package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.enums.PaymentMethod;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import com.PTconnect.backend.entity.enums.PaymentType;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AdminPaymentAnalyticsResponse {

    private Long id;
    private Long walletId;
    private Long userId;
    private String userName;
    private Long enrollmentId;
    private BigDecimal amount;
    private PaymentType paymentType;
    private PaymentMethod paymentMethod;
    private PaymentStatus status;
    private String transactionRef;
    private LocalDateTime createdAt;

    public static AdminPaymentAnalyticsResponse fromEntity(Payment p) {
        if (p == null) return null;
        return AdminPaymentAnalyticsResponse.builder()
                .id(p.getId())
                .walletId(p.getWallet() != null ? p.getWallet().getId() : null)
                .userId(p.getWallet() != null && p.getWallet().getUser() != null ? p.getWallet().getUser().getId() : null)
                .userName(p.getWallet() != null && p.getWallet().getUser() != null ? p.getWallet().getUser().getFullName() : null)
                .enrollmentId(p.getEnrollment() != null ? p.getEnrollment().getId() : null)
                .amount(p.getAmount())
                .paymentType(p.getPaymentType())
                .paymentMethod(p.getPaymentMethod())
                .status(p.getStatus())
                .transactionRef(p.getTransactionRef())
                .createdAt(p.getCreatedAt())
                .build();
    }
}
