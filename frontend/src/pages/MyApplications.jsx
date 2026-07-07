// src/pages/MyApplications.jsx

import { useState, useEffect } from "react";
import axiosInstance from "../api/axiosInstance";

function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [startupMap, setStartupMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const response = await axiosInstance.get("/applications/me");
        setApplications(response.data);

        // Get unique startup IDs and fetch their names
        const startupIds = [...new Set(response.data.map((a) => a.startup_id))];
        const map = {};
        await Promise.all(
          startupIds.map(async (sid) => {
            try {
              const res = await axiosInstance.get(`/startups/${sid}`);
              map[sid] = res.data.startup_name;
            } catch {
              map[sid] = sid;
            }
          }),
        );
        setStartupMap(map);
      } catch (err) {
        setError("Failed to load applications.");
      } finally {
        setLoading(false);
      }
    };
    fetchApplications();
  }, []);

  const getStatusStyle = (status) => {
    switch (status) {
      case "Accepted":
        return "bg-green-100 text-green-700";
      case "Rejected":
        return "bg-red-100 text-red-700";
      default:
        return "bg-yellow-100 text-yellow-700";
    }
  };

  if (loading) {
    return (
      <div className="text-center mt-20 text-gray-500">
        Loading applications...
      </div>
    );
  }

  if (error) {
    return <div className="text-center mt-20 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">My Applications</h1>

      {applications.length === 0 ? (
        <div className="text-center text-gray-500 mt-20">
          <p className="text-xl">No applications yet.</p>
          <p className="mt-2">Browse startups and apply to a role!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {applications.map((app) => (
            <div key={app.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-lg font-bold text-gray-800">
                    {app.role_applied}
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Startup: {startupMap[app.startup_id] || app.startup_id}
                  </p>
                </div>
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${getStatusStyle(app.status)}`}
                >
                  {app.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyApplications;
