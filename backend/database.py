import sqlite3
from datetime import datetime
import json
import os

DB_NAME = 'smart_learning.db'

def init_db():
    """ Khởi tạo cơ sở dữ liệu và tạo các bảng nếu chưa tồn tại. """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Bảng Students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            student_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            major VARCHAR(100),
            gpa_current FLOAT DEFAULT 0.0,
            tlu_token VARCHAR(255),
            last_login DATETIME
        )
    """)
    
    # 2. Bảng Courses: ĐÃ SỬA course_code thành VARCHAR(150)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Courses (
            course_code VARCHAR(150) PRIMARY KEY, 
            course_name VARCHAR(150) NOT NULL,
            credits INTEGER DEFAULT 3,
            description TEXT
        )
    """)
    
    # 3. Bảng Grades_History: ĐÃ SỬA course_code thành VARCHAR(150)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Grades_History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id VARCHAR(10) NOT NULL,
            course_code VARCHAR(150) NOT NULL, 
            semester VARCHAR(20),
            final_mark FLOAT,
            progress_percent INTEGER,
            updated_at DATETIME,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_code) REFERENCES Courses(course_code),
            UNIQUE (student_id, course_code, semester)
        )
    """)
    
    # 4. Bảng Recommendation_Logs: ĐÃ SỬA related_course thành VARCHAR(150)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Recommendation_Logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id VARCHAR(10) NOT NULL,
            log_date DATETIME,
            type VARCHAR(50) NOT NULL,
            related_course VARCHAR(150), 
            details_json TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialization complete.")

# -------------------------------------------------------------
# CÁC HÀM HỖ TRỢ CHO BACKEND (HUY)
# -------------------------------------------------------------

def update_student_session(student_info, access_token):
    """
    Cập nhật/Thêm sinh viên vào DB sau khi đăng nhập thành công.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO Students 
        (student_id, name, major, tlu_token, last_login)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_info["student_id"],
        student_info["name"],
        student_info.get("major", "Hệ thống thông tin"), 
        access_token,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    conn.close()
    
def save_progress_history(student_id, progress_data):
    """
    Lưu dữ liệu tiến độ (progress_data) từ TLU API vào Grades_History.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for item in progress_data:
        course_name = item.get("course")
        progress = item.get("progress")
        
        # BƯỚC 1: Đảm bảo Course có trong bảng Courses (dùng tên môn làm mã giả)
        course_code = course_name 
        try:
            cursor.execute("INSERT OR IGNORE INTO Courses (course_code, course_name) VALUES (?, ?)", 
                           (course_code, course_name))
                           
            # BƯỚC 2: Lưu vào Grades_History
            cursor.execute("""
                INSERT OR REPLACE INTO Grades_History 
                (student_id, course_code, final_mark, progress_percent, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                student_id,
                course_code,
                progress / 10, 
                progress,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        except sqlite3.Error as e:
            print(f"LỖI CSDL KHI LƯU MÔN {course_name}: {e}")
            continue 
        
    conn.commit()
    conn.close()
    print(f"Saved/Updated {len(progress_data)} courses for student {student_id} to DB.")

# --- HẾT FILE database.py ---
