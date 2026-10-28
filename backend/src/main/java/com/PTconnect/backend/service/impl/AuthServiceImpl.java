package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.dto.request.LoginRequest;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.dto.response.AuthResponse;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.WalletStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.handler.UserRegistrationHandler;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import com.PTconnect.backend.service.IAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements IAuthService {

    private final UserRepository userRepository;
    private final WalletRepository walletRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final List<UserRegistrationHandler> registrationHandlers;

    @Override
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // 1. Kiểm tra tính duy nhất của Email và Số điện thoại
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email đã được sử dụng: " + request.getEmail());
        }
        if (userRepository.existsByPhone(request.getPhone())) {
            throw new IllegalArgumentException("Số điện thoại đã được sử dụng: " + request.getPhone());
        }

        // Tìm Handler xử lý đăng ký phù hợp theo vai trò (OCP & Factory/Strategy Pattern)
        UserRegistrationHandler handler = registrationHandlers.stream()
                .filter(h -> h.supports(request.getRole()))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Hệ thống chỉ hỗ trợ đăng ký cho vai trò STUDENT hoặc PT"));

        // 2. Mã hóa mật khẩu bằng BCrypt
        String passwordHash = passwordEncoder.encode(request.getPassword());

        // 3. Khởi tạo và lưu User/Profile thông qua Handler tương ứng (loại bỏ if-else và Downcasting)
        User savedUser = handler.register(request, passwordHash);

        // 4. Tạo ví (Wallet) ban đầu với số dư 0 VND trong cùng Transaction
        Wallet wallet = Wallet.builder()
                .user(savedUser)
                .balance(BigDecimal.ZERO)
                .lockedBalance(BigDecimal.ZERO)
                .currency("VND")
                .status(WalletStatus.ACTIVE)
                .build();
        walletRepository.save(wallet);

        // 5. Sinh JWT Token và trả về thông tin
        String token = jwtUtil.generateToken(savedUser);
        return AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .user(UserDTO.fromEntity(savedUser))
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new UnauthorizedException("Email hoặc mật khẩu không chính xác"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new UnauthorizedException("Email hoặc mật khẩu không chính xác");
        }

        if (user.getStatus() == UserStatus.SUSPENDED) {
            throw new UnauthorizedException("Tài khoản của bạn hiện đang bị tạm khóa");
        }

        String token = jwtUtil.generateToken(user);
        return AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .user(UserDTO.fromEntity(user))
                .build();
    }

    @Override
    @Transactional(readOnly = true)
    public UserDTO getMe(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy thông tin tài khoản"));
        return UserDTO.fromEntity(user);
    }
}
