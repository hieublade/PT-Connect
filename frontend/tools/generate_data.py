#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sinh dữ liệu mẫu toàn diện cho nền tảng PT Connect (Milestone 8 - Output 4).
Tuân thủ toàn bộ các ràng buộc CHECK, UNIQUE, FK, BCNF và Trigger trong database/init.sql & trigger.sql.

Dữ liệu bao phủ mọi ngóc ngách chức năng:
- 1 Quản trị viên (ADMIN)
- 50 Huấn luyện viên (PT) chia thành 8 nhóm chuyên môn phục vụ test tìm kiếm & lọc:
    1. Tăng cơ & Thể hình (Bodybuilding & Hypertrophy)
    2. Giảm cân cấp tốc & HIIT (Weight Loss & Cardio)
    3. Calisthenics & Thể hình tự thân (Bodyweight & Street Workout)
    4. Powerlifting & Sức mạnh tạ nặng (Strength & Heavy Lifting)
    5. Yoga & Pilates chỉnh dáng, thon gọn (Yoga, Pilates & Posture)
    6. Boxing, Kickfit & Muay Thái (Combat Conditioning)
    7. Phục hồi chức năng & Đau vai gáy, Cột sống (Rehabilitation & Spine)
    8. Dinh dưỡng & Thể thao học đường (Nutrition & Special Populations)
  Trạng thái PT: 45 VERIFIED/ACTIVE, 3 PENDING (test duyệt hồ sơ), 2 REJECTED/SUSPENDED.
