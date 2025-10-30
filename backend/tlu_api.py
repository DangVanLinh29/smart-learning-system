import requests
import urllib3
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Tắt cảnh báo về chứng chỉ bảo mật (InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KHU VỰC CÁC HÀM XỬ LÝ API TLU ---

def authenticate_tlu(username, password): 
    """
    Lấy Access Token, xác thực, và lấy thông tin cơ bản của sinh viên.
    SỬ DỤNG MẬT KHẨU ĐƯỢC GỬI TỪ FRONTEND.
    """
    token_url = "https://sinhvien1.tlu.edu.vn/education/oauth/token"

    credentials = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "education_client",
        "client_secret": "password"
    }
    access_token = None

    try:
        # 1. LẤY TOKEN
        token_response = requests.post(token_url, data=credentials, verify=False)
        token_response.raise_for_status() 
        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return None

        # 2. LẤY THÔNG TIN NGƯỜI DÙNG BẰNG TOKEN
        user_info = fetch_student_data(access_token)

        if user_info:
            # Trả về token và thông tin user
            return {
                **user_info,
                "access_token": access_token,
                "success": True
            }
        return None 

    except requests.exceptions.HTTPError as e:
        print(f"LỖI TLU API (Xác thực): {e.response.status_code}")
        print(f"Response Error: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"LỖI TLU API (Kết nối): {e}")
        return None
    except Exception as e:
        print(f"LỖI KHÔNG XÁC ĐỊNH: {e}")
        return None


def fetch_student_data(access_token):
    """
    Lấy thông tin cá nhân của sinh viên từ TLU API.
    """
    url = "https://sinhvien1.tlu.edu.vn/education/api/users/getCurrentUser"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return {
            "student_id": data.get('username', 'N/A'),
            "name": data.get('displayName', 'N/A'),
            "major": "Hệ thống thông tin" # Giả định theo thông tin của anh
        }
    except requests.exceptions.RequestException as e:
        print(f"LỖI TLU API (User Data): {e}")
        return None


def fetch_student_marks(access_token):
    """
    LẤY TOÀN BỘ ĐIỂM TỔNG KẾT (TẤT CẢ HỌC KỲ)
    """
    # 🚨 SỬA LẠI URL: Dùng API đúng (getListMarkDetailStudent)
    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/getListMarkDetailStudent" 
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()

        if not data:
             print("CẢNH BÁO: TLU API (StudentMark) trả về danh sách điểm rỗng.")
        else:
            print(f"Successfully fetched {len(data)} marks from TLU API.")
        return data

    except requests.exceptions.HTTPError as e:
        # Xử lý riêng lỗi 404 (Not Found) nếu có
        if e.response.status_code == 404:
            print(f"LỖI TLU API (StudentMark): 404 Not Found. URL API '{url}' có thể đã sai.")
        else:
            print(f"LỖI TLU API (StudentMark): {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"LỖI TLU API (StudentMark - Kết nối): {e}")
        return None