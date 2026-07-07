// src/pages/StartupList.jsx

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import axiosInstance from "../api/axiosInstance";

function StartupList() {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { user } = useAuth();

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const response = await axiosInstance.get("/startups");
        setStartups(response.data);
      } catch (err) {
        setError("Failed to load startups. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);

  if (loading) {
    return (
      <div className="text-center mt-20 text-gray-500">Loading startups...</div>
    );
  }

  if (error) {
    return <div className="text-center mt-20 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Explore Startups</h1>
        {user && (
          <Link
            to="/create-startup"
            className="bg-blue-600 text-white px-4 py-2 rounded font-semibold hover:bg-blue-700"
          >
            + Create Startup
          </Link>
        )}
      </div>

      {startups.length === 0 ? (
        <div className="text-center text-gray-500 mt-20">
          <p className="text-xl">No startups yet.</p>
          <p className="mt-2">Be the first to create one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {startups.map((startup) => (
            <div
              key={startup.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-xl font-bold text-gray-800">
                  {startup.startup_name}
                </h2>
                <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-1 rounded">
                  {startup.domain}
                </span>
              </div>

              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {startup.description}
              </p>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  {startup.openings.length} open role
                  {startup.openings.length !== 1 ? "s" : ""}
                </span>
                <Link
                  to={`/startups/${startup.id}`}
                  className="text-blue-600 text-sm font-semibold hover:underline"
                >
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StartupList;
