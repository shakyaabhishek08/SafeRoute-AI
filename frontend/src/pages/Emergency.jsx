import React, { useState, useEffect } from "react";
import api from "../lib/api";

function Emergency() {

  const [location, setLocation] = useState(null);

  const [contacts, setContacts] = useState([]);

  const [name, setName] = useState("");

  const [phone, setPhone] = useState("");

  useEffect(() => {

    const watchId = navigator.geolocation.watchPosition(

      (pos) => {

        setLocation({

          lat: pos.coords.latitude,

          lng: pos.coords.longitude

        });

      },

      (err) => {

        console.log(err);

      },

      {

        enableHighAccuracy: true,

        maximumAge: 1000

      }

    );

    loadContacts();

    return () => {

      navigator.geolocation.clearWatch(watchId);

    };

  }, []);

  async function loadContacts() {

    try {

      const res = await api.get("/auth/me");

      if (res.data.emergency_contacts) {

        setContacts(res.data.emergency_contacts);

      }

    }

    catch (err) {

      console.log(err);

    }

  }

  async function addContact() {

    if (name === "" || phone === "") {

      alert("Fill all fields");

      return;

    }

    const newContacts = [

      ...contacts,

      {

        name,

        phone

      }

    ];

    try {

      const res = await api.put(

        "/auth/emergency-contacts",

        {

          contacts: newContacts

        }

      );

      setContacts(res.data.contacts);

      setName("");

      setPhone("");

    }

    catch (err) {

      console.log(err);

    }

  }

  function triggerSOS() {

    if (!location) {

      alert("Location unavailable");

      return;

    }

    if (navigator.vibrate) {

      navigator.vibrate([300, 200, 300, 200, 300]);

    }

    const audio = new Audio(

      "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg"

    );

    audio.play();

    const url =

      `https://maps.google.com/?q=${location.lat},${location.lng}`;

    alert(

`🚨 SOS ACTIVATED

Location Shared

${url}`

    );

  }

  function shareLocation() {

    if (!location) return;

    const url =

      `https://maps.google.com/?q=${location.lat},${location.lng}`;

    if (navigator.share) {

      navigator.share({

        title: "Emergency Location",

        text: "I need help. Here is my location.",

        url

      });

    }

    else {

      navigator.clipboard.writeText(url);

      alert("Location copied to clipboard.");

    }

  }

  const pulseStyle = `

  @keyframes pulse{

      0%{

          transform:scale(1);

      }

      50%{

          transform:scale(1.08);

      }

      100%{

          transform:scale(1);

      }

  }

  `;

  return (

<div
style={{
padding:"30px",
maxWidth:"900px",
margin:"auto"
}}
>

<style>{pulseStyle}</style>

<h1>

🚨 Emergency SOS

</h1>

<br/>

<button

onClick={triggerSOS}

style={{

width:"220px",

height:"220px",

borderRadius:"50%",

background:"#dc2626",

color:"white",

fontSize:"45px",

fontWeight:"bold",

border:"none",

cursor:"pointer",

animation:"pulse 1s infinite"

}}

>

SOS

</button>

<br/><br/>

<button

onClick={shareLocation}

style={{

padding:"12px 20px",

marginRight:"10px",

cursor:"pointer"

}}

>

Share Location

</button>

{

location &&

<div>

<p>

<b>Latitude :</b>

{location.lat}

</p>

<p>

<b>Longitude :</b>

{location.lng}

</p>

</div>

}

<hr/>

<h2>

Emergency Contacts

</h2>

<input

placeholder="Contact Name"

value={name}

onChange={(e)=>setName(e.target.value)}

style={{

padding:"10px",

marginRight:"10px",

marginBottom:"10px"

}}

/>

<input

placeholder="Phone Number"

value={phone}

onChange={(e)=>setPhone(e.target.value)}

style={{

padding:"10px",

marginRight:"10px"

}}

/>

<button

onClick={addContact}

>

Add Contact

</button>

<br/><br/>

{

contacts.length===0 &&

<p>

No emergency contacts saved.

</p>

}

{

contacts.map((contact,index)=>(

<div

key={index}

style={{

border:"1px solid #ddd",

padding:"15px",

marginBottom:"10px",

borderRadius:"10px"

}}

>

<h3>

👤 {contact.name}

</h3>

<p>

📞 {contact.phone}

</p>

<a href={`tel:${contact.phone}`}>

Call Now

</a>

</div>

))

}

<hr/>

<h2>

Nearby Emergency Services

</h2>

<div

style={{

display:"flex",

gap:"20px",

flexWrap:"wrap"

}}

>

<div

style={{

padding:"20px",

border:"1px solid gray",

borderRadius:"10px",

width:"250px"

}}

>

<h3>

🚓 Delhi Police Station

</h3>

<p>

Distance : 1.2 km

</p>

<p>

Emergency : 112

</p>

</div>

<div

style={{

padding:"20px",

border:"1px solid gray",

borderRadius:"10px",

width:"250px"

}}

>

<h3>

🏥 AIIMS Hospital

</h3>

<p>

Distance : 850 m

</p>

<p>

Ambulance : 108

</p>

</div>

</div>

</div>

);

}

export default Emergency;