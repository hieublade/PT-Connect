package com.PTconnect.backend.repository;

import com.PTconnect.backend.entity.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, Long> {

    @Query("""
           SELECT m FROM ChatMessage m
           WHERE (m.sender.id = :u1 AND m.recipient.id = :u2)
              OR (m.sender.id = :u2 AND m.recipient.id = :u1)
           ORDER BY m.createdAt ASC
           """)
    List<ChatMessage> findChatHistory(@Param("u1") Long u1, @Param("u2") Long u2);

    @Query("SELECT COUNT(m) FROM ChatMessage m WHERE m.recipient.id = :recipientId AND m.isRead = false")
    long countUnreadTotal(@Param("recipientId") Long recipientId);

    @Query("SELECT COUNT(m) FROM ChatMessage m WHERE m.sender.id = :senderId AND m.recipient.id = :recipientId AND m.isRead = false")
    long countUnreadFromSender(@Param("senderId") Long senderId, @Param("recipientId") Long recipientId);

    @Modifying
    @Query("UPDATE ChatMessage m SET m.isRead = true WHERE m.sender.id = :senderId AND m.recipient.id = :recipientId AND m.isRead = false")
    int markAsRead(@Param("senderId") Long senderId, @Param("recipientId") Long recipientId);

    @Query("""
           SELECT DISTINCT 
             CASE WHEN m.sender.id = :userId THEN m.recipient.id ELSE m.sender.id END
           FROM ChatMessage m
           WHERE m.sender.id = :userId OR m.recipient.id = :userId
           """)
    List<Long> findDistinctPartnerIds(@Param("userId") Long userId);
}
