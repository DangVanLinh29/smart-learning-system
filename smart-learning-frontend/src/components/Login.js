import React, { useState } from "react";
import axios from "axios";
import "./Login.css";

export default function Login({ onLoginSuccess }) {
  const [studentId, setStudentId] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await axios.post("http://127.0.0.1:5000/api/login", {
        student_id: studentId,
      });

      if (res.data.success) {
        onLoginSuccess(res.data.student);
      } else {
        setError("Không tìm thấy sinh viên!");
      }
    } catch (err) {
      setError("Lỗi kết nối server!");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>🎓 Smart Learning System</h2>
        <p>Đăng nhập bằng mã sinh viên</p>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="Nhập mã sinh viên..."
            required
          />
          <button type="submit">Đăng nhập</button>
        </form>

        {error && <p className="error-text">{error}</p>}
      </div>
    </div>
  );
}
