import numpy as np
from sklearn.linear_model import LinearRegression
import random
import hashlib
import pandas as pd
import requests
import os
from dotenv import load_dotenv  # ✅ Thêm dòng này

# ✅ Nạp file .env để lấy key (bắt buộc)
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("⚠️ CẢNH BÁO: Chưa nạp được YOUTUBE_API_KEY từ .env")
else:
    print("✅ Đã nạp thành công YOUTUBE_API_KEY")



# --- HÀM 1: XỬ LÝ ĐIỂM TỔNG KẾT (CHO DASHBOARD/GỢI Ý) ---
def process_tlu_data_to_progress(tlu_marks_data, student_id):
    """
    Xử lý dữ liệu ĐIỂM TỔNG KẾT (từ TLU API) thành danh sách tiến độ.
    Đọc điểm thật (từ 'mark') thay vì giả lập.
    """
    progress_list = []
    found_real_data = False 
    
    if not isinstance(tlu_marks_data, list):
        print("ERROR: TLU Mark data is not a list.")
        return generate_mock_data(student_id) # Đây đã là DataFrame (Đúng)

    for subject in tlu_marks_data:
        if not isinstance(subject, dict):
            continue 
        try:
            subject_name = subject.get("subject", {}).get("subjectName", "N/A")
            score = subject.get("mark") 

            if (isinstance(score, (int, float))):
                progress = int(score * 10) 
                found_real_data = True
            else:
                continue 

            progress_list.append({
                "course": subject_name,
                "progress": max(0, min(100, progress)) 
            })
                
        except Exception as e:
            print(f"ERROR: Failed processing one subject (Mark). Reason: {e}")

    if not found_real_data:
        print("WARNING: No subjects with real scores ('mark') found. Falling back to Mock Data.")
        return generate_mock_data(student_id) # Gọi hàm giả lập

    print(f"SUCCESS: Processed {len(progress_list)} subjects (Real Mark Data).")
    return pd.DataFrame(progress_list) # (ĐÚNG - Chuyển nó thành DataFrame)

# --- HÀM 2: XỬ LÝ LỊCH HỌC (CHO TRANG "CÁC MÔN ĐANG HỌC") ---
def process_schedule_to_courses(schedule_data, student_id): 
    """
    Xử lý JSON LỊCH HỌC, lấy Mã Môn, Tên Môn, Giảng Viên (DUY NHẤT).
    Tự động gán progress = 0% (vì là môn đang học).
    """
    print("... Dang xu ly du lieu Lich hoc...")
    
    processed_subjects = set() 
    processed_list = [] 

    if not isinstance(schedule_data, list):
        print("ERROR: Du lieu lich hoc tra ve khong phai la mot danh sach.")
        return pd.DataFrame(processed_list) # 🚨 TRẢ VỀ DATAFRAME RỖNG

    for subject in schedule_data:
        try:
            if subject is None:
                continue 
            
            subject_details = subject.get("courseSubject", {}).get("semesterSubject", {}).get("subject", {})
            if subject_details is None:
                subject_details = {} 

            subject_name = subject_details.get("subjectName", "N/A")
            subject_code = subject_details.get("subjectCode", "N/A")
            
            teacher_details = subject.get("courseSubject", {}).get("teacher", {})
            if teacher_details is None: 
                teacher_details = {}
            teacher_name = teacher_details.get("displayName", "N/A")
            
            if subject_name != "N/A" and subject_code != "N/A":
                if subject_code not in processed_subjects:
                    processed_subjects.add(subject_code)
                    processed_list.append({
                        "course": subject_name,
                        "subjectCode": subject_code,
                        "teacherName": teacher_name,
                        "progress": 0 
                    })
                
        except Exception as e:
            print(f"ERROR: Loi khi xu ly mot mon hoc (Schedule): {e}")
    if not processed_list:
        print("WARNING: Khong co du lieu mon hoc (Schedule) de xuat.")
        return generate_mock_data(student_id) 

    print(f"SUCCESS: Da xu ly {len(processed_list)} mon hoc (tu Lich hoc).")
    return pd.DataFrame(processed_list) # 🚨 TRẢ VỀ DATAFRAME


