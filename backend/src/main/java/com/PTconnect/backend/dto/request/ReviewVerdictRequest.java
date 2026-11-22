package com.PTconnect.backend.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.*;

/**
 * DTO Quản trị viên (Admin) đưa ra phán quyết xử lý đánh giá 1-3 sao:
 * REMOVE (Xóa bỏ đánh giá xấu), KEEP (Giữ lại đánh giá xấu), REQUEST_EVIDENCE (Yêu cầu thêm bằng chứng).
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReviewVerdictRequest {

    @NotBlank(message = "Quyết định xử lý không được để trống (REMOVE, KEEP, REQUEST_EVIDENCE)")
    private String decision;

    @NotBlank(message = "Lý do / Ghi chú phán quyết của Quản trị viên không được để trống")
    private String adminNote;
}
