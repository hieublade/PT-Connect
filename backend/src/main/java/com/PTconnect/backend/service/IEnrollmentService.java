package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.PurchaseCourseRequest;
import com.PTconnect.backend.dto.response.EnrollmentResponse;

import java.util.List;

public interface IEnrollmentService {

    EnrollmentResponse purchaseCourse(String studentEmail, PurchaseCourseRequest request);

    List<EnrollmentResponse> getMyEnrollments(String studentEmail);

    EnrollmentResponse getEnrollmentById(String userEmail, Long enrollmentId);

    byte[] getContractPdf(String userEmail, Long enrollmentId);
}
