import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Edit2, Trash2, Users, Eye } from "lucide-react";
import { getMyJobs, deleteJob } from "../../lib/api";
import { JOB_STATUS, EMPLOYMENT_LABELS, WORK_MODE_LABELS, timeAgo } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function EmployerJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    getMyJobs()
      .then(({ data }) => setJobs(data || []))
      .catch(() => toast.error("Gagal memuat lowongan"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Hapus lowongan "${title}"?`)) return;
    try {
      await deleteJob(id);
      setJobs((j) => j.filter((x) => x.id !== id));
      toast.success("Lowongan dihapus");
    } catch { toast.error("Gagal menghapus"); }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-forgotten-blue">Lowongan Saya</h1>
        <Link to="/employer/jobs/new" className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Post Lowongan
        </Link>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📋</div>
          <h3 className="font-semibold text-gray-700 mb-2">Belum ada lowongan</h3>
          <p className="text-sm text-gray-400 mb-4">Post lowongan pertama kamu dan mulai menerima pelamar</p>
          <Link to="/employer/jobs/new" className="btn-primary inline-flex items-center gap-2"><Plus size={16} /> Post Lowongan</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => {
            const status = JOB_STATUS[job.status] || JOB_STATUS.draft;
            return (
              <div key={job.id} className="card p-4" data-testid="job-row">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <p className="font-semibold text-forgotten-blue text-sm">{job.title}</p>
                      <span className={`badge ${status.color}`}>{status.label}</span>
                      {job.is_featured && <span className="badge bg-yellow-50 text-yellow-700">⭐ Featured</span>}
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                      <span>{WORK_MODE_LABELS[job.work_mode]}</span>
                      <span>·</span>
                      <span>{EMPLOYMENT_LABELS[job.employment_type]}</span>
                      <span>·</span>
                      <span>{timeAgo(job.created_at)}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Eye size={13} /> {job.views || 0}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Users size={13} /> {job.applications_count || 0}
                    </div>
                    <Link to={`/employer/jobs/${job.id}/applicants`}
                      className="text-xs text-jungle-teal font-medium hover:underline px-2">
                      Pelamar
                    </Link>
                    <Link to={`/employer/jobs/${job.id}/edit`}
                      className="p-1.5 text-gray-400 hover:text-jungle-teal rounded-lg hover:bg-gray-50 transition-colors">
                      <Edit2 size={15} />
                    </Link>
                    <button onClick={() => handleDelete(job.id, job.title)}
                      className="p-1.5 text-gray-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors">
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
