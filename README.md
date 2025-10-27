# 🧠 Smart Learning System

## 🎯 Giới thiệu

**Smart Learning System** là nền tảng học trực tuyến thông minh giúp sinh viên học theo **lộ trình và tốc độ riêng**, từ đó tăng hiệu quả học tập và hỗ trợ giảng viên trong việc quản lý, đánh giá và định hướng học tập cá nhân hóa.

Dự án gồm **2 phần chính**:

- 🖥 **Frontend (ReactJS):** Giao diện web thân thiện, trực quan.
- ⚙️ **Backend (Flask - Python):** Xử lý dữ liệu, gợi ý lộ trình học tập, kết nối cơ sở dữ liệu và AI.

---

## 👥 Thành viên nhóm

| STT | Họ tên    | Vai trò                                                           |
| --- | --------- | ----------------------------------------------------------------- |
| 1️⃣  | **Linh**  | Frontend Developer – Thiết kế & phát triển giao diện ReactJS      |
| 2️⃣  | **Huy**   | Backend Developer – Xây dựng API Flask & quản lý dữ liệu học tập  |
| 3️⃣  | **Đạt**   | AI Developer – Xây dựng mô hình gợi ý học tập cá nhân hóa         |
| 4️⃣  | **Nhung** | Data Engineer – Xử lý dữ liệu, phân tích hành vi học tập          |
| 5️⃣  | **Như**   | QA & Documentation – Kiểm thử hệ thống và viết tài liệu hướng dẫn |

---

## 🎯 Mục tiêu cụ thể

1. Phân tích dữ liệu học tập để đề xuất khóa học và tài liệu phù hợp.
2. Gợi ý **video, bài tập, quiz** theo năng lực cá nhân bằng mô hình học máy.
3. Xây dựng **dashboard trực quan** theo dõi tiến độ học tập và điểm số theo thời gian thực.
4. Tích hợp **chatbot AI** hỗ trợ sinh viên trong quá trình học.
5. Hỗ trợ giảng viên phát hiện sinh viên gặp khó khăn để can thiệp kịp thời.

---

## ⚙️ Cấu trúc dự án

smart-learning-system/
│
├── backend/ # Flask backend (API, ML model)
│ ├── app.py
│ ├── requirements.txt
│ └── venv/ # Môi trường ảo Python (không push)
│
├── smart-learning-frontend/ # React frontend
│ ├── src/
│ ├── public/
│ └── node_modules/ # Tự sinh khi npm install (không push)
│
└── README.md

## 🚀 Cài đặt & chạy dự án

### 1️⃣ Clone repository

git clone https://github.com/DangVanLinh29/smart-learning-system.git
cd smart-learning-system

### 2️⃣ Cài đặt Backend (Flask)

cd backend
python -m venv venv
venv\Scripts\activate # Windows

# hoặc source venv/bin/activate (Mac/Linux)

pip install -r requirements.txt

3️⃣ Cài đặt Frontend (React)
cd ../smart-learning-frontend
npm install

4️⃣ Chạy toàn bộ hệ thống cùng lúc

Về thư mục gốc: smart-learning-system

npm start

🧰 Công nghệ sử dụng
Frontend
ReactJS
Chart.js
React Router
Axios
Framer Motion
Backend
Flask
Pandas
Scikit-learn
Flask-CORS
