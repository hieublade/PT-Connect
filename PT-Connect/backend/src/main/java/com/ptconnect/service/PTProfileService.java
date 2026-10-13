package com.ptconnect.service;

import com.ptconnect.dto.request.PTProfileUpdateRequest;
import com.ptconnect.dto.response.PTProfileResponse;

import java.util.List;

public interface PTProfileService {
    List<PTProfileResponse> getAllVerifiedPTs(String nameSearch);
    PTProfileResponse getPTProfileById(Long ptId);
    PTProfileResponse updatePTProfile(Long userId, PTProfileUpdateRequest request);
    List<PTProfileResponse> getPendingPTs();
    void approvePT(Long ptId);
}