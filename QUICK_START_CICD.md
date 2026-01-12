# 🚀 Quick Start: CI/CD Pipeline Setup

## Problem Solved
✅ **Automatic token expiration handling for CI/CD pipelines**  
✅ **Proactive alerts before tokens expire**  
✅ **Clear error messages and remediation steps**

---

## ⚡ 5-Minute Setup

### Step 1: Configure Your CI/CD Platform

Choose your platform and follow the instructions:

<details>
<summary><b>GitHub Actions</b></summary>

1. **Add Secrets:**
   - Go to: `Settings` → `Secrets and variables` → `Actions`
   - Click `New repository secret`
   - Add two secrets:
     - Name: `BASE_URL`, Value: `https://api-qa.creditmobility.net`
     - Name: `ACCESS_TOKEN`, Value: `your-token-here`

2. **Commit Workflow Files:**
   ```bash
   git add .github/workflows/
   git commit -m "Add CI/CD with token management"
   git push
   ```

3. **Verify:**
   - Go to `Actions` tab
   - You should see workflows running automatically

</details>

<details>
<summary><b>Azure DevOps</b></summary>

1. **Add Variables:**
   - Go to: `Pipelines` → Your Pipeline → `Edit` → `Variables`
   - Add two variables:
     - Name: `BASE_URL`, Value: `https://api-qa.creditmobility.net`
     - Name: `ACCESS_TOKEN`, Value: `your-token-here` (mark as **Secret**)

2. **Add Pipeline:**
   ```bash
   git add azure-pipelines.yml
   git commit -m "Add Azure pipeline with token management"
   git push
   ```

3. **Create Pipeline:**
   - Go to Pipelines → New Pipeline
   - Select your repository
   - Choose "Existing Azure Pipelines YAML file"
   - Select `azure-pipelines.yml`

</details>

<details>
<summary><b>GitLab CI</b></summary>

1. **Add Variables:**
   - Go to: `Settings` → `CI/CD` → `Variables`
   - Add two variables (mark as **Masked** and **Protected**):
     - Key: `BASE_URL`, Value: `https://api-qa.creditmobility.net`
     - Key: `ACCESS_TOKEN`, Value: `your-token-here`

2. **Commit Pipeline:**
   ```bash
   git add .gitlab-ci.yml
   git commit -m "Add GitLab CI with token management"
   git push
   ```

3. **Verify:**
   - Go to `CI/CD` → `Pipelines`
   - Pipeline should start automatically

</details>

---

### Step 2: Test Locally (Optional but Recommended)

Before pushing to CI/CD, validate your token locally:

```powershell
# Windows PowerShell - Interactive setup
.\validate_token.ps1 -SetEnvVars

# OR set manually
$env:BASE_URL = "https://api-qa.creditmobility.net"
$env:ACCESS_TOKEN = "your-token-here"
.\validate_token.ps1
```

```bash
# Linux/Mac
export BASE_URL="https://api-qa.creditmobility.net"
export ACCESS_TOKEN="your-token-here"
python token_manager.py
```

**Expected Output:**
```
✅ SUCCESS: Token is valid and active
Your token is working correctly and tests can run!
```

---

### Step 3: Monitor and Maintain

#### **Automated Monitoring (Already Configured):**
- ✅ Daily token health checks at 2 AM UTC
- ✅ Weekly token validation with automatic alerts
- ✅ Test failures include token status in error messages

#### **When Token Expires:**

You'll receive an alert like this:
```
❌ FAILURE: Token is expired or invalid (401 Unauthorized)
Action Required: Update ACCESS_TOKEN in pipeline settings
```

**To fix:**
1. Generate new token from API provider
2. Update secret in CI/CD platform (Step 1)
3. Re-run failed pipeline

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `token_manager.py` | Token validation utility |
| `conftest.py` (updated) | Auto-validates token on test startup |
| `.github/workflows/api-tests.yml` | GitHub Actions test workflow |
| `.github/workflows/token-rotation-reminder.yml` | GitHub token monitoring |
| `azure-pipelines.yml` | Azure DevOps pipeline |
| `.gitlab-ci.yml` | GitLab CI pipeline |
| `validate_token.ps1` | Windows PowerShell helper script |
| `TOKEN_MANAGEMENT.md` | Comprehensive documentation |

---

## ✅ What's Automated Now

1. **Token Validation Before Tests**
   - Tests won't run if token is expired
   - Fails fast with clear error messages

2. **Daily Health Checks**
   - Runs tests daily to catch expiration early
   - Prevents surprises during critical deployments

3. **Weekly Token Monitoring**
   - Validates token every Monday
   - Creates alerts/issues when rotation needed

4. **Clear Error Messages**
   - Tells you exactly what's wrong
   - Provides step-by-step fix instructions

---

## 🎯 Common Commands

```powershell
# Validate token (Windows)
.\validate_token.ps1

# Validate token (cross-platform)
python token_manager.py

# Run tests locally
pytest -v

# Run smoke tests
pytest -v -m smoke

# Run with CI profile (faster)
$env:HYPOTHESIS_PROFILE = "ci"
pytest -v
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ACCESS_TOKEN not set" | Run `.\validate_token.ps1 -SetEnvVars` |
| "401 Unauthorized" | Token expired - generate new token and update secrets |
| "Token validation timed out" | Check network/VPN connection |
| Tests pass locally, fail in CI | Verify secrets are set correctly (no trailing spaces) |

---

## 📚 Need More Details?

- **Full Documentation:** [TOKEN_MANAGEMENT.md](TOKEN_MANAGEMENT.md)
- **Token Rotation Guide:** See "Token Rotation Process" in TOKEN_MANAGEMENT.md
- **Best Practices:** See "Best Practices" section in TOKEN_MANAGEMENT.md

---

## ⏱️ Time Savings

**Before:**
- ❌ Manual token rotation every few days
- ❌ Pipeline failures without warning
- ❌ Time wasted debugging expired tokens
- ❌ Tests run with bad credentials

**After:**
- ✅ Proactive alerts before expiration
- ✅ Fails fast with clear error messages
- ✅ Automated health checks
- ✅ Tests only run with valid tokens

---

## 🎉 You're Done!

Your pipeline now:
- ✅ Validates tokens before running tests
- ✅ Alerts you when rotation is needed
- ✅ Provides clear fix instructions
- ✅ Runs daily to catch issues early

**Next Steps:**
1. Commit and push the new files
2. Verify pipeline runs successfully
3. Set a calendar reminder to check token health weekly
4. Keep a backup of TOKEN_MANAGEMENT.md for reference

---

**Questions?** See [TOKEN_MANAGEMENT.md](TOKEN_MANAGEMENT.md) for comprehensive documentation.
