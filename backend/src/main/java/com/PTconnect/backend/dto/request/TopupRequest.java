package com.PTconnect.backend.dto.request;

import com.PTconnect.backend.entity.enums.PaymentMethod;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TopupRequest {

    @NotNull(message = "Số tiền nạp không được để trống")
    @DecimalMin(value = "10000.00", message = "Số tiền nạp tối thiểu là 10,000 VND")
    private BigDecimal amount;

    @Builder.Default
    private PaymentMethod paymentMethod = PaymentMethod.BANK_TRANSFER;
}
