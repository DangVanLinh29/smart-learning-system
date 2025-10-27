import React from "react";
import "./CourseCard.css";

export default function CourseCard({ course, onSelect }) {
  const lessons = course.lessons || [];

  return (
    <div className="course-card">
      <h3>{course.title || course.name}</h3>
      <p>Tiến độ: <b>{course.progress || 0}%</b></p>

      {lessons.length > 0 ? (
        <ul>
          {lessons.slice(0, 3).map((lesson, idx) => (
            <li key={idx}>{lesson.note || lesson.title}</li>
          ))}
        </ul>
      ) : (
        <p>Không có gợi ý cụ thể.</p>
      )}

      <button onClick={() => onSelect(course)}>Xem chi tiết</button>
    </div>
  );
}
