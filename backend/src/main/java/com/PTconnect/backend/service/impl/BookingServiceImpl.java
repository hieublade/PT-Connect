package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CancelBookingRequest;
import com.PTconnect.backend.dto.request.CreateBookingRequest;
import com.PTconnect.backend.dto.request.RejectBookingRequest;
import com.PTconnect.backend.dto.response.BookingResponse;
import com.PTconnect.backend.dto.response.CancelPreviewResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.*;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.BookingConflictException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.policy.CancellationCalculationResult;
import com.PTconnect.backend.policy.CancellationPolicy;
import com.PTconnect.backend.policy.CancellationPolicyFactory;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.IBookingService;
import com.PTconnect.backend.service.IWalletService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Triển khai nghiệp vụ luồng Booking – Trái tim hệ thống (Milestone 6 & 7).
 * Phụ trách bởi: Huy, Hưng, Thắng.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class BookingServiceImpl implements IBookingService {

    private final AvailabilitySlotRepository slotRepository;
    private final BookingRepository bookingRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;
    private final CancellationRepository cancellationRepository;
    private final CancellationPolicyFactory cancellationPolicyFactory;
    private final IWalletService walletService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BookingResponse createBooking(String studentEmail, CreateBookingRequest request) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        // 1. Khóa bi quan (PESSIMISTIC_WRITE) dòng slot để chống đặt trùng đa luồng
        AvailabilitySlot slot = slotRepository.findByIdWithLock(request.getSlotId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khung giờ với ID: " + request.getSlotId()));

        if (slot.getStatus() != SlotStatus.AVAILABLE) {
            throw new BookingConflictException("Khung giờ này đã được đặt hoặc không còn khả dụng");
        }

        if (slot.getStartTime().isBefore(LocalDateTime.now())) {
            throw new BadRequestException("Không thể đặt khung giờ đã trôi qua trong quá khứ");
        }

        List<BookingStatus> activeStatuses = List.of(BookingStatus.PENDING, BookingStatus.CONFIRMED);
        if (bookingRepository.existsOverlappingBookingForStudent(student.getId(), activeStatuses, slot.getStartTime(), slot.getEndTime())) {
            throw new BadRequestException("Bạn đã có một ca tập khác trùng khung giờ này");
        }

        BookingType bookingType = request.getBookingType() != null ? request.getBookingType() : BookingType.PACKAGE;
        Enrollment enrollment = null;
        BigDecimal sessionFee = BigDecimal.ZERO;

        // 2. Xử lý nghiệp vụ theo loại Booking
        if (bookingType == BookingType.TRIAL) {
            // Học thử: Mỗi student chỉ được 1 buổi thử với 1 PT
            if (bookingRepository.existsByStudentIdAndPtIdAndBookingType(student.getId(), slot.getPt().getId(), BookingType.TRIAL)) {
                throw new BadRequestException("Bạn đã từng đặt lịch học thử với Huấn luyện viên này. Mỗi học viên chỉ được học thử 1 lần.");
            }
            sessionFee = BigDecimal.ZERO;
        } else {
            // Đặt theo hợp đồng khóa học (PACKAGE)
            if (request.getEnrollmentId() == null) {
                throw new BadRequestException("Cần chọn hợp đồng khóa học khi đặt lịch theo gói (PACKAGE)");
            }

            enrollment = enrollmentRepository.findByIdWithLock(request.getEnrollmentId())
                    .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng với ID: " + request.getEnrollmentId()));

            if (!enrollment.getStudent().getId().equals(student.getId())) {
                throw new BadRequestException("Hợp đồng này không thuộc về bạn");
            }

            if (!slot.getPt().getId().equals(enrollment.getPt().getId())) {
                throw new BadRequestException("Khung giờ không thuộc về Huấn luyện viên của hợp đồng này");
            }

            if (enrollment.getStatus() != EnrollmentStatus.ACTIVE) {
                throw new BadRequestException("Hợp đồng này hiện không ở trạng thái hoạt động");
            }

            if (LocalDate.now().isAfter(enrollment.getEndDate())) {
                throw new BadRequestException("Hợp đồng khóa học đã hết hạn sử dụng");
            }

            if (slot.getStartTime().toLocalDate().isAfter(enrollment.getEndDate())) {
                throw new BadRequestException("Khung giờ tập vượt quá thời hạn sử dụng của hợp đồng (Hạn chót: " + enrollment.getEndDate() + ")");
            }

            if (enrollment.getRemainingSessions() <= 0) {
                throw new BadRequestException("Hợp đồng đã sử dụng hết số buổi tập");
            }

            // Trừ 1 buổi tập khả dụng (Encapsulation qua consumeSession)
            enrollment.consumeSession();
            enrollmentRepository.save(enrollment);

            if (enrollment.getTotalSessions() != null && enrollment.getTotalSessions() > 0 && enrollment.getFinalPrice() != null) {
                sessionFee = enrollment.getFinalPrice().divide(BigDecimal.valueOf(enrollment.getTotalSessions()), 2, RoundingMode.HALF_UP);
            }
        }

        // 3. Cập nhật trạng thái slot thành BOOKED
        slot.book();
        slotRepository.save(slot);

        // 4. Tạo bản ghi Booking trạng thái PENDING
        Booking booking = Booking.builder()
                .student(student)
                .pt(slot.getPt())
                .slot(slot)
                .enrollment(enrollment)
                .bookingType(bookingType)
                .status(BookingStatus.PENDING)
                .sessionFee(sessionFee)
                .studentNote(request.getStudentNote())
                .build();

        try {
            booking = bookingRepository.saveAndFlush(booking);
        } catch (DataIntegrityViolationException ex) {
            log.warn("Xung đột ràng buộc duy nhất active_slot_id khi đặt slot {}: {}", slot.getId(), ex.getMessage());
            throw new BookingConflictException("Khung giờ này vừa có người khác đặt trước, vui lòng chọn khung giờ khác");
        }

        log.info("Học viên {} đặt thành công booking ID {} (Type: {}, Slot: {})",
                studentEmail, booking.getId(), bookingType, slot.getId());

        return BookingResponse.fromEntity(booking);
    }

    @Override
    @Transactional(readOnly = true)
    public List<BookingResponse> getMyBookings(String studentEmail, BookingStatus status) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        List<Booking> bookings = (status != null)
                ? bookingRepository.findByStudentIdAndStatusOrderByCreatedAtDesc(student.getId(), status)
                : bookingRepository.findByStudentIdOrderByCreatedAtDesc(student.getId());

        return bookings.stream()
                .map(this::mapBookingToResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<BookingResponse> getPTBookings(String ptEmail, BookingStatus status) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        List<Booking> bookings = (status != null)
                ? bookingRepository.findByPtIdAndStatusOrderByCreatedAtDesc(ptProfile.getId(), status)
                : bookingRepository.findByPtIdOrderByCreatedAtDesc(ptProfile.getId());

        return bookings.stream()
                .map(this::mapBookingToResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public BookingResponse getBookingById(String userEmail, Long bookingId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy tài khoản với email: " + userEmail));

        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        boolean isStudent = booking.getStudent() != null && booking.getStudent().getId().equals(user.getId());
        boolean isPT = booking.getPt() != null && booking.getPt().getPt() != null && booking.getPt().getPt().getId().equals(user.getId());
        boolean isAdmin = user.getRole() == Role.ADMIN;

        if (!isStudent && !isPT && !isAdmin) {
            throw new BadRequestException("Bạn không có quyền xem thông tin chi tiết đơn đặt lịch này");
        }

        return mapBookingToResponse(booking);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BookingResponse confirmBooking(String ptEmail, Long bookingId) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền thao tác trên đơn đặt lịch của Huấn luyện viên khác");
        }

        if (booking.getStatus() != BookingStatus.PENDING) {
            throw new BadRequestException("Chỉ có thể xác nhận đơn đặt lịch đang ở trạng thái chờ duyệt (PENDING)");
        }

        booking.confirm();
        booking = bookingRepository.save(booking);

        log.info("PT {} đã xác nhận booking ID {}", ptEmail, booking.getId());
        return mapBookingToResponse(booking);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BookingResponse rejectBooking(String ptEmail, Long bookingId, RejectBookingRequest request) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền thao tác trên đơn đặt lịch của Huấn luyện viên khác");
        }

        if (booking.getStatus() != BookingStatus.PENDING) {
            throw new BadRequestException("Chỉ có thể từ chối đơn đặt lịch đang ở trạng thái chờ duyệt (PENDING)");
        }

        String reason = (request != null && request.getReason() != null && !request.getReason().isBlank())
                ? request.getReason().trim()
                : "Huấn luyện viên từ chối lịch ca tập";

        CancellationPolicy policy = cancellationPolicyFactory.getPolicy(Role.PT);
        CancellationCalculationResult result = policy.calculate(booking, LocalDateTime.now(), reason, null);

        log.info("PT {} đã từ chối booking ID {} với lý do: {}", ptEmail, booking.getId(), reason);
        return executeCancellation(booking, ptProfile.getPt(), "PT", reason, null, result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BookingResponse cancelBookingByStudent(String studentEmail, Long bookingId, CancelBookingRequest request) {
        User student = userRepository.findByEmail(studentEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy học viên với email: " + studentEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getStudent().getId().equals(student.getId())) {
            throw new BadRequestException("Bạn không có quyền hủy đơn đặt lịch của học viên khác");
        }

        if (booking.getStatus() == BookingStatus.CANCELLED) {
            throw new BadRequestException("Đơn đặt lịch này đã được hủy trước đó");
        }

        if (booking.getStatus() == BookingStatus.COMPLETED) {
            throw new BadRequestException("Không thể hủy ca tập đã hoàn thành");
        }

        String reason = (request != null && request.getReason() != null && !request.getReason().isBlank())
                ? request.getReason().trim()
                : "Học viên hủy lịch ca tập";

        String evidenceUrl = (request != null) ? request.getEvidenceUrl() : null;

        CancellationPolicy policy = cancellationPolicyFactory.getPolicy(Role.STUDENT);
        CancellationCalculationResult result = policy.calculate(booking, LocalDateTime.now(), reason, evidenceUrl);

        return executeCancellation(booking, student, "STUDENT", reason, evidenceUrl, result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public BookingResponse cancelBookingByPT(String ptEmail, Long bookingId, CancelBookingRequest request) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền thao tác trên đơn đặt lịch của Huấn luyện viên khác");
        }

        if (booking.getStatus() == BookingStatus.CANCELLED) {
            throw new BadRequestException("Đơn đặt lịch này đã được hủy trước đó");
        }

        if (booking.getStatus() == BookingStatus.COMPLETED) {
            throw new BadRequestException("Không thể hủy ca tập đã hoàn thành");
        }

        String reason = (request != null && request.getReason() != null && !request.getReason().isBlank())
                ? request.getReason().trim()
                : "Huấn luyện viên hủy lịch ca tập";

        String evidenceUrl = (request != null) ? request.getEvidenceUrl() : null;

        CancellationPolicy policy = cancellationPolicyFactory.getPolicy(Role.PT);
        CancellationCalculationResult result = policy.calculate(booking, LocalDateTime.now(), reason, evidenceUrl);

        return executeCancellation(booking, ptProfile.getPt(), "PT", reason, evidenceUrl, result);
    }

    /**
     * Phương thức điều phối cốt lõi dùng chung cho toàn bộ luồng hủy lịch.
     * Thực thi State Transition, thu hồi Slot, hoàn buổi tập, giao dịch ví tiền và ghi nhận Cancellation.
     */
    private BookingResponse executeCancellation(
            Booking booking,
            User cancelledBy,
            String cancelledByRole,
            String reason,
            String evidenceUrl,
            CancellationCalculationResult result
    ) {
        // 1. Chuyển trạng thái booking sang CANCELLED (State Pattern / Entity tự bảo vệ)
        booking.cancel();

        // 2. Trả slot về AVAILABLE
        AvailabilitySlot slot = booking.getSlot();
        if (slot != null) {
            slot.release();
            slotRepository.save(slot);
        }

        // 3. Khôi phục buổi tập nếu chính sách cho phép (đối với gói PACKAGE)
        if (result.isRestoreSession() && booking.getBookingType() == BookingType.PACKAGE && booking.getEnrollment() != null) {
            Enrollment enrollment = booking.getEnrollment();
            enrollment.restoreSession();
            enrollmentRepository.save(enrollment);
        }

        // 4. Xử lý ví tiền (đền bù / phạt)
        handleWalletTransactions(booking, cancelledByRole, result);

        // 5. Ghi nhật ký hủy lịch vào bảng cancellations
        Cancellation cancellation = Cancellation.builder()
                .booking(booking)
                .cancelledBy(cancelledBy)
                .cancelledByRole(cancelledByRole)
                .reason(reason)
                .hoursBeforeSession(result.getHoursBeforeSession())
                .refundAmount(result.getRefundAmount())
                .compensationAmount(result.getCompensationAmount())
                .penaltyAmount(result.getPenaltyAmount())
                .evidenceUrl(evidenceUrl)
                .status(CancellationStatus.PROCESSED)
                .build();

        cancellation = cancellationRepository.save(cancellation);
        booking = bookingRepository.save(booking);

        log.info("{} {} đã hủy booking ID {}: refund={}, comp={}, penalty={}",
                cancelledByRole, cancelledBy != null ? cancelledBy.getEmail() : "N/A",
                booking.getId(), result.getRefundAmount(), result.getCompensationAmount(), result.getPenaltyAmount());
        return BookingResponse.fromEntity(booking, cancellation);
    }

    /**
     * Xử lý giao dịch bồi hoàn hoặc xử phạt trên ví tài chính.
     */
    private void handleWalletTransactions(
            Booking booking,
            String cancelledByRole,
            CancellationCalculationResult result
    ) {
        if ("STUDENT".equalsIgnoreCase(cancelledByRole)) {
            // Học viên hủy: Nếu hủy sát giờ (< 24h), đền bù cho PT
            if (result.getCompensationAmount().compareTo(BigDecimal.ZERO) > 0
                    && booking.getPt() != null && booking.getPt().getPt() != null) {
                walletService.processBookingCompensation(
                        booking.getPt().getPt().getId(),
                        booking.getEnrollment(),
                        result.getCompensationAmount()
                );
            }
        } else if ("PT".equalsIgnoreCase(cancelledByRole)) {
            // Huấn luyện viên hủy:
            // Đền bù cho Student nếu PT hủy sát giờ (< 24h)
            if (result.getCompensationAmount().compareTo(BigDecimal.ZERO) > 0 && booking.getStudent() != null) {
                walletService.processBookingCompensation(
                        booking.getStudent().getId(),
                        booking.getEnrollment(),
                        result.getCompensationAmount()
                );
            }

            // Phạt PT nếu PT hủy sát giờ (< 24h)
            if (result.getPenaltyAmount().compareTo(BigDecimal.ZERO) > 0
                    && booking.getPt() != null && booking.getPt().getPt() != null) {
                walletService.processBookingPenalty(
                        booking.getPt().getPt().getId(),
                        booking.getEnrollment(),
                        result.getPenaltyAmount()
                );
            }
        }
    }

    @Override
    @Transactional(readOnly = true)
    public CancelPreviewResponse previewCancelBooking(String userEmail, Long bookingId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        Role role = Role.STUDENT;
        if (booking.getPt() != null && booking.getPt().getPt() != null && booking.getPt().getPt().getId().equals(user.getId())) {
            role = Role.PT;
        } else if (user.getRole() == Role.ADMIN) {
            role = Role.ADMIN;
        }

        CancellationPolicy policy = cancellationPolicyFactory.getPolicy(role);
        CancellationCalculationResult result = policy.calculate(booking, LocalDateTime.now(), "Xem trước", null);

        return CancelPreviewResponse.builder()
                .bookingId(bookingId)
                .cancelledByRole(role.name())
                .hoursBeforeSession(result.getHoursBeforeSession())
                .restoreSession(result.isRestoreSession())
                .refundAmount(result.getRefundAmount())
                .compensationAmount(result.getCompensationAmount())
                .penaltyAmount(result.getPenaltyAmount())
                .explanation(result.getExplanation())
                .build();
    }

    private BookingResponse mapBookingToResponse(Booking booking) {
        Cancellation cancellation = null;
        if (booking.getStatus() == BookingStatus.CANCELLED) {
            cancellation = cancellationRepository.findByBookingId(booking.getId()).orElse(null);
        }
        return BookingResponse.fromEntity(booking, cancellation);
    }
}
