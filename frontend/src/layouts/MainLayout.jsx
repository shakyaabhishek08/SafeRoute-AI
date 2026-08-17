import React from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

function MainLayout({ children }) {
  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#f3f4f6",
      }}
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Right Section */}
      <div
        style={{
          flex: 1,
          marginLeft: "250px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Navbar */}
        <Navbar />

        {/* Main Content */}
        <div
          style={{
            padding: "25px",
            flex: 1,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

export default MainLayout;