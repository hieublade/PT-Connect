package com.PTconnect.backend.service;

import com.PTconnect.backend.dto.request.TopupRequest;
import com.PTconnect.backend.dto.response.PaymentResponse;
import com.PTconnect.backend.dto.response.WalletResponse;

public interface IWalletService {

    WalletResponse getWallet(String userEmail);

    PaymentResponse topup(String userEmail, TopupRequest request);
}
