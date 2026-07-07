// src/pages/StartupDetails.jsx

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import axiosInstance from "../api/axiosInstance";

function StartupDetails() {
  const [startup, setStartup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [applyingTo, setApplyingTo] = useState(null);
  const [applyMessage, setApplyMessage] = useState("");

  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStartup = async () => {
      try {
        const response = await axiosInstance.get(`/startups/${id}`);
        setStartup(response.data);
      } catch (err) {
        setError("Startup not found.");
      } finally {
        setLoading(false);
      }
    };
    fetchStartup();
  }, [id]);

  const handleApply = async (openingId) => {
    if (!user) {
      navigate("/login");
      return;
    }

    setApplyingTo(openingId);
    setApplyMessage("");

    try {
      await axiosInstance.post("/applications", {
        startup_id: startup.id,
        opening_id: openingId,
      });
      setApplyMessage("Application submitted successfully!");
    } catch (err) {
      setApplyMessage(err.response?.data?.detail || "Failed to apply.");
    } finally {
      setApplyingTo(null);
    }
  };

  if (loading) {
    return <div className="text-center mt-20 text-gray-500">Loading...</div>;
  }

  if (error) {
    return <div className="text-center mt-20 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      {/* Startup Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-3">
          <h1 className="text-3xl font-bold text-gray-800">
            {startup.startup_name}
          </h1>
          <span className="bg-blue-100 text-blue-700 text-sm font-medium px-3 py-1 rounded">
            {startup.domain}
          </span>
        </div>
        <p className="text-gray-600 leading-relaxed">{startup.description}</p>
      </div>

      {/* Apply message */}
      {applyMessage && (
        <div
          className={`px-4 py-2 rounded mb-4 text-sm ${
            applyMessage.includes("successfully")
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {applyMessage}
        </div>
      )}

      {/* Open Roles */}
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        Open Roles ({startup.openings.length})
      </h2>

      {startup.openings.length === 0 ? (
        <div className="text-gray-500 text-center py-10">
          No open roles at the moment.
        </div>
      ) : (
        <div className="space-y-4">
          {startup.openings.map((opening) => (
            <div
              key={opening.opening_id}
              className="bg-white rounded-lg shadow-md p-6"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-bold text-gray-800">
                  {opening.role_name}
                </h3>
                <button
                  onClick={() => handleApply(opening.opening_id)}
                  disabled={applyingTo === opening.opening_id}
                  className="bg-blue-600 text-white px-4 py-1 rounded text-sm font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {applyingTo === opening.opening_id ? "Applying..." : "Apply"}
                </button>
              </div>

              <p className="text-gray-600 text-sm mb-3">
                {opening.role_description}
              </p>

              <div className="flex flex-wrap gap-2">
                {opening.required_skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Back button */}
      <button
        onClick={() => navigate("/")}
        className="mt-8 text-blue-600 hover:underline text-sm"
      >
        ← Back to all startups
      </button>
    </div>
  );
}

export default StartupDetails;
