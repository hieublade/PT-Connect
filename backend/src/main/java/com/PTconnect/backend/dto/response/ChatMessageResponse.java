package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.ChatMessage;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessageResponse {

    private Long id;
    private Long senderId;
    private String senderName;
    private String senderAvatar;
    private Long recipientId;
    private String recipientName;
    private String recipientAvatar;
    private String content;
    private Boolean isRead;
    private Long bookingId;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime createdAt;

    public static ChatMessageResponse fromEntity(ChatMessage m) {
        if (m == null) return null;
        return ChatMessageResponse.builder()
                .id(m.getId())
                .senderId(m.getSender() != null ? m.getSender().getId() : null)
                .senderName(m.getSender() != null ? m.getSender().getFullName() : null)
                .senderAvatar(m.getSender() != null ? m.getSender().getAvatarUrl() : null)
                .recipientId(m.getRecipient() != null ? m.getRecipient().getId() : null)
                .recipientName(m.getRecipient() != null ? m.getRecipient().getFullName() : null)
                .recipientAvatar(m.getRecipient() != null ? m.getRecipient().getAvatarUrl() : null)
                .content(m.getContent())
                .isRead(m.getIsRead())
                .bookingId(m.getBooking() != null ? m.getBooking().getId() : null)
                .createdAt(m.getCreatedAt())
                .build();
    }
}