def generate_mock_data(student_id):
    """
    Hàm tạo dữ liệu giả lập (Mock) khi TLU API không có điểm thật.
    """
    print("Generating Mock Data for Dashboard...")
    mock_courses = [
        {"course": "Lập trình Game (Mock)", "base": 85},
        {"course": "Phát triển Ứng dụng (Mock)", "base": 90},
        {"course": "Cơ sở dữ liệu (Mock)", "base": 70},
        {"course": "Mạng máy tính (Mock)", "base": 65},
        {"course": "Hệ thống thông tin (Mock)", "base": 75}
    ]

    progress_list = []
    for item in mock_courses:
        seed_val = int(hashlib.sha1(f"{student_id}{item['course']}".encode('utf-8')).hexdigest(), 16) % (10**8)
        random.seed(seed_val)
        
        base_progress = 70
        if "Game" in item['course'] or "Ứng dụng" in item['course']:
            base_progress = 85 
        
        progress = base_progress + random.randint(-15, 10)
        progress_list.append({
            "course": item['course'],
            "progress": max(40, min(100, progress))
        })
    return pd.DataFrame(progress_list) # 🚨 TRẢ VỀ DATAFRAME

# --- CÁC HÀM LOGIC AI (ĐÃ SỬA LỖI TYPEERROR) ---

def get_recommendation_logic(progress_data):
    """
    Logic gợi ý học tập dựa trên tiến độ thấp (dưới 70%).
    (progress_data là một DataFrame)
    """
    # Lọc các môn có tiến độ < 70%
    low_courses = [row for index, row in progress_data.iterrows() if row["progress"] < 70]

    if not low_courses:
        return {
            "message": "🎉 Tất cả các môn đều đạt tốt! Bạn đang đi đúng hướng.",
            "recommendations": []
        }

    recommendations = []
    for course_data in low_courses:
        course = course_data["course"]
        progress = course_data["progress"]

        # 🧭 Roadmap (các bước hành động)
        roadmap = [
            f"Ôn lại kiến thức cơ bản trong môn {course} (đạt {progress}%)",
            "Tập trung làm thêm bài tập dự án thực tế liên quan.",
            "Tìm tài liệu/video chuyên sâu từ các nguồn ngoài.",
            "Thảo luận với bạn bè hoặc giảng viên về phần kiến thức khó."
        ]

        # 🔍 Tích hợp gợi ý video YouTube
        videos = search_youtube_videos(f"bài giảng {course} đại học")

        # 📚 Tích hợp tài liệu & bài tập
        resources = get_learning_resources(course)

        # ✅ Tổng hợp thành một gợi ý hoàn chỉnh
        recommendations.append({
            "course": course,
            "progress": progress,
            "roadmap": roadmap,
            "resources": {
                "videos": videos,
                "documents": resources["documents"],
                "exercises": resources["exercises"]
            }
        })

    return {
        "message": "⚡ Một số môn cần cải thiện để đạt thành tích tốt hơn.",
        "recommendations": recommendations
    }


