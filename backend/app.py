import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import random

# IMPORT CÁC MODULE MỚI (Đã sửa tên hàm)
from tlu_api import authenticate_tlu, fetch_student_marks # 🚨 SỬA LỖI IMPORT Ở ĐÂY
from recommender import (
    process_tlu_data_to_progress, 
    get_recommendation_logic, 
    predict_future_logic,
    get_insight_logic
)

app = Flask(__name__)
CORS(app)

user_sessions = {} # Key: student_id, Value: {access_token, student_name, student_info}

# ==============================
# Static upload (avatar)
# ==============================
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload_avatar", methods=["POST"])
def upload_avatar():
    if "file" not in request.files or "student_id" not in request.form:
        return jsonify({"success": False, "message": "Thiếu file hoặc mã sinh viên!"}), 400

    file = request.files["file"]
    student_id = request.form["student_id"]

    if file.filename == "":
        return jsonify({"success": False, "message": "Chưa chọn file!"}), 400
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Định dạng file không hợp lệ!"}), 400

    filename = secure_filename(f"{student_id}.jpg")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    avatar_url = f"http://127.0.0.1:5000/static/uploads/{filename}"
    return jsonify({"success": True, "url": avatar_url})

# Lưu trữ phiên đăng nhập (token và info) tạm thời
user_sessions = {} # Key: student_id, Value: {access_token, student_name, student_info}

# ==============================
# Auth (login theo MSSV)
# ==============================
@app.route('/api/login', methods=['POST'])
def login():
    """
    API đăng nhập. Nhận MSV và Mật khẩu từ frontend.
    """
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')  # <-- 1. LẤY THÊM MẬT KHẨU

    if not student_id or not password:  # <-- 2. KIỂM TRA CẢ HAI
        return jsonify({"success": False, "message": "Vui lòng cung cấp MSV và mật khẩu."}), 400

    # 3. XÁC THỰC VỚI API TLU (Dùng cả 2 tham số)
    auth_result = authenticate_tlu(student_id, password)

    if auth_result and auth_result.get("success"):
        # 4. LƯU PHIÊN ĐĂNG NHẬP
        user_sessions[student_id] = {
            "access_token": auth_result["access_token"],
            "name": auth_result["name"],
            "student_info": auth_result
        }
        # 5. TRẢ VỀ THÔNG TIN SINH VIÊN
        return jsonify({
            "success": True,
            "student": {
                "student_id": auth_result["student_id"],
                "name": auth_result["name"],
                "major": auth_result["major"]
            }
        }), 200
    
    # 6. SỬA LẠI THÔNG BÁO LỖI
    return jsonify({"success": False, "message": "Sai mã sinh viên hoặc mật khẩu."}), 401


def get_progress_data(student_id):
    """ Hàm hỗ trợ lấy dữ liệu tiến độ thật từ TLU API """
    session = user_sessions.get(student_id)
    if not session:
        return None, "Phiên đăng nhập hết hạn."

    # 1. LẤY DỮ LIỆU ĐIỂM TỔNG KẾT
    tlu_marks = fetch_student_marks(session["access_token"]) # 🚨 SỬA LỖI TÊN HÀM Ở ĐÂY
    
    if tlu_marks is None: # Lỗi API
        return None, "Không thể lấy dữ liệu điểm tổng kết từ TLU API."

    # 2. Xử lý dữ liệu thô thành định dạng tiến độ
    progress_data = process_tlu_data_to_progress(tlu_marks, student_id)
    return progress_data, None


@app.route('/api/progress/<student_id>', methods=['GET'])
def get_progress(student_id):
    """ API lấy tiến độ học tập cho Dashboard """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500
    return jsonify(progress_data)


@app.route('/api/recommendation/<student_id>', methods=['GET'])
def get_recommendation(student_id):
    """ API lấy lộ trình gợi ý học tập """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500
    
    recommendations = get_recommendation_logic(progress_data)
    return jsonify(recommendations)


@app.route('/api/insight', methods=['GET'])
def get_insight():
    """ API Phân tích AI tổng quan """
    # Lấy dữ liệu của sinh viên đầu tiên trong session để phân tích
    student_id = list(user_sessions.keys())[0] if user_sessions else None
    if not student_id:
         return jsonify({"insights": ["Chưa có sinh viên đăng nhập để phân tích."]})

    progress_data, error = get_progress_data(student_id)

    if error or not progress_data:
        return jsonify({"insights": ["Không đủ dữ liệu để phân tích tương quan."]})

    insights = get_insight_logic(progress_data)
    return jsonify(insights)

# ==============================
# API dự báo: dựa trên score10 (trả cả score10 & progress %)
# ==============================
@app.route('/api/predict/<student_id>', methods=['GET'])
def predict_future(student_id):
    """ API Dự báo tiến độ học tập """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500

    predictions = predict_future_logic(progress_data)
    return jsonify(predictions)

@app.route('/')
def home():
    return jsonify({"message": "Smart Learning System Backend Ready (TLU Integrated) 🚀"})

if __name__ == '__main__':
    app.run(debug=False, port=5000)
