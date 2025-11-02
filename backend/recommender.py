import numpy as np
from sklearn.linear_model import LinearRegression
import random
import hashlib
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# ✅ NÂNG CẤP: Thêm thư viện cho AI
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans # Mặc dù không dùng ở insight, nhưng vẫn giữ cho các hàm khác nếu cần
from sklearn.preprocessing import StandardScaler
import google.generativeai as genai # 👈 Thêm thư viện Google AI
import json

# ✅ Nạp file .env để lấy key
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # 👈 Lấy key Gemini

if not YOUTUBE_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa nạp được YOUTUBE_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa nạp được GEMINI_API_KEY. AI tạo gợi ý sẽ bị TẮT.")
else:
    # Cấu hình AI
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ Đã nạp thành công Google Gemini AI.")
    except Exception as e:
        print(f"❌ Lỗi khi cấu hình Gemini AI: {e}")
        GEMINI_API_KEY = None # Tắt AI nếu lỗi


# --- CÁC HÀM XỬ LÝ DỮ LIỆU CƠ BẢN (KHÔNG ĐỔI) ---

def process_tlu_data_to_progress(tlu_marks_data, student_id):
    progress_list = []
    found_real_data = False 
    if not isinstance(tlu_marks_data, list):
        return generate_mock_data(student_id)
    for subject in tlu_marks_data:
        if not isinstance(subject, dict): continue 
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
            if subject is None: continue 
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
            print(f"ERROR: Loi khi xu ly mot mon hoc (Schedule): {e}")
    if not processed_list:
        return generate_mock_data(student_id) 
    return pd.DataFrame(processed_list)

def generate_mock_data(student_id):
    mock_courses = [
        {"course": "Lập Trình Game (Mock)", "base": 85}, {"course": "Phát Triển Ứng Dụng (Mock)", "base": 90},
        {"course": "Cơ Sở Dữ Liệu (Mock)", "base": 70}, {"course": "Mạng Máy Tính (Mock)", "base": 65},
    ]
    progress_list = []
    for item in mock_courses:
        seed_val = int(hashlib.sha1(f"{student_id}{item['course']}".encode('utf-8')).hexdigest(), 16) % (10**8)
        random.seed(seed_val)
        progress = (item['base'] + random.randint(-15, 10))
        progress_list.append({"course": item['course'], "progress": max(40, min(100, progress))})
    return pd.DataFrame(progress_list)

# --- CÁC HÀM AI (LỌC CỘNG TÁC & INSIGHT) ---

def build_cf_model_data(csv_data):
    try:
        data = csv_data[['Mã SV', 'Tên Môn Học', 'Điểm Tổng Kết (10)']].copy()
        data = data.dropna(subset=['Điểm Tổng Kết (10)'])
        data['Tên Môn Học'] = data['Tên Môn Học'].str.title()
        utility_matrix = data.pivot_table(index='Mã SV', columns='Tên Môn Học', values='Điểm Tổng Kết (10)').fillna(0)
        similarity_matrix = pd.DataFrame(cosine_similarity(utility_matrix.values), index=utility_matrix.index, columns=utility_matrix.index)
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
        if top_neighbors.empty: return []
        neighbor_scores = utility_matrix.loc[top_neighbors]
        avg_scores = neighbor_scores.mean(axis=0)
        user_scores = utility_matrix.loc[student_id_int]
        unseen_courses = user_scores[user_scores == 0].index
        if unseen_courses.empty: return []
        recommended_scores = avg_scores[unseen_courses]
        top_cf_recs = recommended_scores.nlargest(num_recs)
        return [{"course": course, "predicted_score": round(score, 1)} 
                for course, score in top_cf_recs.items() if score > 0]
    except Exception as e:
        print(f"Lỗi khi tính toán CF: {e}")
        return []

# =========================================================
# ‼️ HÀM ĐÃ SỬA LỖI (BỎ K-MEANS)
# =========================================================
def get_insight_logic(progress_data):
    """
    Phân tích AI dựa trên quy tắc (rule-based) rõ ràng.
    """
    
    if progress_data.empty: 
        return {"insights": ["Không đủ dữ liệu tiến độ để phân tích."]} 
        
    progresses = progress_data["progress"].tolist() 
    if not progresses: 
        return {"insights": ["Không có dữ liệu tiến độ để phân tích."]} 
        
    insights = []
    
    # --- 1. Phân tích cơ bản (Trung bình & Độ ổn định) ---
    avg_prog = np.mean(progresses)
    std_dev = np.std(progresses)
    
    insights.append(f"Điểm tiến độ trung bình của bạn là {avg_prog:.1f}%.")

    if std_dev > 20:
        insights.append(f"Hiệu suất không ổn định (độ lệch chuẩn {std_dev:.1f}%), điểm số chênh lệch lớn.")
    elif std_dev > 10:
         insights.append(f"Bạn học khá đều (độ lệch chuẩn {std_dev:.1f}%), tiếp tục phát huy.")
    else:
         insights.append(f"Bạn học rất ổn định (độ lệch chuẩn {std_dev:.1f}%), các môn có kết quả tương đồng.")

    # --- 2. Phân tích dựa trên quy tắc (Rule-Based) ---
    try:
        # Lấy danh sách các môn (Dùng .tolist() để tránh lỗi)
        strong_courses = progress_data[progress_data['progress'] >= 80]['course'].tolist()
        weak_courses = progress_data[progress_data['progress'] < 60]['course'].tolist()

        if strong_courses:
            insights.append(
                f"Nhóm môn THẾ MẠNH (Điểm >= 80): {', '.join(strong_courses)}."
            )
        
        if weak_courses:
             insights.append(
                f"Nhóm môn CẦN CẢI THIỆN (Điểm < 60): {', '.join(weak_courses)}."
            )
        
        if not strong_courses and not weak_courses:
            insights.append("Tất cả các môn đều đang ở mức ổn định (60-80%).")

    except Exception as e:
        print(f"Lỗi khi chạy phân tích insight dựa trên quy tắc: {e}")
    
    return {"insights": insights}


