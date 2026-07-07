// src/App.jsx

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Register from "./pages/Register";
import StartupList from "./pages/StartupList";
import StartupDetails from "./pages/StartupDetails";
import CreateStartup from "./pages/CreateStartup";
import MyApplications from "./pages/MyApplications";
import FounderDashboard from "./pages/FounderDashboard";
import TeamDashboard from "./pages/TeamDashboard";
import NotFound from "./pages/NotFound";
import Profile from "./pages/Profile";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<StartupList />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/startups/:id" element={<StartupDetails />} />

          {/* Protected routes */}
          <Route
            path="/create-startup"
            element={
              <ProtectedRoute>
                <CreateStartup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-applications"
            element={
              <ProtectedRoute>
                <MyApplications />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <FounderDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team-dashboard"
            element={
              <ProtectedRoute>
                <TeamDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
