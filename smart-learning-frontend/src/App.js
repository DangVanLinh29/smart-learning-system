import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// Import các component cũ
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import Recommendation from "./components/Recommendation";
import CourseVideoPage from "./components/CourseVideoPage";
// 1. IMPORT COMPONENT MỚI (SchedulePage)
import SchedulePage from "./components/SchedulePage"; 

function App() {
  const [student, setStudent] = useState(null);

  return (
    <Router>
      {/* Navbar sẽ hiển thị nếu student (sinh viên) đã đăng nhập */}
      {student && <Navbar studentName={student.name} onLogout={() => setStudent(null)} />}
      
      <Routes>
        {!student ? (
          // Nếu CHƯA đăng nhập, tất cả các đường dẫn đều trỏ về trang Login
          <Route path="*" element={<Login onLoginSuccess={setStudent} />} />
        ) : (
          // Nếu ĐÃ đăng nhập, cho phép truy cập các trang nội bộ
          <>
            <Route
              path="/"
              element={<Dashboard studentId={student.student_id} studentName={student.name} />}
            />
            <Route
              path="/recommendations"
              element={<Recommendation studentId={student.student_id} studentName={student.name} />}
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
    </Router>
  );
}

export default App;