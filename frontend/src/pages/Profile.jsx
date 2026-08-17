import React, { useEffect, useState } from "react";
import api from "../lib/api";

import {
  User,
  Shield,
  Route,
  AlertTriangle,
  Phone,
} from "lucide-react";

import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";

function Profile() {

  /* ---------------- State ---------------- */

  const [user, setUser] = useState({});

  const [journeys, setJourneys] = useState([]);

  const [incidents, setIncidents] = useState([]);

  const [loading, setLoading] = useState(true);

  /* ---------------- Load Data ---------------- */

  useEffect(()=>{

loadData();

// eslint-disable-next-line react-hooks/exhaustive-deps

},[]);

  async function loadData() {

    try {

      const [

        userRes,

        journeyRes,

        incidentRes,

      ] = await Promise.all([

        api.get("/auth/me"),

        api.get("/history"),

        api.get("/incidents"),

      ]);

      setUser(userRes.data.user || {});

      setJourneys(journeyRes.data.history || []);

      setIncidents(incidentRes.data.incidents || []);

    }

    catch (err) {

      console.log(err);

    }

    finally{

setLoading(false);

}

  }

  /* ---------------- Chart Data ---------------- */

  const pieData = [

    {

      name: "Journeys",

      value: journeys.length,

    },

    {

      name: "Reports",

      value: incidents.length,

    },

    {

      name: "Contacts",

      value:

        user.emergency_contacts?.length || 0,

    },

  ];

  const COLORS = [

    "#2563eb",

    "#dc2626",

    "#10b981",

  ];

  const barData = [

    {

      name: "Journeys",

      value: journeys.length,

    },

    {

      name: "Reports",

      value: incidents.length,

    },

    {

      name: "Contacts",

      value:

        user.emergency_contacts?.length || 0,

    },

  ];

  if (loading) {

    return (

      <div
        style={{
          padding: "50px",
          textAlign: "center",
          fontSize: "22px",
        }}
      >

        Loading Profile...

      </div>

    );

  }

  return (
    <div
      style={{
        padding: "30px",
        background: "#f3f4f6",
        minHeight: "100vh",
      }}
    >
{/* ================= Header ================= */}

<div
  style={{
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    marginBottom: "30px",
  }}
>
  <div>
    <h1
      style={{
        fontSize: "38px",
        marginBottom: "8px",
      }}
    >
      👤 User Profile
    </h1>

    <p
      style={{
        color: "#6b7280",
        fontSize: "18px",
      }}
    >
      Welcome back to SafeRoute AI
    </p>
  </div>

  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "20px",
      background: "white",
      padding: "20px",
      borderRadius: "15px",
      boxShadow: "0 5px 20px rgba(0,0,0,.08)",
    }}
  >
    <div
      style={{
        width: "70px",
        height: "70px",
        borderRadius: "50%",
        background: "#2563eb",
        color: "white",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontSize: "28px",
        fontWeight: "bold",
      }}
    >
      {user.name?.charAt(0).toUpperCase() || "U"}
    </div>

    <div>
      <h2 style={{ margin: 0 }}>{user.name}</h2>

      <p style={{ margin: "5px 0" }}>
        {user.email || "--"}
      </p>

      <p
        style={{
          color: "#10b981",
          fontWeight: "bold",
        }}
      >
        {user.role || "User"}
      </p>
    </div>
  </div>
</div>

{/* ================= Statistics ================= */}

<div
  style={{
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit,minmax(220px,1fr))",
    gap: "20px",
    marginBottom: "35px",
  }}
>
  <StatCard
    title="Journeys"
    value={journeys.length}
    color="#2563eb"
    icon={<Route size={32} />}
  />

  <StatCard
    title="Reports"
    value={incidents.length}
    color="#dc2626"
    icon={<AlertTriangle size={32} />}
  />

  <StatCard
    title="Contacts"
    value={
      Array.isArray(user.emergency_contacts)
? user.emergency_contacts.length
:0
    }
    color="#10b981"
    icon={<Phone size={32} />}
  />

  <StatCard
    title="Role"
    value={user.role}
    color="#7c3aed"
    icon={<Shield size={32} />}
  />
</div>

{/* ================= Charts ================= */}

<div
  style={{
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit,minmax(420px,1fr))",
    gap: "25px",
    marginBottom: "40px",
  }}
