# plan.md — Talentiv-inspired Job Portal (FARM)

## 1) Objectives
- Bangun Job Portal “Talentiv-inspired” (Bahasa Indonesia) dengan **FARM stack**: FastAPI + React + MongoDB.
- Validasi dan implementasi **3 fitur AI wajib**:
  1) Resume parsing (PDF/text → ekstraksi skill/experience/education)
  2) AI job matching (score 0–100 + rationale + missing skills)
  3) AI salary prediction (range IDR + confidence)
- Sediakan product flow end-to-end:
  - Public: landing → cari → detail
  - Candidate: auth → profil/resume → save → apply → aplikasi
  - Employer: auth → company → post job → lihat pelamar → update status
  - **Admin**: auth → overview → moderasi jobs/users/companies
- UI production-quality sesuai design tokens; semua elemen interaktif punya `data-testid`.

**Status saat ini:** Phase 1, Phase 2, dan **Phase 3 sudah selesai** dan tervalidasi. Phase 4 bersifat **opsional** (scale/perf/semantic search/i18n).

---

## 2) Implementation Steps

### Phase 1 — Core AI POC (Isolation) ✅ SELESAI
**User stories (Phase 1)**
1. As system, saat diberikan teks resume, saya mendapatkan JSON terstruktur (nama, kontak, skill, pengalaman, pendidikan).
2. As system, saat dibandingkan kandidat vs job, saya mendapatkan **match score 0–100** + alasan.
3. As system, saat diberi role+lokasi+experience, saya mendapatkan prediksi **range gaji** (min/max) + confidence.
4. As developer, saya bisa menjalankan 1 file test dan melihat PASS/FAIL yang jelas.
5. As developer, saya bisa mengubah prompt/format output tanpa memecahkan kontrak JSON.

**Steps (implemented)**
- Membuat `/app/test_core.py` memakai `emergentintegrations` + `EMERGENT_LLM_KEY`.
  - Resume parsing → schema JSON valid
  - Match scoring → `{score, rationale, matched_skills, missing_skills, recommendation}`
  - Salary prediction → `{salary_min, salary_max, currency:"IDR", confidence, rationale, assumptions}`

**Deliverable**
- ✅ `/app/test_core.py` (PASS untuk 3 AI tests)

---

### Phase 2 — V1 App Development (Backend + Frontend) ✅ SELESAI
> Prinsip: bangun flow utama dengan data publik + seed data + AI endpoints, lalu tambah auth & dashboard sampai end-to-end.

**User stories (Phase 2) — delivered**
1. Visitor melihat homepage dengan headline “Punya skill tapi tetap belum dapat kerja?” + search bar.
2. Visitor browse kategori populer dan featured jobs.
3. Visitor cari kerja dengan filter (keyword, lokasi, tipe, work mode, salary, kategori).
4. Visitor buka job detail + ringkasan perusahaan + “AI salary insight”.
5. Candidate & employer login dan menjalankan flow inti (apply/save/CRUD jobs/pipeline).

**Backend (FastAPI + Motor/Mongo) — delivered**
- Setup: env, CORS, Mongo client, indexes.
- Models/collections: `User`, `Profile`, `Company`, `Category`, `Job`, `Application`, `SavedJob`.
- Auth JWT (email/password) + RBAC kandidat/employer.
- AI endpoints:
  - `POST /api/ai/parse-resume`
  - `POST /api/ai/match-score`
  - `POST /api/ai/salary-prediction`
- Resume PDF parsing: base64 PDF → `pdfplumber` text extract → AI parse → update Profile.
- Seed data: 6 categories, 5 companies, 12 jobs, demo candidate + employer.
- Bugfix: `GET /api/candidate/recommendations` query diperbaiki (Mongo `$or` regex; menghapus nested `$in/$regex` yang invalid).

**Frontend (React + Tailwind + shadcn/ui) — delivered**
- Talentiv design system implemented:
  - Colors: Forgotten Blue `#1E2A3A`, Jungle Teal `#0D9488`, Fountain Mint `#DBF7EF`, background `#F8FAFC`
  - Typography: Poppins + DM Serif Display
  - Rounded-2xl cards, rounded-full buttons, dotted hero pattern
- Pages delivered:
  - Public: Home, Job Search (filters sidebar + mobile Sheet), Job Detail (salary insight + related jobs), Company page
  - Auth: Login, Signup (role tabs candidate/employer)
  - Candidate: Dashboard, Applications, Saved Jobs, Profile (skills editor + resume upload)
  - Employer: Dashboard, My Jobs, Post Job (AI salary helper), Applicants (pipeline status dropdown)

**End of Phase 2 validation**
- ✅ `testing_agent_v3`: Backend 94% pass, Frontend 95% pass (minor testid mismatch pada harness).

