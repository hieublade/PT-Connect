package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateWorkoutPlanRequest;
import com.PTconnect.backend.dto.request.CreateWorkoutRequest;
import com.PTconnect.backend.dto.response.WorkoutPlanResponse;
import com.PTconnect.backend.dto.response.WorkoutResponse;
import com.PTconnect.backend.service.IWorkoutPlanService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping({"/api/v1", "/api"})
@RequiredArgsConstructor
public class WorkoutPlanController {

    private final IWorkoutPlanService workoutPlanService;

    @PostMapping("/pt/workout-plans")
    public ResponseEntity<ApiResponse<WorkoutPlanResponse>> createPlan(
            Authentication auth,
            @Valid @RequestBody CreateWorkoutPlanRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        WorkoutPlanResponse response = workoutPlanService.createPlan(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Tạo giáo án luyện tập thành công", response));
    }

    @PostMapping("/pt/workout-plans/{id}/workouts")
    public ResponseEntity<ApiResponse<WorkoutResponse>> addWorkout(
            Authentication auth,
            @PathVariable Long id,
            @Valid @RequestBody CreateWorkoutRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        WorkoutResponse response = workoutPlanService.addWorkout(email, id, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Thêm bài tập vào giáo án thành công", response));
    }

    @GetMapping("/enrollments/{id}/workout-plans")
    public ResponseEntity<ApiResponse<List<WorkoutPlanResponse>>> getPlansByEnrollment(
            Authentication auth,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<WorkoutPlanResponse> plans = workoutPlanService.getPlansByEnrollment(email, id);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách giáo án của hợp đồng thành công", plans));
    }

    @GetMapping("/pt/workout-plans")
    public ResponseEntity<ApiResponse<List<WorkoutPlanResponse>>> getPlansByPt(Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<WorkoutPlanResponse> plans = workoutPlanService.getPlansByPt(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách giáo án đã tạo thành công", plans));
    }

    @DeleteMapping("/pt/workout-plans/{id}")
    public ResponseEntity<ApiResponse<Void>> deletePlan(
            Authentication auth,
            @PathVariable Long id) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        workoutPlanService.deletePlan(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xóa giáo án thành công", null));
    }

    @DeleteMapping("/pt/workout-plans/{planId}/workouts/{workoutId}")
    public ResponseEntity<ApiResponse<Void>> deleteWorkout(
            Authentication auth,
            @PathVariable Long planId,
            @PathVariable Long workoutId) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        workoutPlanService.deleteWorkout(email, planId, workoutId);
        return ResponseEntity.ok(ApiResponse.success("Xóa bài tập khỏi giáo án thành công", null));
    }
}

