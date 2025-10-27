import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import Recommendation from "./components/Recommendation";
import CourseVideoPage from "./components/CourseVideoPage";

function App() {
  const [student, setStudent] = useState(null);

  return (
    <Router>
      {student && <Navbar studentName={student.name} onLogout={() => setStudent(null)} />}
      <Routes>
        {!student ? (
          <Route path="*" element={<Login onLoginSuccess={setStudent} />} />
        ) : (
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
          
          </>
        )}
      </Routes>
    </Router>
  );
}

export default App;
