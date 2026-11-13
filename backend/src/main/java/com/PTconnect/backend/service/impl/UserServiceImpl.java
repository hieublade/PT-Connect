package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IUserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserServiceImpl implements IUserService {

    private final UserRepository userRepository;

    @Override
    public List<UserDTO> getAllUsers() {
        return userRepository.findAll().stream()
                .map(UserDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    public List<UserDTO> getUsersByRole(Role role) {
        return userRepository.findByRole(role).stream()
                .map(UserDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    public UserDTO getUserById(Long id) {
        return userRepository.findById(id)
                .map(UserDTO::fromEntity)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với ID: " + id));
    }

    @Override
    public UserDTO getUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .map(UserDTO::fromEntity)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + email));
    }

    @Override
    @Transactional
    public UserDTO updateProfile(String email, com.PTconnect.backend.dto.request.UpdateProfileRequest request) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + email));

        // Kiểm tra số điện thoại nếu thay đổi
        String newPhone = request.getPhone() != null ? request.getPhone().trim() : null;
        if (newPhone != null && !newPhone.equals(user.getPhone())) {
            if (userRepository.existsByPhone(newPhone)) {
                throw new IllegalArgumentException("Số điện thoại này đã được sử dụng bởi tài khoản khác: " + newPhone);
            }
            user.setPhone(newPhone);
        }

        if (request.getFullName() != null && !request.getFullName().trim().isEmpty()) {
            user.setFullName(request.getFullName().trim());
        }

        if (request.getAvatarUrl() != null) {
            user.setAvatarUrl(request.getAvatarUrl().trim().isEmpty() ? null : request.getAvatarUrl().trim());
        }

        User savedUser = userRepository.save(user);
        return UserDTO.fromEntity(savedUser);
    }

    @Override
    @Transactional
    public UserDTO updateAvatar(String email, String avatarUrl) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + email));

        user.setAvatarUrl(avatarUrl);
        User savedUser = userRepository.save(user);
        return UserDTO.fromEntity(savedUser);
    }

    @Override
    @Transactional
    public UserDTO uploadAvatar(String email, MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BadRequestException("Tập tin hình ảnh không được để trống!");
        }

        String contentType = file.getContentType();
        if (contentType != null && !contentType.startsWith("image/")) {
            throw new BadRequestException("Chỉ chấp nhận các định dạng tệp hình ảnh (JPEG, PNG, WEBP, GIF)!");
        }

        if (file.getSize() > 5 * 1024 * 1024) {
            throw new BadRequestException("Dung lượng tập tin ảnh không được vượt quá 5MB!");
        }

        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + email));

        try {
            Path uploadDir = Paths.get("uploads", "avatars");
            if (!Files.exists(uploadDir)) {
                Files.createDirectories(uploadDir);
            }

            String originalFilename = file.getOriginalFilename();
            String extension = ".jpg";
            if (originalFilename != null && originalFilename.lastIndexOf('.') > 0) {
                extension = originalFilename.substring(originalFilename.lastIndexOf('.')).toLowerCase();
            }

            String uniqueFilename = "avatar_" + user.getId() + "_" + System.currentTimeMillis() + extension;
            Path destinationPath = uploadDir.resolve(uniqueFilename);

            Files.copy(file.getInputStream(), destinationPath, StandardCopyOption.REPLACE_EXISTING);

            String relativeUrl = "/uploads/avatars/" + uniqueFilename;
            user.setAvatarUrl(relativeUrl);
            User savedUser = userRepository.save(user);

            return UserDTO.fromEntity(savedUser);
        } catch (IOException e) {
            throw new BadRequestException("Lỗi lưu trữ tập tin ảnh trên máy chủ: " + e.getMessage());
        }
    }

    @Override
    @Transactional
    public UserDTO updateUserStatus(Long id, UserStatus status) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với ID: " + id));
        user.setStatus(status);
        User savedUser = userRepository.save(user);
        return UserDTO.fromEntity(savedUser);
    }
}
