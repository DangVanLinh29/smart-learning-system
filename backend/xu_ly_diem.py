import pandas as pd
import getpass
import tlu_api # PHAI DAM BAO FILE NAY CO CAC HAM API
import json 
import sys 
import numpy as np # Thêm thư viện numpy để xử lý giá trị NaN/None tốt hơn

# ====================================================================
#              DANH SÁCH SINH VIÊN CẦN LẤY ĐIỂM
# ====================================================================
# Mã SV và Mật khẩu tương ứng (Dựa trên dữ liệu bạn cung cấp)
DANH_SACH_SINH_VIEN = [
    ("2251161965", "001204040865"),
    ("2251162102", "038303015570"),
    ("2251162101", "Nhu2803@"),
    ("2251162052", "Linh2004@"),
    ("2251162036", "036203009785"),
]

# ====================================================================

def export_marks_to_csv(all_marks_data, output_filename='tong_hop_diem_sinh_vien.csv'):
    """
    Chuyển dữ liệu điểm tổng hợp của nhiều sinh viên sang file CSV.
    (Đã sửa lỗi để làm phẳng các cột JSON lồng ghép và chỉ giữ lại cột cần thiết)
    """
    if not all_marks_data:
        print("WARNING: Không có dữ liệu điểm để tạo file CSV.")
        return False
        
    try:
        df = pd.DataFrame(all_marks_data)

        if df.empty:
             print("WARNING: DataFrame rỗng, không thể xuất CSV.")
             return False

        # --- BƯỚC 1: LÀM PHẲNG VÀ TRÍCH XUẤT DỮ LIỆU CẦN THIẾT TỪ JSON LỒNG GHÉP ---
        
        # 1a. Trích xuất subjectName và numberOfCredit từ cột 'subject'
        # Sử dụng errors='ignore' để xử lý trường hợp cột không tồn tại sau khi làm phẳng
        subject_info = df['subject'].apply(pd.Series).rename(columns={
            'subjectName': 'subjectName_flat', 
            'numberOfCredit': 'numberOfCredit_flat'
        })

        # 1b. Trích xuất semesterName từ cột 'semester'
        semester_info = df['semester'].apply(pd.Series).rename(columns={
            'semesterName': 'semesterName_flat'
        })
        
        # 1c. Hợp nhất các cột trích xuất vào DataFrame gốc và loại bỏ các cột JSON gốc
        df = pd.concat([df.drop(columns=['subject', 'semester', 'student', 'details'], errors='ignore'), subject_info, semester_info], axis=1)

        # -------------------------------------------------------------------------
        
        # 2. Định nghĩa Ánh xạ và Thứ tự cho các cột CẦN THIẾT
        # Chỉ giữ lại các cột quan trọng và đổi tên chúng sang tiếng Việt
        
        # Tên cột gốc trong API (key): Tên cột hiển thị (value)
        cols_map = {
            'studentId': 'Mã SV',
            'name': 'Tên SV', 
            'semesterName_flat': 'Học Kỳ', 
            'subjectName_flat': 'Tên Môn Học', 
            'numberOfCredit_flat': 'Số Tín Chỉ',
            'markQT': 'Điểm Quá Trình',      # Điểm Quá Trình
            'markTHI': 'Điểm Thi',         # Điểm Thi
            'mark': 'Điểm Tổng Kết (10)',  # Điểm tổng kết hệ 10
            'mark4': 'Điểm Hệ 4',          # Điểm tổng kết hệ 4
            'charMark': 'Điểm Chữ (A, B, C)',
            'examRound': 'Lần Thi',
            'markFormula': 'Công Thức Tính Điểm',
            'pass': 'Đạt/Trượt', # True/False
        }
        
        # 3. Lọc và Đổi tên cột
        
        # Chỉ lấy các cột có trong cols_map và có trong DataFrame hiện tại
        final_cols_data = {api_key: df[api_key] for api_key in cols_map.keys() if api_key in df.columns}
        df_final = pd.DataFrame(final_cols_data)
        
        # Đổi tên các cột
        df_final.rename(columns=cols_map, inplace=True)

        # 4. Xác định thứ tự cột cuối cùng (đảm bảo hiển thị đẹp và dễ đọc)
        priority_cols_order = [
            'Mã SV', 'Tên SV', 'Học Kỳ', 'Tên Môn Học', 'Số Tín Chỉ', 
            'Điểm Quá Trình', 'Điểm Thi', 'Điểm Tổng Kết (10)', 'Điểm Hệ 4', 
            'Điểm Chữ (A, B, C)', 'Đạt/Trượt', 'Lần Thi', 'Công Thức Tính Điểm'
        ]
        
        # Sắp xếp lại DataFrame theo thứ tự ưu tiên
        df_final = df_final[[col for col in priority_cols_order if col in df_final.columns]]

        # 5. Xuất ra file CSV (encoding='utf-8-sig' đảm bảo hiển thị tiếng Việt trong Excel)
        df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')

        print(f"\n✅ THÀNH CÔNG! Đã tổng hợp và xuất dữ liệu điểm sang file: {output_filename}")
        print(f"   Tổng cộng {len(df_final)} dòng điểm đã được lưu.")
        return True

    except Exception as e:
        print(f"❌ LỖI XUẤT CSV: {e}")
        return False

def process_multiple_students(student_list):
    """
    Vòng lặp qua danh sách sinh viên, đăng nhập và lấy điểm.
    """
    all_marks_combined = []

    for username, password in student_list:
        print(f"\n--- Bắt đầu xử lý cho sinh viên: {username} ---")
        
        # 1. Đăng nhập và lấy token
        auth_result = tlu_api.authenticate_tlu(username, password)

        if auth_result and auth_result.get("success"):
            access_token = auth_result["access_token"]
            student_name = auth_result.get("name", "N/A") 
            
            # 2. Gọi API lấy điểm tổng kết
            marks_data = tlu_api.fetch_student_marks(access_token)
            
            # 3. Thêm thông tin sinh viên vào từng mục điểm
            if marks_data:
                for mark in marks_data:
                    mark["studentId"] = username  # Thêm Mã SV
                    mark["name"] = student_name   # Thêm Tên SV
                    all_marks_combined.append(mark)
                print(f"OK: Đã thêm {len(marks_data)} điểm của {student_name} ({username}).")
            else:
                print(f"WARNING: Sinh viên {username} ({student_name}) không có dữ liệu điểm.")

        else:
            print(f"❌ THẤT BẠI: Không thể đăng nhập hoặc lấy token cho {username}. Bỏ qua.")
            
    return all_marks_combined

# --- PHẦN THỰC THI CHÍNH ---
if __name__ == "__main__":
    if not DANH_SACH_SINH_VIEN:
        print("LỖI: Biến DANH_SACH_SINH_VIEN trống. Vui lòng nhập Mã SV và Mật khẩu.")
        sys.exit()

    print("=== BẮT ĐẦU TỔNG HỢP ĐIỂM TỪ API TLU ===")

    # Thực hiện lấy điểm của tất cả sinh viên
    final_data = process_multiple_students(DANH_SACH_SINH_VIEN)
    
    # Xuất dữ liệu tổng hợp ra CSV
    export_marks_to_csv(final_data)
    
    print("\n=== CHƯƠNG TRÌNH KẾT THÚC ===")
