import React, { useState, useEffect } from "react";
import SearchBox from "../components/SearchBox";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  CircleMarker,
  useMapEvents,
} from "react-leaflet";

import L from "leaflet";

import {
  ShieldCheck,
  AlertTriangle,
  Route,
  Navigation,
  MapPinned,
  Clock,
} from "lucide-react";

import api from "../lib/api";

import "leaflet/dist/leaflet.css";

/* ---------------- Marker Fix ---------------- */

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",

  iconUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",

  shadowUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

/* ---------------- Map Click ---------------- */

function MapClickHandler({
  setDestination,
  setSelectedPoint,
  setShowReport,
}) {
  useMapEvents({
    click(e) {
      setDestination([
        e.latlng.lat,
        e.latlng.lng,
      ]);

      setSelectedPoint({
        lat: e.latlng.lat,
        lng: e.latlng.lng,
      });

      setShowReport(true);
    },
  });

  return null;
}

/* ================================================= */

function MapDashboard() {

  /* ---------------- States ---------------- */

  const [position, setPosition] = useState([
    28.6139,
    77.2090,
  ]);

  const [destination, setDestination] = useState([
    28.6239,
    77.2290,
  ]);

  const [routes, setRoutes] = useState([]);

  const [recommended, setRecommended] = useState(null);

  // NEW (used in Step 1)
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [journeyStarted, setJourneyStarted] = useState(false);

  const [watchId, setWatchId] = useState(null);

  const [currentPosition, setCurrentPosition] = useState(position);

  const [remainingDistance, setRemainingDistance] = useState(0);

  const [remainingTime, setRemainingTime] = useState(0);
  const [navigationStatus, setNavigationStatus] = useState("Ready");
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

const [currentInstruction, setCurrentInstruction] = useState("");

const [voiceEnabled, setVoiceEnabled] = useState(true);

const [journeyDistance, setJourneyDistance] = useState(0);

const [journeyStartTime, setJourneyStartTime] = useState(null);

  const [destinationReached, setDestinationReached] = useState(false);

  const [rerouting, setRerouting] = useState(false);

  const [incidents, setIncidents] = useState([]);

  const [loading, setLoading] = useState(false);

  const [travelMode, setTravelMode] = useState("walking");

  const [travelTime, setTravelTime] = useState("day");

  const [selectedPoint, setSelectedPoint] = useState(null);

  const [showReport, setShowReport] = useState(false);

  const [reportType, setReportType] = useState("Robbery");

  const [severity, setSeverity] = useState("medium");

  const [description, setDescription] = useState("");

  /* ---------------- Current Location ---------------- */

  useEffect(() => {

    if (!navigator.geolocation) {
      console.log("Geolocation not supported");
      return;
    }

    navigator.geolocation.getCurrentPosition(

      (pos) => {

        setPosition([
          pos.coords.latitude,
          pos.coords.longitude,
        ]);

      },

      (err) => {

        console.log("Location Error:", err);

      },

      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }

    );

  }, []);

  /* ---------------- Load Incidents ---------------- */

  useEffect(() => {

    loadIncidents();

  }, []);
/* ---------------- Load Incidents ---------------- */


/* ---------------- Load Incidents ---------------- */

async function loadIncidents() {

  try {

    const res = await api.get("/incidents");

    if (res.data.success) {

      setIncidents(res.data.incidents || []);

    } else {

      setIncidents([]);

    }

  }

  catch (err) {

    console.error("Incident Loading Error:", err);

    setIncidents([]);

  }

}

/* ---------------- Analyze Route ---------------- */

/* ---------------- Analyze Route ---------------- */

