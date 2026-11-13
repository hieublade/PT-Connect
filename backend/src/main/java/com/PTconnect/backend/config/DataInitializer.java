package com.PTconnect.backend.config;

import com.PTconnect.backend.entity.AvailabilitySlot;
import com.PTconnect.backend.entity.PTProfile;
import com.PTconnect.backend.entity.enums.SlotStatus;
import com.PTconnect.backend.repository.AvailabilitySlotRepository;
import com.PTconnect.backend.repository.PTProfileRepository;
import com.PTconnect.backend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Tự động đảm bảo dữ liệu chạy mượt mà khi khởi động hệ thống (không dùng Docker):
 * 1. Đảm bảo các PT luôn có khung giờ trống (Available Slots) trong 14 ngày tới.
 * 2. Đảm bảo các tài khoản thử nghiệm có mật khẩu chuẩn (Password123@ / 123456).
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final PTProfileRepository ptProfileRepository;
    private final AvailabilitySlotRepository slotRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public void run(String... args) {
        log.info("===> [PTConnect] Đang kiểm tra và khởi tạo dữ liệu vận hành...");
        ensureFutureSlotsForPTs();
        ensureAccountPasswords();
        log.info("===> [PTConnect] Hệ thống đã sẵn sàng phục vụ!");
    }

    private void ensureFutureSlotsForPTs() {
        List<PTProfile> profiles = ptProfileRepository.findAll();
        LocalDate today = LocalDate.now();

        // 5 ca tập tiêu chuẩn mỗi ngày: 08:00-09:00, 10:00-11:00, 14:00-15:00, 16:00-17:00, 18:00-19:00
        int[][] dailyHours = { {8, 9}, {10, 11}, {14, 15}, {16, 17}, {18, 19} };

        for (PTProfile profile : profiles) {
            List<AvailabilitySlot> futureSlots = slotRepository
                    .findByPtIdAndStatusAndStartTimeAfterOrderByStartTimeAsc(
                            profile.getId(),
                            SlotStatus.AVAILABLE,
                            LocalDateTime.now()
                    );

            if (futureSlots.size() < 10) {
                log.info("===> Tự động tạo thêm khung giờ trống cho HLV ID {}: {}", 
                        profile.getId(), 
                        profile.getPt() != null ? profile.getPt().getFullName() : "PT #" + profile.getId());
                
                List<AvailabilitySlot> slotsToAdd = new ArrayList<>();

                for (int dayOffset = 0; dayOffset <= 14; dayOffset++) {
                    LocalDate targetDate = today.plusDays(dayOffset);
                    for (int[] hours : dailyHours) {
                        LocalDateTime start = LocalDateTime.of(targetDate, LocalTime.of(hours[0], 0));
                        LocalDateTime end = LocalDateTime.of(targetDate, LocalTime.of(hours[1], 0));

                        if (start.isBefore(LocalDateTime.now())) {
                            continue;
                        }

                        List<AvailabilitySlot> overlap = slotRepository.findOverlapping(profile.getId(), start, end, null);
                        if (overlap.isEmpty()) {
                            slotsToAdd.add(AvailabilitySlot.builder()
                                    .pt(profile)
                                    .startTime(start)
                                    .endTime(end)
                                    .status(SlotStatus.AVAILABLE)
                                    .build());
                        }
                    }
                }

                if (!slotsToAdd.isEmpty()) {
                    slotRepository.saveAll(slotsToAdd);
                    log.info("===> Đã bổ sung {} khung giờ trống tương lai cho HLV ID {}", slotsToAdd.size(), profile.getId());
                }
            }
        }
    }

    private void ensureAccountPasswords() {
        String standardPassword = passwordEncoder.encode("Password123@");
        List<String> demoEmails = List.of(
                "admin@ptconnect.vn",
                "pt.hoangc@ptconnect.vn",
                "pt.minhd@ptconnect.vn",
                "student_24@ptconnect.vn",
                "student.a@ptconnect.vn",
                "123@gmail.com",
                "12@gmail.com"
        );

        for (String email : demoEmails) {
            userRepository.findByEmail(email).ifPresent(user -> {
                // Nếu mật khẩu chưa khớp Password123@ và cũng không phải 123456 thì cập nhật để đăng nhập mượt
                if (!passwordEncoder.matches("Password123@", user.getPasswordHash()) &&
                    !passwordEncoder.matches("123456", user.getPasswordHash()) &&
                    !passwordEncoder.matches("123", user.getPasswordHash())) {
                    user.setPasswordHash(standardPassword);
                    userRepository.save(user);
                    log.info("===> Đồng bộ mật khẩu đăng nhập 'Password123@' cho tài khoản: {}", email);
                }
            });
        }
    }
}
