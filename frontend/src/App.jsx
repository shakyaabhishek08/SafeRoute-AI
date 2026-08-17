import React from "react";

import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MapDashboard from "./pages/MapDashboard";
import AIChat from "./pages/AIChat";
import Emergency from "./pages/Emergency";
import Profile from "./pages/Profile";
import AdminDashboard from "./pages/AdminDashboard";
import MainLayout from "./layouts/MainLayout";
import NotFound from "./pages/NotFound";


// ------------------------------------
// Protected Route
// ------------------------------------

function ProtectedRoute({ children }) {

  const token = localStorage.getItem("token");

  if (!token) {

    return <Navigate to="/login" replace />;

  }

  return children;

}

function App() {

  return (

    <BrowserRouter>

      <Routes>

        {/* Public */}

        <Route
          path="/"
          element={<Landing />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />



        {/* Dashboard */}

        <Route

          path="/dashboard"

          element={

            <ProtectedRoute>

              <MainLayout>

                <MapDashboard />

              </MainLayout>

            </ProtectedRoute>

          }

        />



        {/* Chat */}

        <Route

          path="/chat"

          element={

            <ProtectedRoute>

              <MainLayout>

                <AIChat />

              </MainLayout>

            </ProtectedRoute>

          }

        />



        {/* Profile */}

        <Route

          path="/profile"

          element={

            <ProtectedRoute>

              <MainLayout>

                <Profile />

              </MainLayout>

            </ProtectedRoute>

          }

        />



        {/* Emergency */}

        <Route

          path="/emergency"

          element={

            <ProtectedRoute>

              <MainLayout>

                <Emergency />

              </MainLayout>

            </ProtectedRoute>

          }

        />



        {/* Admin */}

        <Route

          path="/admin"

          element={

            <ProtectedRoute>

              <MainLayout>

                <AdminDashboard />

              </MainLayout>

            </ProtectedRoute>

          }

        />



        {/* 404 */}

        <Route

          path="*"

          element={<NotFound />}

        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;