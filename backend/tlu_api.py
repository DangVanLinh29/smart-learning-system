import requests
import urllib3
import pandas as pd
import getpass # Thu vien de nhap mat khau an toan

# Tat canh bao ve chung chi bao mat (InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def authenticate_tlu(username, password):
    """
    Lay Access Token tu API TLU.
    Tra ve token hoac None neu that bai.
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
        token_response.raise_for_status() # Bao loi neu (4xx, 5xx)
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if access_token:
            print("OK: Dang nhap TLU va lay token thanh cong!") # Sua loi Unicode
            
            # SAU KHI CO TOKEN, LAY LUON THONG TIN USER
            user_info = fetch_student_data(access_token)
            if user_info:
                # Tra ve 1 dict (tu dien) day du thong tin
                return {
                    **user_info, # Ghep user_info vao dict
                    "access_token": access_token,
                    "success": True
                }
            else:
                print("ERROR: Lay token thanh cong nhung khong lay duoc user info.")
                return None
        else:
            print("ERROR: Khong tim thay access_token trong phan hoi.")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"ERROR TLU API (Auth): {e.response.status_code}")
        try:
            print(f"   Chi tiet: {e.response.text}")
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"ERROR (Unknown Auth): {e}")
        return None

# --- HAM MOI (Lay tu script get_lich_hoc.py) ---
def fetch_current_semester_id(access_token):
    """
    GOI API 'semester_info' DE LAY ID HOC KY HIEN TAI.
    """
    semester_info_url = "https://sinhvien1.tlu.edu.vn/education/api/semester/semester_info" # URL ANH EM MINH DA TIM THAY
    
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(semester_info_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        current_semester_id = None
        
        if isinstance(data, list) and len(data) > 0:
            # API TLU tra ve 1 list, [0] la hoc ky hien tai
            current_semester_id = data[0].get('id') 
        elif isinstance(data, dict):
            # De phong TLU API tra ve 1 object
            current_semester_id = data.get('id')
            
        if current_semester_id:
            print(f"OK: Lay thanh cong ID hoc ky hien tai: {current_semester_id}")
            return current_semester_id
        else:
            print("ERROR: Khong the phan tich ID hoc ky tu 'semester_info'.")
            return None
            
    except Exception as e:
        print(f"ERROR TLU API (Semester Info): {e}")
        return None

# --- HAM MOI (Lay tu script get_lich_hoc.py) ---
def fetch_student_schedule(access_token, semester_id): 
    """
    Lay du lieu lich hoc (cac mon dang hoc) tu API TLU.
    """
    schedule_url = f"https://sinhvien1.tlu.edu.vn/education/api/StudentCourseSubject/studentLoginUser/{semester_id}"
    print(f"... Dang goi API lich hoc: {schedule_url}")

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(schedule_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        print(f"OK: Lay thanh cong du lieu lich hoc (Tim thay {len(data)} mon).")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR TLU API (Lich hoc): {e}")
        return None
# --- KET THUC PHAN THEM MOI ---


def fetch_student_data(access_token):
    """
    Lay thong tin ca nhan cua sinh vien tu TLU API.
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
            "major": "He thong thong tin" # Gia dinh theo thong tin cua anh
        }
    except requests.exceptions.RequestException as e:
        print(f"ERROR TLU API (User Data): {e}")
        return None


def fetch_student_marks(access_token):
    """
    LAY TOAN BO DIEM TONG KET (TAT CA HOC KY)
    """
    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/getListMarkDetailStudent" # API DIEM TONG KET
    
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if not data:
             print("WARNING: TLU API (StudentMark) tra ve danh sach diem rong.")
        else:
            print(f"OK: Lay thanh cong {len(data)} diem tong ket tu TLU API.")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR TLU API (StudentMark): {e}")
        return None

