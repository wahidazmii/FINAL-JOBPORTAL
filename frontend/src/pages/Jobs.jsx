import React, { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { Search, SlidersHorizontal, X, ChevronLeft, ChevronRight } from "lucide-react";
import { getJobs, getCategories, getSaved, saveJob, unsaveJob } from "../lib/api";
import { EMPLOYMENT_LABELS, WORK_MODE_LABELS, EXPERIENCE_LABELS } from "../lib/utils";
import JobCard from "../components/JobCard";
import Spinner from "../components/ui/Spinner";
import { useAuth } from "../context/AuthContext";
import { toast } from "react-toastify";

const SORT_OPTIONS = [
  { value: "newest", label: "Terbaru" },
  { value: "relevance", label: "Relevansi" },
  { value: "salary", label: "Gaji Tertinggi" },
];

export default function Jobs() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [savedIds, setSavedIds] = useState(new Set());
  const [showFilters, setShowFilters] = useState(false);

  const [filters, setFilters] = useState({
    q: searchParams.get("q") || "",
    location: searchParams.get("location") || "",
    employment_type: searchParams.get("employment_type") || "",
    work_mode: searchParams.get("work_mode") || "",
    experience_level: searchParams.get("experience_level") || "",
    category_id: searchParams.get("category_id") || "",
    salary_min: searchParams.get("salary_min") || "",
    sort: searchParams.get("sort") || "newest",
  });

  const PAGE_SIZE = 12;

  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, page_size: PAGE_SIZE };
      Object.entries(filters).forEach(([k, v]) => { if (v) params[k] = v; });
      const { data } = await getJobs(params);
      setJobs(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      toast.error("Gagal memuat lowongan");
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => { loadJobs(); }, [loadJobs]);

  useEffect(() => {
    getCategories().then(({ data }) => setCategories(data || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (user?.role === "candidate") {
      getSaved().then(({ data }) => setSavedIds(new Set(data.map((s) => s.job_id)))).catch(() => {});
    }
  }, [user]);

  const applyFilter = (key, val) => {
    setFilters((f) => ({ ...f, [key]: val }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({ q: "", location: "", employment_type: "", work_mode: "", experience_level: "", category_id: "", salary_min: "", sort: "newest" });
    setPage(1);
  };

  const handleSave = async (jobId, isSaved) => {
    if (!user) { toast.info("Login untuk menyimpan lowongan"); return; }
    try {
      if (isSaved) {
        await unsaveJob(jobId);
        setSavedIds((s) => { const n = new Set(s); n.delete(jobId); return n; });
        toast.success("Dihapus dari simpanan");
      } else {
        await saveJob(jobId);
        setSavedIds((s) => new Set([...s, jobId]));
        toast.success("Disimpan!");
      }
    } catch { toast.error("Gagal"); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const hasActiveFilters = Object.entries(filters).some(([k, v]) => v && k !== "sort");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Search bar */}
      <div className="flex gap-2 mb-6">
        <div className="flex-1 flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-4 py-2.5">
          <Search size={16} className="text-gray-400" />
          <input
            value={filters.q}
            onChange={(e) => applyFilter("q", e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadJobs()}
            placeholder="Cari posisi, skill, atau perusahaan..."
            className="flex-1 text-sm outline-none"
            data-testid="search-input"
          />
          {filters.q && <button onClick={() => applyFilter("q", "")}><X size={14} className="text-gray-400" /></button>}
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors ${showFilters ? "bg-jungle-teal text-white border-jungle-teal" : "bg-white text-gray-600 border-gray-200 hover:border-jungle-teal"}`}
          data-testid="filter-btn"
        >
          <SlidersHorizontal size={16} />
          Filter
          {hasActiveFilters && <span className="w-2 h-2 bg-red-500 rounded-full" />}
        </button>
        {/* Sort */}
        <select
          value={filters.sort}
          onChange={(e) => applyFilter("sort", e.target.value)}
          className="bg-white border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 outline-none"
        >
          {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>

      {/* Filters panel */}
      {showFilters && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Tipe</label>
            <select value={filters.employment_type} onChange={(e) => applyFilter("employment_type", e.target.value)}
              className="input-field text-xs">
              <option value="">Semua</option>
              {Object.entries(EMPLOYMENT_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Mode</label>
            <select value={filters.work_mode} onChange={(e) => applyFilter("work_mode", e.target.value)}
              className="input-field text-xs">
              <option value="">Semua</option>
              {Object.entries(WORK_MODE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Level</label>
            <select value={filters.experience_level} onChange={(e) => applyFilter("experience_level", e.target.value)}
              className="input-field text-xs">
              <option value="">Semua</option>
              {Object.entries(EXPERIENCE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Kategori</label>
            <select value={filters.category_id} onChange={(e) => applyFilter("category_id", e.target.value)}
              className="input-field text-xs">
              <option value="">Semua</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Lokasi</label>
            <input value={filters.location} onChange={(e) => applyFilter("location", e.target.value)}
              placeholder="e.g. Jakarta" className="input-field text-xs" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Gaji Min (juta)</label>
            <input type="number" value={filters.salary_min ? Math.round(filters.salary_min / 1000000) : ""}
              onChange={(e) => applyFilter("salary_min", e.target.value ? e.target.value * 1000000 : "")}
              placeholder="e.g. 10" className="input-field text-xs" />
          </div>
          {hasActiveFilters && (
            <div className="col-span-full">
              <button onClick={clearFilters} className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1">
                <X size={12} /> Hapus Semua Filter
              </button>
            </div>
          )}
        </div>
      )}

      {/* Results header */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {loading ? "Memuat..." : `${total.toLocaleString("id-ID")} lowongan ditemukan`}
        </p>
      </div>

      {/* Grid */}
      {loading ? (
        <Spinner center />
      ) : jobs.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="font-semibold text-gray-700 mb-2">Tidak ada lowongan ditemukan</h3>
          <p className="text-sm text-gray-400">Coba ubah filter atau kata kunci pencarian</p>
          <button onClick={clearFilters} className="btn-outline mt-4">Hapus Filter</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              saved={savedIds.has(job.id)}
              onSave={user?.role === "candidate" ? handleSave : undefined}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
            className="p-2 rounded-xl border disabled:opacity-40 hover:border-jungle-teal transition-colors">
            <ChevronLeft size={16} />
          </button>
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i;
            return (
              <button key={p} onClick={() => setPage(p)}
                className={`w-9 h-9 rounded-xl text-sm font-medium transition-colors ${p === page ? "bg-jungle-teal text-white" : "border hover:border-jungle-teal"}`}>
                {p}
              </button>
            );
          })}
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}
            className="p-2 rounded-xl border disabled:opacity-40 hover:border-jungle-teal transition-colors">
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
