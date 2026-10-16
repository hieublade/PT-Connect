package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface PaymentRepository extends JpaRepository<Payment, Long> {
    List<Payment> findByWalletId(Long walletId);
    List<Payment> findByEnrollmentId(Long enrollmentId);
    List<Payment> findByStatus(PaymentStatus status);
    Optional<Payment> findByTransactionRef(String transactionRef);
    List<Payment> findByWalletIdAndStatus(Long walletId, PaymentStatus status);
}
