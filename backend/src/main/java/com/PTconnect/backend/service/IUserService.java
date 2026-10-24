package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.UserDTO;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;

import java.util.List;

public interface IUserService {

    List<UserDTO> getAllUsers();

    List<UserDTO> getUsersByRole(Role role);

    UserDTO getUserById(Long id);

    UserDTO updateAvatar(String email, String avatarUrl);

    UserDTO updateUserStatus(Long id, UserStatus status);
}
