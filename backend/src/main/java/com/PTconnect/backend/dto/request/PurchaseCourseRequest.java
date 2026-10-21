package com.PTconnect.backend.dto.request;

import com.PTconnect.backend.entity.enums.PaymentMethod;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PurchaseCourseRequest {

    @NotNull(message = "Mã khóa học không được để trống")
    private Long courseId;

    @NotBlank(message = "Địa điểm tập luyện cố định không được để trống")
    private String trainingLocation;

    @Builder.Default
    private PaymentMethod paymentMethod = PaymentMethod.WALLET;
}
