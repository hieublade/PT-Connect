package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateAvatarRequest {

    @NotBlank(message = "URL ảnh đại diện không được để trống")
    private String avatarUrl;
}

