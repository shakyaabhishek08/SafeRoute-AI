import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Bot,
  ShieldAlert,
  User,
  Settings,
  LogOut,
} from "lucide-react";

function Navbar() {

  const location = useLocation();
  const navigate = useNavigate();

  const user =
    JSON.parse(localStorage.getItem("user")) || {};

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  }

  const linkStyle = (path) => ({
    display: "flex",
    alignItems: "center",
    gap: "8px",
    textDecoration: "none",
    color:
      location.pathname === path
        ? "#2563eb"
        : "#374151",
    fontWeight:
      location.pathname === path
        ? "600"
        : "500",
    padding: "8px 12px",
    borderRadius: "8px",
    transition: "0.3s",
  });

  return (
    <nav
      style={{
        width: "100%",
        background: "#ffffff",
        boxShadow: "0 2px 10px rgba(0,0,0,.08)",
        padding: "15px 30px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        position: "sticky",
        top: 0,
        zIndex: 1000,
      }}
    >
      {/* Logo */}

      <Link
        to="/dashboard"
        style={{
          textDecoration: "none",
          color: "#111827",
          fontSize: "26px",
          fontWeight: "bold",
        }}
      >
        🛡 SafeRoute AI
      </Link>

      {/* Navigation */}

      <div
        style={{
          display: "flex",
          gap: "18px",
          alignItems: "center",
        }}
      >
        <Link
          to="/dashboard"
          style={linkStyle("/dashboard")}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </Link>

        <Link
          to="/chat"
          style={linkStyle("/chat")}
        >
          <Bot size={18} />
          AI Chat
        </Link>

        <Link
          to="/emergency"
          style={linkStyle("/emergency")}
        >
          <ShieldAlert size={18} />
          Emergency
        </Link>

        <Link
          to="/profile"
          style={linkStyle("/profile")}
        >
          <User size={18} />
          Profile
        </Link>

        <Link
          to="/admin"
          style={linkStyle("/admin")}
        >
          <Settings size={18} />
          Admin
        </Link>
      </div>

      {/* Right Side */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "15px",
        }}
      >
        <div
          style={{
            textAlign: "right",
          }}
        >
          <div
            style={{
              fontWeight: "600",
            }}
          >
            {user.name || "Guest"}
          </div>

          <div
            style={{
              fontSize: "13px",
              color: "#6b7280",
            }}
          >
            {user.email || ""}
          </div>
        </div>

        <button
          onClick={logout}
          style={{
            background: "#ef4444",
            color: "white",
            border: "none",
            padding: "10px 15px",
            borderRadius: "8px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "6px",
          }}
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;