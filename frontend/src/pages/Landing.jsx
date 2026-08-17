import React from "react";
import { Link } from "react-router-dom";

function Landing() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "30px",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          width: "100%",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "50px",
          flexWrap: "wrap",
        }}
      >
        {/* Left */}

        <div style={{ flex: 1, minWidth: "320px" }}>
          <h1
            style={{
              color: "white",
              fontSize: "60px",
              marginBottom: "20px",
            }}
          >
            🛡 SafeRoute AI
          </h1>

          <h2
            style={{
              color: "#bfdbfe",
              fontSize: "32px",
              marginBottom: "25px",
            }}
          >
            AI Powered Smart & Safe Navigation
          </h2>

          <p
            style={{
              color: "white",
              lineHeight: "32px",
              fontSize: "20px",
            }}
          >
            Navigate through the safest routes using Artificial
            Intelligence, crime hotspot detection, emergency SOS,
            and an intelligent safety assistant.
          </p>

          <div
            style={{
              marginTop: "40px",
              display: "flex",
              gap: "20px",
            }}
          >
            <Link to="/login">
              <button
                style={{
                  padding: "15px 35px",
                  borderRadius: "10px",
                  border: "none",
                  background: "#22c55e",
                  color: "white",
                  fontSize: "18px",
                  cursor: "pointer",
                }}
              >
                Get Started
              </button>
            </Link>

            <Link to="/register">
              <button
                style={{
                  padding: "15px 35px",
                  borderRadius: "10px",
                  border: "2px solid white",
                  background: "transparent",
                  color: "white",
                  fontSize: "18px",
                  cursor: "pointer",
                }}
              >
                Register
              </button>
            </Link>
          </div>
        </div>

        {/* Right */}

        <div
          style={{
            flex: 1,
            minWidth: "320px",
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              width: "420px",
              background: "rgba(255,255,255,.12)",
              backdropFilter: "blur(15px)",
              padding: "30px",
              borderRadius: "20px",
              color: "white",
              boxShadow: "0 15px 40px rgba(0,0,0,.3)",
            }}
          >
            <h2>✨ Features</h2>

            <hr />

            <p>🗺 AI Safe Route Recommendation</p>

            <p>🚨 Emergency SOS</p>

            <p>🤖 AI Safety Assistant</p>

            <p>📍 Crime Hotspot Detection</p>

            <p>👤 User Dashboard</p>

            <p>📊 Admin Analytics</p>

            <p>📱 Fully Responsive</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Landing;