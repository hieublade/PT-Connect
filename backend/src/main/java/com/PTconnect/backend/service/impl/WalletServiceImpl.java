package com.PTconnect.backend.service.impl;

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
import com.PTconnect.backend.service.IWalletService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class WalletServiceImpl implements IWalletService {

    private final WalletRepository walletRepository;
    private final UserRepository userRepository;
    private final PaymentRepository paymentRepository;

    @Override
    @Transactional(readOnly = true)
    public WalletResponse getWallet(String userEmail) {
        User user = getUserByEmail(userEmail);
        Wallet wallet = walletRepository.findByUserId(user.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ví của người dùng"));

        List<Payment> payments = paymentRepository.findByWalletId(wallet.getId());
        List<PaymentResponse> transactionResponses = payments.stream()
                .sorted((p1, p2) -> {
                    LocalDateTime t1 = p1.getCreatedAt() != null ? p1.getCreatedAt() : LocalDateTime.MIN;
                    LocalDateTime t2 = p2.getCreatedAt() != null ? p2.getCreatedAt() : LocalDateTime.MIN;
                    return t2.compareTo(t1);
                })
                .map(PaymentResponse::fromEntity)
                .toList();

        return WalletResponse.fromEntity(wallet, transactionResponses);
    }

    @Override
    @Transactional
    public PaymentResponse topup(String userEmail, TopupRequest request) {
        if (request.getAmount() == null || request.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new BadRequestException("Số tiền nạp phải lớn hơn 0");
        }

        User user = getUserByEmail(userEmail);
        Wallet wallet = walletRepository.findByUserId(user.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ví của người dùng"));

        // Cong tien vao vi qua phuong thuc dong goi nghiep vu cua Entity
        wallet.credit(request.getAmount());
        walletRepository.save(wallet);

        // Sinh ma giao dich duy nhat
        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String shortId = UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String txnRef = "TXN_TOPUP_" + datePrefix + "_" + shortId;

        PaymentMethod method = (request.getPaymentMethod() != null)
                ? request.getPaymentMethod()
                : PaymentMethod.BANK_TRANSFER;

        Payment payment = Payment.builder()
                .wallet(wallet)
                .enrollment(null)
                .amount(request.getAmount())
                .paymentType(PaymentType.TOPUP)
                .paymentMethod(method)
                .status(PaymentStatus.SUCCESS)
                .transactionRef(txnRef)
                .build();

        Payment savedPayment = paymentRepository.save(payment);
        log.info("Nạp tiền ví thành công cho user: {}, số tiền: {}, txnRef: {}", userEmail, request.getAmount(), txnRef);

        return PaymentResponse.fromEntity(savedPayment);
    }

    @Override
    @Transactional
    public Payment processCoursePurchase(Long userId, Enrollment enrollment, BigDecimal amount, PaymentMethod paymentMethod) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new BadRequestException("Số tiền thanh toán khóa học phải lớn hơn 0");
        }

        Wallet wallet = walletRepository.findByUserId(userId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ví của học viên ID: " + userId));

        if (wallet.getStatus() != WalletStatus.ACTIVE) {
            throw new BadRequestException("Ví của bạn đang bị khóa, không thể giao dịch");
        }

        // Trừ tiền ví thông qua nghiệp vụ đóng gói trong Entity (Tell, Don't Ask)
        wallet.debit(amount);
        walletRepository.save(wallet);

        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String shortId = UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String txnRef = "TXN_BUY_" + datePrefix + "_" + shortId;

        PaymentMethod method = (paymentMethod != null) ? paymentMethod : PaymentMethod.WALLET;

        Payment payment = Payment.builder()
                .wallet(wallet)
                .enrollment(enrollment)
                .amount(amount)
                .paymentType(PaymentType.PURCHASE_PACKAGE)
                .paymentMethod(method)
                .status(PaymentStatus.SUCCESS)
                .transactionRef(txnRef)
                .build();

        Payment savedPayment = paymentRepository.save(payment);
        log.info("Thanh toán khóa học thành công cho user ID {}, số tiền: {}, txnRef: {}", userId, amount, txnRef);
        return savedPayment;
    }

    @Override
    @Transactional
    public Payment processBookingCompensation(Long userId, Enrollment enrollment, BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return null;
        }

        Wallet wallet = walletRepository.findByUserId(userId).orElse(null);
        if (wallet == null) {
            log.warn("Không tìm thấy ví của user ID {} để đền bù ca tập", userId);
            return null;
        }

        wallet.credit(amount);
        walletRepository.save(wallet);

        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String shortId = UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String txnRef = "TXN_COMP_" + datePrefix + "_" + shortId;

        Payment payment = Payment.builder()
                .wallet(wallet)
                .enrollment(enrollment)
                .amount(amount)
                .paymentType(PaymentType.COMPENSATION)
                .paymentMethod(PaymentMethod.WALLET)
                .status(PaymentStatus.SUCCESS)
                .transactionRef(txnRef)
                .build();

        Payment savedPayment = paymentRepository.save(payment);
        log.info("Đã đền bù {} vào ví user ID {}, txnRef: {}", amount, userId, txnRef);
        return savedPayment;
    }

    @Override
    @Transactional
    public Payment processBookingPenalty(Long userId, Enrollment enrollment, BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return null;
        }

        Wallet wallet = walletRepository.findByUserId(userId).orElse(null);
        if (wallet == null) {
            log.warn("Không tìm thấy ví của user ID {} để phạt ca tập", userId);
            return null;
        }

        wallet.debitPenalty(amount);
        walletRepository.save(wallet);

        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String shortId = UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String txnRef = "TXN_PENALTY_" + datePrefix + "_" + shortId;

        Payment payment = Payment.builder()
                .wallet(wallet)
                .enrollment(enrollment)
                .amount(amount)
                .paymentType(PaymentType.REFUND)
                .paymentMethod(PaymentMethod.WALLET)
                .status(PaymentStatus.SUCCESS)
                .transactionRef(txnRef)
                .build();

        Payment savedPayment = paymentRepository.save(payment);
        log.info("Đã trừ phạt {} từ ví user ID {}, txnRef: {}", amount, userId, txnRef);
        return savedPayment;
    }

    @Override
    @Transactional(readOnly = true)
    public String getTransactionRefByEnrollmentId(Long enrollmentId) {
        List<Payment> payments = paymentRepository.findByEnrollmentId(enrollmentId);
        return payments.isEmpty() ? "TXN_CONTRACT_" + enrollmentId : payments.get(0).getTransactionRef();
    }

    private User getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + email));
    }
}
