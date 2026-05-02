import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getSaved, unsaveJob } from "../../lib/api";
import JobCard from "../../components/JobCard";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function CandidateSaved() {
  const [saved, setSaved] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSaved()
      .then(({ data }) => setSaved(data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleUnsave = async (jobId) => {
    try {
      await unsaveJob(jobId);
      setSaved((s) => s.filter((item) => item.job_id !== jobId));
      toast.success("Dihapus dari simpanan");
    } catch { toast.error("Gagal menghapus"); }
  };

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-forgotten-blue mb-6">Lowongan Disimpan</h1>

      {saved.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">❤️</div>
          <h3 className="font-semibold text-gray-700 mb-2">Belum ada yang disimpan</h3>
          <p className="text-sm text-gray-400 mb-4">Simpan lowongan menarik untuk dilamar nanti</p>
          <Link to="/jobs" className="btn-primary inline-block">Jelajahi Lowongan</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {saved.map((s) => (
            <JobCard
              key={s.job_id}
              job={s.job}
              saved
              onSave={(jobId) => handleUnsave(jobId)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
