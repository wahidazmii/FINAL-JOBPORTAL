import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Briefcase, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-toastify";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(form.email, form.password);
      toast.success(`Selamat datang, ${user.name}! 👋`);
      const paths = { candidate: "/candidate", employer: "/employer", admin: "/admin" };
      navigate(paths[user.role] || "/");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Email atau password salah");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (role) => {
    const accounts = {
      candidate: { email: "kandidat@talentiv.id", password: "password123" },
      employer: { email: "hr@nusantaratech.example.com", password: "password123" },
      admin: { email: "admin@talentiv.id", password: "admin123" },
    };
    setForm(accounts[role]);
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-jungle-teal rounded-xl flex items-center justify-center mx-auto mb-3">
            <Briefcase size={22} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-forgotten-blue">Masuk ke Talentiv</h1>
          <p className="text-gray-400 text-sm mt-1">Lanjutkan perjalanan karirmu</p>
        </div>

        {/* Demo accounts */}
        <div className="bg-fountain-mint rounded-xl p-3 mb-5">
          <p className="text-xs font-semibold text-teal-700 mb-2">🔑 Akun Demo</p>
          <div className="flex gap-2 flex-wrap">
            {["candidate", "employer", "admin"].map((r) => (
              <button key={r} onClick={() => fillDemo(r)}
                className="text-xs px-2.5 py-1 bg-white rounded-lg text-jungle-teal font-medium hover:bg-teal-50 transition-colors capitalize">
                {r}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
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
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="input-field pr-10"
                placeholder="••••••••"
                data-testid="password-input"
              />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full justify-center flex disabled:opacity-60" data-testid="login-btn">
            {loading ? "Masuk..." : "Masuk"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          Belum punya akun?{" "}
          <Link to="/signup" className="text-jungle-teal font-medium hover:underline">Daftar gratis</Link>
        </p>
      </div>
    </div>
  );
}
