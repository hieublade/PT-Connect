package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.TopupRequest;
import com.PTconnect.backend.dto.response.PaymentResponse;
import com.PTconnect.backend.dto.response.WalletResponse;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.service.IWalletService;
import com.PTconnect.backend.util.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping({"/api/v1/wallet", "/api/wallet"})
@RequiredArgsConstructor
public class WalletController {

    private final IWalletService walletService;

    private String getCurrentUserEmail(Authentication auth) {
        if (auth == null || !auth.isAuthenticated()) {
            throw new UnauthorizedException("Chưa đăng nhập");
        }
        Object principal = auth.getPrincipal();
        if (principal instanceof User user) {
            return user.getEmail();
        }
        if (principal instanceof String email) {
            return email;
        }
        return auth.getName();
    }

    @GetMapping
    public ResponseEntity<ApiResponse<WalletResponse>> getWallet(Authentication authentication) {
        String email = getCurrentUserEmail(authentication);
        WalletResponse walletResponse = walletService.getWallet(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin ví và lịch sử giao dịch thành công", walletResponse));
    }

    @PostMapping("/topup")
    public ResponseEntity<ApiResponse<PaymentResponse>> topup(
            Authentication authentication,
            @Valid @RequestBody TopupRequest request) {
        String email = getCurrentUserEmail(authentication);
        PaymentResponse paymentResponse = walletService.topup(email, request);
        return ResponseEntity.ok(ApiResponse.success("Nạp tiền vào ví thành công", paymentResponse));
    }
}
