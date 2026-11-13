package com.PTconnect.backend.dto.response;

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
public class ChatConversationDTO {

    private Long partnerId;
    private String partnerName;
    private String partnerEmail;
    private String partnerAvatar;
    private String partnerRole; // PT hoặc STUDENT
    private String lastMessage;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime lastMessageTime;
    
    private long unreadCount;
}
