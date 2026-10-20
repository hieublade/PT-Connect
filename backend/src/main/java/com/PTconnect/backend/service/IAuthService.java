package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.LoginRequest;
import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.dto.response.AuthResponse;
import com.PTconnect.backend.dto.response.UserDTO;

public interface IAuthService {
    AuthResponse register(RegisterRequest request);
    AuthResponse login(LoginRequest request);
    UserDTO getMe(String email);
}