>
  <div
    style={{
      background: "white",
      padding: "25px",
      borderRadius: "15px",
      boxShadow:
        "0 5px 20px rgba(0,0,0,.08)",
      height: "360px",
    }}
  >
    <h2
      style={{
        marginBottom: "20px",
      }}
    >
      Activity Overview
    </h2>

    <ResponsiveContainer
      width="100%"
      height="100%"
    >
      <PieChart>
        <Pie
          data={pieData}
          dataKey="value"
          outerRadius={110}
          label
        >
          {pieData.map((entry, index) => (
            <Cell
              key={index}
              fill={
                COLORS[
                  index % COLORS.length
                ]
              }
            />
          ))}
        </Pie>

        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  </div>

  <div
    style={{
      background: "white",
      padding: "25px",
      borderRadius: "15px",
      boxShadow:
        "0 5px 20px rgba(0,0,0,.08)",
      height: "360px",
    }}
  >
    <h2
      style={{
        marginBottom: "20px",
      }}
    >
      Statistics
    </h2>

    <ResponsiveContainer
      width="100%"
      height="100%"
    >
      <BarChart data={barData}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="name" />

        <YAxis />

        <Tooltip />

        <Legend />

        <Bar
          dataKey="value"
          fill="#2563eb"
        />
      </BarChart>
    </ResponsiveContainer>
  </div>
</div>

{/* ================= PART 3 STARTS HERE ================= */}
{/* ================= Emergency Contacts ================= */}

<div
  style={{
    background: "white",
    padding: "25px",
    borderRadius: "15px",
    boxShadow: "0 5px 20px rgba(0,0,0,.08)",
    marginBottom: "35px",
  }}
>
  <h2 style={{ marginBottom: "20px" }}>
    ❤️ Emergency Contacts
  </h2>

  {user.emergency_contacts?.length === 0 ? (
    <p>No emergency contacts added.</p>
  ) : (
    user.emergency_contacts.map((contact, index) => (
      <InfoCard key={index}>
        <h3>👤 Emergency Contact</h3>

<p>📞 {typeof contact === "string" ? contact : contact.phone}</p>

<a
href={`tel:${
typeof contact==="string"
? contact
: contact.phone
}`}
>
          Call Now
        </a>
      </InfoCard>
    ))
  )}
</div>

{/* ================= Journey History ================= */}

<div
  style={{
    background: "white",
    padding: "25px",
    borderRadius: "15px",
    boxShadow: "0 5px 20px rgba(0,0,0,.08)",
    marginBottom: "35px",
  }}
>
  <h2 style={{ marginBottom: "20px" }}>
    🚶 Journey History
  </h2>

  {journeys.length === 0 ? (
    <p>No journeys available.</p>
  ) : (
    journeys.map((journey, index) => (
      <InfoCard key={index}>
        <h3>
          {journey.recommended_route}
        </h3>

        <p>

          <b>Safety :</b>

         {journey.safety_score}%

        </p>

        <p>

          <b>Distance :</b>

          {journey.distance_km} km

        </p>

        <p>

          <b>Source :</b>

          {journey.source?.lat},

          {journey.source?.lng}

        </p>

        <p>

          <b>Destination :</b>

          {journey.destination?.lat},

          {journey.destination?.lng}

        </p>

      </InfoCard>
    ))
  )}
</div>

{/* ================= Incident History ================= */}

<div
  style={{
    background: "white",
    padding: "25px",
    borderRadius: "15px",
    boxShadow: "0 5px 20px rgba(0,0,0,.08)",
    marginBottom: "35px",
  }}
>
  <h2 style={{ marginBottom: "20px" }}>
    🚨 Incident Reports
  </h2>

  {incidents.length === 0 ? (
    <p>No incidents reported.</p>
  ) : (
    incidents.map((incident, index) => (
      <InfoCard key={index}>
        <h3>

          {incident.type}

        </h3>

        <p>

          <b>Severity :</b>

          {incident.severity}

        </p>

        <p>

          {incident.description}

        </p>

        {incident.location && (

          <p>

            📍

            {incident.location.lat},

            {incident.location.lng}

          </p>

        )}

      </InfoCard>
    ))
  )}
</div>
</div>

);

}
{/* ================= PART 4 STARTS HERE ================= */}
function StatCard({ title, value, color, icon }) {

  return (

    <div
      style={{
        background: "white",
        borderRadius: "15px",
        padding: "25px",
        boxShadow: "0 5px 20px rgba(0,0,0,.08)",
        borderLeft: `6px solid ${color}`,
      }}
    >

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >

        <div>

          <h3
            style={{
              color: "#6b7280",
              marginBottom: "10px",
            }}
          >
            {title}
          </h3>

          <h1
            style={{
              margin: 0,
              color: color,
              fontSize: "38px",
            }}
          >
            {value}
          </h1>

        </div>

        <div
          style={{
            color: color,
          }}
        >
          {icon}
        </div>

      </div>

    </div>

  );

}

function InfoCard({ children }) {

  return(

    <div
      style={{
        padding: "18px",
        marginBottom: "15px",
        borderRadius: "12px",
        background: "#f9fafb",
        border: "1px solid #e5e7eb",
      }}
    >

      {children}

    </div>

  );

}


export default Profile;