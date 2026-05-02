import React, { useState } from "react";
import { Plus, X, Zap, Loader } from "lucide-react";
import { aiSalaryPrediction } from "../lib/api";
import { formatIDR, EMPLOYMENT_LABELS, WORK_MODE_LABELS, EXPERIENCE_LABELS } from "../lib/utils";
import { toast } from "react-toastify";

const CATEGORIES_LABELS = {
  "": "Pilih Kategori",
};

export default function JobForm({ initialData = {}, categories = [], onSubmit, submitLabel = "Simpan" }) {
  const [form, setForm] = useState({
    title: initialData.title || "",
    description: initialData.description || "",
    requirements: initialData.requirements || "",
    skills: initialData.skills || [],
    employment_type: initialData.employment_type || "full_time",
    work_mode: initialData.work_mode || "onsite",
    experience_level: initialData.experience_level || "mid",
    min_years: initialData.min_years || 0,
    salary_min: initialData.salary_min || "",
    salary_max: initialData.salary_max || "",
    location: initialData.location || "",
    category_id: initialData.category_id || "",
    status: initialData.status || "published",
  });
  const [skillInput, setSkillInput] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [salaryLoading, setSalaryLoading] = useState(false);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const addSkill = () => {
    const s = skillInput.trim();
    if (s && !form.skills.includes(s)) set("skills", [...form.skills, s]);
    setSkillInput("");
  };

  const handleSalaryAI = async () => {
    if (!form.title || !form.location) {
      toast.info("Isi judul dan lokasi dulu");
      return;
    }
    setSalaryLoading(true);
    try {
      const { data } = await aiSalaryPrediction({
        title: form.title,
        location: form.location,
        years_experience: form.min_years || 0,
        level: form.experience_level,
        skills: form.skills,
      });
      set("salary_min", data.salary_min);
      set("salary_max", data.salary_max);
      toast.success(`Estimasi AI: ${formatIDR(data.salary_min)} – ${formatIDR(data.salary_max)}`);
    } catch { toast.error("Gagal mendapatkan estimasi gaji"); }
    finally { setSalaryLoading(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description || !form.requirements || !form.location) {
      toast.error("Lengkapi semua field yang wajib");
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        min_years: parseInt(form.min_years) || 0,
        salary_min: form.salary_min ? parseInt(form.salary_min) : null,
        salary_max: form.salary_max ? parseInt(form.salary_max) : null,
        category_id: form.category_id || null,
      };
      await onSubmit(payload);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Gagal menyimpan lowongan");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Basic */}
      <div className="card p-5 space-y-4">
        <h2 className="font-semibold text-forgotten-blue text-sm">Informasi Dasar</h2>
        <div>
          <label className="text-xs font-medium text-gray-600 mb-1 block">Judul Posisi *</label>
          <input value={form.title} onChange={(e) => set("title", e.target.value)}
            placeholder="e.g. Senior Frontend Developer" className="input-field" required data-testid="title-input" />
        </div>
        <div>
          <label className="text-xs font-medium text-gray-600 mb-1 block">Lokasi *</label>
          <input value={form.location} onChange={(e) => set("location", e.target.value)}
            placeholder="e.g. Jakarta, Indonesia" className="input-field" required data-testid="location-input" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Tipe</label>
            <select value={form.employment_type} onChange={(e) => set("employment_type", e.target.value)} className="input-field text-sm">
              {Object.entries(EMPLOYMENT_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Mode Kerja</label>
            <select value={form.work_mode} onChange={(e) => set("work_mode", e.target.value)} className="input-field text-sm">
              {Object.entries(WORK_MODE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Level</label>
            <select value={form.experience_level} onChange={(e) => set("experience_level", e.target.value)} className="input-field text-sm">
              {Object.entries(EXPERIENCE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Min. Pengalaman (thn)</label>
            <input type="number" min={0} max={20} value={form.min_years} onChange={(e) => set("min_years", e.target.value)} className="input-field text-sm" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Kategori</label>
            <select value={form.category_id} onChange={(e) => set("category_id", e.target.value)} className="input-field text-sm">
              <option value="">Pilih Kategori</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Status</label>
            <select value={form.status} onChange={(e) => set("status", e.target.value)} className="input-field text-sm">
              <option value="published">Aktif</option>
              <option value="draft">Draft</option>
              <option value="paused">Dijeda</option>
            </select>
          </div>
        </div>
      </div>

      {/* Salary */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-forgotten-blue text-sm">Gaji (IDR/bulan)</h2>
          <button type="button" onClick={handleSalaryAI} disabled={salaryLoading}
            className="flex items-center gap-1.5 text-xs text-jungle-teal font-medium hover:underline disabled:opacity-60">
            {salaryLoading ? <Loader size={13} className="animate-spin" /> : <Zap size={13} />}
            AI Estimasi
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Minimum</label>
            <input type="number" value={form.salary_min} onChange={(e) => set("salary_min", e.target.value)}
              placeholder="e.g. 8000000" className="input-field text-sm" data-testid="salary-min" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-600 mb-1 block">Maksimum</label>
            <input type="number" value={form.salary_max} onChange={(e) => set("salary_max", e.target.value)}
              placeholder="e.g. 15000000" className="input-field text-sm" data-testid="salary-max" />
          </div>
        </div>
        {(form.salary_min || form.salary_max) && (
          <p className="text-xs text-jungle-teal">
            {form.salary_min && formatIDR(parseInt(form.salary_min))} {form.salary_min && form.salary_max && "–"} {form.salary_max && formatIDR(parseInt(form.salary_max))}
          </p>
        )}
      </div>

      {/* Skills */}
      <div className="card p-5">
        <h2 className="font-semibold text-forgotten-blue mb-3 text-sm">Skills yang Dibutuhkan</h2>
        <div className="flex flex-wrap gap-2 mb-2">
          {form.skills.map((s) => (
            <span key={s} className="badge badge-teal flex items-center gap-1">
              {s} <button type="button" onClick={() => set("skills", form.skills.filter((x) => x !== s))}><X size={11} /></button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input value={skillInput} onChange={(e) => setSkillInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addSkill())}
            placeholder="Tambah skill (Enter)" className="input-field text-sm flex-1" data-testid="skill-input" />
          <button type="button" onClick={addSkill} className="btn-outline text-sm px-3 py-2"><Plus size={16} /></button>
        </div>
      </div>

      {/* Description */}
      <div className="card p-5 space-y-4">
        <div>
          <label className="text-xs font-medium text-gray-600 mb-1 block">Deskripsi Pekerjaan *</label>
          <textarea value={form.description} onChange={(e) => set("description", e.target.value)}
            rows={6} placeholder="Jelaskan detail pekerjaan, tanggung jawab, benefit, dll." className="input-field text-sm resize-y"
            required data-testid="description-input" />
        </div>
        <div>
          <label className="text-xs font-medium text-gray-600 mb-1 block">Persyaratan *</label>
          <textarea value={form.requirements} onChange={(e) => set("requirements", e.target.value)}
            rows={5} placeholder="Jelaskan kualifikasi dan persyaratan pelamar." className="input-field text-sm resize-y"
            required data-testid="requirements-input" />
        </div>
      </div>

      <div className="flex justify-end">
        <button type="submit" disabled={submitting} className="btn-primary flex items-center gap-2 disabled:opacity-60" data-testid="submit-job">
          {submitting ? <><div className="spinner w-4 h-4" /> Menyimpan...</> : submitLabel}
        </button>
      </div>
    </form>
  );
}
