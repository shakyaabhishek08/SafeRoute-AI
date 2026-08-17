import React, { useState, useRef, useEffect } from "react";
import api from "../lib/api";
import { Send, Bot, User } from "lucide-react";

function AIChat() {

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "👋 Hello! I'm SafeRoute AI. Ask me anything about safe routes, crime hotspots, emergency services or travel safety.",
    },
  ]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function sendMessage() {

    if (!input.trim()) return;

    const userMessage = {
      sender: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);

    try {

      const res = await api.post("/chat", {

        message: input,

      });

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            res.data.reply ||
            res.data.response ||
            "No response received.",
        },
      ]);

    } catch (err) {

      console.log(err);

      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "❌ Unable to contact AI server.",
        },
      ]);

    }

    setInput("");

    setLoading(false);

  }

  return (

    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
      }}
    >

      <h1
        style={{
          marginBottom: "20px",
        }}
      >
        🤖 SafeRoute AI Assistant
      </h1>

      <div
        style={{
          height: "600px",
          overflowY: "auto",
          background: "white",
          borderRadius: "15px",
          padding: "20px",
          boxShadow: "0 5px 15px rgba(0,0,0,.1)",
        }}
      >

        {messages.map((msg, index) => (

          <div
            key={index}
            style={{
              display: "flex",
              justifyContent:
                msg.sender === "user"
                  ? "flex-end"
                  : "flex-start",
              marginBottom: "15px",
            }}
          >

            <div
              style={{
                background:
                  msg.sender === "user"
                    ? "#2563eb"
                    : "#e5e7eb",
                color:
                  msg.sender === "user"
                    ? "white"
                    : "#111827",
                padding: "15px",
                borderRadius: "15px",
                maxWidth: "70%",
                display: "flex",
                gap: "10px",
                alignItems: "flex-start",
              }}
            >

              {msg.sender === "bot" ? (
                <Bot size={20} />
              ) : (
                <User size={20} />
              )}

              <span>{msg.text}</span>

            </div>

          </div>

        ))}

        {loading && (

          <div
            style={{
              color: "#6b7280",
              marginTop: "10px",
            }}
          >

            🤖 AI is typing...

          </div>

        )}

        <div ref={bottomRef}></div>

      </div>

      <div
        style={{
          display: "flex",
          gap: "10px",
          marginTop: "20px",
        }}
      >

        <input
          value={input}
          onChange={(e) =>
            setInput(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendMessage();
            }
          }}
          placeholder="Ask anything..."
          style={{
            flex: 1,
            padding: "15px",
            borderRadius: "10px",
            border: "1px solid #ccc",
            fontSize: "16px",
          }}
        />

        <button
          onClick={sendMessage}
          style={{
            background: "#2563eb",
            color: "white",
            border: "none",
            padding: "15px 20px",
            borderRadius: "10px",
            cursor: "pointer",
          }}
        >

          <Send size={20} />

        </button>

      </div>

    </div>

  );

}

export default AIChat;