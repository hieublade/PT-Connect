package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateCourseRequest;
import com.PTconnect.backend.dto.request.UpdateCourseRequest;
import com.PTconnect.backend.dto.response.CourseResponse;

import java.util.List;

public interface IPTCourseService {

    CourseResponse createCourse(String userEmail, CreateCourseRequest request);

    List<CourseResponse> getCourses(String userEmail);

    CourseResponse updateCourse(String userEmail, Long courseId, UpdateCourseRequest request);

    void deleteCourse(String userEmail, Long courseId);
}
