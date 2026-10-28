package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.service.IPTProfileService;
import com.PTconnect.backend.service.IPTSlotService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Service chuyên biệt quản lý Khung giờ rảnh của Huấn luyện viên (Availability Slots).
 * Đảm bảo nguyên lý Đơn nhiệm (SRP) - Chỉ tiêm các repository liên quan tới Slot và Booking.
 */
@Service
@RequiredArgsConstructor
public class PTSlotServiceImpl implements IPTSlotService {

    private final IPTProfileService ptProfileService;
    private final AvailabilitySlotRepository availabilitySlotRepository;
    private final BookingRepository bookingRepository;

    @Override
    @Transactional
    public SlotResponse createSlot(String userEmail, CreateSlotRequest request) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);

        if (request.getStartTime() == null || request.getEndTime() == null) {
            throw new IllegalArgumentException("Thời gian bắt đầu và kết thúc không được để trống");
        }

        LocalDateTime now = LocalDateTime.now();
        if (request.getStartTime().isBefore(now)) {
            throw new IllegalArgumentException("Thời gian bắt đầu slot không được ở trong quá khứ");
        }

        if (!request.getEndTime().isAfter(request.getStartTime())) {
            throw new IllegalArgumentException("Thời gian kết thúc slot phải sau thời gian bắt đầu");
        }

        List<AvailabilitySlot> overlapping = availabilitySlotRepository.findOverlapping(
                profile.getId(), request.getStartTime(), request.getEndTime(), null);
        if (!overlapping.isEmpty()) {
            throw new IllegalArgumentException("Khung giờ bị trùng hoặc chồng lấn với lịch rảnh khác của bạn");
        }

        AvailabilitySlot slot = AvailabilitySlot.builder()
                .pt(profile)
                .startTime(request.getStartTime())
                .endTime(request.getEndTime())
                .status(SlotStatus.AVAILABLE)
                .build();

        AvailabilitySlot saved = availabilitySlotRepository.save(slot);
        return SlotResponse.fromEntity(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public List<SlotResponse> getSlots(String userEmail) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);
        List<AvailabilitySlot> slots = availabilitySlotRepository.findByPtIdOrderByStartTimeAsc(profile.getId());
        return slots.stream()
                .map(SlotResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional
    public void deleteSlot(String userEmail, Long slotId) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);

        AvailabilitySlot slot = availabilitySlotRepository.findById(slotId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khung giờ (slot) với ID: " + slotId));

        if (!slot.getPt().getId().equals(profile.getId())) {
            throw new UnauthorizedException("Bạn không có quyền xóa khung giờ của Huấn luyện viên khác");
        }

        if (bookingRepository.findBySlotId(slotId).isPresent()) {
            throw new IllegalArgumentException("Không thể xóa khung giờ đã có học viên đặt lịch");
        }

        if (slot.getStatus() != SlotStatus.AVAILABLE) {
            throw new IllegalArgumentException("Chỉ có thể xóa khung giờ đang ở trạng thái AVAILABLE");
        }

        availabilitySlotRepository.delete(slot);
    }
}
