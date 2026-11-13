package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.ArbitrationVerdictRequest;
import com.PTconnect.backend.dto.request.CreateDisputeRequest;
import com.PTconnect.backend.dto.response.DisputeResponse;

import java.util.List;

public interface IDisputeService {

    DisputeResponse createDispute(String callerEmail, CreateDisputeRequest request);

    List<DisputeResponse> getAllDisputes();

    List<DisputeResponse> getMyDisputes(String callerEmail);

    DisputeResponse issueVerdict(String adminEmail, Long disputeId, ArbitrationVerdictRequest request);

    DisputeResponse submitCounterStatement(String callerEmail, Long disputeId, String counterStatement);
}
