"""
Test suite: verifies frontend build and backend structure integrity.
Runs without requiring emergentintegrations or MongoDB.
"""
import ast
import os
import json
import sys
import pathlib

REPO = pathlib.Path("/home/claude/job-portal")
FRONTEND_SRC = REPO / "frontend/src"
BACKEND = REPO / "backend"
BUILD = REPO / "frontend/build"

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
WARN = "\033[93m⚠\033[0m"

results = []

def check(label, condition, critical=True):
    status = PASS if condition else (FAIL if critical else WARN)
    results.append((label, condition, critical))
    print(f"  {status}  {label}")

# ── Frontend build ─────────────────────────────────────────────────────────────
print("\n📦 Frontend Build")
check("build/index.html exists", (BUILD / "index.html").exists())
check("build/assets/ exists",   (BUILD / "assets").is_dir())
js_files = list((BUILD / "assets").glob("*.js")) if (BUILD / "assets").exists() else []
check("at least 5 JS chunks produced", len(js_files) >= 5)
css_files = list((BUILD / "assets").glob("*.css")) if (BUILD / "assets").exists() else []
check("CSS bundle exists", len(css_files) >= 1)

# ── Frontend source files ──────────────────────────────────────────────────────
print("\n📄 Frontend Source Files")
required_pages = [
    "pages/Home.jsx", "pages/Jobs.jsx", "pages/JobDetail.jsx",
    "pages/Login.jsx", "pages/Signup.jsx", "pages/CompanyPage.jsx",
    "pages/NotFound.jsx",
    "pages/candidate/Dashboard.jsx", "pages/candidate/Applications.jsx",
    "pages/candidate/Saved.jsx",     "pages/candidate/Profile.jsx",
    "pages/employer/Dashboard.jsx",  "pages/employer/Jobs.jsx",
    "pages/employer/PostJob.jsx",    "pages/employer/EditJob.jsx",
    "pages/employer/Applicants.jsx",
    "pages/admin/Dashboard.jsx",     "pages/admin/Jobs.jsx",
    "pages/admin/Users.jsx",         "pages/admin/Companies.jsx",
]
for p in required_pages:
    check(f"src/{p}", (FRONTEND_SRC / p).exists())

required_components = [
    "components/Navbar.jsx", "components/Footer.jsx",
    "components/JobCard.jsx", "components/JobForm.jsx",
    "components/ui/Spinner.jsx",
    "context/AuthContext.jsx",
    "lib/api.js", "lib/utils.js",
    "App.jsx",
]
for c in required_components:
    check(f"src/{c}", (FRONTEND_SRC / c).exists())

# ── API completeness check ─────────────────────────────────────────────────────
print("\n🔌 API Functions (lib/api.js)")
api_js = (FRONTEND_SRC / "lib/api.js").read_text()
required_exports = [
    "register", "login", "getMe",
    "getCategories",
    "getJobs", "getFeaturedJobs", "getJob", "createJob", "updateJob", "deleteJob",
    "getMyJobs", "getEmployerStats", "getJobApplicants", "updateApplicationStatus",
    "applyJob", "getMyApplications",
    "saveJob", "unsaveJob", "getSaved", "checkSaved",
    "getProfile", "updateProfile", "uploadResume",
    "getCandidateStats", "getRecommendations",
    "aiSalaryPrediction", "aiParseResume",
    "adminOverview", "adminGetJobs", "adminUpdateJob", "adminDeleteJob",
    "adminGetUsers", "adminUpdateUser", "adminGetCompanies", "adminUpdateCompany",
]
for fn in required_exports:
    check(f"export {fn}()", f"export const {fn}" in api_js or f"export function {fn}" in api_js)

# ── Backend Python syntax ──────────────────────────────────────────────────────
print("\n🐍 Backend Python Syntax")
for pyfile in BACKEND.glob("*.py"):
    try:
        ast.parse(pyfile.read_text())
        check(f"{pyfile.name} syntax OK", True)
    except SyntaxError as e:
        check(f"{pyfile.name} syntax OK ({e})", False)

# ── Backend route coverage ─────────────────────────────────────────────────────
print("\n🛣️  Backend Routes")
server_src = (BACKEND / "server.py").read_text()
required_routes = [
    '"/auth/register"', '"/auth/login"', '"/auth/me"',
    '"/categories"',
    '"/companies/{company_id}"', '"/companies/me"',
    '"/jobs"', '"/jobs/featured"', '"/jobs/{slug}"',
    '"/employer/jobs"', '"/employer/stats"',
    '"/applications"', '"/applications/candidate"',
    '"/applications/job/{job_id}"', '"/applications/{app_id}/status"',
    '"/saved/{job_id}"', '"/saved"', '"/saved/check/{job_id}"',
    '"/profile"',
    '"/profile/resume"',
    '"/candidate/stats"', '"/candidate/recommendations"',
    '"/ai/salary-prediction"', '"/ai/match-score"', '"/ai/parse-resume"',
]
admin_src = (BACKEND / "admin_routes.py").read_text()
admin_routes = [
    '"/overview"', '"/jobs"', '"/jobs/{job_id}"',
    '"/users"', '"/users/{user_id}"',
    '"/companies"', '"/companies/{company_id}"',
]
for r in required_routes:
    check(f"server.py has route {r}", r in server_src)
for r in admin_routes:
    check(f"admin_routes.py has route {r}", r in admin_src)

# ── Bug fixes verification ─────────────────────────────────────────────────────
print("\n🐛 Bug Fixes Verification")
check("featured_jobs queries is_featured=True first",
      'is_featured": True' in server_src or '"is_featured": True' in server_src)
check("update_profile keeps empty lists",
      'isinstance(v, list)' in server_src)
check("admin update_job keeps boolean False",
      'isinstance(v, bool)' in admin_src)
check("Login demo password matches seed (password123)",
      'password123' in (FRONTEND_SRC / "pages/Login.jsx").read_text())
check("Vite config present",
      (REPO / "frontend/vite.config.js").exists())
check(".env.example exists for backend",
      (BACKEND / ".env.example").exists())

# ── Package.json validation ────────────────────────────────────────────────────
print("\n📦 Package.json")
pkg = json.loads((REPO / "frontend/package.json").read_text())
check("vite in devDependencies", "vite" in pkg.get("devDependencies", {}))
check("@vitejs/plugin-react present", "@vitejs/plugin-react" in pkg.get("devDependencies", {}))
check("react 18 present", "react" in pkg.get("dependencies", {}))
check("react-router-dom present", "react-router-dom" in pkg.get("dependencies", {}))
check("axios present", "axios" in pkg.get("dependencies", {}))
check('no "type": "module"', "type" not in pkg)

# ── Summary ────────────────────────────────────────────────────────────────────
total = len(results)
passed = sum(1 for _, ok, _ in results if ok)
critical_failures = [(label, ok, crit) for label, ok, crit in results if not ok and crit]

print(f"\n{'='*60}")
print(f"  Results: {passed}/{total} passed")
if critical_failures:
    print(f"\n  ❌ Critical failures:")
    for label, _, _ in critical_failures:
        print(f"     • {label}")
    sys.exit(1)
else:
    print(f"  🎉 All critical checks passed!")
    sys.exit(0)