def predict_future_logic(progress_data):
    """
    Mô phỏng dự báo tiến độ học tập (dùng Linear Regression).
    (progress_data là một DataFrame)
    """
    future_preds = []
    
    # Đảm bảo import pandas as pd đã được thêm ở đầu file recommender.py
    # if not isinstance(progress_data, pd.DataFrame):
    #     print("ERROR: progress_data is not a DataFrame.")
    #     return {"predictions": []}

    if progress_data.empty: # 🚨 SỬA LỖI: Kiểm tra DataFrame rỗng
        return {"predictions": []}
        
    # 🚨 SỬA LỖI TYPEERROR: Lặp qua DataFrame dùng .iterrows()
    for index, row in progress_data.iterrows(): 
        # Đảm bảo giá trị là float (Chống lỗi 'ambiguous' nếu chưa sửa ở app.py)
        current_progress = float(row["progress"])

        past_scores = np.clip(
            np.random.normal(current_progress, 5, size=5), 40, 100
        )
        X = np.arange(1, 6).reshape(-1, 1) 
        model = LinearRegression().fit(X, past_scores)
        
        # Đảm bảo kết quả là float
        next_week = float(model.predict([[6]])[0]) 
        
        # Hàm tính toán đã ổn sau khi next_week là float
        risk = max(0, min(100, 100 - next_week)) 
        
        future_preds.append({
            "course": row["course"],
            "predicted_progress": round(next_week, 1),
            "risk": round(risk, 1),
        })

    warnings = [
        {
            "course": r["course"],
            "predicted_progress": r["predicted_progress"],
            "risk": r["risk"],
            "advice": (
                "⚠️ Can cung co them trong tuan toi!"
                if r["predicted_progress"] < 60
                else "✅ Tiep tuc duy tri phong do hien tai!"
            ), # <-- KHÔNG CẦN DẤU PHẨY HAY DẤU NGOẶC KÉP THÊM Ở ĐÂY
        }
        for r in sorted(future_preds, key=lambda x: -x["risk"])
    ]

    return {"predictions": warnings}

def get_insight_logic(progress_data):
    """
    Phân tích AI đơn giản (dựa trên độ phân tán của điểm số).
    (progress_data là một DataFrame)
    """
    if progress_data.empty: # 🚨 SỬA LỖI: Kiểm tra DataFrame rỗng
        return {"insights": ["Khong co du lieu tien do de phan tich."]} 
        
    # 🚨 SỬA LỖI TYPEERROR: Lấy cột "progress" từ DataFrame
    progresses = progress_data["progress"].tolist() 
    
    if not progresses: 
        return {"insights": ["Khong co du lieu tien do de phan tich."]} 
        
    avg_prog = np.mean(progresses)

    insights = [
        f"Diem tien do trung binh toan khoa la {avg_prog:.1f}%.",
        f"Co {len([p for p in progresses if p < 70])} mon can uu tien cai thien trong tuan nay.",
        "Moi tuong quan giua cac mon Lap trinh va CSDL dang duoc giu vung.",
    ]
    
    return {"insights": insights}

def search_youtube_videos(query, max_results=3):
    """
    🔍 Tìm video YouTube liên quan đến môn học.
    Trả về danh sách [{title, url}].
    """
    try:
        print(f"🎥 Đang gọi YouTube API với query: {query}")
        print(f"🔑 API KEY: {YOUTUBE_API_KEY[:10]}...")
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=video&q={query}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            video_id = item["id"].get("videoId")
            title = item["snippet"]["title"]
            if video_id:
                videos.append({
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })

        return videos
    except Exception as e:
        print(f"❌ Lỗi khi tìm video YouTube cho {query}: {e}")
        return []

def get_learning_resources(course):
    """
    📚 Gợi ý tài liệu PDF, bài tập online theo môn học.
    Bạn có thể mở rộng bằng cách đọc từ file JSON hoặc DB.
    """
    course = course.lower()
    if "cấu trúc dữ liệu" in course or "giải thuật" in course:
        return {
            "documents": [
                "https://drive.google.com/file/d/1abcXYZ/view",
                "https://viblo.asia/p/cau-truc-du-lieu-va-giai-thuat"
            ],
            "exercises": [
                "https://leetcode.com/problemset/all/",
                "https://www.hackerrank.com/domains/tutorials/10-days-of-algorithms"
            ]
        }
    elif "công nghệ web" in course:
        return {
            "documents": [
                "https://developer.mozilla.org/vi/docs/Learn",
                "https://www.w3schools.com/html/"
            ],
            "exercises": [
                "https://frontendmentor.io/challenges",
                "https://codepen.io/"
            ]
        }
    elif "an toàn" in course:
        return {
            "documents": [
                "https://www.coursera.org/learn/cybersecurity-basics",
                "https://owasp.org/"
            ],
            "exercises": [
                "https://tryhackme.com/",
                "https://www.root-me.org/"
            ]
        }
    else:
        return {"documents": [], "exercises": []}
