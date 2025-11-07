# 🎓 Smart Learning System

Hệ thống học tập thông minh cho sinh viên Đại học Thủy Lợi (TLU), giúp quản lý tiến độ học tập, phân tích kết quả và gợi ý cải thiện bằng **AI Gemini**.  
Website gồm hai phần: **Frontend (React.js)** và **Backend (Flask, Python)**.

👥 Phân công công việc
Thành viên Vai trò chính Công việc phụ trách
Đặng Văn Linh Quản lý tổng thể dự án, merge branch, cấu trúc code, fix lỗi, tối ưu hệ thống, Chat bot
Huy Backend Lead Xử lý gọi API (Axios), hiển thị dữ liệu động, tối ưu trải nghiệm người dùng
Đạt Backend Lead Huấn luyện và tối ưu mô hình Machine Learning (Linear Regression, CF), triển khai logic AI Gemini, gợi ý học tập thông minh
Nhung Data Engineer Xử lý tong_hop_diem_sinh_vien.csv, huấn luyện mô hình ML (CF, Linear Regression)
Như System & Integration Quản lý cấu trúc hệ thống, đồng bộ dữ liệu data_synchronizer.py, test API và kết nối Front–Back

## 🚀 Công nghệ sử dụng

### 🖥️ Frontend

- React.js (Vite)
- Axios (gọi API)
- TailwindCSS / CSS modules
- React Router DOM

### ⚙️ Backend

- Flask (Python)
- SQLite3 Database
- Google Gemini API
- YouTube Data API v3
- Scikit-learn, Pandas, NumPy
- Dotenv (đọc API keys)
- Linear Regression (dự đoán điểm)
- CF (Collaborative Filtering – gợi ý khóa học)

## 🧩 Tính năng chính

✅ **Đăng nhập sinh viên TLU** (qua API)  
✅ **Phân tích tiến độ học tập** theo từng môn  
✅ **Dự đoán kết quả học tập** bằng mô hình Machine Learning  
✅ **Gợi ý học tập cá nhân hoá** bằng AI Gemini  
✅ **Tìm kiếm video YouTube học tập** theo môn học  
✅ **Khám phá môn học mới** bằng hệ gợi ý CF  
✅ **Giao diện thân thiện, phản hồi nhanh**

---

## 📂 Cấu trúc dự án

smart-learning-system/
├── backend/
│ ├── app.py # Flask API chính
│ ├── recommender.py # Logic AI & gợi ý học tập
│ ├── tlu_api_handler.py # Giao tiếp với API TLU
│ ├── data_synchronizer.py # Đồng bộ dữ liệu sinh viên
│ ├── static_data_importer.py # Xử lý dữ liệu CSV mẫu
│ ├── learning_materials.json # Dữ liệu tài liệu học tập
│ ├── ai_youtube_cache.db # Cache AI & YouTube
│ ├── smart_learning.db # CSDL chính
│ ├── models/
│ │ ├── scaler.joblib
│ │ ├── le_course.joblib
│ │ └── score_mlp.keras
│ ├── requirements.txt
│ └── tong_hop_diem_sinh_vien.csv
│
└── smart-learning-frontend/
├── src/
│ ├── pages/
│ │ ├── Login.js / Login.css
│ │ ├── Dashboard.js
│ │ ├── Recommendation.js / Recommendation.css
│ └── components/
└── package.json

🧠 Cấu hình API Keys

Tạo file `.env` trong thư mục `backend/`:
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key

🏃‍♂️ Cách chạy project

1️⃣ Cài đặt môi trường Backend
cd backend
pip install -r requirements.txt
npm start: Mở Chat Bot

2️⃣ Cài đặt Frontend
cd smart-learning-frontend
npm install
npm run start

📊 Ví dụ API
| Endpoint | Mô tả |
| ---------------------------------- | ------------------------------ |
| `/api/login` | Đăng nhập sinh viên TLU |
| `/api/progress/<student_id>` | Lấy tiến độ học tập |
| `/api/recommendation/<student_id>` | Gợi ý học tập bằng AI |
| `/api/insight/<student_id>` | Phân tích AI tổng quan |
| `/api/predict/<student_id>` | Dự đoán kết quả sắp tới |
| `/api/youtube/<keyword>` | Tìm video YouTube theo từ khóa |

🧩 Demo gợi ý AI
Gửi prompt tới Google Gemini → AI trả về JSON gồm “roadmap” & “video_topics” → Flask xử lý và kết hợp kết quả với video YouTube thật.

🧾 License
MIT License — dùng cho mục đích học tập và nghiên cứu.
