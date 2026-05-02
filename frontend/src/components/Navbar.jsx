import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Menu, X, Briefcase, ChevronDown, User, LogOut, LayoutDashboard, FileText, Heart, Settings } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ isAdmin }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [dropOpen, setDropOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const candidateLinks = [
    { to: "/candidate", label: "Dashboard", icon: LayoutDashboard },
    { to: "/candidate/applications", label: "Lamaranku", icon: FileText },
    { to: "/candidate/saved", label: "Disimpan", icon: Heart },
    { to: "/candidate/profile", label: "Profil", icon: User },
  ];

  const employerLinks = [
    { to: "/employer", label: "Dashboard", icon: LayoutDashboard },
    { to: "/employer/jobs", label: "Lowongan Saya", icon: Briefcase },
    { to: "/employer/jobs/new", label: "Post Lowongan", icon: FileText },
  ];

  const adminLinks = [
    { to: "/admin", label: "Overview", icon: LayoutDashboard },
    { to: "/admin/jobs", label: "Kelola Jobs", icon: Briefcase },
    { to: "/admin/users", label: "Kelola Users", icon: User },
    { to: "/admin/companies", label: "Perusahaan", icon: Settings },
  ];

  const navLinks = user?.role === "candidate" ? candidateLinks
    : user?.role === "employer" ? employerLinks
    : user?.role === "admin" ? adminLinks
    : [];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className={`${isAdmin ? "bg-forgotten-blue" : "bg-white"} shadow-sm border-b ${isAdmin ? "border-slate-700" : "border-gray-100"} sticky top-0 z-50`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-jungle-teal rounded-lg flex items-center justify-center">
              <Briefcase size={18} className="text-white" />
            </div>
            <span className={`font-bold text-lg ${isAdmin ? "text-white" : "text-forgotten-blue"}`}>
              Talentiv
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            {!isAdmin && (
              <>
                <Link to="/jobs" className={`text-sm font-medium transition-colors ${isActive("/jobs") ? "text-jungle-teal" : "text-gray-600 hover:text-jungle-teal"}`}>
                  Cari Kerja
                </Link>
                <Link to="/jobs?sort=newest" className={`text-sm font-medium transition-colors text-gray-600 hover:text-jungle-teal`}>
                  Semua Lowongan
                </Link>
              </>
            )}

            {isAdmin && adminLinks.map((l) => (
              <Link key={l.to} to={l.to} className={`text-sm font-medium transition-colors ${isActive(l.to) ? "text-teal-400" : "text-gray-300 hover:text-white"}`}>
                {l.label}
              </Link>
            ))}
          </div>

          {/* Right: Auth */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropOpen(!dropOpen)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm font-medium transition-colors ${isAdmin ? "text-white hover:bg-slate-700" : "text-gray-700 hover:bg-gray-50"}`}
                >
                  <div className="w-7 h-7 bg-jungle-teal rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {user.name?.[0]?.toUpperCase() || "U"}
                  </div>
                  <span className="max-w-[120px] truncate">{user.name}</span>
                  <ChevronDown size={14} />
                </button>

                {dropOpen && (
                  <div className="absolute right-0 top-full mt-1 w-52 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50">
                    <div className="px-3 py-2 border-b border-gray-50">
                      <p className="text-xs text-gray-400">{user.role}</p>
                      <p className="text-sm font-medium text-gray-800 truncate">{user.email}</p>
                    </div>
                    {navLinks.map((l) => (
                      <Link
                        key={l.to}
                        to={l.to}
                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => setDropOpen(false)}
                      >
                        <l.icon size={14} className="text-gray-400" />
                        {l.label}
                      </Link>
                    ))}
                    <button
                      onClick={() => { handleLogout(); setDropOpen(false); }}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 w-full"
                    >
                      <LogOut size={14} />
                      Keluar
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium text-gray-600 hover:text-jungle-teal transition-colors">
                  Masuk
                </Link>
                <Link to="/signup" className="btn-primary text-sm">
                  Daftar Gratis
                </Link>
              </>
            )}
          </div>

          {/* Mobile hamburger */}
          <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={20} className={isAdmin ? "text-white" : "text-gray-600"} /> : <Menu size={20} className={isAdmin ? "text-white" : "text-gray-600"} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className={`md:hidden ${isAdmin ? "bg-forgotten-blue border-slate-700" : "bg-white border-gray-100"} border-t py-2`}>
          {!isAdmin && (
            <>
              <Link to="/jobs" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMenuOpen(false)}>Cari Kerja</Link>
            </>
          )}
          {navLinks.map((l) => (
            <Link key={l.to} to={l.to} className={`block px-4 py-2 text-sm ${isAdmin ? "text-gray-300 hover:text-white" : "text-gray-700 hover:bg-gray-50"}`} onClick={() => setMenuOpen(false)}>
              {l.label}
            </Link>
          ))}
          {user ? (
            <button onClick={() => { handleLogout(); setMenuOpen(false); }} className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">
              Keluar
            </button>
          ) : (
            <div className="flex gap-2 px-4 py-2">
              <Link to="/login" className="btn-outline text-xs flex-1 text-center" onClick={() => setMenuOpen(false)}>Masuk</Link>
              <Link to="/signup" className="btn-primary text-xs flex-1 text-center" onClick={() => setMenuOpen(false)}>Daftar</Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
