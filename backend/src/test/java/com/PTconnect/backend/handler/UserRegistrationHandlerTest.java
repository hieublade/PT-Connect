package com.PTconnect.backend.handler;

import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.Student;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.PTRepository;
import com.PTconnect.backend.repository.StudentRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class UserRegistrationHandlerTest {

    @Mock
    private StudentRepository studentRepository;

    @Mock
    private PTRepository ptRepository;

    @Mock
    private PTProfileRepository ptProfileRepository;

    @InjectMocks
    private StudentRegistrationHandler studentHandler;

    @InjectMocks
    private PtRegistrationHandler ptHandler;

    @Test
    @DisplayName("StudentRegistrationHandler: hỗ trợ đúng Role.STUDENT")
    void testStudentHandlerSupports() {
        assertTrue(studentHandler.supports(Role.STUDENT));
        assertFalse(studentHandler.supports(Role.PT));
        assertFalse(studentHandler.supports(Role.ADMIN));
    }

    @Test
    @DisplayName("StudentRegistrationHandler: lưu Student thành công với status ACTIVE")
    void testStudentRegister() {
        RegisterRequest request = RegisterRequest.builder()
                .fullName("Nguyen Van Hoc")
                .email("student@test.com")
                .phone("0912345678")
                .role(Role.STUDENT)
                .build();

        when(studentRepository.save(any(Student.class))).thenAnswer(i -> i.getArgument(0));

        User user = studentHandler.register(request, "encoded_pwd");

        assertNotNull(user);
        assertTrue(user instanceof Student);
        assertEquals("Nguyen Van Hoc", user.getFullName());
        assertEquals(UserStatus.ACTIVE, user.getStatus());
        assertEquals("encoded_pwd", user.getPasswordHash());
        verify(studentRepository).save(any(Student.class));
    }

    @Test
    @DisplayName("PtRegistrationHandler: hỗ trợ đúng Role.PT")
    void testPtHandlerSupports() {
        assertTrue(ptHandler.supports(Role.PT));
        assertFalse(ptHandler.supports(Role.STUDENT));
        assertFalse(ptHandler.supports(Role.ADMIN));
    }

    @Test
    @DisplayName("PtRegistrationHandler: lưu PT và PTProfile với status PENDING, không dùng Downcasting")
    void testPtRegister() {
        RegisterRequest request = RegisterRequest.builder()
                .fullName("Tran Van Day")
                .email("pt@test.com")
                .phone("0987654321")
                .role(Role.PT)
                .bio("HLV the hinh 3 nam")
                .experienceYears(3)
                .availableLocations("Quan 1")
                .build();

        when(ptRepository.save(any(PT.class))).thenAnswer(i -> i.getArgument(0));
        when(ptProfileRepository.save(any(PTProfile.class))).thenAnswer(i -> i.getArgument(0));

        User user = ptHandler.register(request, "encoded_pwd");

        assertNotNull(user);
        assertTrue(user instanceof PT);
        PT pt = (PT) user;
        assertEquals("Tran Van Day", pt.getFullName());
        assertEquals(UserStatus.PENDING, pt.getStatus());
        assertNotNull(pt.getProfile());
        assertEquals(VerificationStatus.PENDING, pt.getProfile().getVerificationStatus());
        assertEquals("Quan 1", pt.getProfile().getAvailableLocations());

        verify(ptRepository).save(any(PT.class));
        verify(ptProfileRepository).save(any(PTProfile.class));
    }
}
