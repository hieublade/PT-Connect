package com.ptconnect.controller;

import com.ptconnect.dto.request.PTProfileUpdateRequest;
import com.ptconnect.dto.response.ApiResponse;
import com.ptconnect.dto.response.PTProfileResponse;
import com.ptconnect.service.PTProfileService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/pt-profiles")
@RequiredArgsConstructor
public class PTProfileController {

    private final PTProfileService ptProfileService;

    @GetMapping
    public ApiResponse<List<PTProfileResponse>> getAllPTs(@RequestParam(required = false) String name) {
        return ApiResponse.success(ptProfileService.getAllVerifiedPTs(name));
    }

    @GetMapping("/{id}")
    public ApiResponse<PTProfileResponse> getPTById(@PathVariable Long id) {
        return ApiResponse.success(ptProfileService.getPTProfileById(id));
    }

    @PutMapping("/me")
    public ApiResponse<PTProfileResponse> updateProfile(@RequestHeader("X-User-Id") Long userId,
                                                        @Valid @RequestBody PTProfileUpdateRequest request) {
        return ApiResponse.success(ptProfileService.updatePTProfile(userId, request));
    }
}