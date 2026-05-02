import { Link } from "react-router-dom";
import { MapPin, Clock, Zap, BookmarkPlus, BookmarkCheck } from "lucide-react";
import { formatIDR, timeAgo, EMPLOYMENT_LABELS, WORK_MODE_LABELS } from "../lib/utils";

const WORK_MODE_COLORS = {
  remote: "badge-teal",
  hybrid: "badge-blue",
  onsite: "bg-gray-100 text-gray-600 badge",
};

export default function JobCard({ job, onSave, saved }) {
  const company = job.company || {};

  return (
    <div className="card p-5 flex flex-col gap-3" data-testid="job-card">
      {/* Header */}
      <div className="flex justify-between items-start gap-2">
        <div className="flex items-center gap-3">
          {company.logo_url ? (
            <img src={company.logo_url} alt={company.name} className="w-10 h-10 rounded-xl object-cover bg-gray-50" />
          ) : (
            <div className="w-10 h-10 rounded-xl bg-fountain-mint flex items-center justify-center text-jungle-teal font-bold text-sm">
              {company.name?.[0] || "?"}
            </div>
          )}
          <div>
            <p className="text-xs text-gray-400 font-medium">{company.name}</p>
            {job.is_featured && (
              <span className="badge bg-yellow-50 text-yellow-700 text-xs">⭐ Featured</span>
            )}
          </div>
        </div>

        {onSave && (
          <button
            onClick={(e) => { e.preventDefault(); onSave(job.id, saved); }}
            className="text-gray-400 hover:text-jungle-teal transition-colors"
            data-testid="save-btn"
          >
            {saved ? <BookmarkCheck size={18} className="text-jungle-teal" /> : <BookmarkPlus size={18} />}
          </button>
        )}
      </div>

      {/* Title */}
      <Link to={`/jobs/${job.slug}`} className="font-semibold text-forgotten-blue hover:text-jungle-teal transition-colors text-sm leading-snug">
        {job.title}
      </Link>

      {/* Meta */}
      <div className="flex flex-wrap gap-2">
        <span className={WORK_MODE_COLORS[job.work_mode] || "badge bg-gray-100 text-gray-600"}>
          {WORK_MODE_LABELS[job.work_mode] || job.work_mode}
        </span>
        <span className="badge bg-gray-100 text-gray-600">
          {EMPLOYMENT_LABELS[job.employment_type] || job.employment_type}
        </span>
        {job.match_score != null && (
          <span className={`badge ${job.match_score >= 70 ? "badge-teal" : "bg-orange-50 text-orange-600 badge"}`}>
            <Zap size={10} /> {job.match_score}% match
          </span>
        )}
      </div>

      {/* Location + time */}
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span className="flex items-center gap-1"><MapPin size={12} /> {job.location}</span>
        <span className="flex items-center gap-1"><Clock size={12} /> {timeAgo(job.created_at)}</span>
      </div>

      {/* Salary */}
      {(job.salary_min || job.salary_max) && (
        <div className="text-sm font-semibold text-jungle-teal border-t border-gray-50 pt-2">
          {job.salary_min && job.salary_max
            ? `${formatIDR(job.salary_min)} – ${formatIDR(job.salary_max)}`
            : job.salary_min
            ? `≥ ${formatIDR(job.salary_min)}`
            : `≤ ${formatIDR(job.salary_max)}`}
          <span className="text-xs text-gray-400 font-normal">/bulan</span>
        </div>
      )}

      {/* Skills */}
      {job.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {job.skills.slice(0, 4).map((s) => (
            <span key={s} className="badge bg-gray-50 text-gray-600 text-xs">{s}</span>
          ))}
          {job.skills.length > 4 && (
            <span className="badge bg-gray-50 text-gray-500 text-xs">+{job.skills.length - 4}</span>
          )}
        </div>
      )}
    </div>
  );
}
