package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.ArbitrationVerdictRequest;
import com.PTconnect.backend.dto.request.CreateDisputeRequest;
import com.PTconnect.backend.dto.response.DisputeResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.DisputeRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IDisputeService;
import com.PTconnect.backend.service.IWalletService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DisputeServiceImpl implements IDisputeService {

    private final DisputeRepository disputeRepository;
    private final BookingRepository bookingRepository;
    private final UserRepository userRepository;
    private final IWalletService walletService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public DisputeResponse createDispute(String callerEmail, CreateDisputeRequest request) {
        User caller = userRepository.findByEmail(callerEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy thông tin tài khoản: " + callerEmail));

        Booking booking = bookingRepository.findById(request.getBookingId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy ca tập #" + request.getBookingId()));

        User student = booking.getStudent();
        User ptUser = (booking.getPt() != null && booking.getPt().getPt() != null)
                ? booking.getPt().getPt()
                : (booking.getSlot() != null && booking.getSlot().getPt() != null && booking.getSlot().getPt().getPt() != null)
                ? booking.getSlot().getPt().getPt()
                : null;

        boolean isStudent = student != null && caller.getId().equals(student.getId());
        boolean isPt = ptUser != null && caller.getId().equals(ptUser.getId());

        if (!isStudent && !isPt && caller.getRole() != Role.ADMIN) {
            throw new BadRequestException("Bạn không phải là thành viên liên quan tới ca tập #" + booking.getId());
        }

        Role complainantRole = isStudent ? Role.STUDENT : Role.PT;
        User defendant = isStudent ? ptUser : student;

        // Ước tính học phí ca tập
        BigDecimal sessionFee = BigDecimal.valueOf(350000);
        if (booking.getSessionFee() != null) {
            sessionFee = booking.getSessionFee();
        }

        String label = request.getDisputeTypeLabel();
        if (label == null || label.isBlank()) {
            label = switch (request.getDisputeType()) {
                case "PT_ABSENT" -> "HLV Vắng Mặt Không Báo Trước";
                case "LATE_CANCEL_STUDENT" -> "Hủy Lịch Sát Giờ & Khiếu Nại Bất Khả Kháng";
                case "OTP_PREMATURE" -> "Tranh Chấp Điểm Danh OTP";
                case "QUALITY_ISSUE" -> "Chất Lượng Ca Tập Không Đúng Cam Kết";
                default -> "Khiếu Nại & Tranh Chấp Ca Tập";
            };
        }

        String summary = String.format("[%s] %s khiếu nại đối tác ca tập #%d: %s",
                complainantRole.name(), caller.getFullName(), booking.getId(), label);

        DisputeCase dispute = DisputeCase.builder()
                .booking(booking)
                .complainant(caller)
                .complainantRole(complainantRole)
                .defendant(defendant)
                .disputeType(request.getDisputeType())
                .disputeTypeLabel(label)
                .severity(request.getSeverity() != null ? request.getSeverity() : "MEDIUM")
                .summary(summary)
                .statement(request.getStatement())
                .evidenceNote(request.getEvidenceNote())
                .sessionFee(sessionFee)
                .status("PENDING_ARBITRATION")
                .createdAt(LocalDateTime.now())
                .build();

        dispute = disputeRepository.save(dispute);
        log.info("Đã tạo hồ sơ tranh chấp #{} cho ca tập #{} bởi user {}", dispute.getId(), booking.getId(), callerEmail);

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

        String vType = request.getVerdictType();
        String customNote = request.getCustomNote() != null ? request.getCustomNote().trim() : "";
        String resolutionDesc;
        String statusVal;

        BigDecimal fee = dispute.getSessionFee() != null ? dispute.getSessionFee() : BigDecimal.valueOf(350000);
        User student = dispute.getBooking() != null ? dispute.getBooking().getStudent() : null;
        User ptUser = (dispute.getBooking() != null && dispute.getBooking().getPt() != null)
                ? dispute.getBooking().getPt().getPt()
                : null;

        if ("REFUND_STUDENT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_REFUND_STUDENT";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Xử thắng cho Học viên: Hoàn trả 100% học phí buổi tập vào ví và bảo lưu quyền lợi. Khiển trách HLV vi phạm.";
            if (student != null) {
                walletService.processBookingCompensation(student.getId(), null, fee);
                log.info("Trọng tài hoàn trả {} cho học viên {} sau phán quyết vụ việc #{}", fee, student.getEmail(), disputeId);
            }
        } else if ("PAID_PT".equalsIgnoreCase(vType)) {
            statusVal = "RESOLVED_PAID_PT";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Xử thắng cho HLV: Ghi nhận ca tập hợp lệ và giải ngân thù lao cho HLV. Khấu trừ buổi tập của học viên theo điều khoản hủy muộn.";
            if (ptUser != null) {
                walletService.processSessionPayout(ptUser.getId(), null, fee);
                log.info("Trọng tài giải ngân thù lao {} cho PT {} sau phán quyết vụ việc #{}", fee, ptUser.getEmail(), disputeId);
            }
        } else {
            statusVal = "RESOLVED_FORCE_MAJEURE";
            resolutionDesc = !customNote.isEmpty() ? customNote :
                    "Hòa giải Bất Khả Kháng (Admin Policy): Khôi phục buổi tập cho học viên do sự cố bất khả kháng xác minh hợp lệ. Không áp dụng phạt đôi bên.";
        }

        dispute.setStatus(statusVal);
        dispute.setVerdictType(vType);
        dispute.setResolutionDecision(resolutionDesc);
        dispute.setResolvedAt(LocalDateTime.now());

        dispute = disputeRepository.save(dispute);
        log.info("Admin {} đã ban hành phán quyết [{}] cho vụ việc #{}", adminEmail, vType, disputeId);

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
