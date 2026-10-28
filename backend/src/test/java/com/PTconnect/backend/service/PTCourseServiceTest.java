package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.Enrollment;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.service.impl.PTCourseServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("Kiểm thử PTCourseService (Ưu tiên 3 SRP)")
class PTCourseServiceTest {

    @Mock
    private IPTProfileService ptProfileService;

    @Mock
    private CourseRepository courseRepository;

    @Mock
    private EnrollmentRepository enrollmentRepository;

    @InjectMocks
    private PTCourseServiceImpl ptCourseService;

    private PTProfile profile;

    @BeforeEach
    void setUp() {
        PT pt = PT.builder().id(1L).fullName("PT Test").email("pt@test.com").build();
        profile = PTProfile.builder().id(10L).pt(pt).build();
    }

    @Test
    @DisplayName("Tạo khóa học thành công")
    void testCreateCourseSuccess() {
        CreateCourseRequest request = CreateCourseRequest.builder()
                .title("Khóa Giảm Cân")
                .description("Mô tả")
                .totalSessions(10)
                .validityDays(30)
                .basePrice(new BigDecimal("1000000"))
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(courseRepository.save(any(Course.class))).thenAnswer(i -> {
            Course c = i.getArgument(0);
            return Course.builder()
                    .id(100L)
                    .pt(c.getPt())
                    .title(c.getTitle())
                    .description(c.getDescription())
                    .totalSessions(c.getTotalSessions())
                    .validityDays(c.getValidityDays())
                    .basePrice(c.getBasePrice())
                    .status(c.getStatus())
                    .build();
        });

        CourseResponse response = ptCourseService.createCourse("pt@test.com", request);

        assertNotNull(response);
        assertEquals("Khóa Giảm Cân", response.getTitle());
        assertEquals(10, response.getTotalSessions());
        verify(courseRepository).save(any(Course.class));
    }

    @Test
    @DisplayName("Tạo khóa học thất bại khi tổng số buổi <= 0")
    void testCreateCourseInvalidSessionsThrows() {
        CreateCourseRequest request = CreateCourseRequest.builder()
                .title("Khóa Lỗi")
                .totalSessions(0)
                .validityDays(30)
                .basePrice(new BigDecimal("1000000"))
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);

        assertThrows(IllegalArgumentException.class, () -> ptCourseService.createCourse("pt@test.com", request));
        verify(courseRepository, never()).save(any());
    }

    @Test
    @DisplayName("Chỉnh sửa khóa học của PT khác ném UnauthorizedException")
    void testUpdateCourseOtherPTThrows() {
        PTProfile otherProfile = PTProfile.builder().id(99L).build();
        Course course = Course.builder().id(50L).pt(otherProfile).build();

        UpdateCourseRequest request = UpdateCourseRequest.builder()
                .title("Sửa tên")
                .totalSessions(5)
                .validityDays(10)
                .basePrice(new BigDecimal("500000"))
                .build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(courseRepository.findById(50L)).thenReturn(Optional.of(course));

        assertThrows(UnauthorizedException.class, () -> ptCourseService.updateCourse("pt@test.com", 50L, request));
    }

    @Test
    @DisplayName("Xóa khóa học đã có học viên đăng ký ném IllegalArgumentException")
    void testDeleteCourseWithEnrollmentThrows() {
        Course course = Course.builder().id(50L).pt(profile).build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(courseRepository.findById(50L)).thenReturn(Optional.of(course));
        when(enrollmentRepository.findByCourseId(50L)).thenReturn(List.of(new Enrollment()));

        assertThrows(IllegalArgumentException.class, () -> ptCourseService.deleteCourse("pt@test.com", 50L));
        verify(courseRepository, never()).delete(any());
    }

    @Test
    @DisplayName("Xóa khóa học thành công khi chưa có học viên nào mua")
    void testDeleteCourseSuccess() {
        Course course = Course.builder().id(50L).pt(profile).build();

        when(ptProfileService.getPTProfileEntity("pt@test.com")).thenReturn(profile);
        when(courseRepository.findById(50L)).thenReturn(Optional.of(course));
        when(enrollmentRepository.findByCourseId(50L)).thenReturn(List.of());

        ptCourseService.deleteCourse("pt@test.com", 50L);

        verify(courseRepository).delete(course);
    }
}
