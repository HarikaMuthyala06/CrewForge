// src/components/Navbar.jsx

import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center shadow-md">
      <Link to="/" className="text-xl font-bold tracking-wide">
        CrewForge
      </Link>

      <div className="flex gap-4 items-center">
        <Link to="/" className="hover:underline">
          Startups
        </Link>

        {user ? (
          <>
            <Link to="/profile" className="hover:underline">
              Profile
            </Link>
            <Link to="/my-applications" className="hover:underline">
              My Applications
            </Link>
            <Link to="/dashboard" className="hover:underline">
              Founder Dashboard
            </Link>
            <Link to="/team-dashboard" className="hover:underline">
              Team Dashboard
            </Link>
            <span className="text-sm opacity-80">Hi, {user.name}</span>
            <button
              onClick={handleLogout}
              className="bg-white text-blue-600 px-3 py-1 rounded font-semibold hover:bg-gray-100"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="hover:underline">
              Login
            </Link>
            <Link
              to="/register"
              className="bg-white text-blue-600 px-3 py-1 rounded font-semibold hover:bg-gray-100"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