async function analyzeRoute() {

  setLoading(true);

  try {

    const res = await api.post(

      "/route/analyze",

      {

        source: {

          lat: position[0],

          lng: position[1]

        },

        destination: {

          lat: destination[0],

          lng: destination[1]

        },

        travel_mode: travelMode,

        travel_time: travelTime

      }

    );

    const data = res.data;

    if (!data.success) {

      alert("Unable to analyze route");

      return;

    }

    // Store all routes
    setRoutes(data.routes || []);

    // Store AI recommended route
    setRecommended(data.recommended || null);

    // Select recommended route by default
    setSelectedRoute(data.recommended || null);

  }

  catch (err) {

    console.error("Route Analysis Error:", err);

    if (err.response?.data?.detail) {

      alert(err.response.data.detail);

    }

    else {

      alert("Unable to analyze route");

    }

  }

  finally {

    setLoading(false);

  }

}
/* ---------------- Submit Report ---------------- */

/* ---------------- Submit Report ---------------- */

async function submitReport() {

  if (!selectedPoint) {

    alert("Please select a location on the map.");

    return;

  }

  if (!description.trim()) {

    alert("Please enter an incident description.");

    return;

  }

  try {

    const res = await api.post(

      "/report",

      {

        type: reportType,

        severity: severity,

        description: description,

        location: {

          lat: selectedPoint.lat,

          lng: selectedPoint.lng

        }

      }

    );

    if (res.data.success) {

      alert("Incident submitted successfully.");

      setShowReport(false);

      setDescription("");

      setReportType("Robbery");

      setSeverity("medium");

      setSelectedPoint(null);

      await loadIncidents();

    }

    else {

      alert("Unable to submit incident.");

    }

  }

  catch (err) {

    console.error("Report Error:", err);

    if (err.response?.data?.detail) {

      alert(err.response.data.detail);

    }

    else {

      alert("Unable to submit incident.");

    }

  }

}
function calculateDistance(lat1, lon1, lat2, lon2) {

  const R = 6371;

  const dLat = (lat2 - lat1) * Math.PI / 180;

  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a =

    Math.sin(dLat / 2) *

    Math.sin(dLat / 2) +

    Math.cos(lat1 * Math.PI / 180) *

    Math.cos(lat2 * Math.PI / 180) *

    Math.sin(dLon / 2) *

    Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;

}
function speakInstruction(text) {

  if (!voiceEnabled) return;

  if (!window.speechSynthesis) return;

  window.speechSynthesis.cancel();

  const speech = new SpeechSynthesisUtterance(text);

  speech.rate = 1;

  speech.pitch = 1;

  speech.lang = "en-US";

  window.speechSynthesis.speak(speech);

}
function updateNavigationInstruction(lat, lng) {

  if (!selectedRoute) return;

  const steps = selectedRoute.steps || [];

  if (steps.length === 0) return;

  if (currentStepIndex >= steps.length) return;

  const step = steps[currentStepIndex];

  if (!step.maneuver?.location) return;

  const stepLng = step.maneuver.location[0];

  const stepLat = step.maneuver.location[1];

  const distance = calculateDistance(

    lat,

    lng,

    stepLat,

    stepLng

  );

  if (distance < 0.03) {

    const instruction =

      step.maneuver.modifier

      ?

      `${step.maneuver.type} ${step.maneuver.modifier}`

      :

      step.maneuver.type;

    setCurrentInstruction(instruction);

    speakInstruction(instruction);

    setCurrentStepIndex(prev => prev + 1);

  }

}
function isOffRoute(lat, lng) {

  if (!selectedRoute) return false;

  const geometry = selectedRoute.geometry || [];

  let nearest = Infinity;

  geometry.forEach(point => {

    const d = calculateDistance(

      lat,

      lng,

      point.lat,

      point.lng

    );

    if (d < nearest) {

      nearest = d;

    }

  });

  // User is more than 100 meters away

  return nearest > 0.1;

}

