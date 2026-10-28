package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.service.impl.PTSlotServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Kiểm thử PTSlotService (Ưu tiên 3 SRP)")
class PTSlotServiceTest {

    @Mock
    private IPTProfileService ptProfileService;

    @Mock
    private AvailabilitySlotRepository availabilitySlotRepository;

    @Mock
    private BookingRepository bookingRepository;

    @InjectMocks
    private PTSlotServiceImpl ptSlotService;

    private PTProfile profile;

    @BeforeEach
    void setUp() {
        PT pt = PT.builder().id(1L).fullName("PT Test").email("pt@test.com").build();
        profile = PTProfile.builder().id(10L).pt(pt).build();
    }

    @Test
    @DisplayName("Tạo slot thành công")
    void testCreateSlotSuccess() {
        LocalDateTime start = LocalDateTime.now().plusDays(2).withHour(9).withMinute(0);
        LocalDateTime end = start.plusHours(1);
        CreateSlotRequest request = CreateSlotRequest.builder()
                .startTime(start)
                .endTime(end)
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(availabilitySlotRepository.findOverlapping(eq(10L), eq(start), eq(end), isNull())).thenReturn(List.of());
        when(availabilitySlotRepository.save(any(AvailabilitySlot.class))).thenAnswer(i -> {
            AvailabilitySlot s = i.getArgument(0);
            return AvailabilitySlot.builder()
                    .id(200L)
                    .pt(s.getPt())
                    .startTime(s.getStartTime())
                    .endTime(s.getEndTime())
                    .status(s.getStatus())
                    .build();
        });

        SlotResponse response = ptSlotService.createSlot("pt@test.com", request);

        assertNotNull(response);
        assertEquals(SlotStatus.AVAILABLE, response.getStatus());
        verify(availabilitySlotRepository).save(any(AvailabilitySlot.class));
    }

    @Test
    @DisplayName("Tạo slot thất bại khi giờ bắt đầu trong quá khứ")
    void testCreateSlotPastThrows() {
        LocalDateTime start = LocalDateTime.now().minusHours(1);
        LocalDateTime end = LocalDateTime.now().plusHours(1);
        CreateSlotRequest request = CreateSlotRequest.builder()
                .startTime(start)
                .endTime(end)
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);

        assertThrows(IllegalArgumentException.class, () -> ptSlotService.createSlot("pt@test.com", request));
        verify(availabilitySlotRepository, never()).save(any());
    }

    @Test
    @DisplayName("Tạo slot thất bại khi trùng giờ (overlapping)")
    void testCreateSlotOverlappingThrows() {
        LocalDateTime start = LocalDateTime.now().plusDays(1).withHour(10).withMinute(0);
        LocalDateTime end = start.plusHours(1);
        CreateSlotRequest request = CreateSlotRequest.builder()
                .startTime(start)
                .endTime(end)
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(availabilitySlotRepository.findOverlapping(eq(10L), eq(start), eq(end), isNull()))
                .thenReturn(List.of(new AvailabilitySlot()));

        assertThrows(IllegalArgumentException.class, () -> ptSlotService.createSlot("pt@test.com", request));
        verify(availabilitySlotRepository, never()).save(any());
    }

    @Test
    @DisplayName("Xóa slot của PT khác ném UnauthorizedException")
    void testDeleteSlotOtherPTThrows() {
        PTProfile otherProfile = PTProfile.builder().id(99L).build();
        AvailabilitySlot slot = AvailabilitySlot.builder().id(300L).pt(otherProfile).build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(availabilitySlotRepository.findById(300L)).thenReturn(Optional.of(slot));

        assertThrows(UnauthorizedException.class, () -> ptSlotService.deleteSlot("pt@test.com", 300L));
    }

    @Test
    @DisplayName("Xóa slot đã có booking ném IllegalArgumentException")
    void testDeleteSlotHasBookingThrows() {
        AvailabilitySlot slot = AvailabilitySlot.builder().id(300L).pt(profile).status(SlotStatus.AVAILABLE).build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(availabilitySlotRepository.findById(300L)).thenReturn(Optional.of(slot));
        when(bookingRepository.findBySlotId(300L)).thenReturn(Optional.of(new Booking()));

        assertThrows(IllegalArgumentException.class, () -> ptSlotService.deleteSlot("pt@test.com", 300L));
        verify(availabilitySlotRepository, never()).delete(any());
    }

    @Test
    @DisplayName("Xóa slot AVAILABLE thành công")
    void testDeleteSlotSuccess() {
        AvailabilitySlot slot = AvailabilitySlot.builder().id(300L).pt(profile).status(SlotStatus.AVAILABLE).build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(availabilitySlotRepository.findById(300L)).thenReturn(Optional.of(slot));
        when(bookingRepository.findBySlotId(300L)).thenReturn(Optional.empty());

        ptSlotService.deleteSlot("pt@test.com", 300L);

        verify(availabilitySlotRepository).delete(slot);
    }
}
