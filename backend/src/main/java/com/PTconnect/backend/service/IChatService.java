package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.ChatMessageRequest;
import com.PTconnect.backend.dto.response.ChatConversationDTO;
import com.PTconnect.backend.dto.response.ChatMessageResponse;

import java.util.List;

public interface IChatService {

    ChatMessageResponse sendMessage(String userEmail, ChatMessageRequest request);

    List<ChatMessageResponse> getChatHistory(String userEmail, Long partnerId);

    List<ChatConversationDTO> getConversations(String userEmail);

    void markAsRead(String userEmail, Long partnerId);

    long getUnreadCount(String userEmail);
}
