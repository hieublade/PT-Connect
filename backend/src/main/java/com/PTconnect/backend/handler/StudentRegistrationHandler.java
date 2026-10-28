package com.PTconnect.backend.handler;

import com.PTconnect.backend.dto.request.RegisterRequest;
import com.PTconnect.backend.entity.Student;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.repository.StudentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class StudentRegistrationHandler implements UserRegistrationHandler {

    private final StudentRepository studentRepository;

    @Override
    public boolean supports(Role role) {
        return role == Role.STUDENT;
    }

    @Override
    public User register(RegisterRequest request, String encodedPassword) {
        Student student = Student.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .passwordHash(encodedPassword)
                .phone(request.getPhone())
                .role(Role.STUDENT)
                .status(UserStatus.ACTIVE)
                .build();

        return studentRepository.save(student);
    }
}
