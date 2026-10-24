package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateWorkoutPlanRequest;
import com.PTconnect.backend.dto.request.CreateWorkoutRequest;
import com.PTconnect.backend.dto.response.EnrollmentResponse;
import com.PTconnect.backend.dto.response.WorkoutPlanResponse;
import com.PTconnect.backend.dto.response.WorkoutResponse;

import java.util.List;

public interface IWorkoutPlanService {

    WorkoutPlanResponse createPlan(String ptEmail, CreateWorkoutPlanRequest request);

    WorkoutResponse addWorkout(String ptEmail, Long planId, CreateWorkoutRequest request);

    List<WorkoutPlanResponse> getPlansByEnrollment(String userEmail, Long enrollmentId);

    List<WorkoutPlanResponse> getPlansByPt(String ptEmail);

    List<EnrollmentResponse> getPtEnrollments(String ptEmail);

    void deletePlan(String ptEmail, Long planId);

    void deleteWorkout(String ptEmail, Long planId, Long workoutId);
}
