"use client";

import React, { useState, FormEvent } from "react";

interface Message {
  id: number;
  sender: "user" | "bot";
  text: string;
}

const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // ユーザーのメッセージを追加
    const userMessage: Message = {
      id: Date.now(),
      sender: "user",
      text: inputText,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // バックエンドの /chat エンドポイントに POST リクエストを送信
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputText }),
      });

      if (!response.ok) {
        throw new Error("ネットワークエラーが発生しました。");
      }

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now() + 1,
        sender: "bot",
        text: data.reply || "返答がありません。",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      // エラー時のメッセージ表示
      const errorMessage: Message = {
        id: Date.now() + 1,
        sender: "bot",
        text: "エラーが発生しました。",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setInputText("");
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-xl mx-auto border rounded shadow p-4">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`my-2 p-2 rounded ${
              msg.sender === "user"
                ? "bg-blue-100 text-right"
                : "bg-gray-200 text-left"
            }`}
          >
            {msg.text}
          </div>
        ))}
        {loading && <div className="text-center">読み込み中...</div>}
      </div>
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="メッセージを入力..."
          className="flex-1 p-2 border rounded-l focus:outline-none"
        />
        <button
          type="submit"
          className="p-2 bg-blue-500 text-white rounded-r"
          disabled={loading}
        >
          送信
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
