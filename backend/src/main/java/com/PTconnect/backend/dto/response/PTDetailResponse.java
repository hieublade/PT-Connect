package com.PTconnect.backend.dto.response;

import lombok.*;

import java.util.List;

/**
 * DTO chi tiết PT bao gồm hồ sơ công khai, danh sách khóa học ACTIVE và các slot rảnh AVAILABLE.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PTDetailResponse {
    private PTPublicDTO profile;
    private List<CourseResponse> courses;
    private List<SlotResponse> availableSlots;
}
