package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.StudentCheckInRequest;
import com.PTconnect.backend.dto.response.AttendanceResponse;
import com.PTconnect.backend.dto.response.StartAttendanceResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.*;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.IAttendanceService;
import com.PTconnect.backend.util.OtpUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.math.BigDecimal;
import com.PTconnect.backend.service.IWalletService;
import java.util.List;

/**
 * Triển khai nghiệp vụ Điểm danh hai phía bằng mã OTP (Milestone 7).
 * Phụ trách bởi: Huy & Thắng.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AttendanceServiceImpl implements IAttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final BookingRepository bookingRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;
    private final OtpUtil otpUtil;
    private final IWalletService walletService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public StartAttendanceResponse startAttendance(String callerEmail, Long bookingId) {
        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        boolean isPt = booking.getPt() != null && booking.getPt().getPt() != null
                && callerEmail.equalsIgnoreCase(booking.getPt().getPt().getEmail());
        boolean isStudent = booking.getStudent() != null
                && callerEmail.equalsIgnoreCase(booking.getStudent().getEmail());

        if (!isPt && !isStudent) {
            throw new BadRequestException("Bạn không có quyền thao tác trên ca tập này");
        }

        if (booking.getStatus() != BookingStatus.CONFIRMED) {
            throw new BadRequestException("Chỉ có thể điểm danh cho ca tập đã được xác nhận (CONFIRMED)");
        }

        LocalDateTime now = LocalDateTime.now();
        AvailabilitySlot slot = booking.getSlot();

        log.info("User {} mở điểm danh ca #{}: Thời gian hệ thống = {}, Ca tập = {} -> {}",
                callerEmail, bookingId, now,
                slot != null ? slot.getStartTime() : "N/A",
                slot != null ? slot.getEndTime() : "N/A");

        // Kiểm tra khung giờ: cho phép mở trước tối đa 15 phút
        if (slot != null && slot.getStartTime() != null) {
            if (now.isBefore(slot.getStartTime().minusMinutes(15))) {
                java.time.format.DateTimeFormatter formatter = java.time.format.DateTimeFormatter.ofPattern("HH:mm ngày dd/MM/yyyy");
                throw new BadRequestException("Chưa đến thời gian bắt đầu ca tập (Hiện tại: "
                        + now.format(formatter) + " - Ca tập bắt đầu lúc: "
                        + slot.getStartTime().format(formatter) + "). Chỉ được mở điểm danh trước tối đa 15 phút.");
            }
        }

        // Xác định trạng thái đến muộn hay đúng giờ (muộn quá 15 phút so với giờ bắt đầu)
        boolean isLate = false;
        if (slot != null && slot.getStartTime() != null) {
            if (now.isAfter(slot.getStartTime().plusMinutes(15))) {
                isLate = true;
            }
        }

        AttendanceStatus status = isLate ? AttendanceStatus.LATE : AttendanceStatus.PRESENT;

        // Sinh mã OTP 6 số
        String otpCode = otpUtil.generateOtp(bookingId, 30);
        OtpUtil.OtpEntry otpEntry = otpUtil.getActiveOtp(bookingId);
        LocalDateTime expiresAt = otpEntry != null ? otpEntry.expiresAt() : now.plusMinutes(30);

        Attendance attendance = attendanceRepository.findByBookingId(bookingId)
                .orElse(Attendance.builder()
                        .booking(booking)
                        .verificationMethod(VerificationMethod.OTP)
                        .studentConfirmed(false)
                        .ptConfirmed(false)
                        .build());

        attendance.setCheckInTime(now);
        attendance.setStatus(status);
        attendance = attendanceRepository.save(attendance);

        log.info("User {} đã mở phiên điểm danh ca tập #{}, OTP: {}, Status: {}", callerEmail, bookingId, otpCode, status);

        return StartAttendanceResponse.builder()
                .attendanceId(attendance.getId())
                .bookingId(bookingId)
                .otpCode(otpCode)
                .checkInTime(now)
                .expiresAt(expiresAt)
                .status(status)
                .message("Đã mở phiên điểm danh thành công! Vui lòng cung cấp mã OTP 6 số này cho đối tác ca tập.")
                .build();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AttendanceResponse studentCheckIn(String callerEmail, Long bookingId, StudentCheckInRequest request) {
        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        boolean isPt = booking.getPt() != null && booking.getPt().getPt() != null
                && callerEmail.equalsIgnoreCase(booking.getPt().getPt().getEmail());
        boolean isStudent = booking.getStudent() != null
                && callerEmail.equalsIgnoreCase(booking.getStudent().getEmail());

        if (!isPt && !isStudent) {
            throw new BadRequestException("Bạn không có quyền thao tác trên ca tập này");
        }

        if (booking.getStatus() != BookingStatus.CONFIRMED) {
            throw new BadRequestException("Ca tập không ở trạng thái CONFIRMED để có thể điểm danh");
        }

        Attendance attendance = attendanceRepository.findByBookingId(bookingId)
                .orElseGet(() -> {
                    Attendance newAtt = Attendance.builder()
                            .booking(booking)
                            .verificationMethod(VerificationMethod.OTP)
                            .studentConfirmed(false)
                            .ptConfirmed(false)
                            .checkInTime(LocalDateTime.now())
                            .status(AttendanceStatus.PRESENT)
                            .build();
                    return attendanceRepository.save(newAtt);
                });

        // Kiểm tra mã OTP
        if (!otpUtil.validateOtp(bookingId, request.getOtpCode())) {
            throw new BadRequestException("Mã OTP không chính xác hoặc đã hết thời gian hiệu lực. Vui lòng kiểm tra lại!");
        }

        attendance.setStudentConfirmed(true);
        attendance.setPtConfirmed(true);
        completeSession(booking, attendance);

        attendance = attendanceRepository.save(attendance);
        log.info("Người dùng {} đã xác nhận điểm danh ca #{}, Fully confirmed: {}", callerEmail, bookingId, attendance.isFullyConfirmed());

        return AttendanceResponse.fromEntity(attendance);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AttendanceResponse ptConfirmAttendance(String ptEmail, Long bookingId) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền thao tác trên ca tập của Huấn luyện viên khác");
        }

        if (booking.getStatus() != BookingStatus.CONFIRMED) {
            throw new BadRequestException("Ca tập không ở trạng thái CONFIRMED để xác nhận hoàn tất");
        }

        Attendance attendance = attendanceRepository.findByBookingId(bookingId)
                .orElseThrow(() -> new BadRequestException("Chưa có phiên điểm danh cho ca tập này. Vui lòng bấm 'Bắt đầu điểm danh' trước."));

        attendance.setPtConfirmed(true);

        // Nếu học viên cũng đã nhập OTP thành công -> Hoàn tất ca tập sang COMPLETED
        if (Boolean.TRUE.equals(attendance.getStudentConfirmed())) {
            completeSession(booking, attendance);
        }

        attendance = attendanceRepository.save(attendance);
        log.info("Huấn luyện viên {} đã xác nhận điểm danh ca #{}, Fully confirmed: {}", ptEmail, bookingId, attendance.isFullyConfirmed());

        return AttendanceResponse.fromEntity(attendance);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AttendanceResponse markAbsent(String ptEmail, Long bookingId, String reason) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ Huấn luyện viên cho email: " + ptEmail));

        Booking booking = bookingRepository.findByIdWithLock(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        if (!booking.getPt().getId().equals(ptProfile.getId())) {
            throw new BadRequestException("Bạn không có quyền thao tác trên ca tập của Huấn luyện viên khác");
        }

        if (booking.getStatus() != BookingStatus.CONFIRMED) {
            throw new BadRequestException("Chỉ có thể đánh dấu vắng mặt cho ca tập đang ở trạng thái CONFIRMED");
        }

        LocalDateTime now = LocalDateTime.now();
        Attendance attendance = attendanceRepository.findByBookingId(bookingId)
                .orElse(Attendance.builder()
                        .booking(booking)
                        .verificationMethod(VerificationMethod.OTP)
                        .build());

        attendance.setCheckInTime(attendance.getCheckInTime() != null ? attendance.getCheckInTime() : now);
        attendance.setCheckOutTime(now);
        attendance.setStudentConfirmed(false);
        attendance.setPtConfirmed(true);
        attendance.setStatus(AttendanceStatus.ABSENT);
        attendance = attendanceRepository.save(attendance);

        // Theo đặc tả mục 3.10: Học viên vắng mặt thì buổi tập vẫn bị tính -> Chuyển sang COMPLETED
        completeSession(booking, attendance);

        log.info("PT {} đã đánh dấu học viên vắng mặt (ABSENT) cho ca #{}, lý do: {}", ptEmail, bookingId, reason);
        return AttendanceResponse.fromEntity(attendance);
    }

    @Override
    @Transactional(readOnly = true)
    public AttendanceResponse getAttendanceByBookingId(String userEmail, Long bookingId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy đơn đặt lịch với ID: " + bookingId));

        // Kiểm tra quyền xem
        boolean isStudent = booking.getStudent().getId().equals(user.getId());
        boolean isPT = booking.getPt() != null && booking.getPt().getPt() != null && booking.getPt().getPt().getId().equals(user.getId());
        boolean isAdmin = user.getRole() == Role.ADMIN;

        if (!isStudent && !isPT && !isAdmin) {
            throw new UnauthorizedException("Bạn không có quyền xem thông tin điểm danh của ca tập này");
        }

        Attendance attendance = attendanceRepository.findByBookingId(bookingId).orElse(null);
        return AttendanceResponse.fromEntity(attendance);
    }

    private void completeSession(Booking booking, Attendance attendance) {
        attendance.setCheckOutTime(LocalDateTime.now());
        booking.complete();
        bookingRepository.save(booking);

        // Dọn dẹp mã OTP sau khi hoàn tất
        otpUtil.clearOtp(booking.getId());

        // Trả thù lao ca tập vào ví của PT (nếu là gói có phí)
        if (booking.getBookingType() == BookingType.PACKAGE
                && booking.getSessionFee() != null
                && booking.getSessionFee().compareTo(BigDecimal.ZERO) > 0
                && booking.getPt() != null
                && booking.getPt().getPt() != null) {
            try {
                Long ptUserId = booking.getPt().getPt().getId();
                walletService.processSessionPayout(ptUserId, booking.getEnrollment(), booking.getSessionFee());
                log.info("Đã tự động cộng thù lao {} VNĐ vào ví cho PT user ID {}", booking.getSessionFee(), ptUserId);
            } catch (Exception e) {
                log.error("Lỗi khi cộng thù lao ca tập cho PT: {}", e.getMessage());
            }
        }

        // Kiểm tra hợp đồng khóa học: nếu đã hết buổi và không còn booking nào đang PENDING/CONFIRMED -> COMPLETED
        if (booking.getBookingType() == BookingType.PACKAGE && booking.getEnrollment() != null) {
            Enrollment enrollment = booking.getEnrollment();
            if (enrollment.getRemainingSessions() != null && enrollment.getRemainingSessions() == 0) {
                boolean hasActiveBookings = bookingRepository.existsByEnrollmentIdAndStatusIn(
                        enrollment.getId(),
                        List.of(BookingStatus.PENDING, BookingStatus.CONFIRMED)
                );
                if (!hasActiveBookings) {
                    enrollment.complete();
                    enrollmentRepository.save(enrollment);
                    log.info("Hợp đồng #{} đã hoàn tất toàn bộ số buổi tập -> Chuyển trạng thái sang COMPLETED", enrollment.getId());
                }
            }
        }
    }
}
