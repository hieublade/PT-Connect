package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.TopupRequest;
import com.PTconnect.backend.dto.response.PaymentResponse;
import com.PTconnect.backend.dto.response.WalletResponse;
import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.Payment;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.Wallet;
import com.PTconnect.backend.entity.enums.PaymentMethod;
import com.PTconnect.backend.entity.enums.PaymentStatus;
import com.PTconnect.backend.entity.enums.PaymentType;
import com.PTconnect.backend.entity.enums.WalletStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.InsufficientBalanceException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.PaymentRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import com.PTconnect.backend.service.impl.WalletServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WalletServiceTest {

    @Mock
    private WalletRepository walletRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private PaymentRepository paymentRepository;

    @InjectMocks
    private WalletServiceImpl walletService;

    private Wallet activeWallet;

    @BeforeEach
    void setUp() {
        activeWallet = Wallet.builder()
                .id(1L)
                .balance(BigDecimal.valueOf(1000000))
                .lockedBalance(BigDecimal.ZERO)
                .status(WalletStatus.ACTIVE)
                .build();
    }

    @Test
    @DisplayName("Thanh toán khóa học thành công: trừ tiền ví và tạo bản ghi Payment")
    void testProcessCoursePurchaseSuccess() {
        when(walletRepository.findByUserId(10L)).thenReturn(Optional.of(activeWallet));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(i -> i.getArgument(0));

        Enrollment enrollment = Enrollment.builder().id(50L).build();
        BigDecimal price = BigDecimal.valueOf(300000);

        Payment payment = walletService.processCoursePurchase(10L, enrollment, price, PaymentMethod.WALLET);

        assertNotNull(payment);
        assertEquals(PaymentType.PURCHASE_PACKAGE, payment.getPaymentType());
        assertEquals(PaymentStatus.SUCCESS, payment.getStatus());
        assertEquals(price, payment.getAmount());
        assertTrue(payment.getTransactionRef().startsWith("TXN_BUY_"));
        assertEquals(BigDecimal.valueOf(700000), activeWallet.getBalance());
        verify(walletRepository).save(activeWallet);
        verify(paymentRepository).save(any(Payment.class));
    }

    @Test
    @DisplayName("Thanh toán khóa học thất bại khi số dư không đủ")
    void testProcessCoursePurchaseInsufficientBalance() {
        Wallet lowBalanceWallet = Wallet.builder()
                .id(1L)
                .balance(BigDecimal.valueOf(100000))
                .lockedBalance(BigDecimal.ZERO)
                .status(WalletStatus.ACTIVE)
                .build();
        when(walletRepository.findByUserId(10L)).thenReturn(Optional.of(lowBalanceWallet));

        Enrollment enrollment = Enrollment.builder().id(50L).build();
        BigDecimal price = BigDecimal.valueOf(300000);

        assertThrows(InsufficientBalanceException.class, () ->
                walletService.processCoursePurchase(10L, enrollment, price, PaymentMethod.WALLET)
        );
    }

    @Test
    @DisplayName("Bồi thường booking thành công: cộng tiền ví và tạo bản ghi COMPENSATION")
    void testProcessBookingCompensationSuccess() {
        when(walletRepository.findByUserId(20L)).thenReturn(Optional.of(activeWallet));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(i -> i.getArgument(0));

        Enrollment enrollment = Enrollment.builder().id(50L).build();
        BigDecimal compAmount = BigDecimal.valueOf(150000);

        Payment payment = walletService.processBookingCompensation(20L, enrollment, compAmount);

        assertNotNull(payment);
        assertEquals(PaymentType.COMPENSATION, payment.getPaymentType());
        assertEquals(compAmount, payment.getAmount());
        assertTrue(payment.getTransactionRef().startsWith("TXN_COMP_"));
        assertEquals(BigDecimal.valueOf(1150000), activeWallet.getBalance());
        verify(walletRepository).save(activeWallet);
    }

    @Test
    @DisplayName("Phạt tiền HLV khi hủy ca tập: trừ tiền phạt và tạo bản ghi REFUND")
    void testProcessBookingPenaltySuccess() {
        when(walletRepository.findByUserId(30L)).thenReturn(Optional.of(activeWallet));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(i -> i.getArgument(0));

        Enrollment enrollment = Enrollment.builder().id(50L).build();
        BigDecimal penaltyAmount = BigDecimal.valueOf(60000);

        Payment payment = walletService.processBookingPenalty(30L, enrollment, penaltyAmount);

        assertNotNull(payment);
        assertEquals(PaymentType.REFUND, payment.getPaymentType());
        assertEquals(penaltyAmount, payment.getAmount());
        assertTrue(payment.getTransactionRef().startsWith("TXN_PENALTY_"));
        assertEquals(BigDecimal.valueOf(940000), activeWallet.getBalance());
        verify(walletRepository).save(activeWallet);
    }

    @Test
    @DisplayName("Lấy mã giao dịch theo hợp đồng thành công")
    void testGetTransactionRefByEnrollmentIdSuccess() {
        Payment p = Payment.builder().transactionRef("TXN_BUY_12345").build();
        when(paymentRepository.findByEnrollmentId(50L)).thenReturn(java.util.List.of(p));

        String ref = walletService.getTransactionRefByEnrollmentId(50L);
        assertEquals("TXN_BUY_12345", ref);
    }
}
