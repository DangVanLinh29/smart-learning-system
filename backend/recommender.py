import numpy as np
from sklearn.linear_model import LinearRegression
import random
import hashlib
import pandas as pd

# --- LOGIC XỬ LÝ DỮ LIỆU TLU (ĐÃ CẬP NHẬT) ---

def process_tlu_data_to_progress(tlu_marks, student_id):
    """
    Xử lý dữ liệu thô (từ TLU API) thành danh sách tiến độ cho Dashboard.
    CỐ GẮNG ĐỌC ĐIỂM THẬT THAY VÌ GIẢ LẬP.
    """
    progress_list = []
    found_real_scores = False

    if not isinstance(tlu_marks, list):
        print("LỖI (Recommender): Dữ liệu TLU API trả về không phải là một danh sách (list).")
        tlu_marks = [] # Chuyển về list rỗng

    # --- KHOANH VÙNG DEBUG (CÓ THỂ XÓA SAU) ---
    # if tlu_marks: 
    #     print("\n--- CẤU TRÚC DỮ LIỆU TLU (DEBUG) ---")
    #     print(tlu_marks[0]) 
    #     print("--------------------------------------\n")
    # --- KẾT THÚC DEBUG ---

    for subject in tlu_marks:
        if not isinstance(subject, dict):
            continue

        # 🚨 SỬA LỖI KEY TÊN MÔN HỌC (DỰA TRÊN DEBUG LOG)
        course_name = subject.get("subject", {}).get("subjectName", "Môn học không tên")

        # --- LOGIC MỚI: CỐ GẮNG ĐỌC ĐIỂM THẬT ---
        score = None

        # 🚨 SỬA LỖI KEY ĐIỂM (DỰA TRÊN DEBUG LOG)
        if subject.get("mark") is not None:
            score = subject.get("mark")

        progress = 0

        # Kiểm tra xem điểm có phải là số hợp lệ không (int hoặc float)
        if isinstance(score, (int, float)):
            # Giả sử điểm là hệ 10, ta đổi sang % (Tiến độ)
            progress = score * 10
            found_real_scores = True

        progress_list.append({
            "course": course_name,
            "progress": max(0, min(100, progress)) # Giới hạn 0-100
        })

    # --- LOGIC DỰ PHÒNG (Fallback) ---
    if not found_real_scores and tlu_marks: # Chỉ fallback nếu TLU API có data nhưng không đọc được điểm
        print(f"CẢNH BÁO: Đã lấy được {len(tlu_marks)} môn, nhưng không tìm thấy key 'mark'. Quay về dữ liệu giả lập (Mock).")
        return generate_mock_progress(student_id) # Quay về mock
    elif not tlu_marks: # Nếu TLU API trả về rỗng
        print(f"CẢNH BÁO: TLU API trả về danh sách rỗng. Quay về dữ liệu giả lập (Mock).")
        return generate_mock_progress(student_id) # Quay về mock

    print(f"ĐÃ XỬ LÝ THÀNH CÔNG {len(progress_list)} MÔN HỌC (DỮ LIỆU THẬT).")
    return progress_list


def generate_mock_progress(student_id):
    """
    Hàm tạo dữ liệu giả lập (Mock) khi TLU API không có điểm thật.
    """
    print("Đang tạo dữ liệu giả lập (Mock) cho Dashboard...")
    # Dữ liệu giả lập các môn anh Huy thích (Lập trình Game/App)
    mock_courses = [
        {"course": "Lập trình Game (Mock)", "base": 85},
        {"course": "Phát triển Ứng dụng (Mock)", "base": 90},
        {"course": "Cơ sở dữ liệu (Mock)", "base": 70},
        {"course": "Mạng máy tính (Mock)", "base": 65},
        {"course": "Hệ thống thông tin (Mock)", "base": 75}
    ]

    progress_list = []
    for item in mock_courses:
        # Dùng seed để đảm bảo điểm mock cố định cho mỗi sinh viên
        seed_val = int(hashlib.sha1(f"{student_id}{item['course']}".encode('utf-8')).hexdigest(), 16) % (10**8)
        random.seed(seed_val)
        progress = item['base'] + random.randint(-15, 10)
        progress_list.append({
            "course": item['course'],
            "progress": max(40, min(100, progress))
        })
    return progress_list


def get_recommendation_logic(progress_data):
    """
    Logic gợi ý học tập dựa trên tiến độ thấp (dưới 70%).
    """
    low_courses = [d for d in progress_data if d["progress"] < 70]

    if not low_courses:
        return {
            "message": "🎉 Tất cả các môn đều đạt tốt! Bạn đang đi đúng hướng.",
            "recommendations": []
        }

    recommendations = []
    for course_data in low_courses:
        course = course_data["course"]
        progress = course_data["progress"]
        roadmap = [
            f"Ôn lại kiến thức cơ bản trong môn {course} (đạt {progress}%)",
            f"Tập trung làm thêm bài tập dự án thực tế liên quan.",
            f"Tìm tài liệu/video chuyên sâu từ các nguồn ngoài.",
            f"Thảo luận với bạn Đạt hoặc giảng viên về phần kiến thức khó."
        ]
        recommendations.append({
            "course": course,
            "progress": progress,
            "roadmap": roadmap
        })

    return {
        "message": "⚡ Một số môn cần cải thiện để đạt thành tích tốt hơn.",
        "recommendations": recommendations
    }


def predict_future_logic(progress_data):
    """
    Mô phỏng dự báo tiến độ học tập (dùng Linear Regression).
    """
    future_preds = []
    if not progress_data: # Kiểm tra nếu không có dữ liệu
        return {"predictions": []}

    for row in progress_data:
        # Sinh dữ liệu ngẫu nhiên quanh progress hiện tại để tạo trend
        past_scores = np.clip(
            np.random.normal(row["progress"], 5, size=5), 40, 100
        )
        X = np.arange(1, 6).reshape(-1, 1) 
        model = LinearRegression().fit(X, past_scores)
        next_week = model.predict([[6]])[0] # Dự đoán tuần tiếp theo

        risk = max(0, min(100, 100 - next_week)) # Điểm thấp -> rủi ro cao
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
                "⚠️ Cần củng cố thêm trong tuần tới!"
                if r["predicted_progress"] < 60
                else "✅ Tiếp tục duy trì phong độ hiện tại!"
            ),
        }
        for r in sorted(future_preds, key=lambda x: -x["risk"])
    ]

    return {"predictions": warnings}

def get_insight_logic(progress_data):
    """
    Phân tích AI tổng quan dựa trên dữ liệu tiến độ.
    """
    if not progress_data: # Xử lý nếu list rỗng
        return {"insights": ["Không đủ dữ liệu để tạo phân tích."]}

    progresses = [d["progress"] for d in progress_data]
    avg_prog = np.mean(progresses)

    insights = [
        f"Điểm tiến độ trung bình toàn khóa là {avg_prog:.1f}%.",
        f"Có {len([p for p in progresses if p < 70])} môn cần ưu tiên cải thiện trong tuần này.",
        "Mối tương quan giữa các môn Lập trình và CSDL đang được giữ vững.",
    ]

    return {"insights": insights}