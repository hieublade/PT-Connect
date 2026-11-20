"""
ai_services.py
Tầng xử lý AI và Thuật toán gợi ý (AI & Recommendation Layer)
1. Cosine Similarity Service: So khớp vector TF-IDF giữa nhu cầu học viên và hồ sơ PT.
2. Gemini AI Workout Service: Tự động sinh danh sách bài tập chuẩn hóa theo mục tiêu và số buổi.
"""

import json
import math
import os
import re
from typing import Any, Dict, List, Optional
import requests


import unicodedata


def strip_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để hỗ trợ tìm kiếm không dấu lẫn có dấu."""
    if not text:
        return ""
    nfkd_form = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace("đ", "d").replace("Đ", "D")


# =====================================================================
# 1. THUẬT TOÁN GỢI Ý HUẤN LUYỆN VIÊN (COSINE SIMILARITY)
# =====================================================================
class CosineRecommendationService:
    """
    Dịch vụ so khớp thông minh bằng mô hình Vector không gian (Vector Space Model).
    Tính góc Cosine giữa Vector nhu cầu của học viên và Vector hồ sơ của Huấn luyện viên.
    """

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        # Chuẩn hóa chữ thường và kết hợp cả phiên bản có dấu lẫn không dấu
        lower_text = text.lower()
        no_accents = strip_accents(lower_text)
        combined = f"{lower_text} {no_accents}"
        cleaned = re.sub(r"[^\w\s]", " ", combined)
        return re.sub(r"\s+", " ", cleaned).strip()

    @classmethod
    def recommend_pts(
        cls, query_text: str, pts_list: List[Dict[str, Any]], top_k: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Nhận văn bản nhu cầu tự nhiên của học viên, tính Cosine Similarity với từng PT.
        Trả về danh sách PT được lọc và xếp hạng từ cao xuống thấp (dưới 10 người, mặc định top_k=8).
        Chỉ giữ lại các PT có điểm phù hợp liên quan.
        """
        if not pts_list:
            return []

        cleaned_query = cls._clean_text(query_text)
        if not cleaned_query:
            # Nếu người dùng chưa nhập gì, trả về danh sách sắp xếp theo đánh giá sao
            return sorted(pts_list, key=lambda x: (x.get("average_rating", 0), x.get("total_reviews", 0)), reverse=True)[:top_k]

        # 1. Xây dựng văn bản đại diện (Document) cho mỗi PT
        pt_corpus: List[str] = []
        for pt in pts_list:
            spec = pt.get("specialty") or pt.get("specialties", "")
            doc_parts = [
                pt.get("full_name", ""),
                spec,
                spec,  # Nhân đôi trọng số chuyên môn
                pt.get("bio", ""),
                pt.get("working_locations", ""),
                pt.get("working_locations", ""),  # Nhân đôi trọng số địa điểm
                f"{pt.get('experience_years', 0)} năm kinh nghiệm",
            ]
            pt_doc = cls._clean_text(" ".join(filter(None, doc_parts)))
            pt_corpus.append(pt_doc)

        # 2. Thử tính bằng scikit-learn nếu có
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            corpus = [cleaned_query] + pt_corpus
            vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(corpus)

            # Tính cosine similarity giữa query (dòng 0) và tất cả PT (các dòng từ 1 trở đi)
            query_vec = tfidf_matrix[0:1]
            pt_vecs = tfidf_matrix[1:]
            sim_scores = cosine_similarity(query_vec, pt_vecs)[0]

        except Exception:
            # Fallback thuật toán TF-IDF thuần (Pure Python) khi môi trường không có sklearn
            sim_scores = cls._pure_python_cosine_similarity(cleaned_query, pt_corpus)

        # 3. Gán điểm và xếp hạng
        results = []
        for idx, pt in enumerate(pts_list):
            raw_score = float(sim_scores[idx]) if idx < len(sim_scores) else 0.0
            pct_score = round(min(raw_score * 100, 100.0), 1)

            # Tạo bản sao để không thay đổi trực tiếp dict gốc
            item = dict(pt)
            item["similarity_score"] = raw_score
            item["match_percentage"] = pct_score
            item["match_label"] = f"{pct_score}% phù hợp"
            results.append(item)

        # Sắp xếp giảm dần theo điểm tương đồng, nếu bằng điểm thì ưu tiên rating
        results.sort(
            key=lambda x: (x["similarity_score"], x.get("average_rating", 0), x.get("total_reviews", 0)),
            reverse=True,
        )

        # Lọc thông minh: Giữ lại những người có điểm liên quan (> 0), tối đa top_k (dưới 10 người)
        filtered_results = [p for p in results if p["similarity_score"] > 0]
        if not filtered_results:
            # Nếu không có PT nào khớp từ khóa, trả về top PT có đánh giá cao nhất (gắn cờ is_fallback_top_rated=True)
            top_rated = sorted(
                results,
                key=lambda x: (float(x.get("average_rating", 0)), int(x.get("total_reviews", 0)), int(x.get("experience_years", 0))),
                reverse=True
            )[:min(6, top_k)]
            for p in top_rated:
                p["is_fallback_top_rated"] = True
                p["match_percentage"] = None
            return top_rated

        return filtered_results[:top_k]

    @classmethod
    def _pure_python_cosine_similarity(cls, query: str, corpus: List[str]) -> List[float]:
        """Thuật toán TF-IDF + Cosine Similarity thuần Python dự phòng."""
        def tokenize(text: str) -> List[str]:
            return [w for w in text.split() if len(w) > 1]

        q_tokens = tokenize(query)
        doc_tokens_list = [tokenize(doc) for doc in corpus]
        all_docs = [q_tokens] + doc_tokens_list
        num_docs = len(all_docs)

        # Tính Document Frequency (DF)
        vocab = set(q_tokens)
        for tokens in doc_tokens_list:
            vocab.update(tokens)

        idf = {}
        for term in vocab:
            df = sum(1 for tokens in all_docs if term in tokens)
            idf[term] = math.log((num_docs + 1) / (df + 1)) + 1.0

        def to_vector(tokens: List[str]) -> Dict[str, float]:
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            vec = {}
            norm_sq = 0.0
            for t, count in tf.items():
                val = count * idf.get(t, 1.0)
                vec[t] = val
                norm_sq += val * val
            norm = math.sqrt(norm_sq) or 1.0
            return {k: v / norm for k, v in vec.items()}

        q_vec = to_vector(q_tokens)
        scores = []
        for doc_tokens in doc_tokens_list:
            d_vec = to_vector(doc_tokens)
            dot = sum(q_vec[k] * d_vec[k] for k in q_vec if k in d_vec)
            scores.append(max(0.0, dot))
        return scores


