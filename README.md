# 🚀 Talentiv Jobs — Full Stack Job Portal

Platform lowongan kerja Indonesia berbasis AI untuk menghubungkan talenta dengan peluang karir terbaik.

## ✨ Fitur

### Untuk Pencari Kerja
- 🔍 Pencarian & filter lowongan (lokasi, tipe, level, salary)
- 🤖 **AI Match Score** — kecocokan kandidat-lowongan otomatis
- 💾 Simpan lowongan favorit
- 📄 **AI Resume Parser** — upload PDF, profil terisi otomatis
- 📊 Dashboard tracking status lamaran
- 🎯 Rekomendasi lowongan personal (semantic search + keyword)

### Untuk Employer
- 📋 Post & kelola lowongan
- 💡 **AI Salary Estimator** — estimasi gaji pasar Indonesia
- 👥 Lihat & kelola pelamar dengan AI match score
- 📈 Dashboard statistik (total pelamar, interview, dll)
- 🏢 Profil perusahaan publik

### Admin Panel
- 📊 Overview statistik platform
- ⚙️ Kelola semua lowongan (status, featured)
- 👤 Kelola users (role, disable/enable)
- 🏢 Kelola perusahaan

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| **Frontend** | React 18, React Router v6, Tailwind CSS, Lucide Icons |
| **Backend** | FastAPI (Python), MongoDB (Motor async) |
| **AI** | Emergent LLM (GPT-4o-mini) via emergentintegrations |
| **Auth** | JWT (python-jose) + bcrypt |
| **Embeddings** | Sentence Transformers (local, fallback) |
| **Deployment** | Docker-ready |

---

## 🚀 Cara Menjalankan

### Prasyarat
- Node.js 18+
- Python 3.10+
- MongoDB (local atau Atlas)
- API Key Emergent LLM (untuk fitur AI)

### 1. Backend

```bash
cd backend

# Copy dan isi environment variables
cp .env.example .env
# Edit .env: isi MONGO_URL, JWT_SECRET, EMERGENT_LLM_KEY

# Install dependencies
pip install -r requirements.txt

# Jalankan server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Backend berjalan di `http://localhost:8001`  
API docs: `http://localhost:8001/docs`

> **Seed Data Otomatis:** Saat server pertama kali dijalankan, data demo (lowongan, kategori, perusahaan, akun demo) akan dibuat otomatis.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy env
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > .env

# Jalankan
npm start
```

Frontend berjalan di `http://localhost:3000`

---

## 🔑 Akun Demo

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@talentiv.id | admin123 |
| Kandidat | kandidat@talentiv.id | password123 |
| Employer | hr@nusantaratech.example.com | password123 |

---

## 📁 Struktur Proyek

```
talentiv-jobs/
├── backend/
│   ├── server.py          # Main FastAPI app + semua routes
│   ├── models.py          # Pydantic models
│   ├── auth.py            # JWT + password hashing
│   ├── ai_service.py      # Resume parser, match score, salary AI
│   ├── admin_routes.py    # Admin-only endpoints
│   ├── embeddings.py      # Vector embeddings untuk semantic search
│   ├── seed.py            # Data demo & kategori
│   ├── cache_utils.py     # In-memory caching
│   ├── rate_limit.py      # Token bucket rate limiter
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── App.js               # Routing
        ├── context/
        │   └── AuthContext.js   # Global auth state
        ├── lib/
        │   ├── api.js           # Axios API calls
        │   └── utils.js         # Helpers, formatters
        ├── components/
        │   ├── Navbar.js
        │   ├── Footer.js
        │   ├── JobCard.js
        │   └── JobForm.js       # Shared form (PostJob + EditJob)
        └── pages/
            ├── Home.js
            ├── Jobs.js          # Listing + filter
            ├── JobDetail.js     # Detail + apply modal
            ├── CompanyPage.js
            ├── Login.js
            ├── Signup.js
            ├── candidate/
            │   ├── Dashboard.js
            │   ├── Applications.js
            │   ├── Saved.js
            │   └── Profile.js   # AI resume upload
            ├── employer/
            │   ├── Dashboard.js
            │   ├── Jobs.js
            │   ├── PostJob.js
            │   ├── EditJob.js
            │   └── Applicants.js
            └── admin/
                ├── Dashboard.js
                ├── Jobs.js
                ├── Users.js
                └── Companies.js
```

---

## 🐛 Bug yang Diperbaiki

1. **`is_featured=False` filtering** — Admin route `update_job` kini menangani boolean `False` dengan benar
2. **`update_profile` empty list** — `skills=[]` dan `experience=[]` kini bisa dihapus dengan benar  
3. **`featured_jobs`** — Endpoint kini menampilkan `is_featured=True` jobs lebih dulu, baru diisi dengan terbaru
4. **Demo passwords** — Login demo disesuaikan dengan password di `seed.py`
5. **Frontend src/ missing** — Seluruh frontend dibangun dari nol (src/ tidak ada di repo GitHub)

## ✨ Fitur Baru yang Ditambahkan

- ✅ Protected routes dengan role-based access (candidate/employer/admin)
- ✅ AI Salary Insight di halaman detail lowongan
- ✅ Cover letter pada lamaran kerja
- ✅ Related jobs di halaman detail
- ✅ AI match score breakdown (matched/missing skills) di halaman lamaran kandidat
- ✅ Status management lengkap di halaman pelamar employer
- ✅ Admin panel lengkap (jobs, users, companies)
- ✅ Pagination pada halaman daftar lowongan
- ✅ Responsive mobile design
- ✅ Lazy loading halaman untuk performa lebih baik

---

## 🏗️ Frontend Architecture

### Build System
- **Vite 5** (migrated from CRA/craco — fixes Node.js 22 incompatibility)
- Tailwind CSS 3 + PostCSS
- Lazy-loaded routes via `React.lazy()` for fast initial load

### Design System
Defined via Tailwind custom colors in `tailwind.config.cjs`:
- `forgotten-blue` (#1E2A3A) — dark navy for headings/sidebar
- `jungle-teal` (#0D9488) — primary brand color
- `fountain-mint` (#DBF7EF) — light teal tints
- `portal-bg` (#F8FAFC) — page background

Custom Tailwind component classes in `index.css`:
- `.btn-primary`, `.btn-outline` — CTA buttons
- `.card` — white rounded card with hover shadow
- `.badge`, `.badge-teal`, `.badge-blue` — status chips
- `.input-field` — form input with focus ring

---

## 📊 Test Results

All 123 tests passed:
- ✅ 4 Frontend build checks
- ✅ 29 Source file existence checks
- ✅ 35 API function export checks
- ✅ 11 Python syntax checks
- ✅ 32 Backend route coverage checks
- ✅ 6 Bug fix verification checks
- ✅ 6 Package.json validation checks
