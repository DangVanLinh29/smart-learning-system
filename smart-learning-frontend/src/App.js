import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

// Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Recommendation from "./pages/Recommendation";
import CourseVideoPage from "./pages/CourseVideoPage";
import QuizPage from "./pages/QuizPage";

// ✅ import Chatbot (đường dẫn chỉnh lại đúng)
import Chatbot from "./components/Chatbot";

function App() {
  const [student, setStudent] = useState(null);

  return (
    <Router>
      {/* Navbar chỉ hiện khi đã đăng nhập */}
      {student && (
        <Navbar studentName={student.name} onLogout={() => setStudent(null)} />
      )}

      <Routes>
        {/* Nếu chưa đăng nhập → hiển thị trang Login */}
        {!student ? (
          <Route path="*" element={<Login onLoginSuccess={setStudent} />} />
        ) : (
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
              element={
                <Recommendation
                  studentId={student.student_id}
                  studentName={student.name}
                />
              }
            />
            <Route path="/course-video" element={<CourseVideoPage />} />
            <Route path="/quiz" element={<QuizPage />} />
          </>
        )}
      </Routes>

      {/* ✅ Thêm Chatbot nổi ở mọi trang khi sinh viên đã đăng nhập */}
      {student && <Chatbot />}
    </Router>
  );
}

export default App;
