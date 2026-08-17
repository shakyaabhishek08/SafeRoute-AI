import React, { useEffect, useState } from "react";
import api from "../lib/api";

import {

BarChart,
Bar,
PieChart,
Pie,
Cell,
ResponsiveContainer,
Tooltip,
CartesianGrid,
XAxis,
YAxis,
Legend

} from "recharts";

import {

Users,
Route,
AlertTriangle,
ShieldCheck,
RefreshCcw

} from "lucide-react";

function AdminDashboard(){

const [users,setUsers]=useState([]);

const [journeys,setJourneys]=useState([]);

const [incidents,setIncidents]=useState([]);

const [loading,setLoading]=useState(true);
const [error,setError]=useState("");

useEffect(()=>{

loadDashboard();

},[]);

async function loadDashboard(){

try{

const [

userRes,

journeyRes,

incidentRes

]=await Promise.all([

api.get("/admin/users"),

api.get("/history"),

api.get("/incidents")

]);

setUsers(userRes.data.data || []);

setJourneys(journeyRes.data.history || []);

setIncidents(incidentRes.data.incidents || []);

}

catch(err){

console.log(err);
setError("Unable to load dashboard.");

}

finally{

setLoading(false);

}
}

const pieData=[

{

name:"Users",

value:users.length

},

{

name:"Journeys",

value:journeys.length

},

{

name:"Reports",

value:incidents.length

}

];

const COLORS=[

"#2563eb",

"#22c55e",

"#ef4444"

];

if(loading){

return(

<div

style={{

padding:"80px",

textAlign:"center",

fontSize:"25px"

}}

>

Loading Dashboard...

</div>

);

}

return(

<div

style={{

padding:"30px",

background:"#f3f4f6",

minHeight:"100vh"

}}

>
{/* ================= Header ================= */}

<div
style={{
display:"flex",
justifyContent:"space-between",
alignItems:"center",
marginBottom:"30px",
flexWrap:"wrap"
}}
>

<div>

<h1
style={{
fontSize:"36px",
marginBottom:"5px"
}}
>

📊 Admin Dashboard

</h1>

<p
style={{
color:"#6b7280"
}}
>

SafeRoute AI Analytics Panel

</p>

</div>

<button

onClick={loadDashboard}

style={{

display:"flex",

alignItems:"center",

gap:"8px",

padding:"12px 18px",

background:"#2563eb",

color:"white",

border:"none",

borderRadius:"10px",

cursor:"pointer"

}}

>

<RefreshCcw size={18}/>

Refresh

</button>

</div>

{/* ================= Statistics ================= */}

<div
style={{
display:"grid",
gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",
gap:"20px",
marginBottom:"35px"
}}
>

<StatCard

title="Users"

value={users.length}

color="#2563eb"

icon={<Users size={34}/>}

/>

<StatCard

title="Journeys"

value={journeys.length}

color="#22c55e"

icon={<Route size={34}/>}

/>

<StatCard

title="Reports"

value={incidents.length}

color="#ef4444"

icon={<AlertTriangle size={34}/>}

/>

<StatCard

title="System"

value="Online"

color="#7c3aed"

icon={<ShieldCheck size={34}/>}

/>

</div>

{/* ================= Charts ================= */}

<div
style={{
display:"grid",
gridTemplateColumns:"repeat(auto-fit,minmax(450px,1fr))",
gap:"25px",
marginBottom:"35px"
}}
>

<div
style={{
background:"white",
padding:"25px",
borderRadius:"15px",
boxShadow:"0 5px 20px rgba(0,0,0,.08)",
height:"360px"
}}
>

<h2>

Platform Overview

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

{

pieData.map((item,index)=>(

<Cell

key={index}

fill={COLORS[index]}

/>

))

}

</Pie>

<Tooltip/>

</PieChart>

</ResponsiveContainer>

</div>

<div
style={{
background:"white",
padding:"25px",
borderRadius:"15px",
boxShadow:"0 5px 20px rgba(0,0,0,.08)",
height:"360px"
}}
>

<h2>

Platform Statistics

</h2>

<ResponsiveContainer
width="100%"
height="100%"
>

<BarChart
data={pieData}
>

<CartesianGrid strokeDasharray="3 3"/>

<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Legend/>

<Bar

dataKey="value"

fill="#2563eb"

/>

</BarChart>

</ResponsiveContainer>

</div>

</div>

{/* ================= PART 3 STARTS HERE ================= */}
{/* ================= Users Table ================= */}

<div
style={{
background:"white",
padding:"25px",
borderRadius:"15px",
boxShadow:"0 5px 20px rgba(0,0,0,.08)",
marginBottom:"30px"
}}
>

<h2
style={{
marginBottom:"20px"
}}
>

👥 Registered Users

</h2>

<div
style={{
overflowX:"auto"
}}
>

<table
style={{
width:"100%",
borderCollapse:"collapse"
}}
>

<thead>

<tr
style={{
background:"#2563eb",
color:"white"
}}
>

<th style={thStyle}>Name</th>

<th style={thStyle}>Email</th>

<th style={thStyle}>Role</th>

</tr>

</thead>

<tbody>

{

users.length===0

?

<tr>

<td
colSpan="3"
style={tdStyle}
>

No Users Found

</td>

</tr>

:

users.map((user,index)=>(

<tr key={index}>

<td style={tdStyle}>{user.name || "--"}</td>

<td style={tdStyle}>{user.email || "--"}</td>

<td style={tdStyle}>{user.role || "User"}</td>

</tr>

))

}

</tbody>

</table>

</div>

</div>

{/* ================= Journey History ================= */}

<div
style={{
background:"white",
padding:"25px",
borderRadius:"15px",
boxShadow:"0 5px 20px rgba(0,0,0,.08)",
marginBottom:"30px"
}}
>

<h2
style={{
marginBottom:"20px"
}}
>

🚶 Journey History

</h2>

{

journeys.length===0

?

<p>No Journey Available</p>

:

journeys.map((item,index)=>(

<div

key={item._id}

style={{

padding:"15px",

border:"1px solid #ddd",

borderRadius:"10px",

marginBottom:"15px"

}}

>

<h3>

{item.recommended_route}

</h3>

<p>

Safety :

<b>

 {item.safety_score}%

</b>

</p>

<p>

Distance :

<b>

 {item.distance_km} km

</b>

</p>

</div>

))

}

</div>

{/* ================= Incident Reports ================= */}

<div
style={{
background:"white",
padding:"25px",
borderRadius:"15px",
boxShadow:"0 5px 20px rgba(0,0,0,.08)",
marginBottom:"30px"
}}
>

<h2
style={{
marginBottom:"20px"
}}
>

🚨 Incident Reports

</h2>

{

incidents.length===0

?

<p>

No Incident Reports

</p>

:

incidents.map((incident,index)=>(

<div

key={incident._id}

style={{

padding:"15px",

border:"1px solid #ddd",

borderRadius:"10px",

marginBottom:"15px",

display:"flex",

justifyContent:"space-between",

alignItems:"center"

}}

>

<div>

<h3>

{incident.type}

</h3>

<p>

Severity :

<b>

{incident.severity}

</b>

</p>

<p>

{incident.description}

</p>

</div>

<button

style={{

background:"#ef4444",

color:"white",

border:"none",

padding:"10px 18px",

borderRadius:"8px",

cursor:"pointer"

}}

onClick={()=>alert("Delete API will be added")}

>

Delete

</button>

</div>

))

}

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

          <p
            style={{
              color: "#6b7280",
              marginBottom: "10px",
              fontSize: "18px",
            }}
          >
            {title}
          </p>

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

const thStyle = {
  padding: "12px",
  textAlign: "left",
};

const tdStyle = {
  padding: "12px",
  borderBottom: "1px solid #e5e7eb",
};


export default AdminDashboard;