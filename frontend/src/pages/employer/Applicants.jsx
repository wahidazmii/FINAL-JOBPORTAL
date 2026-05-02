import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { MapPin, Zap, Mail, ChevronDown } from "lucide-react";
import { getJobApplicants, updateApplicationStatus, getJob } from "../../lib/api";
import { APP_STATUS, scoreColor } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

const STATUS_OPTIONS = ["applied", "reviewing", "interview", "rejected", "hired"];

export default function Applicants() {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getJob(id), getJobApplicants(id)])
      .then(([j, a]) => { setJob(j.data); setApps(a.data || []); })
      .catch(() => toast.error("Gagal memuat data"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleStatusChange = async (appId, status) => {
    try {
      await updateApplicationStatus(appId, status);
      setApps((prev) => prev.map((a) => a.id === appId ? { ...a, status } : a));
      toast.success(`Status diperbarui: ${APP_STATUS[status]?.label}`);
    } catch { toast.error("Gagal memperbarui status"); }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <Link to="/employer/jobs" className="text-xs text-gray-400 hover:text-jungle-teal mb-2 inline-block">← Kembali</Link>
        <h1 className="text-2xl font-bold text-forgotten-blue">Pelamar: {job?.title}</h1>
        <p className="text-sm text-gray-400">{apps.length} total pelamar</p>
      </div>

      {/* Status summary */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        {STATUS_OPTIONS.map((s) => {
          const cnt = apps.filter((a) => a.status === s).length;
          const info = APP_STATUS[s];
          return (
            <div key={s} className={`rounded-xl p-3 text-center ${info.color}`}>
              <p className="text-lg font-bold">{cnt}</p>
              <p className="text-xs">{info.label}</p>
            </div>
          );
        })}
      </div>

      {apps.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-5xl mb-3">👥</div>
          <p className="font-medium">Belum ada pelamar</p>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app) => {
            const { candidate } = app;
            const status = APP_STATUS[app.status] || APP_STATUS.applied;
            return (
              <div key={app.id} className="card p-5" data-testid="applicant-card">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="w-10 h-10 bg-jungle-teal rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
                      {candidate?.name?.[0] || "?"}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-forgotten-blue text-sm">{candidate?.name}</p>
                      {candidate?.headline && <p className="text-xs text-gray-500 truncate">{candidate.headline}</p>}
                      <div className="flex flex-wrap gap-2 mt-1 text-xs text-gray-400">
                        {candidate?.email && (
                          <span className="flex items-center gap-1"><Mail size={11} /> {candidate.email}</span>
                        )}
                        {candidate?.location && (
                          <span className="flex items-center gap-1"><MapPin size={11} /> {candidate.location}</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    {app.match_score != null && (
                      <span className={`text-sm font-bold flex items-center gap-1 ${scoreColor(app.match_score)}`}>
                        <Zap size={13} /> {app.match_score}%
                      </span>
                    )}
                    <div className="relative">
                      <select
                        value={app.status}
                        onChange={(e) => handleStatusChange(app.id, e.target.value)}
                        className={`appearance-none pr-6 pl-2 py-1 rounded-lg text-xs font-medium cursor-pointer border-0 outline-none ${status.color}`}
                        data-testid="status-select"
                      >
                        {STATUS_OPTIONS.map((s) => (
                          <option key={s} value={s}>{APP_STATUS[s].label}</option>
                        ))}
                      </select>
                      <ChevronDown size={11} className="absolute right-1 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>
                </div>

                {candidate?.skills?.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-400 mb-1.5">Skills</p>
                    <div className="flex flex-wrap gap-1">
                      {candidate.skills.slice(0, 6).map((s) => (
                        <span key={s} className={`badge text-xs ${app.matched_skills?.includes(s) ? "badge-teal" : "bg-gray-100 text-gray-500"}`}>{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {app.rationale && (
                  <div className="mt-3 p-2.5 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 flex items-center gap-1 mb-1"><Zap size={11} className="text-jungle-teal" /> AI Rationale</p>
                    <p className="text-xs text-gray-600">{app.rationale}</p>
                  </div>
                )}

                {app.cover_letter && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-400 mb-1">Cover Letter:</p>
                    <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">{app.cover_letter}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
