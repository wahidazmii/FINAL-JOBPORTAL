import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, MapPin, ArrowRight, Zap, Star, Users } from "lucide-react";
import { getCategories, getFeaturedJobs } from "../lib/api";
import JobCard from "../components/JobCard";
import Spinner from "../components/ui/Spinner";

const LOCATIONS = ["Semua", "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Bali", "Remote"];

export default function Home() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [location, setLocation] = useState("Semua");
  const [categories, setCategories] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [catRes, featRes] = await Promise.all([getCategories(), getFeaturedJobs(6)]);
      setCategories(catRes.data || []);
      setFeatured(featRes.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleSearch = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (location && location !== "Semua") params.set("location", location);
    navigate(`/jobs?${params.toString()}`);
  };

  return (
    <div>
      {/* Hero */}
      <section className="bg-forgotten-blue hero-dots relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-20 text-center">
          <div className="inline-flex items-center gap-2 bg-jungle-teal/20 rounded-full px-4 py-1.5 mb-6">
            <Zap size={14} className="text-teal-400" />
            <span className="text-teal-300 text-xs font-semibold">AI-Powered Job Matching</span>
          </div>
          <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl text-white leading-tight mb-4">
            Punya skill tapi tetap<br /><span className="text-jungle-teal">belum dapat kerja?</span>
          </h1>
          <p className="text-gray-300 text-lg mb-8 max-w-xl mx-auto">
            Temukan lowongan yang benar-benar cocok denganmu. AI kami mencocokkan skill & pengalaman kamu secara otomatis.
          </p>

          {/* Search form */}
          <form onSubmit={handleSearch} className="bg-white rounded-2xl p-3 flex flex-col sm:flex-row gap-2 shadow-xl max-w-2xl mx-auto">
            <div className="flex-1 flex items-center gap-2 px-3">
              <Search size={16} className="text-gray-400 flex-shrink-0" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Posisi, skill, atau perusahaan..."
                className="flex-1 text-sm outline-none text-gray-700 placeholder-gray-400"
                data-testid="search-input"
              />
            </div>
            <div className="flex items-center gap-2 border-l border-gray-100 pl-3">
              <MapPin size={16} className="text-gray-400 flex-shrink-0" />
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="text-sm outline-none text-gray-700 bg-transparent"
                data-testid="location-select"
              >
                {LOCATIONS.map((l) => <option key={l}>{l}</option>)}
              </select>
            </div>
            <button type="submit" className="btn-primary" data-testid="search-btn">
              Cari Sekarang
            </button>
          </form>

          {/* Stats */}
          <div className="flex justify-center gap-8 mt-8 text-sm text-gray-400">
            <span className="flex items-center gap-1"><Star size={12} className="text-yellow-400" /> 1.000+ Lowongan Aktif</span>
            <span className="flex items-center gap-1"><Users size={12} className="text-teal-400" /> 500+ Perusahaan</span>
            <span className="flex items-center gap-1"><Zap size={12} className="text-purple-400" /> AI Match Otomatis</span>
          </div>
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-forgotten-blue">Jelajahi Kategori</h2>
          <button onClick={() => navigate("/jobs")} className="text-jungle-teal text-sm font-medium flex items-center gap-1 hover:gap-2 transition-all">
            Lihat Semua <ArrowRight size={14} />
          </button>
        </div>

        {loading ? <Spinner center /> : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => navigate(`/jobs?category_id=${cat.id}`)}
                className="group card p-4 text-center hover:border-jungle-teal hover:shadow-md transition-all"
                data-testid="category-card"
              >
                {cat.image_url && (
                  <div className="w-12 h-12 rounded-xl overflow-hidden mx-auto mb-2 bg-fountain-mint">
                    <img src={cat.image_url} alt={cat.name} className="w-full h-full object-cover" />
                  </div>
                )}
                <p className="text-xs font-semibold text-forgotten-blue group-hover:text-jungle-teal transition-colors">
                  {cat.name}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">{cat.job_count} lowongan</p>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* Featured Jobs */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-forgotten-blue">Lowongan Terbaru</h2>
          <button onClick={() => navigate("/jobs")} className="text-jungle-teal text-sm font-medium flex items-center gap-1 hover:gap-2 transition-all">
            Lihat Semua <ArrowRight size={14} />
          </button>
        </div>

        {loading ? <Spinner center /> : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {featured.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </section>

      {/* CTA */}
      <section className="bg-jungle-teal py-14">
        <div className="max-w-2xl mx-auto text-center px-4">
          <h2 className="text-2xl font-bold text-white mb-3">Siap Mulai Perjalanan Karirmu?</h2>
          <p className="text-teal-100 mb-6">Daftar gratis dan biarkan AI kami mencocokkan kamu dengan lowongan yang tepat.</p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a href="/signup?role=candidate" className="bg-white text-jungle-teal rounded-full px-6 py-2.5 text-sm font-semibold hover:shadow-lg transition-all">
              Daftar Sebagai Kandidat
            </a>
            <a href="/signup?role=employer" className="border-2 border-white text-white rounded-full px-6 py-2.5 text-sm font-semibold hover:bg-white hover:text-jungle-teal transition-all">
              Post Lowongan
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
