package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.request.UpdatePTProfileRequest;
import com.PTconnect.backend.dto.response.CourseResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.dto.response.SlotResponse;
import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.Course;
import com.PTconnect.backend.entity.PT;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.CourseStatus;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.entity.enums.UserStatus;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.CourseRepository;
import com.PTconnect.backend.repository.EnrollmentRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IPTService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class PTServiceImpl implements IPTService {

    private final UserRepository userRepository;
    private final PTProfileRepository ptProfileRepository;
    private final CourseRepository courseRepository;
    private final AvailabilitySlotRepository availabilitySlotRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final BookingRepository bookingRepository;

    private PTProfile getPTProfileByEmail(String userEmail) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        if (user.getRole() != Role.PT) {
            throw new IllegalArgumentException("Người dùng không phải là Huấn luyện viên (PT)");
        }

        if (user.getStatus() == UserStatus.SUSPENDED) {
            throw new UnauthorizedException("Tài khoản của bạn đang bị tạm ngưng (SUSPENDED)");
        }

        return ptProfileRepository.findByPtId(user.getId())
                .orElseGet(() -> {
                    PTProfile newProfile = PTProfile.builder()
                            .pt((PT) user)
                            .bio("")
                            .experienceYears(0)
                            .availableLocations("Chưa cập nhật địa điểm")
                            .verificationStatus(VerificationStatus.PENDING)
                            .build();
                    return ptProfileRepository.save(newProfile);
                });
    }

    @Override
    @Transactional(readOnly = true)
    public PTProfileResponse getProfile(String userEmail) {
        PTProfile profile = getPTProfileByEmail(userEmail);
        return PTProfileResponse.fromEntity(profile);
    }

    @Override
    @Transactional
    public PTProfileResponse updateProfile(String userEmail, UpdatePTProfileRequest request) {
        PTProfile profile = getPTProfileByEmail(userEmail);

        if (request.getExperienceYears() != null && request.getExperienceYears() < 0) {
            throw new IllegalArgumentException("Số năm kinh nghiệm phải lớn hơn hoặc bằng 0");
        }

        if (request.getAvailableLocations() == null || request.getAvailableLocations().trim().isEmpty()) {
            throw new IllegalArgumentException("Địa điểm nhận dạy không được để trống");
        }

        if (request.getBio() != null) {
            profile.setBio(request.getBio().trim());
        }
        if (request.getExperienceYears() != null) {
            profile.setExperienceYears(request.getExperienceYears());
        }
        profile.setAvailableLocations(request.getAvailableLocations().trim());

        if (request.getLocationPricingNote() != null) {
            profile.setLocationPricingNote(request.getLocationPricingNote().trim());
        }

        if (request.getCertificateUrls() != null) {
            profile.setCertificateUrls(request.getCertificateUrls());
        }

        PTProfile saved = ptProfileRepository.save(profile);
        return PTProfileResponse.fromEntity(saved);
    }

    @Override
    @Transactional
    public CourseResponse createCourse(String userEmail, CreateCourseRequest request) {
        PTProfile profile = getPTProfileByEmail(userEmail);

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
        PTProfile profile = getPTProfileByEmail(userEmail);
        List<Course> courses = courseRepository.findByPtId(profile.getId());
        return courses.stream()
                .map(CourseResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional
    public CourseResponse updateCourse(String userEmail, Long courseId, UpdateCourseRequest request) {
        PTProfile profile = getPTProfileByEmail(userEmail);

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
        PTProfile profile = getPTProfileByEmail(userEmail);

        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khóa học với ID: " + courseId));

        if (!course.getPt().getId().equals(profile.getId())) {
            throw new UnauthorizedException("Bạn không có quyền xóa khóa học của Huấn luyện viên khác");
        }

        // Kiểm tra xem khóa học đã có hợp đồng hay chưa
        if (!enrollmentRepository.findByCourseId(courseId).isEmpty()) {
            throw new IllegalArgumentException("Khóa học đã có hợp đồng học viên đăng ký, chỉ có thể ngưng bán (chuyển sang INACTIVE)");
        }

        courseRepository.delete(course);
    }

    @Override
    @Transactional
    public SlotResponse createSlot(String userEmail, CreateSlotRequest request) {
        PTProfile profile = getPTProfileByEmail(userEmail);

        if (request.getStartTime() == null || request.getEndTime() == null) {
            throw new IllegalArgumentException("Thời gian bắt đầu và kết thúc không được để trống");
        }

        // Quy tắc 1: Không tạo slot trong quá khứ
        LocalDateTime now = LocalDateTime.now();
        if (request.getStartTime().isBefore(now)) {
            throw new IllegalArgumentException("Thời gian bắt đầu slot không được ở trong quá khứ");
        }

        // Quy tắc 2: Giờ kết thúc lớn hơn giờ bắt đầu
        if (!request.getEndTime().isAfter(request.getStartTime())) {
            throw new IllegalArgumentException("Thời gian kết thúc slot phải sau thời gian bắt đầu");
        }

        // Quy tắc 3: Không trùng/chồng thời gian với slot khác của chính PT
        List<AvailabilitySlot> overlapping = availabilitySlotRepository.findOverlapping(
                profile.getId(), request.getStartTime(), request.getEndTime(), null);
        if (!overlapping.isEmpty()) {
            throw new IllegalArgumentException("Khung giờ bị trùng hoặc chồng lấn với lịch rảnh khác của bạn");
        }

        AvailabilitySlot slot = AvailabilitySlot.builder()
                .pt(profile)
                .startTime(request.getStartTime())
                .endTime(request.getEndTime())
                .status(SlotStatus.AVAILABLE)
                .build();

        AvailabilitySlot saved = availabilitySlotRepository.save(slot);
        return SlotResponse.fromEntity(saved);
    }

    @Override
    @Transactional(readOnly = true)
    public List<SlotResponse> getSlots(String userEmail) {
        PTProfile profile = getPTProfileByEmail(userEmail);
        List<AvailabilitySlot> slots = availabilitySlotRepository.findByPtIdOrderByStartTimeAsc(profile.getId());
        return slots.stream()
                .map(SlotResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional
    public void deleteSlot(String userEmail, Long slotId) {
        PTProfile profile = getPTProfileByEmail(userEmail);

        AvailabilitySlot slot = availabilitySlotRepository.findById(slotId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy khung giờ (slot) với ID: " + slotId));

        if (!slot.getPt().getId().equals(profile.getId())) {
            throw new UnauthorizedException("Bạn không có quyền xóa khung giờ của Huấn luyện viên khác");
        }

        // Quy tắc: Chỉ xóa được slot đang AVAILABLE và chưa từng có booking
        if (bookingRepository.findBySlotId(slotId).isPresent()) {
            throw new IllegalArgumentException("Không thể xóa khung giờ đã có học viên đặt lịch");
        }

        if (slot.getStatus() != SlotStatus.AVAILABLE) {
            throw new IllegalArgumentException("Chỉ có thể xóa khung giờ đang ở trạng thái AVAILABLE");
        }

        availabilitySlotRepository.delete(slot);
    }
}
