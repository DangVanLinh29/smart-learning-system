import React from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";  // ✅ thêm useLocation
import "./Navbar.css";

export default function Navbar({ studentName, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation(); // ✅ hook này thay cho window.location

  return (
    <nav className="navbar">
      <div className="navbar-logo" onClick={() => navigate("/")}>
        Smart Learning
      </div>

      <div className="navbar-links">
        <NavLink to="/" end>
          Tổng quan
        </NavLink>
        <NavLink to="/recommendations">
          Gợi ý học tập
        </NavLink>
        <NavLink
          to="/schedule"
          className={`navbar-link ${
            location.pathname === "/schedule" ? "active" : ""
          }`}
        >
          Các môn đang học
        </NavLink>
      </div>

      <div className="navbar-user">
        <span>
          Xin chào, <b>{studentName}</b>
        </span>
        <button className="logout-btn" onClick={onLogout}>
          Đăng xuất
        </button>
      </div>
    </nav>
  );
}
