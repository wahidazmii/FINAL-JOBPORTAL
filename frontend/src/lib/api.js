import axios from "axios";

const BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8001";

const api = axios.create({ baseURL: `${BASE}/api` });

api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// Auth
export const register = (data) => api.post("/auth/register", data);
export const login = (data) => api.post("/auth/login", data);
export const getMe = () => api.get("/auth/me");

// Categories
export const getCategories = () => api.get("/categories");

// Companies
export const getCompany = (slug) => api.get(`/companies/${slug}`);
export const updateMyCompany = (data) => api.put("/companies/me", data);

// Jobs
export const getJobs = (params) => api.get("/jobs", { params });
export const getFeaturedJobs = (limit = 6) => api.get("/jobs/featured", { params: { limit } });
export const getJob = (slug) => api.get(`/jobs/${slug}`);
export const createJob = (data) => api.post("/jobs", data);
export const updateJob = (id, data) => api.put(`/jobs/${id}`, data);
export const deleteJob = (id) => api.delete(`/jobs/${id}`);

// Employer
export const getMyJobs = () => api.get("/employer/jobs");
export const getEmployerStats = () => api.get("/employer/stats");
export const getJobApplicants = (jobId) => api.get(`/applications/job/${jobId}`);
export const updateApplicationStatus = (appId, status) =>
  api.put(`/applications/${appId}/status`, { status });

// Applications (Candidate)
export const applyJob = (data) => api.post("/applications", data);
export const getMyApplications = () => api.get("/applications/candidate");

// Saved Jobs
export const saveJob = (jobId) => api.post(`/saved/${jobId}`);
export const unsaveJob = (jobId) => api.delete(`/saved/${jobId}`);
export const getSaved = () => api.get("/saved");
export const checkSaved = (jobId) => api.get(`/saved/check/${jobId}`);

// Profile
export const getProfile = () => api.get("/profile");
export const updateProfile = (data) => api.put("/profile", data);
export const uploadResume = (data) => api.post("/profile/resume", data);

// Candidate
export const getCandidateStats = () => api.get("/candidate/stats");
export const getRecommendations = (limit = 6) =>
  api.get("/candidate/recommendations", { params: { limit } });

// AI
export const aiMatchScore = (data) => api.post("/ai/match-score", data);
export const aiSalaryPrediction = (data) => api.post("/ai/salary-prediction", data);
export const aiParseResume = (data) => api.post("/ai/parse-resume", data);

// Admin
export const adminOverview = () => api.get("/admin/overview");
export const adminGetJobs = (params) => api.get("/admin/jobs", { params });
export const adminUpdateJob = (id, data) => api.put(`/admin/jobs/${id}`, data);
export const adminDeleteJob = (id) => api.delete(`/admin/jobs/${id}`);
export const adminGetUsers = (params) => api.get("/admin/users", { params });
export const adminUpdateUser = (id, data) => api.put(`/admin/users/${id}`, data);
export const adminGetCompanies = (params) => api.get("/admin/companies", { params });
export const adminUpdateCompany = (id, data) => api.put(`/admin/companies/${id}`, data);

export default api;
