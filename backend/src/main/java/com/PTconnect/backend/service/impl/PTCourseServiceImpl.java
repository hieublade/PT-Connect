package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.service.IPTCourseService;
import com.PTconnect.backend.service.IPTProfileService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

/**
 * Service chuyên biệt quản lý Khóa học của Huấn luyện viên (PT Course).
 * Đảm bảo nguyên lý Đơn nhiệm (SRP) - Chỉ tiêm các repository liên quan tới Course và Enrollment.
 */
@Service
@RequiredArgsConstructor
public class PTCourseServiceImpl implements IPTCourseService {

    private final IPTProfileService ptProfileService;
    private final CourseRepository courseRepository;
    private final EnrollmentRepository enrollmentRepository;

    @Override
    @Transactional
    public CourseResponse createCourse(String userEmail, CreateCourseRequest request) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);

        if (request.getTitle() == null || request.getTitle().trim().isEmpty()) {
            throw new IllegalArgumentException("Tên khóa học không được để trống");
        }
        if (request.getTotalSessions() == null || request.getTotalSessions() <= 0) {
            throw new IllegalArgumentException("Tổng số buổi học phải lớn hơn 0");
        }
        if (request.getValidityDays() == null || request.getValidityDays() <= 0) {
            throw new IllegalArgumentException("Thời hạn khóa học phải lớn hơn 0 ngày");
        }
        if (request.getBasePrice() == null || request.getBasePrice().compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Giá khóa học không được âm");
        }

        Course course = Course.builder()
                .pt(profile)
                .title(request.getTitle().trim())
                .description(request.getDescription())
                .totalSessions(request.getTotalSessions())
                .validityDays(request.getValidityDays())
                .basePrice(request.getBasePrice())
                .status(CourseStatus.ACTIVE)
                .build();

        Course saved = courseRepository.save(course);
        return CourseResponse.fromEntity(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CourseResponse> getCourses(String userEmail) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);
        List<Course> courses = courseRepository.findByPtId(profile.getId());
        return courses.stream()
                .map(CourseResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional
    public CourseResponse updateCourse(String userEmail, Long courseId, UpdateCourseRequest request) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);

        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khóa học với ID: " + courseId));

        if (!course.getPt().getId().equals(profile.getId())) {
            throw new UnauthorizedException("Bạn không có quyền chỉnh sửa khóa học của Huấn luyện viên khác");
        }

        if (request.getTitle() == null || request.getTitle().trim().isEmpty()) {
            throw new IllegalArgumentException("Tên khóa học không được để trống");
        }
        if (request.getTotalSessions() == null || request.getTotalSessions() <= 0) {
            throw new IllegalArgumentException("Tổng số buổi học phải lớn hơn 0");
        }
        if (request.getValidityDays() == null || request.getValidityDays() <= 0) {
            throw new IllegalArgumentException("Thời hạn khóa học phải lớn hơn 0 ngày");
        }
        if (request.getBasePrice() == null || request.getBasePrice().compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Giá khóa học không được âm");
        }

        course.setTitle(request.getTitle().trim());
        course.setDescription(request.getDescription());
        course.setTotalSessions(request.getTotalSessions());
        course.setValidityDays(request.getValidityDays());
        course.setBasePrice(request.getBasePrice());

        if (request.getStatus() != null) {
            course.setStatus(request.getStatus());
        }

        Course saved = courseRepository.save(course);
        return CourseResponse.fromEntity(saved);
    }

    @Override
    @Transactional
    public void deleteCourse(String userEmail, Long courseId) {
        PTProfile profile = ptProfileService.getPTProfileEntity(userEmail);

        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khóa học với ID: " + courseId));

        if (!course.getPt().getId().equals(profile.getId())) {
            throw new UnauthorizedException("Bạn không có quyền xóa khóa học của Huấn luyện viên khác");
        }

        if (!enrollmentRepository.findByCourseId(courseId).isEmpty()) {
            throw new IllegalArgumentException("Khóa học đã có hợp đồng học viên đăng ký, chỉ có thể ngưng bán (chuyển sang INACTIVE)");
        }

        courseRepository.delete(course);
    }
}
