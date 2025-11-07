import requests
import urllib3
import pandas as pd
import getpass # Thư viện để nhập mật khẩu an toàn
import sys
# Fix lỗi encoding khi in ra console
sys.stdout.reconfigure(encoding='utf-8')

# Tắt cảnh báo về chứng chỉ bảo mật (InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_tlu(username, password):
    """
    Lấy Access Token từ API TLU.
    Trả về token (string) nếu thành công hoặc None nếu thất bại.
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
        print(f"❌ LỖI TLU API (Xác thực): {e.response.status_code}. Chi tiết: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ LỖI KHÔNG XÁC ĐỊNH (Auth): {e}")
        return None

def fetch_current_semester_id(access_token):
    """
    GỌI API 'semester_info' ĐỂ LẤY ID HỌC KỲ HIỆN TẠI.
    Trả về ID học kỳ (string) hoặc None.
    """
    semester_info_url = "https://sinhvien1.tlu.edu.vn/education/api/semester/semester_info"
    
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(semester_info_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        current_semester_id = None
        
        if isinstance(data, list) and len(data) > 0:
            current_semester_id = data[0].get('id') 
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

def fetch_student_data(access_token):
    """
    Lấy thông tin cá nhân của sinh viên từ TLU API.
    Trả về dict chứa user info hoặc None.
    """
    url = "https://sinhvien1.tlu.edu.vn/education/api/users/getCurrentUser"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        print("✅ Lấy thông tin cá nhân sinh viên thành công.")
        return {
            "student_id": data.get('username', 'N/A'),
            "name": data.get('displayName', 'N/A'),
            "email": data.get('email', 'N/A'), # Thêm trường email (nếu API TLU cung cấp)
            "major": "Hệ thống thông tin" # Giả định theo thông tin chung
        }
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI TLU API (User Data): {e}")
        return None

def fetch_student_marks(access_token):
    """
    Lấy TOÀN BỘ ĐIỂM TỔNG KẾT (TẤT CẢ HỌC KỲ).
    Trả về danh sách list of dicts hoặc None.
    """
    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/getListMarkDetailStudent" # API DIEM TONG KET
    
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()

        if not data:
             print("⚠️ CẢNH BÁO: TLU API (StudentMark) trả về danh sách điểm rỗng.")
        else:
            print(f"✅ Lấy thành công {len(data)} điểm tổng kết từ TLU API.")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI TLU API (StudentMark): {e}")
        return None
    
def fetch_schedule(access_token, semester_id): 
    """
    Lấy dữ liệu lịch học (các môn đang học) từ API TLU.
    """
    schedule_url = f"https://sinhvien1.tlu.edu.vn/education/api/StudentCourseSubject/studentLoginUser/{semester_id}"
    print(f"... Đang gọi API lịch học: {schedule_url}")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(schedule_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ LỖI TLU API (Lịch học): {e}")
        return None
