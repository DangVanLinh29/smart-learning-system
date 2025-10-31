from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import random

# IMPORT CÁC MODULE CỐT LÕI
from tlu_api import authenticate_tlu, fetch_student_marks 
from recommender import (
    process_tlu_data_to_progress, 
    get_recommendation_logic, 
    predict_future_logic,
    get_insight_logic
)
from database import update_student_session, save_progress_history, init_db # <--- THÊM init_db

app = Flask(__name__)
CORS(app)

# KHỞI TẠO CSDL NGAY KHI APP BẮT ĐẦU CHẠY ĐỂ ĐẢM BẢO CẤU TRÚC ĐÃ CÓ
init_db() 

# Lưu trữ phiên đăng nhập (token và info) tạm thời trong memory
user_sessions = {} 


@app.route('/api/login', methods=['POST'])
def login():
    """
    API đăng nhập. Nhận MSV và Mật khẩu từ frontend, xác thực với TLU API.
    """
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password') 
    
    if not student_id or not password:
        return jsonify({"success": False, "message": "Vui lòng cung cấp MSV và mật khẩu."}), 400

    # 1. XÁC THỰC VỚI API TLU
    auth_result = authenticate_tlu(student_id, password) 

    if auth_result and auth_result.get("success"):
        
        # Lấy thông tin cơ bản của sinh viên
        student_info = {
            "student_id": auth_result["student_id"],
            "name": auth_result["name"],
            "major": auth_result.get("major", "Hệ thống thông tin") 
        }
        
        # 2. LƯU PHIÊN ĐĂNG NHẬP VÀO CSDL VÀ CẬP NHẬT LAST_LOGIN
        update_student_session(student_info, auth_result["access_token"])
        
        # 3. LƯU PHIÊN TẠM THỜI TRONG MEMORY (Để lấy token nhanh)
        user_sessions[student_info["student_id"]] = {
            "access_token": auth_result["access_token"],
            "name": student_info["name"],
            "student_info": student_info
        }

        # 4. TRẢ VỀ THÔNG TIN SINH VIÊN
        return jsonify({
            "success": True,
            "student": student_info
        }), 200
    
    # TRẢ VỀ LỖI XÁC THỰC TỪ TLU API
    return jsonify({"success": False, "message": "Sai mã sinh viên hoặc mật khẩu."}), 401


# Trong file app.py, thay thế hàm get_progress_data hiện tại bằng code này:
def get_progress_data(student_id):
    """
    Hàm hỗ trợ lấy dữ liệu tiến độ thật từ TLU API, sau đó lưu vào CSDL.
    """
    session = user_sessions.get(student_id)
    if not session:
        return None, "Phiên đăng nhập hết hạn."

    try:
        # 1. LẤY DỮ LIỆU ĐIỂM TỔNG KẾT TỪ TLU API
        tlu_marks = fetch_student_marks(session["access_token"])
        
        if tlu_marks is None or not isinstance(tlu_marks, list):
            print("CẢNH BÁO: TLU API trả về dữ liệu rỗng hoặc không hợp lệ. Trả về None.")
            return None, "Không thể lấy dữ liệu điểm tổng kết từ TLU API."

        # 2. Xử lý dữ liệu thô thành định dạng tiến độ
        progress_data = process_tlu_data_to_progress(tlu_marks, student_id)
        
        # 3. LƯU TIẾN ĐỘ VÀO CSDL
        save_progress_history(student_id, progress_data)
        
        return progress_data, None
        
    except Exception as e:
        # BẮT LỖI TỔNG QUAN VÀ IN RA LOG ĐỂ DỄ DEBUG
        print(f"LỖI NGHIÊM TRỌNG TRONG get_progress_data cho SV {student_id}: {e}")
        import traceback
        traceback.print_exc()
        return None, "Lỗi xử lý dữ liệu nội bộ."


@app.route('/api/progress/<student_id>', methods=['GET'])
def get_progress(student_id):
    """ API lấy tiến độ học tập cho Dashboard """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500
        
    return jsonify(progress_data)


@app.route('/api/recommendation/<student_id>', methods=['GET'])
def get_recommendation(student_id):
    """ API lấy lộ trình gợi ý học tập (dùng logic recommender) """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500
        
    recommendations = get_recommendation_logic(progress_data)
    # TODO: Cần lưu recommendations vào Recommendation_Logs
    return jsonify(recommendations)


@app.route('/api/predict/<student_id>', methods=['GET'])
def predict_future(student_id):
    """ API Dự báo tiến độ học tập (dùng logic recommender) """
    progress_data, error = get_progress_data(student_id)
    if error:
        return jsonify({"message": error}), 500
        
    predictions = predict_future_logic(progress_data)
    # TODO: Cần lưu predictions vào Recommendation_Logs
    return jsonify(predictions)


@app.route('/api/insight', methods=['GET'])
def get_insight():
    """ API Phân tích AI tổng quan (dùng logic recommender) """
    # Lấy dữ liệu của sinh viên đầu tiên trong session để phân tích
    student_id = list(user_sessions.keys())[0] if user_sessions else None

    if not student_id:
        return jsonify({"insights": ["Chưa có sinh viên đăng nhập để phân tích."]})

    progress_data, error = get_progress_data(student_id)

    if error or not progress_data:
        return jsonify({"insights": ["Không đủ dữ liệu để phân tích tương quan."]})
        
    insights = get_insight_logic(progress_data)
    # TODO: Cần lưu insights vào Recommendation_Logs
    return jsonify(insights)


@app.route('/')
def home():
    """ Trang chủ / Kiểm tra trạng thái Backend """
    return jsonify({"message": "Smart Learning System Backend Ready (TLU Integrated) 🚀"})


if __name__ == '__main__':
    # Chạy ứng dụng Flask trên cổng 5000
    app.run(debug=False, port=5000)
