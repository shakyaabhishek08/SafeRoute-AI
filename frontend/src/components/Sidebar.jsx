import React from "react";
import { NavLink } from "react-router-dom";
import {
  Home,
  Bot,
  ShieldAlert,
  User,
  Settings,
  History,
  MapPinned,
} from "lucide-react";

function Sidebar() {

  const menu = [

    {
      name: "Dashboard",
      path: "/dashboard",
      icon: <Home size={20} />,
    },

    {
      name: "AI Chat",
      path: "/chat",
      icon: <Bot size={20} />,
    },

    {
      name: "Emergency",
      path: "/emergency",
      icon: <ShieldAlert size={20} />,
    },

    {
      name: "History",
      path: "/history",
      icon: <History size={20} />,
    },

    {
      name: "Profile",
      path: "/profile",
      icon: <User size={20} />,
    },

    {
      name: "Admin",
      path: "/admin",
      icon: <Settings size={20} />,
    }

  ];

  return (

    <div
      style={{
        width: "250px",
        height: "100vh",
        background: "#111827",
        color: "white",
        display: "flex",
        flexDirection: "column",
        position: "fixed",
        left: 0,
        top: 0,
      }}
    >

      <div
        style={{
          padding: "30px",
          borderBottom: "1px solid #374151",
        }}
      >

        <h2
          style={{
            margin: 0,
          }}
        >

          🛡 SafeRoute

        </h2>

        <p
          style={{
            color: "#9ca3af",
            fontSize: "13px",
            marginTop: "8px",
          }}
        >

          AI Navigation System

        </p>

      </div>

      <div
        style={{
          flex: 1,
          padding: "20px 15px",
        }}
      >

        {

          menu.map((item) => (

            <NavLink

              key={item.path}

              to={item.path}

              style={({ isActive }) => ({

                display: "flex",

                alignItems: "center",

                gap: "12px",

                padding: "14px 18px",

                marginBottom: "10px",

                borderRadius: "10px",

                textDecoration: "none",

                color: "white",

                background: isActive
                  ? "#2563eb"
                  : "transparent",

                transition: ".3s",

              })}

            >

              {item.icon}

              {item.name}

            </NavLink>

          ))

        }

      </div>

      <div
        style={{
          padding: "20px",
          borderTop: "1px solid #374151",
          color: "#9ca3af",
          fontSize: "13px",
        }}
      >

        <MapPinned size={18} />

        <span
          style={{
            marginLeft: "10px",
          }}
        >

          SafeRoute AI v1.0

        </span>

      </div>

    </div>

  );

}

export default Sidebar;