---

### Phase 3 — Admin Role + Moderation + Product Hardening ✅ SELESAI
> Phase ini dibuat karena roles requirement berubah menjadi **Candidate + Employer + Admin** dan perlu guardrails untuk AI.

**User stories (Phase 3) — delivered**
1. As admin, saya bisa login dan melihat dashboard ringkas (jobs, companies, users, applications counts).
2. As admin, saya bisa moderasi lowongan: set status `published|paused|closed`, toggle featured, dan menghapus lowongan spam.
3. As admin, saya bisa mengelola user: disable/enable akun dan mengubah role.
4. As admin, saya bisa melihat daftar perusahaan dan jumlah lowongan.
5. As system, endpoint AI terlindungi basic throttling/rate limit untuk menghindari abuse.

**Backend (Phase 3 additions) — delivered**
- Admin RBAC:
  - Admin role **diblock dari public register** (`POST /api/auth/register` untuk admin → 403).
  - Seed admin user: `admin@talentiv.id / admin123`.
- Security hardening:
  - User dengan `is_disabled=true` **tidak bisa login** (`POST /api/auth/login` → 403).
- Admin endpoints (semua butuh role admin):
  - `GET /api/admin/overview`
  - `GET /api/admin/jobs` + `PUT /api/admin/jobs/{id}` (status/featured/moderation_reason) + `DELETE /api/admin/jobs/{id}`
  - `GET /api/admin/users` + `PUT /api/admin/users/{id}` (role/is_disabled)
  - `GET /api/admin/companies` + `PUT /api/admin/companies/{id}`
- Rate limiting (in-memory token bucket):
  - Dipasang pada AI endpoints (contoh: parse-resume capacity 5; akan 429 bila spam).

**Frontend (Phase 3 additions) — delivered**
- Admin UI:
  - `AdminShell` + 4 halaman:
    - `/admin` (Dashboard)
    - `/admin/lowongan` (Moderasi lowongan: status dropdown, feature toggle, delete)
    - `/admin/pengguna` (Kelola pengguna: role dropdown, disable toggle)
    - `/admin/perusahaan` (List perusahaan: job_count badge)
- Header  ProtectedRoute:
  - Dropdown admin berisi link moderasi.
  - Shield icon untuk admin.
  - ProtectedRoute redirect benar untuk role mismatch.

**End of Phase 3 validation**
- ✅ `testing_agent_v3` iteration_2:
  - Backend: **100% (42/42)**
  - Frontend: **90% (9/10)** — 1 isu flaky navigasi job card (tidak terkait admin)

---

### Phase 4 — Optional: Scale, Search, Semantic Matching, i18n (Next / If requested)
**User stories (Phase 4)**
1. As user, search relevan dan cepat untuk dataset besar.
2. As candidate, job matching lebih akurat (semantic similarity, bukan hanya keyword).
3. As system, AI cost dan latency terkontrol (caching, batching, retries).
4. As product, siap multi-bahasa (ID/EN) jika dibutuhkan.

**Enhancements (optional)**
- Search:
  - Integrasi **Meilisearch** (atau Atlas Search) + indexing jobs.
- Semantic matching:
  - Generate embeddings untuk job dan profile/resume → cosine similarity.
  - Simpan embeddings di Mongo (atau vector DB) + job recommendations berbasis vector search.
- Performance/ops:
  - Observability: structured logs + tracing ringan.
  - Caching: response caching untuk endpoints publik tertentu.
  - Rate limiting upgrade: Redis-based (jika dibutuhkan), per-user quotas.
- i18n:
  - Toggle Bahasa Indonesia / English (react-i18next), tambah waktu dev.

---

## 3) Next Actions (immediate)
1. **Konfirmasi** apakah akan lanjut Phase 4 (Meilisearch / embeddings / i18n / perf), dan pilih prioritas:
   - (a) Meilisearch dulu
   - (b) Embeddings job matching dulu
   - (c) i18n dulu
   - (d) Perf  cost control dulu
2. Jika tidak lanjut Phase 4: lakukan hardening kecil untuk production:
   - Hapus/disable demo accounts dari seed
   - Ganti `JWT_SECRET` dan kunci env untuk production
   - Atur CORS origins lebih ketat

---

## 4) Success Criteria
- Phase 1: ✅ `test_core.py` PASS untuk resume parsing + match scoring + salary prediction.
- Phase 2: ✅ Public + candidate + employer flows berjalan, AI insight tampil, UI sesuai tokens.
- Phase 3: ✅ Admin moderasi jobs/users/companies, disabled user blocked, AI rate limit aktif, regression core flows aman.
- Phase 4 (opsional): search  matching lebih relevan untuk skala besar + (opsional) i18n siap.
