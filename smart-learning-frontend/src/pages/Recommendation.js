import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Recommendation.css";

export default function Recommendation({ studentId = "2251162036", studentName = "Nguyễn Văn A" }) {
  const [recommendations, setRecommendations] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:5000/api/recommendation/${studentId}`)
      .then((res) => {
        const fixedData = JSON.parse(
          JSON.stringify(res.data).replace(/\\u[\dA-F]{4}/gi, (m) =>
            String.fromCharCode(parseInt(m.replace(/\\u/g, ""), 16))
          )
        );
        setRecommendations(fixedData.recommendations || []);
        setMessage(fixedData.message || "");
      })
      .catch(() => {
        setMessage("⚠️ Không thể tải dữ liệu gợi ý học tập.");
      });
  }, [studentId]);

  return (
    <div className="recommend-page">
      <div className="content-container">
        {/* Thông tin sinh viên */}
        <section className="student-info">
          <h2>🎓 Thông tin tổng quát sinh viên</h2>
          <p><b>Họ tên:</b> {studentName}</p>
          <p><b>Mã SV:</b> {studentId}</p>
          <p><b>Ngành:</b> Hệ thống thông tin</p>
          <p><b>GPA:</b> 7.8</p>
          <p>💪 <b>Mạnh:</b> Lập trình, CSDL</p>
          <p>⚠️ <b>Cần cải thiện:</b> Giải thuật, Toán rời rạc</p>
        </section>

        {/* Gợi ý học liệu */}
        <section className="recommend-wrapper">
          <h2>💡 Gợi ý học liệu cá nhân hóa</h2>
          <div className="recommend-grid">
            {recommendations.length > 0 ? (
              recommendations.map((rec, index) => (
                <div key={index} className="recommend-card">
                  <h3>📘 {rec.course}</h3>
                  <p>{rec.reason || "AI gợi ý bạn nên củng cố thêm kỹ năng này."}</p>
                  <a href={rec.link || "#"} target="_blank" rel="noreferrer">🔗 Xem chi tiết</a>
                </div>
              ))
            ) : (
              <>
                <div className="recommend-card">
                  <h3>🧠 Giải thuật tìm kiếm nhị phân – Binary Search</h3>
                  <p>Bạn có điểm thấp trong phần Giải thuật (6.5) và làm sai 40% câu hỏi về đệ quy.</p>
                  <a href="#">🔗 Xem chi tiết</a>
                </div>
                <div className="recommend-card">
                  <h3>📗 Cấu trúc dữ liệu – PDF minh họa dễ hiểu</h3>
                  <p>AI phát hiện bạn xem lại video 3 lần nhưng vẫn sai ở phần cây nhị phân.</p>
                  <a href="#">🔗 Xem chi tiết</a>
                </div>
                <div className="recommend-card">
                  <h3>🌱 Luyện tập Cấu trúc dữ liệu tổng hợp</h3>
                  <p>Phù hợp để củng cố kỹ năng lập trình căn bản.</p>
                  <a href="#">🔗 Xem chi tiết</a>
                </div>
              </>
            )}
          </div>
        </section>

        {/* Lý do gợi ý */}
        <section className="reason-section">
          <h2>💬 Lý do gợi ý</h2>
          <p>
            Dựa trên phân tích điểm học tập và tiến độ học của bạn, hệ thống nhận thấy một số kỹ năng
            cần cải thiện để đạt hiệu suất tốt hơn. AI đã tổng hợp gợi ý phù hợp với năng lực của bạn.
          </p>
        </section>

        {/* Theo dõi tiến độ */}
        <section className="progress-section">
          <h2>📈 Theo dõi tiến độ học tập</h2>
          <div className="sl-progress-item">
            <span>🎥 Video</span>
            <div className="sl-progress-track">
              <div className="sl-progress-fill" style={{ width: "70%", background: "#42a5f5" }}></div>
            </div>
            <p>70% hoàn thành</p>
          </div>
          <div className="sl-progress-item">
            <span>🧩 Quiz</span>
            <div className="sl-progress-track">
              <div className="sl-progress-fill" style={{ width: "80%", background: "#66bb6a" }}></div>
            </div>
            <p>80% hoàn thành</p>
          </div>
          <div className="sl-progress-item">
            <span>📄 Tài liệu</span>
            <div className="sl-progress-track">
              <div className="sl-progress-fill" style={{ width: "60%", background: "#5c6bc0" }}></div>
            </div>
            <p>60% hoàn thành</p>
          </div>
        </section>
      </div>
    </div>
  );
}
