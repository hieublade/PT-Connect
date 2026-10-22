package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

/**
 * DTO yêu cầu cập nhật ảnh đại diện người dùng (Milestone 6 - Hiệu).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateAvatarRequest {

    @NotBlank(message = "URL ảnh đại diện không được để trống")
    private String avatarUrl;
}