def predict_future_logic(progress_data):
    future_preds = []
    if progress_data.empty: return {"predictions": []}
    for index, row in progress_data.iterrows(): 
        current_progress = float(row["progress"])
        past_scores = np.clip(np.random.normal(current_progress, 5, size=5), 40, 100)
        X = np.arange(1, 6).reshape(-1, 1); model = LinearRegression().fit(X, past_scores)
        next_week = float(model.predict([[6]])[0]); risk = max(0, min(100, 100 - next_week)) 
        future_preds.append({"course": row["course"], "predicted_progress": round(next_week, 1), "risk": round(risk, 1)})
    warnings = [{"course": r["course"], "predicted_progress": r["predicted_progress"], "risk": r["risk"],
                 "advice": ("⚠️ Cần củng cố!" if r["predicted_progress"] < 60 else "✅ Tốt!")}
                for r in sorted(future_preds, key=lambda x: -x["risk"])]
    return {"predictions": warnings}


# =========================================================
# ✅ NÂNG CẤP AI: HÀM TẠO GỢI Ý BẰNG GEMINI AI
# =========================================================
def generate_ai_driven_content(course_name, progress):
    """
    Sử dụng Google Gemini AI để tạo lộ trình và chủ đề video.
    """
    if not GEMINI_API_KEY:
        print("TẮT AI: Không có GEMINI_API_KEY.")
        return None # Trả về None nếu không có key

    try:
        # 1. Cấu hình mô hình
        # ‼️ SỬA LỖI: Đổi tên model về 'gemini-pro' (phiên bản ổn định)
        model = genai.GenerativeModel('gemini-pro')
        
        # 2. Tạo Prompt (Câu lệnh)
        prompt = f"""
        Một sinh viên Việt Nam đang học yếu môn "{course_name}" (tiến độ hiện tại: {progress}%).
        Hãy đóng vai trò là một cố vấn học tập.
        
        Nhiệm vụ: Tạo một đối tượng JSON CHÍNH XÁC theo cấu trúc sau:
        {{
          "roadmap": [
            "một lời khuyên 1 (ngắn gọn, tập trung vào chủ đề quan trọng nhất)",
            "một lời khuyên 2 (về thực hành hoặc lý thuyết)",
            "một lời khuyên 3 (về kỹ năng liên quan)",
            "một lời khuyên 4 (về tài liệu hoặc bước tiếp theo)"
          ],
          "video_topics": [
            "chủ đề tìm kiếm video 1 (ví dụ: 'hướng dẫn {course_name} cơ bản')",
            "chủ đề tìm kiếm video 2 (ví dụ: 'thực hành {course_name} cho người mới bắt đầu')",
            "chủ đề tìm kiếm video 3 (ví dụ: 'bài tập {course_name} nâng cao')"
          ]
        }}
        
        QUAN TRỌNG: Chỉ trả lời bằng đối tượng JSON, không thêm bất kỳ văn bản nào khác.
        """
        
        # 3. Gọi AI
        print(f"🤖 Đang gọi Gemini AI cho môn: {course_name}...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json" # Yêu cầu AI trả về JSON
            )
        )
        
        # 4. Xử lý kết quả
        # Loại bỏ các ký tự ```json và ``` ở đầu/cuối nếu có
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        ai_content = json.loads(cleaned_response_text)
        print(f"✅ AI đã tạo gợi ý cho: {course_name}")
        return ai_content

    except Exception as e:
        print(f"❌ Lỗi khi gọi Gemini AI cho môn {course_name}: {e}")
        if 'response' in locals():
            print(f"   Response text (nếu có): {response.text}")
        return None # Trả về None nếu AI thất bại

