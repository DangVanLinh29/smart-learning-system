import sqlite3
import os
import json
import getpass
from datetime import datetime
import sys
# Fix lỗi encoding khi in ra console
sys.stdout.reconfigure(encoding='utf-8')

# 🚨 IMPORT CÁC HÀM API TỪ FILE TLU API HANDLER (ĐÃ CÓ Ở CỬA SỔ BÊN PHẢI)
from tlu_api_handler import (
    authenticate_tlu,
    fetch_student_data,
    fetch_student_marks
)

DATABASE_NAME = 'smart_learning.db'

# --- 1. HÀM QUẢN LÝ CƠ SỞ DỮ LIỆU ---

def create_connection(db_file):
    """Tạo kết nối CSDL và bật khóa ngoại."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return None

def create_tables(conn):
    """Tạo tất cả các bảng cần thiết."""
    cursor = conn.cursor()
    
    # 1. Bảng STUDENTS (Sinh viên)
    sql_create_students_table = """
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        date_of_birth TEXT,
        major TEXT
    );
    """

    # 2. Bảng SUBJECTS (Môn học)
    sql_create_subjects_table = """
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id TEXT PRIMARY KEY,
        subject_name TEXT NOT NULL,
        credits INTEGER NOT NULL,
        description TEXT
    );
    """
    
    # 3. Bảng GRADES (Điểm số) - Liên kết Sinh viên và Môn học
    sql_create_grades_table = """
    CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        subject_id TEXT NOT NULL,
        semester TEXT NOT NULL,
        score REAL,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects (subject_id) ON DELETE CASCADE,
        UNIQUE (student_id, subject_id, semester)
    );
    """
    
    # 4. Bảng LOG_HISTORY (Nhật ký thay đổi/hành động)
    sql_create_log_history_table = """
    CREATE TABLE IF NOT EXISTS log_history (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        details TEXT,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE SET NULL
    );
    """
    
    # 5. Bảng CHATBOT_LOGS (Nhật ký Chatbot)
    sql_create_chatbot_logs_table = """
    CREATE TABLE IF NOT EXISTS chatbot_logs (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        timestamp TEXT NOT NULL,
        user_query TEXT NOT NULL,
        chatbot_response TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE SET NULL
    );
    """

    try:
        cursor.execute(sql_create_students_table)
        cursor.execute(sql_create_subjects_table)
        cursor.execute(sql_create_grades_table)
        cursor.execute(sql_create_log_history_table)
        cursor.execute(sql_create_chatbot_logs_table)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Lỗi khi tạo bảng: {e}")

# --- 2. HÀM ĐỒNG BỘ DỮ LIỆU ---

def sync_student_data(conn, student_info):
    """Lưu thông tin cá nhân sinh viên vào bảng students."""
    cursor = conn.cursor()
    student_id = student_info.get('student_id')
    
    if student_id == 'N/A':
        return 0

    full_name = student_info.get('name', 'N/A')
    email = student_info.get('email')
    major = student_info.get('major', 'N/A')
    
    # Xử lý nếu email không có, tạo email giả định để tránh lỗi UNIQUE
    if email == 'N/A' or not email:
        email = f"{student_id}@tlu.edu.vn" 

    try:
        # INSERT OR REPLACE: Chèn hoặc thay thế nếu student_id đã tồn tại
        cursor.execute("""
            INSERT OR REPLACE INTO students (student_id, full_name, email, date_of_birth, major)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, full_name, email, None, major))
        conn.commit()
        print(f"✅ Lưu thông tin sinh viên {student_id} thành công.")
        return 1
    except sqlite3.Error as e:
        print(f"❌ Lỗi lưu thông tin sinh viên: {e}")
        return 0

