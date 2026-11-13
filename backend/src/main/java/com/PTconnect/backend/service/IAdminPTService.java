package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.entity.enums.VerificationStatus;

import java.util.List;

public interface IAdminPTService {

    List<PendingPTResponse> getPendingPTs();

    List<PendingPTResponse> getAllPTs(VerificationStatus status);

    PTProfileResponse approvePT(Long ptProfileId);

    PTProfileResponse rejectPT(Long ptProfileId);
}
