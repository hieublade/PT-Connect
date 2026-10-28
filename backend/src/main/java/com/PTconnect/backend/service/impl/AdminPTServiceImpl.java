package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.response.PendingPTResponse;
import com.PTconnect.backend.dto.response.PTProfileResponse;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.VerificationStatus;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IAdminPTService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AdminPTServiceImpl implements IAdminPTService {

    private final PTProfileRepository ptProfileRepository;
    private final UserRepository userRepository;

    @Override
    @Transactional(readOnly = true)
    public List<PendingPTResponse> getPendingPTs() {
        List<PTProfile> pendingList = ptProfileRepository.findByVerificationStatus(VerificationStatus.PENDING);
        return pendingList.stream()
                .map(PendingPTResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional
    public PTProfileResponse approvePT(Long ptProfileId) {
        PTProfile profile = ptProfileRepository.findById(ptProfileId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ PT với ID: " + ptProfileId));

        profile.approve();
        if (profile.getPt() != null) {
            userRepository.save(profile.getPt());
        }

        PTProfile saved = ptProfileRepository.save(profile);
        return PTProfileResponse.fromEntity(saved);
    }

    @Override
    @Transactional
    public PTProfileResponse rejectPT(Long ptProfileId) {
        PTProfile profile = ptProfileRepository.findById(ptProfileId)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy hồ sơ PT với ID: " + ptProfileId));

        profile.reject();
        if (profile.getPt() != null) {
            userRepository.save(profile.getPt());
        }

        PTProfile saved = ptProfileRepository.save(profile);
        return PTProfileResponse.fromEntity(saved);
    }
}
