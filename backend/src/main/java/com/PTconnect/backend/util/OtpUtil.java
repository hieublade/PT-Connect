package com.PTconnect.backend.util;

import org.springframework.stereotype.Component;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Tiện ích sinh và xác thực mã OTP 6 số phục vụ điểm danh ca tập (Milestone 7).
 * Được quản lý trong bộ nhớ (Thread-safe ConcurrentHashMap) có thời hạn hiệu lực.
 */
@Component
public class OtpUtil {

    private static final SecureRandom RANDOM = new SecureRandom();
    private static final int DEFAULT_EXPIRY_MINUTES = 30;

    public record OtpEntry(String code, LocalDateTime expiresAt) {
        public boolean isExpired() {
            return LocalDateTime.now().isAfter(expiresAt);
        }
    }

    private final Map<Long, OtpEntry> otpStorage = new ConcurrentHashMap<>();

    /**
     * Sinh mã OTP 6 chữ số ngẫu nhiên cho một ca đặt lịch (Booking).
     */
    public String generateOtp(Long bookingId) {
        return generateOtp(bookingId, DEFAULT_EXPIRY_MINUTES);
    }

    /**
     * Sinh mã OTP 6 chữ số ngẫu nhiên với thời hạn tùy chỉnh (phút).
     */
    public String generateOtp(Long bookingId, int expiryMinutes) {
        int number = 100000 + RANDOM.nextInt(900000);
        String code = String.valueOf(number);
        LocalDateTime expiresAt = LocalDateTime.now().plusMinutes(expiryMinutes);

        otpStorage.put(bookingId, new OtpEntry(code, expiresAt));
        return code;
    }

    /**
     * Lấy thông tin OTP hiện tại của booking nếu còn hiệu lực.
     */
    public OtpEntry getActiveOtp(Long bookingId) {
        OtpEntry entry = otpStorage.get(bookingId);
        if (entry != null && !entry.isExpired()) {
            return entry;
        }
        if (entry != null && entry.isExpired()) {
            otpStorage.remove(bookingId);
        }
        return null;
    }

    /**
     * Kiểm tra tính hợp lệ của mã OTP do học viên nhập.
     * Trả về true nếu mã trùng khớp và còn trong thời hạn hiệu lực.
     */
    public boolean validateOtp(Long bookingId, String inputOtp) {
        if (bookingId == null || inputOtp == null || inputOtp.isBlank()) {
            return false;
        }

        OtpEntry entry = otpStorage.get(bookingId);
        if (entry == null) {
            return false;
        }

        if (entry.isExpired()) {
            otpStorage.remove(bookingId);
            return false;
        }

        return entry.code().equals(inputOtp.trim());
    }

    /**
     * Xóa mã OTP sau khi điểm danh thành công hoặc hủy.
     */
    public void clearOtp(Long bookingId) {
        if (bookingId != null) {
            otpStorage.remove(bookingId);
        }
    }
}
