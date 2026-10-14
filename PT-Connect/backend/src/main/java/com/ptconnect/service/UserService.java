package com.ptconnect.service;

import com.ptconnect.dto.request.UserRegisterRequest;
import com.ptconnect.dto.response.UserResponse;

import java.util.List;

public interface UserService {
    UserResponse registerUser(UserRegisterRequest request);
    UserResponse getUserById(Long userId);
    List<UserResponse> getAllUsers();
}