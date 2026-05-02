import React, { useEffect, useState } from "react";
import { Search, Building2, X } from "lucide-react";
import { adminGetCompanies, adminUpdateCompany } from "../../lib/api";
import Spinner from "../../components/ui/Spinner";
import { toast } from "react-toastify";

export default function AdminCompanies() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState(null);
  const [editForm, setEditForm] = useState({});

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await adminGetCompanies({ q: q || undefined, limit: 100 });
      setCompanies(data || []);
    } catch { toast.error("Gagal memuat data"); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const startEdit = (company) => {
    setEditing(company.id);
    setEditForm({ name: company.name, industry: company.industry || "", location: company.location || "", website: company.website || "" });
  };

  const handleSave = async (id) => {
    try {
      await adminUpdateCompany(id, editForm);
      setCompanies((c) => c.map((x) => x.id === id ? { ...x, ...editForm } : x));
      setEditing(null);
      toast.success("Perusahaan diperbarui");
    } catch { toast.error("Gagal menyimpan"); }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <h1 className="text-2xl font-bold text-white mb-6">Kelola Perusahaan</h1>

      <div className="flex gap-3 mb-5">
        <div className="flex-1 flex items-center gap-2 bg-slate-800 rounded-xl px-3 py-2">
          <Search size={15} className="text-gray-400" />
          <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && load()}
            placeholder="Cari nama atau industri..." className="flex-1 bg-transparent text-white text-sm outline-none placeholder-gray-500" />
          {q && <button onClick={() => setQ("")}><X size={13} className="text-gray-400" /></button>}
        </div>
        <button onClick={load} className="px-4 py-2 bg-jungle-teal text-white rounded-xl text-sm font-medium hover:bg-teal-700">Cari</button>
      </div>

      {loading ? <Spinner center /> : (
        <div className="space-y-2">
          {companies.map((co) => (
            <div key={co.id} className="bg-slate-800 rounded-xl p-4" data-testid="admin-company-row">
              {editing === co.id ? (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    {[["name", "Nama"], ["industry", "Industri"], ["location", "Lokasi"], ["website", "Website"]].map(([k, label]) => (
                      <div key={k}>
                        <label className="text-xs text-gray-400 mb-1 block">{label}</label>
                        <input value={editForm[k] || ""} onChange={(e) => setEditForm({ ...editForm, [k]: e.target.value })}
                          className="bg-slate-700 text-white rounded-lg px-3 py-1.5 text-sm w-full outline-none focus:ring-1 focus:ring-jungle-teal" />
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleSave(co.id)} className="px-3 py-1.5 bg-jungle-teal text-white rounded-lg text-xs font-medium">Simpan</button>
                    <button onClick={() => setEditing(null)} className="px-3 py-1.5 bg-slate-700 text-gray-300 rounded-lg text-xs">Batal</button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {co.logo_url ? (
                      <img src={co.logo_url} alt="" className="w-9 h-9 rounded-lg object-cover flex-shrink-0" />
                    ) : (
                      <div className="w-9 h-9 rounded-lg bg-teal-900 flex items-center justify-center text-teal-400 flex-shrink-0">
                        <Building2 size={16} />
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="text-white font-medium text-sm">{co.name}</p>
                      <p className="text-xs text-gray-400 truncate">{co.industry} · {co.location} · {co.job_count} lowongan</p>
                    </div>
                  </div>
                  <button onClick={() => startEdit(co)} className="text-jungle-teal text-xs font-medium hover:underline flex-shrink-0">
                    Edit
                  </button>
                </div>
              )}
            </div>
          ))}
          {companies.length === 0 && <p className="text-center text-gray-500 py-12 text-sm">Tidak ada perusahaan ditemukan</p>}
        </div>
      )}
    </div>
  );
}
