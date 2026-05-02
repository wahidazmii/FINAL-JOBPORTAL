"""Phase 3 Backend Tests - Admin Role + Rate Limiting + Regression."""
import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://job-search-ai-2.preview.emergentagent.com/api"

class Phase3Tester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.candidate_token = None
        self.employer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.test_candidate_id = None
        self.test_job_id = None

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
                self.log(f"   Response: {response.text[:300]}", "FAIL")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:300]
                })
                return False, {}

        except Exception as e:
            self.log(f"❌ FAILED - {name} (Error: {str(e)})", "FAIL")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    # ========== PHASE 3: ADMIN TESTS ==========
    
    def test_admin_cannot_register(self):
        """Test POST /auth/register with role=admin returns 403."""
        timestamp = datetime.now().strftime("%H%M%S")
        success, data = self.run_test(
            "Admin Cannot Self-Register",
            "POST",
            "auth/register",
            403,
            data={
                "email": f"admin_test_{timestamp}@test.com",
                "password": "password123",
                "name": "Test Admin",
                "role": "admin"
            }
        )
        return success

    def test_admin_login(self):
        """Test POST /auth/login with admin@talentiv.id / admin123."""
        success, data = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "admin@talentiv.id",
                "password": "admin123"
            }
        )
        if success:
            if 'token' not in data:
                self.log("❌ Admin login response missing token", "FAIL")
                return False
            if data.get('user', {}).get('role') != 'admin':
                self.log(f"❌ Expected role=admin, got {data.get('user', {}).get('role')}", "FAIL")
                return False
            self.admin_token = data['token']
            self.log(f"✅ Admin logged in successfully with role=admin", "PASS")
        return success

    def test_disabled_user_cannot_login(self):
        """Test disabled user cannot login - create candidate, disable via admin, try login."""
        # First, login as admin
        if not self.admin_token:
            self.log("⚠️  Skipping disabled user test (no admin token)", "WARN")
            return True
        
        # Create a test candidate
        timestamp = datetime.now().strftime("%H%M%S")
        test_email = f"disable_test_{timestamp}@test.com"
        success_reg, reg_data = self.run_test(
            "Create Test Candidate for Disable",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "password123",
                "name": "Test Disable User",
                "role": "candidate"
            }
        )
        if not success_reg:
            self.log("❌ Failed to create test candidate", "FAIL")
            return False
        
        test_user_id = reg_data.get('user', {}).get('id')
        if not test_user_id:
            self.log("❌ No user ID in registration response", "FAIL")
            return False
        
        # Disable the user via admin endpoint
        success_disable, _ = self.run_test(
            "Admin Disables User",
            "PUT",
            f"admin/users/{test_user_id}",
            200,
            data={"is_disabled": True},
            token=self.admin_token
        )
        if not success_disable:
            self.log("❌ Failed to disable user", "FAIL")
            return False
        
        # Try to login as disabled user - should get 403
        success_login, login_data = self.run_test(
            "Disabled User Cannot Login",
            "POST",
            "auth/login",
            403,
            data={
                "email": test_email,
                "password": "password123"
            }
        )
        
        # Re-enable the user for cleanup
        self.run_test(
            "Re-enable User (Cleanup)",
            "PUT",
            f"admin/users/{test_user_id}",
            200,
            data={"is_disabled": False},
            token=self.admin_token
        )
        
        return success_login

    def test_admin_overview(self):
        """Test GET /admin/overview returns counts object."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin overview test (no admin token)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin Overview",
            "GET",
            "admin/overview",
            200,
            token=self.admin_token
        )
        if success:
            required_keys = ['users', 'companies', 'jobs', 'applications']
            missing = [k for k in required_keys if k not in data]
            if missing:
                self.log(f"❌ Overview missing keys: {missing}", "FAIL")
                return False
            
            # Check users breakdown
            user_keys = ['total', 'candidates', 'employers', 'admins']
            missing_user = [k for k in user_keys if k not in data.get('users', {})]
            if missing_user:
                self.log(f"❌ Users breakdown missing keys: {missing_user}", "FAIL")
                return False
            
            # Check jobs breakdown
            job_keys = ['total', 'published', 'paused', 'closed', 'featured']
            missing_job = [k for k in job_keys if k not in data.get('jobs', {})]
            if missing_job:
                self.log(f"❌ Jobs breakdown missing keys: {missing_job}", "FAIL")
                return False
            
            self.log(f"✅ Overview: {data['users']['total']} users, {data['jobs']['total']} jobs, {data['applications']['total']} apps", "PASS")
        return success

    def test_non_admin_cannot_access_overview(self):
        """Test non-admin (candidate) calling /admin/overview returns 403."""
        # Login as candidate first
        success_login, login_data = self.run_test(
            "Login Candidate for Non-Admin Test",
            "POST",
            "auth/login",
            200,
            data={
                "email": "kandidat@talentiv.id",
                "password": "password123"
            }
        )
        if not success_login:
            self.log("⚠️  Could not login as candidate", "WARN")
            return True
        
        candidate_token = login_data.get('token')
        success, data = self.run_test(
            "Non-Admin Cannot Access Overview",
            "GET",
            "admin/overview",
            403,
            token=candidate_token
        )
        return success

    def test_unauthenticated_cannot_access_admin(self):
        """Test unauthenticated request to /admin/* returns 401."""
        success, data = self.run_test(
            "Unauthenticated Cannot Access Admin",
            "GET",
            "admin/overview",
            401
        )
        return success

    def test_admin_list_jobs(self):
        """Test GET /admin/jobs returns jobs with company name enriched."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin list jobs test (no admin token)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin List Jobs",
            "GET",
            "admin/jobs",
            200,
            token=self.admin_token
        )
        if success:
            if not isinstance(data, list):
                self.log("❌ Admin jobs response is not a list", "FAIL")
                return False
            if data and 'company' not in data[0]:
                self.log("❌ Admin jobs missing company enrichment", "FAIL")
                return False
            if data:
                self.test_job_id = data[0]['id']
            self.log(f"✅ Admin jobs returned {len(data)} jobs with company info", "PASS")
        return success

    def test_admin_list_jobs_with_filters(self):
        """Test GET /admin/jobs with q and status filters."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin jobs filter test (no admin token)", "WARN")
            return True
        
        # Test query filter
        success_q, data_q = self.run_test(
            "Admin Jobs Filter by Query",
            "GET",
            "admin/jobs",
            200,
            token=self.admin_token,
            params={'q': 'engineer'}
        )
        
        # Test status filter
        success_status, data_status = self.run_test(
            "Admin Jobs Filter by Status",
            "GET",
            "admin/jobs",
            200,
            token=self.admin_token,
            params={'status': 'published'}
        )
        
        return success_q and success_status

    def test_admin_update_job_status(self):
        """Test PUT /admin/jobs/{id} with {status: 'paused'} changes status."""
        if not self.admin_token or not self.test_job_id:
            self.log("⚠️  Skipping admin update job status test (no admin token or job_id)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin Update Job Status to Paused",
            "PUT",
            f"admin/jobs/{self.test_job_id}",
            200,
            data={"status": "paused"},
            token=self.admin_token
        )
        if success:
            if data.get('status') != 'paused':
                self.log(f"❌ Job status not updated, got {data.get('status')}", "FAIL")
                return False
            self.log(f"✅ Job status updated to paused", "PASS")
        
        # Restore to published
        self.run_test(
            "Admin Restore Job Status to Published",
            "PUT",
            f"admin/jobs/{self.test_job_id}",
            200,
            data={"status": "published"},
            token=self.admin_token
        )
        
        return success

    def test_admin_toggle_featured(self):
        """Test PUT /admin/jobs/{id} with {is_featured: true} toggles featured flag."""
        if not self.admin_token or not self.test_job_id:
            self.log("⚠️  Skipping admin toggle featured test (no admin token or job_id)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin Toggle Job Featured",
            "PUT",
            f"admin/jobs/{self.test_job_id}",
            200,
            data={"is_featured": True},
            token=self.admin_token
        )
        if success:
            if not data.get('is_featured'):
                self.log(f"❌ Job is_featured not updated", "FAIL")
                return False
            self.log(f"✅ Job is_featured toggled to true", "PASS")
        
        # Toggle back to false
        self.run_test(
            "Admin Toggle Job Featured Back",
            "PUT",
            f"admin/jobs/{self.test_job_id}",
            200,
            data={"is_featured": False},
            token=self.admin_token
        )
        
        return success

    def test_admin_delete_job(self):
        """Test DELETE /admin/jobs/{id} removes job."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin delete job test (no admin token)", "WARN")
            return True
        
        # Create a test job first via employer
        # Login as employer
        success_login, login_data = self.run_test(
            "Login Employer for Delete Test",
            "POST",
            "auth/login",
            200,
            data={
                "email": "hr@nusantaratech.example.com",
                "password": "password123"
            }
        )
        if not success_login:
            self.log("⚠️  Could not login as employer", "WARN")
            return True
        
        employer_token = login_data.get('token')
        timestamp = datetime.now().strftime("%H%M%S")
        success_create, create_data = self.run_test(
            "Create Job for Delete Test",
            "POST",
            "jobs",
            200,
            data={
                "title": f"Delete Test Job {timestamp}",
                "description": "Test job for deletion",
                "requirements": "Test",
                "skills": ["Test"],
                "location": "Jakarta",
                "employment_type": "full_time",
                "work_mode": "remote"
            },
            token=employer_token
        )
        if not success_create:
            self.log("⚠️  Could not create test job", "WARN")
            return True
        
        delete_job_id = create_data.get('id')
        
        # Now delete via admin
        success, data = self.run_test(
            "Admin Delete Job",
            "DELETE",
            f"admin/jobs/{delete_job_id}",
            200,
            token=self.admin_token
        )
        return success

    def test_admin_list_users(self):
        """Test GET /admin/users returns users without password_hash."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin list users test (no admin token)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin List Users",
            "GET",
            "admin/users",
            200,
            token=self.admin_token
        )
        if success:
            if not isinstance(data, list):
                self.log("❌ Admin users response is not a list", "FAIL")
                return False
            if data and 'password_hash' in data[0]:
                self.log("❌ Admin users response contains password_hash (security issue!)", "FAIL")
                return False
            if data:
                self.test_candidate_id = next((u['id'] for u in data if u.get('role') == 'candidate'), None)
            self.log(f"✅ Admin users returned {len(data)} users without password_hash", "PASS")
        return success

    def test_admin_list_users_with_filters(self):
        """Test GET /admin/users with q and role filters."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin users filter test (no admin token)", "WARN")
            return True
        
        # Test role filter
        success_role, data_role = self.run_test(
            "Admin Users Filter by Role",
            "GET",
            "admin/users",
            200,
            token=self.admin_token,
            params={'role': 'candidate'}
        )
        if success_role and data_role:
            # Verify all returned users are candidates
            non_candidates = [u for u in data_role if u.get('role') != 'candidate']
            if non_candidates:
                self.log(f"❌ Role filter returned non-candidates: {len(non_candidates)}", "FAIL")
                return False
        
        # Test query filter
        success_q, data_q = self.run_test(
            "Admin Users Filter by Query",
            "GET",
            "admin/users",
            200,
            token=self.admin_token,
            params={'q': 'talentiv'}
        )
        
        return success_role and success_q

    def test_admin_disable_user(self):
        """Test PUT /admin/users/{id} with {is_disabled: true} disables user."""
        if not self.admin_token or not self.test_candidate_id:
            self.log("⚠️  Skipping admin disable user test (no admin token or candidate_id)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin Disable User",
            "PUT",
            f"admin/users/{self.test_candidate_id}",
            200,
            data={"is_disabled": True},
            token=self.admin_token
        )
        if success:
            if not data.get('is_disabled'):
                self.log(f"❌ User is_disabled not updated", "FAIL")
                return False
            self.log(f"✅ User disabled successfully", "PASS")
        
        # Re-enable for cleanup
        self.run_test(
            "Admin Re-enable User",
            "PUT",
            f"admin/users/{self.test_candidate_id}",
            200,
            data={"is_disabled": False},
            token=self.admin_token
        )
        
        return success

    def test_admin_change_user_role(self):
        """Test PUT /admin/users/{id} with {role: 'employer'} changes role."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin change role test (no admin token)", "WARN")
            return True
        
        # Create a test candidate
        timestamp = datetime.now().strftime("%H%M%S")
        success_reg, reg_data = self.run_test(
            "Create Test Candidate for Role Change",
            "POST",
            "auth/register",
            200,
            data={
                "email": f"role_test_{timestamp}@test.com",
                "password": "password123",
                "name": "Test Role Change",
                "role": "candidate"
            }
        )
        if not success_reg:
            self.log("⚠️  Could not create test candidate", "WARN")
            return True
        
        test_user_id = reg_data.get('user', {}).get('id')
        
        # Change role to employer
        success, data = self.run_test(
            "Admin Change User Role",
            "PUT",
            f"admin/users/{test_user_id}",
            200,
            data={"role": "employer"},
            token=self.admin_token
        )
        if success:
            if data.get('role') != 'employer':
                self.log(f"❌ User role not updated, got {data.get('role')}", "FAIL")
                return False
            self.log(f"✅ User role changed to employer", "PASS")
        
        return success

    def test_admin_list_companies(self):
        """Test GET /admin/companies returns companies with job_count."""
        if not self.admin_token:
            self.log("⚠️  Skipping admin list companies test (no admin token)", "WARN")
            return True
        
        success, data = self.run_test(
            "Admin List Companies",
            "GET",
            "admin/companies",
            200,
            token=self.admin_token
        )
        if success:
            if not isinstance(data, list):
                self.log("❌ Admin companies response is not a list", "FAIL")
                return False
            if data and 'job_count' not in data[0]:
                self.log("❌ Admin companies missing job_count enrichment", "FAIL")
                return False
            self.log(f"✅ Admin companies returned {len(data)} companies with job_count", "PASS")
        return success

    def test_rate_limiting_parse_resume(self):
        """Test rate limiting on /ai/parse-resume - 6+ rapid requests should hit 429."""
        self.log("Testing rate limiting (firing 6+ rapid requests)...")
        
        resume_text = "Test resume for rate limiting"
        success_count = 0
        rate_limited = False
        
        for i in range(7):
            url = f"{self.base_url}/ai/parse-resume"
            headers = {'Content-Type': 'application/json'}
            try:
                response = requests.post(url, json={"text": resume_text}, headers=headers, timeout=10)
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    self.log(f"✅ Rate limited on request #{i+1}", "PASS")
                    break
            except Exception as e:
                self.log(f"Request #{i+1} error: {e}", "WARN")
            time.sleep(0.1)  # Small delay between requests
        
        self.tests_run += 1
        if rate_limited:
            self.tests_passed += 1
            self.log(f"✅ PASSED - Rate Limiting (got 429 after {success_count} successful requests)", "PASS")
            return True
        else:
            self.log(f"❌ FAILED - Rate Limiting (expected 429, got {success_count} successful requests)", "FAIL")
            self.failed_tests.append({
                "test": "Rate Limiting",
                "expected": "429 after 5-6 requests",
                "actual": f"{success_count} successful requests without 429"
            })
            return False

    # ========== REGRESSION TESTS ==========
    
    def test_regression_candidate_apply(self):
        """Regression: Candidate can still apply to jobs."""
        # Login as candidate
        success_login, login_data = self.run_test(
            "Regression: Candidate Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "kandidat@talentiv.id",
                "password": "password123"
            }
        )
        if not success_login:
            return False
        
        candidate_token = login_data.get('token')
        
        # Get a job to apply to
        success_jobs, jobs_data = self.run_test(
            "Regression: Get Jobs",
            "GET",
            "jobs",
            200
        )
        if not success_jobs or not jobs_data.get('items'):
            self.log("⚠️  No jobs found for regression test", "WARN")
            return True
        
        job_id = jobs_data['items'][0]['id']
        
        # Apply to job
        timestamp = datetime.now().strftime("%H%M%S%f")
        success, data = self.run_test(
            "Regression: Candidate Apply",
            "POST",
            "applications",
            200,
            data={
                "job_id": job_id,
                "cover_letter": f"Regression test application {timestamp}"
            },
            token=candidate_token
        )
        return success

    def test_regression_candidate_save_job(self):
        """Regression: Candidate can save jobs."""
        # Login as candidate
        success_login, login_data = self.run_test(
            "Regression: Candidate Login for Save",
            "POST",
            "auth/login",
            200,
            data={
                "email": "kandidat@talentiv.id",
                "password": "password123"
            }
        )
        if not success_login:
            return False
        
        candidate_token = login_data.get('token')
        
        # Get a job to save
        success_jobs, jobs_data = self.run_test(
            "Regression: Get Jobs for Save",
            "GET",
            "jobs",
            200,
            params={'page_size': 20}
        )
        if not success_jobs or not jobs_data.get('items'):
            self.log("⚠️  No jobs found for save test", "WARN")
            return True
        
        job_id = jobs_data['items'][0]['id']
        
        # Save job
        success, data = self.run_test(
            "Regression: Candidate Save Job",
            "POST",
            f"saved/{job_id}",
            200,
            token=candidate_token
        )
        return success

    def test_regression_candidate_update_profile(self):
        """Regression: Candidate can update profile."""
        # Login as candidate
        success_login, login_data = self.run_test(
            "Regression: Candidate Login for Profile",
            "POST",
            "auth/login",
            200,
            data={
                "email": "kandidat@talentiv.id",
                "password": "password123"
            }
        )
        if not success_login:
            return False
        
        candidate_token = login_data.get('token')
        
        # Update profile
        success, data = self.run_test(
            "Regression: Candidate Update Profile",
            "PUT",
            "profile",
            200,
            data={
                "headline": "Senior Frontend Engineer (Updated)",
                "skills": ["React", "TypeScript", "Next.js", "Python"]
            },
            token=candidate_token
        )
        return success

    def test_regression_employer_create_job(self):
        """Regression: Employer can create jobs."""
        # Login as employer
        success_login, login_data = self.run_test(
            "Regression: Employer Login",
            "POST",
            "auth/login",
            200,
            data={
                "email": "hr@nusantaratech.example.com",
                "password": "password123"
            }
        )
        if not success_login:
            return False
        
        employer_token = login_data.get('token')
        
        # Create job
        timestamp = datetime.now().strftime("%H%M%S")
        success, data = self.run_test(
            "Regression: Employer Create Job",
            "POST",
            "jobs",
            200,
            data={
                "title": f"Regression Test Job {timestamp}",
                "description": "Test job for regression",
                "requirements": "Test requirements",
                "skills": ["Python", "FastAPI"],
                "location": "Jakarta",
                "employment_type": "full_time",
                "work_mode": "remote"
            },
            token=employer_token
        )
        return success

    def test_regression_employer_manage_applicants(self):
        """Regression: Employer can view and manage applicants."""
        # Login as employer
        success_login, login_data = self.run_test(
            "Regression: Employer Login for Applicants",
            "POST",
            "auth/login",
            200,
            data={
                "email": "hr@nusantaratech.example.com",
                "password": "password123"
            }
        )
        if not success_login:
            return False
        
        employer_token = login_data.get('token')
        
        # Get employer's jobs
        success_jobs, jobs_data = self.run_test(
            "Regression: Get Employer Jobs",
            "GET",
            "employer/jobs",
            200,
            token=employer_token
        )
        if not success_jobs or not jobs_data:
            self.log("⚠️  No employer jobs found", "WARN")
            return True
        
        if len(jobs_data) == 0:
            self.log("⚠️  Employer has no jobs", "WARN")
            return True
        
        job_id = jobs_data[0]['id']
        
        # Get applicants for job
        success, data = self.run_test(
            "Regression: Employer Get Applicants",
            "GET",
            f"applications/job/{job_id}",
            200,
            token=employer_token
        )
        return success

    def run_all_tests(self):
        """Run all Phase 3 tests."""
        self.log("=" * 80)
        self.log("PHASE 3 BACKEND TESTS - ADMIN ROLE + RATE LIMITING + REGRESSION")
        self.log("=" * 80)

        # ========== ADMIN TESTS ==========
        self.log("\n--- ADMIN AUTHENTICATION ---")
        self.test_admin_cannot_register()
        self.test_admin_login()
        self.test_disabled_user_cannot_login()

        self.log("\n--- ADMIN AUTHORIZATION ---")
        self.test_unauthenticated_cannot_access_admin()
        self.test_non_admin_cannot_access_overview()

        self.log("\n--- ADMIN OVERVIEW ---")
        self.test_admin_overview()

        self.log("\n--- ADMIN JOB MANAGEMENT ---")
        self.test_admin_list_jobs()
        self.test_admin_list_jobs_with_filters()
        self.test_admin_update_job_status()
        self.test_admin_toggle_featured()
        self.test_admin_delete_job()

        self.log("\n--- ADMIN USER MANAGEMENT ---")
        self.test_admin_list_users()
        self.test_admin_list_users_with_filters()
        self.test_admin_disable_user()
        self.test_admin_change_user_role()

        self.log("\n--- ADMIN COMPANY MANAGEMENT ---")
        self.test_admin_list_companies()

        self.log("\n--- RATE LIMITING ---")
        self.test_rate_limiting_parse_resume()

        # ========== REGRESSION TESTS ==========
        self.log("\n--- REGRESSION: CANDIDATE FLOWS ---")
        self.test_regression_candidate_apply()
        self.test_regression_candidate_save_job()
        self.test_regression_candidate_update_profile()

        self.log("\n--- REGRESSION: EMPLOYER FLOWS ---")
        self.test_regression_employer_create_job()
        self.test_regression_employer_manage_applicants()

        # Summary
        self.log("=" * 80)
        self.log(f"TESTS COMPLETED: {self.tests_passed}/{self.tests_run} PASSED")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"SUCCESS RATE: {success_rate:.1f}%")
        self.log("=" * 80)

        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for fail in self.failed_tests:
                self.log(f"  - {fail.get('test', 'Unknown')}")
                if 'error' in fail:
                    self.log(f"    Error: {fail['error']}")
                else:
                    self.log(f"    Expected: {fail.get('expected')}, Got: {fail.get('actual')}")

        return 0 if self.tests_passed == self.tests_run else 1


if __name__ == "__main__":
    tester = Phase3Tester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
