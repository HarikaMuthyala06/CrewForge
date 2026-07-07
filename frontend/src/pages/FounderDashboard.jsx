// src/pages/FounderDashboard.jsx

import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import axiosInstance from "../api/axiosInstance";

function FounderDashboard() {
  const { user } = useAuth();

  const [startups, setStartups] = useState([]);
  const [selectedStartup, setSelectedStartup] = useState(null);
  const [applications, setApplications] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usersMap, setUsersMap] = useState({});

  const [openingForm, setOpeningForm] = useState({
    role_name: "",
    required_skills: "",
    role_description: "",
  });
  const [openingMessage, setOpeningMessage] = useState("");

  const [taskForm, setTaskForm] = useState({
    assigned_to: "",
    title: "",
    description: "",
  });
  const [taskMessage, setTaskMessage] = useState("");

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const response = await axiosInstance.get("/startups");
        const myStartups = response.data.filter(
          (s) => s.founder_id === user.id,
        );
        setStartups(myStartups);
        if (myStartups.length > 0) {
          setSelectedStartup(myStartups[0]);
        }
      } catch (err) {
        console.error("Failed to fetch startups");
      } finally {
        setLoading(false);
      }
    };
    fetchStartups();
  }, [user.id]);

  useEffect(() => {
    if (!selectedStartup) return;

    const fetchDetails = async () => {
      try {
        const [appsRes, tasksRes] = await Promise.all([
          axiosInstance.get(`/applications/startup/${selectedStartup.id}`),
          axiosInstance.get(`/tasks/startup/${selectedStartup.id}`),
        ]);
        setApplications(appsRes.data);
        setTasks(tasksRes.data);

        const userIds = [
          ...new Set([
            ...appsRes.data.map((a) => a.user_id),
            ...tasksRes.data.map((t) => t.assigned_to),
          ]),
        ];

        const map = {};
        await Promise.all(
          userIds.map(async (uid) => {
            try {
              const res = await axiosInstance.get(`/users/${uid}`);
              map[uid] = `${res.data.name} (${res.data.email})`;
            } catch {
              map[uid] = uid;
            }
          }),
        );
        setUsersMap(map);
      } catch (err) {
        console.error("Failed to fetch details");
      }
    };
    fetchDetails();
  }, [selectedStartup]);

  const handleAccept = async (appId) => {
    try {
      await axiosInstance.put(`/applications/${appId}/accept`);
      setApplications(
        applications.map((a) =>
          a.id === appId ? { ...a, status: "Accepted" } : a,
        ),
      );
    } catch (err) {
      console.error("Failed to accept");
    }
  };

  const handleReject = async (appId) => {
    try {
      await axiosInstance.put(`/applications/${appId}/reject`);
      setApplications(
        applications.map((a) =>
          a.id === appId ? { ...a, status: "Rejected" } : a,
        ),
      );
    } catch (err) {
      console.error("Failed to reject");
    }
  };

  const handleAddOpening = async (e) => {
    e.preventDefault();
    setOpeningMessage("");
    try {
      const payload = {
        role_name: openingForm.role_name,
        role_description: openingForm.role_description,
        required_skills: openingForm.required_skills
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s.length > 0),
      };
      const response = await axiosInstance.post(
        `/startups/${selectedStartup.id}/openings`,
        payload,
      );
      setSelectedStartup(response.data);
      setOpeningForm({
        role_name: "",
        required_skills: "",
        role_description: "",
      });
      setOpeningMessage("Opening added successfully!");
    } catch (err) {
      setOpeningMessage(err.response?.data?.detail || "Failed to add opening.");
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    setTaskMessage("");
    try {
      const payload = {
        startup_id: selectedStartup.id,
        assigned_to: taskForm.assigned_to,
        title: taskForm.title,
        description: taskForm.description,
      };
      const response = await axiosInstance.post("/tasks", payload);
      setTasks([...tasks, response.data]);
      setTaskForm({ assigned_to: "", title: "", description: "" });
      setTaskMessage("Task created successfully!");
    } catch (err) {
      setTaskMessage(err.response?.data?.detail || "Failed to create task.");
    }
  };

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

  const getTaskStatusStyle = (status) => {
    switch (status) {
      case "Completed":
        return "bg-green-100 text-green-700";
      case "In Progress":
        return "bg-blue-100 text-blue-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  if (loading) {
    return (
      <div className="text-center mt-20 text-gray-500">
        Loading dashboard...
      </div>
    );
  }

  if (startups.length === 0) {
    return (
      <div className="text-center mt-20 text-gray-500">
        <p className="text-xl">You haven't created any startups yet.</p>
        <a
          href="/create-startup"
          className="text-blue-600 hover:underline mt-2 block"
        >
          Create your first startup →
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Founder Dashboard
      </h1>

      {/* Startup Selector */}
      {startups.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Select Startup
          </label>
          <select
            className="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            onChange={(e) => {
              const found = startups.find((s) => s.id === e.target.value);
              setSelectedStartup(found);
            }}
          >
            {startups.map((s) => (
              <option key={s.id} value={s.id}>
                {s.startup_name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Startup Info */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start mb-2">
          <h2 className="text-xl font-bold text-gray-800">
            {selectedStartup.startup_name}
          </h2>
          <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded">
            {selectedStartup.domain}
          </span>
        </div>
        <p className="text-gray-600 text-sm">{selectedStartup.description}</p>
      </div>

      {/* Add Opening */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">
          Add Role Opening
        </h2>

        {openingMessage && (
          <div
            className={`px-4 py-2 rounded mb-3 text-sm ${
              openingMessage.includes("successfully")
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {openingMessage}
          </div>
        )}

        <form onSubmit={handleAddOpening} className="space-y-3">
          <input
            type="text"
            placeholder="Role name e.g. Backend Developer"
            value={openingForm.role_name}
            onChange={(e) =>
              setOpeningForm({ ...openingForm, role_name: e.target.value })
            }
            required
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Required skills (comma separated)"
            value={openingForm.required_skills}
            onChange={(e) =>
              setOpeningForm({
                ...openingForm,
                required_skills: e.target.value,
              })
            }
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Role description"
            value={openingForm.role_description}
            onChange={(e) =>
              setOpeningForm({
                ...openingForm,
                role_description: e.target.value,
              })
            }
            required
            rows={2}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700"
          >
            Add Opening
          </button>
        </form>

        {selectedStartup.openings.length > 0 && (
          <div className="mt-4 space-y-2">
            <h3 className="text-sm font-semibold text-gray-700">
              Current Openings:
            </h3>
            {selectedStartup.openings.map((o) => (
              <div
                key={o.opening_id}
                className="bg-gray-50 rounded px-3 py-2 text-sm"
              >
                <span className="font-medium">{o.role_name}</span>
                <span className="text-gray-500 ml-2">
                  — {o.required_skills.join(", ")}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Applications */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">
          Applications ({applications.length})
        </h2>

        {applications.length === 0 ? (
          <p className="text-gray-500 text-sm">No applications yet.</p>
        ) : (
          <div className="space-y-3">
            {applications.map((app) => (
              <div
                key={app.id}
                className="flex justify-between items-center border border-gray-100 rounded px-4 py-3"
              >
                <div>
                  <p className="font-medium text-gray-800">
                    {app.role_applied}
                  </p>
                  <p className="text-xs text-gray-500">
                    Applicant: {usersMap[app.user_id] || app.user_id}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded-full ${getStatusStyle(app.status)}`}
                  >
                    {app.status}
                  </span>
                  {app.status === "Pending" && (
                    <>
                      <button
                        onClick={() => handleAccept(app.id)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-xs font-semibold hover:bg-green-600"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => handleReject(app.id)}
                        className="bg-red-500 text-white px-3 py-1 rounded text-xs font-semibold hover:bg-red-600"
                      >
                        Reject
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Task */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">Create Task</h2>

        {taskMessage && (
          <div
            className={`px-4 py-2 rounded mb-3 text-sm ${
              taskMessage.includes("successfully")
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {taskMessage}
          </div>
        )}

        <form onSubmit={handleAddTask} className="space-y-3">
          {/* Dropdown of accepted team members */}
          <select
            value={taskForm.assigned_to}
            onChange={(e) =>
              setTaskForm({ ...taskForm, assigned_to: e.target.value })
            }
            required
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select team member</option>
            {applications
              .filter((app) => app.status === "Accepted")
              .map((app) => (
                <option key={app.user_id} value={app.user_id}>
                  {usersMap[app.user_id] || app.user_id}
                </option>
              ))}
          </select>

          <input
            type="text"
            placeholder="Task title"
            value={taskForm.title}
            onChange={(e) =>
              setTaskForm({ ...taskForm, title: e.target.value })
            }
            required
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            placeholder="Task description (optional)"
            value={taskForm.description}
            onChange={(e) =>
              setTaskForm({ ...taskForm, description: e.target.value })
            }
            rows={2}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-semibold hover:bg-blue-700"
          >
            Create Task
          </button>
        </form>
      </div>

      {/* Tasks */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">
          Tasks ({tasks.length})
        </h2>

        {tasks.length === 0 ? (
          <p className="text-gray-500 text-sm">No tasks yet.</p>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="flex justify-between items-center border border-gray-100 rounded px-4 py-3"
              >
                <div>
                  <p className="font-medium text-gray-800">{task.title}</p>
                  <p className="text-xs text-gray-500">{task.description}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    Assigned to:{" "}
                    {usersMap[task.assigned_to] || task.assigned_to}
                  </p>
                </div>
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded-full ${getTaskStatusStyle(task.status)}`}
                >
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default FounderDashboard;
