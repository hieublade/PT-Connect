package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.CreateSlotRequest;
import com.PTconnect.backend.dto.response.SlotResponse;

import java.util.List;

public interface IPTSlotService {

    SlotResponse createSlot(String userEmail, CreateSlotRequest request);

    List<SlotResponse> getSlots(String userEmail);

    void deleteSlot(String userEmail, Long slotId);
}
