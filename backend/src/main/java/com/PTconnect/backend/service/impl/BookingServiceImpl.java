package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.enums.EnrollmentStatus;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.service.IBookingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * Bản nháp triển khai BookingService chuẩn bị cho Milestone 6.
 * Phụ trách bởi: Huy.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class BookingServiceImpl implements IBookingService {

    private final AvailabilitySlotRepository slotRepository;
    private final BookingRepository bookingRepository;
    private final EnrollmentRepository enrollmentRepository;

    @Override
    public boolean canBookSlot(Long slotId, Long studentId) {
        try {
            validateBookingRequest(slotId, studentId, null);
            return true;
        } catch (Exception e) {
            log.debug("Slot {} không khả dụng cho student {}: {}", slotId, studentId, e.getMessage());
            return false;
        }
    }

    @Override
    public void validateBookingRequest(Long slotId, Long studentId, Long enrollmentId) {
        AvailabilitySlot slot = slotRepository.findById(slotId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khung giờ với ID: " + slotId));

        if (slot.getStatus() != SlotStatus.AVAILABLE) {
            throw new BadRequestException("Khung giờ này đã được đặt hoặc không còn khả dụng");
        }

        if (slot.getStartTime().isBefore(LocalDateTime.now())) {
            throw new BadRequestException("Không thể đặt khung giờ đã trôi qua trong quá khứ");
        }

        if (enrollmentId != null) {
            Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
                    .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng với ID: " + enrollmentId));

            if (!enrollment.getStudent().getId().equals(studentId)) {
                throw new BadRequestException("Hợp đồng này không thuộc về bạn");
            }

            if (enrollment.getStatus() != EnrollmentStatus.ACTIVE) {
                throw new BadRequestException("Hợp đồng này hiện không ở trạng thái hoạt động");
            }

            if (enrollment.getRemainingSessions() <= 0) {
                throw new BadRequestException("Hợp đồng đã sử dụng hết số buổi tập");
            }

            if (LocalDate.now().isAfter(enrollment.getEndDate())) {
                throw new BadRequestException("Hợp đồng khóa học đã hết hạn sử dụng");
            }

            if (!slot.getPt().getId().equals(enrollment.getPt().getId())) {
                throw new BadRequestException("Khung giờ không thuộc về Huấn luyện viên của hợp đồng này");
            }
        }
    }
}
