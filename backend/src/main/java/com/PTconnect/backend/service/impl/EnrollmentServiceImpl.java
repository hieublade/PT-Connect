package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.PurchaseCourseRequest;
import com.PTconnect.backend.dto.response.EnrollmentResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.*;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.InsufficientBalanceException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IEnrollmentService;
import com.PTconnect.backend.service.IWalletService;
import com.PTconnect.backend.util.ContractPdfGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class EnrollmentServiceImpl implements IEnrollmentService {

    private final EnrollmentRepository enrollmentRepository;
    private final CourseRepository courseRepository;
    private final UserRepository userRepository;
    private final IWalletService walletService;
    private final PTProfileRepository ptProfileRepository;
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

        // Kiểm tra học viên có đang theo học khóa này không (chưa hoàn thành hết số buổi)
        List<Enrollment> existingActiveEnrollments = enrollmentRepository
                .findByStudentIdAndCourseIdAndStatus(student.getId(), course.getId(), EnrollmentStatus.ACTIVE);
        Enrollment activeEnrollment = existingActiveEnrollments.stream()
                .filter(e -> e.getRemainingSessions() != null && e.getRemainingSessions() > 0)
                .findFirst()
                .orElse(null);

        if (activeEnrollment != null) {
            int rem = activeEnrollment.getRemainingSessions();
            int tot = activeEnrollment.getTotalSessions();
            log.warn("Học viên {} cố gắng đăng ký trùng khóa học ID {} khi còn {}/{} buổi",
                    studentEmail, course.getId(), rem, tot);
            throw new BadRequestException("Bạn đang có một hợp đồng cho khóa học này còn hiệu lực (còn "
                    + rem + "/" + tot + " buổi chưa hoàn thành). Vui lòng hoàn thành toàn bộ buổi tập trước khi đăng ký tiếp!");
        }

        if (request.getTrainingLocation() == null || request.getTrainingLocation().trim().isEmpty()) {
            throw new BadRequestException("Địa điểm tập luyện cố định không được để trống");
        }

        BigDecimal coursePrice = course.getBasePrice();

        // 1. Tính thời hạn khóa tập
        LocalDate startDate = LocalDate.now();
        LocalDate endDate = startDate.plusDays(course.getValidityDays());

        // 2. Khởi tạo hợp đồng Enrollment (kho buổi ban đầu: remaining = total)
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

        // 3. Xử lý thanh toán tài chính qua IWalletService
        Payment payment = walletService.processCoursePurchase(
                student.getId(),
                savedEnrollment,
                coursePrice,
                request.getPaymentMethod()
        );

        // 4. Cập nhật URL hợp đồng chính thức
        String contractUrl = "/api/v1/enrollments/" + savedEnrollment.getId() + "/contract";
        savedEnrollment.setContractUrl(contractUrl);
        enrollmentRepository.save(savedEnrollment);

        // 5. Sinh hợp đồng điện tử PDF
        try {
            contractPdfGenerator.generateContractPdf(savedEnrollment, payment.getTransactionRef());
        } catch (Exception e) {
            log.warn("Không thể sinh file PDF hợp đồng: {}", e.getMessage());
            // Vẫn tiếp tục nếu sinh file gặp trục trặc, hoặc để transactional xử lý
        }

        log.info("Mua khóa học thành công! Enrollment ID: {}, TxnRef: {}", savedEnrollment.getId(), payment.getTransactionRef());
        return EnrollmentResponse.fromEntity(savedEnrollment);
    }

    @Override
    @Transactional(readOnly = true)
    public List<EnrollmentResponse> getMyEnrollments(String studentEmail) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        List<Enrollment> enrollments = enrollmentRepository.findByStudentIdWithDetails(student.getId());
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
            String txnRef = walletService.getTransactionRefByEnrollmentId(enrollmentId);
            pdfBytes = contractPdfGenerator.generateContractPdf(enrollment, txnRef);
        }

        return pdfBytes;
    }

    @Override
    @Transactional(readOnly = true)
    public List<EnrollmentResponse> getPtEnrollments(String ptEmail) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xem danh sách hợp đồng"));

        return enrollmentRepository.findByPtIdWithDetails(ptProfile.getId()).stream()
                .sorted((e1, e2) -> {
                    LocalDateTime t1 = e1.getCreatedAt() != null ? e1.getCreatedAt() : LocalDateTime.MIN;
                    LocalDateTime t2 = e2.getCreatedAt() != null ? e2.getCreatedAt() : LocalDateTime.MIN;
                    return t2.compareTo(t1);
                })
                .map(EnrollmentResponse::fromEntity)
                .toList();
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
