package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;

import java.util.List;

public interface IAdminPTService {

    List<PendingPTResponse> getPendingPTs();

    PTProfileResponse approvePT(Long ptProfileId);

    PTProfileResponse rejectPT(Long ptProfileId);
}
