import { Link } from "react-router-dom";
import { Briefcase, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-forgotten-blue text-gray-300 pt-12 pb-6 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div className="col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 bg-jungle-teal rounded-lg flex items-center justify-center">
                <Briefcase size={16} className="text-white" />
              </div>
              <span className="text-white font-bold text-lg">Talentiv</span>
            </Link>
            <p className="text-sm text-gray-400 leading-relaxed">
              Platform karir berbasis AI untuk menghubungkan talenta Indonesia dengan peluang terbaik.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Pencari Kerja</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/jobs" className="hover:text-jungle-teal transition-colors">Cari Lowongan</Link></li>
              <li><Link to="/signup?role=candidate" className="hover:text-jungle-teal transition-colors">Daftar Sebagai Kandidat</Link></li>
              <li><Link to="/candidate/profile" className="hover:text-jungle-teal transition-colors">Upload Resume</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Perusahaan</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link to="/signup?role=employer" className="hover:text-jungle-teal transition-colors">Post Lowongan</Link></li>
              <li><Link to="/employer" className="hover:text-jungle-teal transition-colors">Dashboard Employer</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Kontak</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>info@talentiv.id</li>
              <li>Jakarta, Indonesia</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-700 pt-6 flex flex-col sm:flex-row justify-between items-center gap-2">
          <p className="text-xs text-gray-500">© 2025 Talentiv Jobs. All rights reserved.</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            Made with <Heart size={12} className="text-red-400" /> in Indonesia
          </p>
        </div>
      </div>
    </footer>
  );
}
