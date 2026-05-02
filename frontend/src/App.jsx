import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Spinner from "./components/ui/Spinner";

// Lazy-load pages
const Home = lazy(() => import("./pages/Home"));
const Jobs = lazy(() => import("./pages/Jobs"));
const JobDetail = lazy(() => import("./pages/JobDetail"));
const CompanyPage = lazy(() => import("./pages/CompanyPage"));
const Login = lazy(() => import("./pages/Login"));
const Signup = lazy(() => import("./pages/Signup"));
const CandidateDashboard = lazy(() => import("./pages/candidate/Dashboard"));
const CandidateApplications = lazy(() => import("./pages/candidate/Applications"));
const CandidateSaved = lazy(() => import("./pages/candidate/Saved"));
const CandidateProfile = lazy(() => import("./pages/candidate/Profile"));
const EmployerDashboard = lazy(() => import("./pages/employer/Dashboard"));
const EmployerJobs = lazy(() => import("./pages/employer/Jobs"));
const PostJob = lazy(() => import("./pages/employer/PostJob"));
const EditJob = lazy(() => import("./pages/employer/EditJob"));
const Applicants = lazy(() => import("./pages/employer/Applicants"));
const AdminDashboard = lazy(() => import("./pages/admin/Dashboard"));
const AdminJobs = lazy(() => import("./pages/admin/Jobs"));
const AdminUsers = lazy(() => import("./pages/admin/Users"));
const AdminCompanies = lazy(() => import("./pages/admin/Companies"));
const NotFound = lazy(() => import("./pages/NotFound"));

function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="spinner w-10 h-10" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to="/" replace />;
  return children;
}

function GuestRoute({ children }) {
  const { user } = useAuth();
  if (user) {
    const paths = { candidate: "/candidate", employer: "/employer", admin: "/admin" };
    return <Navigate to={paths[user.role] || "/"} replace />;
  }
  return children;
}

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="spinner w-10 h-10" />
    </div>
  );
}

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-portal-bg">
      <Navbar />
      <main className="flex-1">
        <Suspense fallback={<PageLoader />}>{children}</Suspense>
      </main>
      <Footer />
    </div>
  );
}

function AdminLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar isAdmin />
      <main className="flex-1">
        <Suspense fallback={<PageLoader />}>{children}</Suspense>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />
        <Routes>
          {/* Public */}
          <Route path="/" element={<Layout><Home /></Layout>} />
          <Route path="/jobs" element={<Layout><Jobs /></Layout>} />
          <Route path="/jobs/:slug" element={<Layout><JobDetail /></Layout>} />
          <Route path="/companies/:slug" element={<Layout><CompanyPage /></Layout>} />

          {/* Auth */}
          <Route path="/login" element={<GuestRoute><Layout><Login /></Layout></GuestRoute>} />
          <Route path="/signup" element={<GuestRoute><Layout><Signup /></Layout></GuestRoute>} />

          {/* Candidate */}
          <Route path="/candidate" element={<ProtectedRoute role="candidate"><Layout><CandidateDashboard /></Layout></ProtectedRoute>} />
          <Route path="/candidate/applications" element={<ProtectedRoute role="candidate"><Layout><CandidateApplications /></Layout></ProtectedRoute>} />
          <Route path="/candidate/saved" element={<ProtectedRoute role="candidate"><Layout><CandidateSaved /></Layout></ProtectedRoute>} />
          <Route path="/candidate/profile" element={<ProtectedRoute role="candidate"><Layout><CandidateProfile /></Layout></ProtectedRoute>} />

          {/* Employer */}
          <Route path="/employer" element={<ProtectedRoute role="employer"><Layout><EmployerDashboard /></Layout></ProtectedRoute>} />
          <Route path="/employer/jobs" element={<ProtectedRoute role="employer"><Layout><EmployerJobs /></Layout></ProtectedRoute>} />
          <Route path="/employer/jobs/new" element={<ProtectedRoute role="employer"><Layout><PostJob /></Layout></ProtectedRoute>} />
          <Route path="/employer/jobs/:id/edit" element={<ProtectedRoute role="employer"><Layout><EditJob /></Layout></ProtectedRoute>} />
          <Route path="/employer/jobs/:id/applicants" element={<ProtectedRoute role="employer"><Layout><Applicants /></Layout></ProtectedRoute>} />

          {/* Admin */}
          <Route path="/admin" element={<ProtectedRoute role="admin"><AdminLayout><AdminDashboard /></AdminLayout></ProtectedRoute>} />
          <Route path="/admin/jobs" element={<ProtectedRoute role="admin"><AdminLayout><AdminJobs /></AdminLayout></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute role="admin"><AdminLayout><AdminUsers /></AdminLayout></ProtectedRoute>} />
          <Route path="/admin/companies" element={<ProtectedRoute role="admin"><AdminLayout><AdminCompanies /></AdminLayout></ProtectedRoute>} />

          <Route path="*" element={<Layout><NotFound /></Layout>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
