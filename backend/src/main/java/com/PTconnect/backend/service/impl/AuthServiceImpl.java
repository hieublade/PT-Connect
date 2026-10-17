package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.config.JwtUtil;
import com.PTconnect.backend.dto.request.LoginRequest;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.dto.response.AuthResponse;
import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.entity.enums.WalletStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.repository.WalletRepository;
import com.PTconnect.backend.service.IAuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements IAuthService {

    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;
    private final WalletRepository walletRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

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
        if (request.getRole() != Role.STUDENT && request.getRole() != Role.PT) {
            throw new IllegalArgumentException("Hệ thống chỉ hỗ trợ đăng ký cho vai trò STUDENT hoặc PT");
        }

        // 2. Mã hóa mật khẩu bằng BCrypt
        String passwordHash = passwordEncoder.encode(request.getPassword());

        User savedUser;

        // 3. Tạo Entity tương ứng theo Role trong cùng 1 Transaction
        if (request.getRole() == Role.PT) {
            PT pt = PT.builder()
                    .fullName(request.getFullName())
                    .email(request.getEmail())
                    .passwordHash(passwordHash)
                    .phone(request.getPhone())
                    .role(Role.PT)
                    .status(UserStatus.ACTIVE)
                    .build();
            savedUser = userRepository.save(pt);

            String locations = (request.getAvailableLocations() != null && !request.getAvailableLocations().isBlank())
                    ? request.getAvailableLocations()
                    : "Chưa cập nhật địa điểm";

            PTProfile profile = PTProfile.builder()
                    .pt((PT) savedUser)
                    .bio(request.getBio())
                    .experienceYears(request.getExperienceYears() != null ? request.getExperienceYears() : 0)
                    .availableLocations(locations)
                    .locationPricingNote(request.getLocationPricingNote())
                    .certificateUrls(request.getCertificateUrls())
                    .verificationStatus(VerificationStatus.PENDING) // PT mới đăng ký ở PENDING
                    .build();

            ptProfileRepository.save(profile);
            ((PT) savedUser).setProfile(profile);
        } else {
            Student student = Student.builder()
                    .fullName(request.getFullName())
                    .email(request.getEmail())
                    .passwordHash(passwordHash)
                    .phone(request.getPhone())
                    .role(Role.STUDENT)
                    .status(UserStatus.ACTIVE)
                    .build();
            savedUser = userRepository.save(student);
        }

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
