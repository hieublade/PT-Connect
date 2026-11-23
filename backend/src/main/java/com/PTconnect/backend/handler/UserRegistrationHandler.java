package com.PTconnect.backend.handler;

import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;

public interface UserRegistrationHandler {

    boolean supports(Role role);

    User register(RegisterRequest request, String encodedPassword);
}

