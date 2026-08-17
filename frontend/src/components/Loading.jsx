import React from "react";

function Loading() {
  return (
    <div
      style={{
        height: "80vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          width: "60px",
          height: "60px",
          border: "6px solid #ddd",
          borderTop: "6px solid #2563eb",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
        }}
      />

      <p
        style={{
          marginTop: "20px",
          fontSize: "20px",
        }}
      >
        Loading...
      </p>

      <style>{`
        @keyframes spin{
          from{transform:rotate(0deg);}
          to{transform:rotate(360deg);}
        }
      `}</style>
    </div>
  );
}

export default Loading;