- 15 Học viên (STUDENT): Học viên chính (student_minhanh@gmail.com / student.a@ptconnect.vn)
- 70+ Khóa học đa dạng giá từ 2.400.000đ đến 12.600.000đ
- 600+ Khung giờ rảnh (Availability Slots) trải đều các ca sáng/trưa/tối
- Hợp đồng (Enrollments): ACTIVE, COMPLETED, EXPIRED
- Ca đặt lịch (Bookings): PENDING, CONFIRMED, COMPLETED, CANCELLED
- Điểm danh (Attendance) & Đánh giá (Reviews) cho các ca COMPLETED
- Lịch sử hủy ca (Cancellations) kèm lý do và bên hủy (Student / PT)
- Khiếu nại (Booking Disputes): PENDING, EVIDENCE_REQUESTED, RESOLVED_REFUND
- Giáo án & Bài tập (Workout Plans & Workouts) có thứ tự exercise_order chuẩn 1..N
- Giao dịch tài chính (Payments) & Sổ cái biến động (Wallet Audit Logs)
- Tin nhắn trao đổi (Chat Messages)
"""

import os
import sys
import random
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SEED = 42
random.seed(SEED)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_FILES = [
    os.path.join(PROJECT_ROOT, "database", "seed_demo.sql"),
]

def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "1" if val else "0"
    s = str(val).replace("\\", "\\\\").replace("'", "''")
    return f"'{s}'"

def main():
    print(f"Bắt đầu sinh dữ liệu mẫu 50 PT & đầy đủ chức năng cho PT Connect (Seed: {SEED})...")

    password_plain = "Password123@"
    password_hash = "$2b$10$/M8YC0N1J98TLXyEp2nElOlRYtF2vNuQK.J0cBFlU6syj7Wf1ROaK"

    sql_lines = []
    sql_lines.append("-- =====================================================================")
    sql_lines.append("-- DỮ LIỆU MẪU CHẠY DEMO HỆ THỐNG PT CONNECT (50 PTs & ĐẦY ĐỦ CÁC MỤC NGHIỆP VỤ)")
    sql_lines.append(f"-- Sinh tự động ngày: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_lines.append("-- Mật khẩu đăng nhập mặc định cho TẤT CẢ tài khoản: Password123@")
    sql_lines.append("-- =====================================================================")
    sql_lines.append("USE ptconnect;")
    sql_lines.append("SET NAMES utf8mb4;")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    sql_lines.append("")
    sql_lines.append("TRUNCATE TABLE `chat_messages`;")
    sql_lines.append("TRUNCATE TABLE `attendance`;")
    sql_lines.append("TRUNCATE TABLE `booking_disputes`;")
    sql_lines.append("TRUNCATE TABLE `cancellations`;")
    sql_lines.append("TRUNCATE TABLE `reviews`;")
    sql_lines.append("TRUNCATE TABLE `workouts`;")
    sql_lines.append("TRUNCATE TABLE `workout_plans`;")
    sql_lines.append("TRUNCATE TABLE `bookings`;")
    sql_lines.append("TRUNCATE TABLE `availability_slots`;")
    sql_lines.append("TRUNCATE TABLE `payments`;")
    sql_lines.append("TRUNCATE TABLE `wallet_audit_logs`;")
    sql_lines.append("TRUNCATE TABLE `enrollments`;")
    sql_lines.append("TRUNCATE TABLE `courses`;")
    sql_lines.append("TRUNCATE TABLE `wallets`;")
    sql_lines.append("TRUNCATE TABLE `pt_locations`;")
    sql_lines.append("TRUNCATE TABLE `pt_profiles`;")
    sql_lines.append("TRUNCATE TABLE `users`;")
    sql_lines.append("")
    sql_lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    sql_lines.append("")

    # =========================================================================
    # 1. USERS & WALLETS & PT PROFILES (50 PTs)
    # =========================================================================
    users = []
    wallets = []
    pt_profiles = []
    user_id_seq = 1

    # 1.1 Admin Hệ Thống
    users.append({
        "id": user_id_seq,
        "full_name": "Quản Trị Viên Hệ Thống",
        "email": "admin@ptconnect.vn",
        "password_hash": password_hash,
        "phone": "0900000000",
        "role": "ADMIN",
        "status": "ACTIVE",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=AdminSystem"
    })
    wallets.append({"id": user_id_seq, "user_id": user_id_seq, "balance": 28500000.0, "locked_balance": 0.0})
    user_id_seq += 1

    # 1.2 Danh sách 50 PT với 8 nhóm chuyên môn rõ ràng
    pt_raw_configs = [
        # Nhóm 1: Tăng cơ & Thể hình (Bodybuilding & Hypertrophy) - 7 PTs
        ("Lê Hoàng Cường", "pt.hoangc@ptconnect.vn", "0901000001", 6, "VERIFIED", "ACTIVE",
         "HLV Thể hình chuyên nghiệp & Tăng cơ chuyên sâu. Đạt chứng chỉ NASM CPT quốc tế.",
         "Tăng cơ, Giảm mỡ, Thể hình, Dinh dưỡng thể thao",
         ["Phòng Cali Cầu Giấy", "FitZone Thanh Xuân"], "Dạy tại nhà phụ thu 20% tiền đi lại",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Nguyễn Hoàng Nam", "pt.hoangnam@ptconnect.vn", "0901000002", 5, "VERIFIED", "ACTIVE",
         "Cựu vận động viên Men Physique quốc gia, chuyên coaching tăng kích thước cơ bắp và định hình cơ thể săn chắc.",
         "Tăng cơ Hypertrophy, Siết mỡ, Thể hình nam nữ",
         ["Cầu Giấy", "Nam Từ Liêm"], "Hỗ trợ học viên đo InBody định kỳ hàng tuần",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Đặng Quốc Huy", "pt.quochuy@ptconnect.vn", "0901000003", 7, "VERIFIED", "ACTIVE",
         "Hơn 7 năm dẫn dắt hàng trăm học viên cải thiện vóc dáng từ gầy ốm sang cơ bắp vạm vỡ.",
         "Thể hình chuyên sâu, Tăng cơ không mỡ, Dinh dưỡng macro",
         ["Thanh Xuân", "Hà Đông"], "Cam kết đạt mục tiêu nếu theo sát thực đơn",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Bùi Anh Dũng", "pt.anhdung@ptconnect.vn", "0901000004", 4, "VERIFIED", "ACTIVE",
         "Chuyên phương pháp tập luyện Push-Pull-Legs tối ưu tăng cơ toàn diện.",
         "Tăng cơ thể hình, Cắt nét cơ bụng, Tăng cân cho nam",
         ["Đống Đa", "Ba Đình"], "Giáo án cá nhân hóa theo từng buổi",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Trần Đình Trọng", "pt.dinhtrong.bb@ptconnect.vn", "0901000005", 8, "VERIFIED", "ACTIVE",
         "Huấn luyện viên thể hình thi đấu, kèm cặp siết cơ thi đấu và tạo khối cơ sắc nét.",
         "Thể hình thi đấu, Siết cơ chuyên sâu, Bulking & Cutting",
         ["Hai Bà Trưng", "Hoàn Kiếm"], "Kèm 1-1 chuyên sâu",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Nguyễn Văn Hùng", "pt.vanhung@ptconnect.vn", "0901000006", 5, "VERIFIED", "ACTIVE",
         "Tập trung cải thiện ngực, vai, lưng xô chữ V cho học viên nam văn phòng.",
         "Tăng cơ thân trên, Lưng xô chữ V, Ngực nở vai rộng",
         ["Tây Hồ", "Cầu Giấy"], "Có phòng gym liên kết cao cấp",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Vũ Đức Thành", "pt.ducthanh@ptconnect.vn", "0901000007", 3, "VERIFIED", "ACTIVE",
         "Phương pháp tập tạ khoa học, không dùng thực phẩm chức năng tràn lan.",
         "Tăng cơ tự nhiên, Thể hình cơ bản, Form tạ chuẩn",
         ["Bắc Từ Liêm", "Nam Từ Liêm"], "Linh hoạt lịch tập tối",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),

        # Nhóm 2: Giảm cân cấp tốc & HIIT (Weight Loss & Cardio) - 6 PTs
        ("Trần Tuấn Anh", "pt.tuananh@ptconnect.vn", "0901000008", 4, "VERIFIED", "ACTIVE",
         "Huấn luyện viên thể lực năng động, chuyên giáo án cường độ cao đốt mỡ và tăng cường sức bền hệ tuần hoàn.",
         "Giảm mỡ cấp tốc, HIIT, Thể lực toàn thân",
         ["Đống Đa", "Ba Đình"], "Tặng kèm thực đơn giảm cân 4 tuần",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Vũ Minh Quân", "pt.minhquan@ptconnect.vn", "0901000009", 3, "VERIFIED", "ACTIVE",
         "Tận tâm, kiên nhẫn, chuyên các bài tập bảo vệ khớp gối cho người có chỉ số BMI cao muốn giảm cân an toàn.",
         "Giảm mỡ bụng, Chỉnh tư thế cho người thừa cân, Tim mạch",
         ["Hai Bà Trưng", "Hoàn Kiếm"], "Khởi động kỹ và kiểm tra tim mạch trước mỗi buổi",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Nguyễn Thị Mai", "pt.thimai@ptconnect.vn", "0901000010", 5, "VERIFIED", "ACTIVE",
         "Chuyên giảm mỡ toàn thân cho nữ giới, siết eo và đùi bằng Tabata và tạ chuông Kettlebell.",
         "Giảm mỡ nữ, Tabata, Kettlebell, Đốt mỡ thừa",
         ["Cầu Giấy", "Thanh Xuân"], "Kèm sát thực đơn ăn uống mỗi bữa",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Đỗ Phương Thảo", "pt.phuongthao.wl@ptconnect.vn", "0901000011", 4, "VERIFIED", "ACTIVE",
         "Giảm cân khoa học không nhịn ăn, kết hợp Cardio ngắt quãng và bài tập kháng lực.",
         "Giảm cân không nhịn ăn, Cardio ngắt quãng, Eat Clean",
         ["Tây Hồ", "Ba Đình"], "Theo dõi chỉ số mỡ nội tạng hàng tuần",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Lê Hải Yến", "pt.haiyen@ptconnect.vn", "0901000012", 3, "VERIFIED", "ACTIVE",
         "Chuyên giúp các bạn trẻ giảm từ 5 - 10kg mỡ thừa trong 8 đến 12 tuần an toàn.",
         "Giảm mỡ sinh viên, Vóc dáng thon thả, Cardio vui vẻ",
         ["Hoàng Mai", "Thanh Xuân"], "Học phí ưu đãi cho sinh viên",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Phạm Thanh Tùng", "pt.thanhtung@ptconnect.vn", "0901000013", 6, "VERIFIED", "ACTIVE",
         "Huấn luyện viên Bootcamp thể lực ngoài trời, đốt cháy tối đa calo mỗi buổi tập.",
         "Bootcamp ngoài trời, Thể lực sức bền, Giảm mỡ siêu tốc",
         ["Công viên Cầu Giấy", "Công viên Thống Nhất"], "Tập nhóm nhỏ hoặc cá nhân",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),

        # Nhóm 3: Calisthenics & Thể hình tự thân (Bodyweight & Street Workout) - 6 PTs
        ("Phạm Minh Dũng", "pt.minhd@ptconnect.vn", "0901000014", 4, "VERIFIED", "ACTIVE",
         "Huấn luyện viên Calisthenics và chỉnh sửa tư thế cột sống, cải thiện gù lưng đau mỏi vai gáy cho dân công sở.",
         "Calisthenics, Chỉnh sửa tư thế, Tăng thể lực, Đau vai gáy",
         ["Khu vực Đống Đa", "Studio cá nhân tại Thanh Xuân"], "Dụng cụ xà và vòng treo mang theo tận nơi",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Bùi Thế Long", "pt.thelong@ptconnect.vn", "0901000015", 5, "VERIFIED", "ACTIVE",
         "Chuyên gia kỹ thuật Handstand (trồng chuối) và Muscle Up. Hướng dẫn kiểm soát nhóm cơ cốt lõi (Core) hoàn hảo.",
         "Calisthenics nâng cao, Muscle Up, Handstand, Giãn cơ",
         ["Tây Hồ", "Cầu Giấy"], "Phù hợp cả người mới tập từ hít xà cơ bản",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Hoàng Khắc Tiệp", "pt.khactiep@ptconnect.vn", "0901000016", 3, "VERIFIED", "ACTIVE",
         "Tập luyện ngoài trời hoặc tại nhà không cần tạ, tối ưu sức mạnh dẻo dai và phản xạ cơ bắp nhanh nhạy.",
         "Street Workout, Sức mạnh tự thân, Sức bền cơ bắp",
         ["Thanh Xuân", "Hoàng Mai"], "Không gian tập thoáng mát ngoài công viên hoặc tại nhà",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Ngô Gia Bảo", "pt.giabao@ptconnect.vn", "0901000017", 6, "VERIFIED", "ACTIVE",
         "Kết hợp Calisthenics và bài tập kích hoạt thần kinh cơ để phục hồi chức năng vận động cho dân văn phòng ngồi nhiều.",
         "Chỉnh sửa gù lưng, Thoát vị nhẹ, Calisthenics trị liệu",
         ["Cầu Giấy", "Ba Đình"], "Kiểm tra độ linh hoạt khớp trước khi tập",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Phan Trọng Đạt", "pt.trongdat@ptconnect.vn", "0901000018", 4, "VERIFIED", "ACTIVE",
         "Xây dựng cơ bắp săn chắc không cần tạ nặng, kiểm soát toàn diện cơ thể trên xà đơn và xà kép.",
         "Cơ bắp tự thân, Xà đơn xà kép, Kiểm soát trọng lượng",
         ["Nam Từ Liêm", "Cầu Giấy"], "Kèm kỹ thuật thở và bảo vệ khớp cổ tay",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Lê Viết Thắng", "pt.vietthang@ptconnect.vn", "0901000019", 5, "VERIFIED", "ACTIVE",
         "Chuyên đào tạo các bài skill Calisthenics: Front Lever, Planche, Human Flag.",
         "Kỹ năng Calisthenics, Sức mạnh gân khớp, Core đỉnh cao",
         ["Hà Đông", "Thanh Xuân"], "Giáo án phân tầng từ cơ bản đến siêu cấp",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),

        # Nhóm 4: Powerlifting & Sức mạnh tạ nặng (Strength & Heavy Lifting) - 6 PTs
        ("Trần Quốc Bảo", "pt.quocbao@ptconnect.vn", "0901000020", 5, "VERIFIED", "ACTIVE",
         "Chuyên gia Powerlifting và phát triển sức mạnh tối đa (Squat, Bench, Deadlift). Đạt chứng chỉ NASM CPT quốc tế.",
         "Powerlifting, Sức mạnh, Tăng cân, Bulking, Squat Bench Deadlift",
         ["Phòng tập Elite Fitness Tây Hồ", "Cầu Giấy"], "Trang bị đầy đủ đai lưng và bảo hộ đầu gối",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
        ("Lương Đình Trọng", "pt.dinhtrong@ptconnect.vn", "0901000021", 8, "VERIFIED", "ACTIVE",
         "Vận động viên thi đấu Powerlifting chuyên nghiệp với kỷ lục tổng tạ trên 600kg. Chuyên chỉnh form chống chấn thương.",
         "Sức mạnh bộc phát, Powerlifting thi đấu, Chỉnh form tạ nặng",
         ["Thanh Xuân", "Đống Đa"], "Kiểm soát an toàn 100% trong từng rep tạ nặng",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
        ("Đỗ Mạnh Hùng", "pt.manhhung@ptconnect.vn", "0901000022", 6, "VERIFIED", "ACTIVE",
         "Đào tạo bài bản theo giáo trình quốc tế CSCS. Giúp học viên tăng cường sức mạnh toàn diện mà không lo chấn thương.",
         "Strength & Conditioning, Tăng cơ tạ nặng, Deadlift an toàn",
         ["Nam Từ Liêm", "Cầu Giấy"], "Phân tích chuyển động qua video quay chậm",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
        ("Vũ Đức Thịnh", "pt.ducthinh@ptconnect.vn", "0901000023", 4, "VERIFIED", "ACTIVE",
         "Chuyên cải thiện kỹ thuật Squat sâu không đau lưng và nâng cao mức tạ 1RM.",
         "Squat chuyên sâu, Mức tạ 1RM, Gia tăng sức mạnh",
         ["Hai Bà Trưng", "Hoàn Kiếm"], "Hỗ trợ học viên test 1RM định kỳ",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
        ("Nguyễn Quang Vinh", "pt.quangvinh@ptconnect.vn", "0901000024", 7, "VERIFIED", "ACTIVE",
         "Tập trung xây dựng nền tảng sức mạnh thô và kích thích mật độ xương khớp cho nam giới tuổi 30+.",
         "Sức mạnh nam giới 30+, Tăng mật độ xương, Tạ nặng an toàn",
         ["Ba Đình", "Đống Đa"], "Khởi động và kích hoạt khớp háng chuyên nghiệp",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),
        ("Phạm Thế Hiển", "pt.thehien@ptconnect.vn", "0901000025", 5, "VERIFIED", "ACTIVE",
         "Chuyên môn Deadlift và gia tăng sức kéo lưng dưới, khắc phục thói quen cong lưng.",
         "Deadlift chuyên sâu, Sức kéo lưng dưới, Form tạ hoàn hảo",
         ["Long Biên", "Gia Lâm"], "Trang bị phấn tạ và dây kéo strap",
         "https://www.youtube.com/watch?v=bEv6CCg2BC8"),

        # Nhóm 5: Yoga & Pilates chỉnh dáng, thon gọn (Yoga, Pilates & Posture) - 7 PTs
        ("Nguyễn Thu Hà", "pt.thuha@ptconnect.vn", "0901000026", 4, "VERIFIED", "ACTIVE",
         "HLV chuyên sâu Giảm mỡ siết cơ nữ, Pilates, Yoga phục hồi và thon gọn vóc dáng sau sinh. Chứng chỉ Pilates Thụy Sĩ.",
         "Giảm mỡ nữ, Yoga, Pilates, Giảm cân sau sinh, Dinh dưỡng Eat Clean",
         ["Phòng tập Yoga Plus Ba Đình", "Cầu Giấy"], "Kèm tại nhà phụ thu 50k tiền di chuyển",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Phan Mai Linh", "pt.mailinh@ptconnect.vn", "0901000027", 5, "VERIFIED", "ACTIVE",
         "Hơn 5 năm giảng dạy Pilates Reformer cho phái nữ. Chuyên các bài tập siết eo, nâng cung mông và tạo đường cong mềm mại.",
         "Pilates thảm & máy Reformer, Siết eo thon gọn, Định hình mông",
         ["Tây Hồ", "Ba Đình"], "Có phòng tập studio riêng tư cao cấp",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Trần Thùy Dung", "pt.thuydung@ptconnect.vn", "0901000028", 3, "VERIFIED", "ACTIVE",
         "Chứng chỉ 500h Yoga Alliance quốc tế. Giúp học viên giải tỏa stress công việc, thư giãn tâm trí và cơ thể dẻo dai.",
         "Yoga trị liệu, Giảm căng thẳng, Dẻo dai cơ thể, Giãn cơ sâu",
         ["Đống Đa", "Thanh Xuân"], "Cung cấp tinh dầu thơm và thảm tập cao cấp",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Hoàng Phương Thảo", "pt.phuongthao@ptconnect.vn", "0901000029", 4, "VERIFIED", "ACTIVE",
         "Chuyên gia thể hình nữ giúp chị em phụ nữ sở hữu số đo 3 vòng chuẩn chỉnh, tự tin diện trang phục ôm sát.",
         "Siết cơ bụng nữ, Tăng cơ mông đùi không to chân, Eat Clean",
         ["Hai Bà Trưng", "Hoàn Kiếm"], "Thiết kế giáo án riêng biệt cho từng tạng người nữ",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Đặng Thúy Nga", "pt.thuynga@ptconnect.vn", "0901000030", 2, "VERIFIED", "ACTIVE",
         "Huấn luyện viên Yoga nhiệt huyết, chuyên phục hồi căng cứng cơ bắp cho nhân viên ngồi máy tính kéo dài.",
         "Yoga phục hồi chấn thương nhẹ, Giãn cơ văn phòng, Thư giãn",
         ["Cầu Giấy", "Nam Từ Liêm"], "Giờ tập linh hoạt vào buổi sáng sớm hoặc trưa",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Vũ Quỳnh Anh", "pt.quynhanh@ptconnect.vn", "0901000031", 6, "VERIFIED", "ACTIVE",
         "Chuyên gia Pilates thon gọn bắp tay, rãnh bụng số 11 và chỉnh gù lưng cho phụ nữ hiện đại.",
         "Pilates rãnh bụng 11, Chỉnh tư thế nữ, Thon gọn bắp tay",
         ["Hoàn Kiếm", "Hai Bà Trưng"], "Studio máy móc nhập khẩu Mỹ",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Lê Kim Ngân", "pt.kimngan@ptconnect.vn", "0901000032", 5, "VERIFIED", "ACTIVE",
         "HLV Yoga Vinyasa và Hatha, giúp học viên tăng độ mở khớp hông và kéo giãn cột sống tối đa.",
         "Yoga Vinyasa, Mở khớp hông, Dẻo dai cột sống, Thiền định",
         ["Tây Hồ", "Cầu Giấy"], "Học viên được hướng dẫn thiền định cuối buổi",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),

        # Nhóm 6: Boxing, Kickfit, Muay Thái & Võ tự vệ (Combat Conditioning) - 6 PTs
        ("Đỗ Tuấn Kiệt", "pt.tuankiet@ptconnect.vn", "0901000033", 7, "VERIFIED", "ACTIVE",
         "HLV thể lực, Boxing, Kickfit cường độ cao đốt mỡ cấp tốc và phản xạ tự vệ. Hơn 7 năm kinh nghiệm tại Times City.",
         "Kickfit, Boxing, Cardio đốt mỡ, Tự vệ, Tăng sức bền",
         ["Fit24 Hai Bà Trưng", "Times City"], "HLV chuẩn bị sẵn găng tay và đích đấm chất lượng cao",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),
        ("Vũ Văn Quyền", "pt.vanquyen@ptconnect.vn", "0901000034", 6, "VERIFIED", "ACTIVE",
         "Võ sĩ Muay Thai chuyên nghiệp, kết hợp đòn chân, gối, chỏ giúp học viên tăng phản xạ và tiêu hao calo thần tốc.",
         "Muay Thai, Kickboxing, Kỹ năng tự vệ đường phố, Đốt mỡ",
         ["Cầu Giấy", "Đống Đa"], "Tập luyện an toàn, không va chạm gây chấn thương",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),
        ("Phạm Hải Đăng", "pt.haidang@ptconnect.vn", "0901000035", 4, "VERIFIED", "ACTIVE",
         "Chuyên môn Kickfit cho nữ giới và người làm việc căng thẳng, xả stress tối đa sau giờ làm việc.",
         "Kickfit nữ giới, Xả stress, Phản xạ nhanh, Săn chắc toàn thân",
         ["Thanh Xuân", "Hà Đông"], "Dạy kèm tận nhà hoặc tại phòng gym tiện lợi",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),
        ("Nguyễn Công Phượng", "pt.congphuong@ptconnect.vn", "0901000036", 5, "VERIFIED", "ACTIVE",
         "Boxing phương Tây cổ điển, rèn luyện bộ pháp di chuyển chân nhịp nhàng và sức mạnh đòn tay.",
         "Boxing cổ điển, Bộ pháp di chuyển, Tự vệ thực tế",
         ["Ba Đình", "Hoàn Kiếm"], "Có sàn đài tập luyện thực tế",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),
        ("Đinh Quang Khải", "pt.quangkhai@ptconnect.vn", "0901000037", 3, "VERIFIED", "ACTIVE",
         "Kickboxing giảm mỡ eo hông và bắp chân, bài tập sôi động trên nền nhạc tạo hưng phấn.",
         "Kickboxing theo nhạc, Giảm mỡ eo hông, Năng lượng tích cực",
         ["Nam Từ Liêm", "Cầu Giấy"], "Trang bị đầy đủ băng quấn tay bảo vệ khớp",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),
        ("Trịnh Bá Hưng", "pt.bahung@ptconnect.vn", "0901000038", 8, "VERIFIED", "ACTIVE",
         "Cựu HLV đội tuyển đối kháng, chuyên huấn luyện kỹ năng thoát hiểm và tự vệ trong không gian hẹp.",
         "Võ tự vệ cận chiến, Thoát hiểm, Bản lĩnh tự tin",
         ["Tây Hồ", "Ba Đình"], "Giáo trình an toàn tuyệt đối cho người chưa từng tập võ",
         "https://www.youtube.com/watch?v=1bPEqY_4j-w"),

        # Nhóm 7: Phục hồi chức năng & Chấn thương, Thoát vị, Đau vai gáy (Rehabilitation & Spine) - 6 PTs
        ("Trần Văn Khoa", "pt.vankhoa@ptconnect.vn", "0901000039", 9, "VERIFIED", "ACTIVE",
         "Bác sĩ Y học thể thao kiêm HLV phục hồi chức năng, chuyên điều trị đau lưng, thoát vị đĩa đệm và lệch vẹo cột sống.",
         "Phục hồi chức năng, Thoát vị đĩa đệm, Đau cột sống, Lệch xương chậu",
         ["Cầu Giấy", "Đống Đa"], "Phác đồ điều trị kết hợp bài tập trị liệu khoa học",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Lê Minh Đức", "pt.minhduc.pt@ptconnect.vn", "0901000040", 6, "VERIFIED", "ACTIVE",
         "Chuyên gia giải phóng mạc cơ (Myofascial Release) và khắc phục hội chứng cổ rùa, đau mỏi vai gáy văn phòng.",
         "Hội chứng cổ rùa, Đau vai gáy văn phòng, Giải phóng mạc cơ",
         ["Thanh Xuân", "Ba Đình"], "Có dụng cụ con lăn Foam Roller và súng massage chuyên dụng",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Hoàng Thu Trang", "pt.thutrang@ptconnect.vn", "0901000041", 5, "VERIFIED", "ACTIVE",
         "Chuyên chỉnh sửa chân vòng kiềng (chân chữ X, chữ O) và cân chỉnh dáng đi cho thanh thiếu niên.",
         "Chân vòng kiềng chữ X chữ O, Chỉnh dáng đi, Phục hồi khớp gối",
         ["Hai Bà Trưng", "Hoàn Kiếm"], "Đo góc lệch khớp trước và sau khóa học",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Vũ Ngọc Ánh", "pt.ngocanh@ptconnect.vn", "0901000042", 7, "VERIFIED", "ACTIVE",
         "Huấn luyện viên phục hồi sau chấn thương đứt dây chằng chéo trước ACL và thoái hóa khớp gối sớm.",
         "Phục hồi dây chằng ACL, Khớp gối thoái hóa, Tái hòa nhập thể thao",
         ["Tây Hồ", "Cầu Giấy"], "Phối hợp cùng bác sĩ chỉnh hình của học viên",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Nguyễn Hải Đăng", "pt.haidang.rehab@ptconnect.vn", "0901000043", 4, "VERIFIED", "ACTIVE",
         "Phương pháp kéo giãn PNF và kích hoạt các nhóm cơ yếu nhằm triệt tiêu các cơn đau lưng dưới dai dẳng.",
         "Kéo giãn PNF, Giảm đau lưng dưới, Kích hoạt cơ yếu",
         ["Nam Từ Liêm", "Bắc Từ Liêm"], "Bài tập êm dịu, không gây đau buốt",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),
        ("Trương Quốc Đạt", "pt.quocdat@ptconnect.vn", "0901000044", 5, "VERIFIED", "ACTIVE",
         "Trị liệu hội chứng chèn ép thần kinh tọa và cải thiện độ linh hoạt của toàn bộ khớp háng.",
         "Đau thần kinh tọa, Linh hoạt khớp háng, Giảm căng cứng thắt lưng",
         ["Hoàng Mai", "Hà Đông"], "Kèm tận tình từng cử động nhỏ",
         "https://www.youtube.com/watch?v=IODxDxX7oi4"),

        # Nhóm 8: Dinh dưỡng, Tăng cân cho người gầy & Đối tượng đặc biệt - 6 PTs
        ("Nguyễn Thanh Phong", "pt.thanhphong@ptconnect.vn", "0901000045", 5, "VERIFIED", "ACTIVE",
         "Chuyên gia tăng cân an toàn cho người gầy lâu năm, cơ địa khó hấp thụ. Xây dựng thực đơn dinh dưỡng chuẩn y khoa.",
         "Tăng cân người gầy, Dinh dưỡng hấp thụ, Tăng cơ tự nhiên",
         ["Đống Đa", "Thanh Xuân"], "Kèm sổ tay công thức nấu ăn ngon miệng dễ tăng cân",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
        ("Hoàng Thị Lan", "pt.thilan@ptconnect.vn", "0901000046", 6, "VERIFIED", "ACTIVE",
         "Huấn luyện viên thể dục vận động cho người trung niên và người cao tuổi, tăng cường tuần hoàn máu và huyết áp ổn định.",
         "Thể dục người cao tuổi, Ổn định huyết áp, Vận động nhẹ nhàng",
         ["Ba Đình", "Tây Hồ"], "Đo huyết áp trước và sau mỗi buổi tập",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        ("Bùi Thị Bích", "pt.thibich@ptconnect.vn", "0901000047", 4, "VERIFIED", "ACTIVE",
         "Chuyên gia tập luyện cho mẹ bầu (Prenatal) và phục hồi cơ sàn chậu, tách cơ bụng sau sinh (Postnatal).",
         "Tập luyện mẹ bầu, Phục hồi sau sinh, Tách cơ bụng diastasis recti",
         ["Cầu Giấy", "Nam Từ Liêm"], "Đạt chứng chỉ quốc tế huấn luyện phụ nữ mang thai",
         "https://www.youtube.com/watch?v=v7AYKMP6rOE"),

        # 3 PT PENDING (để test duyệt Admin)
        ("Vũ Hoàng Nam", "pt.hoangnam.pending@ptconnect.vn", "0901000048", 2, "PENDING", "PENDING",
         "HLV Fitness trẻ nhiệt huyết, tốt nghiệp Đại học Thể dục Thể thao, chuyên giảm mỡ cho thanh niên.",
         "Giảm mỡ trẻ em, Thể thao học đường, Bơi lội",
         ["Khu vực Hoàng Mai", "Hà Đông"], "Chờ ban quản trị xét duyệt hồ sơ",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),
        ("Đỗ Tuấn Minh", "pt.tuanminh.pending@ptconnect.vn", "0901000049", 1, "PENDING", "PENDING",
         "HLV Aerobic và Cardio nhóm, nộp chứng chỉ chờ xác minh.",
         "Aerobic nhóm, Group X, Đốt mỡ vui nhộn",
         ["Khu vực Nam Từ Liêm"], "Chờ kiểm tra bằng cấp chứng chỉ",
         "https://www.youtube.com/watch?v=sw_Rvhw2qf4"),

        # 1 PT REJECTED / SUSPENDED (để test khóa / từ chối)
        ("Bùi Văn Quyết", "pt.vanquyet.rej@ptconnect.vn", "0901000050", 3, "REJECTED", "SUSPENDED",
         "Hồ sơ chứng chỉ chưa đạt chuẩn theo quy định hệ thống PT Connect.",
         "Thể hình tự do, Tập luyện cá nhân",
         ["Khu vực Bắc Từ Liêm"], "Tài khoản bị tạm ngưng",
         "https://www.youtube.com/watch?v=aclHkVaku9U"),
    ]

    pt_id_seq = 1
    pt_profile_map = {}
    pt_locations_data = []
    location_id_seq = 1

    for name, email, phone, exp, verif, status, bio, specs, locs, note, video in pt_raw_configs:
        u_id = user_id_seq
        user_id_seq += 1

        users.append({
            "id": u_id,
            "full_name": name,
            "email": email,
            "password_hash": password_hash,
            "phone": phone,
            "role": "PT",
            "status": status,
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"
        })
        pt_balance = 8500000.0 if status == "ACTIVE" else 0.0
        pt_locked = 1500000.0 if status == "ACTIVE" else 0.0
        wallets.append({"id": u_id, "user_id": u_id, "balance": pt_balance, "locked_balance": pt_locked})

        pt_obj = {
            "id": pt_id_seq,
            "user_id": u_id,
            "bio": bio,
            "specialty": specs,
            "specialties": specs,
            "experience_years": exp,
            "location_pricing_note": note,
            "certificate_url": "https://storage.ptconnect.vn/certs/cert_nasam.jpg",
            "demo_video_url": video,
            "verification_status": verif,
            "name": name,
            "active": (verif == "VERIFIED" and status == "ACTIVE")
        }
        pt_profiles.append(pt_obj)
        pt_profile_map[pt_id_seq] = pt_obj

        for loc in locs:
            pt_locations_data.append({
                "id": location_id_seq,
                "pt_id": pt_id_seq,
                "location_name": loc
            })
            location_id_seq += 1

        pt_id_seq += 1

    # 1.3 Học viên (STUDENT) - 15 học viên
    student_users = []
    # Học viên chính 1: student_minhanh@gmail.com
    u_id = user_id_seq
    user_id_seq += 1
    s_main_1 = {
        "id": u_id,
        "full_name": "Nguyễn Minh Anh",
        "email": "student_minhanh@gmail.com",
        "password_hash": password_hash,
        "phone": "0988776655",
        "role": "STUDENT",
        "status": "ACTIVE",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=student_minhanh"
    }
    users.append(s_main_1)
    student_users.append(s_main_1)
    wallets.append({"id": u_id, "user_id": u_id, "balance": 15000000.0, "locked_balance": 0.0})

    # Học viên chính 2: student.a@ptconnect.vn
    u_id = user_id_seq
    user_id_seq += 1
    s_main_2 = {
        "id": u_id,
        "full_name": "Nguyễn Văn A",
        "email": "student.a@ptconnect.vn",
        "password_hash": password_hash,
        "phone": "0900000001",
        "role": "STUDENT",
        "status": "ACTIVE",
        "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=student_a"
    }
    users.append(s_main_2)
    student_users.append(s_main_2)
    wallets.append({"id": u_id, "user_id": u_id, "balance": 7700000.0, "locked_balance": 0.0})

    # 13 học viên phụ
    for i in range(2, 15):
        u_id = user_id_seq
        user_id_seq += 1
        s_name = f"Học Viên {i}"
        s_email = f"student_{i:02d}@ptconnect.vn"
        s_phone = f"0912345{i:03d}"
        s_balance = float(random.choice([3000000, 5000000, 8000000, 10000000]))

        u_data = {
            "id": u_id,
            "full_name": s_name,
            "email": s_email,
            "password_hash": password_hash,
            "phone": s_phone,
            "role": "STUDENT",
            "status": "ACTIVE",
            "avatar_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed=student_{i}"
        }
        users.append(u_data)
        student_users.append(u_data)
        wallets.append({"id": u_id, "user_id": u_id, "balance": s_balance, "locked_balance": 0.0})

    # =========================================================================
    # 2. COURSES (Mỗi PT VERIFIED có 1-2 khóa học)
    # =========================================================================
    active_pts = [p for p in pt_profiles if p["active"]]
    courses = []
    course_id_seq = 1

    sample_course_templates = [
        ("Khóa Khởi Động Nhập Môn 12 Buổi", "Làm quen với phòng gym và thể lực nền tảng", 12, 60, 3600000.0),
        ("Gói Tăng Cơ Chuyên Sâu 24 Buổi", "Tối ưu hóa phì đại cơ bắp Hypertrophy chuẩn khoa học", 24, 90, 7200000.0),
        ("Khóa Đốt Mỡ Cấp Tốc HIIT 16 Buổi", "Đốt calo cường độ cao, thon gọn vóc dáng nhanh chóng", 16, 60, 4800000.0),
        ("Gói Calisthenics & Thể Hình Tự Thân 20 Buổi", "Làm chủ cơ thể với xà đơn, xà kép và các chuyển động thăng bằng", 20, 90, 6000000.0),
        ("Gói Pilates Chỉnh Dáng & Cột Sống 20 Buổi", "Siết cơ bụng sâu, cân chỉnh lưng gù và tạo đường cong mềm mại", 20, 90, 8000000.0),
        ("Gói Boxing Thể Lực & Xả Stress 16 Buổi", "Tập luyện phản xạ nhanh, xả stress và tăng sức bền tim mạch", 16, 60, 5600000.0),
        ("Khóa Phục Hồi Cột Sống & Đau Vai Gáy 12 Buổi", "Khắc phục đau nhức vai gáy và thoát vị nhẹ cho dân văn phòng", 12, 60, 4200000.0),
        ("Khóa Powerlifting Sức Mạnh Squat-Bench-Deadlift 24 Buổi", "Nâng cao mức tạ tối đa 1RM và hoàn thiện kỹ thuật tạ nặng", 24, 90, 8400000.0),
        ("Gói Tăng Cân Khỏe Đẹp Cho Người Gầy 16 Buổi", "Kết hợp thực đơn giàu dinh dưỡng và bài tập hấp thụ tối đa", 16, 60, 5200000.0),
        ("Khóa Yoga Dẻo Dai & Thư Giãn Tinh Thần 12 Buổi", "Giải tỏa căng thẳng tinh thần, dẻo dai cơ bắp và lưu thông khí huyết", 12, 60, 3800000.0),
    ]

    for pt in active_pts:
        p_id = pt["id"]
        pt_short = pt["name"].split()[-1]
        # Tạo 1 hoặc 2 khóa học cho PT này
        num_c = 2 if p_id <= 15 else 1
        for c_idx in range(num_c):
            t_title, t_desc, t_sessions, t_valid, t_price = sample_course_templates[(p_id + c_idx) % len(sample_course_templates)]
            courses.append({
                "id": course_id_seq,
                "pt_id": p_id,
                "title": f"{t_title} - HLV {pt_short}",
                "description": f"{t_desc} cùng HLV {pt['name']}.",
                "total_sessions": t_sessions,
                "validity_days": t_valid,
                "base_price": t_price,
                "status": "ACTIVE"
            })
            course_id_seq += 1

    course_lookup = {c["id"]: c for c in courses}

    # =========================================================================
    # 3. AVAILABILITY SLOTS (Cho 45 PT active)
    # =========================================================================
    slots = []
    # Sinh khung giờ rảnh từ hôm nay (15/11/2026) đến tháng 01/2027
    start_base = datetime(2026, 11, 15)
    hours = [
        (8, 0, 9, 0),
        (9, 30, 10, 30),
        (14, 0, 15, 0),
        (15, 30, 16, 30),
        (17, 30, 18, 30),
        (19, 0, 20, 0)
    ]

    pt_slots_map = {}
    for pt in active_pts:
        p_id = pt["id"]
        pt_slots_map[p_id] = []
        for day_offset in range(0, 45, 2):  # cách 2 ngày mở 1 ngày
            current_day = start_base + timedelta(days=day_offset)
            # Chọn 2-3 khung giờ mỗi ngày
            for h_start, m_start, h_end, m_end in random.sample(hours, k=3):
                st_time = current_day.replace(hour=h_start, minute=m_start, second=0, microsecond=0)
                en_time = current_day.replace(hour=h_end, minute=m_end, second=0, microsecond=0)
                slot_obj = {
                    "pt_id": p_id,
                    "start_time": st_time,
                    "end_time": en_time,
                    "status": "AVAILABLE"
                }
                slots.append(slot_obj)
                pt_slots_map[p_id].append(slot_obj)

    # Bổ sung các khung giờ chuẩn cho PT 1 và PT 4 để khớp các ca tập thực tế
    custom_required_slots = [
        # PT 1 (Cuong)
        (1, datetime(2026, 11, 18, 15, 30), datetime(2026, 11, 18, 16, 30)),
        (1, datetime(2026, 11, 19, 14, 0), datetime(2026, 11, 19, 15, 0)),
        (1, datetime(2026, 11, 19, 17, 30), datetime(2026, 11, 19, 18, 30)),
        (1, datetime(2026, 11, 21, 8, 0), datetime(2026, 11, 21, 9, 0)),
        (1, datetime(2026, 11, 21, 9, 30), datetime(2026, 11, 21, 10, 30)),
        (1, datetime(2026, 11, 21, 14, 0), datetime(2026, 11, 21, 15, 0)),
        (1, datetime(2026, 11, 23, 15, 30), datetime(2026, 11, 23, 16, 30)),
        # PT 4 (Dung)
        (4, datetime(2026, 11, 17, 8, 0), datetime(2026, 11, 17, 9, 0)),
        (4, datetime(2026, 11, 19, 9, 30), datetime(2026, 11, 19, 10, 30)),
        (4, datetime(2026, 11, 22, 9, 30), datetime(2026, 11, 22, 10, 30)),
        (4, datetime(2026, 11, 24, 17, 30), datetime(2026, 11, 24, 18, 30)),
    ]
    existing_slot_keys = {(s["pt_id"], s["start_time"]) for s in slots}
    for p_id, st_t, en_t in custom_required_slots:
        if (p_id, st_t) not in existing_slot_keys:
            slot_obj = {
                "pt_id": p_id,
                "start_time": st_t,
                "end_time": en_t,
                "status": "AVAILABLE"
            }
            slots.append(slot_obj)
            pt_slots_map[p_id].append(slot_obj)
            existing_slot_keys.add((p_id, st_t))

    # =========================================================================
    # 4. ENROLLMENTS & PAYMENTS
    # =========================================================================
    enrollments = []
    payments = []
    enrollment_id_seq = 1
    payment_id_seq = 1

    main_student_id = s_main_1["id"]

    # Hợp đồng 1: Minh Anh với PT 1 (Cường) - ACTIVE (12 buổi, còn 7)
    e1 = {
        "id": enrollment_id_seq,
        "student_id": main_student_id,
        "course_id": 1,
        "pt_id": 1,
        "training_location": "FitZone Thanh Xuân",
        "final_price": 3600000.0,
        "total_sessions": 12,
        "remaining_sessions": 7,
        "start_date": "2026-11-01",
        "end_date": "2027-02-28",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000001.pdf",
        "status": "ACTIVE"
    }
    enrollments.append(e1)
    enrollment_id_seq += 1

    # Hợp đồng 2: Minh Anh với PT 5 (Thu Hà - Yoga/Pilates) - ACTIVE
    pt_ha_course = next((c for c in courses if c["pt_id"] == 5), courses[4])
    e2 = {
        "id": enrollment_id_seq,
        "student_id": main_student_id,
        "course_id": pt_ha_course["id"],
        "pt_id": pt_ha_course["pt_id"],
        "training_location": "Phòng tập Yoga Plus Ba Đình",
        "final_price": pt_ha_course["base_price"],
        "total_sessions": pt_ha_course["total_sessions"],
        "remaining_sessions": pt_ha_course["total_sessions"] - 2,
        "start_date": "2026-11-05",
        "end_date": "2027-03-15",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000002.pdf",
        "status": "ACTIVE"
    }
    enrollments.append(e2)
    enrollment_id_seq += 1

    # Hợp đồng 3: Minh Anh với PT 3 (Quốc Huy) - COMPLETED (16 buổi, còn 0)
    pt_huy_course = next((c for c in courses if c["pt_id"] == 3), courses[2])
    e3 = {
        "id": enrollment_id_seq,
        "student_id": main_student_id,
        "course_id": pt_huy_course["id"],
        "pt_id": pt_huy_course["pt_id"],
        "training_location": "Thanh Xuân",
        "final_price": pt_huy_course["base_price"],
        "total_sessions": 16,
        "remaining_sessions": 0,
        "start_date": "2026-08-01",
        "end_date": "2026-10-15",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000003.pdf",
        "status": "COMPLETED"
    }
    enrollments.append(e3)
    enrollment_id_seq += 1

    # Hợp đồng 4: Minh Anh với PT 4 (Anh Dũng) - EXPIRED (12 buổi, còn 2, hết hạn tháng 10)
    pt_dung_course = next((c for c in courses if c["pt_id"] == 4), courses[3])
    e4 = {
        "id": enrollment_id_seq,
        "student_id": main_student_id,
        "course_id": pt_dung_course["id"],
        "pt_id": pt_dung_course["pt_id"],
        "training_location": "Đống Đa",
        "final_price": pt_dung_course["base_price"],
        "total_sessions": 12,
        "remaining_sessions": 2,
        "start_date": "2026-07-01",
        "end_date": "2026-10-01",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000004.pdf",
        "status": "EXPIRED"
    }
    enrollments.append(e4)
    enrollment_id_seq += 1

    # Hợp đồng 5: Nguyễn Văn A (id 53) với PT 4 (Bùi Anh Dũng - Pilates 20 buổi) - ACTIVE
    pt_dung_course = next((c for c in courses if c["pt_id"] == 4 and "Pilates" in c["title"]), courses[4])
    e_st_a_pilates = {
        "id": 5,
        "student_id": s_main_2["id"],
        "course_id": pt_dung_course["id"],
        "pt_id": pt_dung_course["pt_id"],
        "training_location": "Cầu Giấy",
        "final_price": 5000000.0,
        "total_sessions": 20,
        "remaining_sessions": 18,
        "start_date": "2026-11-01",
        "end_date": "2027-02-01",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000005.pdf",
        "status": "ACTIVE"
    }
    enrollments.append(e_st_a_pilates)

    # 4 hợp đồng cho các học viên khác (student_users[2:6]) -> id 6, 7, 8, 9
    enrollment_id_seq = 6
    for st in student_users[2:6]:
        crs = random.choice(courses[:10])
        enrollments.append({
            "id": enrollment_id_seq,
            "student_id": st["id"],
            "course_id": crs["id"],
            "pt_id": crs["pt_id"],
            "training_location": "Cầu Giấy",
            "final_price": crs["base_price"],
            "total_sessions": crs["total_sessions"],
            "remaining_sessions": crs["total_sessions"] - 2,
            "start_date": "2026-11-01",
            "end_date": "2027-02-01",
            "contract_url": f"https://storage.ptconnect.vn/contracts/ptc_hd_{enrollment_id_seq:06d}.pdf",
            "status": "ACTIVE"
        })
        enrollment_id_seq += 1

    # Hợp đồng 10: Nguyễn Văn A (id 53) với PT 1 (Lê Hoàng Cường - HIIT 16 buổi) - ACTIVE
    pt_cuong_course = next((c for c in courses if c["pt_id"] == 1 and "HIIT" in c["title"]), courses[1])
    e_st_a_hiit = {
        "id": 10,
        "student_id": s_main_2["id"],
        "course_id": pt_cuong_course["id"],
        "pt_id": pt_cuong_course["pt_id"],
        "training_location": "Phòng Cali Cầu Giấy",
        "final_price": 4500000.0,
        "total_sessions": 16,
        "remaining_sessions": 14,
        "start_date": "2026-11-15",
        "end_date": "2027-01-15",
        "contract_url": "https://storage.ptconnect.vn/contracts/ptc_hd_000010.pdf",
        "status": "ACTIVE"
    }
    enrollments.append(e_st_a_hiit)
    enrollment_id_seq = 11

    # Payments cho Minh Anh
    payments.append({
        "id": payment_id_seq,
        "wallet_id": main_student_id,
        "enrollment_id": None,
        "amount": 25000000.0,
        "payment_type": "TOPUP",
        "payment_method": "BANK_TRANSFER",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_TOPUP_{payment_id_seq:05d}",
        "created_at": "2026-11-01 08:00:00"
    })
    payment_id_seq += 1

    for enr in [e1, e2]:
        payments.append({
            "id": payment_id_seq,
            "wallet_id": main_student_id,
            "enrollment_id": enr["id"],
            "amount": enr["final_price"],
            "payment_type": "PURCHASE_PACKAGE",
            "payment_method": "WALLET",
            "status": "SUCCESS",
            "transaction_ref": f"TXN_BUY_{payment_id_seq:05d}",
            "created_at": f"{enr['start_date']} 09:00:00"
        })
        payment_id_seq += 1

    # 1 giao dịch bồi thường & 1 hoàn tiền
    payments.append({
        "id": payment_id_seq,
        "wallet_id": main_student_id,
        "enrollment_id": None,
        "amount": 150000.0,
        "payment_type": "COMPENSATION",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_COMP_{payment_id_seq:05d}",
        "created_at": "2026-11-10 14:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": main_student_id,
        "enrollment_id": None,
        "amount": 300000.0,
        "payment_type": "REFUND",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_REF_{payment_id_seq:05d}",
        "created_at": "2026-11-12 16:30:00"
    })
    payment_id_seq += 1

    # Phí nền tảng cho Admin (10%)
    payments.append({
        "id": payment_id_seq,
        "wallet_id": 1,
        "enrollment_id": 1,
        "amount": 360000.0,
        "payment_type": "PLATFORM_FEE",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_PFEE_{payment_id_seq:05d}",
        "created_at": "2026-11-01 09:05:00"
    })
    payment_id_seq += 1

    # Payments cho Nguyễn Văn A (s_main_2, id 53)
    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": None,
        "amount": 10000000.0,
        "payment_type": "TOPUP",
        "payment_method": "BANK_TRANSFER",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_TOPUP_{payment_id_seq:05d}",
        "created_at": "2026-11-10 08:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": 10,
        "amount": 4500000.0,
        "payment_type": "PURCHASE_PACKAGE",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_BUY_{payment_id_seq:05d}",
        "created_at": "2026-11-10 09:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": None,
        "amount": 6900000.0,
        "payment_type": "TOPUP",
        "payment_method": "CREDIT_CARD",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_TOPUP_{payment_id_seq:05d}",
        "created_at": "2026-11-12 10:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": 5,
        "amount": 5000000.0,
        "payment_type": "PURCHASE_PACKAGE",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_BUY_{payment_id_seq:05d}",
        "created_at": "2026-11-12 11:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": 5,
        "amount": 250000.0,
        "payment_type": "REFUND",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_REF_{payment_id_seq:05d}",
        "created_at": "2026-11-18 14:00:00"
    })
    payment_id_seq += 1

    payments.append({
        "id": payment_id_seq,
        "wallet_id": s_main_2["id"],
        "enrollment_id": None,
        "amount": 50000.0,
        "payment_type": "COMPENSATION",
        "payment_method": "WALLET",
        "status": "SUCCESS",
        "transaction_ref": f"TXN_COMP_{payment_id_seq:05d}",
        "created_at": "2026-11-18 14:00:00"
    })
    payment_id_seq += 1

    # =========================================================================
    # 5. BOOKINGS (PENDING, CONFIRMED, COMPLETED, CANCELLED)
    # =========================================================================
    bookings = []
    cancellations = []
    attendances = []
    reviews = []
    disputes = []

    booking_id_seq = 1
    cancel_id_seq = 1
    attend_id_seq = 1
    review_id_seq = 1
    dispute_id_seq = 1

    # Helper lấy slot của PT (luôn khởi tạo AVAILABLE để thỏa mãn trg_bookings_before_insert)
    def pick_slot_for_pt(pt_id, index=0, set_status="AVAILABLE"):
        slot = pt_slots_map[pt_id][index]
        slot["status"] = "AVAILABLE"
        return slot

    # 5.1 Ca tập của Minh Anh với HLV Lê Hoàng Cường (e1, pt_id=1)
    # 2 Ca PENDING (Chờ PT duyệt)
    s_p1 = pick_slot_for_pt(1, index=10, set_status="BOOKED")
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_p1["start_time"],
        "session_fee": 300000.0,
        "status": "PENDING",
        "student_note": "Em muốn tập trung kỹ thuật Squat và Deadlift",
        "created_at": "2026-11-18 10:00:00"
    })
    booking_id_seq += 1

    s_p2 = pick_slot_for_pt(1, index=11, set_status="BOOKED")
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_p2["start_time"],
        "session_fee": 300000.0,
        "status": "PENDING",
        "student_note": "Ca tập bổ trợ cơ ngực và tay sau",
        "created_at": "2026-11-19 14:00:00"
    })
    booking_id_seq += 1

    # 2 Ca CONFIRMED (Đã duyệt, sắp diễn ra)
    s_c1 = pick_slot_for_pt(1, index=12, set_status="BOOKED")
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_c1["start_time"],
        "session_fee": 300000.0,
        "status": "CONFIRMED",
        "student_note": "Ca tập đã được HLV phê duyệt",
        "created_at": "2026-11-17 08:30:00"
    })
    booking_id_seq += 1

    s_c2 = pick_slot_for_pt(1, index=13, set_status="BOOKED")
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_c2["start_time"],
        "session_fee": 300000.0,
        "status": "CONFIRMED",
        "student_note": "Chuẩn bị giày và khăn tập đầy đủ",
        "created_at": "2026-11-17 09:00:00"
    })
    booking_id_seq += 1

    # 3 Ca COMPLETED (Đã hoàn thành - có điểm danh & review)
    for idx, (cmt, star) in enumerate([
        ("HLV hướng dẫn rất tận tình, chỉnh form tạ tỉ mỉ không bị đau lưng.", 5),
        ("Buổi tập rất hiệu quả, bài tập đa dạng và nhịp độ vừa sức.", 5),
        ("Rất hài lòng, cơ bắp căng mỏi đúng nhóm cơ mục tiêu.", 4),
    ]):
        s_comp = pick_slot_for_pt(1, index=idx, set_status="BOOKED")
        b_id = booking_id_seq
        booking_id_seq += 1
        bookings.append({
            "id": b_id,
            "booking_type": "PACKAGE",
            "enrollment_id": e1["id"],
            "student_id": main_student_id,
            "pt_id": 1,
            "slot_start_time": s_comp["start_time"],
            "session_fee": 300000.0,
            "status": "COMPLETED",
            "student_note": "Ca tập hoàn thành tốt",
            "created_at": "2026-11-05 08:00:00"
        })
        # Điểm danh
        attendances.append({
            "id": attend_id_seq,
            "booking_id": b_id,
            "check_in_time": s_comp["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "check_out_time": s_comp["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "verification_method": "OTP",
            "student_confirmed": True,
            "pt_confirmed": True,
            "status": "PRESENT"
        })
        attend_id_seq += 1

        # Đánh giá
        reviews.append({
            "id": review_id_seq,
            "booking_id": b_id,
            "rating": star,
            "comment": cmt,
            "created_at": s_comp["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        })
        review_id_seq += 1

    # 2 Ca CANCELLED (1 học viên hủy, 1 PT hủy)
    s_can1 = pick_slot_for_pt(1, index=14, set_status="AVAILABLE")
    b_can1_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_can1_id,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_can1["start_time"],
        "session_fee": 300000.0,
        "status": "CANCELLED",
        "student_note": "Hủy do bận việc đột xuất",
        "created_at": "2026-11-10 08:00:00"
    })
    cancellations.append({
        "id": cancel_id_seq,
        "booking_id": b_can1_id,
        "cancelled_by_id": main_student_id,  # Học viên hủy
        "reason": "Học viên có lịch công tác đột xuất, báo trước hơn 24 giờ",
        "evidence_url": None,
        "status": "PROCESSED",
        "cancelled_at": "2026-11-10 14:00:00"
    })
    cancel_id_seq += 1

    # Ca 2: PT hủy (user_id của PT 1 là 2)
    pt1_user_id = pt_profile_map[1]["user_id"]
    s_can2 = pick_slot_for_pt(1, index=15, set_status="AVAILABLE")
    b_can2_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_can2_id,
        "booking_type": "PACKAGE",
        "enrollment_id": e1["id"],
        "student_id": main_student_id,
        "pt_id": 1,
        "slot_start_time": s_can2["start_time"],
        "session_fee": 300000.0,
        "status": "CANCELLED",
        "student_note": "Ca HLV xin phép hủy",
        "created_at": "2026-11-11 09:00:00"
    })
    cancellations.append({
        "id": cancel_id_seq,
        "booking_id": b_can2_id,
        "cancelled_by_id": pt1_user_id,  # PT hủy
        "reason": "HLV bị sốt phát ban phải nghỉ khám bệnh, hoàn trả buổi tập kèm bồi thường 150k",
        "evidence_url": "/app/static/uploads/don_thuoc.jpg",
        "status": "PROCESSED",
        "cancelled_at": "2026-11-11 15:30:00"
    })
    cancel_id_seq += 1

    # 1 Ca có khiếu nại (Dispute - PENDING)
    dispute_b_id = b_can2_id
    disputes.append({
        "id": dispute_id_seq,
        "booking_id": dispute_b_id,
        "sender_id": main_student_id,
        "dispute_type": "PT_NO_SHOW",
        "reason": "HLV hủy sát giờ tập gây ảnh hưởng đến lịch trình cá nhân của em",
        "evidence_url": "/app/static/uploads/tin_nhan_huy_lich.png",
        "counter_evidence_url": "/app/static/uploads/giay_xac_nhan_benh_vien.png",
        "counter_argument": "Tôi đã gọi điện xin lỗi và nộp đơn thuốc của bệnh viện kèm bồi thường cho học viên",
        "status": "PENDING",
        "admin_notes": "Đang chờ Ban quản trị đối soát chứng từ y tế của HLV",
        "resolved_at": None,
        "created_at": "2026-11-11 16:00:00"
    })
    dispute_id_seq += 1

    # 1 Ca TRIAL (Học thử miễn phí)
    s_tr = pick_slot_for_pt(2, index=5, set_status="BOOKED")
    bookings.append({
        "id": booking_id_seq,
        "booking_type": "TRIAL",
        "enrollment_id": None,
        "student_id": main_student_id,
        "pt_id": 2,
        "slot_start_time": s_tr["start_time"],
        "session_fee": 0.0,
        "status": "CONFIRMED",
        "student_note": "Em đăng ký buổi tập thử Calisthenics với HLV Nam",
        "created_at": "2026-11-18 16:00:00"
    })
    booking_id_seq += 1

    # 5.2 Ca tập của Nguyễn Văn A (s_main_2, id 53)
    # Ca 1: COMPLETED (Hôm qua 14:00 - 15:00) với PT 1 (Cường) - ĐỦ ĐIỀU KIỆN KHIẾU NẠI MỚI!
    b_a1_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a1_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 10,
        "student_id": s_main_2["id"],
        "pt_id": 1,
        "slot_start_time": datetime(2026, 11, 19, 14, 0),
        "session_fee": 300000.0,
        "status": "COMPLETED",
        "student_note": "Tập trung nâng cao nhịp tim và bài Burpee",
        "created_at": "2026-11-18 10:00:00"
    })
    attendances.append({
        "id": attend_id_seq,
        "booking_id": b_a1_id,
        "check_in_time": "2026-11-19 14:00:00",
        "check_out_time": "2026-11-19 15:00:00",
        "verification_method": "OTP",
        "student_confirmed": True,
        "pt_confirmed": True,
        "status": "PRESENT"
    })
    attend_id_seq += 1
    reviews.append({
        "id": review_id_seq,
        "booking_id": b_a1_id,
        "rating": 5,
        "comment": "Tập bài Burpee và Mountain Climbers rất đã, HLV Cường hướng dẫn nhịp thở cực kỳ chuẩn chỉnh.",
        "created_at": "2026-11-19 15:05:00"
    })
    review_id_seq += 1

    # Ca 2: COMPLETED (Hôm qua 09:30 - 10:30) với PT 4 (Dũng) - ĐỦ ĐIỀU KIỆN KHIẾU NẠI MỚI!
    b_a2_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a2_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 5,
        "student_id": s_main_2["id"],
        "pt_id": 4,
        "slot_start_time": datetime(2026, 11, 19, 9, 30),
        "session_fee": 250000.0,
        "status": "COMPLETED",
        "student_note": "Ca Pilates phục hồi thắt lưng",
        "created_at": "2026-11-18 08:30:00"
    })
    attendances.append({
        "id": attend_id_seq,
        "booking_id": b_a2_id,
        "check_in_time": "2026-11-19 09:30:00",
        "check_out_time": "2026-11-19 10:30:00",
        "verification_method": "OTP",
        "student_confirmed": True,
        "pt_confirmed": True,
        "status": "PRESENT"
    })
    attend_id_seq += 1
    reviews.append({
        "id": review_id_seq,
        "booking_id": b_a2_id,
        "rating": 5,
        "comment": "Bài tập The Hundred và Roll Up giãn cơ lưng rất dễ chịu, HLV Dũng hỗ trợ tận tình.",
        "created_at": "2026-11-19 10:35:00"
    })
    review_id_seq += 1

    # Ca 3: CANCELLED (Hôm qua 17:30 - 18:30) với PT 1 (Cường) - ĐỦ ĐIỀU KIỆN KHIẾU NẠI MỚI!
    b_a3_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a3_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 10,
        "student_id": s_main_2["id"],
        "pt_id": 1,
        "slot_start_time": datetime(2026, 11, 19, 17, 30),
        "session_fee": 300000.0,
        "status": "CANCELLED",
        "student_note": "Học viên bận việc đột xuất",
        "created_at": "2026-11-18 11:00:00"
    })
    cancellations.append({
        "id": cancel_id_seq,
        "booking_id": b_a3_id,
        "cancelled_by_id": s_main_2["id"],
        "reason": "Học viên có lịch công tác đột xuất, báo trước hơn 24 giờ",
        "evidence_url": None,
        "status": "PROCESSED",
        "cancelled_at": "2026-11-19 11:00:00"
    })
    cancel_id_seq += 1

    # Ca 4: COMPLETED có Dispute PENDING (18/11 15:30 - 16:30) với PT 1 (Cường)
    b_a4_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a4_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 10,
        "student_id": s_main_2["id"],
        "pt_id": 1,
        "slot_start_time": datetime(2026, 11, 18, 15, 30),
        "session_fee": 300000.0,
        "status": "COMPLETED",
        "student_note": "Ca tập HIIT nâng cao",
        "created_at": "2026-11-17 14:00:00"
    })
    attendances.append({
        "id": attend_id_seq,
        "booking_id": b_a4_id,
        "check_in_time": None,
        "check_out_time": None,
        "verification_method": "OTP",
        "student_confirmed": False,
        "pt_confirmed": True,
        "status": "ABSENT"
    })
    attend_id_seq += 1
    disputes.append({
        "id": dispute_id_seq,
        "booking_id": b_a4_id,
        "sender_id": s_main_2["id"],
        "dispute_type": "PT_NO_SHOW",
        "reason": "Tôi có mặt tại phòng tập Cầu Giấy lúc 15h20 và chờ đến 16h00 nhưng HLV Cường không xuất hiện, gọi điện thoại không liên lạc được. Yêu cầu Ban quản trị kiểm tra camera và hoàn trả 01 buổi tập khả dụng vào gói tập.",
        "evidence_url": "/app/static/uploads/evidence_letan_cho_hlv.jpg",
        "counter_evidence_url": None,
        "counter_argument": None,
        "status": "PENDING",
        "admin_notes": "Đang mở thời hạn 48 giờ để HLV gửi văn bản giải trình đối chất.",
        "resolved_at": None,
        "created_at": "2026-11-19 18:00:00"
    })
    dispute_id_seq += 1

    # Ca 5: CANCELLED có Dispute RESOLVED_REFUND (17/11 08:00 - 09:00) với PT 4 (Dũng)
    b_a5_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a5_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 5,
        "student_id": s_main_2["id"],
        "pt_id": 4,
        "slot_start_time": datetime(2026, 11, 17, 8, 0),
        "session_fee": 250000.0,
        "status": "CANCELLED",
        "student_note": "Ca Pilates giãn cơ",
        "created_at": "2026-11-16 09:00:00"
    })
    cancellations.append({
        "id": cancel_id_seq,
        "booking_id": b_a5_id,
        "cancelled_by_id": pt_profile_map[4]["user_id"],
        "reason": "Hệ thống ghi nhận hủy ca do điểm danh vắng mặt",
        "evidence_url": "/app/static/uploads/don_xin_hoan_lich.jpg",
        "status": "RESOLVED",
        "cancelled_at": "2026-11-17 09:30:00"
    })
    cancel_id_seq += 1
    disputes.append({
        "id": dispute_id_seq,
        "booking_id": b_a5_id,
        "sender_id": s_main_2["id"],
        "dispute_type": "WRONG_ABSENT",
        "reason": "Tôi có đến tập và check-in tại quầy lễ tân lúc 7h55, nhưng mạng wifi phòng tập lỗi khiến mã OTP không đồng bộ được trên ứng dụng, dẫn đến bị tính vắng mặt và trừ buổi tập vô lý.",
        "evidence_url": "/app/static/uploads/bien_lai_checkin_letan.jpg",
        "counter_evidence_url": "/app/static/uploads/xac_nhan_hlv_dung.jpg",
        "counter_argument": "Tôi xác nhận học viên Nguyễn Văn A có mặt đúng giờ. Lúc đó mạng wifi tại cơ sở bị mất kết nối nên không thể đồng bộ mã OTP lên máy chủ. Đề nghị Admin hoàn lại buổi tập cho học viên.",
        "status": "RESOLVED_REFUND",
        "admin_notes": "Ban quản trị đã đối soát camera quầy lễ tân và xác nhận của HLV Bùi Anh Dũng. Phán quyết: Hủy ghi nhận vắng mặt, hoàn trả 01 buổi tập khả dụng cho học viên Nguyễn Văn A.",
        "resolved_at": "2026-11-18 14:00:00",
        "created_at": "2026-11-17 10:00:00"
    })
    dispute_id_seq += 1

    # Ca 6: CONFIRMED (Ngày mai 21/11 14:00 - 15:00) với PT 1 (Cường) - CÓ MÃ OTP!
    b_a6_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a6_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 10,
        "student_id": s_main_2["id"],
        "pt_id": 1,
        "slot_start_time": datetime(2026, 11, 21, 14, 0),
        "session_fee": 300000.0,
        "status": "CONFIRMED",
        "student_note": "Tập trung nâng cao nhịp tim và bài Burpee",
        "created_at": "2026-11-20 09:00:00"
    })

    # Ca 7: CONFIRMED (Ngày kia 22/11 09:30 - 10:30) với PT 4 (Dũng) - CÓ MÃ OTP!
    b_a7_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a7_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 5,
        "student_id": s_main_2["id"],
        "pt_id": 4,
        "slot_start_time": datetime(2026, 11, 22, 9, 30),
        "session_fee": 250000.0,
        "status": "CONFIRMED",
        "student_note": "Bài tập Pilates mở khớp hông và kéo giãn cột sống",
        "created_at": "2026-11-20 10:00:00"
    })

    # Ca 8: PENDING (23/11 15:30 - 16:30) với PT 1 (Cường) - CHỜ HLV DUYỆT!
    b_a8_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a8_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 10,
        "student_id": s_main_2["id"],
        "pt_id": 1,
        "slot_start_time": datetime(2026, 11, 23, 15, 30),
        "session_fee": 300000.0,
        "status": "PENDING",
        "student_note": "Yêu cầu tập nâng cao bài Kettlebell",
        "created_at": "2026-11-20 14:00:00"
    })

    # Ca 9: PENDING (24/11 17:30 - 18:30) với PT 4 (Dũng) - CHỜ HLV DUYỆT!
    b_a9_id = booking_id_seq
    booking_id_seq += 1
    bookings.append({
        "id": b_a9_id,
        "booking_type": "PACKAGE",
        "enrollment_id": 5,
        "student_id": s_main_2["id"],
        "pt_id": 4,
        "slot_start_time": datetime(2026, 11, 24, 17, 30),
        "session_fee": 250000.0,
        "status": "PENDING",
        "student_note": "Ca tập phục hồi cơ thắt lưng và vai gáy",
        "created_at": "2026-11-20 15:00:00"
    })

    # =========================================================================
    # 6. WORKOUT PLANS & WORKOUTS
    # =========================================================================
    workout_plans = []
    workouts = []
    plan_id_seq = 1

    # Giáo án 1 cho Hợp đồng 1 (Tăng cơ Thể hình)
    wp1 = {
        "id": plan_id_seq,
        "enrollment_id": e1["id"],
        "title": "Giáo án Tăng cơ Thể hình 4 Tuần - HLV Cường",
        "goal": "Tối ưu phì đại cơ ngực và tay sau, hoàn thiện form Bench Press",
        "start_date": "2026-11-01",
        "end_date": "2026-11-30",
        "created_at": "2026-11-01 10:00:00"
    }
    workout_plans.append(wp1)

    wo_list_1 = [
        (1, "Barbell Bench Press", "Ngực", 4, 10, 60.0, 90, "https://www.youtube.com/watch?v=rT7DgCr-3pg"),
        (2, "Incline Dumbbell Press", "Ngực trên", 3, 12, 20.0, 60, "https://www.youtube.com/watch?v=8iPEnn-ltC8"),
        (3, "Dips (Xà kép ngực)", "Ngực dưới & Tay sau", 3, 10, None, 60, "https://www.youtube.com/watch?v=2z8JmcrW-As"),
        (4, "Cable Tricep Pushdown", "Tay sau", 4, 15, 25.0, 45, "https://www.youtube.com/watch?v=2-LAMcpzODU"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_1:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    # Giáo án 2 cho Hợp đồng 2 (Yoga / Pilates)
    wp2 = {
        "id": plan_id_seq,
        "enrollment_id": e2["id"],
        "title": "Giáo án Pilates Chỉnh dáng Cột sống & Siết eo",
        "goal": "Tạo rãnh bụng 11, thắt chặt khung chậu và khắc phục gù lưng",
        "start_date": "2026-11-05",
        "end_date": "2026-12-05",
        "created_at": "2026-11-05 11:00:00"
    }
    workout_plans.append(wp2)

    wo_list_2 = [
        (1, "Pilates Hundred (Thở kích hoạt Core)", "Cơ bụng sâu", 3, 100, None, 45, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (2, "Pelvic Bridge (Cầu nâng mông siết chậu)", "Cơ sàn chậu & Mông", 4, 15, None, 45, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (3, "Cat-Cow Stretch (Mèo bò kéo giãn lưng)", "Cột sống & Vai", 3, 12, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_2:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    # Giáo án 3 & 4 cho Hợp đồng 5 (Pilates của Nguyễn Văn A)
    wp3 = {
        "id": plan_id_seq,
        "enrollment_id": 5,
        "title": "Giáo Án Pilates Mat Cân Bằng Cột Sống & Mở Khớp Hông (Tháng 1)",
        "goal": "Mở khớp vai, kéo giãn cơ thắt lưng và thiết lập hơi thở lồng ngực chuẩn Pilates",
        "start_date": "2026-11-01",
        "end_date": "2026-11-30",
        "created_at": "2026-11-01 10:00:00"
    }
    workout_plans.append(wp3)
    wo_list_3 = [
        (1, "The Hundred (Trăm nhịp thở kích hoạt cơ lõi sâu)", "Cơ bụng ngang sâu", 1, 100, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (2, "Pilates Roll Up (Cuộn cột sống từng đốt)", "Cột sống & Cơ bụng", 3, 8, None, 45, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (3, "Single Leg Circles (Xoay tròn chân linh hoạt khớp hông)", "Khớp hông & Khung chậu", 3, 10, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (4, "Swan Dive (Thiên nga uốn cong lưng mở ngực)", "Cơ dựng gai sống & Lưng trên", 3, 8, None, 45, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (5, "Criss-Cross (Xoắn chéo siết eo thon gọn)", "Cơ chéo bụng & Vòng eo", 3, 16, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_3:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    wp4 = {
        "id": plan_id_seq,
        "enrollment_id": 5,
        "title": "Giáo Án Định Hình Đường Cong & Tăng Cường Khung Chậu (Tháng 2)",
        "goal": "Tạo dáng chữ S tự nhiên, siết cơ sàn chậu và cải thiện tư thế đứng",
        "start_date": "2026-12-01",
        "end_date": "2026-12-31",
        "created_at": "2026-11-01 11:00:00"
    }
    workout_plans.append(wp4)
    wo_list_4 = [
        (1, "Pilates Teaser (Nâng chân chữ V thăng bằng)", "Toàn bộ cơ Core & Hông", 3, 6, None, 60, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (2, "Side Kick Series (Đá chân nghiêng thon gọn hông)", "Mông nhỡ & Đùi ngoài", 3, 15, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (3, "Spine Stretch Forward (Kéo giãn lưng về phía trước)", "Lưng dưới & Gân kheo", 3, 8, None, 30, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
        (4, "Swimming Pilates (Bơi cạn tăng sức mạnh thân sau)", "Cơ lưng, Mông & Đùi sau", 3, 30, None, 45, "https://www.youtube.com/watch?v=v7AYKMP6rOE"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_4:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    # Giáo án 5 & 6 cho Hợp đồng 10 (HIIT Đốt mỡ của Nguyễn Văn A)
    wp5 = {
        "id": plan_id_seq,
        "enrollment_id": 10,
        "title": "Giáo Án HIIT & Tabata Đốt Mỡ Thần Tốc (Giai đoạn 1: Tuần 1 - 2)",
        "goal": "Kích hoạt chuyển hóa trao đổi chất, tăng sức bền tim mạch và đốt mỡ toàn thân",
        "start_date": "2026-11-01",
        "end_date": "2026-11-15",
        "created_at": "2026-11-01 10:00:00"
    }
    workout_plans.append(wp5)
    wo_list_5 = [
        (1, "Burpees Bật Cao (Nhảy burpee toàn thân)", "Toàn thân (Full Body)", 4, 15, None, 45, "https://www.youtube.com/watch?v=TU8QYVW0gDU"),
        (2, "Mountain Climbers (Leo núi kích hoạt bụng)", "Cơ bụng & Hông (Core & Abs)", 4, 20, None, 30, "https://www.youtube.com/watch?v=nmwgirgXLYM"),
        (3, "Kettlebell Swings (Vung tạ ấm bộc phát)", "Mông & Đùi sau", 4, 16, 12.0, 45, "https://www.youtube.com/watch?v=sSESeQEqu28"),
        (4, "Jump Squat (Squat bật nhảy)", "Cơ tứ đầu đùi & Bắp chân", 4, 15, None, 45, "https://www.youtube.com/watch?v=DeZXsfnf3tY"),
        (5, "Plank Shoulder Taps (Plank chạm vai siết bụng)", "Cơ lõi & Vai", 3, 20, None, 30, "https://www.youtube.com/watch?v=gKA_gI0H3rA"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_5:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    wp6 = {
        "id": plan_id_seq,
        "enrollment_id": 10,
        "title": "Giáo Án Core & Siết Mỡ Tầng Sâu (Giai đoạn 2: Tuần 3 - 4)",
        "goal": "Tối ưu hóa đốt calo sau tập (EPOC), hình thành múi bụng và tăng độ dẻo dai",
        "start_date": "2026-11-16",
        "end_date": "2026-11-30",
        "created_at": "2026-11-01 11:00:00"
    }
    workout_plans.append(wp6)
    wo_list_6 = [
        (1, "Battle Rope Slams (Đập dây thừng thể lực)", "Vai, Cánh tay & Tim mạch", 4, 30, None, 45, "https://www.youtube.com/watch?v=842vF_b-mOQ"),
        (2, "Dumbbell Thrusters (Squat đẩy tạ đôi)", "Đùi trước & Vai", 4, 12, 8.0, 60, "https://www.youtube.com/watch?v=L219ltL15zk"),
        (3, "Bicycle Crunches (Gập bụng đạp xe)", "Cơ liên sườn & Bụng dưới", 4, 20, None, 30, "https://www.youtube.com/watch?v=9FGilxCbdz8"),
        (4, "Box Jump (Bật nhảy lên bục gỗ)", "Sức bật đùi & Mông", 4, 12, None, 60, "https://www.youtube.com/watch?v=52r_Ul5k03g"),
    ]
    for ord_num, name, muscle, sets, reps, wt, rest, vid in wo_list_6:
        workouts.append({
            "plan_id": plan_id_seq,
            "exercise_order": ord_num,
            "exercise_name": name,
            "target_muscle": muscle,
            "sets": sets,
            "reps": reps,
            "weight_kg": wt,
            "rest_seconds": rest,
            "video_demo_url": vid
        })
    plan_id_seq += 1

    # =========================================================================
    # 7. WALLET AUDIT LOGS (Tạo audit logs cho ví)
    # =========================================================================
    wallet_audit_logs = []
    # Audit log cho Minh Anh (wallet_id = main_student_id)
    wallet_audit_logs.append({
        "wallet_id": main_student_id,
        "seq_no": 1,
        "old_balance": 0.0,
        "new_balance": 25000000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "TOPUP",
        "reason": "Nạp tiền vào ví qua chuyển khoản ngân hàng",
        "created_at": "2026-11-01 08:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": main_student_id,
        "seq_no": 2,
        "old_balance": 25000000.0,
        "new_balance": 21400000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "PAYMENT",
        "reason": "Mua khóa học Khởi Động Nhập Môn 12 Buổi - HLV Cường",
        "created_at": "2026-11-01 09:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": main_student_id,
        "seq_no": 3,
        "old_balance": 21400000.0,
        "new_balance": 14200000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "PAYMENT",
        "reason": "Mua gói Pilates Chỉnh Dáng & Cột Sống - HLV Hà",
        "created_at": "2026-11-05 09:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": main_student_id,
        "seq_no": 4,
        "old_balance": 14200000.0,
        "new_balance": 14350000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "COMPENSATION",
        "reason": "Bồi thường ca tập do HLV hủy lịch",
        "created_at": "2026-11-10 14:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": main_student_id,
        "seq_no": 5,
        "old_balance": 14350000.0,
        "new_balance": 14650000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "REFUND",
        "reason": "Hoàn tiền ca tập hủy hợp lệ",
        "created_at": "2026-11-12 16:30:00"
    })

    # Audit log cho Nguyễn Văn A (wallet_id = s_main_2["id"] = 53)
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 1,
        "old_balance": 0.0,
        "new_balance": 10000000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "TOPUP",
        "reason": "Nạp tiền vào ví qua chuyển khoản Vietcombank",
        "created_at": "2026-11-10 08:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 2,
        "old_balance": 10000000.0,
        "new_balance": 5500000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "PAYMENT",
        "reason": "Thanh toán Khóa Đốt Mỡ Cấp Tốc HIIT 16 Buổi - HLV Cường",
        "created_at": "2026-11-10 09:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 3,
        "old_balance": 5500000.0,
        "new_balance": 12400000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "TOPUP",
        "reason": "Nạp tiền vào ví qua Thẻ tín dụng Visa",
        "created_at": "2026-11-12 10:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 4,
        "old_balance": 12400000.0,
        "new_balance": 7400000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "PAYMENT",
        "reason": "Thanh toán Gói Pilates Chỉnh Dáng & Cột Sống 20 Buổi - HLV Dũng",
        "created_at": "2026-11-12 11:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 5,
        "old_balance": 7400000.0,
        "new_balance": 7650000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "REFUND",
        "reason": "Hoàn tiền 01 buổi tập do phân xử khiếu nại thành công",
        "created_at": "2026-11-18 14:00:00"
    })
    wallet_audit_logs.append({
        "wallet_id": s_main_2["id"],
        "seq_no": 6,
        "old_balance": 7650000.0,
        "new_balance": 7700000.0,
        "old_locked_balance": 0.0,
        "new_locked_balance": 0.0,
        "action_type": "COMPENSATION",
        "reason": "Nhận tiền bồi thường phân xử từ Ban quản trị",
        "created_at": "2026-11-18 14:00:00"
    })

    # =========================================================================
    # 8. CHAT MESSAGES
    # =========================================================================
    chat_messages = []
    chat_id_seq = 1
    pt1_uid = pt_profile_map[1]["user_id"]
    pt4_uid = pt_profile_map[4]["user_id"]
    chats_raw = [
        (main_student_id, pt1_uid, "Chào anh Cường, em vừa đăng ký khóa tập 12 buổi của anh ạ!", "2026-11-01 10:15:00"),
        (pt1_uid, main_student_id, "Chào Minh Anh nhé! Anh rất vui được đồng hành cùng em. Em đã có kinh nghiệm tập gym trước đây chưa?", "2026-11-01 10:20:00"),
        (main_student_id, pt1_uid, "Dạ em mới tập tạ đơn ở nhà một ít thôi ạ, form tạ còn chưa chuẩn lắm.", "2026-11-01 10:22:00"),
        (pt1_uid, main_student_id, "Không sao em, buổi đầu tiên anh sẽ kiểm tra độ linh hoạt khớp và hướng dẫn em từ căn bản nhé!", "2026-11-01 10:25:00"),
        (main_student_id, pt1_uid, "Dạ vâng anh, em đã đặt lịch buổi đầu tiên vào sáng mai rồi ạ.", "2026-11-01 10:28:00"),
        (pt1_uid, main_student_id, "Anh vừa duyệt lịch rồi nhé. Em nhớ mang giày thể thao và bình nước nhé!", "2026-11-01 10:30:00"),
        # Chat của Nguyễn Văn A (id 53) với HLV Cường (id 2) và HLV Dũng (id 5)
        (pt1_uid, s_main_2["id"], "Chào bạn Văn A! Mình đã lên xong giáo án HIIT đốt mỡ cho bạn ở mục Khóa của tôi rồi nhé. Bạn xem trước bài Burpee và Mountain Climbers nhé!", "2026-11-16 09:00:00"),
        (s_main_2["id"], pt1_uid, "Dạ em chào anh Cường, em vừa xem qua giáo án rồi ạ, rất chi tiết và có video dễ hiểu. Chiều mai mình tập ở cơ sở Cầu Giấy đúng không anh?", "2026-11-16 09:15:00"),
        (pt1_uid, s_main_2["id"], "Đúng rồi em nhé, em nhớ uống đủ nước trước 30 phút và mang giày chạy bộ chuyên dụng nhé. Hẹn gặp em!", "2026-11-16 09:20:00"),
        (s_main_2["id"], pt1_uid, "Vâng anh, em sẽ đến đúng giờ ạ!", "2026-11-16 09:25:00"),
        (pt4_uid, s_main_2["id"], "Chào bạn A, giáo án Pilates chỉnh dáng cột sống của bạn đã được cập nhật lộ trình 2 tháng. Buổi tới chúng ta sẽ tập trung vào nhóm cơ thắt lưng và mở khớp hông nhé.", "2026-11-15 14:00:00"),
        (s_main_2["id"], pt4_uid, "Dạ vâng anh Dũng, lưng em dạo này ngồi làm việc văn phòng nhiều bị mỏi, tập bài Pilates Roll Up thấy đỡ hẳn ạ.", "2026-11-15 14:30:00"),
        (pt4_uid, s_main_2["id"], "Tuyệt vời, buổi tới anh sẽ chỉnh thêm form bài The Hundred để cơ bụng sâu kích hoạt tốt hơn nữa nhé!", "2026-11-15 15:00:00"),
    ]
    for s_id, r_id, msg, dt in chats_raw:
        chat_messages.append({
            "id": chat_id_seq,
            "sender_id": s_id,
            "receiver_id": r_id,
            "content": msg,
            "is_read": True,
            "created_at": dt
        })
        chat_id_seq += 1

    # =========================================================================
    # 9. TỔNG HỢP VÀ GHI DỮ LIỆU SQL
    # =========================================================================
    print(f"Tổng hợp: {len(users)} users, {len(pt_profiles)} PTs, {len(courses)} courses, {len(slots)} slots, {len(bookings)} bookings.")

    # 1. users
    sql_lines.append("INSERT INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `role`, `status`, `avatar_url`) VALUES")
    u_vals = [f"({u['id']}, {escape_sql(u['full_name'])}, {escape_sql(u['email'])}, {escape_sql(u['password_hash'])}, {escape_sql(u['phone'])}, {escape_sql(u['role'])}, {escape_sql(u['status'])}, {escape_sql(u['avatar_url'])})" for u in users]
    sql_lines.append(",\n".join(u_vals) + ";\n")

    # 2. wallets
    sql_lines.append("INSERT INTO `wallets` (`id`, `user_id`, `balance`, `locked_balance`) VALUES")
    w_vals = [f"({w['id']}, {w['user_id']}, {w['balance']:.2f}, {w['locked_balance']:.2f})" for w in wallets]
    sql_lines.append(",\n".join(w_vals) + ";\n")

    # 3. pt_profiles
    sql_lines.append("INSERT INTO `pt_profiles` (`id`, `user_id`, `bio`, `specialty`, `experience_years`, `location_pricing_note`, `certificate_url`, `demo_video_url`, `verification_status`) VALUES")
    pt_vals = [f"({p['id']}, {p['user_id']}, {escape_sql(p['bio'])}, {escape_sql(p['specialty'])}, {p['experience_years']}, {escape_sql(p['location_pricing_note'])}, {escape_sql(p['certificate_url'])}, {escape_sql(p['demo_video_url'])}, {escape_sql(p['verification_status'])})" for p in pt_profiles]
    sql_lines.append(",\n".join(pt_vals) + ";\n")

    # 4. pt_locations
    sql_lines.append("INSERT INTO `pt_locations` (`id`, `pt_id`, `location_name`) VALUES")
    loc_vals = [f"({l['id']}, {l['pt_id']}, {escape_sql(l['location_name'])})" for l in pt_locations_data]
    sql_lines.append(",\n".join(loc_vals) + ";\n")

    # 5. courses
    sql_lines.append("INSERT INTO `courses` (`id`, `pt_id`, `title`, `description`, `total_sessions`, `validity_days`, `base_price`, `status`) VALUES")
    c_vals = [f"({c['id']}, {c['pt_id']}, {escape_sql(c['title'])}, {escape_sql(c['description'])}, {c['total_sessions']}, {c['validity_days']}, {c['base_price']:.2f}, {escape_sql(c['status'])})" for c in courses]
    sql_lines.append(",\n".join(c_vals) + ";\n")

    # 6. enrollments
    sql_lines.append("INSERT INTO `enrollments` (`id`, `student_id`, `course_id`, `training_location`, `final_price`, `total_sessions`, `remaining_sessions`, `start_date`, `end_date`, `contract_url`, `status`) VALUES")
    enr_vals = [f"({e['id']}, {e['student_id']}, {e['course_id']}, {escape_sql(e['training_location'])}, {e['final_price']:.2f}, {e['total_sessions']}, {e['remaining_sessions']}, {escape_sql(e['start_date'])}, {escape_sql(e['end_date'])}, {escape_sql(e['contract_url'])}, {escape_sql(e['status'])})" for e in enrollments]
    sql_lines.append(",\n".join(enr_vals) + ";\n")

    # 7. availability_slots (Weak entity: PRIMARY KEY (pt_id, start_time))
    sql_lines.append("INSERT INTO `availability_slots` (`pt_id`, `start_time`, `end_time`, `status`) VALUES")
    sl_vals = [f"({s['pt_id']}, '{s['start_time'].strftime('%Y-%m-%d %H:%M:%S')}', '{s['end_time'].strftime('%Y-%m-%d %H:%M:%S')}', {escape_sql(s['status'])})" for s in slots]
    sql_lines.append(",\n".join(sl_vals) + ";\n")

    # 8. bookings (Composite FK: pt_id, slot_start_time)
    sql_lines.append("INSERT INTO `bookings` (`id`, `booking_type`, `enrollment_id`, `student_id`, `pt_id`, `slot_start_time`, `session_fee`, `status`, `student_note`, `created_at`) VALUES")
    bk_vals = [f"({b['id']}, {escape_sql(b['booking_type'])}, {escape_sql(b['enrollment_id'])}, {b['student_id']}, {b['pt_id']}, '{b['slot_start_time'].strftime('%Y-%m-%d %H:%M:%S')}', {b['session_fee']:.2f}, {escape_sql(b['status'])}, {escape_sql(b['student_note'])}, {escape_sql(b['created_at'])})" for b in bookings]
    sql_lines.append(",\n".join(bk_vals) + ";\n")

    # 9. attendances
    if attendances:
        sql_lines.append("INSERT INTO `attendance` (`id`, `booking_id`, `check_in_time`, `check_out_time`, `verification_method`, `student_confirmed`, `pt_confirmed`, `status`) VALUES")
        att_vals = [f"({a['id']}, {a['booking_id']}, {escape_sql(a['check_in_time'])}, {escape_sql(a['check_out_time'])}, {escape_sql(a['verification_method'])}, {escape_sql(a['student_confirmed'])}, {escape_sql(a['pt_confirmed'])}, {escape_sql(a['status'])})" for a in attendances]
        sql_lines.append(",\n".join(att_vals) + ";\n")

    # 10. reviews
    if reviews:
        sql_lines.append("INSERT INTO `reviews` (`id`, `booking_id`, `rating`, `comment`, `created_at`) VALUES")
        rev_vals = [f"({r['id']}, {r['booking_id']}, {r['rating']}, {escape_sql(r['comment'])}, {escape_sql(r['created_at'])})" for r in reviews]
        sql_lines.append(",\n".join(rev_vals) + ";\n")

    # 11. cancellations
    if cancellations:
        sql_lines.append("INSERT INTO `cancellations` (`id`, `booking_id`, `cancelled_by_id`, `reason`, `evidence_url`, `status`, `cancelled_at`) VALUES")
        can_vals = [f"({c['id']}, {c['booking_id']}, {escape_sql(c['cancelled_by_id'])}, {escape_sql(c['reason'])}, {escape_sql(c['evidence_url'])}, {escape_sql(c['status'])}, {escape_sql(c['cancelled_at'])})" for c in cancellations]
        sql_lines.append(",\n".join(can_vals) + ";\n")

    # 12. booking_disputes
    if disputes:
        sql_lines.append("INSERT INTO `booking_disputes` (`id`, `booking_id`, `sender_id`, `dispute_type`, `reason`, `evidence_url`, `counter_evidence_url`, `counter_argument`, `status`, `admin_notes`, `resolved_at`, `created_at`) VALUES")
        disp_vals = [f"({d['id']}, {d['booking_id']}, {d['sender_id']}, {escape_sql(d['dispute_type'])}, {escape_sql(d['reason'])}, {escape_sql(d['evidence_url'])}, {escape_sql(d['counter_evidence_url'])}, {escape_sql(d['counter_argument'])}, {escape_sql(d['status'])}, {escape_sql(d['admin_notes'])}, {escape_sql(d['resolved_at'])}, {escape_sql(d['created_at'])})" for d in disputes]
        sql_lines.append(",\n".join(disp_vals) + ";\n")

    # 13. workout_plans
    if workout_plans:
        sql_lines.append("INSERT INTO `workout_plans` (`id`, `enrollment_id`, `title`, `goal`, `start_date`, `end_date`, `created_at`) VALUES")
        wp_vals = [f"({wp['id']}, {wp['enrollment_id']}, {escape_sql(wp['title'])}, {escape_sql(wp['goal'])}, {escape_sql(wp['start_date'])}, {escape_sql(wp['end_date'])}, {escape_sql(wp['created_at'])})" for wp in workout_plans]
        sql_lines.append(",\n".join(wp_vals) + ";\n")

    # 14. workouts (Weak entity: PRIMARY KEY (plan_id, exercise_order))
    if workouts:
        sql_lines.append("INSERT INTO `workouts` (`plan_id`, `exercise_order`, `exercise_name`, `target_muscle`, `sets`, `reps`, `weight_kg`, `rest_seconds`, `video_demo_url`) VALUES")
        wo_vals = [f"({w['plan_id']}, {w['exercise_order']}, {escape_sql(w['exercise_name'])}, {escape_sql(w['target_muscle'])}, {w['sets']}, {w['reps']}, {escape_sql(w['weight_kg'])}, {w['rest_seconds']}, {escape_sql(w['video_demo_url'])})" for w in workouts]
        sql_lines.append(",\n".join(wo_vals) + ";\n")

    # 15. payments
    if payments:
        sql_lines.append("INSERT INTO `payments` (`id`, `wallet_id`, `enrollment_id`, `amount`, `payment_type`, `payment_method`, `status`, `transaction_ref`, `created_at`) VALUES")
        p_vals = [f"({p['id']}, {p['wallet_id']}, {escape_sql(p['enrollment_id'])}, {p['amount']:.2f}, {escape_sql(p['payment_type'])}, {escape_sql(p['payment_method'])}, {escape_sql(p['status'])}, {escape_sql(p['transaction_ref'])}, {escape_sql(p['created_at'])})" for p in payments]
        sql_lines.append(",\n".join(p_vals) + ";\n")

    # 16. wallet_audit_logs (Weak entity: PRIMARY KEY (wallet_id, seq_no))
    if wallet_audit_logs:
        sql_lines.append("INSERT INTO `wallet_audit_logs` (`wallet_id`, `seq_no`, `old_balance`, `new_balance`, `old_locked_balance`, `new_locked_balance`, `action_type`, `reason`, `created_at`) VALUES")
        wal_vals = [f"({l['wallet_id']}, {l['seq_no']}, {l['old_balance']:.2f}, {l['new_balance']:.2f}, {l['old_locked_balance']:.2f}, {l['new_locked_balance']:.2f}, {escape_sql(l['action_type'])}, {escape_sql(l['reason'])}, {escape_sql(l['created_at'])})" for l in wallet_audit_logs]
        sql_lines.append(",\n".join(wal_vals) + ";\n")

    # 17. chat_messages
    if chat_messages:
        sql_lines.append("INSERT INTO `chat_messages` (`id`, `sender_id`, `receiver_id`, `content`, `is_read`, `created_at`) VALUES")
        cm_vals = [f"({m['id']}, {m['sender_id']}, {m['receiver_id']}, {escape_sql(m['content'])}, {escape_sql(m['is_read'])}, {escape_sql(m['created_at'])})" for m in chat_messages]
        sql_lines.append(",\n".join(cm_vals) + ";\n")

    # 18. ĐỒNG BỘ CHỈ SỐ ĐÁNH GIÁ CỦA PT THEO REVIEWS THỰC TẾ (Thuộc tính dẫn xuất BCNF tính động)
    sql_lines.append("-- 18. ĐỒNG BỘ CHỈ SỐ ĐÁNH GIÁ CỦA PT THEO REVIEWS THỰC TẾ (Thuộc tính dẫn xuất BCNF tính động)")
    sql_lines.append("-- (Chỉ số đánh giá được tính động qua VIEW v_pt_profile_details)")

    # 19. ĐỒNG BỘ TRẠNG THÁI KHUNG GIỜ VỚI BOOKING
    sql_lines.append("-- 19. ĐỒNG BỘ TRẠNG THÁI KHUNG GIỜ VỚI BOOKING")
    sql_lines.append("UPDATE `availability_slots` s")
    sql_lines.append("JOIN `bookings` b ON s.`pt_id` = b.`pt_id` AND s.`start_time` = b.`slot_start_time`")
    sql_lines.append("SET s.`status` = 'BOOKED'")
    sql_lines.append("WHERE b.`status` IN ('PENDING', 'CONFIRMED', 'COMPLETED');")
    sql_lines.append("")
    sql_lines.append("UPDATE `availability_slots` s")
    sql_lines.append("JOIN `bookings` b ON s.`pt_id` = b.`pt_id` AND s.`start_time` = b.`slot_start_time`")
    sql_lines.append("SET s.`status` = 'AVAILABLE'")
    sql_lines.append("WHERE b.`status` = 'CANCELLED';")

    full_sql = "\n".join(sql_lines)
    for out_path in OUTPUT_FILES:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_sql)
        print(f"Đã lưu thành công dữ liệu mẫu tại: {out_path}")

if __name__ == "__main__":
    main()
