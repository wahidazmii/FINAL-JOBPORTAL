"""Seed demo data for Talentiv Jobs (idempotent, upsert by slug)."""
from __future__ import annotations

from slugify import slugify

from models import Category, Company, Job, new_id, now_iso, Profile
from auth import hash_password


CATEGORIES = [
    {
        "name": "Teknologi & IT",
        "description": "Software engineer, data, devops, dan peran teknologi lainnya.",
        "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=70&auto=format&fit=crop",
    },
    {
        "name": "Desain & Kreatif",
        "description": "UI/UX, graphic design, motion, dan konten kreatif.",
        "image_url": "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=800&q=70&auto=format&fit=crop",
    },
    {
        "name": "Marketing & Sales",
        "description": "Digital marketing, content, growth, dan sales.",
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=70&auto=format&fit=crop",
    },
    {
        "name": "Keuangan & Akuntansi",
        "description": "Finance, accounting, audit, analisa investasi.",
        "image_url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=70&auto=format&fit=crop",
    },
    {
        "name": "Kesehatan",
        "description": "Dokter, perawat, kesehatan publik, farmasi.",
        "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=70&auto=format&fit=crop",
    },
    {
        "name": "Pendidikan",
        "description": "Guru, tutor, pelatihan, kurikulum.",
        "image_url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800&q=70&auto=format&fit=crop",
    },
]

COMPANIES = [
    {
        "name": "Nusantara Tech",
        "industry": "Technology",
        "size": "201-500",
        "location": "Jakarta, Indonesia",
        "description": "Startup teknologi yang membangun produk SaaS untuk UKM Indonesia.",
        "website": "https://nusantaratech.example.com",
        "logo_url": "https://api.dicebear.com/7.x/shapes/svg?seed=nusantara&backgroundColor=0D9488",
    },
    {
        "name": "Garuda Digital",
        "industry": "Digital Agency",
        "size": "51-200",
        "location": "Bandung, Indonesia",
        "description": "Agency digital yang membantu brand meluncurkan kampanye berdampak.",
        "website": "https://garudadigital.example.com",
        "logo_url": "https://api.dicebear.com/7.x/shapes/svg?seed=garuda&backgroundColor=1E2A3A",
    },
    {
        "name": "SehatKita",
        "industry": "Healthcare",
        "size": "501-1000",
        "location": "Surabaya, Indonesia",
        "description": "Jaringan klinik modern dengan misi akses kesehatan yang merata.",
        "website": "https://sehatkita.example.com",
        "logo_url": "https://api.dicebear.com/7.x/shapes/svg?seed=sehatkita&backgroundColor=DBF7EF",
    },
    {
        "name": "RupaDesain",
        "industry": "Design Studio",
        "size": "11-50",
        "location": "Yogyakarta, Indonesia",
        "description": "Studio desain produk dan branding untuk brand lokal dan global.",
        "website": "https://rupadesain.example.com",
        "logo_url": "https://api.dicebear.com/7.x/shapes/svg?seed=rupa&backgroundColor=0D9488",
    },
    {
        "name": "BelajarBersama",
        "industry": "EdTech",
        "size": "201-500",
        "location": "Jakarta, Indonesia",
        "description": "Platform pendidikan daring untuk siswa dan profesional Indonesia.",
        "website": "https://belajarbersama.example.com",
        "logo_url": "https://api.dicebear.com/7.x/shapes/svg?seed=belajar&backgroundColor=1E2A3A",
    },
]


def _job(
    company_name: str,
    category_name: str,
    title: str,
    description: str,
    requirements: str,
    skills: list,
    location: str,
    employment_type="full_time",
    work_mode="hybrid",
    experience_level="mid",
    min_years=2,
    salary_min=10_000_000,
    salary_max=18_000_000,
):
    return dict(
        _company_name=company_name,
        _category_name=category_name,
        title=title,
        description=description,
        requirements=requirements,
        skills=skills,
        location=location,
        employment_type=employment_type,
        work_mode=work_mode,
        experience_level=experience_level,
        min_years=min_years,
        salary_min=salary_min,
        salary_max=salary_max,
    )


