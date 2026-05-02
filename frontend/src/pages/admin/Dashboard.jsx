import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users, Briefcase, Building2, FileText, TrendingUp, ShieldAlert } from "lucide-react";
import { adminOverview } from "../../lib/api";
import Spinner from "../../components/ui/Spinner";

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminOverview()
      .then(({ data }) => setData(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center gap-3 mb-6">
        <ShieldAlert size={22} className="text-teal-400" />
        <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Users", val: data?.users?.total || 0, sub: `${data?.users?.candidates || 0} kandidat · ${data?.users?.employers || 0} employer`, icon: Users, color: "text-blue-400" },
          { label: "Perusahaan", val: data?.companies?.total || 0, icon: Building2, color: "text-purple-400" },
          { label: "Total Lowongan", val: data?.jobs?.total || 0, sub: `${data?.jobs?.published || 0} aktif · ${data?.jobs?.featured || 0} featured`, icon: Briefcase, color: "text-teal-400" },
          { label: "Lamaran", val: data?.applications?.total || 0, icon: FileText, color: "text-orange-400" },
        ].map(({ label, val, sub, icon: Icon, color }) => (
          <div key={label} className="bg-slate-800 rounded-2xl p-5" data-testid="stat-card">
            <Icon size={20} className={`${color} mb-3`} />
            <p className="text-2xl font-bold text-white">{val}</p>
            <p className="text-sm text-gray-400">{label}</p>
            {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
          </div>
        ))}
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { to: "/admin/jobs", label: "Kelola Lowongan", desc: `${data?.jobs?.total || 0} total, ${data?.jobs?.published || 0} aktif`, icon: Briefcase, color: "border-teal-700 hover:border-teal-500" },
          { to: "/admin/users", label: "Kelola Users", desc: `${data?.users?.total || 0} users, ${data?.users?.disabled || 0} dinonaktifkan`, icon: Users, color: "border-blue-700 hover:border-blue-500" },
          { to: "/admin/companies", label: "Perusahaan", desc: `${data?.companies?.total || 0} perusahaan terdaftar`, icon: Building2, color: "border-purple-700 hover:border-purple-500" },
        ].map(({ to, label, desc, icon: Icon, color }) => (
          <Link key={to} to={to} className={`bg-slate-800 rounded-2xl p-5 border-2 border-transparent ${color} transition-all`}>
            <Icon size={20} className="text-gray-400 mb-3" />
            <p className="font-semibold text-white text-sm">{label}</p>
            <p className="text-xs text-gray-500 mt-1">{desc}</p>
          </Link>
        ))}
      </div>

      {/* Jobs status breakdown */}
      {data?.jobs && (
        <div className="bg-slate-800 rounded-2xl p-5 mt-4">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-teal-400" />
            <h2 className="font-semibold text-white text-sm">Status Lowongan</h2>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[
              ["published", "Aktif", "text-green-400", data.jobs.published],
              ["paused", "Dijeda", "text-yellow-400", data.jobs.paused],
              ["closed", "Ditutup", "text-red-400", data.jobs.closed],
              ["featured", "Featured", "text-yellow-300", data.jobs.featured],
            ].map(([key, label, color, val]) => (
              <div key={key} className="text-center">
                <p className={`text-xl font-bold ${color}`}>{val}</p>
                <p className="text-xs text-gray-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
