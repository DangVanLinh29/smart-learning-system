import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Recommendation.css";

export default function RecommendationPage({ student }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!student || !student.student_id) {
        console.warn("⚠️ Chưa có thông tin sinh viên.");
        setLoading(false);
        return;
      }

      try {
        const res = await axios.get(
          `http://127.0.0.1:5000/api/recommendation/${student.student_id}`
        );
        setRecommendations(res.data.recommendations || []);
        setMessage(res.data.message || "");
      } catch (err) {
        console.error("❌ Lỗi khi gọi API:", err);
        setError("Không thể tải gợi ý học tập!");
      } finally {
        setLoading(false);
      }
    };
    fetchRecommendations();
  }, [student]);

  if (loading)
    return <div className="recommendation-loading">⏳ Đang tải dữ liệu...</div>;
  if (error) return <div className="recommendation-error">{error}</div>;

  return (
    <div className="recommendation-container">
      <h2>💡 Gợi ý học tập cá nhân hoá</h2>
      <p className="recommendation-message">⚡ {message}</p>

      <div className="recommendation-list">
        {recommendations.map((item, idx) => (
          <div className="recommendation-card" key={idx}>
            <h3 className="course-title">📘 {item.course}</h3>
            <p className="progress-text">
              Tiến độ: <b>{item.progress}%</b>
            </p>

            <ul className="roadmap">
              {item.roadmap.map((tip, i) => (
                <li key={i}>✅ {tip}</li>
              ))}
            </ul>

            {/* 🔹 Video gợi ý */}
            {item.resources?.videos?.length > 0 && (
              <div className="resource-block">
                <h4>📺 Video gợi ý</h4>
                <div className="video-grid">
                  {item.resources.videos.slice(0, 2).map((v, i) => {
                    const videoId = v.url.split("v=")[1]?.split("&")[0];
                    const thumb = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
                    return (
                      <a
                        key={i}
                        href={v.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="video-card"
                      >
                        <img src={thumb} alt={v.title} className="video-thumb" />
                        <p className="video-title">{v.title}</p>
                      </a>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 🔹 Tài liệu tham khảo */}
            {item.resources?.documents?.length > 0 && (
              <div className="resource-block">
                <h4>📘 Tài liệu tham khảo</h4>
                <ul className="link-list">
                  {item.resources.documents.map((doc, i) => (
                    <li key={i}>
                      <a
                        href={doc}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-truncate"
                      >
                        📄 {new URL(doc).hostname.replace("www.", "")}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 🔹 Bài tập luyện tập */}
            {item.resources?.exercises?.length > 0 && (
              <div className="resource-block">
                <h4>🧩 Bài tập luyện tập</h4>
                <ul className="link-list">
                  {item.resources.exercises.map((ex, i) => (
                    <li key={i}>
                      <a
                        href={ex}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-truncate"
                      >
                        💡 {new URL(ex).hostname.replace("www.", "")}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
