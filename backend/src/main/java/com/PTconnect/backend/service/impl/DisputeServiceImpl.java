package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.ArbitrationVerdictRequest;
import com.PTconnect.backend.dto.request.CreateDisputeRequest;
import com.PTconnect.backend.dto.response.DisputeResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.DisputeRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IDisputeService;
import com.PTconnect.backend.service.IWalletService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DisputeServiceImpl implements IDisputeService {

    private final DisputeRepository disputeRepository;
    private final BookingRepository bookingRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final IWalletService walletService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse createDispute(String callerEmail, CreateDisputeRequest request) {
        User caller = userRepository.findByEmail(callerEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy thông tin tài khoản: " + callerEmail));

        Enrollment enrollment = null;
        Booking booking = null;

        if (request.getEnrollmentId() != null) {
            enrollment = enrollmentRepository.findById(request.getEnrollmentId())
                    .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng #" + request.getEnrollmentId()));
        }

        if (request.getBookingId() != null) {
            booking = bookingRepository.findById(request.getBookingId()).orElse(null);
            if (booking != null && enrollment == null) {
                enrollment = booking.getEnrollment();
            }
        }

        if (booking == null && enrollment == null) {
            throw new BadRequestException("Vui lòng cung cấp mã ca tập hoặc mã hợp đồng cần khiếu nại.");
        }

        boolean isContractDispute = (enrollment != null && "CONTRACT_TERMINATION".equalsIgnoreCase(request.getDisputeType()))
                || (request.getEnrollmentId() != null && request.getBookingId() == null);

        // Nếu khiếu nại hủy hợp đồng nhưng chưa truyền bookingId, gắn với booking đầu tiên của enrollment nếu có để đảm bảo toàn vẹn dữ liệu
        if (booking == null && enrollment != null) {
            List<Booking> list = bookingRepository.findByEnrollmentId(enrollment.getId());
            if (!list.isEmpty()) {
                booking = list.get(0);
            }
        }

        User student = (booking != null && booking.getStudent() != null) ? booking.getStudent() : enrollment.getStudent();
        User ptUser = null;
        if (booking != null && booking.getPt() != null && booking.getPt().getPt() != null) {
            ptUser = booking.getPt().getPt();
        } else if (enrollment != null && enrollment.getPt() != null && enrollment.getPt().getPt() != null) {
            ptUser = enrollment.getPt().getPt();
        }

        boolean isStudent = student != null && caller.getId().equals(student.getId());
        boolean isPt = ptUser != null && caller.getId().equals(ptUser.getId());

        if (!isStudent && !isPt && caller.getRole() != Role.ADMIN) {
            throw new BadRequestException("Bạn không phải thành viên liên quan tới ca tập hoặc hợp đồng này.");
        }

        Role complainantRole = isStudent ? Role.STUDENT : Role.PT;
        User defendant = isStudent ? ptUser : student;

        BigDecimal fee = BigDecimal.valueOf(350000);
        if (isContractDispute && enrollment != null) {
            int total = (enrollment.getTotalSessions() != null && enrollment.getTotalSessions() > 0) ? enrollment.getTotalSessions() : 1;
            int remain = enrollment.getRemainingSessions() != null ? enrollment.getRemainingSessions() : total;
            if (enrollment.getFinalPrice() != null) {
                fee = enrollment.getFinalPrice().multiply(BigDecimal.valueOf(remain))
                        .divide(BigDecimal.valueOf(total), 0, RoundingMode.HALF_UP);
            }
        } else if (booking != null && booking.getSessionFee() != null) {
            fee = booking.getSessionFee();
        } else if (enrollment != null && enrollment.getFinalPrice() != null) {
            fee = enrollment.getFinalPrice();
        }

        String label = request.getDisputeTypeLabel();
        if (label == null || label.isBlank()) {
            label = switch (request.getDisputeType()) {
                case "CONTRACT_TERMINATION" -> "Khiếu Nại & Yêu Cầu Hủy Hợp Đồng Khóa Học";
                case "PT_ABSENT" -> "HLV Vắng Mặt Không Báo Trước";
                case "LATE_CANCEL_STUDENT" -> "Hủy Lịch Sát Giờ & Khiếu Nại Bất Khả Kháng";
                case "OTP_PREMATURE" -> "Tranh Chấp Điểm Danh OTP";
                case "QUALITY_ISSUE" -> "Chất Lượng Ca Tập Không Đúng Cam Kết";
                default -> "Khiếu Nại & Tranh Chấp Nền Tảng";
            };
        }

        String targetInfo = (enrollment != null && "CONTRACT_TERMINATION".equals(request.getDisputeType()))
                ? String.format("hợp đồng #%d", enrollment.getId())
                : String.format("ca tập #%d", booking != null ? booking.getId() : 0);

        String summary = String.format("[%s] %s khiếu nại đối tác %s: %s",
                complainantRole.name(), caller.getFullName(), targetInfo, label);

        DisputeCase dispute = DisputeCase.builder()
                .booking(booking)
                .enrollment(enrollment)
                .complainant(caller)
                .complainantRole(complainantRole)
                .defendant(defendant)
                .disputeType(request.getDisputeType())
                .disputeTypeLabel(label)
                .severity(request.getSeverity() != null ? request.getSeverity() : "MEDIUM")
                .summary(summary)
                .statement(request.getStatement())
                .evidenceNote(request.getEvidenceNote())
                .sessionFee(fee)
                .status("PENDING_ARBITRATION")
                .createdAt(LocalDateTime.now())
                .build();

        dispute = disputeRepository.save(dispute);
        log.info("Đã tạo hồ sơ tranh chấp #{} cho {} bởi user {}", dispute.getId(), targetInfo, callerEmail);

        return DisputeResponse.fromEntity(dispute);
    }

    @Override
    @Transactional(readOnly = true)
    public List<DisputeResponse> getAllDisputes() {
        return disputeRepository.findAllWithDetails().stream()
                .map(DisputeResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<DisputeResponse> getMyDisputes(String callerEmail) {
        User caller = userRepository.findByEmail(callerEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy tài khoản: " + callerEmail));

        return disputeRepository.findByUserInvolved(caller.getId()).stream()
                .map(DisputeResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse issueVerdict(String adminEmail, Long disputeId, ArbitrationVerdictRequest request) {
        DisputeCase dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ tranh chấp #" + disputeId));

        // Kiểm tra điều kiện thời hạn 48 giờ chống phán quyết độc đoán
        LocalDateTime createdAt = dispute.getCreatedAt() != null ? dispute.getCreatedAt() : LocalDateTime.now().minusHours(49);
        LocalDateTime deadline = createdAt.plusHours(48);
        boolean hasCounterStatement = dispute.getCounterStatement() != null && !dispute.getCounterStatement().trim().isEmpty();
        boolean isAfter48Hours = LocalDateTime.now().isAfter(deadline);

        if (!hasCounterStatement && !isAfter48Hours && !Boolean.TRUE.equals(request.getBypass48hWaiting())) {
            long hoursLeft = java.time.Duration.between(LocalDateTime.now(), deadline).toHours();
            long minutesLeft = Math.max(0, java.time.Duration.between(LocalDateTime.now(), deadline).toMinutesPart());
            throw new BadRequestException(String.format(
                    "Quy chế trọng tài chống phán quyết độc đoán: Bên bị khiếu nại có 48 giờ để gửi bản phản biện đối chứng. Hiện còn %d giờ %d phút và chưa nhận được phản biện. Admin chỉ được phán quyết sau khi nhận phản biện hoặc sau khi hết thời hạn 48 giờ.",
                    Math.max(0, hoursLeft), minutesLeft
            ));
        }

        String vType = request.getVerdictType();
        String customNote = request.getCustomNote() != null ? request.getCustomNote().trim() : "";
        if (customNote.isEmpty() && request.getVerdictReason() != null) {
            customNote = request.getVerdictReason().trim();
        }

        String resolutionDesc;
        String statusVal;

        Booking booking = dispute.getBooking();
        BigDecimal fee = dispute.getSessionFee() != null ? dispute.getSessionFee() : BigDecimal.valueOf(350000);
        User student = booking != null ? booking.getStudent() : null;
        if (student == null && dispute.getEnrollment() != null) {
            student = dispute.getEnrollment().getStudent();
        }

        User ptUser = null;
        if (booking != null && booking.getPt() != null) {
            ptUser = booking.getPt().getPt();
        } else if (dispute.getEnrollment() != null && dispute.getEnrollment().getPt() != null) {
            ptUser = dispute.getEnrollment().getPt().getPt();
        }

        Enrollment enr = dispute.getEnrollment() != null ? dispute.getEnrollment()
                : (booking != null ? booking.getEnrollment() : null);

        if ("CANCEL_CONTRACT_REFUND_STUDENT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_CONTRACT_TERMINATION";
            BigDecimal refundAmt = fee;
            if (enr != null) {
                enr.setStatus(EnrollmentStatus.CANCELLED);
                enrollmentRepository.save(enr);
                int total = (enr.getTotalSessions() != null && enr.getTotalSessions() > 0) ? enr.getTotalSessions() : 1;
                int remain = enr.getRemainingSessions() != null ? enr.getRemainingSessions() : 0;
                refundAmt = enr.getFinalPrice().multiply(BigDecimal.valueOf(remain))
                        .divide(BigDecimal.valueOf(total), 2, RoundingMode.HALF_UP);

                // Hủy các ca tập chưa diễn ra thuộc hợp đồng đã thanh lý để giải phóng lịch cho cả 2 bên
                List<Booking> contractBookings = bookingRepository.findByEnrollmentId(enr.getId());
                for (Booking b : contractBookings) {
                    if (b.getStatus() == BookingStatus.PENDING || b.getStatus() == BookingStatus.CONFIRMED) {
                        b.setStatus(BookingStatus.CANCELLED);
                        bookingRepository.save(b);
                    }
                }
            }
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    String.format("Phán quyết Trọng tài: Hủy toàn bộ hợp đồng khóa học. Hoàn trả %s ₫ vào ví học viên cho các buổi chưa tập.",
                            refundAmt.toBigInteger().toString());
            if (student != null) {
                walletService.processBookingCompensation(student.getId(), null, refundAmt);
                log.info("Trọng tài hủy hợp đồng và hoàn trả {} cho học viên {} sau phán quyết vụ việc #{}", refundAmt, student.getEmail(), disputeId);
            }
        } else if ("CANCEL_CONTRACT_PAID_PT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_CONTRACT_TERMINATION";
            BigDecimal ptPayout = fee;
            if (enr != null) {
                enr.setStatus(EnrollmentStatus.CANCELLED);
                enrollmentRepository.save(enr);

                int total = (enr.getTotalSessions() != null && enr.getTotalSessions() > 0) ? enr.getTotalSessions() : 1;
                int remain = enr.getRemainingSessions() != null ? enr.getRemainingSessions() : 0;
                ptPayout = enr.getFinalPrice().multiply(BigDecimal.valueOf(remain))
                        .divide(BigDecimal.valueOf(total), 0, RoundingMode.HALF_UP);

                List<Booking> contractBookings = bookingRepository.findByEnrollmentId(enr.getId());
                for (Booking b : contractBookings) {
                    if (b.getStatus() == BookingStatus.PENDING || b.getStatus() == BookingStatus.CONFIRMED) {
                        b.setStatus(BookingStatus.CANCELLED);
                        bookingRepository.save(b);
                    }
                }
            }
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    String.format("Phán quyết Trọng tài: Chấp thuận hủy hợp đồng do lỗi từ phía học viên. Quyết toán chi trả %s ₫ thù lao các buổi còn lại cho Huấn luyện viên.",
                            ptPayout.toBigInteger().toString());
            if (ptUser != null) {
                walletService.processSessionPayout(ptUser.getId(), null, ptPayout);
                log.info("Trọng tài giải ngân {} cho PT {} sau phán quyết hủy hợp đồng vụ việc #{}", ptPayout, ptUser.getEmail(), disputeId);
            }
        } else if ("REFUND_STUDENT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_REFUND_STUDENT";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Xử thắng cho Học viên: Hoàn trả 100% học phí buổi tập vào ví và khôi phục quyền lợi buổi tập. Khiển trách HLV vi phạm.";
            if (student != null) {
                walletService.processBookingCompensation(student.getId(), null, fee);
                log.info("Trọng tài hoàn trả {} cho học viên {} sau phán quyết vụ việc #{}", fee, student.getEmail(), disputeId);
            }
            if (booking != null) {
                booking.setStatus(BookingStatus.CANCELLED);
                bookingRepository.save(booking);
            }
            if (enr != null && enr.getStatus() == EnrollmentStatus.ACTIVE) {
                enr.restoreSession();
                enrollmentRepository.save(enr);
            }
        } else if ("PAID_PT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_PAID_PT";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Xử thắng cho HLV: Ghi nhận ca tập hợp lệ và giải ngân thù lao cho HLV. Khấu trừ buổi tập của học viên theo điều khoản hủy muộn.";
            if (ptUser != null) {
                walletService.processSessionPayout(ptUser.getId(), null, fee);
                log.info("Trọng tài giải ngân thù lao {} cho PT {} sau phán quyết vụ việc #{}", fee, ptUser.getEmail(), disputeId);
            }
            if (booking != null) {
                booking.setStatus(BookingStatus.COMPLETED);
                bookingRepository.save(booking);
            }
        } else {
            statusVal = "RESOLVED_FORCE_MAJEURE";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Hòa giải Bất Khả Kháng (Admin Policy): Khôi phục buổi tập cho học viên do sự cố bất khả kháng xác minh hợp lệ. Không áp dụng phạt đôi bên.";
            if (booking != null) {
                booking.setStatus(BookingStatus.CANCELLED);
                bookingRepository.save(booking);
            }
            if (enr != null && enr.getStatus() == EnrollmentStatus.ACTIVE) {
                enr.restoreSession();
                enrollmentRepository.save(enr);
            }
        }

        dispute.setStatus(statusVal);
        dispute.setVerdictType(vType);
        dispute.setResolutionDecision(resolutionDesc);
        dispute.setVerdictReason(resolutionDesc);
        dispute.setResolvedAt(LocalDateTime.now());
        dispute.setEvidenceRequested(false); // Đóng cờ yêu cầu bằng chứng khi đã có phán quyết

        dispute = disputeRepository.save(dispute);
        log.info("Admin {} đã ban hành phán quyết [{}] cho vụ việc #{}", adminEmail, vType, disputeId);

        return DisputeResponse.fromEntity(dispute);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse requestAdditionalEvidence(String adminEmail, Long disputeId, String target, String note) {
        DisputeCase dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ tranh chấp #" + disputeId));

        if (dispute.getStatus() != null && dispute.getStatus().startsWith("RESOLVED")) {
            throw new BadRequestException("Vụ việc đã có phán quyết trọng tài từ Ban Quản Trị, không thể yêu cầu thêm bằng chứng.");
        }

        dispute.setEvidenceRequested(true);
        String reqTarget = target != null ? target.toUpperCase() : "BOTH";
        dispute.setEvidenceRequestTarget(reqTarget);
        dispute.setEvidenceRequestNote(note != null && !note.isBlank() ? note.trim() : "Ban Quản Trị yêu cầu bổ sung bằng chứng xác minh vụ việc.");
        dispute.setStatus("AWAITING_ADDITIONAL_EVIDENCE");

        // Mỗi lần gửi yêu cầu bổ sung mới, reset trạng thái nộp về đang chờ (false) cho bên bị yêu cầu
        if ("STUDENT".equals(reqTarget)) {
            dispute.setStudentEvidenceSubmitted(false);
        } else if ("PT".equals(reqTarget)) {
            dispute.setPtEvidenceSubmitted(false);
        } else {
            dispute.setStudentEvidenceSubmitted(false);
            dispute.setPtEvidenceSubmitted(false);
        }

        dispute = disputeRepository.save(dispute);
        log.info("Admin {} đã gửi yêu cầu bổ sung bằng chứng tới [{}] cho vụ việc #{}: {}", adminEmail, target, disputeId, note);

        return DisputeResponse.fromEntity(dispute);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse submitAdditionalEvidence(String callerEmail, Long disputeId, String evidence) {
        DisputeCase dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ tranh chấp #" + disputeId));

        User caller = userRepository.findByEmail(callerEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy thông tin tài khoản: " + callerEmail));

        boolean isStudent = (dispute.getBooking() != null && dispute.getBooking().getStudent() != null && caller.getId().equals(dispute.getBooking().getStudent().getId()))
                || (dispute.getEnrollment() != null && dispute.getEnrollment().getStudent() != null && caller.getId().equals(dispute.getEnrollment().getStudent().getId()))
                || (dispute.getComplainantRole() == Role.STUDENT && caller.getId().equals(dispute.getComplainant().getId()))
                || (dispute.getDefendant() != null && dispute.getDefendant().getRole() == Role.STUDENT && caller.getId().equals(dispute.getDefendant().getId()));

        if (isStudent) {
            String current = dispute.getAdditionalEvidenceStudent() != null ? dispute.getAdditionalEvidenceStudent() + "\n" : "";
            dispute.setAdditionalEvidenceStudent(current + evidence.trim());
            dispute.setStudentEvidenceSubmitted(true);
        } else {
            String current = dispute.getAdditionalEvidencePt() != null ? dispute.getAdditionalEvidencePt() + "\n" : "";
            dispute.setAdditionalEvidencePt(current + evidence.trim());
            dispute.setPtEvidenceSubmitted(true);
        }

        dispute = disputeRepository.save(dispute);
        log.info("Người dùng {} đã nộp bằng chứng bổ sung cho vụ việc #{}", callerEmail, disputeId);

        return DisputeResponse.fromEntity(dispute);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse submitCounterStatement(String callerEmail, Long disputeId, String counterStatement) {
        DisputeCase dispute = disputeRepository.findById(disputeId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ tranh chấp #" + disputeId));

        User caller = userRepository.findByEmail(callerEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy thông tin tài khoản: " + callerEmail));

        boolean isDefendant = dispute.getDefendant() != null && caller.getId().equals(dispute.getDefendant().getId());
        boolean isComplainant = dispute.getComplainant() != null && caller.getId().equals(dispute.getComplainant().getId());

        // Hỗ trợ dự phòng trường hợp hồ sơ cũ chưa kịp lưu defendant vào CSDL
        if (!isDefendant && !isComplainant) {
            com.PTconnect.backend.entity.Booking b = dispute.getBooking();
            if (b != null) {
                if (b.getStudent() != null && caller.getId().equals(b.getStudent().getId())) {
                    isDefendant = true;
                } else if (b.getPt() != null && b.getPt().getPt() != null && caller.getId().equals(b.getPt().getPt().getId())) {
                    isDefendant = true;
                }
            }
        }

        if (!isDefendant && !isComplainant && caller.getRole() != Role.ADMIN) {
            throw new BadRequestException("Bạn không phải thành viên liên quan tới vụ tranh chấp này.");
        }

        if (dispute.getStatus() != null && dispute.getStatus().startsWith("RESOLVED")) {
            throw new BadRequestException("Vụ việc đã có phán quyết trọng tài từ Ban Quản Trị, không thể gửi thêm phản biện.");
        }

        dispute.setCounterStatement(counterStatement != null ? counterStatement.trim() : "");
        dispute = disputeRepository.save(dispute);
        log.info("Người dùng {} đã gửi phản biện đối chứng cho vụ tranh chấp #{}", callerEmail, disputeId);

        return DisputeResponse.fromEntity(dispute);
    }
}
