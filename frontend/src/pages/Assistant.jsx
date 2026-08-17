import React, { useState } from "react";

function Assistant() {
  const [msg, setMsg] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);

  async function askAI() {
    if (msg.trim() === "") {
      alert("Please enter your question.");
      return;
    }

    setLoading(true);
    setReply("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: msg,
          session_id: "demo",
        }),
      });

      if (!res.ok) {
        throw new Error("Server Error");
      }

      const data = await res.json();

      setReply(data.reply);
    } catch (err) {
      setReply("❌ Unable to connect to AI Server.");
      console.log(err);
    }

    setLoading(false);
  }

  return (
    <div
      style={{
        maxWidth: "800px",
        margin: "40px auto",
        padding: "25px",
        background: "#1e293b",
        color: "white",
        borderRadius: "10px",
      }}
    >
      <h1>🤖 SafeRoute AI Assistant</h1>

      <p>
        Ask anything related to travel safety, routes, emergencies or crime
        hotspots.
      </p>

      <textarea
        rows="4"
        value={msg}
        onChange={(e) => setMsg(e.target.value)}
        placeholder="Example: How can I stay safe while travelling at night?"
        style={{
          width: "100%",
          padding: "12px",
          marginTop: "15px",
          borderRadius: "8px",
          fontSize: "16px",
        }}
      />

      <br />
      <br />

      <button
        onClick={askAI}
        disabled={loading}
        style={{
          padding: "12px 25px",
          background: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        {loading ? "Thinking..." : "Ask AI"}
      </button>

      {reply && (
        <div
          style={{
            marginTop: "25px",
            padding: "20px",
            background: "#0f172a",
            borderRadius: "10px",
            border: "1px solid gray",
          }}
        >
          <h3>🤖 AI Response</h3>

          <p>{reply}</p>
        </div>
      )}
    </div>
  );
}

export default Assistant;