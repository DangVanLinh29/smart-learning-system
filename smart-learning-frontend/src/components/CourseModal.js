import React from "react";
import { useNavigate } from "react-router-dom";
import "./CourseModal.css";

export default function CourseModal({ course, onClose }) {
  const navigate = useNavigate();

  // Nếu chưa chọn môn nào thì không hiển thị modal
  if (!course) return null;

  const lessons = course.lessons || [];

  // Khi ấn "Xem khóa học" → điều hướng sang trang video kèm dữ liệu môn học
  const handleOpenCourse = () => {
    navigate("/course-video", { state: { course } });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>
          ×
        </button>

        <h2>{course.title}</h2>
        <p>
          Tiến độ hiện tại: <b>{course.progress || 0}%</b>
        </p>

        <h3>📘 Chương trình học</h3>

        {lessons.length === 0 ? (
          <p>Không có nội dung chi tiết cho môn học này.</p>
        ) : (
          lessons.map((lesson, index) => (
            <div key={index} className="enhanced-card">
              <h4>{lesson.title || `Chương ${index + 1}`}</h4>

              {/* 🔹 Phần gợi ý học tập */}
              {lesson.note && (
                <p
                  style={{
                    fontStyle: "italic",
                    marginBottom: "0.5rem",
                    color: "#374151",
                    lineHeight: "1.5",
                  }}
                >
                  {lesson.note}
                </p>
              )}

              {/* 🔹 Thanh tiến độ */}
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${lesson.match || 0}%`,
                    background:
                      lesson.match > 80
                        ? "linear-gradient(90deg, #3b82f6, #2563eb)"
                        : "linear-gradient(90deg, #f59e0b, #d97706)",
                  }}
                ></div>
              </div>

              <p>Độ phù hợp: {lesson.match || 0}%</p>

              {/* 🔹 Link học liệu */}
              <div style={{ marginTop: "0.5rem" }}>
                {lesson.document && (
                  <a
                    href={lesson.document}
                    target="_blank"
                    rel="noreferrer"
                    className="lesson-link"
                  >
                    📁 Xem tài liệu
                  </a>
                )}
                {lesson.video && (
                  <>
                    <br />
                    <a
                      href={lesson.video}
                      target="_blank"
                      rel="noreferrer"
                      className="lesson-link"
                    >
                      🎥 Xem video
                    </a>
                  </>
                )}
              </div>
            </div>
          ))
        )}

        {/* 🔹 Nút xem khóa học */}
        <div className="footer-actions">
          <button className="download-btn" onClick={handleOpenCourse}>
            🚀 Xem khóa học
          </button>
        </div>
      </div>
    </div>
  );
}
