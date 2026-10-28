package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.impl.AdminPTServiceImpl;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AdminPTServiceTest {

    @Mock
    private PTProfileRepository ptProfileRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private AdminPTServiceImpl adminPTService;

    @Test
    @DisplayName("Lấy danh sách PT đang chờ duyệt (PENDING)")
    void testGetPendingPTs() {
        PT pt = PT.builder().id(1L).fullName("PT Test").email("pt@test.com").status(UserStatus.PENDING).build();
        PTProfile profile = PTProfile.builder().id(10L).pt(pt).verificationStatus(VerificationStatus.PENDING).build();

        when(ptProfileRepository.findByVerificationStatus(VerificationStatus.PENDING)).thenReturn(List.of(profile));

        List<PendingPTResponse> result = adminPTService.getPendingPTs();
        assertEquals(1, result.size());
        assertEquals("PT Test", result.get(0).getFullName());
        assertEquals(VerificationStatus.PENDING, result.get(0).getVerificationStatus());
    }

    @Test
    @DisplayName("Admin phê duyệt PT thành công: profile chuyển VERIFIED, PT chuyển ACTIVE (Rich Domain Model)")
    void testApprovePTSuccess() {
        PT pt = PT.builder().id(2L).fullName("PT Hoang").email("hoang@test.com").status(UserStatus.PENDING).build();
        PTProfile profile = PTProfile.builder().id(20L).pt(pt).verificationStatus(VerificationStatus.PENDING).build();

        when(ptProfileRepository.findById(20L)).thenReturn(Optional.of(profile));
        when(ptProfileRepository.save(any(PTProfile.class))).thenAnswer(i -> i.getArgument(0));

        PTProfileResponse response = adminPTService.approvePT(20L);

        assertNotNull(response);
        assertEquals(VerificationStatus.VERIFIED, profile.getVerificationStatus());
        assertEquals(UserStatus.ACTIVE, pt.getStatus());
        verify(userRepository).save(pt);
        verify(ptProfileRepository).save(profile);
    }

    @Test
    @DisplayName("Admin từ chối PT thành công: profile chuyển REJECTED, PT giữ PENDING (Rich Domain Model)")
    void testRejectPTSuccess() {
        PT pt = PT.builder().id(3L).fullName("PT Binh").email("binh@test.com").status(UserStatus.PENDING).build();
        PTProfile profile = PTProfile.builder().id(30L).pt(pt).verificationStatus(VerificationStatus.PENDING).build();

        when(ptProfileRepository.findById(30L)).thenReturn(Optional.of(profile));
        when(ptProfileRepository.save(any(PTProfile.class))).thenAnswer(i -> i.getArgument(0));

        PTProfileResponse response = adminPTService.rejectPT(30L);

        assertNotNull(response);
        assertEquals(VerificationStatus.REJECTED, profile.getVerificationStatus());
        assertEquals(UserStatus.PENDING, pt.getStatus());
        verify(userRepository).save(pt);
        verify(ptProfileRepository).save(profile);
    }

    @Test
    @DisplayName("Phê duyệt thất bại khi không tìm thấy hồ sơ PT")
    void testApprovePTNotFound() {
        when(ptProfileRepository.findById(999L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class, () -> adminPTService.approvePT(999L));
        verify(ptProfileRepository, never()).save(any());
    }
}