def get_fallback_recommendation(course_name, progress):
    """
    Hàm dự phòng (fallback) nếu AI bị lỗi.
    Sử dụng template cũ.
    """
    print(f"⚠️ Dùng gợi ý dự phòng (template) cho môn: {course_name}")
    roadmap = [
        f"Xác định lại các khái niệm cốt lõi của môn {course_name} (hiện tại {progress}%)"
    ]
    if progress < 50:
        roadmap.append("Bắt đầu lại với các bài giảng cơ bản, tập trung vào nền tảng.")
    else:
        roadmap.append("Tập trung vào các chủ đề nâng cao và bài tập lớn mà bạn còn vướng mắc.")
    roadmap.append("Chủ động đặt câu hỏi với giảng viên hoặc trợ giảng.")
    
    # Tìm kiếm Google/YouTube chung chung
    videos = search_youtube_videos(f"bài giảng {course_name}")
    query_safe_course = course_name.replace(' ', '+')
    documents = [{"title": f"Tìm tài liệu {course_name}", "url": f"https://www.google.com/search?q=tài+liệu+{query_safe_course}+pdf"}]
    exercises = [{"title": f"Tìm bài tập {course_name}", "url": f"https://www.google.com/search?q=bài+tập+{query_safe_course}"}]
    
    return {"roadmap": roadmap, "videos": videos, "documents": documents, "exercises": exercises}

# =========================================================
# ✅ NÂNG CẤP AI: HÀM GỢI Ý CHÍNH (ĐÃ NÂNG CẤP)
# =========================================================
def get_recommendation_logic(progress_data, student_id_int, cf_model_data, materials_db=None): # Bỏ materials_db
    """
    Logic gợi ý TỔNG HỢP:
    1. Gợi ý "Cải thiện": Dựa trên Gemini AI (thay thế JSON và template)
    2. Gợi ý "Khám phá": Dựa trên mô hình CF (từ CSV)
    """
    
    # --- 1. Gợi ý "Cần cải thiện" (Từ TLU API + Gemini AI) ---
    improve_recommendations = []
    low_courses = [row for index, row in progress_data.iterrows() if row["progress"] < 70]

    for course_data in low_courses:
        course = course_data["course"]
        progress = course_data["progress"]
        
        # Thử gọi AI để tạo nội dung
        ai_content = generate_ai_driven_content(course, progress)
        
        roadmap, videos, documents, exercises = [], [], [], []

        if ai_content:
            # AI THÀNH CÔNG!
            roadmap = ai_content.get("roadmap", [])
            
            # Lấy các chủ đề video từ AI và dùng chúng để TÌM KIẾM
            video_topics = ai_content.get("video_topics", [])
            for topic in video_topics:
                # Gọi API YouTube với chủ đề "thông minh" từ AI
                videos.extend(search_youtube_videos(topic, max_results=1)) 
            
            # AI không tạo tài liệu/bài tập, chúng ta tạo link Google
            query_safe_course = course.replace(' ', '+')
            documents = [{"title": f"Tìm tài liệu {course} (Google)", "url": f"https://www.google.com/search?q=tài+liệu+{query_safe_course}+pdf"}]
            exercises = [{"title": f"Tìm bài tập {course} (Google)", "url": f"https://www.google.com/search?q=bài+tập+{query_safe_course}"}]
        
        else:
            # AI THẤT BẠI! (do lỗi key, v.v.)
            # Dùng hàm dự phòng (template cũ)
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

    # --- 2. Gợi ý "Khám phá" (Từ mô hình CF) ---
    discover_recommendations = []
    if cf_model_data and student_id_int:
        utility_matrix, similarity_matrix = cf_model_data
        if utility_matrix is not None and similarity_matrix is not None:
            discover_recommendations = get_cf_recommendations(
                student_id_int, utility_matrix, similarity_matrix, num_recs=5
            )
            
    # --- 3. Tổng hợp kết quả ---
    message = "Đây là các gợi ý được cá nhân hoá bằng AI cho bạn."
    if not improve_recommendations and not discover_recommendations:
        message = "🎉 Học tốt! AI không tìm thấy gợi ý nào cần thiết cho bạn."
    elif not improve_recommendations:
        message = "🎉 Các môn đều đạt tốt! Đây là một số gợi ý khám phá môn học mới từ AI."
        
    return {
        "message": message,
        "improve_recommendations": improve_recommendations,
        "discover_recommendations": discover_recommendations
    }

def search_youtube_videos(query, max_results=2):
    """
    🔍 Tìm video YouTube liên quan đến môn học. (Hàm này vẫn được giữ lại)
    """
    if not YOUTUBE_API_KEY:
        print("Lỗi: Thiếu YOUTUBE_API_KEY. Không thể tìm video.")
        return []
    try:
        print(f"🎥 Đang gọi YouTube API với query (từ AI): {query}")
        url = (f"https://www.googleapis.com/youtube/v3/search"
               f"?part=snippet&type=video&q={query}&maxResults={max_results}&key={YOUTUBE_API_KEY}")
        response = requests.get(url, timeout=5)
        response.raise_for_status(); data = response.json()
        videos = []
        for item in data.get("items", []):
            video_id = item["id"].get("videoId")
            title = item["snippet"]["title"]
            if video_id:
                videos.append({"title": title, "url": f"https://www.youtube.com/watch?v={video_id}"})
        return videos
    except Exception as e:
        print(f"❌ Lỗi khi tìm video YouTube cho {query}: {e}")
        return []