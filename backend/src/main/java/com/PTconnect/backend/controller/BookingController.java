package com.PTconnect.backend.controller;

import com.PTconnect.backend.dto.request.CreateBookingRequest;
import com.PTconnect.backend.dto.request.RejectBookingRequest;
import com.PTconnect.backend.dto.response.BookingResponse;
import com.PTconnect.backend.entity.User;
import com.PTconnect.backend.entity.enums.BookingStatus;
import com.PTconnect.backend.exception.UnauthorizedException;
import com.PTconnect.backend.service.IBookingService;
import com.PTconnect.backend.util.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Controller phục vụ toàn bộ luồng Booking ca tập (Milestone 6).
 * Phụ trách bởi: Huy & Hưng.
 */
@RestController
@RequiredArgsConstructor
public class BookingController {

    private final IBookingService bookingService;

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

    // -------------------------------------------------------------
    // 1. Phía Học viên (Student Booking Endpoints)
    // -------------------------------------------------------------

    @PostMapping({"/api/v1/bookings", "/api/bookings"})
    public ResponseEntity<ApiResponse<BookingResponse>> createBooking(
            Authentication authentication,
            @Valid @RequestBody CreateBookingRequest request) {
        String email = getCurrentUserEmail(authentication);
        BookingResponse response = bookingService.createBooking(email, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Đặt lịch ca tập thành công (chờ Huấn luyện viên phê duyệt)", response));
    }

    @GetMapping({"/api/v1/bookings/my", "/api/bookings/my"})
    public ResponseEntity<ApiResponse<List<BookingResponse>>> getMyBookings(
            Authentication authentication,
            @RequestParam(required = false) BookingStatus status) {
        String email = getCurrentUserEmail(authentication);
        List<BookingResponse> bookings = bookingService.getMyBookings(email, status);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách lịch tập của tôi thành công", bookings));
    }

    @GetMapping({"/api/v1/bookings/{id}", "/api/bookings/{id}"})
    public ResponseEntity<ApiResponse<BookingResponse>> getBookingById(
            Authentication authentication,
            @PathVariable Long id) {
        String email = getCurrentUserEmail(authentication);
        BookingResponse booking = bookingService.getBookingById(email, id);
        return ResponseEntity.ok(ApiResponse.success("Lấy thông tin chi tiết đơn đặt lịch thành công", booking));
    }

    // -------------------------------------------------------------
    // 2. Phía Huấn luyện viên (PT Booking Endpoints)
    // -------------------------------------------------------------

    @GetMapping({"/api/v1/pt/bookings", "/api/pt/bookings"})
    public ResponseEntity<ApiResponse<List<BookingResponse>>> getPTBookings(
            Authentication authentication,
            @RequestParam(required = false) BookingStatus status) {
        String email = getCurrentUserEmail(authentication);
        List<BookingResponse> bookings = bookingService.getPTBookings(email, status);
        return ResponseEntity.ok(ApiResponse.success("Lấy danh sách đơn đặt lịch thành công", bookings));
    }

    @PutMapping({"/api/v1/pt/bookings/{id}/confirm", "/api/pt/bookings/{id}/confirm"})
    public ResponseEntity<ApiResponse<BookingResponse>> confirmBooking(
            Authentication authentication,
            @PathVariable Long id) {
        String email = getCurrentUserEmail(authentication);
        BookingResponse response = bookingService.confirmBooking(email, id);
        return ResponseEntity.ok(ApiResponse.success("Xác nhận ca tập thành công", response));
    }

    @PutMapping({"/api/v1/pt/bookings/{id}/reject", "/api/pt/bookings/{id}/reject"})
    public ResponseEntity<ApiResponse<BookingResponse>> rejectBooking(
            Authentication authentication,
            @PathVariable Long id,
            @RequestBody(required = false) RejectBookingRequest request) {
        String email = getCurrentUserEmail(authentication);
        if (request == null) {
            request = RejectBookingRequest.builder().reason("Huấn luyện viên bận đột xuất").build();
        }
        BookingResponse response = bookingService.rejectBooking(email, id, request);
        return ResponseEntity.ok(ApiResponse.success("Đã từ chối đơn đặt lịch và hoàn lại buổi tập", response));
    }
}
