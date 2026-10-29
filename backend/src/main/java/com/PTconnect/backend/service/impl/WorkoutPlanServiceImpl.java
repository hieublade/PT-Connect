package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.CreateWorkoutPlanRequest;
import com.PTconnect.backend.dto.request.CreateWorkoutRequest;
import com.PTconnect.backend.dto.response.WorkoutPlanResponse;
import com.PTconnect.backend.dto.response.WorkoutResponse;
import com.PTconnect.backend.entity.*;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.exception.BadRequestException;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.repository.*;
import com.PTconnect.backend.service.IWorkoutPlanService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class WorkoutPlanServiceImpl implements IWorkoutPlanService {

    private final WorkoutPlanRepository workoutPlanRepository;
    private final WorkoutRepository workoutRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final PTProfileRepository ptProfileRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional
    public WorkoutPlanResponse createPlan(String ptEmail, CreateWorkoutPlanRequest request) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có quyền tạo giáo án"));

        Enrollment enrollment = enrollmentRepository.findById(request.getEnrollmentId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng khóa học với ID: " + request.getEnrollmentId()));

        if (!enrollment.getPt().getId().equals(ptProfile.getId())) {
            throw new UnauthorizedException("Bạn không phải là Huấn luyện viên phụ trách hợp đồng này");
        }

        LocalDate start = request.getStartDate() != null ? request.getStartDate() : enrollment.getStartDate();
        LocalDate end = request.getEndDate() != null ? request.getEndDate() : enrollment.getEndDate();
        if (start == null) {
            start = LocalDate.now();
        }
        if (end == null) {
            end = start.plusWeeks(4);
        }

        if (start.isAfter(end)) {
            throw new BadRequestException("Ngày bắt đầu giáo án không thể sau ngày kết thúc");
        }

        WorkoutPlan plan = WorkoutPlan.builder()
                .enrollment(enrollment)
                .pt(ptProfile)
                .title(request.getTitle())
                .goal(request.getGoal())
                .startDate(start)
                .endDate(end)
                .build();

        WorkoutPlan savedPlan = workoutPlanRepository.save(plan);
        return WorkoutPlanResponse.fromEntity(savedPlan);
    }

    @Override
    @Transactional
    public WorkoutResponse addWorkout(String ptEmail, Long planId, CreateWorkoutRequest request) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có quyền thêm bài tập"));

        WorkoutPlan plan = workoutPlanRepository.findById(planId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy giáo án với ID: " + planId));

        if (!plan.getPt().getId().equals(ptProfile.getId())) {
            throw new UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này");
        }

        Workout workout = Workout.builder()
                .plan(plan)
                .exerciseName(request.getExerciseName())
                .targetMuscle(request.getTargetMuscle())
                .sets(request.getSets())
                .reps(request.getReps())
                .weightKg(request.getWeightKg())
                .restSeconds(request.getRestSeconds())
                .videoDemoUrl(request.getVideoDemoUrl())
                .build();

        Workout savedWorkout = workoutRepository.save(workout);
        return WorkoutResponse.fromEntity(savedWorkout);
    }

    @Override
    @Transactional(readOnly = true)
    public List<WorkoutPlanResponse> getPlansByEnrollment(String userEmail, Long enrollmentId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new UnauthorizedException("Chưa đăng nhập"));

        Enrollment enrollment = enrollmentRepository.findById(enrollmentId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hợp đồng khóa học với ID: " + enrollmentId));

        // Phân quyền: Học viên của hợp đồng, PT của hợp đồng, hoặc ADMIN mới được xem
        boolean isStudent = enrollment.getStudent().getId().equals(user.getId());
        boolean isPt = enrollment.getPt().getPt().getId().equals(user.getId());
        boolean isAdmin = user.getRole() == Role.ADMIN;

        if (!isStudent && !isPt && !isAdmin) {
            throw new UnauthorizedException("Bạn không có quyền xem giáo án của hợp đồng này");
        }

        return workoutPlanRepository.findByEnrollmentIdOrderByCreatedAtDesc(enrollmentId).stream()
                .map(WorkoutPlanResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<WorkoutPlanResponse> getPlansByPt(String ptEmail) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có danh sách giáo án"));

        return workoutPlanRepository.findByPtIdOrderByCreatedAtDesc(ptProfile.getId()).stream()
                .map(WorkoutPlanResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public void deletePlan(String ptEmail, Long planId) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xóa giáo án"));

        WorkoutPlan plan = workoutPlanRepository.findById(planId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy giáo án với ID: " + planId));

        if (!plan.getPt().getId().equals(ptProfile.getId())) {
            throw new UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này");
        }

        workoutRepository.deleteByPlanId(planId);
        workoutPlanRepository.delete(plan);
    }

    @Override
    @Transactional
    public void deleteWorkout(String ptEmail, Long planId, Long workoutId) {
        PTProfile ptProfile = ptProfileRepository.findByPtEmail(ptEmail)
                .orElseThrow(() -> new UnauthorizedException("Chỉ Huấn luyện viên mới có quyền xóa bài tập"));

        WorkoutPlan plan = workoutPlanRepository.findById(planId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy giáo án với ID: " + planId));

        if (!plan.getPt().getId().equals(ptProfile.getId())) {
            throw new UnauthorizedException("Bạn không phải là Huấn luyện viên của giáo án này");
        }

        Workout workout = workoutRepository.findById(workoutId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy bài tập với ID: " + workoutId));

        if (!workout.getPlan().getId().equals(planId)) {
            throw new BadRequestException("Bài tập không thuộc giáo án này");
        }

        workoutRepository.delete(workout);
    }
}


