import React, { useState, useRef } from "react";
import { Plus, X, Upload, Zap, Save, ChevronDown, ChevronUp } from "lucide-react";
import { updateProfile, uploadResume } from "../../lib/api";
import { useAuth } from "../../context/AuthContext";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

function SkillsEditor({ skills, onChange }) {
  const [input, setInput] = useState("");
  const add = () => {
    const s = input.trim();
    if (s && !skills.includes(s)) onChange([...skills, s]);
    setInput("");
  };
  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-2">
        {skills.map((s) => (
          <span key={s} className="badge badge-teal text-sm flex items-center gap-1">
            {s}
            <button onClick={() => onChange(skills.filter((x) => x !== s))} className="hover:text-red-500">
              <X size={11} />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())}
          placeholder="Tambah skill (Enter)"
          className="input-field text-sm flex-1"
          data-testid="skill-input"
        />
        <button onClick={add} className="btn-outline text-sm px-3 py-2"><Plus size={16} /></button>
      </div>
    </div>
  );
}

function ExperienceForm({ exp, onChange, onRemove }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="border border-gray-100 rounded-xl p-4 mb-3">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-gray-700">{exp.title || "Pengalaman Baru"} {exp.company ? `@ ${exp.company}` : ""}</p>
        <div className="flex gap-2">
          <button onClick={() => setOpen(!open)} className="text-gray-400">
            {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <button onClick={onRemove} className="text-red-400 hover:text-red-600"><X size={16} /></button>
        </div>
      </div>
      {open && (
        <div className="grid grid-cols-2 gap-3">
          {[["title", "Posisi", "col-span-2"], ["company", "Perusahaan", "col-span-2"], ["start", "Mulai", ""], ["end", "Selesai", ""]].map(([k, label, cls]) => (
            <div key={k} className={cls}>
              <label className="text-xs font-medium text-gray-500 mb-1 block">{label}</label>
              <input value={exp[k] || ""} onChange={(e) => onChange({ ...exp, [k]: e.target.value })}
                className="input-field text-sm" placeholder={label} />
            </div>
          ))}
          <div className="col-span-2">
            <label className="text-xs font-medium text-gray-500 mb-1 block">Deskripsi</label>
            <textarea value={exp.description || ""} onChange={(e) => onChange({ ...exp, description: e.target.value })}
              rows={2} className="input-field text-sm resize-none" />
          </div>
        </div>
      )}
    </div>
  );
}

