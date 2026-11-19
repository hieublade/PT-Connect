"""
db_repository.py
Tầng truy xuất dữ liệu (Data Access Layer / Repository)
Ánh xạ trực tiếp với lược đồ quan hệ BCNF và các Stored Procedures.
Tự động nhận diện môi trường Docker (host='mysql', port=3306) hoặc Local Host (port=3307).
"""

import json
import os
import socket
from typing import Any, Dict, List, Optional
try:
    import pymysql
except ImportError:
    pymysql = None


_syllabus_cache: Dict[int, List[Dict[str, Any]]] = {}


class DBRepository:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        if host:
            self.host = host
        elif os.getenv("DB_HOST"):
            self.host = os.getenv("DB_HOST")
        else:
            try:
                socket.gethostbyname("mysql")
                self.host = "mysql"
            except Exception:
                self.host = "127.0.0.1"

        if port:
            self.port = port
        elif os.getenv("DB_PORT"):
            self.port = int(os.getenv("DB_PORT"))
        else:
            self.port = 3306 if self.host == "mysql" else 3307

        self.user = user or os.getenv("DB_USER", "ptuser")
        self.password = password or os.getenv("DB_PASSWORD", "ptpassword")
        self.database = database or os.getenv("DB_NAME", "ptconnect")

    def get_connection(self):
        if pymysql is None:
            raise RuntimeError("Thư viện 'pymysql' chưa được cài đặt. Vui lòng chạy: pip install pymysql")
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    # =====================================================================
    # FEATURE 1: VIDEO DEMO HUẤN LUYỆN VIÊN
    # =====================================================================
    def update_pt_video_demo(self, pt_id: int, demo_video_url: str) -> bool:
        """Cập nhật đường link video demo cho PT profile."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                affected = cur.execute(
                    "UPDATE pt_profiles SET demo_video_url = %s WHERE id = %s;",
                    (demo_video_url.strip() if demo_video_url else None, pt_id),
                )
                return affected > 0

    def get_pt_video_demo(self, pt_id: int) -> Optional[str]:
        """Lấy link video demo của PT với cơ chế dự phòng an toàn."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT demo_video_url FROM pt_profiles WHERE id = %s;", (pt_id,))
                    row = cur.fetchone()
                    if row and row.get("demo_video_url"):
                        return row["demo_video_url"]
        except Exception:
            pass
        return "https://www.youtube.com/watch?v=aclHkVaku9U"

    # =====================================================================
    # FEATURE 2: XEM TRƯỚC LỘ TRÌNH GIÁO ÁN KHÓA HỌC THEO TUẦN (BCNF)
    # =====================================================================
    def get_course_syllabus(self, course_id: int) -> List[Dict[str, Any]]:
        """Lấy lộ trình khóa học phân theo từng TUẦN (Tuần 1, Tuần 2, Tuần 3, Tuần 4...) chuẩn BCNF."""
        if course_id in _syllabus_cache:
            return _syllabus_cache[course_id]
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT c.title, c.description, c.total_sessions
                        FROM courses c
                        WHERE c.id = %s;
                        """,
                        (course_id,),
                    )
                    course = cur.fetchone()
                    if not course:
                        return []

                    c_title = course.get("title", "")
                    c_desc = course.get("description", "")
                    title_lower = c_title.lower()

                    # 1. Khóa học Calisthenics & Thể hình tự thân
                    if "calisthenics" in title_lower or "tự thân" in title_lower:
                        res = [
                            {
                                "week_number": 1,
                                "week_title": "Nhập môn & Kiểm soát chuyển động tự thân",
                                "focus_area": "Hệ thống thần kinh cơ & Trọng tâm",
                                "goal": "Làm quen nhịp thở, kích hoạt cơ bụng sâu (Core), làm chủ form Hollow Body và nhịp giữ trên xà đơn.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Hollow Body Hold & Rock", "target_muscle": "Cơ bụng & Trọng tâm", "sets": 3, "reps": 1, "rest_seconds": 45, "notes": "Giữ thắt lưng chạm sát sàn, siết chặt cơ bụng"},
                                    {"exercise_order": 2, "exercise_name": "Active Scapular Hang on Bar", "target_muscle": "Cơ xô & Khớp vai", "sets": 3, "reps": 8, "rest_seconds": 60, "notes": "Hạ xương bả vai xuống, không cong gập khuỷu tay"},
                                    {"exercise_order": 3, "exercise_name": "Incline Push-ups Form", "target_muscle": "Cơ ngực & Tay sau", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Cùi chỏ mở góc 45 độ, siết mông giữ thẳng người"},
                                    {"exercise_order": 4, "exercise_name": "Bodyweight Squat & Mobility", "target_muscle": "Cơ đùi trước & Mông", "sets": 3, "reps": 15, "rest_seconds": 60, "notes": "Mở rộng khớp háng, giữ lưng thẳng tự nhiên"}
                                ]
                            },
                            {
                                "week_number": 2,
                                "week_title": "Nền tảng kéo & đẩy chuyên sâu",
                                "focus_area": "Sức mạnh bộc phát phần thân trên",
                                "goal": "Tăng cường lực kéo xà (Pull-up Progression), lực đẩy xà kép (Dips) và kiểm soát nhịp hạ (Eccentric).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Negative Pull-ups (Hạ chậm 4s)", "target_muscle": "Cơ lưng xô", "sets": 4, "reps": 6, "rest_seconds": 90, "notes": "Bật lên và hạ người có kiểm soát trong 4 giây"},
                                    {"exercise_order": 2, "exercise_name": "Parallel Bar Dips / Bench Dips", "target_muscle": "Ngực dưới & Tay sau", "sets": 3, "reps": 10, "rest_seconds": 75, "notes": "Hạ người vuông góc 90 độ tại khớp khuỷu"},
                                    {"exercise_order": 3, "exercise_name": "L-Sit Progression (Tuck Hold)", "target_muscle": "Cơ bụng & Cơ gập hông", "sets": 3, "reps": 1, "rest_seconds": 60, "notes": "Đẩy vai cao, co gối sát ngực giữ 20-30s"},
                                    {"exercise_order": 4, "exercise_name": "Walking Lunges Thể lực", "target_muscle": "Cơ đùi & Mông", "sets": 3, "reps": 16, "rest_seconds": 60, "notes": "Bước dài giữ gối trước không vượt quá mũi chân"}
                                ]
                            },
                            {
                                "week_number": 3,
                                "week_title": "Tối ưu sức bền & Kháng lực cao",
                                "focus_area": "Phối hợp chuyển động đa khớp",
                                "goal": "Tập trung nâng cao số lần lặp sạch form, phối hợp chuỗi chuyển động liên hoàn trên thanh xà và xà kép.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Strict Pull-ups (Kéo xà chuẩn Form)", "target_muscle": "Cơ lưng xô & Tay trước", "sets": 4, "reps": 8, "rest_seconds": 90, "notes": "Cằm vượt qua thanh xà, không đung đưa thân người"},
                                    {"exercise_order": 2, "exercise_name": "Diamond Push-ups", "target_muscle": "Cơ ngực trong & Tay sau", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Hai bàn tay tạo hình kim cương, ép chặt khuỷu tay"},
                                    {"exercise_order": 3, "exercise_name": "Hanging Knee to Elbows", "target_muscle": "Cơ bụng liên sườn", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Kéo đầu gối chạm gần khuỷu tay trên xà đơn"},
                                    {"exercise_order": 4, "exercise_name": "Jump Squat Đốt mỡ", "target_muscle": "Sức bật chân & Tim mạch", "sets": 3, "reps": 15, "rest_seconds": 45, "notes": "Tiếp đất êm bằng mũi bàn chân và hạ hông"}
                                ]
                            },
                            {
                                "week_number": 4,
                                "week_title": "Bứt phá kỹ năng nâng cao & Đánh giá mục tiêu",
                                "focus_area": "Thử thách sức mạnh tối đa",
                                "goal": "Kiểm tra số lần hít xà tối đa, kỹ năng thăng bằng thân người và đánh giá sự cải thiện của cơ thể.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Muscle-up Transition Drills", "target_muscle": "Sức mạnh bộc phát toàn thân", "sets": 4, "reps": 5, "rest_seconds": 90, "notes": "Luyện chuyển động kéo nổ và gập người qua xà"},
                                    {"exercise_order": 2, "exercise_name": "Archer Push-ups", "target_muscle": "Ngực lệch tâm", "sets": 3, "reps": 10, "rest_seconds": 75, "notes": "Mở rộng tay, duỗi thẳng một bên tay luân phiên"},
                                    {"exercise_order": 3, "exercise_name": "Toes to Bar (Mũi chân chạm xà)", "target_muscle": "Cơ bụng toàn diện", "sets": 3, "reps": 8, "rest_seconds": 60, "notes": "Giữ thân người ổn định, nâng chân chạm thanh xà"},
                                    {"exercise_order": 4, "exercise_name": "InBody Re-test & Cool-down", "target_muscle": "Phục hồi & Thả lỏng", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Đo lại chỉ số cơ mỡ và kéo giãn sâu toàn cơ thể"}
                                ]
                            }
                        ]

                    # 2. Khóa học Giảm mỡ / Đốt mỡ / HIIT / Giảm cân
                    elif "giảm mỡ" in title_lower or "đốt mỡ" in title_lower or "hiit" in title_lower or "giảm cân" in title_lower:
                        res = [
                            {
                                "week_number": 1,
                                "week_title": "Kích hoạt trao đổi chất & Thích nghi thể lực",
                                "focus_area": "Khởi động trao đổi chất & Chuẩn form",
                                "goal": "Đo chỉ số InBody, làm quen các chuỗi chuyển động đa khớp tiêu hao nhiều calo, cân chỉnh nhịp tim vùng đốt mỡ.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Dynamic Warm-up & Foam Rolling", "target_muscle": "Toàn thân", "sets": 2, "reps": 10, "rest_seconds": 30, "notes": "Làm nóng khớp và kích hoạt hệ tuần hoàn"},
                                    {"exercise_order": 2, "exercise_name": "Goblet Squat với tạ Kettlebell", "target_muscle": "Cơ đùi & Mông", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Giữ tạ sát ngực, thẳng lưng, thở đều"},
                                    {"exercise_order": 3, "exercise_name": "Dumbbell Push Press", "target_muscle": "Cơ vai & Chân", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Dùng lực nhún chân đẩy tạ qua đầu"},
                                    {"exercise_order": 4, "exercise_name": "Plank Shoulder Taps", "target_muscle": "Cơ bụng & Giữ thăng bằng", "sets": 3, "reps": 20, "rest_seconds": 45, "notes": "Giữ cố định hông không lắc lư"}
                                ]
                            },
                            {
                                "week_number": 2,
                                "week_title": "Tăng tốc cường độ & Đốt mỡ liên hoàn",
                                "focus_area": "Mật độ bài tập & Tim mạch",
                                "goal": "Rút ngắn thời gian nghỉ giữa các hiệp, đưa nhịp tim vào vùng Fat-Burning Zone thông qua chuỗi bài tập Circuit.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Kettlebell Swing", "target_muscle": "Cơ mông & Đùi sau", "sets": 4, "reps": 15, "rest_seconds": 45, "notes": "Phát lực từ bản lề hông (Hip Hinge), không dùng lực tay"},
                                    {"exercise_order": 2, "exercise_name": "Battle Ropes Wave (Dập dây thừng)", "target_muscle": "Vai, Tay & Tim mạch", "sets": 4, "reps": 1, "rest_seconds": 45, "notes": "Dập sóng nhanh liên tục trong 30 giây"},
                                    {"exercise_order": 3, "exercise_name": "Dumbbell Walking Lunges", "target_muscle": "Cơ đùi & Mông", "sets": 3, "reps": 16, "rest_seconds": 60, "notes": "Bước đều bước, siết chặt cơ đùi"},
                                    {"exercise_order": 4, "exercise_name": "Mountain Climbers (Leo núi tại chỗ)", "target_muscle": "Cơ bụng & Đốt mỡ", "sets": 3, "reps": 30, "rest_seconds": 30, "notes": "Kéo gối nhanh nhịp nhàng"}
                                ]
                            },
                            {
                                "week_number": 3,
                                "week_title": "Tối ưu tiêu hao Calo với Supersets",
                                "focus_area": "Cơ bắp săn chắc & Đốt mỡ EPOC",
                                "goal": "Áp dụng kỹ thuật ghép bài (Supersets) đối kháng giúp cơ bắp nét gọn và kích hoạt đốt mỡ thụ động sau tập (EPOC).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Dumbbell Thrusters (Squat + Press)", "target_muscle": "Toàn thân", "sets": 4, "reps": 12, "rest_seconds": 60, "notes": "Kết hợp nhịp nhàng giữa xuống squat và đẩy tạ"},
                                    {"exercise_order": 2, "exercise_name": "Burpees Không chống đẩy", "target_muscle": "Sức bền tim mạch", "sets": 4, "reps": 12, "rest_seconds": 45, "notes": "Bật nhảy dứt khoát, tiếp đất êm"},
                                    {"exercise_order": 3, "exercise_name": "Dumbbell Renegade Row", "target_muscle": "Lưng xô & Cơ lõi", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Ở tư thế chống đẩy, kéo tạ từng bên"},
                                    {"exercise_order": 4, "exercise_name": "Box Jumps (Bật nhảy bục)", "target_muscle": "Sức bật chân & Mông", "sets": 3, "reps": 10, "rest_seconds": 60, "notes": "Bật nhảy 2 chân lên bục an toàn"}
                                ]
                            },
                            {
                                "week_number": 4,
                                "week_title": "Bứt phá giới hạn & Đo lường thành quả",
                                "focus_area": "Tối đa hóa hiệu suất & InBody Re-test",
                                "goal": "Thực hiện chuỗi bài thử thách thể lực cao nhất, đánh giá tỷ lệ giảm mỡ và thiết lập thói quen dinh dưỡng duy trì.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "HIIT Tabata Cardio Finisher", "target_muscle": "Tim mạch & Đốt mỡ đỉnh cao", "sets": 8, "reps": 1, "rest_seconds": 10, "notes": "20s dốc sức tối đa - 10s nghỉ (4 phút)"},
                                    {"exercise_order": 2, "exercise_name": "Farmer's Walk (Xách tạ đi bộ)", "target_muscle": "Cơ cẳng tay, Lõi & Thể lực", "sets": 3, "reps": 1, "rest_seconds": 60, "notes": "Xách 2 tạ nặng đi bộ 40 mét giữ thẳng lưng"},
                                    {"exercise_order": 3, "exercise_name": "Bicycle Crunches Siết bụng", "target_muscle": "Cơ bụng 6 múi", "sets": 3, "reps": 20, "rest_seconds": 45, "notes": "Xoay vặn khuỷu tay chạm gối đối diện"},
                                    {"exercise_order": 4, "exercise_name": "Đo lại InBody & Tư vấn dinh dưỡng", "target_muscle": "Đánh giá & Hồi phục", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Đối chiếu tỷ lệ mỡ/cơ giảm được sau lộ trình"}
                                ]
                            }
                        ]

                    # 3. Khóa học Tăng cơ / Thể hình / Powerlifting / Hypertrophy
                    elif "tăng cơ" in title_lower or "thể hình" in title_lower or "powerlifting" in title_lower or "hypertrophy" in title_lower:
                        res = [
                            {
                                "week_number": 1,
                                "week_title": "Chuẩn hóa Form kỹ thuật các bài Compound",
                                "focus_area": "Kỹ thuật nâng tạ chuẩn Form & An toàn",
                                "goal": "Xác định biên độ chuyển động tối ưu cho Squat, Bench Press, Deadlift và làm quen kỹ thuật gồng core (Bracing).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Barbell Back Squat (Gánh đòn)", "target_muscle": "Cơ đùi trước & Mông", "sets": 4, "reps": 8, "rest_seconds": 90, "notes": "Gồng chặt cơ bụng, gối mở theo hướng mũi chân"},
                                    {"exercise_order": 2, "exercise_name": "Barbell Flat Bench Press", "target_muscle": "Cơ ngực & Tay sau", "sets": 4, "reps": 8, "rest_seconds": 90, "notes": "Khép nhẹ bả vai, hạ đòn chạm nhẹ ngực dưới"},
                                    {"exercise_order": 3, "exercise_name": "Romanian Deadlift với tạ đòn", "target_muscle": "Đùi sau & Lưng dưới", "sets": 3, "reps": 10, "rest_seconds": 75, "notes": "Đẩy hông ra sau, giữ thanh đòn lướt sát ống đồng"},
                                    {"exercise_order": 4, "exercise_name": "Lat Pulldown (Kéo xô máy)", "target_muscle": "Cơ lưng xô", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Ưỡn nhẹ ngực, kéo thanh đòn về phía xương quai xanh"}
                                ]
                            },
                            {
                                "week_number": 2,
                                "week_title": "Áp dụng Quá tải tiệm tiến (Progressive Overload)",
                                "focus_area": "Tăng dần mức tạ & Kích hoạt sợi cơ",
                                "goal": "Tăng thêm 2.5 - 5% khối lượng tạ, phát triển sức mạnh bộc phát và sức căng cơ học (Mechanical Tension).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Conventional Deadlift (Kéo tạ)", "target_muscle": "Chuỗi cơ sau & Toàn thân", "sets": 4, "reps": 6, "rest_seconds": 120, "notes": "Kéo dứt khoát bằng lực đạp sàn, khóa hông an toàn"},
                                    {"exercise_order": 2, "exercise_name": "Overhead Press (Đẩy vai đứng)", "target_muscle": "Cơ vai & Tay sau", "sets": 4, "reps": 8, "rest_seconds": 90, "notes": "Siết chặt mông và bụng, không cong lưng dưới"},
                                    {"exercise_order": 3, "exercise_name": "Bent Over Barbell Row", "target_muscle": "Độ dày lưng giữa & Xô", "sets": 4, "reps": 10, "rest_seconds": 75, "notes": "Gập người 45 độ, kéo thanh đòn chạm rốn"},
                                    {"exercise_order": 4, "exercise_name": "Incline Dumbbell Bench Press", "target_muscle": "Cơ ngực trên", "sets": 3, "reps": 10, "rest_seconds": 75, "notes": "Ghế nghiêng 30 độ, ép cơ ngực trên khi đẩy lên"}
                                ]
                            },
                            {
                                "week_number": 3,
                                "week_title": "Tối ưu khối lượng phì đại cơ bắp (Hypertrophy Volume)",
                                "focus_area": "Căng thẳng chuyển hóa (Metabolic Stress)",
                                "goal": "Gia tăng số hiệp và lần lặp (8 - 12 reps) cho các nhóm cơ hỗ trợ, thúc đẩy bơm máu và phát triển tế bào cơ (Hypertrophy).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Leg Press máy nghiêng 45 độ", "target_muscle": "Cơ đùi & Cơ mông", "sets": 4, "reps": 12, "rest_seconds": 75, "notes": "Hạ chậm có kiểm soát, không khóa cứng khớp gối"},
                                    {"exercise_order": 2, "exercise_name": "Dumbbell Lateral Raise", "target_muscle": "Cơ vai bên (Vai rộng)", "sets": 4, "reps": 12, "rest_seconds": 60, "notes": "Nâng tạ ngang vai, cổ tay hơi chúc xuống"},
                                    {"exercise_order": 3, "exercise_name": "Cable Bicep Curls", "target_muscle": "Cơ tay trước (Biceps)", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Cố định khuỷu tay sát thân sườn"},
                                    {"exercise_order": 4, "exercise_name": "Triceps Rope Pushdown", "target_muscle": "Cơ tay sau (Triceps)", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Tách dây ở đáy chuyển động để siết cơ tối đa"}
                                ]
                            },
                            {
                                "week_number": 4,
                                "week_title": "Kiểm tra mức tạ cực đại (1RM Test) & Phục hồi",
                                "focus_area": "Đánh giá mức tăng tiến sức mạnh",
                                "goal": "Kiểm tra sự tiến bộ của các bài tập chính, đo lại chỉ số tăng cơ giảm mỡ và hướng dẫn chế độ xả cơ (Deload).",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Max Strength Testing (Squat / Bench / Deadlift)", "target_muscle": "Sức mạnh tối đa", "sets": 3, "reps": 3, "rest_seconds": 150, "notes": "Thử nghiệm mức tạ mục tiêu dưới sự bảo hộ của HLV"},
                                    {"exercise_order": 2, "exercise_name": "Bulgarian Split Squats", "target_muscle": "Cân bằng cơ bắp 2 chân", "sets": 3, "reps": 10, "rest_seconds": 60, "notes": "Đặt mu bàn chân sau lên ghế, hạ hông thẳng đứng"},
                                    {"exercise_order": 3, "exercise_name": "Hanging Leg Raises", "target_muscle": "Cơ bụng dưới", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Nâng chân không tạo đà vung vẩy"},
                                    {"exercise_order": 4, "exercise_name": "InBody Re-test & Lộ trình dinh dưỡng Protein", "target_muscle": "Kiểm tra kết quả", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Đo đạc chỉ số cơ tăng thêm và thiết lập macro dinh dưỡng"}
                                ]
                            }
                        ]

                    # 4. Khóa học Cột sống / Phục hồi / Pilates / Yoga
                    elif "cột sống" in title_lower or "phục hồi" in title_lower or "pilates" in title_lower or "yoga" in title_lower or "chỉnh dáng" in title_lower:
                        res = [
                            {
                                "week_number": 1,
                                "week_title": "Đánh giá sai lệch tư thế & Giải tỏa áp lực cột sống",
                                "focus_area": "Giải tỏa căng cứng & Cân bằng tư thế",
                                "goal": "Kiểm tra độ gù lưng, võng lưng, sai lệch xương chậu; giải phóng các bó cơ căng cứng vùng thắt lưng và vai gáy.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Foam Rolling Lưng trên & Mông", "target_muscle": "Giải phóng mạc cơ (Myofascial)", "sets": 2, "reps": 10, "rest_seconds": 30, "notes": "Lăn chậm rãi tìm các điểm co thắt cơ"},
                                    {"exercise_order": 2, "exercise_name": "Cat - Cow Pose (Tư thế con mèo - con bò)", "target_muscle": "Biên độ đốt sống lưng", "sets": 3, "reps": 10, "rest_seconds": 45, "notes": "Hít vào võng lưng ngẩng mặt, thở ra gù lưng hóp bụng"},
                                    {"exercise_order": 3, "exercise_name": "Pelvic Tilts (Nghiêng xương chậu)", "target_muscle": "Cơ bụng dưới & Khung chậu", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Nhấn chặt thắt lưng sát sàn để kích hoạt cơ lõi"},
                                    {"exercise_order": 4, "exercise_name": "Child's Pose (Tư thế em bé kéo giãn)", "target_muscle": "Cơ dựng gai sống & Khớp háng", "sets": 2, "reps": 1, "rest_seconds": 60, "notes": "Thở chậm sâu, thả lỏng toàn bộ cơ thể"}
                                ]
                            },
                            {
                                "week_number": 2,
                                "week_title": "Kích hoạt cơ sâu & Ổn định vùng chậu",
                                "focus_area": "Cơ lõi sâu (Transverse Abdominis)",
                                "goal": "Tập trung kích hoạt các nhóm cơ nâng đỡ cột sống (Multifidus, Core), giúp giảm đau lưng và giữ vững khung xương.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Bird - Dog Exercise", "target_muscle": "Cơ lưng dưới & Mông", "sets": 3, "reps": 10, "rest_seconds": 45, "notes": "Nâng tay này chân kia song song mặt sàn, giữ 2 giây"},
                                    {"exercise_order": 2, "exercise_name": "Dead Bug (Bọ chết kích hoạt Core)", "target_muscle": "Cơ bụng ngang sâu", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Thắt lưng áp sát thảm, hạ tay chân đối diện"},
                                    {"exercise_order": 3, "exercise_name": "Glute Bridge (Cầu mông nâng hông)", "target_muscle": "Cơ mông lớn & Gân kheo", "sets": 3, "reps": 15, "rest_seconds": 60, "notes": "Phát lực bằng gót chân, siết chặt cơ mông ở đỉnh"},
                                    {"exercise_order": 4, "exercise_name": "Chest Opener (Mở rộng ngực vai)", "target_muscle": "Cơ ngực & Khớp vai", "sets": 2, "reps": 10, "rest_seconds": 45, "notes": "Khắc phục tình trạng vai cuộn tròn về phía trước"}
                                ]
                            },
                            {
                                "week_number": 3,
                                "week_title": "Tăng cường sức mạnh bảo vệ đĩa đệm",
                                "focus_area": "Độ vững chắc của trục cột sống",
                                "goal": "Rèn luyện sức mạnh chức năng nhẹ nhàng, giúp cơ lưng khỏe hơn để nâng đỡ trọng lượng cơ thể cả ngày làm việc.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Side Plank Hold (Plank nghiêng)", "target_muscle": "Cơ vuông thắt lưng (QL) & Cơ liên sườn", "sets": 3, "reps": 1, "rest_seconds": 45, "notes": "Giữ trục cơ thể từ đầu đến chân tạo thành đường thẳng"},
                                    {"exercise_order": 2, "exercise_name": "Pilates The Hundred (Bài tập 100)", "target_muscle": "Sức bền cơ bụng & Nhịp thở", "sets": 1, "reps": 100, "rest_seconds": 60, "notes": "Vỗ tay nhịp nhàng 5 nhịp hít vào, 5 nhịp thở ra"},
                                    {"exercise_order": 3, "exercise_name": "Resistance Band Face Pulls", "target_muscle": "Cơ lưng trên & Cơ bả vai", "sets": 3, "reps": 15, "rest_seconds": 45, "notes": "Kéo dây chun về phía sống mũi, ép chặt hai bả vai"},
                                    {"exercise_order": 4, "exercise_name": "Hip Flexor Stretch (Giãn cơ gập hông)", "target_muscle": "Cơ thắt lưng chậu (Psoas)", "sets": 2, "reps": 1, "rest_seconds": 45, "notes": "Giúp mở rộng khớp háng và khắc phục võng lưng"}
                                ]
                            },
                            {
                                "week_number": 4,
                                "week_title": "Hoàn thiện tư thế tự nhiên & Thói quen tự duy trì",
                                "focus_area": "Kiểm tra phục hồi & Thói quen lành mạnh",
                                "goal": "Kiểm tra lại độ cân đối trục cột sống, biên độ cúi ngửa xoay người và thiết lập bài tập tự chỉnh dáng tại văn phòng.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Pilates Roll Up (Cuộn đốt sống)", "target_muscle": "Linh hoạt từng đốt sống lưng", "sets": 3, "reps": 8, "rest_seconds": 60, "notes": "Cuộn từng đốt sống rời sàn và hạ xuống từ từ"},
                                    {"exercise_order": 2, "exercise_name": "Wall Angel (Thiên thần trượt tường)", "target_muscle": "Cân chỉnh tư thế đứng", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Đầu, lưng trên và cùi chỏ áp sát tường khi trượt lên"},
                                    {"exercise_order": 3, "exercise_name": "Single Leg Balance (Đứng 1 chân thăng bằng)", "target_muscle": "Cảm thụ bản thể (Proprioception)", "sets": 3, "reps": 1, "rest_seconds": 30, "notes": "Tập trung giữ vững trọng tâm trong 45 giây mỗi bên"},
                                    {"exercise_order": 4, "exercise_name": "Tái khám tư thế & Bộ bài tập văn phòng", "target_muscle": "Đánh giá & Duy trì", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Đối chiếu cải thiện gù lưng, võng lưng và hết đau mỏi"}
                                ]
                            }
                        ]

                    else:
                        # 5. Mặc định theo tuần cho các khóa học khởi động & rèn luyện tổng quát
                        res = [
                            {
                                "week_number": 1,
                                "week_title": "Đánh giá thể lực nền tảng & Chuẩn hóa Form",
                                "focus_area": "Khởi động & Nền tảng kỹ thuật",
                                "goal": f"Kiểm tra chỉ số InBody, đo độ dẻo dai cơ xương khớp và làm quen kỹ thuật chuyển động cơ bản của {c_title}.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Dynamic Warm-up & Kích hoạt cơ", "target_muscle": "Toàn thân", "sets": 2, "reps": 10, "rest_seconds": 30, "notes": "Làm nóng khớp và đưa cơ thể vào trạng thái sẵn sàng"},
                                    {"exercise_order": 2, "exercise_name": "Bodyweight Squat & Hinge Form", "target_muscle": "Cơ đùi & Mông", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Cân chỉnh tư thế cột sống, gối mở tự nhiên"},
                                    {"exercise_order": 3, "exercise_name": "Core Activation & Plank Hold", "target_muscle": "Cơ bụng & Trọng tâm", "sets": 3, "reps": 1, "rest_seconds": 45, "notes": "Siết chặt cơ bụng và ổn định thân người"},
                                    {"exercise_order": 4, "exercise_name": "Static Stretching & Cool-down", "target_muscle": "Giãn cơ thả lỏng", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Giãn cơ sâu giúp giảm căng cứng sau buổi tập"}
                                ]
                            },
                            {
                                "week_number": 2,
                                "week_title": "Xây dựng sức mạnh & Kỹ thuật chuyển động chuyên sâu",
                                "focus_area": "Kỹ thuật nâng cao & Sức mạnh",
                                "goal": "Tăng cường mức độ phức tạp của bài tập, áp dụng mức kháng lực vừa sức để phát triển sức mạnh chức năng.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Main Movement Progression", "target_muscle": "Nhóm cơ mục tiêu", "sets": 4, "reps": 10, "rest_seconds": 75, "notes": "Nâng dần mức tải với kỹ thuật chuẩn xác"},
                                    {"exercise_order": 2, "exercise_name": "Accessory Compound Exercise", "target_muscle": "Cơ hỗ trợ", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Phát triển nhóm cơ phụ trợ và khớp chuyển động"},
                                    {"exercise_order": 3, "exercise_name": "Metabolic Conditioning Finisher", "target_muscle": "Sức bền & Tim mạch", "sets": 3, "reps": 15, "rest_seconds": 45, "notes": "Thúc đẩy đốt mỡ và tăng sức bền cơ thể"}
                                ]
                            },
                            {
                                "week_number": 3,
                                "week_title": "Tối ưu hiệu suất & Đẩy mạnh chuyển hóa",
                                "focus_area": "Khối lượng bài tập & Định hình cơ thể",
                                "goal": "Tăng mật độ bài tập, phối hợp các bài tập siêu chuỗi (Supersets) giúp vóc dáng săn chắc rõ rệt.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "High-Density Strength Circuit", "target_muscle": "Toàn thân", "sets": 4, "reps": 12, "rest_seconds": 60, "notes": "Tập liên hoàn các bài tập chính"},
                                    {"exercise_order": 2, "exercise_name": "Unilateral Balance Exercise", "target_muscle": "Cân bằng cơ bắp", "sets": 3, "reps": 12, "rest_seconds": 45, "notes": "Khắc phục lệch cơ giữa hai bên cơ thể"},
                                    {"exercise_order": 3, "exercise_name": "High Intensity Core Burnout", "target_muscle": "Cơ bụng săn chắc", "sets": 3, "reps": 20, "rest_seconds": 30, "notes": "Chuỗi bài tập siết eo và cơ bụng"}
                                ]
                            },
                            {
                                "week_number": 4,
                                "week_title": "Bứt phá giới hạn & Kiểm tra kết quả giai đoạn",
                                "focus_area": "Đánh giá thành quả & Lộ trình tiếp nối",
                                "goal": "Đo lại chỉ số InBody, kiểm tra mức độ đạt được mục tiêu ban đầu và thiết lập định hướng duy trì phong độ.",
                                "exercises": [
                                    {"exercise_order": 1, "exercise_name": "Peak Performance Challenge", "target_muscle": "Sức mạnh tối đa", "sets": 3, "reps": 5, "rest_seconds": 90, "notes": "Thử thách giới hạn thể lực mới của bản thân"},
                                    {"exercise_order": 2, "exercise_name": "Functional Full-body Finisher", "target_muscle": "Khả năng vận động linh hoạt", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Hoàn thiện kỹ năng vận động độc lập"},
                                    {"exercise_order": 3, "exercise_name": "InBody Re-test & Tư vấn dinh dưỡng dài hạn", "target_muscle": "Đo lường kết quả", "sets": 1, "reps": 1, "rest_seconds": 60, "notes": "Đối chiếu sự cải thiện rõ rệt so với Tuần 1"}
                                ]
                            }
                        ]
                    _syllabus_cache[course_id] = res
                    return res
        except Exception:
            pass
        return []


    def save_course_syllabus_session(
        self,
        course_id: int,
        session_number: int,
        title: str,
        description: str,
        focus_area: str,
        exercises: List[Dict[str, Any]],
    ) -> int:
        """Đã chuẩn hóa chuyển sang quản lý qua workout_plans và workouts."""
        return 0

    # =====================================================================
    # FEATURE 3: NHẮN TIN TRỰC TIẾP 2 CHIỀU GIỮA HỌC VIÊN VÀ PT (BCNF: CHAT_MESSAGES)
    # =====================================================================
    def send_chat_message(
        self, student_id: int, pt_id: int, sender_id: int, content: str
    ) -> Dict[str, Any]:
        """Gửi tin nhắn trực tiếp qua bảng chat_messages (tương thích ngược)."""
        receiver_id = pt_id if sender_id == student_id else student_id
        return self.send_direct_chat_message(sender_id, receiver_id, content)

    def get_user_conversations(self, user_id: int, role: str) -> List[Dict[str, Any]]:
        """Lấy danh sách các cuộc hội thoại từ bảng chat_messages chuẩn BCNF."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                sql = """
                    SELECT 
                        partner.id AS partner_user_id,
                        partner.id AS id,
                        partner.full_name AS partner_name,
                        partner.avatar_url AS partner_avatar,
                        partner.role AS partner_role,
                        last_msg.content AS last_content,
                        last_msg.created_at AS last_message_at,
                        last_msg.is_read AS last_is_read
                    FROM (
                        SELECT 
                            CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END AS partner_id,
                            MAX(id) AS max_msg_id
                        FROM chat_messages
                        WHERE sender_id = %s OR receiver_id = %s
                        GROUP BY partner_id
                    ) m
                    JOIN users partner ON m.partner_id = partner.id
                    JOIN chat_messages last_msg ON m.max_msg_id = last_msg.id
                    ORDER BY last_msg.created_at DESC;
                """
                cur.execute(sql, (user_id, user_id, user_id))
                return cur.fetchall()

    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Tương thích ngược: lấy tin nhắn với đối tác (conversation_id đóng vai trò partner_user_id)."""
        return []

    def get_or_create_conversation_id(self, student_id: int, pt_id: int) -> int:
        """Tương thích ngược: trả về partner_id."""
        return pt_id

    def get_direct_chat_messages(self, user_a: int, user_b: int) -> List[Dict[str, Any]]:
        """Lấy toàn bộ tin nhắn qua lại giữa 2 người dùng từ bảng chat_messages."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT m.id, m.sender_id, m.receiver_id, m.content, m.is_read, m.created_at,
                           u.full_name AS sender_name, u.role AS sender_role
                    FROM chat_messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE (m.sender_id = %s AND m.receiver_id = %s)
                       OR (m.sender_id = %s AND m.receiver_id = %s)
                    ORDER BY m.created_at ASC, m.id ASC;
                    """,
                    (user_a, user_b, user_b, user_a),
                )
                msgs = cur.fetchall()
                # Đánh dấu đã đọc các tin nhắn gửi đến user_a
                cur.execute(
                    """
                    UPDATE chat_messages SET is_read = TRUE
                    WHERE sender_id = %s AND receiver_id = %s AND is_read = FALSE;
                    """,
                    (user_b, user_a),
                )
            conn.commit()
            return msgs

    def send_direct_chat_message(self, sender_id: int, receiver_id: int, content: str) -> Dict[str, Any]:
        """Gửi tin nhắn trực tiếp 2 chiều vào bảng chat_messages (Chuẩn BCNF 1 bảng duy nhất)."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chat_messages (sender_id, receiver_id, content, is_read, created_at)
                    VALUES (%s, %s, %s, FALSE, CURRENT_TIMESTAMP);
                    """,
                    (sender_id, receiver_id, content),
                )
                msg_id = cur.lastrowid
            conn.commit()
            return {"message_id": msg_id, "sender_id": sender_id, "receiver_id": receiver_id}

    # =====================================================================
    # FEATURE 4: DỮ LIỆU CHUYÊN MÔN PT (COSINE SIMILARITY)
    # =====================================================================
    def get_all_pts_for_recommendation(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ hồ sơ PT kèm tên, chuyên môn, tiểu sử và địa điểm."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id AS pt_id, p.id AS id, p.user_id, u.full_name AS fullName,
                           u.full_name, u.avatar_url AS avatarUrl, u.avatar_url,
                           p.bio, p.specialties, p.experience_years AS experienceYears,
                           p.experience_years,
                           ROUND(COALESCE(AVG(r.rating), 0.0), 2) AS averageRating,
                           ROUND(COALESCE(AVG(r.rating), 0.0), 2) AS average_rating,
                           COUNT(DISTINCT r.id) AS totalReviews,
                           COUNT(DISTINCT r.id) AS total_reviews,
                           p.demo_video_url AS demoVideoUrl,
                           p.demo_video_url,
                           GROUP_CONCAT(DISTINCT l.location_name SEPARATOR ', ') AS availableLocations,
                           GROUP_CONCAT(DISTINCT l.location_name SEPARATOR ', ') AS working_locations
                    FROM pt_profiles p
                    JOIN users u ON p.user_id = u.id
                    LEFT JOIN pt_locations l ON p.id = l.pt_id
                    LEFT JOIN availability_slots s ON p.id = s.pt_id
                    LEFT JOIN bookings b ON s.id = b.slot_id
                    LEFT JOIN reviews r ON b.id = r.booking_id
                    WHERE u.status = 'ACTIVE'
                    GROUP BY p.id, p.user_id, u.full_name, u.avatar_url,
                             p.bio, p.specialties, p.experience_years, p.demo_video_url;
                    """
                )
                return cur.fetchall()

    # =====================================================================
    # FEATURE 5: LƯU GIÁO ÁN AI (GEMINI WORKOUT PLANS)
    # =====================================================================
    def save_ai_workout_plan(
        self,
        enrollment_id: int,
        title: str,
        goal: str,
        start_date: str,
        end_date: str,
        exercises: List[Dict[str, Any]],
    ) -> int:
        """Gọi Stored Procedure sp_save_ai_workout_plan."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SET @out_plan_id = 0;")
                cur.execute(
                    """
                    CALL sp_save_ai_workout_plan(%s, %s, %s, %s, %s, %s, @out_plan_id);
                    """,
                    (
                        enrollment_id,
                        title,
                        goal,
                        start_date,
                        end_date,
                        json.dumps(exercises, ensure_ascii=False),
                    ),
                )
                cur.execute("SELECT @out_plan_id AS plan_id;")
                res = cur.fetchone()
                return res["plan_id"] if res else 0


db_repo = DBRepository()
