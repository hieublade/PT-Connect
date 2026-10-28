package com.PTconnect.backend.service;

import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.dto.response.AuthResponse;
import com.PTconnect.backend.entity.Student;
import com.PTconnect.backend.entity.Wallet;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.handler.UserRegistrationHandler;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import com.PTconnect.backend.service.impl.AuthServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private WalletRepository walletRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Mock
    private JwtUtil jwtUtil;

    @Mock
    private UserRegistrationHandler studentRegistrationHandler;

    private AuthServiceImpl authService;

    @BeforeEach
    void setUp() {
        authService = new AuthServiceImpl(
                userRepository,
                walletRepository,
                passwordEncoder,
                jwtUtil,
                List.of(studentRegistrationHandler)
        );
    }

    @Test
    @DisplayName("Đăng ký thành công: ủy thác cho UserRegistrationHandler phù hợp và tự tạo ví")
    void testRegisterSuccessViaHandler() {
        RegisterRequest request = RegisterRequest.builder()
                .fullName("Nguyen Van A")
                .email("test@ptconnect.vn")
                .password("123456")
                .phone("0981112233")
                .role(Role.STUDENT)
                .build();

        when(userRepository.existsByEmail("test@ptconnect.vn")).thenReturn(false);
        when(userRepository.existsByPhone("0981112233")).thenReturn(false);
        when(studentRegistrationHandler.supports(Role.STUDENT)).thenReturn(true);

        Student student = Student.builder()
                .id(100L)
                .fullName("Nguyen Van A")
                .email("test@ptconnect.vn")
                .passwordHash("hashed_123")
                .phone("0981112233")
                .role(Role.STUDENT)
                .status(UserStatus.ACTIVE)
                .build();

        when(passwordEncoder.encode("123456")).thenReturn("hashed_123");
        when(studentRegistrationHandler.register(request, "hashed_123")).thenReturn(student);
        when(jwtUtil.generateToken(student)).thenReturn("jwt_mock_token");

        AuthResponse response = authService.register(request);

        assertNotNull(response);
        assertEquals("jwt_mock_token", response.getToken());
        assertEquals("test@ptconnect.vn", response.getUser().getEmail());

        verify(walletRepository).save(any(Wallet.class));
        verify(studentRegistrationHandler).register(request, "hashed_123");
    }

    @Test
    @DisplayName("Đăng ký thất bại khi email đã tồn tại")
    void testRegisterDuplicateEmail() {
        RegisterRequest request = RegisterRequest.builder()
                .email("dup@ptconnect.vn")
                .phone("0981112233")
                .role(Role.STUDENT)
                .build();

        when(userRepository.existsByEmail("dup@ptconnect.vn")).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> authService.register(request));
        verify(studentRegistrationHandler, never()).register(any(), any());
    }

    @Test
    @DisplayName("Đăng ký thất bại khi vai trò không được hỗ trợ bởi handler nào")
    void testRegisterUnsupportedRole() {
        RegisterRequest request = RegisterRequest.builder()
                .email("admin@ptconnect.vn")
                .phone("0981112233")
                .role(Role.ADMIN)
                .password("123456")
                .build();

        when(userRepository.existsByEmail("admin@ptconnect.vn")).thenReturn(false);
        when(userRepository.existsByPhone("0981112233")).thenReturn(false);
        when(studentRegistrationHandler.supports(Role.ADMIN)).thenReturn(false);

        assertThrows(IllegalArgumentException.class, () -> authService.register(request));
    }
}
