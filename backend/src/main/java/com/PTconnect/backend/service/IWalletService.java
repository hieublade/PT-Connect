package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.TopupRequest;
import com.PTconnect.backend.dto.response.PaymentResponse;
import com.PTconnect.backend.dto.response.WalletResponse;
import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.enums.PaymentMethod;

import java.math.BigDecimal;

public interface IWalletService {

    WalletResponse getWallet(String userEmail);

    PaymentResponse topup(String userEmail, TopupRequest request);

    Payment processCoursePurchase(Long userId, Enrollment enrollment, BigDecimal amount, PaymentMethod paymentMethod);

    Payment processBookingCompensation(Long userId, Enrollment enrollment, BigDecimal amount);

    Payment processBookingPenalty(Long userId, Enrollment enrollment, BigDecimal amount);

    String getTransactionRefByEnrollmentId(Long enrollmentId);
}
