import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center">
      <div className="text-8xl mb-6">🔍</div>
      <h1 className="text-3xl font-bold text-forgotten-blue mb-2">Halaman Tidak Ditemukan</h1>
      <p className="text-gray-400 mb-6">Maaf, halaman yang kamu cari tidak ada atau telah dipindahkan.</p>
      <div className="flex gap-3">
        <Link to="/" className="btn-primary">Ke Beranda</Link>
        <Link to="/jobs" className="btn-outline">Cari Lowongan</Link>
      </div>
    </div>
  );
}
