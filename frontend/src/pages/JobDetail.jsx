import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { MapPin, Clock, Briefcase, Monitor, TrendingUp, BookmarkPlus, BookmarkCheck, Building2, ExternalLink, Zap, AlertCircle } from "lucide-react";
import { getJob, saveJob, unsaveJob, checkSaved, applyJob, aiSalaryPrediction } from "../lib/api";
import { formatIDR, timeAgo, EMPLOYMENT_LABELS, WORK_MODE_LABELS, EXPERIENCE_LABELS } from "../lib/utils";
import Spinner from "../components/ui/Spinner";
import JobCard from "../components/JobCard";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-toastify";

export default function JobDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(false);
  const [coverLetter, setCoverLetter] = useState("");
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [salaryInsight, setSalaryInsight] = useState(null);
  const [salaryLoading, setSalaryLoading] = useState(false);

  const loadJob = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await getJob(slug);
      setJob(data);
    } catch {
      toast.error("Lowongan tidak ditemukan");
      navigate("/jobs");
    } finally {
      setLoading(false);
    }
  }, [slug, navigate]);

  useEffect(() => { loadJob(); }, [loadJob]);

  useEffect(() => {
    if (user?.role === "candidate" && job) {
      checkSaved(job.id).then(({ data }) => setSaved(data.saved)).catch(() => {});
    }
  }, [user, job]);

  const handleSave = async () => {
    if (!user) { toast.info("Login untuk menyimpan"); return; }
    try {
      if (saved) { await unsaveJob(job.id); setSaved(false); toast.success("Dihapus dari simpanan"); }
      else { await saveJob(job.id); setSaved(true); toast.success("Disimpan!"); }
    } catch { toast.error("Gagal"); }
  };

  const handleApply = async () => {
    if (!user) { navigate("/login"); return; }
    if (user.role !== "candidate") { toast.info("Hanya kandidat yang bisa melamar"); return; }
    setApplying(true);
    try {
      await applyJob({ job_id: job.id, cover_letter: coverLetter });
      setApplied(true);
      setShowApplyModal(false);
      toast.success("Lamaran berhasil dikirim! 🎉");
    } catch (e) {
      const msg = e.response?.data?.detail || "Gagal melamar";
      if (msg.includes("sudah melamar")) { setApplied(true); toast.info("Kamu sudah melamar lowongan ini"); }
      else toast.error(msg);
    } finally {
      setApplying(false);
    }
  };

  const loadSalaryInsight = async () => {
    if (!job || salaryInsight) return;
    setSalaryLoading(true);
    try {
      const { data } = await aiSalaryPrediction({
        title: job.title,
        location: job.location,
        years_experience: job.min_years || 0,
        level: job.experience_level,
        skills: job.skills || [],
      });
      setSalaryInsight(data);
    } catch { toast.error("Gagal memuat salary insight"); }
    finally { setSalaryLoading(false); }
  };

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-12"><Spinner center /></div>;
  if (!job) return null;

  const company = job.company || {};

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main */}
        <div className="lg:col-span-2 space-y-5">
          {/* Header card */}
          <div className="card p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                {company.logo_url ? (
                  <img src={company.logo_url} alt={company.name} className="w-14 h-14 rounded-xl object-cover bg-gray-50" />
                ) : (
                  <div className="w-14 h-14 rounded-xl bg-fountain-mint flex items-center justify-center text-jungle-teal font-bold text-lg">
                    {company.name?.[0] || "?"}
                  </div>
                )}
                <div>
                  <h1 className="text-xl font-bold text-forgotten-blue">{job.title}</h1>
                  <Link to={`/companies/${company.slug}`} className="text-jungle-teal text-sm font-medium hover:underline flex items-center gap-1">
                    {company.name} <ExternalLink size={12} />
                  </Link>
                  <p className="text-gray-400 text-xs mt-1">{timeAgo(job.created_at)}</p>
                </div>
              </div>
              <button onClick={handleSave} className="text-gray-400 hover:text-jungle-teal transition-colors flex-shrink-0">
                {saved ? <BookmarkCheck size={22} className="text-jungle-teal" /> : <BookmarkPlus size={22} />}
              </button>
            </div>

            {/* Meta badges */}
            <div className="flex flex-wrap gap-2 mt-4">
              <span className="badge badge-teal"><MapPin size={11} /> {job.location}</span>
              <span className="badge badge-blue"><Monitor size={11} /> {WORK_MODE_LABELS[job.work_mode]}</span>
              <span className="badge bg-purple-50 text-purple-700"><Briefcase size={11} /> {EMPLOYMENT_LABELS[job.employment_type]}</span>
              <span className="badge bg-orange-50 text-orange-700"><TrendingUp size={11} /> {EXPERIENCE_LABELS[job.experience_level]}</span>
              {job.min_years > 0 && <span className="badge bg-gray-100 text-gray-600">{job.min_years}+ thn pengalaman</span>}
              {job.is_featured && <span className="badge bg-yellow-50 text-yellow-700">⭐ Featured</span>}
            </div>

            {/* Salary */}
            {(job.salary_min || job.salary_max) && (
              <div className="mt-4 p-3 bg-fountain-mint rounded-xl">
                <p className="text-xs text-gray-500 mb-0.5">Estimasi Gaji</p>
                <p className="text-lg font-bold text-jungle-teal">
                  {job.salary_min && job.salary_max
                    ? `${formatIDR(job.salary_min)} – ${formatIDR(job.salary_max)}`
                    : job.salary_min ? `≥ ${formatIDR(job.salary_min)}` : `≤ ${formatIDR(job.salary_max)}`}
                  <span className="text-sm font-normal text-gray-500">/bulan</span>
                </p>
              </div>
            )}

            {/* Apply button */}
            <div className="mt-4">
              {applied ? (
                <div className="flex items-center gap-2 text-green-600 text-sm font-medium">
                  <Zap size={16} /> Lamaran sudah dikirim!
                </div>
              ) : user?.role === "candidate" ? (
                <button
                  onClick={() => setShowApplyModal(true)}
                  className="btn-primary w-full sm:w-auto"
                  data-testid="apply-btn"
                >
                  Lamar Sekarang
                </button>
              ) : !user ? (
                <Link to="/login" className="btn-primary inline-block">
                  Login untuk Melamar
                </Link>
              ) : null}
            </div>
          </div>

          {/* Description */}
          <div className="card p-6">
            <h2 className="font-bold text-forgotten-blue mb-3">Deskripsi Pekerjaan</h2>
            <div className="prose prose-sm max-w-none text-gray-600 leading-relaxed whitespace-pre-wrap text-sm">
              {job.description}
            </div>
          </div>

          {/* Requirements */}
          <div className="card p-6">
            <h2 className="font-bold text-forgotten-blue mb-3">Persyaratan</h2>
            <div className="prose prose-sm max-w-none text-gray-600 leading-relaxed whitespace-pre-wrap text-sm">
              {job.requirements}
            </div>
          </div>

          {/* Skills */}
          {job.skills?.length > 0 && (
            <div className="card p-6">
              <h2 className="font-bold text-forgotten-blue mb-3">Skill yang Dibutuhkan</h2>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((s) => (
                  <span key={s} className="badge badge-teal text-sm">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-5">
          {/* Company info */}
          <div className="card p-5">
            <h3 className="font-semibold text-forgotten-blue mb-3 text-sm">Tentang Perusahaan</h3>
            <div className="flex items-center gap-3 mb-3">
              {company.logo_url ? (
                <img src={company.logo_url} alt={company.name} className="w-10 h-10 rounded-lg" />
              ) : (
                <div className="w-10 h-10 rounded-lg bg-fountain-mint flex items-center justify-center text-jungle-teal font-bold">
                  {company.name?.[0]}
                </div>
              )}
              <div>
                <p className="font-semibold text-sm text-forgotten-blue">{company.name}</p>
                {company.location && <p className="text-xs text-gray-400">{company.location}</p>}
              </div>
            </div>
            <Link to={`/companies/${company.slug}`} className="text-jungle-teal text-xs font-medium flex items-center gap-1 hover:underline">
              <Building2 size={12} /> Lihat Profil Perusahaan
            </Link>
          </div>

          {/* AI Salary Insight */}
          <div className="card p-5">
            <div className="flex items-center gap-2 mb-3">
              <Zap size={16} className="text-jungle-teal" />
              <h3 className="font-semibold text-forgotten-blue text-sm">AI Salary Insight</h3>
            </div>
            {salaryInsight ? (
              <div>
                <p className="text-lg font-bold text-jungle-teal">
                  {formatIDR(salaryInsight.salary_min)} – {formatIDR(salaryInsight.salary_max)}
                </p>
                <p className="text-xs text-gray-500 mt-1">/bulan · Confidence: <span className="font-medium">{salaryInsight.confidence}</span></p>
                <p className="text-xs text-gray-600 mt-2 leading-relaxed">{salaryInsight.rationale}</p>
                {salaryInsight.assumptions?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {salaryInsight.assumptions.slice(0, 3).map((a, i) => (
                      <li key={i} className="text-xs text-gray-400 flex items-start gap-1">
                        <span className="text-jungle-teal mt-0.5">•</span> {a}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <button
                onClick={loadSalaryInsight}
                disabled={salaryLoading}
                className="w-full py-2 rounded-xl border-2 border-dashed border-teal-200 text-jungle-teal text-sm font-medium hover:bg-fountain-mint transition-colors flex items-center justify-center gap-2"
              >
                {salaryLoading ? <><div className="spinner w-4 h-4" /> Memuat...</> : <><Zap size={14} /> Lihat Estimasi Gaji AI</>}
              </button>
            )}
          </div>

          {/* Job summary */}
          <div className="card p-5">
            <h3 className="font-semibold text-forgotten-blue mb-3 text-sm">Ringkasan</h3>
            <div className="space-y-2 text-sm">
              {[
                ["Tipe", EMPLOYMENT_LABELS[job.employment_type]],
                ["Mode Kerja", WORK_MODE_LABELS[job.work_mode]],
                ["Level", EXPERIENCE_LABELS[job.experience_level]],
                ["Pengalaman", job.min_years ? `${job.min_years}+ tahun` : "Tidak ditentukan"],
                ["Dilihat", `${job.views || 0}x`],
                ["Pelamar", `${job.applications_count || 0} orang`],
              ].map(([label, val]) => (
                <div key={label} className="flex justify-between">
                  <span className="text-gray-400">{label}</span>
                  <span className="font-medium text-gray-700">{val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Related jobs */}
      {job.related?.length > 0 && (
        <div className="mt-10">
          <h2 className="font-bold text-forgotten-blue mb-4">Lowongan Serupa</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {job.related.map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        </div>
      )}

      {/* Apply Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="font-bold text-forgotten-blue mb-1">Lamar: {job.title}</h3>
            <p className="text-sm text-gray-400 mb-4">{company.name}</p>
            <div className="bg-fountain-mint rounded-xl p-3 mb-4 flex items-start gap-2">
              <AlertCircle size={14} className="text-jungle-teal mt-0.5 flex-shrink-0" />
              <p className="text-xs text-teal-700">Profil & skill kamu akan otomatis disertakan. AI akan menghitung match score lamaranmu.</p>
            </div>
            <div className="mb-4">
              <label className="text-xs font-medium text-gray-600 mb-1 block">Cover Letter (opsional)</label>
              <textarea
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                rows={4}
                placeholder="Ceritakan mengapa kamu cocok untuk posisi ini..."
                className="input-field text-sm resize-none"
                data-testid="cover-letter"
              />
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowApplyModal(false)} className="flex-1 btn-outline text-sm">Batal</button>
              <button
                onClick={handleApply}
                disabled={applying}
                className="flex-1 btn-primary text-sm disabled:opacity-60"
                data-testid="confirm-apply"
              >
                {applying ? "Mengirim..." : "Kirim Lamaran"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
