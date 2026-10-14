package com.ptconnect.controller;

import com.ptconnect.dto.response.ApiResponse;
import com.ptconnect.dto.response.SpecializationResponse;
import com.ptconnect.repository.SpecializationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/specializations")
@RequiredArgsConstructor
public class SpecializationController {

    private final SpecializationRepository specializationRepository;

    @GetMapping
    public ApiResponse<List<SpecializationResponse>> getAllSpecializations() {
        List<SpecializationResponse> responses = specializationRepository.findAll().stream()
                .map(s -> SpecializationResponse.builder()
                        .id(s.getId())
                        .name(s.getName())
                        .description(s.getDescription())
                        .build())
                .collect(Collectors.toList());
        return ApiResponse.success(responses);
    }
}