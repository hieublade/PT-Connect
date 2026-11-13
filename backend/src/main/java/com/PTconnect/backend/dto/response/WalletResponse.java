package com.PTconnect.backend.dto.response;

import com.PTconnect.backend.entity.Wallet;
import com.PTconnect.backend.entity.enums.WalletStatus;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class WalletResponse {

    private Long id;
    private Long userId;
    private String ownerName;
    private String ownerEmail;
    private BigDecimal balance;
    private BigDecimal lockedBalance;
    private String currency;
    private WalletStatus status;
    private LocalDateTime updatedAt;
    private List<PaymentResponse> transactions;

    public static WalletResponse fromEntity(Wallet wallet, List<PaymentResponse> transactions) {
        if (wallet == null) {
            return null;
        }

        Long uId = (wallet.getUser() != null) ? wallet.getUser().getId() : null;
        String name = (wallet.getUser() != null) ? wallet.getUser().getFullName() : null;
        String email = (wallet.getUser() != null) ? wallet.getUser().getEmail() : null;

        return WalletResponse.builder()
                .id(wallet.getId())
                .userId(uId)
                .ownerName(name)
                .ownerEmail(email)
                .balance(wallet.getBalance())
                .lockedBalance(wallet.getLockedBalance())
                .currency(wallet.getCurrency())
                .status(wallet.getStatus())
                .updatedAt(wallet.getUpdatedAt())
                .transactions(transactions)
                .build();
    }
}
