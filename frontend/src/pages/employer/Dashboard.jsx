import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Briefcase, Users, TrendingUp, Plus, ArrowRight } from "lucide-react";
import { getEmployerStats, getMyJobs } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import { JOB_STATUS, timeAgo } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";

export default function EmployerDashboard() {
  const { user, company } = useAuth();
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getEmployerStats(), getMyJobs()])
      .then(([s, j]) => { setStats(s.data); setJobs((j.data || []).slice(0, 5)); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-forgotten-blue">Dashboard Employer</h1>
          <p className="text-gray-400 text-sm">{company?.name || user?.name}</p>
        </div>
        <Link to="/employer/jobs/new" className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Post Lowongan
        </Link>
      </div>

      {loading ? <Spinner center /> : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Total Lowongan", val: stats?.total_jobs || 0, icon: Briefcase, color: "text-blue-600 bg-blue-50" },
              { label: "Lowongan Aktif", val: stats?.active_jobs || 0, icon: TrendingUp, color: "text-green-600 bg-green-50" },
              { label: "Total Pelamar", val: stats?.total_applications || 0, icon: Users, color: "text-purple-600 bg-purple-50" },
              { label: "Interview", val: stats?.interview_count || 0, icon: TrendingUp, color: "text-orange-600 bg-orange-50" },
            ].map(({ label, val, icon: Icon, color }) => (
              <div key={label} className="card p-4" data-testid="stat-card">
                <div className={`w-9 h-9 rounded-xl ${color} flex items-center justify-center mb-3`}>
                  <Icon size={16} />
                </div>
                <p className="text-2xl font-bold text-forgotten-blue">{val}</p>
                <p className="text-xs text-gray-400">{label}</p>
              </div>
            ))}
          </div>

          {/* Recent jobs */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-bold text-forgotten-blue">Lowongan Terbaru</h2>
              <Link to="/employer/jobs" className="text-jungle-teal text-sm flex items-center gap-1">
                Kelola Semua <ArrowRight size={14} />
              </Link>
            </div>
            {jobs.length === 0 ? (
              <div className="text-center py-12 text-sm text-gray-400 card">
                Belum ada lowongan.{" "}
                <Link to="/employer/jobs/new" className="text-jungle-teal font-medium">Post sekarang →</Link>
              </div>
            ) : (
              <div className="space-y-3">
                {jobs.map((job) => {
                  const status = JOB_STATUS[job.status] || JOB_STATUS.draft;
                  return (
                    <div key={job.id} className="card p-4 flex items-center justify-between gap-3">
                      <div className="min-w-0">
                        <p className="font-medium text-forgotten-blue text-sm truncate">{job.title}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{timeAgo(job.created_at)} · {job.applications_count || 0} pelamar</p>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <span className={`badge ${status.color}`}>{status.label}</span>
                        <Link to={`/employer/jobs/${job.id}/applicants`} className="text-jungle-teal text-xs font-medium hover:underline">
                          Lihat Pelamar
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
