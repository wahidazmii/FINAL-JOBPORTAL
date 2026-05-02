import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileText, Heart, TrendingUp, Zap, ArrowRight, User } from "lucide-react";
import { getCandidateStats, getRecommendations } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import JobCard from "../../components/JobCard";
import Spinner from "../../components/ui/Spinner";

export default function CandidateDashboard() {
  const { user, profile } = useAuth();
  const [stats, setStats] = useState(null);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getCandidateStats(), getRecommendations(6)])
      .then(([s, r]) => { setStats(s.data); setRecs(r.data || []); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const profileComplete = profile && (profile.skills?.length > 0 || profile.headline);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Welcome */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-forgotten-blue">Hai, {user?.name}! 👋</h1>
        <p className="text-gray-400 text-sm mt-1">Temukan peluang karir terbaik untukmu hari ini.</p>
      </div>

      {/* Profile incomplete warning */}
      {!profileComplete && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6 flex items-start gap-3">
          <Zap size={18} className="text-yellow-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-800">Profil kamu belum lengkap</p>
            <p className="text-xs text-yellow-600 mt-0.5">Lengkapi skill dan upload resume untuk mendapatkan rekomendasi lowongan yang akurat.</p>
            <Link to="/candidate/profile" className="text-xs text-yellow-700 font-semibold hover:underline mt-1 inline-block">
              Lengkapi Profil →
            </Link>
          </div>
        </div>
      )}

      {/* Stats */}
      {loading ? <Spinner center /> : (
        <>
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[
              { label: "Total Lamaran", val: stats?.total_applications || 0, icon: FileText, color: "text-blue-600 bg-blue-50" },
              { label: "Interview", val: stats?.interview_count || 0, icon: TrendingUp, color: "text-purple-600 bg-purple-50" },
              { label: "Disimpan", val: stats?.saved_count || 0, icon: Heart, color: "text-red-500 bg-red-50" },
            ].map(({ label, val, icon: Icon, color }) => (
              <div key={label} className="card p-4 text-center" data-testid="stat-card">
                <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center mx-auto mb-2`}>
                  <Icon size={18} />
                </div>
                <p className="text-2xl font-bold text-forgotten-blue">{val}</p>
                <p className="text-xs text-gray-400">{label}</p>
              </div>
            ))}
          </div>

          {/* Quick links */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
            {[
              { to: "/jobs", label: "Cari Kerja", icon: "🔍" },
              { to: "/candidate/applications", label: "Lamaranku", icon: "📄" },
              { to: "/candidate/saved", label: "Disimpan", icon: "❤️" },
              { to: "/candidate/profile", label: "Edit Profil", icon: "👤" },
            ].map((l) => (
              <Link key={l.to} to={l.to} className="card p-4 flex items-center gap-3 hover:border-jungle-teal transition-all">
                <span className="text-xl">{l.icon}</span>
                <span className="text-sm font-medium text-gray-700">{l.label}</span>
              </Link>
            ))}
          </div>

          {/* Recommendations */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Zap size={16} className="text-jungle-teal" />
                <h2 className="font-bold text-forgotten-blue">Rekomendasi Untukmu</h2>
              </div>
              <Link to="/jobs" className="text-jungle-teal text-sm flex items-center gap-1">
                Lihat Semua <ArrowRight size={14} />
              </Link>
            </div>
            {recs.length === 0 ? (
              <div className="text-center py-12 text-sm text-gray-400">
                <User size={32} className="mx-auto mb-2 opacity-30" />
                Lengkapi profil untuk mendapatkan rekomendasi personal
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recs.map((job) => <JobCard key={job.id} job={job} />)}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
