package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.TopupRequest;
import com.PTconnect.backend.dto.response.PaymentResponse;
import com.PTconnect.backend.dto.response.WalletResponse;
import com.PTconnect.backend.service.IWalletService;
import com.PTconnect.backend.util.ApiResponse;
import com.PTconnect.backend.util.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/wallet")
@RequiredArgsConstructor
public class WalletController {

    private final IWalletService walletService;

    @GetMapping
    public ResponseEntity<ApiResponse<WalletResponse>> getWallet(Authentication authentication) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        WalletResponse walletResponse = walletService.getWallet(email);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin ví và lịch sử giao dịch thành công", walletResponse));
    }

    @PostMapping("/topup")
    public ResponseEntity<ApiResponse<PaymentResponse>> topup(
            Authentication authentication,
            @Valid @RequestBody TopupRequest request) {
        String email = SecurityUtils.getCurrentUserEmail(authentication);
        PaymentResponse paymentResponse = walletService.topup(email, request);
        return ResponseEntity.ok(ApiResponse.success("Nạp tiền vào ví thành công", paymentResponse));
    }
}
