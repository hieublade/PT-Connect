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
public class PaymentResponse {

    private Long id;
    private Long walletId;
    private Long enrollmentId;
    private BigDecimal amount;
    private PaymentType paymentType;
    private PaymentMethod paymentMethod;
    private PaymentStatus status;
    private String transactionRef;
    private LocalDateTime createdAt;

    public static PaymentResponse fromEntity(Payment payment) {
        if (payment == null) {
            return null;
        }

        Long eId = (payment.getEnrollment() != null) ? payment.getEnrollment().getId() : null;
        Long wId = (payment.getWallet() != null) ? payment.getWallet().getId() : null;

        return PaymentResponse.builder()
                .id(payment.getId())
                .walletId(wId)
                .enrollmentId(eId)
                .amount(payment.getAmount())
                .paymentType(payment.getPaymentType())
                .paymentMethod(payment.getPaymentMethod())
                .status(payment.getStatus())
                .transactionRef(payment.getTransactionRef())
                .createdAt(payment.getCreatedAt())
                .build();
    }
}
