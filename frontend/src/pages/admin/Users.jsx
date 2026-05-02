import React, { useEffect, useState } from "react";
import { Search, Shield, Ban, X } from "lucide-react";
import { adminGetUsers, adminUpdateUser } from "../../lib/api";
import { formatDate } from "../../lib/utils";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [roleFilter, setRoleFilter] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await adminGetUsers({ q: q || undefined, role: roleFilter || undefined, limit: 200 });
      setUsers(data || []);
    } catch { toast.error("Gagal memuat data"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleToggleDisable = async (id, disabled) => {
    try {
      await adminUpdateUser(id, { is_disabled: !disabled });
      setUsers((u) => u.map((x) => x.id === id ? { ...x, is_disabled: !disabled } : x));
      toast.success(!disabled ? "User dinonaktifkan" : "User diaktifkan kembali");
    } catch { toast.error("Gagal"); }
  };

  const handleRoleChange = async (id, role) => {
    try {
      await adminUpdateUser(id, { role });
      setUsers((u) => u.map((x) => x.id === id ? { ...x, role } : x));
      toast.success("Role diperbarui");
    } catch { toast.error("Gagal memperbarui role"); }
  };

  const ROLE_COLORS = {
    candidate: "badge bg-blue-900 text-blue-300",
    employer: "badge bg-purple-900 text-purple-300",
    admin: "badge bg-teal-900 text-teal-300",
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Kelola Users</h1>

      <div className="flex gap-3 mb-5">
        <div className="flex-1 flex items-center gap-2 bg-slate-800 rounded-xl px-3 py-2">
          <Search size={15} className="text-gray-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && load()}
            placeholder="Cari nama atau email..." className="flex-1 bg-transparent text-white text-sm outline-none placeholder-gray-500" />
          {q && <button onClick={() => setQ("")}><X size={13} className="text-gray-400" /></button>}
        </div>
        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
          className="bg-slate-800 text-gray-300 rounded-xl px-3 py-2 text-sm outline-none">
          <option value="">Semua Role</option>
          <option value="candidate">Kandidat</option>
          <option value="employer">Employer</option>
          <option value="admin">Admin</option>
        </select>
        <button onClick={load} className="px-4 py-2 bg-jungle-teal text-white rounded-xl text-sm font-medium hover:bg-teal-700">Cari</button>
      </div>

      {loading ? <Spinner center /> : (
        <div className="space-y-2">
          {users.map((user) => (
            <div key={user.id} className={`bg-slate-800 rounded-xl p-4 flex items-center justify-between gap-3 ${user.is_disabled ? "opacity-50" : ""}`} data-testid="admin-user-row">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 bg-jungle-teal/30 rounded-xl flex items-center justify-center text-teal-400 font-bold text-sm flex-shrink-0">
                  {user.name?.[0]?.toUpperCase()}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-white font-medium text-sm">{user.name}</p>
                    <span className={ROLE_COLORS[user.role] || "badge bg-gray-700 text-gray-300"}>{user.role}</span>
                    {user.is_disabled && <span className="badge bg-red-900 text-red-300">Dinonaktifkan</span>}
                  </div>
                  <p className="text-xs text-gray-400 truncate">{user.email} · {formatDate(user.created_at)}</p>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <select value={user.role} onChange={(e) => handleRoleChange(user.id, e.target.value)}
                  className="bg-slate-700 text-gray-300 rounded-lg px-2 py-1 text-xs outline-none">
                  <option value="candidate">Candidate</option>
                  <option value="employer">Employer</option>
                  <option value="admin">Admin</option>
                </select>
                <button onClick={() => handleToggleDisable(user.id, user.is_disabled)}
                  className={`p-1.5 rounded-lg transition-colors ${user.is_disabled ? "text-green-400 hover:bg-green-900/20" : "text-red-400 hover:bg-red-900/20"}`}
                  title={user.is_disabled ? "Aktifkan" : "Nonaktifkan"}>
                  {user.is_disabled ? <Shield size={15} /> : <Ban size={15} />}
                </button>
              </div>
            </div>
          ))}
          {users.length === 0 && <p className="text-center text-gray-500 py-12 text-sm">Tidak ada user ditemukan</p>}
        </div>
      )}
    </div>
  );
}
