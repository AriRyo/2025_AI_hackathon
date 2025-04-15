"use client";


// src/components/ChatBox.tsx
import React, { useState, FormEvent } from "react";

// メッセージの型（簡単なサンプル）
interface Message {
  id: number;
  sender: "user" | "bot";
  text: string;
}

const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    // ユーザーのメッセージを追加
    const userMessage: Message = {
      id: Date.now(),
      sender: "user",
      text: inputText,
    };
    setMessages((prev) => [...prev, userMessage]);
    
    // ここで将来的に ChatGPT API 連携（バックエンド経由）の実装を追加する
    // 暫定的に bot の返答を模倣
    const botMessage: Message = {
      id: Date.now() + 1,
      sender: "bot",
      text: "これはサンプルの返答です。",
    };
    setMessages((prev) => [...prev, botMessage]);
    
    setInputText("");
  };

  return (
    <div className="flex flex-col h-full max-w-xl mx-auto border rounded shadow p-4">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`my-2 p-2 rounded ${
              msg.sender === "user" ? "bg-blue-100 text-right" : "bg-gray-200 text-left"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="メッセージを入力..."
          className="flex-1 p-2 border rounded-l focus:outline-none"
        />
        <button type="submit" className="p-2 bg-blue-500 text-white rounded-r">
          送信
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