JOBS = [
    _job(
        "Nusantara Tech", "Teknologi & IT",
        "Senior Frontend Engineer",
        "Kami mencari Senior Frontend Engineer untuk membangun produk SaaS UKM. Kamu akan memimpin arsitektur UI, memastikan performa, dan mentoring tim.",
        "Pengalaman 4+ tahun React/TypeScript. Familiar dengan Next.js, testing, CI/CD. Mampu memimpin code review.",
        ["React", "TypeScript", "Next.js", "Tailwind CSS", "GraphQL"],
        "Jakarta, Indonesia", experience_level="senior", min_years=4,
        salary_min=22_000_000, salary_max=38_000_000,
        work_mode="hybrid",
    ),
    _job(
        "Nusantara Tech", "Teknologi & IT",
        "Backend Engineer (Python)",
        "Bangun API dan layanan backend scalable untuk produk kami. Kamu akan bekerja sama dengan tim produk dan data.",
        "3+ tahun Python (FastAPI/Django), PostgreSQL/MongoDB, Redis, Docker. Bonus: Kubernetes.",
        ["Python", "FastAPI", "MongoDB", "PostgreSQL", "Docker"],
        "Jakarta, Indonesia", experience_level="mid", min_years=3,
        salary_min=15_000_000, salary_max=28_000_000, work_mode="remote",
    ),
    _job(
        "Nusantara Tech", "Teknologi & IT",
        "Data Engineer",
        "Rancang dan jaga data pipeline untuk kebutuhan analitik dan ML. Bekerja dengan BigQuery dan Airflow.",
        "3+ tahun data engineering. SQL lanjut, Python, Airflow, warehouse (BigQuery/Snowflake).",
        ["Python", "SQL", "Airflow", "BigQuery", "ETL"],
        "Jakarta, Indonesia", experience_level="mid", min_years=3,
        salary_min=18_000_000, salary_max=32_000_000, work_mode="hybrid",
    ),
    _job(
        "Garuda Digital", "Marketing & Sales",
        "Digital Marketing Specialist",
        "Rencanakan, jalankan, dan ukur kampanye digital untuk klien fintech dan F&B.",
        "2+ tahun menjalankan FB/Google/TikTok Ads. Mampu analisis data kampanye dan optimasi CPA/ROAS.",
        ["Google Ads", "Meta Ads", "SEO", "Analytics", "Copywriting"],
        "Bandung, Indonesia", experience_level="junior", min_years=2,
        salary_min=7_000_000, salary_max=12_000_000, work_mode="onsite",
    ),
    _job(
        "Garuda Digital", "Marketing & Sales",
        "Content Strategist",
        "Kembangkan strategi konten lintas kanal dan tim editorial untuk brand klien.",
        "3+ tahun content strategy. Mampu menyusun editorial calendar, KPIs, SEO research.",
        ["Content Strategy", "SEO", "Editorial", "Copywriting"],
        "Bandung, Indonesia", experience_level="mid", min_years=3,
        salary_min=10_000_000, salary_max=18_000_000, work_mode="hybrid",
    ),
    _job(
        "RupaDesain", "Desain & Kreatif",
        "Senior UI/UX Designer",
        "Pimpin desain produk end-to-end dari riset hingga prototyping. Kolaborasi erat dengan engineering.",
        "4+ tahun UI/UX. Kuat di Figma, design system, user research, prototyping.",
        ["Figma", "UI Design", "UX Research", "Design Systems", "Prototyping"],
        "Yogyakarta, Indonesia", experience_level="senior", min_years=4,
        salary_min=15_000_000, salary_max=28_000_000, work_mode="hybrid",
    ),
    _job(
        "RupaDesain", "Desain & Kreatif",
        "Motion Graphics Designer",
        "Buat konten motion berkualitas tinggi untuk kampanye brand dan produk.",
        "2+ tahun After Effects, animasi 2D, kompositing sederhana. Portofolio wajib.",
        ["After Effects", "Premiere", "Illustrator", "Motion Design"],
        "Yogyakarta, Indonesia", experience_level="junior", min_years=2,
        salary_min=7_500_000, salary_max=13_000_000, work_mode="onsite",
    ),
    _job(
        "SehatKita", "Kesehatan",
        "Dokter Umum",
        "Layani pasien di klinik SehatKita cabang Surabaya dengan pendekatan holistik.",
        "STR aktif, pengalaman 1+ tahun di klinik/rumah sakit. Komunikatif dan empatik.",
        ["Medical", "Patient Care", "Clinical"],
        "Surabaya, Indonesia", experience_level="junior", min_years=1,
        salary_min=10_000_000, salary_max=16_000_000, work_mode="onsite",
    ),
    _job(
        "SehatKita", "Kesehatan",
        "Perawat Klinik",
        "Dukung tim medis dalam pelayanan pasien harian, edukasi, dan administrasi medis.",
        "STR perawat aktif. 1+ tahun pengalaman klinik. Teliti dan ramah.",
        ["Nursing", "Patient Care", "Clinical"],
        "Surabaya, Indonesia", experience_level="entry", min_years=1,
        salary_min=5_000_000, salary_max=8_000_000, work_mode="onsite",
    ),
    _job(
        "BelajarBersama", "Pendidikan",
        "Curriculum Designer",
        "Rancang kurikulum pembelajaran daring yang menarik dan terukur untuk siswa SMA.",
        "3+ tahun di edtech/pendidikan. Kuat instructional design dan asesmen.",
        ["Curriculum", "Instructional Design", "Assessment", "EdTech"],
        "Jakarta, Indonesia", experience_level="mid", min_years=3,
        salary_min=10_000_000, salary_max=17_000_000, work_mode="hybrid",
    ),
    _job(
        "BelajarBersama", "Pendidikan",
        "Online Math Tutor",
        "Ajar Matematika daring untuk siswa SMP/SMA dalam format kelompok kecil.",
        "S1 Matematika/Pendidikan Matematika. Suka mengajar dan sabar.",
        ["Teaching", "Mathematics", "Communication"],
        "Remote", experience_level="entry", min_years=0,
        salary_min=4_000_000, salary_max=7_000_000, work_mode="remote",
        employment_type="part_time",
    ),
    _job(
        "Nusantara Tech", "Keuangan & Akuntansi",
        "Finance Analyst",
        "Lakukan analisis keuangan, forecasting, dan pelaporan manajemen.",
        "2+ tahun finance analysis. Excel/Sheets lanjut, SQL, reporting.",
        ["Financial Analysis", "Excel", "SQL", "Forecasting"],
        "Jakarta, Indonesia", experience_level="mid", min_years=2,
        salary_min=9_000_000, salary_max=15_000_000, work_mode="hybrid",
    ),
]


