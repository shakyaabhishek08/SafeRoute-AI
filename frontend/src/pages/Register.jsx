import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../lib/api";

function Register() {

  const navigate = useNavigate();

  const [name, setName] = useState("");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  async function register(e) {

    e.preventDefault();

    setLoading(true);

    try {

      const res = await api.post("/auth/signup", {

        name,

        email,

        password

      });

      localStorage.setItem("token", res.data.token);

      localStorage.setItem(
        "user",
        JSON.stringify(res.data.user)
      );

      alert("Registration Successful");

      navigate("/dashboard");

    }

    catch (err) {

      console.log(err);

      alert(

        err.response?.data?.detail ||

        "Registration Failed"

      );

    }

    setLoading(false);

  }

  return (

    <div

      style={{

        minHeight:"100vh",

        display:"flex",

        justifyContent:"center",

        alignItems:"center",

        background:
        "linear-gradient(135deg,#0f172a,#1e3a8a,#2563eb)"

      }}

    >

      <form

        onSubmit={register}

        style={{

          width:"450px",

          background:"white",

          padding:"40px",

          borderRadius:"20px",

          boxShadow:"0 20px 40px rgba(0,0,0,.25)"

        }}

      >

        <h1

          style={{

            textAlign:"center",

            marginBottom:"30px"

          }}

        >

          📝 Create Account

        </h1>

        <input

          type="text"

          placeholder="Full Name"

          value={name}

          onChange={(e)=>setName(e.target.value)}

          required

          style={inputStyle}

        />

        <input

          type="email"

          placeholder="Email"

          value={email}

          onChange={(e)=>setEmail(e.target.value)}

          required

          style={inputStyle}

        />

        <input

          type="password"

          placeholder="Password"

          value={password}

          onChange={(e)=>setPassword(e.target.value)}

          required

          style={inputStyle}

        />

        <button

          type="submit"

          disabled={loading}

          style={buttonStyle}

        >

          {

            loading

            ?

            "Creating Account..."

            :

            "Register"

          }

        </button>

        <p

          style={{

            marginTop:"20px",

            textAlign:"center"

          }}

        >

          Already have an account?

          <Link

            to="/login"

            style={{

              color:"#2563eb",

              marginLeft:"8px",

              textDecoration:"none",

              fontWeight:"bold"

            }}

          >

            Login

          </Link>

        </p>

      </form>

    </div>

  );

}

const inputStyle={

  width:"100%",

  padding:"15px",

  marginBottom:"18px",

  borderRadius:"10px",

  border:"1px solid #ddd",

  fontSize:"16px",

  outline:"none",

  boxSizing:"border-box"

};

const buttonStyle={

  width:"100%",

  padding:"15px",

  border:"none",

  borderRadius:"10px",

  background:"#2563eb",

  color:"white",

  fontSize:"18px",

  cursor:"pointer",

  marginTop:"10px"

};

export default Register;