def sync_marks_and_subjects(conn, student_id, access_token):
    """Lấy điểm số và cập nhật bảng subjects/grades."""
    marks_data = fetch_student_marks(access_token)
    
    if not marks_data:
        print("⚠️ Không có dữ liệu điểm số để đồng bộ.")
        return

    cursor = conn.cursor()
    count = 0
    
    # Duyệt qua từng môn học đã có điểm
    for subject in marks_data:
        try:
            # 1. TRÍCH XUẤT THÔNG TIN MÔN HỌC
            subject_details = subject.get("subject", {})
            subject_id = subject_details.get("subjectCode", "N/A") 
            subject_name = subject_details.get("subjectName", "N/A")
            credits = subject_details.get("credit", 0)
            
            # 2. TRÍCH XUẤT ĐIỂM VÀ HỌC KỲ
            score = subject.get("mark") # Điểm cuối cùng
            semester = subject.get("semesterName", "N/A")

            if subject_id == 'N/A' or score is None:
                continue

            # --- INSERT/UPDATE SUBJECTS ---
            # INSERT OR IGNORE: Chỉ chèn nếu subject_id chưa tồn tại
            cursor.execute("""
                INSERT OR IGNORE INTO subjects (subject_id, subject_name, credits)
                VALUES (?, ?, ?)
            """, (subject_id, subject_name, credits))

            # --- INSERT/UPDATE GRADES ---
            # INSERT OR REPLACE: Thay thế điểm nếu đã tồn tại cho SV/Môn/Kỳ này
            cursor.execute("""
                INSERT OR REPLACE INTO grades (student_id, subject_id, semester, score)
                VALUES (?, ?, ?, ?)
            """, (student_id, subject_id, semester, score))
            count += 1
            
        except sqlite3.Error as e:
            subject_name_log = subject.get("subject", {}).get("subjectName", "Unknown Subject")
            print(f"❌ Lỗi đồng bộ điểm cho {subject_name_log}: {e}")

    conn.commit()
    print(f"✅ Đồng bộ thành công {count} mục điểm số và môn học.")

def sync_logs(conn, student_id, log_type, data):
    """Lưu log đồng bộ vào bảng log_history."""
    cursor = conn.cursor()
    action = f"API_Sync_{log_type}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Lưu trữ toàn bộ dữ liệu (JSON.dumps) để debugging sau này
        cursor.execute("""
            INSERT INTO log_history (student_id, action, timestamp, details) 
            VALUES (?, ?, ?, ?)
        """, (student_id, action, timestamp, json.dumps(data, ensure_ascii=False)))
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ Lỗi lưu log: {e}")

# --- KHỐI CHẠY CHÍNH ---

def initial_setup_and_sync(username, password):
    """Quy trình chính: Tạo CSDL, Đăng nhập API và Đồng bộ."""
    
    # 0. TẠO HOẶC KẾT NỐI CSDL
    conn = create_connection(DATABASE_NAME)
    if conn is None:
        return
    
    # Đảm bảo các bảng tồn tại trước khi đồng bộ
    create_tables(conn)
    print(f"✅ CSDL '{DATABASE_NAME}' và các bảng đã sẵn sàng.")

    print("\n--- BẮT ĐẦU QUÁ TRÌNH ĐỒNG BỘ DỮ LIỆU THẬT TLU ---")
    
    # 1. AUTHENTICATE VÀ LẤY TOKEN
    access_token = authenticate_tlu(username, password)
    if not access_token:
        conn.close()
        return

    # 2. LẤY THÔNG TIN CÁ NHÂN (để lấy student_id)
    student_info = fetch_student_data(access_token)
    if not student_info or student_info.get('student_id') == 'N/A':
        print("❌ Lỗi: Không lấy được thông tin người dùng (student_id). Dừng đồng bộ.")
        conn.close()
        return

    student_id = student_info['student_id']

    # 3. LƯU THÔNG TIN SINH VIÊN VÀO BẢNG STUDENTS
    sync_student_data(conn, student_info)
    
    # 4. LƯU ĐIỂM VÀ MÔN HỌC VÀO BẢNG SUBJECTS VÀ GRADES
    sync_marks_and_subjects(conn, student_id, access_token)

    # 5. GHI LẠI LOG ĐỒNG BỘ
    sync_logs(conn, student_id, "SUCCESS", student_info)

    conn.close()
    print("\n--- ĐỒNG BỘ KẾT THÚC THÀNH CÔNG ---")

if __name__ == '__main__':
    # YÊU CẦU NGƯỜI DÙNG NHẬP THÔNG TIN
    STUDENT_ID = input("Nhập Mã Sinh Viên TLU: ")
    PASSWORD = getpass.getpass("Nhập Mật khẩu TLU (sẽ bị ẩn): ")
    
    # Chạy quy trình đồng bộ hóa
    initial_setup_and_sync(STUDENT_ID, PASSWORD)
