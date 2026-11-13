package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;

import java.util.List;

public interface IUserService {

    List<UserDTO> getAllUsers();

    List<UserDTO> getUsersByRole(Role role);

    UserDTO getUserById(Long id);

    UserDTO getUserByEmail(String email);

    UserDTO updateProfile(String email, com.PTconnect.backend.dto.request.UpdateProfileRequest request);

    UserDTO updateAvatar(String email, String avatarUrl);

    UserDTO uploadAvatar(String email, org.springframework.web.multipart.MultipartFile file);

    UserDTO updateUserStatus(Long id, UserStatus status);
}
