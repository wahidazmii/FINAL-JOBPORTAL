import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Briefcase, Eye, EyeOff, User, Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-toastify";

export default function Signup() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initRole = searchParams.get("role") || "candidate";

  const [role, setRole] = useState(initRole);
  const [form, setForm] = useState({ name: "", email: "", password: "", company_name: "" });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password.length < 6) { toast.error("Password minimal 6 karakter"); return; }
    if (role === "employer" && !form.company_name) { toast.error("Nama perusahaan wajib"); return; }
    setLoading(true);
    try {
      const payload = { ...form, role };
      if (role !== "employer") delete payload.company_name;
      const user = await register(payload);
      toast.success(`Akun berhasil dibuat! Selamat datang, ${user.name} 🎉`);
      navigate(role === "employer" ? "/employer" : "/candidate");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Pendaftaran gagal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-jungle-teal rounded-xl flex items-center justify-center mx-auto mb-3">
            <Briefcase size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-forgotten-blue">Daftar Gratis</h1>
          <p className="text-gray-400 text-sm mt-1">Mulai karir impianmu sekarang</p>
        </div>

        {/* Role toggle */}
        <div className="flex rounded-xl bg-gray-100 p-1 mb-5">
          {[
            { val: "candidate", label: "Pencari Kerja", icon: User },
            { val: "employer", label: "Perusahaan", icon: Building2 },
          ].map(({ val, label, icon: Icon }) => (
            <button
              key={val}
              onClick={() => setRole(val)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all ${role === val ? "bg-white text-jungle-teal shadow-sm" : "text-gray-500 hover:text-gray-700"}`}
              data-testid={`role-${val}`}
            >
              <Icon size={15} /> {label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              {role === "employer" ? "Nama Penanggung Jawab" : "Nama Lengkap"}
            </label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="input-field"
              placeholder="Nama kamu"
              data-testid="name-input"
            />
          </div>

          {role === "employer" && (
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">Nama Perusahaan</label>
              <input
                type="text"
                required
                value={form.company_name}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                className="input-field"
                placeholder="PT. Nama Perusahaan"
                data-testid="company-name-input"
              />
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="input-field"
              placeholder="email@contoh.com"
              data-testid="email-input"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Password</label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                required
                minLength={6}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="input-field pr-10"
                placeholder="Minimal 6 karakter"
                data-testid="password-input"
              />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full justify-center flex disabled:opacity-60" data-testid="signup-btn">
            {loading ? "Mendaftar..." : "Buat Akun"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Sudah punya akun?{" "}
          <Link to="/login" className="text-jungle-teal font-medium hover:underline">Masuk</Link>
        </p>
      </div>
    </div>
  );
}