# =====================================================================
# 2. DỊCH VỤ SINH BÀI TẬP BẰNG AI (GOOGLE GEMINI API)
# =====================================================================
class GeminiWorkoutService:
    """
    Dịch vụ sinh giáo án bài tập chuẩn hóa bằng Google Gemini API (Zero-Shot).
    Có cơ chế dự phòng thông minh (Rule-Based Engine) đảm bảo hệ thống luôn sẵn sàng 100%.
    """

    @classmethod
    def generate_workout_plan(
        cls, goal: str, level: str = "Trung bình", sessions_per_week: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Sinh danh sách bài tập chi tiết theo cấu trúc chuẩn:
        - exercise_name: Tên bài tập
        - target_muscle: Nhóm cơ tác động
        - sets: Số hiệp
        - reps: Số lần lặp / thời lượng
        - rest_seconds: Thời gian nghỉ
        - notes: Kỹ thuật và lưu ý an toàn
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if api_key:
            try:
                ai_result = cls._call_gemini_api(api_key, goal, level, sessions_per_week)
                if ai_result:
                    return ai_result
            except Exception:
                pass

        # Khi không có API key hoặc lỗi mạng: Dùng hệ thống chuyên gia thể hình dự phòng
        return cls._generate_fallback_workout(goal, level, sessions_per_week)

    @classmethod
    def _call_gemini_api(
        cls, api_key: str, goal: str, level: str, sessions_per_week: int
    ) -> Optional[List[Dict[str, Any]]]:
        """Gọi HTTP REST API tới Gemini 1.5 Flash."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        prompt = f"""
        Bạn là Chuyên gia Huấn luyện viên Thể hình Chuyên nghiệp (Master Personal Trainer).
        Hãy thiết kế một danh sách các bài tập cho một buổi tập theo yêu cầu sau:
        - Mục tiêu: {goal}
        - Trình độ thể lực: {level}
        - Tần suất: {sessions_per_week} buổi/tuần

        YÊU CẦU ĐỊNH DẠNG:
        Chỉ trả về DUY NHẤT một mảng JSON thuần túy (không markdown, không bọc ```json, không giải thích thêm) với các trường:
        [
          {{
            "exercise_order": 1,
            "exercise_name": "Tên bài tập tiếng Anh hoặc tiếng Việt chuẩn",
            "target_muscle": "Nhóm cơ chính",
            "sets": 3,
            "reps": 12,
            "rest_seconds": 60,
            "notes": "Lưu ý tư thế, cách thở và kiểm soát tạ"
          }}
        ]
        """
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1000},
        }

        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Bóc tách JSON nếu bị bọc trong markdown
            raw_text = re.sub(r"^```(?:json)?", "", raw_text)
            raw_text = re.sub(r"```$", "", raw_text).strip()
            parsed = json.loads(raw_text)
            if isinstance(parsed, list) and len(parsed) > 0:
                # Đảm bảo có đủ thuộc tính
                for idx, item in enumerate(parsed):
                    item["exercise_order"] = idx + 1
                    item["sets"] = int(item.get("sets", 3))
                    item["reps"] = int(item.get("reps", 12))
                    item["rest_seconds"] = int(item.get("rest_seconds", 60))
                return parsed
        return None

    @classmethod
    def _generate_fallback_workout(
        cls, goal: str, level: str, sessions_per_week: int
    ) -> List[Dict[str, Any]]:
        """Hệ thống sinh bài tập chuyên môn dự phòng chuẩn khoa học thể thao."""
        goal_lower = goal.lower()

        if any(w in goal_lower for w in ["giảm mỡ", "giảm cân", "cardio", "hiit", "đốt calo"]):
            return [
                {
                    "exercise_order": 1,
                    "exercise_name": "Kettlebell Swing",
                    "target_muscle": "Đùi sau, Mông & Tim mạch",
                    "sets": 4,
                    "reps": 15,
                    "rest_seconds": 45,
                    "notes": "Phát lực bằng khớp hông, gồng chặt cơ bụng khi vung tạ lên",
                },
                {
                    "exercise_order": 2,
                    "exercise_name": "Dumbbell Goblet Squat",
                    "target_muscle": "Đùi trước & Cơ lõi",
                    "sets": 4,
                    "reps": 12,
                    "rest_seconds": 60,
                    "notes": "Hạ mông sâu ngang đầu gối, ngực mở rộng, gót chân bám chặt sàn",
                },
                {
                    "exercise_order": 3,
                    "exercise_name": "Push-up to Renegade Row",
                    "target_muscle": "Ngực, Lưng xô & Vai",
                    "sets": 3,
                    "reps": 10,
                    "rest_seconds": 45,
                    "notes": "Chống đẩy 1 nhịp rồi kéo tạ đơn từng bên, khóa chặt hông không lắc",
                },
                {
                    "exercise_order": 4,
                    "exercise_name": "Mountain Climber",
                    "target_muscle": "Cơ bụng & Tim mạch",
                    "sets": 3,
                    "reps": 20,
                    "rest_seconds": 30,
                    "notes": "Kéo đầu gối luân phiên về phía ngực với tốc độ cao, giữ lưng thẳng",
                },
                {
                    "exercise_order": 5,
                    "exercise_name": "Plank Shoulder Tap",
                    "target_muscle": "Cơ liên sườn & Ổn định",
                    "sets": 3,
                    "reps": 16,
                    "rest_seconds": 45,
                    "notes": "Vỗ tay chéo vai nhịp nhàng, kiểm soát thân người không xoay",
                },
            ]
        elif any(w in goal_lower for w in ["pilates", "chữa", "đau lưng", "phục hồi", "dẻo dai"]):
            return [
                {
                    "exercise_order": 1,
                    "exercise_name": "Cat-Cow Stretch",
                    "target_muscle": "Cột sống & Khớp cổ",
                    "sets": 3,
                    "reps": 10,
                    "rest_seconds": 30,
                    "notes": "Hít sâu võng lưng ngửa cổ, thở ra cuộn tròn lưng thu cằm về ngực",
                },
                {
                    "exercise_order": 2,
                    "exercise_name": "Bird-Dog Extension",
                    "target_muscle": "Lưng dưới & Cơ lõi sâu",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 45,
                    "notes": "Nâng tay trái chân phải thẳng hàng, giữ 2 giây ở đỉnh rồi đổi bên",
                },
                {
                    "exercise_order": 3,
                    "exercise_name": "Glute Bridge with Squeeze",
                    "target_muscle": "Mông & Gân kheo",
                    "sets": 4,
                    "reps": 15,
                    "rest_seconds": 45,
                    "notes": "Nâng hông ép chặt cơ mông, không dùng lực thắt lưng để đẩy",
                },
                {
                    "exercise_order": 4,
                    "exercise_name": "Dead Bug Core Stabilization",
                    "target_muscle": "Cơ bụng ngang & Xương chậu",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 45,
                    "notes": "Áp sát toàn bộ thắt lưng xuống thảm trong suốt quá trình hạ tay chân",
                },
            ]
        else:
            # Mặc định: Tăng cơ / Thể hình đa nhóm cơ (Hypertrophy Standard)
            return [
                {
                    "exercise_order": 1,
                    "exercise_name": "Barbell Bench Press",
                    "target_muscle": "Ngực toàn diện & Tay sau",
                    "sets": 4,
                    "reps": 10,
                    "rest_seconds": 90,
                    "notes": "Kẹp xương bả vai về sau, hạ thanh đòn có kiểm soát chạm ngực dưới",
                },
                {
                    "exercise_order": 2,
                    "exercise_name": "Incline Dumbbell Flyes",
                    "target_muscle": "Ngực trên & Tách cơ",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 60,
                    "notes": "Mở rộng góc cùi chỏ căng cơ ngực, khép tạ thở ra gồng ngực đỉnh",
                },
                {
                    "exercise_order": 3,
                    "exercise_name": "Dumbbell Overhead Shoulder Press",
                    "target_muscle": "Cơ vai trước & Vai giữa",
                    "sets": 4,
                    "reps": 10,
                    "rest_seconds": 75,
                    "notes": "Đẩy tạ dứt khoát qua đầu, không ưỡn cong lưng dưới",
                },
                {
                    "exercise_order": 4,
                    "exercise_name": "Tricep Rope Pushdown",
                    "target_muscle": "Cơ tam đầu (Tay sau)",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 60,
                    "notes": "Khóa chặt cùi chỏ sát sườn, mở rộng dây cáp ở điểm cuối",
                },
                {
                    "exercise_order": 5,
                    "exercise_name": "Hanging Leg Raise",
                    "target_muscle": "Cơ bụng dưới",
                    "sets": 3,
                    "reps": 12,
                    "rest_seconds": 45,
                    "notes": "Cuộn xương chậu lên cao, tránh đu lắc người lấy đà",
                },
            ]


cosine_service = CosineRecommendationService()
gemini_workout_service = GeminiWorkoutService()