function updateJourney(lat, lng) {

  if (!selectedRoute) return;

  setCurrentPosition([lat, lng]);
  updateNavigationInstruction(lat, lng);

  const distance = calculateDistance(

    lat,

    lng,

    destination[0],

    destination[1]

  );

  setRemainingDistance(distance.toFixed(2));
  setJourneyDistance(prev =>

Number(prev) + 0.01

);

  const avgSpeed =

    travelMode === "walking"

      ? 5

      : travelMode === "bike"

      ? 18

      : 40;

  const eta = (distance / avgSpeed) * 60;

  setRemainingTime(Math.round(eta));
  if (distance < 0.05) {

  setDestinationReached(true);

  setJourneyStarted(false);

  setNavigationStatus("Destination Reached");

  if (watchId !== null) {

    navigator.geolocation.clearWatch(watchId);

  }

  return;

}

if (isOffRoute(lat, lng)) {

    setNavigationStatus("Off Route");

    if (!rerouting) {

        rerouteJourney();

    }
  }

else {

  setNavigationStatus("On Route");

}

}
async function rerouteJourney() {

  if (rerouting) return;

  setRerouting(true);

  setNavigationStatus("Recalculating Route...");

  try {

    const res = await api.post(

      "/route/analyze",

      {

        source: {

          lat: currentPosition[0],

          lng: currentPosition[1]

        },

        destination: {

          lat: destination[0],

          lng: destination[1]

        },

        travel_mode: travelMode,

        travel_time: travelTime

      }

    );

    if (res.data.success) {

      setRoutes(res.data.routes);

      setRecommended(res.data.recommended);

      setSelectedRoute(res.data.recommended);

      setNavigationStatus("Route Updated");

    }

  }

  catch (err) {

    console.log(err);

    setNavigationStatus("Unable to reroute");

  }

  finally {

    setRerouting(false);

  }

}
function startJourney() {

  if (!selectedRoute) {

    alert("Please analyze route first.");

    return;

  }

  if (!navigator.geolocation) {

    alert("Geolocation not supported.");

    return;

  }

  const id = navigator.geolocation.watchPosition(

    (pos) => {

      updateJourney(

        pos.coords.latitude,

        pos.coords.longitude

      );

    },

    (err) => {

      console.log(err);

    },

    {

      enableHighAccuracy: true,

      maximumAge: 0,

      timeout: 5000

    }

  );

  setWatchId(id);

  setJourneyStarted(true);
  setJourneyStartTime(Date.now());

setJourneyDistance(0);

setCurrentStepIndex(0);

setCurrentInstruction("Navigation Started");

speakInstruction("Navigation Started");

}
function stopJourney() {

  if (watchId !== null) {

    navigator.geolocation.clearWatch(watchId);

  }

  setJourneyStarted(false);

}

/* ================= RETURN START ================= */

