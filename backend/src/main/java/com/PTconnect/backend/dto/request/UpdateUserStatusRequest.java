package com.PTconnect.backend.dto.request;

import com.PTconnect.backend.entity.enums.UserStatus;
import jakarta.validation.constraints.NotNull;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateUserStatusRequest {

    @NotNull(message = "Trạng thái người dùng không được để trống")
    private UserStatus status;
}
