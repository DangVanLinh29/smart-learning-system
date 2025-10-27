from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

# Đọc danh sách sinh viên từ file CSV
students_df = pd.read_csv("data/students.csv")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = str(data.get('student_id'))

    # Tìm sinh viên trong danh sách
    student = students_df[students_df['MSV'].astype(str) == student_id]

    if len(student) == 0:
        return jsonify({"success": False, "message": "Không tìm thấy sinh viên!"})

    # Lấy tên sinh viên
    name = student.iloc[0]['Họ và tên']
    return jsonify({
        "success": True,
        "student": {
            "student_id": student_id,
            "name": name,
            "major": "Hệ thống thông tin"
        }
    })


# ✅ Endpoint dữ liệu tiến độ học tập (để Dashboard hoạt động)
subjects = [
    "Phân tích hệ thống thông tin",
    "Cơ sở dữ liệu",
    "Lập trình Python",
    "Khai phá dữ liệu",
    "Hệ quản trị CSDL nâng cao"
]

def generate_progress_data():
    """
    Tạo dữ liệu tiến độ học tập có tính tương quan giữa các môn.
    """
    records = []
    for _, row in students_df.iterrows():
        base = random.randint(50, 90)  # năng lực chung của sinh viên

        # Các môn có tương quan logic
        courses = {
            "Phân tích hệ thống thông tin": base + random.randint(-10, 10),
            "Cơ sở dữ liệu": base + random.randint(-15, 10),
            "Lập trình Python": base + random.randint(-10, 15),
            "Khai phá dữ liệu": base + random.randint(-5, 10),
            "Hệ quản trị CSDL nâng cao": base + random.randint(-10, 10),
        }

        for course, progress in courses.items():
            progress = max(40, min(100, progress))  # giới hạn 40–100
            records.append({
                "student_id": row["MSV"],
                "student_name": row["Họ và tên"],
                "course": course,
                "progress": progress
            })
    return pd.DataFrame(records)


df_progress = generate_progress_data()


@app.route('/api/progress/<student_id>', methods=['GET'])
def get_progress(student_id):
    # Lấy dữ liệu tiến độ của sinh viên theo mã số
    data = df_progress[df_progress["student_id"].astype(str) == student_id]

    if data.empty:
        return jsonify([])

    return jsonify(data.to_dict(orient="records"))


@app.route('/api/recommendation/<student_id>', methods=['GET'])
def get_recommendation(student_id):
    data = df_progress[df_progress["student_id"].astype(str) == student_id]
    low_courses = data[data["progress"] < 70]

    if low_courses.empty:
        return jsonify({
            "message": "🎉 Tất cả các môn đều đạt tốt! Bạn đang đi đúng hướng.",
            "recommendations": []
        })

    recommendations = []
    for _, row in low_courses.iterrows():
        course = row["course"]
        progress = row["progress"]
        roadmap = [
            f"Ôn lại kiến thức cơ bản trong môn {course}",
            f"Làm thêm bài tập và dự án nhỏ để củng cố kỹ năng",
            f"Tham khảo khóa học trực tuyến hoặc video hướng dẫn về {course}",
            f"Tương tác với giảng viên hoặc bạn bè để hỏi về phần chưa hiểu"
        ]
        recommendations.append({
            "course": course,
            "progress": progress,
            "roadmap": roadmap
        })

    return jsonify({
        "message": "⚡ Một số môn cần cải thiện để đạt thành tích tốt hơn.",
        "recommendations": recommendations
    })

@app.route('/api/insight', methods=['GET'])
def get_insight():
    """
    Phân tích tương quan giữa các môn học để gợi ý chiến lược học tập.
    """
    pivot = df_progress.pivot_table(index="student_id", columns="course", values="progress")
    corr = pivot.corr().round(2)

    # Lấy top 3 cặp môn có tương quan mạnh nhất
    corr_pairs = []
    for c1 in corr.columns:
        for c2 in corr.columns:
            if c1 != c2:
                corr_pairs.append((c1, c2, corr.loc[c1, c2]))

    corr_pairs = sorted(corr_pairs, key=lambda x: -abs(x[2]))[:5]

    insights = [
        f"📊 {a} ↔ {b}: tương quan {v*100:.1f}%. "
        + ("Học tốt môn này sẽ giúp cải thiện môn kia." if v > 0 else "Điểm yếu ở môn này có thể ảnh hưởng ngược lại.")
        for a, b, v in corr_pairs
    ]

    return jsonify({
        "message": "Phân tích mối tương quan giữa các môn học",
        "insights": insights
    })

@app.route('/api/predict/<student_id>', methods=['GET'])
def predict_future(student_id):
    """
    Mô phỏng dự báo tiến độ học tập dựa trên xu hướng hiện tại (Linear Regression).
    """
    data = df_progress[df_progress["student_id"] == int(student_id)]

    # giả định ta có 5 tuần dữ liệu trước (mô phỏng)
    future_preds = []
    for _, row in data.iterrows():
        # Sinh dữ liệu ngẫu nhiên quanh progress hiện tại để tạo trend
        past_scores = np.clip(
            np.random.normal(row["progress"], 5, size=5), 40, 100
        )
        X = np.arange(1, 6).reshape(-1, 1)
        model = LinearRegression().fit(X, past_scores)
        next_week = model.predict([[6]])[0]

        risk = max(0, min(100, 100 - next_week))  # điểm thấp → rủi ro cao
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

    return jsonify({
        "message": "Dự đoán tiến độ học tập tuần tới",
        "predictions": warnings
    })

@app.route('/')
def home():
    return jsonify({"message": "Smart Learning System Backend Ready 🚀"})


if __name__ == '__main__':
    app.run(debug=True)
