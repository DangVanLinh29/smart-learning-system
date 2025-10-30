import React, { useState } from "react";
import QuizGame from "./QuizGame";
import "./QuizPage.css";
import { FaBook, FaArrowLeft, FaPlayCircle, FaHistory, FaChartPie } from "react-icons/fa";

export default function QuizPage() {
  const subjects = [
    {
      id: "httt",
      name: "Phân tích hệ thống thông tin",
      chapters: [
        { id: 1, title: "Chương 1: Tổng quan về hệ thống thông tin" },
        { id: 2, title: "Chương 2: Mô hình hóa nghiệp vụ" },
        { id: 3, title: "Chương 3: Thiết kế hệ thống" },
      ],
    },
    {
      id: "csdl",
      name: "Cơ sở dữ liệu",
      chapters: [
        { id: 1, title: "Chương 1: Mô hình ER" },
        { id: 2, title: "Chương 2: SQL nâng cao" },
        { id: 3, title: "Chương 3: Tối ưu truy vấn" },
      ],
    },
    {
      id: "python",
      name: "Lập trình Python",
      chapters: [
        { id: 1, title: "Chương 1: Biến và kiểu dữ liệu" },
        { id: 2, title: "Chương 2: Cấu trúc điều khiển" },
        { id: 3, title: "Chương 3: Hàm và mô-đun" },
      ],
    },
  ];

  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [quizHistory, setQuizHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("quiz"); // quiz | history | stats

  const handleStartQuiz = (chapter) => {
    setSelectedChapter(chapter);
  };

  const handleBack = () => {
    if (selectedChapter) {
      setSelectedChapter(null);
    } else {
      setSelectedSubject(null);
    }
  };

  const handleFinishQuiz = (score, total) => {
    const percent = Math.round((score / total) * 100);
    const record = {
      subject: selectedSubject.name,
      chapter: selectedChapter.title,
      score: percent,
      date: new Date().toLocaleString("vi-VN"),
    };

    setQuizHistory([record, ...quizHistory]);
    setSelectedChapter(null);
  };

  // ---- Nếu đang trong QuizGame ----
  if (selectedChapter) {
    return (
      <QuizGame
        subject={selectedSubject.name}
        chapter={selectedChapter}
        onBack={handleBack}
        onFinish={handleFinishQuiz}
      />
    );
  }

  // ---- Tab Lịch sử làm bài ----
  if (activeTab === "history") {
    return (
      <div className="quiz-container">
        <div className="tab-nav">
          <button onClick={() => setActiveTab("quiz")} className="tab-btn">
            <FaBook /> Danh sách quiz
          </button>
          <button className="tab-btn active">
            <FaHistory /> Lịch sử
          </button>
          <button onClick={() => setActiveTab("stats")} className="tab-btn">
            <FaChartPie /> Thống kê
          </button>
        </div>

        <h2>📜 Lịch sử làm bài</h2>
        {quizHistory.length === 0 ? (
          <p>Chưa có bài kiểm tra nào được hoàn thành.</p>
        ) : (
          <table className="quiz-history-table">
            <thead>
              <tr>
                <th>Môn học</th>
                <th>Chương</th>
                <th>Điểm (%)</th>
                <th>Thời gian</th>
              </tr>
            </thead>
            <tbody>
              {quizHistory.map((h, i) => (
                <tr key={i}>
                  <td>{h.subject}</td>
                  <td>{h.chapter}</td>
                  <td>{h.score}</td>
                  <td>{h.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }

  // ---- Tab Thống kê ----
  if (activeTab === "stats") {
    const avg =
      quizHistory.length > 0
        ? (quizHistory.reduce((sum, q) => sum + q.score, 0) /
            quizHistory.length).toFixed(1)
        : 0;

    return (
      <div className="quiz-container">
        <div className="tab-nav">
          <button onClick={() => setActiveTab("quiz")} className="tab-btn">
            <FaBook /> Danh sách quiz
          </button>
          <button onClick={() => setActiveTab("history")} className="tab-btn">
            <FaHistory /> Lịch sử
          </button>
          <button className="tab-btn active">
            <FaChartPie /> Thống kê
          </button>
        </div>

        <h2>📊 Thống kê tổng quan</h2>
        <p>Tổng số bài đã làm: <b>{quizHistory.length}</b></p>
        <p>Điểm trung bình: <b>{avg}%</b></p>
      </div>
    );
  }

  // ---- Tab Danh sách quiz (mặc định) ----
  return (
    <div className="quiz-container">
      <div className="tab-nav">
        <button className="tab-btn active">
          <FaBook /> Danh sách quiz
        </button>
        <button onClick={() => setActiveTab("history")} className="tab-btn">
          <FaHistory /> Lịch sử
        </button>
        <button onClick={() => setActiveTab("stats")} className="tab-btn">
          <FaChartPie /> Thống kê
        </button>
      </div>

      {!selectedSubject ? (
        <>
          <h2>🎯 Chọn môn học để làm bài trắc nghiệm</h2>
          <div className="subject-grid">
            {subjects.map((s) => (
              <div
                key={s.id}
                className="subject-card"
                onClick={() => setSelectedSubject(s)}
              >
                <FaBook className="subject-icon" />
                <h3>{s.name}</h3>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="chapter-view">
          <button className="back-btn" onClick={handleBack}>
            <FaArrowLeft /> Quay lại
          </button>
          <h2>{selectedSubject.name}</h2>
          <p>📘 Chọn chương để bắt đầu làm bài kiểm tra</p>

          <ul className="chapter-list">
            {selectedSubject.chapters.map((c) => (
              <li key={c.id} className="chapter-item">
                <span>{c.title}</span>
                <button className="start-btn" onClick={() => handleStartQuiz(c)}>
                  <FaPlayCircle /> Bắt đầu
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