DEMO_USERS = [
    {
        "email": "admin@talentiv.id",
        "password": "admin123",
        "name": "Admin Talentiv",
        "role": "admin",
    },
    {
        "email": "kandidat@talentiv.id",
        "password": "password123",
        "name": "Ahmad Wijaya",
        "role": "candidate",
        "profile": {
            "headline": "Senior Frontend Engineer",
            "summary": "Software engineer dengan passion membangun produk yang bermakna.",
            "location": "Jakarta, Indonesia",
            "phone": "+62 812-3456-7890",
            "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS", "Node.js", "GraphQL"],
            "experience": [
                {"title": "Senior Software Engineer", "company": "Tokopedia", "start": "Jan 2023", "end": None,
                 "description": "Memimpin modul checkout baru."},
            ],
            "education": [
                {"degree": "S1 Teknik Informatika", "institution": "Universitas Indonesia",
                 "start": "2016", "end": "2020", "gpa": "3.78"},
            ],
        },
    },
    {
        "email": "hr@nusantaratech.example.com",
        "password": "password123",
        "name": "Sari Pertiwi",
        "role": "employer",
        "company_name": "Nusantara Tech",
    },
]


async def seed_database(db, include_demo_users: bool = True) -> dict:
    counts = {"categories": 0, "companies": 0, "jobs": 0, "users": 0}

    # Categories
    category_map: dict = {}
    for i, c in enumerate(CATEGORIES):
        slug = slugify(c["name"])
        existing = await db.categories.find_one({"slug": slug})
        if existing:
            category_map[c["name"]] = existing["id"]
            continue
        cat = Category(name=c["name"], slug=slug, image_url=c["image_url"],
                       description=c["description"], order_rank=i)
        await db.categories.insert_one(cat.model_dump())
        category_map[c["name"]] = cat.id
        counts["categories"] += 1

    # Companies
    company_map: dict = {}
    for co in COMPANIES:
        slug = slugify(co["name"])
        existing = await db.companies.find_one({"slug": slug})
        if existing:
            company_map[co["name"]] = existing["id"]
            continue
        comp = Company(
            name=co["name"], slug=slug,
            industry=co.get("industry"), size=co.get("size"),
            location=co.get("location"), description=co.get("description"),
            website=co.get("website"), logo_url=co.get("logo_url"),
        )
        await db.companies.insert_one(comp.model_dump())
        company_map[co["name"]] = comp.id
        counts["companies"] += 1

    # Jobs
    for j in JOBS:
        slug = slugify(j["title"])
        # unique by company+slug
        existing = await db.jobs.find_one({"slug": slug, "company_id": company_map[j["_company_name"]]})
        if existing:
            continue
        # ensure slug unique globally (append -N if needed)
        base_slug = slug
        i = 1
        while await db.jobs.find_one({"slug": slug}):
            i += 1
            slug = f"{base_slug}-{i}"
        job = Job(
            company_id=company_map[j["_company_name"]],
            slug=slug,
            title=j["title"],
            description=j["description"],
            requirements=j["requirements"],
            skills=j["skills"],
            location=j["location"],
            employment_type=j["employment_type"],
            work_mode=j["work_mode"],
            experience_level=j["experience_level"],
            min_years=j["min_years"],
            salary_min=j["salary_min"],
            salary_max=j["salary_max"],
            category_id=category_map.get(j["_category_name"]),
        )
        await db.jobs.insert_one(job.model_dump())
        counts["jobs"] += 1

    # Demo users (for testing convenience)
    if not include_demo_users:
        return counts
    for u in DEMO_USERS:
        existing = await db.users.find_one({"email": u["email"].lower()})
        if existing:
            continue
        user_id = new_id()
        doc = {
            "id": user_id,
            "email": u["email"].lower(),
            "name": u["name"],
            "role": u["role"],
            "password_hash": hash_password(u["password"]),
            "created_at": now_iso(),
        }
        if u["role"] == "employer":
            comp_id = company_map.get(u.get("company_name") or "")
            if comp_id:
                # Assign owner if not set
                await db.companies.update_one(
                    {"id": comp_id, "$or": [{"owner_id": None}, {"owner_id": {"$exists": False}}]},
                    {"$set": {"owner_id": user_id}},
                )
                doc["company_id"] = comp_id
        await db.users.insert_one(doc)
        counts["users"] += 1

        if u["role"] == "candidate" and u.get("profile"):
            prof = Profile(user_id=user_id, **u["profile"])
            await db.profiles.update_one(
                {"user_id": user_id},
                {"$set": prof.model_dump()},
                upsert=True,
            )

    return counts
