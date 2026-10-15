package com.PTconnect.backend.entity;

import com.PTconnect.backend.entity.enums.WalletStatus;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "wallets")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Wallet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    private User user;

    // Không có setter: chỉ đổi số dư qua credit()/debit()
    @Setter(AccessLevel.NONE)
    @Column(nullable = false, precision = 14, scale = 2)
    @Builder.Default
    private BigDecimal balance = BigDecimal.ZERO;

    @Setter(AccessLevel.NONE)
    @Column(name = "locked_balance", nullable = false, precision = 14, scale = 2)
    @Builder.Default
    private BigDecimal lockedBalance = BigDecimal.ZERO;

    @Column(nullable = false, length = 10)
    @Builder.Default
    private String currency = "VND";

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    @Builder.Default
    private WalletStatus status = WalletStatus.ACTIVE;

    @Column(name = "updated_at", insertable = false, updatable = false)
    private LocalDateTime updatedAt;

    // Đóng gói: quy tắc nghiệp vụ nằm trong Entity
    public void credit(BigDecimal amount) {
        checkUsable(amount);
        this.balance = this.balance.add(amount);
    }

    public void debit(BigDecimal amount) {
        checkUsable(amount);
        if (this.balance.compareTo(amount) < 0) {
            throw new IllegalStateException("Số dư không đủ");
        }
        this.balance = this.balance.subtract(amount);
    }

    private void checkUsable(BigDecimal amount) {
        if (this.status != WalletStatus.ACTIVE) {
            throw new IllegalStateException("Ví đang bị đóng băng");
        }
        if (amount == null || amount.signum() <= 0) {
            throw new IllegalArgumentException("Số tiền phải lớn hơn 0");
        }
    }
}