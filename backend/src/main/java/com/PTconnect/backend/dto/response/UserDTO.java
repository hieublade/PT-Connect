package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.UserStatus;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDTO {

    private Long id;
    private String fullName;
    private String email;
    private String phone;
    private Role role;
    private UserStatus status;
    private String avatarUrl;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String displayRole;
    private String homePage;

    public static UserDTO fromEntity(User user) {
        if (user == null) {
            return null;
        }
        return UserDTO.builder()
                .id(user.getId())
                .fullName(user.getFullName())
                .email(user.getEmail())
                .phone(user.getPhone())
                .role(user.getRole())
                .status(user.getStatus())
                .avatarUrl(user.getAvatarUrl())
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .displayRole(user.getDisplayRole())
                .homePage(user.getHomePage())
                .build();
    }
}
