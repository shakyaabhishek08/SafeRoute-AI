import { Link } from "react-router-dom";

function NotFound() {
  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      <h1
        style={{
          fontSize: "90px",
        }}
      >
        404
      </h1>

      <h2>Page Not Found</h2>

      <Link to="/dashboard">
        Go Back
      </Link>
    </div>
  );
}

export default NotFound;