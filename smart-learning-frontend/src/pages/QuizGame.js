import React, { useState, useEffect } from "react";
import "./QuizGame.css";

export default function QuizGame({ subject, chapter, onBack, onFinish }) {
  const questions = [
    {
      q: "Python dùng kiểu dữ liệu nào để lưu danh sách?",
      options: ["List", "Tuple", "Dict", "Set"],
      answer: "List",
    },
    {
      q: "Hàm nào dùng để in ra màn hình trong Python?",
      options: ["input()", "print()", "echo()", "display()"],
      answer: "print()",
    },
    {
      q: "Kiểu dữ liệu của giá trị True trong Python là?",
      options: ["int", "bool", "string", "float"],
      answer: "bool",
    },
  ];

  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  const handleAnswer = (selected) => {
    if (selected === questions[index].answer) {
      setScore(score + 1);
    }

    if (index + 1 < questions.length) {
      setIndex(index + 1);
    } else {
      setIsFinished(true);
    }
  };

  // 🔥 Gửi kết quả lên QuizPage khi hoàn thành
  useEffect(() => {
    if (isFinished && onFinish) {
      onFinish(score, questions.length);
    }
  }, [isFinished]);

  if (isFinished) {
    return (
      <div className="quiz-end">
        <button className="back-btn" onClick={onBack}>← Quay lại danh sách</button>
        <h2>🧠 Bài kiểm tra: {subject} — {chapter.title}</h2>
        <p>✅ Bạn đúng {score}/{questions.length} câu!</p>
        <p>{score / questions.length >= 0.7 ? "Tốt lắm!" : "Khá ổn! Cần ôn thêm chút nữa."}</p>
      </div>
    );
  }

  const current = questions[index];

  return (
    <div className="quiz-game">
      <button className="back-btn" onClick={onBack}>← Quay lại</button>
      <h2>{subject} — {chapter.title}</h2>
      <p><b>Câu {index + 1}:</b> {current.q}</p>

      <div className="options">
        {current.options.map((opt, i) => (
          <button key={i} className="option-btn" onClick={() => handleAnswer(opt)}>
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
