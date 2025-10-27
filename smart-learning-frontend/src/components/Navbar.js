import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar({ studentName, onLogout }) {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <div className="navbar-logo">🎓 Smart Learning</div>
      </div>

      <div className="navbar-center">
        <Link
          to="/"
          className={`navbar-link ${location.pathname === "/" ? "active" : ""}`}
        >
          Trang chủ
        </Link>
        <Link
          to="/recommendations"
          className={`navbar-link ${
            location.pathname === "/recommendations" ? "active" : ""
          }`}
        >
          Gợi ý học tập
        </Link>
      </div>

      <div className="navbar-right">
        <span>
          Xin chào, <b>{studentName}</b> 👋
        </span>
        <button className="logout-btn" onClick={onLogout}>
          Đăng xuất
        </button>
      </div>
    </nav>
  );
}
