import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import random
import json
import sqlite3 
import time 
from io import StringIO

# IMPORT CÁC MODULE MỚI 
from tlu_api import (
    authenticate_tlu, 
    fetch_student_marks,
    fetch_current_semester_id, 
    fetch_student_schedule     
)
from recommender import (
    process_tlu_data_to_progress, 
    get_recommendation_logic, 
    predict_future_logic,
    get_insight_logic,
    process_schedule_to_courses,
    build_cf_model_data
)

app = Flask(__name__)
CORS(app)

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


# --- THIẾT LẬP CACHE (BỘ NHỚ ĐỆM) ---
DB_NAME = "tlu_cache.db"
CACHE_DURATION = 3600 # 1 giờ

def init_db():
    """ Khởi tạo CSDL SQLite (chạy 1 lần) """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_cache (
        student_id TEXT,
        data_type TEXT,
        json_data TEXT,
        timestamp REAL,
        PRIMARY KEY (student_id, data_type)
    )
    ''')
    conn.commit()
    conn.close()

    
def get_from_cache(student_id, data_type):
    """ Lấy dữ liệu từ cache (nếu có và chưa hết hạn) """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT json_data, timestamp 
        FROM api_cache 
        WHERE student_id = ? AND data_type = ?
    ''', (student_id, data_type))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        json_data, cache_timestamp = result
        
        if time.time() - cache_timestamp > CACHE_DURATION:
            print(f"CACHE EXPIRED: Du lieu {data_type} da het han. Goi lai API TLU.")
            return None
            
        print(f"CACHE HIT: Tra ve du lieu {data_type} cho {student_id} tu CSDL.")
        
        try:
            json_io = StringIO(json_data) 
            return pd.read_json(json_io, orient='records')
        except Exception as e:
            print(f"ERROR: Khong the doc/convert JSON tu cache CSDL: {e}")
            return None 
    
    print(f"CACHE MISS: Khong tim thay {data_type} cho {student_id} trong CSDL.")
    return None

def set_to_cache(student_id, data_type, data):
    """ Lưu dữ liệu vào cache CSDL """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if isinstance(data, pd.DataFrame):
             data_to_serialize = data
        elif isinstance(data, list) and all(isinstance(i, dict) for i in data):
             data_to_serialize = pd.DataFrame(data)
        else:
             print(f"ERROR: Du lieu {data_type} khong the luu vao cache (phai la list/DataFrame).")
             return

        json_data = data_to_serialize.to_json(orient='records') 
        
        cursor.execute(
            "INSERT OR REPLACE INTO api_cache (student_id, data_type, json_data, timestamp) VALUES (?, ?, ?, ?)",
            (student_id, data_type, json_data, time.time())
        )
        conn.commit()
        print(f"CACHE SET: Da luu du lieu {data_type} cho {student_id} vao CSDL.")
    except Exception as e:
        print(f"ERROR: Khong the luu vao cache. Ly do: {e}")
    finally:
        conn.close()
# --- KẾT THÚC THIẾT LẬP CACHE ---

# =========================================================
# NẠP VÀ HUẤN LUYỆN MÔ HÌNH AI KHI KHỞI ĐỘNG
# =========================================================
print("🚀 Đang nạp mô hình gợi ý AI (CF) từ 'tong_hop_diem_sinh_vien.csv'...")
cf_model_data = None
try:
    full_data = pd.read_csv("tong_hop_diem_sinh_vien.csv")
    cf_model_data = build_cf_model_data(full_data)
    
    if cf_model_data and cf_model_data[0] is not None:
        print(f"✅ Nạp mô hình AI (CF) thành công. Đã phân tích {len(cf_model_data[0])} sinh viên.")
    else:
        print("❌ LỖI: Không thể nạp mô hình AI (CF).")
        cf_model_data = None
        
except FileNotFoundError:
    print("❌ LỖI: Không tìm thấy tệp 'tong_hop_diem_sinh_vien.csv'.")
    cf_model_data = None
except Exception as e:
    print(f"❌ LỖI: Không thể nạp mô hình AI (CF) từ CSV. Lý do: {e}")
    cf_model_data = None
    
# =========================================================
# NẠP CƠ SỞ DỮ LIỆU HỌC LIỆU (JSON) - (Đã bị AI thay thế, nhưng cứ để đây)
# =========================================================
print("🚀 Đang nạp 'Cơ sở dữ liệu học liệu' từ 'learning_materials.json'...")
materials_db = {}
try:
    with open("learning_materials.json", "r", encoding="utf-8") as f:
        materials_db = json.load(f)
    print(f"✅ Nạp CSDL học liệu thành công. Đã tải {len(materials_db)} môn học.")
except FileNotFoundError:
    print("⚠️ CẢNH BÁO: Không tìm thấy tệp 'learning_materials.json'. Gợi ý thủ công sẽ bị TẮT.")
except Exception as e:
    print(f"❌ LỖI: Không thể nạp 'learning_materials.json'. Lý do: {e}")
# =========================================================

# Lưu trữ phiên đăng nhập (token và info) tạm thời
user_sessions = {} 

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Yeu cau khong co JSON body."}), 400
            
        student_id = data.get('student_id')
        password = data.get('password') 
        
        if not student_id or not password: 
            return jsonify({"success": False, "message": "Vui long cung cap MSV va mat khau."}), 400

        auth_result = authenticate_tlu(student_id, password) 

        if auth_result and auth_result.get("success"):
            user_sessions[student_id] = {
                "access_token": auth_result["access_token"],
                "name": auth_result["name"],
                "student_info": auth_result
            }
            
            return jsonify({
                "success": True,
                "student": {
                    "student_id": auth_result["student_id"],
                    "name": auth_result["name"],
                    "major": auth_result["major"]
                }
            }), 200
        
        return jsonify({"success": False, "message": "Sai ma sinh vien hoac mat khau."}), 401
    
    except Exception as e:
        print(f"LOI CRITICAL TAI API LOGIN: {e}")
        return jsonify({"success": False, "message": "Loi server khi dang nhap."}), 500


