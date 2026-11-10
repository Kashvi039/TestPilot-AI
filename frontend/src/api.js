
import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Get all registered projects
export const getProjects = async () => {
  const response = await API.get("/api/projects/");
  return response.data;
};

// Register a new project
export const registerProject = async (projectData) => {
  const response = await API.post("/api/projects/", projectData);
  return response.data;
};

// Get execution history for a project
export const getHistory = async (projectId) => {
  const response = await API.get(`/api/history/${projectId}`);
  return response.data;
};

// Start test execution
export const executeTests = async (projectId, language = "python") => {
  const response = await API.post("/api/executions/", {
    project_id: projectId,
    language,
  });
  return response.data;
};

// Approve or reject an AI-generated fix
export const submitApproval = async (threadId, projectId, approved) => {
  const response = await API.post(
    `/api/executions/${threadId}/approval`,
    {
      project_id: projectId,
      approved,
    }
  );
  return response.data;
};

export default API;
