import numpy as np
from sklearn.linear_model import LinearRegression
import random
import hashlib
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import json
import sqlite3
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import google.generativeai as genai

# Đã nạp file .env để lấy key
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Lấy key Gemini

if not YOUTUBE_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa nạp đủ YOUTUBE_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa nạp đủ GEMINI_API_KEY. AI trình gửi sẽ bị Tắt.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Đã nạp thành công Google Gemini AI.")
    except Exception as e:
        print(f"❌ Lỗi khi cấu hình Gemini AI: {e}")
        GEMINI_API_KEY = None

# =========================================================
# Khởi tạo hệ thống cache (AI + YouTube)
# =========================================================
DB_NAME = os.path.join(os.path.dirname(__file__), "ai_youtube_cache.db")

def init_cache_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_cache (
            prompt TEXT PRIMARY KEY,
            response TEXT,
            expires_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS youtube_cache (
            query TEXT PRIMARY KEY,
            result TEXT,
            expires_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Cache DB sẵn sàng (ai_cache + youtube_cache).")

init_cache_db()

# --- Hàm cache AI ---
def get_ai_cache(prompt):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT response, expires_at FROM ai_cache WHERE prompt=?", (prompt,))
    row = c.fetchone()
    conn.close()
    if row:
        response, expires_at = row
        if datetime.now() < datetime.fromisoformat(expires_at):
            print(f"CACHE HIT: AI cache cho '{prompt[:40]}...'")
            return json.loads(response)
        else:
            print(f"CACHE EXPIRED: AI cache cho '{prompt[:40]}...'")
    return None

def set_ai_cache(prompt, response):
    expires_at = (datetime.now() + timedelta(hours=12)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO ai_cache (prompt, response, expires_at)
        VALUES (?, ?, ?)
    """, (prompt, json.dumps(response), expires_at))
    conn.commit()
    conn.close()
    print(f"CACHE SET: AI cache cho '{prompt[:40]}...'")

# --- Hàm cache YouTube ---
def get_youtube_cache(query):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT result, expires_at FROM youtube_cache WHERE query=?", (query,))
    row = c.fetchone()
    conn.close()
    if row:
        result, expires_at = row
        if datetime.now() < datetime.fromisoformat(expires_at):
            print(f"CACHE HIT: YouTube cache cho '{query[:40]}...'")
            return json.loads(result)
        else:
            print(f"CACHE EXPIRED: YouTube cache cho '{query[:40]}...'")
    return None

def set_youtube_cache(query, result):
    expires_at = (datetime.now() + timedelta(hours=12)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO youtube_cache (query, result, expires_at)
        VALUES (?, ?, ?)
    """, (query, json.dumps(result), expires_at))
    conn.commit()
    conn.close()
    print(f"CACHE SET: YouTube cache cho '{query[:40]}...'")

# --- Các hàm xử lý dữ liệu cơ bản (KHÔNG đổi) ---

def process_tlu_data_to_progress(tlu_marks_data, student_id):
    progress_list = []
    found_real_data = False 
    if not isinstance(tlu_marks_data, list):
        return generate_mock_data(student_id)
    for subject in tlu_marks_data:
        if not isinstance(subject, dict):
            continue 
        try:
            subject_name = subject.get("subject", {}).get("subjectName", "N/A").title()
            score = subject.get("mark") 
            if (isinstance(score, (int, float))):
                progress = int(score * 10) 
                found_real_data = True
            else:
                continue 
            progress_list.append({"course": subject_name, "progress": max(0, min(100, progress))})
        except Exception as e:
            print(f"ERROR: Failed processing one subject (Mark). Reason: {e}")
    if not found_real_data:
        return generate_mock_data(student_id)
    return pd.DataFrame(progress_list)

def process_schedule_to_courses(schedule_data, student_id): 
    processed_subjects, processed_list = set(), []
    if not isinstance(schedule_data, list):
        return pd.DataFrame(processed_list)
    for subject in schedule_data:
        try:
            if subject is None:
                continue 
            subject_details = subject.get("courseSubject", {}).get("semesterSubject", {}).get("subject", {}) or {}
            subject_name = subject_details.get("subjectName", "N/A").title()
            subject_code = subject_details.get("subjectCode", "N/A")
            teacher_details = subject.get("courseSubject", {}).get("teacher", {}) or {}
            teacher_name = teacher_details.get("displayName", "N/A")
            if subject_name != "N/A" and subject_code != "N/A":
                if subject_code not in processed_subjects:
                    processed_subjects.add(subject_code)
                    processed_list.append({"course": subject_name, "subjectCode": subject_code, "teacherName": teacher_name, "progress": 0})
        except Exception as e:
            print(f"ERROR: Lỗi khi xử lý một môn học (Schedule): {e}")
    if not processed_list:
        return generate_mock_data(student_id) 
    return pd.DataFrame(processed_list)

def generate_mock_data(student_id):
    mock_courses = [
        {"course": "Lập Trình Game (Mock)", "base": 85}, 
        {"course": "Phát Triển Đường Dừng (Mock)", "base": 90},
        {"course": "Cơ Sở Dữ Liệu (Mock)", "base": 70}, 
        {"course": "Mạng Máy Tính (Mock)", "base": 65},
    ]
    progress_list = []
    for item in mock_courses:
        seed_val = int(hashlib.sha1(f"{student_id}{item['course']}".encode('utf-8')).hexdigest(), 16) % (10**8)
        random.seed(seed_val)
        progress = (item['base'] + random.randint(-15, 10))
        progress_list.append({"course": item['course'], "progress": max(40, min(100, progress))})
    return pd.DataFrame(progress_list)

# --- Các hàm AI (logic & insight) ---

def build_cf_model_data(csv_data):
    try:
        data = csv_data[['Mã SV', 'Tên Môn Học', 'Điểm Tổng Kết (10)']].copy()
        data = data.dropna(subset=['Điểm Tổng Kết (10)'])
        data['Tên Môn Học'] = data['Tên Môn Học'].str.title()
        utility_matrix = data.pivot_table(index='Mã SV', columns='Tên Môn Học', values='Điểm Tổng Kết (10)').fillna(0)
        similarity_matrix = pd.DataFrame(cosine_similarity(utility_matrix.values),
                                         index=utility_matrix.index,
                                         columns=utility_matrix.index)
        return utility_matrix, similarity_matrix
    except Exception as e:
        print(f"Lỗi khi xây dựng mô hình CF: {e}")
        return None, None

def get_cf_recommendations(student_id_int, utility_matrix, similarity_matrix, num_recs=5):
    try:
        if student_id_int not in similarity_matrix.index:
            return []
        sim_scores = similarity_matrix[student_id_int].drop(student_id_int)
        top_neighbors = sim_scores.nlargest(5).index
        if top_neighbors.empty:
            return []
        neighbor_scores = utility_matrix.loc[top_neighbors]
        avg_scores = neighbor_scores.mean(axis=0)
        user_scores = utility_matrix.loc[student_id_int]
        unseen_courses = user_scores[user_scores == 0].index
        if unseen_courses.empty:
            return []
        recommended_scores = avg_scores[unseen_courses]
        top_cf_recs = recommended_scores.nlargest(num_recs)
        return [{"course": course, "predicted_score": round(score, 1)} 
                for course, score in top_cf_recs.items() if score > 0]
    except Exception as e:
        print(f"Lỗi khi tính toán CF: {e}")
        return []

# =========================================================
# Hàm Insight (K-Means, rule-based) -- phiên bản đơn giản
# =========================================================
def get_insight_logic(progress_data):
    """
    Phân tích AI dựa trên quy tắc rõ ràng.
    """
    if progress_data.empty:
        return {"insights": ["Không đủ dữ liệu tiến độ để phân tích."]}
    progresses = progress_data["progress"].tolist()
    if not progresses:
        return {"insights": ["Không có dữ liệu tiến độ để phân tích."]}
    insights = []
    # --- 1. Phân tích cơ bản (Trung bình & Độ lệch chuẩn) ---
    avg_prog = np.mean(progresses)
    std_dev = np.std(progresses)
    insights.append(f"Điểm tiến độ trung bình của bạn là {avg_prog:.1f}%.")
    if std_dev > 20:
        insights.append(f"Hiệu suất không ổn định (độ lệch chuẩn khoảng {std_dev:.1f}%), cần chỉnh lịch làm.")
    elif std_dev > 10:
        insights.append(f"Bạn học khá ổn (độ lệch chuẩn khoảng {std_dev:.1f}%), tiếp tục phát huy.")
    else:
        insights.append(f"Bạn học rất ổn định (độ lệch chuẩn khoảng {std_dev:.1f}%), các môn có kết quả tương đồng.")
    # --- 2. Phân tích theo quy tắc ---
    try:
        strong_courses = progress_data[progress_data['progress'] >= 80]['course'].tolist()
        weak_courses = progress_data[progress_data['progress'] < 60]['course'].tolist()
        if strong_courses:
            insights.append(f"Nhóm môn THÀNH CÔNG (điểm >= 80): {', '.join(strong_courses)}.")
        if weak_courses:
            insights.append(f"Nhóm môn CẦN CẢI THIỆN (điểm < 60): {', '.join(weak_courses)}.")
        if not strong_courses and not weak_courses:
            insights.append("Tất cả các môn đều đang ở mức trung bình (60-80%).")
    except Exception as e:
        print(f"Lỗi khi chạy phân tích insight theo quy tắc: {e}")
    return {"insights": insights}

def predict_future_logic(progress_data):
    future_preds = []
    if progress_data.empty:
        return {"predictions": []}
    for index, row in progress_data.iterrows():
        current_progress = float(row["progress"])
        past_scores = np.clip(np.random.normal(current_progress, 5, size=5), 40, 100)
        X = np.arange(1, 6).reshape(-1, 1)
        model = LinearRegression().fit(X, past_scores)
        next_week = float(model.predict([[6]])[0])
        risk = max(0, min(100, 100 - next_week))
        future_preds.append({
            "course": row["course"],
            "predicted_progress": round(next_week, 1),
            "risk": round(risk, 1)
        })
    warnings = [
        {
            "course": r["course"],
            "predicted_progress": r["predicted_progress"],
            "risk": r["risk"],
            "advice": ("⚠️ Cần cố gắng!" if r["predicted_progress"] < 60 else "✅ Đã tốt!")
        }
        for r in sorted(future_preds, key=lambda x: -x["risk"])
    ]
    return {"predictions": warnings}

# =========================================================
# Hàm gọi GEMINI AI để gợi ý học tập
# =========================================================
def generate_ai_driven_content(course_name, progress):
    if not GEMINI_API_KEY:
        print("Tắt AI: Không có GEMINI_API_KEY.")
        return None
    prompt = f"AI_GEMINI_{course_name}_{progress}"
    cached = get_ai_cache(prompt)
    if cached:
        return cached
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt_text = f"""
        Một sinh viên Việt Nam đang học yếu môn "{course_name}" (tiến độ: {progress}%).
        Tạo JSON có dạng:
        {{
          "roadmap": ["Lời khuyên 1", "Lời khuyên 2", "Lời khuyên 3", "Lời khuyên 4"],
          "video_topics": ["chủ đề video 1", "chủ đề video 2", "chủ đề video 3"]
        }}
        """
        print(f"➡️ Đang gọi Gemini AI cho môn: {course_name}...")
        response = model.generate_content(
            prompt_text,
            generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
        )
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        ai_content = json.loads(cleaned_text)
        set_ai_cache(prompt, ai_content)
        print(f"✅ AI trả về gợi ý cho: {course_name}")
        return ai_content
    except Exception as e:
        print(f"❌ Lỗi khi gọi Gemini AI cho môn {course_name}: {e}")
        return None

def get_fallback_recommendation(course_name, progress):
    """
    Hàm dự phòng (fallback) nếu AI bị lỗi.
    Dùng template cố định.
    """
    print(f"⚠️ Dùng gợi ý dự phòng (template) cho môn: {course_name}")
    roadmap = [
        f"Xác định lại khối nền tảng của môn {course_name} (hiện tại {progress}%)."
    ]
    if progress < 50:
        roadmap.append("Bắt đầu lại với các bài giảng cơ bản, tập trung vào nền tảng.")
    else:
        roadmap.append("Tập trung vào các chủ đề nâng cao và bài tập lớn cần vượt trội.")
    roadmap.append("Tìm đường hướng học với giảng viên hoặc người có kinh nghiệm.")
    videos = search_youtube_videos(f"bài giảng {course_name}")
    query_safe_course = course_name.replace(' ', '+')
    documents = [
        {
            "title": f"Tải tài liệu {course_name}",
            "url": f"https://www.google.com/search?q=tải+{query_safe_course}+pdf"
        }
    ]
    exercises = [
        {
            "title": f"Tìm bài tập {course_name}",
            "url": f"https://www.google.com/search?q=bài+tập+{query_safe_course}"
        }
    ]
    return {
        "roadmap": roadmap,
        "videos": videos,
        "documents": documents,
        "exercises": exercises
    }

# =========================================================
# Hàm logic chính gợi ý học tập
# =========================================================
def get_recommendation_logic(progress_data, student_id_int, cf_model_data, materials_db=None):
    """
    Logic gợi ý tổng hợp:
    1. Gợi ý 'Cần cải thiện': Dựa trên Gemini AI
    2. Gợi ý 'Khám phá': Dựa trên mô hình CF (CSV)
    """
    # --- 1. Gợi ý 'Cần cải thiện' (TLU API + Gemini AI) ---
    improve_recommendations = []
    low_courses = [row for index, row in progress_data.iterrows() if row["progress"] < 70]
    for course_data in low_courses:
        course = course_data["course"]
        progress = course_data["progress"]
        ai_content = generate_ai_driven_content(course, progress)
        roadmap, videos, documents, exercises = [], [], [], []
        if ai_content:
            if isinstance(ai_content, dict):
                roadmap = ai_content.get("roadmap", [])
                video_topics = ai_content.get("video_topics", [])
            elif isinstance(ai_content, list):
                if len(ai_content) > 0 and isinstance(ai_content[0], dict):
                    roadmap = ai_content[0].get("roadmap", [])
                    video_topics = ai_content[0].get("video_topics", [])
                else:
                    roadmap = ai_content
                    video_topics = []
            else:
                roadmap, video_topics = [], []

            for topic in video_topics:
                videos.extend(search_youtube_videos(topic, max_results=1))
            query_safe_course = course.replace(' ', '+')
            documents = [
                {"title": f"Tải tài liệu {course} (Google)", "url": f"https://www.google.com/search?q=tải+{query_safe_course}+pdf"}
            ]
            exercises = [
                {"title": f"Tìm bài tập {course} (Google)", "url": f"https://www.google.com/search?q=bài+tập+{query_safe_course}"}
            ]
        else:
            fallback_data = get_fallback_recommendation(course, progress)
            roadmap = fallback_data["roadmap"]
            videos = fallback_data["videos"]
            documents = fallback_data["documents"]
            exercises = fallback_data["exercises"]

        improve_recommendations.append({
            "course": course,
            "progress": progress,
            "roadmap": roadmap,
            "resources": {"videos": videos, "documents": documents, "exercises": exercises}
        })
    # --- 2. Gợi ý 'Khám phá' (mô hình CF) ---
    discover_recommendations = []
    if cf_model_data and student_id_int:
        utility_matrix, similarity_matrix = cf_model_data
        if utility_matrix is not None and similarity_matrix is not None:
            discover_recommendations = get_cf_recommendations(student_id_int,
                                                               utility_matrix,
                                                               similarity_matrix,
                                                               num_recs=5)
    # --- 3. Tổng hợp kết quả ---
    message = "Dưới đây là các gợi ý tốt nhất cho bạn."
    if not improve_recommendations and not discover_recommendations:
        message = "🎉 Bạn học tốt! AI không tìm thấy gợi ý nào cần thiết."
    elif not improve_recommendations:
        message = "🔍 Các môn học của bạn khá ổn! Dưới đây là gợi ý khám phá thêm."
    return {
        "message": message,
        "improve_recommendations": improve_recommendations,
        "discover_recommendations": discover_recommendations
    }

import requests, urllib.parse

def search_youtube_videos(query, max_results=2):
    if not YOUTUBE_API_KEY:
        print("❌ Thiếu API key YouTube.")
        return []
    academic_keywords = " học tập OR bài giảng OR course OR university OR tutorial OR giới thiệu học OR cybersecurity"
    full_query = f"{query} {academic_keywords}"
    encoded_query = urllib.parse.quote(full_query)
    url = (
        f"https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&type=video&maxResults={max_results}"
        f"&regionCode=VN&relevanceLanguage=vi"
        f"&safeSearch=strict&order=relevance"
        f"&q={encoded_query}&key={YOUTUBE_API_KEY}"
    )
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        videos = []
        for item in data.get("items", []):
            vid = item["id"]["videoId"]
            title = item["snippet"]["title"]
            if not any(word in title.lower() for word in ["kickfit", "boxing", "nhảy", "review", "vlog"]):
                videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={vid}",
                })
        return videos
    except Exception as e:
        print(f"❌ Lỗi YouTube: {e}")
        return []