def get_ALL_marks_data(student_id): 
    """ 
    Hàm hỗ trợ: Lấy dữ liệu ĐIỂM TỔNG KẾT (Tất cả các môn đã học).
    """
    cached_data = get_from_cache(student_id, "marks")
    if cached_data is not None:
        return cached_data, None 

    session = user_sessions.get(student_id)
    if not session or "access_token" not in session:
        return None, "Phien dang nhap het han."

    access_token = session.get("access_token")
    
    tlu_marks = fetch_student_marks(access_token)
    
    if tlu_marks is None: 
        return None, "Khong the lay du lieu diem tong ket tu TLU API."
    
    progress_data = process_tlu_data_to_progress(tlu_marks, student_id)
    
    set_to_cache(student_id, "marks", progress_data)

    return progress_data, None


@app.route('/api/progress/<student_id>', methods=['GET'])
def get_progress(student_id):
    """ 
    API lấy tiến độ học tập (dùng cho Dashboard).
    """
    progress_data, error = get_ALL_marks_data(student_id) 
    if error:
        return jsonify({"message": error}), 500
        
    return jsonify(progress_data.to_dict(orient='records'))


@app.route('/api/recommendation/<student_id>', methods=['GET'])
def get_recommendation(student_id):
    """ 
    API Gợi ý, sử dụng Cả 3 nguồn: TLU API, CF (CSV), và Gemini AI
    """
    progress_data, error = get_ALL_marks_data(student_id) 
    if error:
        return jsonify({"message": error}), 500
    
    try:
        student_id_int = int(student_id)
    except ValueError:
        student_id_int = None
        print(f"Warning: student_id {student_id} không phải là số, không thể dùng mô hình CF.")

    recommendations = get_recommendation_logic(
        progress_data,
        student_id_int, 
        cf_model_data,
        materials_db # materials_db này có thể bị bỏ qua nếu logic dùng AI
    )
    
    return jsonify(recommendations)

# =========================================================
# ‼️ SỬA LỖI LOGIC: API /api/insight PHẢI LẤY ĐÚNG student_id
# =========================================================
@app.route('/api/insight/<student_id>', methods=['GET'])
def get_insight(student_id): # <-- Thêm (student_id)
    """ 
    API Phân tích AI tổng quan (dùng cho Dashboard).
    Sử dụng API Điểm tổng kết (của sinh viên đang xem).
    """
    # ‼️ XÓA BỎ LOGIC CŨ (lấy sinh viên đầu tiên)
    # student_id = list(user_sessions.keys())[0] if user_sessions else None
    
    if not student_id:
           return jsonify({"insights": ["Không tìm thấy mã sinh viên để phân tích."]})

    # Hàm get_ALL_marks_data sẽ lấy điểm của đúng sinh viên này
    progress_data, error = get_ALL_marks_data(student_id) 

    if error or progress_data.empty:
        return jsonify({"insights": ["Không đủ dữ liệu để phân tích."]})
        
    # (Hàm get_insight_logic đã được sửa ở lần trước)
    insights = get_insight_logic(progress_data)
    return jsonify(insights)


@app.route('/api/predict/<student_id>', methods=['GET'])
def predict_future(student_id):
    """ API Dự báo tiến độ học tập (MÔ PHỎNG) """
    progress_list, error = get_ALL_marks_data(student_id)
    if error:
        return jsonify({"message": error}), 500
        
    try:
        progress_data = pd.DataFrame(progress_list)
    except Exception as e:
        return jsonify({"message": f"Loi khi tao DataFrame tu tien do: {e}"}), 500

    predictions = predict_future_logic(progress_data) 
    return jsonify(predictions)


# --- API CHO TRANG "CÁC MÔN ĐANG HỌC" ---

@app.route('/api/current-schedule/<student_id>', methods=['GET'])
def get_current_schedule(student_id):
    """
    API lấy các môn ĐANG HỌC (cho trang SchedulePage.js)
    """
    cached_data = get_from_cache(student_id, "schedule")
    if cached_data is not None:
        return jsonify(cached_data.to_dict(orient='records')) 

    session = user_sessions.get(student_id)
    if not session or "access_token" not in session:
        return jsonify({"error": "Phien dang nhap het han."}), 401

    access_token = session.get("access_token")

    current_semester_id = fetch_current_semester_id(access_token)
    if not current_semester_id:
        return jsonify({"error": "Khong the lay du lieu hoc ky hien tai."}), 500

    schedule_data = fetch_student_schedule(access_token, current_semester_id)
    
    if schedule_data is None: 
        return jsonify({"error": "Khong the lay du lieu lich hoc."}), 500
    
    processed_schedule = process_schedule_to_courses(schedule_data, student_id)
    
    set_to_cache(student_id, "schedule", processed_schedule)
    
    return jsonify(processed_schedule.to_dict(orient='records'))


@app.route('/')
def home():
    return jsonify({"message": "Smart Learning System Backend Ready (TLU Integrated) 🚀"})

if __name__ == '__main__':
    init_db() 
    app.run(debug=True, port=5000)