import React, { useState } from "react";

function SearchBox({ placeholder, onSelect }) {
  const [query, setQuery] = useState("");

  async function searchLocation() {
    if (!query.trim()) return;

    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`
      );

      const data = await res.json();

      if (data.length === 0) {
        alert("Location not found");
        return;
      }

      const place = data[0];

      onSelect([
        parseFloat(place.lat),
        parseFloat(place.lon),
      ]);

      setQuery(place.display_name);

    } catch (err) {
      console.log(err);
      alert("Search failed");
    }
  }

  return (
    <div
      style={{
        display: "flex",
        gap: "10px",
        marginBottom: "20px",
      }}
    >
      <input
        value={query}
        placeholder={placeholder}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          flex: 1,
          padding: "12px",
          fontSize: "16px",
          borderRadius: "8px",
          border: "1px solid gray",
        }}
      />

      <button
        onClick={searchLocation}
        style={{
          padding: "12px 20px",
          background: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
        }}
      >
        Search
      </button>
    </div>
  );
}

export default SearchBox;