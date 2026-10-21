package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.PurchaseCourseRequest;
import com.PTconnect.backend.dto.response.EnrollmentResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.*;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.IEnrollmentService;
import com.PTconnect.backend.util.ContractPdfGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class EnrollmentServiceImpl implements IEnrollmentService {

    private final EnrollmentRepository enrollmentRepository;
    private final CourseRepository courseRepository;
    private final UserRepository userRepository;
    private final WalletRepository walletRepository;
    private final PaymentRepository paymentRepository;
    private final ContractPdfGenerator contractPdfGenerator;

    @Override
    @Transactional
    public EnrollmentResponse purchaseCourse(String studentEmail, PurchaseCourseRequest request) {
        log.info("Bắt đầu xử lý mua khóa học cho học viên {}: courseId={}", studentEmail, request.getCourseId());

        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        Course course = courseRepository.findById(request.getCourseId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khóa học với ID: " + request.getCourseId()));

        if (course.getStatus() != CourseStatus.ACTIVE) {
            throw new BadRequestException("Khóa học hiện không còn mở bán");
        }

        if (request.getTrainingLocation() == null || request.getTrainingLocation().trim().isEmpty()) {
            throw new BadRequestException("Địa điểm tập luyện cố định không được để trống");
        }

        Wallet wallet = walletRepository.findByUserId(student.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ví của học viên"));

        if (wallet.getStatus() != WalletStatus.ACTIVE) {
            throw new BadRequestException("Ví của bạn đang bị khóa, không thể giao dịch");
        }

        BigDecimal coursePrice = course.getBasePrice();
        BigDecimal availableBalance = wallet.getBalance().subtract(wallet.getLockedBalance());
        if (availableBalance.compareTo(coursePrice) < 0) {
            log.warn("Học viên {} không đủ số dư ví: cần {}, hiện có {}", studentEmail, coursePrice, availableBalance);
            throw new BadRequestException("Số dư ví không đủ để thanh toán khóa học. Vui lòng nạp thêm tiền!");
        }

        // 1. Trừ tiền ví thông qua nghiệp vụ đóng gói trong Entity
        wallet.debit(coursePrice);
        walletRepository.save(wallet);

        // 2. Tính thời hạn khóa tập
        LocalDate startDate = LocalDate.now();
        LocalDate endDate = startDate.plusDays(course.getValidityDays());

        // 3. Khởi tạo hợp đồng Enrollment (kho buổi ban đầu: remaining = total)
        Enrollment enrollment = Enrollment.builder()
                .student(student)
                .course(course)
                .pt(course.getPt())
                .trainingLocation(request.getTrainingLocation().trim())
                .finalPrice(coursePrice)
                .totalSessions(course.getTotalSessions())
                .remainingSessions(course.getTotalSessions())
                .startDate(startDate)
                .endDate(endDate)
                .contractUrl("/api/v1/enrollments/contract-generating")
                .status(EnrollmentStatus.ACTIVE)
                .build();

        Enrollment savedEnrollment = enrollmentRepository.save(enrollment);

        // 4. Sinh mã giao dịch duy nhất
        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String shortId = UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String txnRef = "TXN_BUY_" + datePrefix + "_" + shortId;

        // 5. Cập nhật URL hợp đồng chính thức
        String contractUrl = "/api/v1/enrollments/" + savedEnrollment.getId() + "/contract";
        savedEnrollment.setContractUrl(contractUrl);
        enrollmentRepository.save(savedEnrollment);

        // 6. Ghi nhận giao dịch tài chính Payment
        PaymentMethod method = (request.getPaymentMethod() != null)
                ? request.getPaymentMethod()
                : PaymentMethod.WALLET;

        Payment payment = Payment.builder()
                .wallet(wallet)
                .enrollment(savedEnrollment)
                .amount(coursePrice)
                .paymentType(PaymentType.PURCHASE_PACKAGE)
                .paymentMethod(method)
                .status(PaymentStatus.SUCCESS)
                .transactionRef(txnRef)
                .build();

        paymentRepository.save(payment);

        // 7. Sinh hợp đồng điện tử PDF
        try {
            contractPdfGenerator.generateContractPdf(savedEnrollment, txnRef);
        } catch (Exception e) {
            log.warn("Không thể sinh file PDF hợp đồng: {}", e.getMessage());
            // Vẫn tiếp tục nếu sinh file gặp trục trặc, hoặc để transactional xử lý
        }

        log.info("Mua khóa học thành công! Enrollment ID: {}, TxnRef: {}", savedEnrollment.getId(), txnRef);
        return EnrollmentResponse.fromEntity(savedEnrollment);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EnrollmentResponse> getMyEnrollments(String studentEmail) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        List<Enrollment> enrollments = enrollmentRepository.findByStudentId(student.getId());
        return enrollments.stream()
                .sorted((e1, e2) -> {
                    LocalDateTime t1 = e1.getCreatedAt() != null ? e1.getCreatedAt() : LocalDateTime.MIN;
                    LocalDateTime t2 = e2.getCreatedAt() != null ? e2.getCreatedAt() : LocalDateTime.MIN;
                    return t2.compareTo(t1);
                })
                .map(EnrollmentResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public EnrollmentResponse getEnrollmentById(String userEmail, Long enrollmentId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng với ID: " + enrollmentId));

        validateAccess(user, enrollment);

        return EnrollmentResponse.fromEntity(enrollment);
    }

    @Override
    @Transactional(readOnly = true)
    public byte[] getContractPdf(String userEmail, Long enrollmentId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng với ID: " + enrollmentId));

        validateAccess(user, enrollment);

        byte[] pdfBytes = contractPdfGenerator.getExistingContractPdf(enrollmentId);
        if (pdfBytes == null) {
            List<Payment> payments = paymentRepository.findByEnrollmentId(enrollmentId);
            String txnRef = payments.isEmpty() ? "TXN_CONTRACT_" + enrollmentId : payments.get(0).getTransactionRef();
            pdfBytes = contractPdfGenerator.generateContractPdf(enrollment, txnRef);
        }

        return pdfBytes;
    }

    private void validateAccess(User user, Enrollment enrollment) {
        if (user.getRole() == Role.ADMIN) {
            return;
        }

        if (user.getRole() == Role.STUDENT && enrollment.getStudent().getId().equals(user.getId())) {
            return;
        }

        if (user.getRole() == Role.PT && enrollment.getPt() != null && enrollment.getPt().getPt().getId().equals(user.getId())) {
            return;
        }

        throw new AccessDeniedException("Bạn không có quyền truy cập hợp đồng này");
    }
}
