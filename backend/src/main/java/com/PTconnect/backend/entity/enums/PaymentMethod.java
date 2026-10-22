package com.PTconnect.backend.entity.enums;

import com.fasterxml.jackson.annotation.JsonCreator;

public enum PaymentMethod {
    WALLET,
    BANK_TRANSFER,
    CREDIT_CARD,
    CASH;

    @JsonCreator
    public static PaymentMethod fromString(String value) {
        if (value == null) {
            return BANK_TRANSFER;
        }
        String upper = value.trim().toUpperCase();
        if ("VNPAY".equals(upper) || "MOMO".equals(upper) || "ZALOPAY".equals(upper) || "QR".equals(upper)) {
            return BANK_TRANSFER;
        }
        for (PaymentMethod m : values()) {
            if (m.name().equalsIgnoreCase(upper)) {
                return m;
            }
        }
        return BANK_TRANSFER;
    }
}
