import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import "./Navbar.css";

export default function Navbar({ studentName, onLogout }) {
  const navigate = useNavigate();

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
        <NavLink to="/progress">
          Tiến độ học tập
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
