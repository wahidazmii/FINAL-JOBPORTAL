import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, Zap, Clock } from "lucide-react";
import { getMyApplications } from "../../lib/api";
import { APP_STATUS, timeAgo, scoreColor } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";

export default function CandidateApplications() {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyApplications()
      .then(({ data }) => setApps(data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-12"><Spinner center /></div>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-forgotten-blue mb-6">Lamaranku</h1>

      {apps.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📄</div>
          <h3 className="font-semibold text-gray-700 mb-2">Belum ada lamaran</h3>
          <p className="text-sm text-gray-400 mb-4">Mulai lamar lowongan dan pantau statusnya di sini</p>
          <Link to="/jobs" className="btn-primary inline-block">Cari Lowongan</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app) => {
            const { job } = app;
            const status = APP_STATUS[app.status] || { label: app.status, color: "bg-gray-100 text-gray-600" };
            return (
              <div key={app.id} className="card p-5" data-testid="application-card">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    {job?.company?.logo_url ? (
                      <img src={job.company.logo_url} alt="" className="w-10 h-10 rounded-xl object-cover flex-shrink-0" />
                    ) : (
                      <div className="w-10 h-10 rounded-xl bg-fountain-mint flex items-center justify-center text-jungle-teal font-bold flex-shrink-0">
                        {job?.company?.name?.[0] || "?"}
                      </div>
                    )}
                    <div className="min-w-0">
                      <Link to={`/jobs/${job?.slug}`} className="font-semibold text-forgotten-blue hover:text-jungle-teal text-sm">
                        {job?.title}
                      </Link>
                      <p className="text-xs text-gray-400 mt-0.5">{job?.company?.name}</p>
                      {job?.location && (
                        <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                          <MapPin size={11} /> {job.location}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2 flex-shrink-0">
                    <span className={`badge ${status.color}`}>{status.label}</span>
                    {app.match_score != null && (
                      <span className={`text-xs font-semibold flex items-center gap-1 ${scoreColor(app.match_score)}`}>
                        <Zap size={11} /> {app.match_score}% match
                      </span>
                    )}
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      <Clock size={10} /> {timeAgo(app.created_at)}
                    </span>
                  </div>
                </div>

                {app.matched_skills?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-50">
                    <p className="text-xs text-gray-500 mb-1.5">Skill yang cocok:</p>
                    <div className="flex flex-wrap gap-1">
                      {app.matched_skills.slice(0, 5).map((s) => (
                        <span key={s} className="badge badge-teal text-xs">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {app.missing_skills?.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1.5">Skill yang kurang:</p>
                    <div className="flex flex-wrap gap-1">
                      {app.missing_skills.slice(0, 4).map((s) => (
                        <span key={s} className="badge bg-red-50 text-red-500 text-xs">{s}</span>
                      ))}
                    </div>
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
