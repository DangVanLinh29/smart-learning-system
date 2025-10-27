import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./CourseVideoPage.css";

export default function CourseVideoPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const course = state?.course;

  // Nếu không có dữ liệu, quay về trang gợi ý
  if (!course) {
    return (
      <div className="video-page-wrapper">
        <h2>⚠️ Không tìm thấy thông tin khóa học.</h2>
        <button className="back-btn" onClick={() => navigate("/recommendations")}>
          ← Quay lại gợi ý học tập
        </button>
      </div>
    );
  }

  return (
    <div className="video-page-container fade-in">
      <div className="video-section">
        <div className="video-header">
          <h2>{course.title}</h2>
          <p>Tiến độ hiện tại: <b>{course.progress}%</b></p>
        </div>

        <div className="video-player">
          {/* Giả lập video player (bạn có thể nhúng link YouTube, file .mp4, hoặc iframe sau này) */}
          <iframe
            width="100%"
            height="450"
            src="https://www.youtube.com/embed/dQw4w9WgXcQ"
            title="Khóa học"
            frameBorder="0"
            allowFullScreen
          ></iframe>
        </div>

        <div className="video-info">
          <p>📘 Môn học: {course.title}</p>
          <p>🎯 Tiến độ: {course.progress}%</p>
        </div>

        <button className="back-btn" onClick={() => navigate("/recommendations")}>
          ← Quay lại gợi ý học tập
        </button>
      </div>

      <div className="lesson-section">
        <h3>📖 Danh sách chương trình học</h3>
        {course.lessons && course.lessons.length > 0 ? (
          <ul className="lesson-list">
            {course.lessons.map((lesson, index) => (
              <li key={index} className="lesson-item">
                <div>
                  <strong>{lesson.title}</strong>
                  {lesson.note && (
                    <p style={{ fontStyle: "italic", margin: "2px 0" }}>
                      {lesson.note}
                    </p>
                  )}
                  <p>Độ phù hợp: {lesson.match}%</p>
                </div>
                <div className="lesson-links">
                  {lesson.document && (
                    <a href={lesson.document} target="_blank" rel="noreferrer">
                      📁 Tài liệu
                    </a>
                  )}
                  {lesson.video && (
                    <a href={lesson.video} target="_blank" rel="noreferrer">
                      🎥 Video
                    </a>
                  )}
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>Không có nội dung bài học nào được tìm thấy.</p>
        )}
      </div>
    </div>
  );
}
