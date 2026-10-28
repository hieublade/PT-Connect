package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import com.PTconnect.backend.entity.enums.PaymentType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.math.BigDecimal;
import java.util.List;

public interface PaymentRepository extends JpaRepository<Payment, Long> {
    List<Payment> findByWalletId(Long walletId);
    List<Payment> findByEnrollmentId(Long enrollmentId);
    List<Payment> findByPaymentTypeAndStatus(PaymentType paymentType, PaymentStatus status);
    List<Payment> findAllByOrderByCreatedAtDesc();
    Page<Payment> findAllByOrderByCreatedAtDesc(Pageable pageable);

    @Query("""
           SELECT COALESCE(SUM(p.amount), 0) FROM Payment p 
           WHERE p.paymentType = :paymentType AND p.status = :status
           """)
    BigDecimal sumAmountByPaymentTypeAndStatus(
            @Param("paymentType") PaymentType paymentType,
            @Param("status") PaymentStatus status
    );
}

