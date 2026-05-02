"""Comprehensive backend API tests for Talentiv Jobs."""
import requests
import sys
import json
from datetime import datetime

BASE_URL = "https://job-search-ai-2.preview.emergentagent.com/api"

class TalentivAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.candidate_token = None
        self.employer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.category_id = None
        self.job_id = None
        self.application_id = None
        self.saved_job_id = None

    def log(self, msg, level="INFO"):
        print(f"[{level}] {msg}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, params=None):
        """Run a single API test."""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name} (Status: {response.status_code})", "PASS")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ FAILED - {name} (Expected {expected_status}, got {response.status_code})", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "FAIL")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            self.log(f"❌ FAILED - {name} (Error: {str(e)})", "FAIL")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    # ========== BASIC TESTS ==========
    def test_health(self):
        """Test health endpoint."""
        return self.run_test("Health Check", "GET", "health", 200)

    # ========== CATEGORIES ==========
    def test_categories(self):
        """Test GET /categories returns 6 seeded categories with image_url."""
        success, data = self.run_test("Get Categories", "GET", "categories", 200)
        if success:
            if not isinstance(data, list):
                self.log("❌ Categories response is not a list", "FAIL")
                return False
            if len(data) < 6:
                self.log(f"❌ Expected at least 6 categories, got {len(data)}", "FAIL")
                return False
            # Check first category has image_url
            if data and not data[0].get('image_url'):
                self.log("❌ Categories missing image_url", "FAIL")
                return False
            self.category_id = data[0]['id']
            self.log(f"✅ Found {len(data)} categories with image_url", "PASS")
        return success

    # ========== JOBS ==========
    def test_jobs_list(self):
        """Test GET /jobs returns 12 jobs with total+pagination."""
        success, data = self.run_test("Get Jobs List", "GET", "jobs", 200)
        if success:
            if 'items' not in data or 'total' not in data:
                self.log("❌ Jobs response missing items or total", "FAIL")
                return False
            if len(data['items']) < 12:
                self.log(f"⚠️  Expected 12 jobs, got {len(data['items'])}", "WARN")
            if data['items']:
                self.job_id = data['items'][0]['id']
            self.log(f"✅ Found {data['total']} total jobs, {len(data['items'])} in page", "PASS")
        return success

    def test_jobs_filter_query(self):
        """Test GET /jobs?q=engineer filters results."""
        success, data = self.run_test("Filter Jobs by Query", "GET", "jobs", 200, params={'q': 'engineer'})
        if success:
            if 'items' not in data:
                self.log("❌ Jobs response missing items", "FAIL")
                return False
            self.log(f"✅ Query filter returned {len(data['items'])} jobs", "PASS")
        return success

    def test_jobs_filter_location(self):
        """Test GET /jobs?location=Jakarta filters correctly."""
        success, data = self.run_test("Filter Jobs by Location", "GET", "jobs", 200, params={'location': 'Jakarta'})
        if success:
            if 'items' not in data:
                self.log("❌ Jobs response missing items", "FAIL")
                return False
            self.log(f"✅ Location filter returned {len(data['items'])} jobs", "PASS")
        return success

    def test_jobs_filter_category(self):
        """Test GET /jobs?category_id=<id> filters correctly."""
        if not self.category_id:
            self.log("⚠️  Skipping category filter test (no category_id)", "WARN")
            return True
        success, data = self.run_test("Filter Jobs by Category", "GET", "jobs", 200, 
                                      params={'category_id': self.category_id})
        if success:
            if 'items' not in data:
                self.log("❌ Jobs response missing items", "FAIL")
                return False
            self.log(f"✅ Category filter returned {len(data['items'])} jobs", "PASS")
        return success

    def test_featured_jobs(self):
        """Test GET /jobs/featured?limit=6 returns enriched jobs."""
        success, data = self.run_test("Get Featured Jobs", "GET", "jobs/featured", 200, params={'limit': 6})
        if success:
            if not isinstance(data, list):
                self.log("❌ Featured jobs response is not a list", "FAIL")
                return False
            if data and 'company' not in data[0]:
                self.log("❌ Featured jobs missing company info", "FAIL")
                return False
            self.log(f"✅ Featured jobs returned {len(data)} jobs with company info", "PASS")
        return success

    def test_job_detail(self):
        """Test GET /jobs/{slug} returns full detail with company + related jobs."""
        if not self.job_id:
            self.log("⚠️  Skipping job detail test (no job_id)", "WARN")
            return True
        success, data = self.run_test("Get Job Detail", "GET", f"jobs/{self.job_id}", 200)
        if success:
            if 'company' not in data:
                self.log("❌ Job detail missing company info", "FAIL")
                return False
            if 'related' not in data:
                self.log("❌ Job detail missing related jobs", "FAIL")
                return False
            self.log(f"✅ Job detail has company and {len(data.get('related', []))} related jobs", "PASS")
        return success

    # ========== AUTH ==========
    def test_register_candidate(self):
        """Test POST /auth/register creates candidate and returns JWT + user."""
        timestamp = datetime.now().strftime("%H%M%S")
        success, data = self.run_test(
            "Register Candidate",
            "POST",
            "auth/register",
            200,
            data={
                "email": f"test_candidate_{timestamp}@test.com",
                "password": "password123",
                "name": "Test Candidate",
                "role": "candidate"
            }
        )
        if success:
            if 'token' not in data or 'user' not in data:
                self.log("❌ Register response missing token or user", "FAIL")
                return False
            self.candidate_token = data['token']
            self.log(f"✅ Candidate registered with token", "PASS")
        return success

    def test_register_employer(self):
        """Test POST /auth/register with role=employer + company_name creates company."""
        timestamp = datetime.now().strftime("%H%M%S")
        success, data = self.run_test(
            "Register Employer",
            "POST",
            "auth/register",
            200,
            data={
                "email": f"test_employer_{timestamp}@test.com",
                "password": "password123",
                "name": "Test Employer",
                "role": "employer",
                "company_name": f"Test Company {timestamp}"
            }
        )
        if success:
            if 'token' not in data or 'user' not in data:
                self.log("❌ Register response missing token or user", "FAIL")
                return False
            self.employer_token = data['token']
            self.log(f"✅ Employer registered with token", "PASS")
        return success

    def test_login_candidate(self):
        """Test POST /auth/login with demo candidate credentials."""
        success, data = self.run_test(
            "Login Candidate",
            "POST",
            "auth/login",
            200,
            data={
                "email": "kandidat@talentiv.id",
                "password": "password123"
            }
        )
        if success:
            if 'token' not in data:
                self.log("❌ Login response missing token", "FAIL")
                return False
            self.candidate_token = data['token']
            self.log(f"✅ Candidate logged in successfully", "PASS")
        return success

    def test_login_employer(self):
        """Test POST /auth/login with demo employer credentials."""
        success, data = self.run_test(
            "Login Employer",
            "POST",
            "auth/login",
            200,
            data={
                "email": "hr@nusantaratech.example.com",
                "password": "password123"
            }
        )
        if success:
            if 'token' not in data:
                self.log("❌ Login response missing token", "FAIL")
                return False
            self.employer_token = data['token']
            self.log(f"✅ Employer logged in successfully", "PASS")
        return success

    def test_auth_me_candidate(self):
        """Test GET /auth/me returns user+profile for candidate."""
        if not self.candidate_token:
            self.log("⚠️  Skipping auth/me candidate test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Auth Me (Candidate)", "GET", "auth/me", 200, token=self.candidate_token)
        if success:
            if 'user' not in data or 'profile' not in data:
                self.log("❌ Auth me response missing user or profile", "FAIL")
                return False
            self.log(f"✅ Auth me returned user and profile", "PASS")
        return success

    def test_auth_me_employer(self):
        """Test GET /auth/me returns user+company for employer."""
        if not self.employer_token:
            self.log("⚠️  Skipping auth/me employer test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Auth Me (Employer)", "GET", "auth/me", 200, token=self.employer_token)
        if success:
            if 'user' not in data or 'company' not in data:
                self.log("❌ Auth me response missing user or company", "FAIL")
                return False
            self.log(f"✅ Auth me returned user and company", "PASS")
        return success

    # ========== AI ENDPOINTS ==========
    def test_ai_salary_prediction(self):
        """Test POST /ai/salary-prediction returns realistic IDR amounts."""
        success, data = self.run_test(
            "AI Salary Prediction",
            "POST",
            "ai/salary-prediction",
            200,
            data={
                "title": "Senior Frontend Engineer",
                "location": "Jakarta",
                "years_experience": 5,
                "level": "senior",
                "skills": ["React", "TypeScript", "Next.js"]
            }
        )
        if success:
            required_fields = ['salary_min', 'salary_max', 'currency', 'confidence', 'rationale']
            missing = [f for f in required_fields if f not in data]
            if missing:
                self.log(f"❌ Salary prediction missing fields: {missing}", "FAIL")
                return False
            if data.get('currency') != 'IDR':
                self.log(f"❌ Expected currency IDR, got {data.get('currency')}", "FAIL")
                return False
            if data.get('salary_min', 0) < 1000000 or data.get('salary_max', 0) < 1000000:
                self.log(f"❌ Salary amounts seem unrealistic: {data.get('salary_min')}-{data.get('salary_max')}", "FAIL")
                return False
            self.log(f"✅ Salary prediction: {data.get('salary_min'):,} - {data.get('salary_max'):,} IDR", "PASS")
        return success

    def test_ai_match_score(self):
        """Test POST /ai/match-score returns score, rationale, matched/missing skills."""
        if not self.job_id:
            self.log("⚠️  Skipping match score test (no job_id)", "WARN")
            return True
        success, data = self.run_test(
            "AI Match Score",
            "POST",
            "ai/match-score",
            200,
            data={
                "candidate_skills": ["React", "TypeScript", "Node.js"],
                "candidate_years_experience": 3,
                "job_id": self.job_id
            }
        )
        if success:
            required_fields = ['score', 'rationale', 'matched_skills', 'missing_skills', 'recommendation']
            missing = [f for f in required_fields if f not in data]
            if missing:
                self.log(f"❌ Match score missing fields: {missing}", "FAIL")
                return False
            if not isinstance(data.get('score'), int) or not (0 <= data.get('score') <= 100):
                self.log(f"❌ Invalid score: {data.get('score')}", "FAIL")
                return False
            self.log(f"✅ Match score: {data.get('score')}/100, recommendation: {data.get('recommendation')}", "PASS")
        return success

    def test_ai_parse_resume(self):
        """Test POST /ai/parse-resume with text returns structured profile JSON."""
        resume_text = """
        Ahmad Wijaya
        Email: ahmad@example.com
        Phone: +62 812-3456-7890
        Location: Jakarta, Indonesia
        
        Professional Summary:
        Senior Frontend Engineer with 5 years of experience building scalable web applications.
        
        Skills: React, TypeScript, Next.js, Tailwind CSS, Node.js, GraphQL
        
        Experience:
        Senior Software Engineer at Tokopedia (Jan 2023 - Present)
        - Led checkout module redesign
        
        Education:
        S1 Teknik Informatika, Universitas Indonesia (2016-2020)
        GPA: 3.78
        """
        success, data = self.run_test(
            "AI Parse Resume",
            "POST",
            "ai/parse-resume",
            200,
            data={"text": resume_text}
        )
        if success:
            required_fields = ['skills', 'experience', 'education']
            missing = [f for f in required_fields if f not in data]
            if missing:
                self.log(f"❌ Parse resume missing fields: {missing}", "FAIL")
                return False
            self.log(f"✅ Resume parsed: {len(data.get('skills', []))} skills, {len(data.get('experience', []))} experience", "PASS")
        return success

    # ========== CANDIDATE FLOWS ==========
    def test_candidate_apply_job(self):
        """Test POST /applications creates application with match_score."""
        if not self.candidate_token or not self.job_id:
            self.log("⚠️  Skipping apply job test (no token or job_id)", "WARN")
            return True
        success, data = self.run_test(
            "Candidate Apply Job",
            "POST",
            "applications",
            200,
            data={
                "job_id": self.job_id,
                "cover_letter": "I am very interested in this position."
            },
            token=self.candidate_token
        )
        if success:
            if 'id' not in data or 'match_score' not in data:
                self.log("❌ Application response missing id or match_score", "FAIL")
                return False
            self.application_id = data['id']
            self.log(f"✅ Application created with match_score: {data.get('match_score')}", "PASS")
        return success

    def test_candidate_save_job(self):
        """Test POST /saved/{job_id} saves job."""
        if not self.candidate_token or not self.job_id:
            self.log("⚠️  Skipping save job test (no token or job_id)", "WARN")
            return True
        # Find a different job to save
        success_list, jobs_data = self.run_test("Get Jobs for Save", "GET", "jobs", 200, params={'page_size': 20})
        if success_list and jobs_data.get('items'):
            # Find a job we haven't applied to
            save_job_id = None
            for job in jobs_data['items']:
                if job['id'] != self.job_id:
                    save_job_id = job['id']
                    break
            if save_job_id:
                success, data = self.run_test(
                    "Candidate Save Job",
                    "POST",
                    f"saved/{save_job_id}",
                    200,
                    token=self.candidate_token
                )
                if success:
                    self.saved_job_id = save_job_id
                    self.log(f"✅ Job saved successfully", "PASS")
                return success
        self.log("⚠️  Could not find job to save", "WARN")
        return True

    def test_candidate_get_saved(self):
        """Test GET /saved returns saved jobs."""
        if not self.candidate_token:
            self.log("⚠️  Skipping get saved test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Saved Jobs", "GET", "saved", 200, token=self.candidate_token)
        if success:
            if not isinstance(data, list):
                self.log("❌ Saved jobs response is not a list", "FAIL")
                return False
            self.log(f"✅ Found {len(data)} saved jobs", "PASS")
        return success

    def test_candidate_delete_saved(self):
        """Test DELETE /saved/{job_id} removes saved job."""
        if not self.candidate_token or not self.saved_job_id:
            self.log("⚠️  Skipping delete saved test (no token or saved_job_id)", "WARN")
            return True
        success, data = self.run_test(
            "Delete Saved Job",
            "DELETE",
            f"saved/{self.saved_job_id}",
            200,
            token=self.candidate_token
        )
        return success

    def test_candidate_update_profile(self):
        """Test PUT /profile updates headline/skills."""
        if not self.candidate_token:
            self.log("⚠️  Skipping update profile test (no token)", "WARN")
            return True
        success, data = self.run_test(
            "Update Profile",
            "PUT",
            "profile",
            200,
            data={
                "headline": "Senior Full Stack Engineer",
                "skills": ["React", "TypeScript", "Python", "FastAPI"]
            },
            token=self.candidate_token
        )
        if success:
            if data.get('headline') != "Senior Full Stack Engineer":
                self.log("❌ Profile update did not persist headline", "FAIL")
                return False
            self.log(f"✅ Profile updated successfully", "PASS")
        return success

    def test_candidate_stats(self):
        """Test GET /candidate/stats returns counts."""
        if not self.candidate_token:
            self.log("⚠️  Skipping candidate stats test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Candidate Stats", "GET", "candidate/stats", 200, token=self.candidate_token)
        if success:
            required_fields = ['total_applications', 'interview_count', 'saved_count']
            missing = [f for f in required_fields if f not in data]
            if missing:
                self.log(f"❌ Candidate stats missing fields: {missing}", "FAIL")
                return False
            self.log(f"✅ Stats: {data.get('total_applications')} apps, {data.get('saved_count')} saved", "PASS")
        return success

    def test_candidate_recommendations(self):
        """Test GET /candidate/recommendations returns jobs."""
        if not self.candidate_token:
            self.log("⚠️  Skipping recommendations test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Recommendations", "GET", "candidate/recommendations", 200, 
                                      token=self.candidate_token, params={'limit': 6})
        if success:
            if not isinstance(data, list):
                self.log("❌ Recommendations response is not a list", "FAIL")
                return False
            self.log(f"✅ Found {len(data)} recommended jobs", "PASS")
        return success

    # ========== EMPLOYER FLOWS ==========
    def test_employer_get_jobs(self):
        """Test GET /employer/jobs returns their jobs."""
        if not self.employer_token:
            self.log("⚠️  Skipping employer jobs test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Employer Jobs", "GET", "employer/jobs", 200, token=self.employer_token)
        if success:
            if not isinstance(data, list):
                self.log("❌ Employer jobs response is not a list", "FAIL")
                return False
            self.log(f"✅ Employer has {len(data)} jobs", "PASS")
        return success

    def test_employer_stats(self):
        """Test GET /employer/stats returns counts."""
        if not self.employer_token:
            self.log("⚠️  Skipping employer stats test (no token)", "WARN")
            return True
        success, data = self.run_test("Get Employer Stats", "GET", "employer/stats", 200, token=self.employer_token)
        if success:
            required_fields = ['total_jobs', 'active_jobs', 'total_applications']
            missing = [f for f in required_fields if f not in data]
            if missing:
                self.log(f"❌ Employer stats missing fields: {missing}", "FAIL")
                return False
            self.log(f"✅ Stats: {data.get('total_jobs')} jobs, {data.get('total_applications')} apps", "PASS")
        return success

    def test_employer_create_job(self):
        """Test POST /jobs creates a job."""
        if not self.employer_token:
            self.log("⚠️  Skipping create job test (no token)", "WARN")
            return True
        timestamp = datetime.now().strftime("%H%M%S")
        success, data = self.run_test(
            "Employer Create Job",
            "POST",
            "jobs",
            200,
            data={
                "title": f"Test Job {timestamp}",
                "description": "This is a test job posting.",
                "requirements": "Test requirements",
                "skills": ["Python", "FastAPI"],
                "location": "Jakarta",
                "employment_type": "full_time",
                "work_mode": "remote",
                "experience_level": "mid",
                "min_years": 2,
                "salary_min": 10000000,
                "salary_max": 18000000
            },
            token=self.employer_token
        )
        if success:
            if 'id' not in data:
                self.log("❌ Create job response missing id", "FAIL")
                return False
            self.employer_job_id = data['id']
            self.log(f"✅ Job created with id: {self.employer_job_id}", "PASS")
        return success

    def test_employer_update_job(self):
        """Test PUT /jobs/{id} updates job."""
        if not self.employer_token or not hasattr(self, 'employer_job_id'):
            self.log("⚠️  Skipping update job test (no token or job_id)", "WARN")
            return True
        success, data = self.run_test(
            "Employer Update Job",
            "PUT",
            f"jobs/{self.employer_job_id}",
            200,
            data={
                "title": "Updated Test Job",
                "description": "Updated description",
                "requirements": "Updated requirements",
                "skills": ["Python", "FastAPI", "MongoDB"],
                "location": "Jakarta",
                "employment_type": "full_time",
                "work_mode": "hybrid"
            },
            token=self.employer_token
        )
        return success

    def test_employer_delete_job(self):
        """Test DELETE /jobs/{id} deletes job."""
        if not self.employer_token or not hasattr(self, 'employer_job_id'):
            self.log("⚠️  Skipping delete job test (no token or job_id)", "WARN")
            return True
        success, data = self.run_test(
            "Employer Delete Job",
            "DELETE",
            f"jobs/{self.employer_job_id}",
            200,
            token=self.employer_token
        )
        return success

    def test_employer_get_applicants(self):
        """Test GET /applications/job/{job_id} returns applicants sorted by match_score."""
        if not self.employer_token:
            self.log("⚠️  Skipping get applicants test (no token)", "WARN")
            return True
        # Get first job from employer's jobs
        success_jobs, jobs_data = self.run_test("Get Employer Jobs for Applicants", "GET", "employer/jobs", 200, 
                                                token=self.employer_token)
        if success_jobs and jobs_data and len(jobs_data) > 0:
            job_id = jobs_data[0]['id']
            success, data = self.run_test(
                "Get Job Applicants",
                "GET",
                f"applications/job/{job_id}",
                200,
                token=self.employer_token
            )
            if success:
                if not isinstance(data, list):
                    self.log("❌ Applicants response is not a list", "FAIL")
                    return False
                self.log(f"✅ Found {len(data)} applicants", "PASS")
            return success
        self.log("⚠️  No jobs found to get applicants", "WARN")
        return True

    def test_employer_update_application_status(self):
        """Test PUT /applications/{app_id}/status changes status."""
        if not self.employer_token or not self.application_id:
            self.log("⚠️  Skipping update application status test (no token or app_id)", "WARN")
            return True
        success, data = self.run_test(
            "Update Application Status",
            "PUT",
            f"applications/{self.application_id}/status",
            200,
            data={"status": "interview"},
            token=self.employer_token
        )
        if success:
            if data.get('status') != 'interview':
                self.log("❌ Application status not updated", "FAIL")
                return False
            self.log(f"✅ Application status updated to interview", "PASS")
        return success

    # ========== ROLE ENFORCEMENT ==========
    def test_role_enforcement_candidate_cannot_post_job(self):
        """Test candidate cannot POST /jobs (should 403)."""
        if not self.candidate_token:
            self.log("⚠️  Skipping role enforcement test (no candidate token)", "WARN")
            return True
        success, data = self.run_test(
            "Role Enforcement: Candidate Cannot Post Job",
            "POST",
            "jobs",
            403,
            data={
                "title": "Unauthorized Job",
                "description": "Test",
                "requirements": "Test",
                "skills": [],
                "location": "Test"
            },
            token=self.candidate_token
        )
        return success

    def test_role_enforcement_employer_cannot_apply(self):
        """Test employer cannot POST /applications (should 403)."""
        if not self.employer_token or not self.job_id:
            self.log("⚠️  Skipping role enforcement test (no employer token or job_id)", "WARN")
            return True
        success, data = self.run_test(
            "Role Enforcement: Employer Cannot Apply",
            "POST",
            "applications",
            403,
            data={
                "job_id": self.job_id,
                "cover_letter": "Test"
            },
            token=self.employer_token
        )
        return success

    def run_all_tests(self):
        """Run all tests in sequence."""
        self.log("=" * 80)
        self.log("STARTING TALENTIV JOBS BACKEND API TESTS")
        self.log("=" * 80)

        # Basic
        self.test_health()

        # Categories
        self.test_categories()

        # Jobs
        self.test_jobs_list()
        self.test_jobs_filter_query()
        self.test_jobs_filter_location()
        self.test_jobs_filter_category()
        self.test_featured_jobs()
        self.test_job_detail()

        # Auth
        self.test_login_candidate()
        self.test_login_employer()
        self.test_auth_me_candidate()
        self.test_auth_me_employer()
        self.test_register_candidate()
        self.test_register_employer()

        # AI Endpoints (can be slow)
        self.log("\n--- Testing AI Endpoints (may take 5-10s each) ---")
        self.test_ai_salary_prediction()
        self.test_ai_match_score()
        self.test_ai_parse_resume()

        # Candidate Flows
        self.log("\n--- Testing Candidate Flows ---")
        self.test_candidate_apply_job()
        self.test_candidate_save_job()
        self.test_candidate_get_saved()
        self.test_candidate_delete_saved()
        self.test_candidate_update_profile()
        self.test_candidate_stats()
        self.test_candidate_recommendations()

        # Employer Flows
        self.log("\n--- Testing Employer Flows ---")
        self.test_employer_get_jobs()
        self.test_employer_stats()
        self.test_employer_create_job()
        self.test_employer_update_job()
        self.test_employer_get_applicants()
        self.test_employer_update_application_status()
        self.test_employer_delete_job()

        # Role Enforcement
        self.log("\n--- Testing Role Enforcement ---")
        self.test_role_enforcement_candidate_cannot_post_job()
        self.test_role_enforcement_employer_cannot_apply()

        # Summary
        self.log("=" * 80)
        self.log(f"TESTS COMPLETED: {self.tests_passed}/{self.tests_run} PASSED")
        self.log("=" * 80)

        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for fail in self.failed_tests:
                self.log(f"  - {fail.get('test', 'Unknown')}: {fail}")

        return 0 if self.tests_passed == self.tests_run else 1


if __name__ == "__main__":
    tester = TalentivAPITester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
