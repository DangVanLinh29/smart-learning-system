## 🎯 Giới thiệu

**Smart Learning System** là nền tảng học trực tuyến thông minh giúp sinh viên học theo **lộ trình và tốc độ riêng**, từ đó tăng hiệu quả học tập và hỗ trợ giảng viên trong việc quản lý, đánh giá và định hướng học tập cá nhân hóa.

Dự án gồm **2 phần chính**:

- 🖥 **Frontend (ReactJS):** Giao diện web thân thiện, trực quan.
- ⚙️ **Backend (Flask - Python):** Xử lý dữ liệu, gợi ý lộ trình học tập, kết nối cơ sở dữ liệu và AI.

---

### Phân chia công việc

| Thành phần                       | Công nghệ                                | Vai trò chính                                              | Người phụ trách |
| -------------------------------- | ---------------------------------------- | ---------------------------------------------------------- | --------------- |
| 🖥 **Frontend**                   | ReactJS / ChartJS / Framer Motion        | Giao diện học tập, dashboard, quiz, chatbot                | **Linh**        |
| ⚙️ **Backend**                   | Flask (Python)                           | API xử lý dữ liệu, kết nối mô hình AI                      | **Huy**         |
| 🧩 **Cơ sở dữ liệu**             | MySQL / SQLite                           | Lưu trữ thông tin sinh viên, khóa học, kết quả học tập     | **Nhung**       |
| 🤖 **AI / Machine Learning**     | Scikit-learn / TensorFlow / Pandas / NLP | Gợi ý học liệu, phân tích năng lực học tập, chatbot hỗ trợ | **Đạt**         |
| ☁️ **Hạ tầng lưu trữ**           | Google Cloud / Firebase / AWS            | Lưu trữ tài nguyên học tập, mở rộng triển khai             | **Như**         |
| 📊 **Phân tích & trực quan hóa** | Power BI / ChartJS / Looker Studio       | Theo dõi tiến độ học, phân tích kết quả theo thời gian     | **Như**         |
| 🐳 **Triển khai & CI/CD**        | Docker / GitHub Actions / Render         | Tự động hóa build – deploy hệ thống                        | **Nhung**       |

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
├── 📁 backend/ # Xử lý dữ liệu, API, mô hình AI
│ ├── app.py # Flask / FastAPI server chính
│ ├── recommender.py # Mô hình gợi ý học tập cá nhân
│ ├── data/ # Dữ liệu mô phỏng
│ │ ├── students.csv # Danh sách sinh viên
│ │ ├── courses.csv # Danh sách khóa học
│ │ └── progress.csv # Tiến độ học tập
│ └── requirements.txt # Danh sách thư viện Python cần cài
│
├── 📁 frontend/ # Giao diện người dùng (React)
│ ├── src/
│ │ ├── components/ # Các component: Login, Dashboard, CourseModal...
│ │ ├── pages/ # Các trang: Home, Recommendation, VideoPlayer...
│ │ └── assets/ # Ảnh, biểu tượng, CSS
│ └── package.json # Cấu hình và dependency React
│
├── 📁 dashboard/ # Phân tích và trực quan hóa dữ liệu
│ ├── analysis.ipynb # Notebook phân tích tiến độ học tập
│ ├── looker_dashboard_link.txt # Link Looker Studio (hoặc Power BI)
│ └── superset_config.py # Cấu hình Apache Superset (nếu có)
│
├── 📁 docs/ # Tài liệu và báo cáo
│ ├── proposal.pdf # Đề cương dự án
│ ├── architecture-diagram.png # Sơ đồ kiến trúc hệ thống
│ ├── system_design.docx # Tài liệu thiết kế hệ thống
│ └── final_report.docx # Báo cáo cuối kỳ
│
├── 📁 .github/ # CI/CD tự động (tùy chọn)
│ └── workflows/
│ └── deploy.yml # Pipeline build & deploy
│
├── .gitignore # Loại trừ node_modules, venv, v.v.
├── README.md # Hướng dẫn và mô tả dự án
└── LICENSE # Giấy phép mã nguồn mở (MIT / Apache 2.0)

## 🚀 Cài đặt & chạy dự án

### 1️⃣ Clone repository

git clone https://github.com/DangVanLinh29/smart-learning-system.git
cd smart-learning-system

### 2️⃣ Cài đặt Backend (Flask)

cd backend
python -m venv venv
venv\Scripts\activate # Windows
pip install -r requirements.txt

3️⃣ Cài đặt Frontend (React)
cd ../smart-learning-frontend
npm install

4️⃣ Chạy toàn bộ hệ thống cùng lúc

Về thư mục gốc: smart-learning-system
Chạy chương trình:smart-learning-frontend
npm start
Chạy chatbot: cd backend   
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
