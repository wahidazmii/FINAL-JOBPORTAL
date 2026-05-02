import React, { useEffect, useState } from "react";
import { Search, Trash2, Star, X } from "lucide-react";
import { adminGetJobs, adminUpdateJob, adminDeleteJob } from "../../lib/api";
import { JOB_STATUS, timeAgo } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function AdminJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await adminGetJobs({ q: q || undefined, status: statusFilter || undefined, limit: 100 });
      setJobs(data || []);
    } catch { toast.error("Gagal memuat data"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleStatus = async (id, status) => {
    try {
      await adminUpdateJob(id, { status });
      setJobs((j) => j.map((x) => x.id === id ? { ...x, status } : x));
      toast.success("Status diperbarui");
    } catch { toast.error("Gagal"); }
  };

  const handleFeatured = async (id, featured) => {
    try {
      await adminUpdateJob(id, { is_featured: featured });
      setJobs((j) => j.map((x) => x.id === id ? { ...x, is_featured: featured } : x));
      toast.success(featured ? "Dijadikan featured" : "Dihapus dari featured");
    } catch { toast.error("Gagal"); }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Hapus lowongan "${title}"?`)) return;
    try {
      await adminDeleteJob(id);
      setJobs((j) => j.filter((x) => x.id !== id));
      toast.success("Lowongan dihapus");
    } catch { toast.error("Gagal menghapus"); }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Kelola Lowongan</h1>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <div className="flex-1 flex items-center gap-2 bg-slate-800 rounded-xl px-3 py-2">
          <Search size={15} className="text-gray-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && load()}
            placeholder="Cari judul lowongan..." className="flex-1 bg-transparent text-white text-sm outline-none placeholder-gray-500" />
          {q && <button onClick={() => { setQ(""); }}><X size={13} className="text-gray-400" /></button>}
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-800 text-gray-300 rounded-xl px-3 py-2 text-sm outline-none">
          <option value="">Semua Status</option>
          <option value="published">Aktif</option>
          <option value="paused">Dijeda</option>
          <option value="closed">Ditutup</option>
          <option value="draft">Draft</option>
        </select>
        <button onClick={load} className="px-4 py-2 bg-jungle-teal text-white rounded-xl text-sm font-medium hover:bg-teal-700 transition-colors">
          Cari
        </button>
      </div>

      {loading ? <Spinner center /> : (
        <div className="space-y-2">
          {jobs.map((job) => {
            const status = JOB_STATUS[job.status] || JOB_STATUS.draft;
            return (
              <div key={job.id} className="bg-slate-800 rounded-xl p-4 flex items-start justify-between gap-3" data-testid="admin-job-row">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-white font-medium text-sm">{job.title}</p>
                    <span className={`badge ${status.color}`}>{status.label}</span>
                    {job.is_featured && <span className="badge bg-yellow-900 text-yellow-300">⭐ Featured</span>}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{job.company?.name} · {timeAgo(job.created_at)} · {job.applications_count || 0} pelamar</p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <select value={job.status} onChange={(e) => handleStatus(job.id, e.target.value)}
                    className="bg-slate-700 text-gray-300 rounded-lg px-2 py-1 text-xs outline-none">
                    <option value="published">Aktif</option>
                    <option value="paused">Jeda</option>
                    <option value="closed">Tutup</option>
                    <option value="draft">Draft</option>
                  </select>
                  <button onClick={() => handleFeatured(job.id, !job.is_featured)}
                    className={`p-1.5 rounded-lg transition-colors ${job.is_featured ? "text-yellow-400 bg-yellow-900/30" : "text-gray-500 hover:text-yellow-400"}`}>
                    <Star size={15} fill={job.is_featured ? "currentColor" : "none"} />
                  </button>
                  <button onClick={() => handleDelete(job.id, job.title)}
                    className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-900/20 transition-colors">
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            );
          })}
          {jobs.length === 0 && (
            <p className="text-center text-gray-500 py-12 text-sm">Tidak ada lowongan ditemukan</p>
          )}
        </div>
      )}
    </div>
  );
}