function EducationForm({ edu, onChange, onRemove }) {
  return (
    <div className="border border-gray-100 rounded-xl p-4 mb-3">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-gray-700">{edu.degree || "Pendidikan Baru"}</p>
        <button onClick={onRemove} className="text-red-400"><X size={16} /></button>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {[["degree", "Gelar/Program", "col-span-2"], ["institution", "Institusi", "col-span-2"], ["start", "Mulai", ""], ["end", "Selesai", ""], ["gpa", "IPK", ""]].map(([k, label, cls]) => (
          <div key={k} className={cls}>
            <label className="text-xs font-medium text-gray-500 mb-1 block">{label}</label>
            <input value={edu[k] || ""} onChange={(e) => onChange({ ...edu, [k]: e.target.value })}
              className="input-field text-sm" placeholder={label} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function CandidateProfile() {
  const { profile, refreshMe } = useAuth();
  const fileRef = useRef();

  const [form, setForm] = useState({
    headline: profile?.headline || "",
    summary: profile?.summary || "",
    location: profile?.location || "",
    phone: profile?.phone || "",
    skills: profile?.skills || [],
    experience: profile?.experience || [],
    education: profile?.education || [],
  });

  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(form);
      await refreshMe();
      toast.success("Profil berhasil disimpan!");
    } catch { toast.error("Gagal menyimpan profil"); }
    finally { setSaving(false); }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      if (file.type === "application/pdf") {
        const buf = await file.arrayBuffer();
        const b64 = btoa(String.fromCharCode(...new Uint8Array(buf)));
        const { data } = await uploadResume({ pdf_base64: b64 });
        const parsed = data.profile || {};
        setForm((f) => ({
          ...f,
          headline: parsed.headline || f.headline,
          summary: parsed.summary || f.summary,
          location: parsed.location || f.location,
          phone: parsed.phone || f.phone,
          skills: parsed.skills?.length ? parsed.skills : f.skills,
          experience: parsed.experience?.length ? parsed.experience : f.experience,
          education: parsed.education?.length ? parsed.education : f.education,
        }));
        toast.success("Resume berhasil diparse oleh AI! 🎉");
      } else {
        const text = await file.text();
        const { data } = await uploadResume({ text });
        const parsed = data.profile || {};
        setForm((f) => ({
          ...f,
          skills: parsed.skills?.length ? parsed.skills : f.skills,
          experience: parsed.experience?.length ? parsed.experience : f.experience,
          education: parsed.education?.length ? parsed.education : f.education,
          headline: parsed.headline || f.headline,
          summary: parsed.summary || f.summary,
        }));
        toast.success("Resume diparse!");
      }
      await refreshMe();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Gagal parse resume");
    } finally { setUploading(false); }
  };

  const addExperience = () => setForm((f) => ({ ...f, experience: [...f.experience, { title: "", company: "", start: "", end: "", description: "" }] }));
  const addEducation = () => setForm((f) => ({ ...f, education: [...f.education, { degree: "", institution: "", start: "", end: "", gpa: "" }] }));

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-forgotten-blue">Edit Profil</h1>
        <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2 disabled:opacity-60" data-testid="save-profile">
          {saving ? <><div className="spinner w-4 h-4" /> Menyimpan...</> : <><Save size={16} /> Simpan</>}
        </button>
      </div>

      {/* Resume upload */}
      <div className="card p-5 mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Zap size={16} className="text-jungle-teal" />
          <h2 className="font-semibold text-forgotten-blue text-sm">Upload Resume (AI Auto-Fill)</h2>
        </div>
        <p className="text-xs text-gray-400 mb-3">Upload resume PDF atau TXT — AI akan mengisi profil kamu otomatis.</p>
        <input ref={fileRef} type="file" accept=".pdf,.txt" onChange={handleFileUpload} className="hidden" data-testid="resume-upload" />
        <button
          onClick={() => fileRef.current.click()}
          disabled={uploading}
          className="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-teal-200 rounded-xl text-jungle-teal text-sm hover:bg-fountain-mint transition-colors disabled:opacity-60"
        >
          {uploading ? <><div className="spinner w-4 h-4" /> Memproses AI...</> : <><Upload size={16} /> Pilih File Resume</>}
        </button>
      </div>

      {/* Basic info */}
      <div className="card p-5 mb-5 space-y-4">
        <h2 className="font-semibold text-forgotten-blue text-sm">Informasi Dasar</h2>
        {[["headline", "Headline / Jabatan", "e.g. Full Stack Developer | 3 Tahun Pengalaman"], ["summary", "Ringkasan", "Ceritakan tentang dirimu..."], ["location", "Lokasi", "e.g. Jakarta, Indonesia"], ["phone", "Nomor Telepon", "e.g. 08123456789"]].map(([k, label, ph]) => (
          <div key={k}>
            <label className="text-xs font-medium text-gray-600 mb-1 block">{label}</label>
            {k === "summary" ? (
              <textarea value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })}
                rows={3} placeholder={ph} className="input-field text-sm resize-none" data-testid={`${k}-input`} />
            ) : (
              <input value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })}
                placeholder={ph} className="input-field text-sm" data-testid={`${k}-input`} />
            )}
          </div>
        ))}
      </div>

      {/* Skills */}
      <div className="card p-5 mb-5">
        <h2 className="font-semibold text-forgotten-blue mb-3 text-sm">Skills</h2>
        <SkillsEditor skills={form.skills} onChange={(s) => setForm({ ...form, skills: s })} />
      </div>

      {/* Experience */}
      <div className="card p-5 mb-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-forgotten-blue text-sm">Pengalaman Kerja</h2>
          <button onClick={addExperience} className="text-jungle-teal text-xs flex items-center gap-1 hover:underline"><Plus size={14} /> Tambah</button>
        </div>
        {form.experience.map((exp, i) => (
          <ExperienceForm key={i} exp={exp}
            onChange={(upd) => setForm((f) => ({ ...f, experience: f.experience.map((x, j) => j === i ? upd : x) }))}
            onRemove={() => setForm((f) => ({ ...f, experience: f.experience.filter((_, j) => j !== i) }))}
          />
        ))}
        {form.experience.length === 0 && <p className="text-xs text-gray-400 text-center py-4">Belum ada pengalaman. Klik "Tambah" untuk menambahkan.</p>}
      </div>

      {/* Education */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-forgotten-blue text-sm">Pendidikan</h2>
          <button onClick={addEducation} className="text-jungle-teal text-xs flex items-center gap-1 hover:underline"><Plus size={14} /> Tambah</button>
        </div>
        {form.education.map((edu, i) => (
          <EducationForm key={i} edu={edu}
            onChange={(upd) => setForm((f) => ({ ...f, education: f.education.map((x, j) => j === i ? upd : x) }))}
            onRemove={() => setForm((f) => ({ ...f, education: f.education.filter((_, j) => j !== i) }))}
          />
        ))}
        {form.education.length === 0 && <p className="text-xs text-gray-400 text-center py-4">Belum ada pendidikan. Klik "Tambah" untuk menambahkan.</p>}
      </div>

      <div className="mt-5 flex justify-end">
        <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2 disabled:opacity-60">
          {saving ? "Menyimpan..." : <><Save size={16} /> Simpan Profil</>}
        </button>
      </div>
    </div>
  );
}
