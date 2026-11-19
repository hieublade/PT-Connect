"""
seed_30_pts.py
Script nạp 30 Huấn luyện viên mẫu phong phú và toàn diện cho PT Connect.
Mỗi PT có:
- Họ tên, tiểu sử, nhóm chuyên môn chi tiết
- Khu vực nhận dạy (Cầu Giấy, Ba Đình, Đống Đa, Thanh Xuân, Hai Bà Trưng, Tây Hồ, Nam Từ Liêm,...)
- Số năm kinh nghiệm (1 đến 12 năm), đánh giá sao (4.2 đến 5.0)
- Link video demo YouTube tập luyện thể hình, calisthenics, powerlifting, yoga, boxing, v.v.
- Tối thiểu 1 khóa học mẫu và khung giờ rảnh (AVAILABLE)
- Tuân thủ chặt chẽ chuẩn BCNF và lưu bằng UTF-8 không lỗi font chữ.
"""

from db_repository import db_repo

PT_DATA = [
    # Nhóm 1: Tăng cơ & Giảm mỡ Thể hình (Bodybuilding & Fat Loss)
    {
        "name": "Lê Hoàng Cường",
        "email": "pt.hoangc@ptconnect.vn",
        "phone": "0901000001",
        "exp": 6,
        "rating": 4.8,
        "reviews": 18,
        "specialties": "Tăng cơ, Giảm mỡ, Thể hình, Dinh dưỡng thể thao",
        "bio": "Chuyên gia thể hình cá nhân và tăng cơ giảm mỡ chuẩn khoa học. Hơn 6 năm kinh nghiệm huấn luyện thi đấu và xây dựng thực đơn macro.",
        "locations": ["FitZone Thanh Xuân", "Phòng Cali Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=aclHkVaku9U",
        "note": "Dạy tại nhà phụ thu 20% phí di chuyển",
        "course_title": "Khóa Khởi Động Nhập Môn 12 Buổi - HLV Cường",
        "course_price": 3600000,
        "course_sessions": 12,
        "course_desc": "Dành cho người mới bắt đầu làm quen với phòng gym và thể lực nền tảng.",
    },
    {
        "name": "Nguyễn Hoàng Nam",
        "email": "pt.hoangnam@ptconnect.vn",
        "phone": "0901000002",
        "exp": 5,
        "rating": 4.9,
        "reviews": 24,
        "specialties": "Tăng cơ Hypertrophy, Siết mỡ, Thể hình nam nữ",
        "bio": "Cựu vận động viên Men Physique quốc gia, chuyên coaching tăng kích thước cơ bắp và định hình cơ thể săn chắc.",
        "locations": ["Cầu Giấy", "Nam Từ Liêm"],
        "video": "https://www.youtube.com/watch?v=aclHkVaku9U",
        "note": "Hỗ trợ học viên đo InBody định kỳ hàng tuần",
        "course_title": "Gói Hypertrophy Tăng Cơ Cắt Nét 24 Buổi - HLV Nam",
        "course_price": 7200000,
        "course_sessions": 24,
        "course_desc": "Phương pháp Hypertrophy tối ưu phát triển cơ bắp toàn diện.",
    },
    {
        "name": "Trần Tuấn Anh",
        "email": "pt.tuananh@ptconnect.vn",
        "phone": "0901000003",
        "exp": 4,
        "rating": 4.7,
        "reviews": 15,
        "specialties": "Giảm mỡ cấp tốc, HIIT, Thể lực toàn thân",
        "bio": "Huấn luyện viên thể lực năng động, chuyên giáo án cường độ cao đốt mỡ và tăng cường sức bền hệ tuần hoàn.",
        "locations": ["Đống Đa", "Ba Đình"],
        "video": "https://www.youtube.com/watch?v=sw_Rvhw2qf4",
        "note": "Tặng kèm thực đơn giảm cân 4 tuần",
        "course_title": "Khóa Đốt Mỡ Cấp Tốc HIIT 16 Buổi - HLV Tuấn Anh",
        "course_price": 4800000,
        "course_sessions": 16,
        "course_desc": "Đốt cháy calo tối đa với các bài tập cường độ cao kết hợp tạ đơn.",
    },
    {
        "name": "Đặng Quốc Huy",
        "email": "pt.quochuy@ptconnect.vn",
        "phone": "0901000004",
        "exp": 7,
        "rating": 4.9,
        "reviews": 32,
        "specialties": "Thể hình chuyên sâu, Tăng cơ không mỡ, Dinh dưỡng macro",
        "bio": "Hơn 7 năm dẫn dắt hàng trăm học viên cải thiện vóc dáng từ gầy ốm sang cơ bắp vạm vỡ.",
        "locations": ["Thanh Xuân", "Hà Đông"],
        "video": "https://www.youtube.com/watch?v=aclHkVaku9U",
        "note": "Cam kết đạt mục tiêu nếu theo sát thực đơn",
        "course_title": "Lộ Trình Tăng Cơ Nạc Lean Body 20 Buổi - HLV Huy",
        "course_price": 6000000,
        "course_sessions": 20,
        "course_desc": "Tập trung các nhóm cơ chính Ngực - Lưng - Chân với bài tập đa khớp.",
    },
    {
        "name": "Vũ Minh Quân",
        "email": "pt.minhquan@ptconnect.vn",
        "phone": "0901000005",
        "exp": 3,
        "rating": 4.6,
        "reviews": 11,
        "specialties": "Giảm mỡ bụng, Chỉnh tư thế cho người thừa cân",
        "bio": "Tận tâm, kiên nhẫn, chuyên các bài tập bảo vệ khớp gối cho người có chỉ số BMI cao muốn giảm cân an toàn.",
        "locations": ["Hai Bà Trưng", "Hoàn Kiếm"],
        "video": "https://www.youtube.com/watch?v=sw_Rvhw2qf4",
        "note": "Khởi động kỹ và kiểm tra tim mạch trước mỗi buổi",
        "course_title": "Khóa Giảm Cân An Toàn Cho Người Mới 12 Buổi - HLV Quân",
        "course_price": 3600000,
        "course_sessions": 12,
        "course_desc": "Giáo án vận động vừa sức giúp giảm mỡ thừa và bảo vệ hệ xương khớp.",
    },

    # Nhóm 2: Calisthenics & Thể hình tự thân (Bodyweight & Mobility)
    {
        "name": "Phạm Minh Dũng",
        "email": "pt.minhd@ptconnect.vn",
        "phone": "0901000006",
        "exp": 4,
        "rating": 4.8,
        "reviews": 21,
        "specialties": "Calisthenics, Chỉnh sửa tư thế, Tăng thể lực, Đau vai gáy",
        "bio": "Huấn luyện viên Calisthenics và chỉnh sửa tư thế cột sống, cải thiện gù lưng đau mỏi vai gáy cho dân công sở.",
        "locations": ["Khu vực Đống Đa", "Studio cá nhân tại Thanh Xuân"],
        "video": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "note": "Dụng cụ xà và vòng treo mang theo tận nơi",
        "course_title": "Gói Calisthenics & Thể Hình Tự Thân 24 Buổi - HLV Dũng",
        "course_price": 7200000,
        "course_sessions": 24,
        "course_desc": "Làm chủ cơ thể với xà đơn, xà kép và các chuyển động thăng bằng.",
    },
    {
        "name": "Bùi Thế Long",
        "email": "pt.thelong@ptconnect.vn",
        "phone": "0901000007",
        "exp": 5,
        "rating": 4.9,
        "reviews": 19,
        "specialties": "Calisthenics nâng cao, Muscle Up, Handstand, Giãn cơ",
        "bio": "Chuyên gia kỹ thuật Handstand (trồng chuối) và Muscle Up. Hướng dẫn kiểm soát nhóm cơ cốt lõi (Core) hoàn hảo.",
        "locations": ["Tây Hồ", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "note": "Phù hợp cả người mới tập từ hít xà cơ bản",
        "course_title": "Khóa Chinh Phục Handstand & Calisthenics 16 Buổi - HLV Long",
        "course_price": 5200000,
        "course_sessions": 16,
        "course_desc": "Luyện tập thăng bằng vai cổ tay và sức mạnh toàn thân.",
    },
    {
        "name": "Hoàng Khắc Tiệp",
        "email": "pt.khactiep@ptconnect.vn",
        "phone": "0901000008",
        "exp": 3,
        "rating": 4.7,
        "reviews": 12,
        "specialties": "Street Workout, Sức mạnh tự thân, Sức bền cơ bắp",
        "bio": "Tập luyện ngoài trời hoặc tại nhà không cần tạ, tối ưu sức mạnh dẻo dai và phản xạ cơ bắp nhanh nhạy.",
        "locations": ["Thanh Xuân", "Hoàng Mai"],
        "video": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "note": "Không gian tập thoáng mát ngoài công viên hoặc tại nhà",
        "course_title": "Street Workout Cơ Bản Cho Người Bận Rộn 12 Buổi - HLV Tiệp",
        "course_price": 3500000,
        "course_sessions": 12,
        "course_desc": "Giáo án vận động tự thân hiệu quả cao không cần tạ.",
    },
    {
        "name": "Ngô Gia Bảo",
        "email": "pt.giabao@ptconnect.vn",
        "phone": "0901000009",
        "exp": 6,
        "rating": 4.9,
        "reviews": 27,
        "specialties": "Chỉnh sửa gù lưng, Thoát vị nhẹ, Calisthenics trị liệu",
        "bio": "Kết hợp Calisthenics và bài tập kích hoạt thần kinh cơ để phục hồi chức năng vận động cho dân văn phòng ngồi nhiều.",
        "locations": ["Cầu Giấy", "Ba Đình"],
        "video": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "note": "Kiểm tra độ linh hoạt khớp trước khi tập",
        "course_title": "Phục Hồi Cột Sống & Cân Chỉnh Dáng 16 Buổi - HLV Gia Bảo",
        "course_price": 5600000,
        "course_sessions": 16,
        "course_desc": "Khắc phục đau mỏi vai gáy, lệch hông và gù lưng.",
    },

    # Nhóm 3: Powerlifting & Sức mạnh tối đa (Strength & Heavy Lifting)
    {
        "name": "Trần Quốc Bảo",
        "email": "pt.quocbao@ptconnect.vn",
        "phone": "0901000010",
        "exp": 5,
        "rating": 4.8,
        "reviews": 17,
        "specialties": "Powerlifting, Sức mạnh, Tăng cân, Bulking, Squat Bench Deadlift",
        "bio": "Chuyên gia Powerlifting và phát triển sức mạnh tối đa (Squat, Bench, Deadlift). Đạt chứng chỉ NASM CPT quốc tế.",
        "locations": ["Phòng tập Elite Fitness Tây Hồ", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=bEv6CCg2BC8",
        "note": "Trang bị đầy đủ đai lưng và bảo hộ đầu gối",
        "course_title": "Powerlifting Chuyên Sâu Squat-Bench-Deadlift 24 Buổi - HLV Bảo",
        "course_price": 7500000,
        "course_sessions": 24,
        "course_desc": "Xây dựng nền tảng sức mạnh thô và tối ưu hóa 3 chuyển động chính.",
    },
    {
        "name": "Lương Đình Trọng",
        "email": "pt.dinhtrong@ptconnect.vn",
        "phone": "0901000011",
        "exp": 8,
        "rating": 5.0,
        "reviews": 36,
        "specialties": "Sức mạnh bộc phát, Powerlifting thi đấu, Chỉnh form tạ nặng",
        "bio": "Vận động viên thi đấu Powerlifting chuyên nghiệp với kỷ lục tổng tạ trên 600kg. Chuyên chỉnh form chống chấn thương.",
        "locations": ["Thanh Xuân", "Đống Đa"],
        "video": "https://www.youtube.com/watch?v=bEv6CCg2BC8",
        "note": "Kiểm soát an toàn 100% trong từng rep tạ nặng",
        "course_title": "Khóa Đột Phá Mức Tạ 1RM Powerlifting 18 Buổi - HLV Trọng",
        "course_price": 6500000,
        "course_sessions": 18,
        "course_desc": "Giáo án Periodization khoa học phá vỡ ngưỡng giới hạn sức mạnh.",
    },
    {
        "name": "Đỗ Mạnh Hùng",
        "email": "pt.manhhung@ptconnect.vn",
        "phone": "0901000012",
        "exp": 6,
        "rating": 4.8,
        "reviews": 23,
        "specialties": "Strength & Conditioning, Tăng cơ tạ nặng, Deadlift an toàn",
        "bio": "Đào tạo bài bản theo giáo trình quốc tế CSCS. Giúp học viên tăng cường sức mạnh toàn diện mà không lo chấn thương.",
        "locations": ["Nam Từ Liêm", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=bEv6CCg2BC8",
        "note": "Phân tích chuyển động qua video quay chậm",
        "course_title": "Strength Training Tăng Thể Lực Tối Đa 20 Buổi - HLV Hùng",
        "course_price": 6200000,
        "course_sessions": 20,
        "course_desc": "Tập trung gia tăng mật độ xương và sức mạnh gân cơ.",
    },

    # Nhóm 4: Pilates & Giảm mỡ nữ & Yoga phục hồi (Pilates, Yoga & Women Fitness)
    {
        "name": "Nguyễn Thu Hà",
        "email": "pt.thuha@ptconnect.vn",
        "phone": "0901000013",
        "exp": 4,
        "rating": 4.9,
        "reviews": 29,
        "specialties": "Giảm mỡ nữ, Yoga, Pilates, Giảm cân sau sinh, Dinh dưỡng Eat Clean",
        "bio": "HLV chuyên sâu Giảm mỡ siết cơ nữ, Pilates, Yoga phục hồi và thon gọn vóc dáng sau sinh. Chứng chỉ Pilates Thụy Sĩ.",
        "locations": ["Phòng tập Yoga Plus Ba Đình", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Kèm tại nhà phụ thu 50k tiền di chuyển",
        "course_title": "Gói Pilates Chỉnh Dáng & Cột Sống 20 Buổi - HLV Hà",
        "course_price": 8000000,
        "course_sessions": 20,
        "course_desc": "Siết cơ bụng sâu, mở rộng khung xương chậu và tạo rãnh bụng 11.",
    },
    {
        "name": "Phan Mai Linh",
        "email": "pt.mailinh@ptconnect.vn",
        "phone": "0901000014",
        "exp": 5,
        "rating": 4.9,
        "reviews": 31,
        "specialties": "Pilates thảm & máy Reformer, Siết eo thon gọn, Định hình mông",
        "bio": "Hơn 5 năm giảng dạy Pilates Reformer cho phái nữ. Chuyên các bài tập siết eo, nâng cung mông và tạo đường cong mềm mại.",
        "locations": ["Tây Hồ", "Ba Đình"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Có phòng tập studio riêng tư cao cấp",
        "course_title": "Pilates Reformer Tạo Dáng Nữ Quyến Rũ 16 Buổi - HLV Linh",
        "course_price": 7200000,
        "course_sessions": 16,
        "course_desc": "Tập luyện chuyên sâu với máy Reformer và dây đàn hồi cao cấp.",
    },
    {
        "name": "Trần Thùy Dung",
        "email": "pt.thuydung@ptconnect.vn",
        "phone": "0901000015",
        "exp": 3,
        "rating": 4.7,
        "reviews": 16,
        "specialties": "Yoga trị liệu, Giảm căng thẳng, Dẻo dai cơ thể, Giãn cơ sâu",
        "bio": "Chứng chỉ 500h Yoga Alliance quốc tế. Giúp học viên giải tỏa stress công việc, thư giãn tâm trí và cơ thể dẻo dai.",
        "locations": ["Đống Đa", "Thanh Xuân"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Cung cấp tinh dầu thơm và thảm tập cao cấp",
        "course_title": "Khóa Yoga Trị Liệu & Giảm Stress 12 Buổi - HLV Dung",
        "course_price": 4200000,
        "course_sessions": 12,
        "course_desc": "Kết hợp thở pranayama và asana phục hồi thể chất tinh thần.",
    },
    {
        "name": "Hoàng Phương Thảo",
        "email": "pt.phuongthao@ptconnect.vn",
        "phone": "0901000016",
        "exp": 4,
        "rating": 4.8,
        "reviews": 22,
        "specialties": "Siết cơ bụng nữ, Tăng cơ mông đùi không to chân, Eat Clean",
        "bio": "Chuyên gia thể hình nữ giúp chị em phụ nữ sở hữu số đo 3 vòng chuẩn chỉnh, tự tin diện trang phục ôm sát.",
        "locations": ["Hai Bà Trưng", "Hoàn Kiếm"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Thiết kế giáo án riêng biệt cho từng tạng người nữ",
        "course_title": "Gói Tăng Vòng 3 & Siết Eo Con Kiến 20 Buổi - HLV Thảo",
        "course_price": 6800000,
        "course_sessions": 20,
        "course_desc": "Kích hoạt nhóm cơ mông tối đa và bảo vệ đùi trước không bị thô.",
    },
    {
        "name": "Đặng Thúy Nga",
        "email": "pt.thuynga@ptconnect.vn",
        "phone": "0901000017",
        "exp": 2,
        "rating": 4.6,
        "reviews": 9,
        "specialties": "Yoga phục hồi chấn thương nhẹ, Giãn cơ văn phòng, Thư giãn",
        "bio": "Huấn luyện viên Yoga nhiệt huyết, chuyên phục hồi căng cứng cơ bắp cho nhân viên ngồi máy tính kéo dài.",
        "locations": ["Cầu Giấy", "Nam Từ Liêm"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Giờ tập linh hoạt vào buổi sáng sớm hoặc trưa",
        "course_title": "Yoga Nhẹ Nhàng Phục Hồi Năng Lượng 10 Buổi - HLV Nga",
        "course_price": 3200000,
        "course_sessions": 10,
        "course_desc": "Các tư thế nhẹ nhàng giãn cơ lưng vai và lưu thông khí huyết.",
    },

    # Nhóm 5: Kickfit, Boxing & Tự vệ (Boxing, Kickfit & Combat Conditioning)
    {
        "name": "Đỗ Tuấn Kiệt",
        "email": "pt.tuankiet@ptconnect.vn",
        "phone": "0901000018",
        "exp": 7,
        "rating": 4.9,
        "reviews": 28,
        "specialties": "Kickfit, Boxing, Cardio đốt mỡ, Tự vệ, Tăng sức bền",
        "bio": "HLV thể lực, Boxing, Kickfit cường độ cao đốt mỡ cấp tốc và phản xạ tự vệ. Hơn 7 năm kinh nghiệm tại Times City.",
        "locations": ["Fit24 Hai Bà Trưng", "Times City"],
        "video": "https://www.youtube.com/watch?v=1bPEqY_4j-w",
        "note": "HLV chuẩn bị sẵn găng tay và đích đấm chất lượng cao",
        "course_title": "Gói Boxing Thể Lực & Xả Stress 16 Buổi - HLV Kiệt",
        "course_price": 5600000,
        "course_sessions": 16,
        "course_desc": "Tập luyện đòn đấm kết hợp di chuyển né đòn đốt mỡ toàn diện.",
    },
    {
        "name": "Vũ Văn Quyền",
        "email": "pt.vanquyen@ptconnect.vn",
        "phone": "0901000019",
        "exp": 6,
        "rating": 4.8,
        "reviews": 20,
        "specialties": "Muay Thai, Kickboxing, Kỹ năng tự vệ đường phố, Đốt mỡ",
        "bio": "Võ sĩ Muay Thai chuyên nghiệp, kết hợp đòn chân, gối, chỏ giúp học viên tăng phản xạ và tiêu hao calo thần tốc.",
        "locations": ["Cầu Giấy", "Đống Đa"],
        "video": "https://www.youtube.com/watch?v=1bPEqY_4j-w",
        "note": "Tập luyện an toàn, không va chạm gây chấn thương",
        "course_title": "Muay Thai Thể Lực & Tự Vệ Thực Chiến 20 Buổi - HLV Quyền",
        "course_price": 6400000,
        "course_sessions": 20,
        "course_desc": "Đốt cháy lên đến 800 calo mỗi buổi tập với đòn chân và đấm kết hợp.",
    },
    {
        "name": "Phạm Hải Đăng",
        "email": "pt.haidang@ptconnect.vn",
        "phone": "0901000020",
        "exp": 4,
        "rating": 4.7,
        "reviews": 14,
        "specialties": "Boxing cơ bản, Footwork, Tăng tốc độ phản xạ, Cardio",
        "bio": "Giảng dạy Boxing chuẩn kỹ thuật từ cách nắm đấm, giữ thăng bằng đến các chuỗi tổ hợp đòn cơ bản.",
        "locations": ["Ba Đình", "Tây Hồ"],
        "video": "https://www.youtube.com/watch?v=1bPEqY_4j-w",
        "note": "Thích hợp cho cả nam và nữ muốn giải tỏa căng thẳng",
        "course_title": "Khóa Nhập Môn Boxing Căn Bản 12 Buổi - HLV Đăng",
        "course_price": 3800000,
        "course_sessions": 12,
        "course_desc": "Học kỹ thuật Jab, Cross, Hook, Uppercut và di chuyển chân.",
    },
    {
        "name": "Nguyễn Hoàng Bách",
        "email": "pt.hoangbach@ptconnect.vn",
        "phone": "0901000021",
        "exp": 5,
        "rating": 4.8,
        "reviews": 18,
        "specialties": "Kickfit giảm mỡ cấp tốc, Săn chắc cơ bụng, Thể lực tim mạch",
        "bio": "HLV Kickfit nhiệt tình, phong cách huấn luyện truyền cảm hứng mạnh mẽ, giúp học viên vượt qua ngưỡng mệt mỏi.",
        "locations": ["Thanh Xuân", "Hà Đông"],
        "video": "https://www.youtube.com/watch?v=1bPEqY_4j-w",
        "note": "Âm nhạc sôi động tạo động lực tập luyện hết mình",
        "course_title": "Kickfit Đốt Mỡ Cường Độ Cao 16 Buổi - HLV Bách",
        "course_price": 5000000,
        "course_sessions": 16,
        "course_desc": "Bài tập đấm đá trên nền nhạc nhịp nhanh giúp săn chắc cơ bắp.",
    },

    # Nhóm 6: Chức năng, Phục hồi & Người cao tuổi (Functional Training & Rehab)
    {
        "name": "Dương Văn Hùng",
        "email": "pt.vanhung@ptconnect.vn",
        "phone": "0901000022",
        "exp": 9,
        "rating": 5.0,
        "reviews": 40,
        "specialties": "Phục hồi sau chấn thương, Khớp gối dây chằng, Functional Training",
        "bio": "Chuyên gia vật lý trị liệu và phục hồi vận động sau mổ dây chằng, bảo dưỡng khớp gối và thoái hóa cột sống.",
        "locations": ["Cầu Giấy", "Tây Hồ"],
        "video": "https://www.youtube.com/watch?v=Dy28eq2PjcM",
        "note": "Theo dõi sát sao từng biên độ chuyển động",
        "course_title": "Phục Hồi Khớp Gối & Cải Thiện Vận Động 16 Buổi - HLV Hùng",
        "course_price": 6800000,
        "course_sessions": 16,
        "course_desc": "Tập tăng cường cơ đùi trước đùi sau nhằm giảm tải áp lực lên khớp gối.",
    },
    {
        "name": "Trịnh Thu Trang",
        "email": "pt.thutrang@ptconnect.vn",
        "phone": "0901000023",
        "exp": 6,
        "rating": 4.9,
        "reviews": 25,
        "specialties": "Tập luyện cho người trung niên, Tăng mật độ xương, Dẻo dai",
        "bio": "Tận tâm chăm sóc sức khỏe thể chất cho phụ huynh và người lớn tuổi. Thiết kế bài tập an toàn, không tạ nặng.",
        "locations": ["Ba Đình", "Đống Đa"],
        "video": "https://www.youtube.com/watch?v=Dy28eq2PjcM",
        "note": "Hướng dẫn thở sâu và kiểm tra huyết áp mỗi buổi",
        "course_title": "Dưỡng Sinh Thể Lực Cho Người Trung Niên 15 Buổi - HLV Trang",
        "course_price": 4500000,
        "course_sessions": 15,
        "course_desc": "Tăng cường sự dẻo dai cơ bắp, thăng bằng và phòng ngừa té ngã.",
    },
    {
        "name": "Lê Đình Thắng",
        "email": "pt.dinhthang@ptconnect.vn",
        "phone": "0901000024",
        "exp": 5,
        "rating": 4.8,
        "reviews": 19,
        "specialties": "Functional Fitness, Bài tập đa hướng, Nâng cao chất lượng sống",
        "bio": "Giúp học viên di chuyển linh hoạt, bê vác đồ đạc nhẹ nhàng trong sinh hoạt hàng ngày mà không sợ đau lưng.",
        "locations": ["Thanh Xuân", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=Dy28eq2PjcM",
        "note": "Tập trung vào chuyển động cơ bản hàng ngày",
        "course_title": "Functional Training Cho Cuộc Sống Năng Động 18 Buổi - HLV Thắng",
        "course_price": 5400000,
        "course_sessions": 18,
        "course_desc": "Tối ưu hóa các chuỗi chuyển động xoay, đẩy, kéo, gập hông tự nhiên.",
    },

    # Nhóm 7: Huấn luyện viên Trẻ Năng Động & Người Mới Bắt Đầu (Beginners & Youth)
    {
        "name": "Ngô Tiến Đạt",
        "email": "pt.tiendat@ptconnect.vn",
        "phone": "0901000025",
        "exp": 3,
        "rating": 4.7,
        "reviews": 13,
        "specialties": "Người mới bắt đầu, Thể dục giảm cân nhẹ nhàng, Thói quen lành mạnh",
        "bio": "HLV trẻ tràn đầy năng lượng, đồng hành cùng bạn từ số 0 để xây dựng thói quen đi gym đều đặn không áp lực.",
        "locations": ["Nam Từ Liêm", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=kGgU8wH3XgA",
        "note": "Hỗ trợ hướng dẫn sử dụng toàn bộ máy móc trong phòng tập",
        "course_title": "Nhập Môn Phòng Gym Cho Người Mới 12 Buổi - HLV Đạt",
        "course_price": 3200000,
        "course_sessions": 12,
        "course_desc": "Nắm vững cách chỉnh máy tạ, nguyên tắc hít thở và các bài tập cơ bản.",
    },
    {
        "name": "Chu Kim Ngân",
        "email": "pt.kimngan@ptconnect.vn",
        "phone": "0901000026",
        "exp": 4,
        "rating": 4.8,
        "reviews": 17,
        "specialties": "Thể dục thẩm mỹ nữ, Tabata, Giảm mỡ toàn thân, Tăng sức bền",
        "bio": "HLV nữ hòa đồng, sôi nổi, tạo không khí tập luyện vui vẻ giúp học viên vượt qua cảm giác mệt mỏi.",
        "locations": ["Hai Bà Trưng", "Đống Đa"],
        "video": "https://www.youtube.com/watch?v=kGgU8wH3XgA",
        "note": "Có thể tập nhóm nhỏ 2-3 người bạn",
        "course_title": "Tabata Vui Nhộn Đốt Mỡ Cùng Bạn Thân 12 Buổi - HLV Ngân",
        "course_price": 3600000,
        "course_sessions": 12,
        "course_desc": "Tập luyện theo nhạc kết hợp các động tác thể dục nhịp điệu đốt mỡ.",
    },
    {
        "name": "Mai Văn Đức",
        "email": "pt.vanduc@ptconnect.vn",
        "phone": "0901000027",
        "exp": 2,
        "rating": 4.6,
        "reviews": 8,
        "specialties": "Tăng thể lực thanh thiếu niên, Phát triển chiều cao, Bổ trợ thể thao",
        "bio": "Chuyên các bài tập kéo giãn xương khớp và tăng cường thể lực cho học sinh, sinh viên phát triển chiều cao tối đa.",
        "locations": ["Cầu Giấy", "Ba Đình"],
        "video": "https://www.youtube.com/watch?v=kGgU8wH3XgA",
        "note": "Giáo án vận động khoa học phù hợp lứa tuổi dậy thì",
        "course_title": "Tăng Chiều Cao & Thể Lực Thanh Thiếu Niên 16 Buổi - HLV Đức",
        "course_price": 4000000,
        "course_sessions": 16,
        "course_desc": "Tập trung các bài tập nhảy bật xà đơn và bơi lội bổ trợ.",
    },
    {
        "name": "Lâm Quốc Khánh",
        "email": "pt.quockhanh@ptconnect.vn",
        "phone": "0901000028",
        "exp": 4,
        "rating": 4.7,
        "reviews": 15,
        "specialties": "Thể hình tăng cân cho người gầy, Chế độ ăn Bulking khoa học",
        "bio": "Từng vượt qua tạng người gầy khó tăng cân. Hướng dẫn chi tiết cách nạp đủ calo và tập tạ nặng để tăng cân chắc khỏe.",
        "locations": ["Thanh Xuân", "Hà Đông"],
        "video": "https://www.youtube.com/watch?v=aclHkVaku9U",
        "note": "Kèm sổ theo dõi cân nặng và khẩu phần ăn mỗi ngày",
        "course_title": "Thoát Gầy & Tăng Cơ Vạm Vỡ 20 Buổi - HLV Khánh",
        "course_price": 5800000,
        "course_sessions": 20,
        "course_desc": "Chiến lược tăng cân bền vững không tích tụ mỡ bụng xấu.",
    },
    {
        "name": "Nguyễn Yến Nhi",
        "email": "pt.yennhi@ptconnect.vn",
        "phone": "0901000029",
        "exp": 3,
        "rating": 4.9,
        "reviews": 21,
        "specialties": "Pilates giãn cơ, Thon gọn bắp tay, Đẹp dáng cho cô dâu",
        "bio": "Chuyên các khóa tập ngắn hạn cấp tốc giúp các bạn nữ chuẩn bị lên xe hoa có bờ vai thon và lưng trần gợi cảm.",
        "locations": ["Tây Hồ", "Hoàn Kiếm"],
        "video": "https://www.youtube.com/watch?v=v7AYKMP6rOE",
        "note": "Thiết kế lộ trình đặc biệt trong 6-8 tuần",
        "course_title": "Dáng Chuẩn Cô Dâu Cấp Tốc 12 Buổi - HLV Nhi",
        "course_price": 4800000,
        "course_sessions": 12,
        "course_desc": "Đốt mỡ nách, thon gọn bắp tay và siết rãnh lưng quyến rũ.",
    },
    {
        "name": "Tạ Quang Dũng",
        "email": "pt.quangdung@ptconnect.vn",
        "phone": "0901000030",
        "exp": 8,
        "rating": 4.9,
        "reviews": 35,
        "specialties": "Thể hình tổng quát, Sức bền tim mạch, Chạy bộ và Gym kết hợp",
        "bio": "HLV kỳ cựu kết hợp nâng tạ và chạy bộ cự ly dài (Marathon). Tối ưu cả sức mạnh cơ bắp lẫn sức bền tim mạch vượt trội.",
        "locations": ["Tây Hồ", "Cầu Giấy"],
        "video": "https://www.youtube.com/watch?v=g_tea8ZNk5A",
        "note": "Thích hợp cho người chuẩn bị thi chạy hoặc ba môn phối hợp",
        "course_title": "Hybrid Athlete Thể Hình & Sức Bền 24 Buổi - HLV Quang Dũng",
        "course_price": 7600000,
        "course_sessions": 24,
        "course_desc": "Chương trình huấn luyện Hybrid kết hợp tập tạ và chạy bộ sức bền.",
    },
]

def seed_pts():
    conn = db_repo.get_connection()
    with conn.cursor() as cur:
        # Đảm bảo UTF-8
        cur.execute("SET NAMES utf8mb4;")

        # Lấy hash mật khẩu chuẩn từ user id 2
        cur.execute("SELECT password_hash FROM users WHERE id = 2;")
        pw_row = cur.fetchone()
        pw_hash = pw_row["password_hash"] if pw_row else "$2b$10$97NHtEb/u6D3YO6v3GWpfuhQFZkJ.CsF1eCCorUvtDzBafzxRbx92"

        print(f"Bắt đầu nạp {len(PT_DATA)} Huấn luyện viên chuyên nghiệp...")

        for idx, pt in enumerate(PT_DATA, start=1):
            email = pt["email"]
            name = pt["name"]
            phone = pt["phone"]
            avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}"

            # 1. Tìm hoặc tạo User
            cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
            u_row = cur.fetchone()
            if u_row:
                user_id = u_row["id"]
                cur.execute(
                    "UPDATE users SET full_name = %s, phone = %s, avatar_url = %s, status = 'ACTIVE' WHERE id = %s;",
                    (name, phone, avatar, user_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, full_name, phone, role, status, avatar_url)
                    VALUES (%s, %s, %s, %s, 'PT', 'ACTIVE', %s);
                    """,
                    (email, pw_hash, name, phone, avatar),
                )
                user_id = cur.lastrowid

            # 2. Tìm hoặc tạo pt_profile
            cur.execute("SELECT id FROM pt_profiles WHERE user_id = %s;", (user_id,))
            prof_row = cur.fetchone()
            if prof_row:
                pt_id = prof_row["id"]
                cur.execute(
                    """
                    UPDATE pt_profiles
                    SET bio = %s, specialties = %s, experience_years = %s,
                        location_pricing_note = %s, demo_video_url = %s,
                        average_rating = %s, total_reviews = %s, verification_status = 'VERIFIED'
                    WHERE id = %s;
                    """,
                    (
                        pt["bio"],
                        pt["specialties"],
                        pt["exp"],
                        pt["note"],
                        pt["video"],
                        pt["rating"],
                        pt["reviews"],
                        pt_id,
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO pt_profiles (user_id, bio, specialties, experience_years, location_pricing_note, certificate_url, demo_video_url, average_rating, total_reviews, verification_status)
                    VALUES (%s, %s, %s, %s, %s, 'https://storage.ptconnect.vn/certs/cert_nasam.jpg', %s, %s, %s, 'VERIFIED');
                    """,
                    (
                        user_id,
                        pt["bio"],
                        pt["specialties"],
                        pt["exp"],
                        pt["note"],
                        pt["video"],
                        pt["rating"],
                        pt["reviews"],
                    ),
                )
                pt_id = cur.lastrowid

            # 3. Tạo địa điểm pt_locations
            cur.execute("DELETE FROM pt_locations WHERE pt_id = %s;", (pt_id,))
            for loc in pt["locations"]:
                cur.execute(
                    "INSERT INTO pt_locations (pt_id, location_name) VALUES (%s, %s);",
                    (pt_id, loc),
                )

            # 4. Tạo khóa học mẫu nếu chưa có
            cur.execute("SELECT id FROM courses WHERE pt_id = %s;", (pt_id,))
            c_row = cur.fetchone()
            if not c_row:
                cur.execute(
                    """
                    INSERT INTO courses (pt_id, title, description, total_sessions, validity_days, base_price, status)
                    VALUES (%s, %s, %s, %s, 90, %s, 'ACTIVE');
                    """,
                    (pt_id, pt["course_title"], pt["course_desc"], pt["course_sessions"], pt["course_price"]),
                )
                c_id = cur.lastrowid
            else:
                c_id = c_row["id"]

            # 5. Tạo 2-3 khung giờ rảnh AVAILABLE trong tương lai nếu chưa có
            cur.execute("SELECT COUNT(*) as c FROM availability_slots WHERE pt_id = %s AND status = 'AVAILABLE';", (pt_id,))
            slot_cnt = cur.fetchone()["c"]
            if slot_cnt == 0:
                cur.execute(
                    """
                    INSERT INTO availability_slots (pt_id, start_time, end_time, status)
                    VALUES
                      (%s, '2026-11-20 08:00:00', '2026-11-20 09:00:00', 'AVAILABLE'),
                      (%s, '2026-11-20 17:30:00', '2026-11-20 18:30:00', 'AVAILABLE'),
                      (%s, '2026-11-22 09:30:00', '2026-11-22 10:30:00', 'AVAILABLE');
                    """,
                    (pt_id, pt_id, pt_id),
                )

        conn.commit()
        print("Hoàn tất nạp 30 Huấn luyện viên mẫu vào hệ thống!")

if __name__ == "__main__":
    seed_pts()
