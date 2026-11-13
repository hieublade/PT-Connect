package com.PTconnect.backend.service.impl;

import com.PTconnect.backend.dto.request.ChatMessageRequest;
import com.PTconnect.backend.dto.response.ChatConversationDTO;
import com.PTconnect.backend.dto.response.ChatMessageResponse;
import com.PTconnect.backend.entity.Booking;
import com.PTconnect.backend.entity.ChatMessage;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.Role;
import com.PTconnect.backend.exception.ResourceNotFoundException;
import com.PTconnect.backend.repository.BookingRepository;
import com.PTconnect.backend.repository.ChatMessageRepository;
import com.PTconnect.backend.repository.UserRepository;
import com.PTconnect.backend.service.IChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements IChatService {

    private final ChatMessageRepository chatMessageRepository;
    private final UserRepository userRepository;
    private final BookingRepository bookingRepository;

    @Override
    @Transactional
    public ChatMessageResponse sendMessage(String userEmail, ChatMessageRequest request) {
        User sender = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người gửi với email: " + userEmail));

        User recipient = userRepository.findById(request.getRecipientId())
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người nhận với ID: " + request.getRecipientId()));

        if (sender.getId().equals(recipient.getId())) {
            throw new IllegalArgumentException("Không thể tự nhắn tin cho chính mình");
        }

        Booking booking = null;
        if (request.getBookingId() != null) {
            booking = bookingRepository.findById(request.getBookingId()).orElse(null);
        }

        ChatMessage message = ChatMessage.builder()
                .sender(sender)
                .recipient(recipient)
                .booking(booking)
                .content(request.getContent().trim())
                .isRead(false)
                .createdAt(LocalDateTime.now())
                .build();

        ChatMessage saved = chatMessageRepository.save(message);
        return ChatMessageResponse.fromEntity(saved);
    }

    @Override
    @Transactional
    public List<ChatMessageResponse> getChatHistory(String userEmail, Long partnerId) {
        User currentUser = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        // Tự động đánh dấu đã đọc các tin nhắn mà đối phương gửi cho mình
        chatMessageRepository.markAsRead(partnerId, currentUser.getId());

        List<ChatMessage> list = chatMessageRepository.findChatHistory(currentUser.getId(), partnerId);
        return list.stream()
                .map(ChatMessageResponse::fromEntity)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<ChatConversationDTO> getConversations(String userEmail) {
        User currentUser = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng với email: " + userEmail));

        Long currentUserId = currentUser.getId();
        List<Long> partnerIds = chatMessageRepository.findDistinctPartnerIds(currentUserId);
        Set<Long> allPartnerIds = new LinkedHashSet<>(partnerIds);

        // Bổ sung các đối tác từ bookings nếu chưa nhắn tin
        if (currentUser.getRole() == Role.STUDENT) {
            List<Booking> bookings = bookingRepository.findByStudentIdOrderByCreatedAtDesc(currentUserId);
            for (Booking b : bookings) {
                if (b.getSlot() != null && b.getSlot().getPt() != null && b.getSlot().getPt().getPt() != null) {
                    allPartnerIds.add(b.getSlot().getPt().getPt().getId());
                }
            }
        } else if (currentUser.getRole() == Role.PT) {
            // Lấy các học viên đã đặt lịch với PT này
            List<Booking> ptBookings = bookingRepository.findAll();
            for (Booking b : ptBookings) {
                if (b.getSlot() != null && b.getSlot().getPt() != null && b.getSlot().getPt().getPt() != null
                        && b.getSlot().getPt().getPt().getId().equals(currentUserId)) {
                    if (b.getStudent() != null) {
                        allPartnerIds.add(b.getStudent().getId());
                    }
                }
            }
        }

        List<ChatConversationDTO> conversations = new ArrayList<>();
        for (Long pid : allPartnerIds) {
            Optional<User> optPartner = userRepository.findById(pid);
            if (optPartner.isEmpty()) continue;
            User partner = optPartner.get();

            List<ChatMessage> history = chatMessageRepository.findChatHistory(currentUserId, pid);
            String lastMsg = "Bắt đầu cuộc trò chuyện";
            LocalDateTime lastTime = null;
            if (!history.isEmpty()) {
                ChatMessage last = history.get(history.size() - 1);
                lastMsg = last.getContent();
                lastTime = last.getCreatedAt();
            }

            long unread = chatMessageRepository.countUnreadFromSender(pid, currentUserId);

            conversations.add(ChatConversationDTO.builder()
                    .partnerId(partner.getId())
                    .partnerName(partner.getFullName())
                    .partnerEmail(partner.getEmail())
                    .partnerAvatar(partner.getAvatarUrl())
                    .partnerRole(partner.getRole() != null ? partner.getRole().name() : "USER")
                    .lastMessage(lastMsg)
                    .lastMessageTime(lastTime)
                    .unreadCount(unread)
                    .build());
        }

        // Sắp xếp: tin nhắn mới nhất lên đầu
        conversations.sort((a, b) -> {
            if (a.getLastMessageTime() == null && b.getLastMessageTime() == null) return 0;
            if (a.getLastMessageTime() == null) return 1;
            if (b.getLastMessageTime() == null) return -1;
            return b.getLastMessageTime().compareTo(a.getLastMessageTime());
        });

        return conversations;
    }

    @Override
    @Transactional
    public void markAsRead(String userEmail, Long partnerId) {
        User currentUser = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng: " + userEmail));
        chatMessageRepository.markAsRead(partnerId, currentUser.getId());
    }

    @Override
    @Transactional(readOnly = true)
    public long getUnreadCount(String userEmail) {
        User currentUser = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("Không tìm thấy người dùng: " + userEmail));
        return chatMessageRepository.countUnreadTotal(currentUser.getId());
    }
}
