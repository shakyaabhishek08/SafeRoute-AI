import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../lib/api";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  async function login(e) {

    e.preventDefault();

    setLoading(true);

    try {

      const res = await api.post("/auth/login", {

        email,

        password,

      });

      localStorage.setItem("token", res.data.token);

      localStorage.setItem(
        "user",
        JSON.stringify(res.data.user)
      );

      alert("Login Successful");

      navigate("/dashboard");

    }

    catch (err) {

      console.log(err);

      alert(

        err.response?.data?.detail ||

        "Login Failed"

      );

    }

    setLoading(false);

  }

  return (

    <div

      style={{

        minHeight: "100vh",

        display: "flex",

        justifyContent: "center",

        alignItems: "center",

        background:

          "linear-gradient(135deg,#1e3a8a,#2563eb,#0f172a)"

      }}

    >

      <form

        onSubmit={login}

        style={{

          width: "420px",

          background: "white",

          padding: "40px",

          borderRadius: "20px",

          boxShadow:

            "0 15px 40px rgba(0,0,0,.25)"

        }}

      >

        <h1

          style={{

            textAlign: "center",

            marginBottom: "30px"

          }}

        >

          🔐 Login

        </h1>

        <input

          type="email"

          placeholder="Email"

          value={email}

          onChange={(e)=>setEmail(e.target.value)}

          required

          style={{

            width:"100%",

            padding:"15px",

            marginBottom:"20px",

            borderRadius:"10px",

            border:"1px solid #ddd",

            fontSize:"16px"

          }}

        />

        <input

          type="password"

          placeholder="Password"

          value={password}

          onChange={(e)=>setPassword(e.target.value)}

          required

          style={{

            width:"100%",

            padding:"15px",

            marginBottom:"25px",

            borderRadius:"10px",

            border:"1px solid #ddd",

            fontSize:"16px"

          }}

        />

        <button

          type="submit"

          disabled={loading}

          style={{

            width:"100%",

            padding:"15px",

            border:"none",

            borderRadius:"10px",

            background:"#2563eb",

            color:"white",

            fontSize:"18px",

            cursor:"pointer"

          }}

        >

          {

            loading

            ?

            "Logging in..."

            :

            "Login"

          }

        </button>

        <p

          style={{

            marginTop:"20px",

            textAlign:"center"

          }}

        >

          Don't have an account?

          <Link

            to="/register"

            style={{

              color:"#2563eb",

              marginLeft:"8px",

              textDecoration:"none",

              fontWeight:"bold"

            }}

          >

            Register

          </Link>

        </p>

      </form>

    </div>

  );

}

export default Login;