package com.ptconnect.service.impl;

import com.ptconnect.dto.request.UserRegisterRequest;
import com.ptconnect.dto.response.UserResponse;
import com.ptconnect.entity.PT;
import com.ptconnect.entity.PTProfile;
import com.ptconnect.entity.Student;
import com.ptconnect.entity.User;
import com.ptconnect.enums.Role;
import com.ptconnect.enums.UserStatus;
import com.ptconnect.enums.VerificationStatus;
import com.ptconnect.exception.AppException;
import com.ptconnect.exception.ErrorCode;
import com.ptconnect.repository.PTProfileRepository;
import com.ptconnect.repository.UserRepository;
import com.ptconnect.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;

    @Override
    @Transactional
    public UserResponse registerUser(UserRegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail()) || userRepository.existsByPhone(request.getPhone())) {
            throw new AppException(ErrorCode.USER_EXISTED);
        }

        // Tạo đối tượng theo Role
        if (request.getRole() == Role.PT) {
            PT pt = PT.builder()
                    .fullName(request.getFullName())
                    .email(request.getEmail())
                    .passwordHash(request.getPassword()) // Lưu ý: Cần Bcrypt hash khi tích hợp Security
                    .phone(request.getPhone())
                    .status(UserStatus.PENDING) // PT mới tạo ở trạng thái PENDING
                    .build();

            PT savedPT = userRepository.save(pt);

            // Tự động khởi tạo hồ sơ PTProfile tương ứng
            PTProfile profile = PTProfile.builder()
                    .user(savedPT)
                    .experienceYears(0)
                    .averageRating(BigDecimal.ZERO)
                    .totalReviews(0)
                    .verificationStatus(VerificationStatus.PENDING)
                    .build();
            ptProfileRepository.save(profile);

            return mapToResponse(savedPT);
        } else {
            Student student = Student.builder()
                    .fullName(request.getFullName())
                    .email(request.getEmail())
                    .passwordHash(request.getPassword())
                    .phone(request.getPhone())
                    .status(UserStatus.ACTIVE) // STUDENT mặc định ACTIVE
                    .build();

            Student savedStudent = userRepository.save(student);
            return mapToResponse(savedStudent);
        }
    }

    @Override
    public UserResponse getUserById(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_FOUND));
        return mapToResponse(user);
    }

    @Override
    public List<UserResponse> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private UserResponse mapToResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .fullName(user.getFullName())
                .email(user.getEmail())
                .phone(user.getPhone())
                .role(user.getRole() != null ? user.getRole().name() : null)
                .status(user.getStatus() != null ? user.getStatus().name() : null)
                .avatarUrl(user.getAvatarUrl())
                .createdAt(user.getCreatedAt())
                .build();
    }
}