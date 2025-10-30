import React, { useState } from "react";
import axios from "axios";
import "./Login.css";

export default function Login({ onLoginSuccess }) {
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await axios.post("http://127.0.0.1:5000/api/login", {
        student_id: studentId,
        password: password,
      });

      if (res.data.success) {
        // ✅ Lưu thông tin sinh viên để các trang khác (như Hồ sơ) đọc lại được
        localStorage.setItem("student", JSON.stringify(res.data.student));

        // ✅ Gọi hàm App để chuyển hướng
        onLoginSuccess(res.data.student);
      } else {
        setError(res.data.message || "Sai mã sinh viên hoặc mật khẩu!");
      }
    } catch (err) {
      setError("Lỗi kết nối server!");
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>🎓 Smart Learning System</h2>
        <p>Đăng nhập bằng tài khoản TLU</p>

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="Nhập mã sinh viên..."
            required
          />

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Nhập mật khẩu..."
            required
          />
          <button type="submit">Đăng nhập</button>
        </form>

        {error && <p className="error-text">{error}</p>}
      </div>
    </div>
  );
}
