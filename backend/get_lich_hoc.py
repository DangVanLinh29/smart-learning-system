import requests
import urllib3
import pandas as pd
import getpass # Thư viện để nhập mật khẩu an toàn

# Tắt cảnh báo về chứng chỉ bảo mật (InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_tlu(username, password):
    """
    Lấy Access Token từ API TLU.
    Trả về token hoặc None nếu thất bại.
    """
    token_url = "https://sinhvien1.tlu.edu.vn/education/oauth/token"
    credentials = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "education_client",
        "client_secret": "password"
    }
    
    try:
        token_response = requests.post(token_url, data=credentials, verify=False)
        token_response.raise_for_status() # Báo lỗi nếu (4xx, 5xx)
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if access_token:
            print("✅ Đăng nhập TLU và lấy token thành công!")
            return access_token
        else:
            print("❌ Lỗi: Không tìm thấy access_token trong phản hồi.")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ LỖI TLU API (Xác thực): {e.response.status_code}")
        print(f"   Chi tiết: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ LỖI KHÔNG XÁC ĐỊNH (Auth): {e}")
        return None

# --- HÀM MỚI ---
def fetch_current_semester_id(access_token):
    """
    GỌI API 'semester_info' ĐỂ LẤY ID HỌC KỲ HIỆN TẠI.
    """
    # 🚨 ANH HUY VUI LÒNG DÙNG F12 TÌM URL CỦA API "semester_info" VÀ DÁN VÀO ĐÂY
    # (Nó có thể là .../api/semester/semester_info hoặc tương tự)
    semester_info_url = "https://sinhvien1.tlu.edu.vn/education/api/semester/semester_info" # ĐOÁN URL, ANH HÃY KIỂM TRA LẠI
    
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(semester_info_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        current_semester_id = None
        
        # API TLU thường trả về 1 list (danh sách)
        if isinstance(data, list) and len(data) > 0:
            # Ta giả định học kỳ hiện tại là phần tử đầu tiên
            current_semester_id = data[0].get('id') 
        # Hoặc đôi khi nó trả về 1 object (đối tượng)
        elif isinstance(data, dict):
            current_semester_id = data.get('id')
            
        if current_semester_id:
            print(f"✅ Lấy thành công ID học kỳ hiện tại: {current_semester_id}")
            return current_semester_id
        else:
            print("❌ Lỗi: Không thể phân tích ID học kỳ từ 'semester_info'.")
            return None
            
    except Exception as e:
        print(f"❌ LỖI TLU API (Semester Info): {e}")
        return None

# --- HÀM ĐÃ SỬA ---
def fetch_schedule(access_token, semester_id): # Thêm tham số semester_id
    """
    Lấy dữ liệu lịch học (các môn đang học) từ API TLU.
    """
    
    # 🚨 SỬ DỤNG ID HỌC KỲ ĐỘNG (Dynamic)
    schedule_url = f"https://sinhvien1.tlu.edu.vn/education/api/StudentCourseSubject/studentLoginUser/{semester_id}"
    print(f"... Đang gọi API lịch học: {schedule_url}")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(schedule_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Lấy thành công dữ liệu lịch học (Tìm thấy {len(data)} mục).")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI TLU API (Lịch học): {e}")
        return None

# --- ĐÂY LÀ PHẦN CODE ĐẦY ĐỦ ANH CẦN (ĐÃ SỬA) ---
def process_and_export_csv(schedule_data):
    """
    Xử lý JSON lịch học, lấy Mã Môn, Tên Môn, Giảng Viên (DUY NHẤT) và xuất CSV.
    """
    print("... Bắt đầu xử lý dữ liệu (lấy Tên môn, Mã môn, Giảng viên)...")
    
    # Dùng (set) để tự động loại bỏ các môn trùng lặp
    processed_subjects = set() 

    if not isinstance(schedule_data, list):
        print("❌ Lỗi: Dữ liệu lịch học trả về không phải là một danh sách.")
        return

    for subject in schedule_data:
        try:
            # Bỏ qua nếu TLU API trả về một môn học rỗng (None)
            if subject is None:
                continue 
            
            # Lấy Tên Môn và Mã Môn (Đã fix)
            subject_details = subject.get("courseSubject", {}).get("semesterSubject", {}).get("subject", {})
            if subject_details is None:
                subject_details = {} 

            subject_name = subject_details.get("subjectName", "N/A")
            subject_code = subject_details.get("subjectCode", "N/A")
            
            # --- SỬA LỖI LẤY TÊN GIÁO VIÊN ---
            # Tên GV nằm lồng bên trong "courseSubject" -> "teacher" -> "displayName"
            teacher_details = subject.get("courseSubject", {}).get("teacher", {})
            if teacher_details is None: # Xử lý trường hợp teacher: null
                teacher_details = {}
            teacher_name = teacher_details.get("displayName", "N/A")
            # --- HẾT SỬA LỖI ---
            
            # Chỉ thêm vào danh sách nếu có Mã môn và Tên môn hợp lệ
            if subject_name != "N/A" and subject_code != "N/A":
                processed_subjects.add((subject_code, subject_name, teacher_name))
                
        except Exception as e:
            print(f"Lỗi khi xử lý một mục: {e}")

    # Sử dụng Pandas để xuất CSV
    if not processed_subjects:
        print("Không có dữ liệu môn học để xuất.")
        return

    # Chuyển (set) thành (list) để tạo DataFrame
    df = pd.DataFrame(list(processed_subjects), columns=["MaMon", "TenMon", "GiangVien"]) # Thêm cột GiangVien
    
    # Sắp xếp theo Tên Môn (Alphabet)
    df_sorted = df.sort_values(by="TenMon")
    
    output_filename = "danh_sach_mon_hoc_va_giang_vien.csv" # Đổi tên file cho đúng
    # Dùng encoding='utf-8-sig' để Excel đọc được Tiếng Việt có dấu
    df_sorted.to_csv(output_filename, index=False, encoding='utf-8-sig') 
    
    print(f"🎉 HOÀN TẤT! Đã xuất danh sách môn học (và GV) ra file: {output_filename}")


# --- HÀM CHẠY CHÍNH (ĐÃ CẬP NHẬT) ---
if __name__ == "__main__":
    # 1. Nhập thông tin
    student_id = input("Nhập Mã sinh viên TLU: ")
    password = getpass.getpass("Nhập Mật khẩu TLU (sẽ bị ẩn): ") # Nhập mật khẩu an toàn

    # 2. Lấy Token
    token = authenticate_tlu(student_id, password)
    
    if token:
        # 3. LẤY ID HỌC KỲ HIỆN TẠI (MỚI)
        current_semester_id = fetch_current_semester_id(token)
        
        if current_semester_id:
            # 4. Lấy Lịch học (dựa trên ID vừa lấy)
            schedule_data = fetch_schedule(token, current_semester_id)
            
            if schedule_data:
                # 5. Xử lý và Xuất CSV
                process_and_export_csv(schedule_data)

