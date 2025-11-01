import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// Import các component cũ
import Navbar from "./components/Navbar";

// Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Recommendation from "./pages/Recommendation";
import CourseVideoPage from "./pages/CourseVideoPage";

// ✅ import Chatbot (đường dẫn chỉnh lại đúng)
import Chatbot from "./components/Chatbot";

// 1. IMPORT COMPONENT MỚI (SchedulePage)
import SchedulePage from "./components/SchedulePage"; 


function App() {
  const [student, setStudent] = useState(null);

  return (
    <Router>
      {/* Navbar sẽ hiển thị nếu student (sinh viên) đã đăng nhập */}
      {student && <Navbar studentName={student.name} onLogout={() => setStudent(null)} />}
      
      <Routes>
        {/* Nếu chưa đăng nhập → hiển thị trang Login */}
        {!student ? (
          // Nếu CHƯA đăng nhập, tất cả các đường dẫn đều trỏ về trang Login
          <Route path="*" element={<Login onLoginSuccess={setStudent} />} />
        ) : (
          // Nếu ĐÃ đăng nhập, cho phép truy cập các trang nội bộ
          <>
            <Route
              path="/"
              element={
                <Dashboard
                  studentId={student.student_id}
                  studentName={student.name}
                />
              }
            />
            <Route
              path="/recommendations"
              element={<Recommendation student={student} />}
            />

            <Route path="/course-video" element={<CourseVideoPage />} />
            
            {/* 2. ĐỊNH TUYẾN CHO /schedule (PHẢI KHỚP VỚI NAVBAR) */}
            <Route 
              path="/schedule" 
              element={<SchedulePage studentId={student.student_id} studentName={student.name} />} 
            />
            {/* === HẾT PHẦN THÊM MỚI === */}
            
          </>
        )}
      </Routes>

      {/* ✅ Thêm Chatbot nổi ở mọi trang khi sinh viên đã đăng nhập */}
      {student && <Chatbot />}
    </Router>
  );
}

export default App;