return(<div
style={{
display:"flex",
flexDirection:"column",
height:"100vh",
background:"#f3f4f6"
}}
>

{/* ================= Header ================= */}

<div
style={{
background:"#111827",
padding:"18px 30px",
color:"white",
display:"flex",
justifyContent:"space-between",
alignItems:"center"
}}
>

<div>

<h1
style={{
margin:0,
fontSize:"28px"
}}
>

🛡 SafeRoute AI

</h1>

<p
style={{
marginTop:"5px",
color:"#d1d5db"
}}
>

AI Powered Smart Navigation

</p>

</div>

<div
style={{
display:"flex",
gap:"15px"
}}
>

<button
style={{
padding:"10px 18px",
borderRadius:"8px",
border:"none",
background:"#2563eb",
color:"white",
cursor:"pointer"
}}
>

Dashboard

</button>

<button
style={{
padding:"10px 18px",
borderRadius:"8px",
border:"none",
background:"#10b981",
color:"white",
cursor:"pointer"
}}
>

Emergency

</button>

<button
style={{
padding:"10px 18px",
borderRadius:"8px",
border:"none",
background:"#f59e0b",
color:"white",
cursor:"pointer"
}}
>

AI Chat

</button>

</div>

</div>

{/* ================= Body ================= */}

<div
style={{
display:"flex",
flex:1
}}
>

{/* ================= Left Panel ================= */}

<div
style={{
width:"360px",
background:"white",
padding:"25px",
overflowY:"auto",
boxShadow:"0 2px 15px rgba(0,0,0,.1)"
}}
>

<h2>

<Route/>

 Route Planner

</h2>

<SearchBox

placeholder="Source"

onSelect={setPosition}

/>

<div
style={{
height:"15px"
}}
/>

<SearchBox

placeholder="Destination"

onSelect={setDestination}

/>

<div
style={{
marginTop:"25px"
}}
>

<label>

Travel Time

</label>

<select

value={travelTime}

onChange={(e)=>setTravelTime(e.target.value)}

style={{
width:"100%",
padding:"12px",
marginTop:"8px",
marginBottom:"18px"
}}
>

<option value="day">

Day

</option>

<option value="night">

Night

</option>

</select>

<label>

Travel Mode

</label>

<select

value={travelMode}

onChange={(e)=>setTravelMode(e.target.value)}

style={{
width:"100%",
padding:"12px",
marginTop:"8px"
}}
>

<option value="walking">

Walking

</option>

<option value="bike">

Bike

</option>

<option value="car">

Car

</option>

</select>

</div>

<button

onClick={analyzeRoute}

disabled={loading}

style={{

marginTop:"30px",

width:"100%",

padding:"15px",

background:"#2563eb",

color:"white",

border:"none",

borderRadius:"10px",

fontSize:"18px",

cursor:"pointer"

}}

>

{

loading

?

"Analyzing Routes..."

:

"Analyze Safe Route"

}

</button>
{

rerouting &&

<div

style={{

marginTop:"15px",

padding:"12px",

background:"#dbeafe",

color:"#1d4ed8",

border:"1px solid #93c5fd",

borderRadius:"10px",

textAlign:"center",

fontWeight:"bold"

}}

>

🔄 Recalculating safest route...

</div>

}
<button

onClick={

journeyStarted

?

stopJourney

:

startJourney

}

style={{

marginTop:"15px",

width:"100%",

padding:"15px",

background:

journeyStarted

?

"#dc2626"

:

"#16a34a",

color:"white",

border:"none",

borderRadius:"10px",

fontSize:"17px",

cursor:"pointer"

}}

>

{

journeyStarted

?

"Stop Journey"

:

"Start Journey"

}

</button>
<button

onClick={()=>

setVoiceEnabled(!voiceEnabled)

}

style={{

marginTop:"10px",

width:"100%",

padding:"12px",

background:

voiceEnabled

?

"#16a34a"

:

"#6b7280",

color:"white",

border:"none",

borderRadius:"10px",

cursor:"pointer"

}}

>

{

voiceEnabled

?

"🔊 Voice ON"

:

"🔇 Voice OFF"

}

</button>
{

recommended &&

<div

style={{

marginTop:"30px",

background:"#eff6ff",

padding:"20px",

borderRadius:"15px"

}}

>

<h3>

AI Recommended Route

</h3>

<p>

<Route size={18}/>

<b>

 {selectedRoute?.route_type}

</b>

</p>

<p>

<ShieldCheck size={18}/>

 Safety Score :

<b>

 {selectedRoute?.safety_score}

</b>

</p>

<p>

<AlertTriangle size={18}/>

 Risk :

<b>

 {selectedRoute?.risk_level}

</b>

</p>

</div>

}

</div>

{/* ================= Map Container ================= */}

<div
style={{
flex:1,
position:"relative"
}}
>

{

destinationReached &&

<div

style={{

position:"absolute",

top:"20px",

left:"50%",

transform:"translateX(-50%)",

background:"#16a34a",

color:"white",

padding:"15px 30px",

borderRadius:"12px",

fontWeight:"bold",

fontSize:"18px",

zIndex:9999,

boxShadow:"0 8px 20px rgba(0,0,0,.25)"

}}

>

🎉 Congratulations!

You have safely reached your destination.

</div>

}

<MapContainer

center={

journeyStarted

?

currentPosition

:

position

}

zoom={13}

style={{

height:"100%",

width:"100%"

}}

>

<TileLayer

url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

/>

<MapClickHandler

setDestination={setDestination}

setSelectedPoint={setSelectedPoint}

setShowReport={setShowReport}

/>

<Marker

position={

journeyStarted

?

currentPosition

:

position

}

>

<Popup>

📍 Current Location

</Popup>

</Marker>

<Marker position={destination}>

<Popup>

🎯 Destination

</Popup>

</Marker>

{/* ======= PART 3 STARTS HERE ======= */}
{/* ================= Crime Hotspots ================= */}

{
incidents.map((item,index)=>(

<CircleMarker

key={index}

center={[

item.location?.lat,

item.location?.lng

]}

radius={8}

pathOptions={{

color:

item.severity==="high"

?

"red"

:

item.severity==="medium"

?

"orange"

:

"green",

fillOpacity:0.8

}}

>

<Popup>

<h3>{item.type}</h3>

<p>

<b>Severity :</b>

{item.severity || "Unknown"}

</p>

<p>

{item.description || "No description"}

</p>

</Popup>

</CircleMarker>

))
}

{/* ================= Route Lines ================= */}

{/* ================= Route Lines ================= */}

{

routes.map((route,index)=>(

<Polyline

key={index}

positions={

(route.geometry || []).map(point => [

point.lat,

point.lng

])

}

color={

selectedRoute &&

selectedRoute.route_type===route.route_type

?

"#2563eb"

:

index===1

?

"#16a34a"

:

"#6b7280"

}

weight={

selectedRoute &&

selectedRoute.route_type===route.route_type

?

8

:

4

}

opacity={

selectedRoute &&

selectedRoute.route_type===route.route_type

?

1

:

0.7

}

eventHandlers={{

click:()=>{

setSelectedRoute(route);

}

}}

/>

))

}
</MapContainer>

{/* ================= Floating Map Info ================= */}

<div

style={{

position:"absolute",

bottom:"25px",

right:"25px",

background:"white",

padding:"18px",

borderRadius:"15px",

boxShadow:"0 8px 25px rgba(0,0,0,.15)",

width:"270px",

zIndex:999

}}

>

<h3
style={{
marginBottom:"15px"
}}
>

<Navigation/>

 Navigation Summary

</h3>

{

journeyStarted &&

<>

<p>

Remaining Distance

<b>

{remainingDistance} km

</b>

</p>

<p>

ETA

<b>

{remainingTime} min

</b>

</p>

</>

}

<p>

<MapPinned size={18}/>

 Destination Selected

</p>

<p>

<Clock size={18}/>

 Mode :

<b>

 {travelMode}

</b>

</p>

<p>

Time :

<b>

 {travelTime}

</b>

</p>

{

selectedRoute &&

<>

<p>

<ShieldCheck size={18}/>

 Safety :

<b>

{selectedRoute.safety_score}%

</b>

</p>

<p>

<Route size={18}/>

 Distance :

<b>

{selectedRoute.distance_km} km

</b>

</p>

<p>

<Clock size={18}/>

 ETA :

<b>

{selectedRoute.time_min} min

</b>

</p>

{

journeyStarted &&

<>

<p>

📍 Remaining Distance :

<b>

 {remainingDistance} km

</b>

</p>

<p>

⏱ Remaining ETA :

<b>

 {remainingTime} min

</b>

</p>

<p>

🛰 Status :

<b>

{

destinationReached

?

"Destination Reached"

:

navigationStatus

}

</b>

</p>

</>

}

</>

}
</div>

</div>

{/* ================= PART 3B STARTS HERE ================= */}
{/* ================= Available Routes ================= */}

</div>

{
routes.length>0 &&

<div
style={{
padding:"25px",
background:"#ffffff"
}}
>

<h2>

🗺 Available Routes

</h2>
<div

style={{

display:"flex",

gap:"15px",

marginBottom:"25px",

flexWrap:"wrap"

}}

>

<div>

🔵 Selected Route

</div>

<div>

🟢 Alternative

</div>

<div>

⚪ Other Route

</div>

</div>
<p
style={{
color:"#6b7280",
marginBottom:"25px"
}}
>

Click any route to preview it on the map.

</p>

{
routes.map((route,index)=>(

<div

key={index}

onClick={()=>setSelectedRoute(route)}

style={{

cursor:"pointer",

border:

selectedRoute &&
selectedRoute.route_type===route.route_type

?

"2px solid #2563eb"

:

"1px solid #d1d5db",

background:

selectedRoute &&
selectedRoute.route_type===route.route_type

?

"#eff6ff"

:

"#ffffff",

padding:"20px",

marginBottom:"18px",

borderRadius:"16px",

boxShadow:"0 5px 15px rgba(0,0,0,.08)",

transition:"0.3s"

}}

>

<div

style={{

display:"flex",

justifyContent:"space-between",

alignItems:"center",

marginBottom:"12px"

}}

>

<h3
style={{margin:0}}
>

🚗 {route.route_type}

</h3>
{

selectedRoute &&
selectedRoute.route_type===route.route_type &&

<span
style={{
marginLeft:"10px"
}}
>

✅

</span>

}

{

recommended &&
recommended.route_type===route.route_type &&

<span

style={{

background:"#2563eb",

color:"white",

padding:"6px 12px",

borderRadius:"20px",

fontSize:"13px",

fontWeight:"bold"

}}

>

AI Recommended

</span>

}

</div>

<div

style={{

display:"grid",

gridTemplateColumns:"1fr 1fr",

gap:"12px",

marginBottom:"15px"

}}

>

<div>

📏 Distance

<br/>

<b>

{route.distance_km} km

</b>

</div>

<div>

⏱ ETA

<br/>

<b>

{route.time_min} min

</b>

</div>

<div>

🛡 Safety

<br/>

<b>

{route.safety_score}%

</b>

</div>

<div>

⚠ Risk

<br/>

<b>

{route.risk_level}

</b>

</div>

</div>

{

route.reasons &&
route.reasons.length>0 &&

<>

<h4
style={{
marginBottom:"10px"
}}
>

Why this score?

</h4>

<ul
style={{

paddingLeft:"20px",

margin:0

}}
>

{

route.reasons.map((reason,i)=>(

<li

key={i}

style={{

marginBottom:"6px"

}}

>

{reason}

</li>

))

}

</ul>

</>

}

</div>

))
}

</div>

}

{/* ================= Incident Report Modal ================= */}

{

showReport &&

<div

style={{

position:"fixed",

top:0,

left:0,

width:"100%",

height:"100%",

background:"rgba(0,0,0,.45)",

display:"flex",

justifyContent:"center",

alignItems:"center",

zIndex:9999

}}

>

<div

style={{

width:"420px",

background:"white",

padding:"25px",

borderRadius:"15px"

}}

>

<h2>

🚨 Report Incident

</h2>

<select

value={reportType}

onChange={(e)=>setReportType(e.target.value)}

style={{

width:"100%",

padding:"12px",

marginTop:"15px"

}}

>

<option>Robbery</option>

<option>Accident</option>

<option>Harassment</option>

<option>Suspicious Activity</option>

<option>Other</option>

</select>

<select

value={severity}

onChange={(e)=>setSeverity(e.target.value)}

style={{

width:"100%",

padding:"12px",

marginTop:"15px"

}}

>

<option value="low">

Low

</option>

<option value="medium">

Medium

</option>

<option value="high">

High

</option>

</select>

<textarea

value={description}

onChange={(e)=>setDescription(e.target.value)}

rows={4}

placeholder="Description"

style={{

width:"100%",

padding:"12px",

marginTop:"15px",

resize:"none"

}}

></textarea>

<div

style={{

display:"flex",

justifyContent:"space-between",

marginTop:"20px"

}}

>

<button

onClick={()=>setShowReport(false)}

style={{

padding:"12px 20px",

border:"none",

background:"#6b7280",

color:"white",

borderRadius:"8px"

}}

>

Cancel

</button>

<button

onClick={submitReport}

style={{

padding:"12px 20px",

border:"none",

background:"#2563eb",

color:"white",

borderRadius:"8px"

}}

>

Submit

</button>

</div>

</div>

</div>

}

</div>

);

}

export default MapDashboard;