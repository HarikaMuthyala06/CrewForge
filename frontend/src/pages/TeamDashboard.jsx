// src/pages/TeamDashboard.jsx

import { useState, useEffect } from "react";
import axiosInstance from "../api/axiosInstance";

function TeamDashboard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingTask, setUpdatingTask] = useState(null)
  const [updateMessage, setUpdateMessage] = useState("")

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axiosInstance.get("/tasks/me");
        setTasks(response.data);
      } catch (err) {
        setError("Failed to load tasks.");
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, []);

  const handleStatusUpdate = async (taskId, newStatus) => {
    setUpdatingTask(taskId)
    setUpdateMessage("")
    try {
      const response = await axiosInstance.put(`/tasks/${taskId}/status`, {
        status: newStatus
      })
      setTasks(tasks.map(t =>
        t.id === taskId ? { ...t, status: response.data.status } : t
      ))
      setUpdateMessage("Task status updated!")
      setTimeout(() => setUpdateMessage(""), 3000)
    } catch (err) {
      setUpdateMessage(err.response?.data?.detail || "Failed to update status.")
    } finally {
      setUpdatingTask(null)
    }
  }

  const getStatusStyle = (status) => {
    switch (status) {
      case "Completed": return "bg-green-100 text-green-700";
      case "In Progress": return "bg-blue-100 text-blue-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  if (loading) {
    return <div className="text-center mt-20 text-gray-500">Loading tasks...</div>;
  }

  if (error) {
    return <div className="text-center mt-20 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">
        Team Dashboard
      </h1>
      <p className="text-gray-500 mb-8">Your assigned tasks</p>

      {updateMessage && (
        <div className="bg-green-100 text-green-700 px-4 py-2 rounded mb-4 text-sm">
          {updateMessage}
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="text-center text-gray-500 mt-20">
          <p className="text-xl">No tasks assigned yet.</p>
          <p className="mt-2">Your founder will assign tasks once you join a team.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="bg-white rounded-lg shadow-md p-6"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h2 className="text-lg font-bold text-gray-800">
                    {task.title}
                  </h2>
                  {task.description && (
                    <p className="text-sm text-gray-500 mt-1">
                      {task.description}
                    </p>
                  )}
                </div>
                <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getStatusStyle(task.status)}`}>
                  {task.status}
                </span>
              </div>

              {/* Status Update Buttons */}
              <div className="flex gap-2 mt-4">
                {["Todo", "In Progress", "Completed"].map((s) => (
                  <button
                    key={s}
                    onClick={() => handleStatusUpdate(task.id, s)}
                    disabled={task.status === s || updatingTask === task.id}
                    className={`px-3 py-1 rounded text-xs font-semibold transition-colors
                      ${task.status === s
                        ? "bg-blue-600 text-white cursor-default"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      } disabled:opacity-50`}
                  >
                    {updatingTask === task.id ? "Updating..." : s}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TeamDashboard;