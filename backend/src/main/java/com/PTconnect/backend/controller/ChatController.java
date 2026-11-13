package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.ChatMessageRequest;
import com.PTconnect.backend.dto.response.ChatConversationDTO;
import com.PTconnect.backend.dto.response.ChatMessageResponse;
import com.PTconnect.backend.service.IChatService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
public class ChatController {

    private final IChatService chatService;

    @PostMapping("/send")
    public ResponseEntity<ApiResponse<ChatMessageResponse>> sendMessage(
            Authentication auth,
            @Valid @RequestBody ChatMessageRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        ChatMessageResponse response = chatService.sendMessage(email, request);
        return ResponseEntity.ok(ApiResponse.success("Gửi tin nhắn thành công", response));
    }

    @GetMapping("/messages/{partnerId}")
    public ResponseEntity<ApiResponse<List<ChatMessageResponse>>> getChatHistory(
            Authentication auth,
            @PathVariable Long partnerId) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<ChatMessageResponse> messages = chatService.getChatHistory(email, partnerId);
        return ResponseEntity.ok(ApiResponse.success("Lấy lịch sử tin nhắn thành công", messages));
    }

    @GetMapping("/conversations")
    public ResponseEntity<ApiResponse<List<ChatConversationDTO>>> getConversations(
            Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        List<ChatConversationDTO> conversations = chatService.getConversations(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách hội thoại thành công", conversations));
    }

    @PutMapping("/read/{partnerId}")
    public ResponseEntity<ApiResponse<Void>> markAsRead(
            Authentication auth,
            @PathVariable Long partnerId) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        chatService.markAsRead(email, partnerId);
        return ResponseEntity.ok(ApiResponse.success("Đã đánh dấu đã đọc", null));
    }

    @GetMapping("/unread-count")
    public ResponseEntity<ApiResponse<Long>> getUnreadCount(
            Authentication auth) {
        String email = SecurityUtils.getCurrentUserEmail(auth);
        long count = chatService.getUnreadCount(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy số tin chưa đọc thành công", count));
    }
}
