# 🔐 Token Management Guide for CI/CD Pipelines

## Overview

This guide explains how to manage API access tokens for automated test execution in CI/CD pipelines. The access token expires periodically and needs to be rotated to maintain continuous test automation.

---

## 🚨 Problem Statement

**Issue:** Access tokens expire after a few days, causing automated tests to fail in CI/CD pipelines.

**Impact:**
- ❌ Pipeline failures due to 401 Unauthorized errors
- ❌ False negatives in test results
- ❌ Blocked deployments and releases
- ❌ Manual intervention required for every token expiration

---

## ✅ Solution Architecture

### 1. **Token Validation on Startup**
The test suite now validates the access token **before** running any tests, providing immediate feedback if the token is expired.

### 2. **Automated Token Health Checks**
CI/CD pipelines include scheduled workflows that monitor token validity and alert when rotation is needed.

### 3. **Clear Error Messages**
When tokens expire, you receive actionable error messages with exact steps to resolve the issue.

---

## 🛠️ Implementation Components

### A. Token Manager Module (`token_manager.py`)

A Python utility that validates access tokens by making test API calls.

**Features:**
- ✅ Validates token before test execution
- ✅ Provides clear success/failure messages
- ✅ Can be run standalone or imported as a module
- ✅ Returns proper exit codes for CI/CD integration

**Usage:**
```bash
# Validate current token
python token_manager.py

# Output examples:
# ✅ SUCCESS: Token is valid and active
# ❌ FAILURE: Token is expired or invalid (401 Unauthorized)
```

### B. Enhanced Pytest Configuration (`conftest.py`)

The pytest configuration now includes a session hook that validates tokens at startup.

**Benefits:**
- Fails fast if token is invalid
- Prevents wasting time running tests with bad credentials
- Provides clear error messages in CI/CD logs

### C. CI/CD Pipeline Configurations

#### **GitHub Actions** (`.github/workflows/`)

**1. `api-tests.yml`** - Main test execution workflow
- Runs on push, PR, and daily schedule
- Validates token before running tests
- Executes smoke tests first, then full suite
- Uploads test results as artifacts

**2. `token-rotation-reminder.yml`** - Proactive monitoring
- Runs weekly to check token health
- Creates GitHub issues automatically when tokens expire
- Provides step-by-step rotation instructions

#### **Azure DevOps** (`azure-pipelines.yml`)

- Token validation stage (blocks tests if token is invalid)
- Automated test execution with proper environment variables
- Daily scheduled runs to catch expiration early
- Test result publishing and artifact management

---

## 📋 Setup Instructions

### Step 1: Configure Secrets/Variables

#### **For GitHub Actions:**

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `BASE_URL`: Your API base URL (e.g., `https://api-qa.creditmobility.net`)
   - `ACCESS_TOKEN`: Your API access token

#### **For Azure DevOps:**

1. Go to your pipeline → **Edit** → **Variables**
2. Add the following variables:
   - `BASE_URL`: Your API base URL
   - `ACCESS_TOKEN`: Your API access token (mark as **Secret**)

#### **For GitLab CI:**

1. Go to **Settings** → **CI/CD** → **Variables**
2. Add the following variables (mark both as **Protected** and **Masked**):
   - `BASE_URL`: Your API base URL
   - `ACCESS_TOKEN`: Your API access token

---

### Step 2: Test Token Validation Locally

Before pushing to CI/CD, test token validation locally:

```powershell
# Windows PowerShell
$env:BASE_URL = "https://api-qa.creditmobility.net"
$env:ACCESS_TOKEN = "your-token-here"
python token_manager.py
```

```bash
# Linux/Mac
export BASE_URL="https://api-qa.creditmobility.net"
export ACCESS_TOKEN="your-token-here"
python token_manager.py
```

**Expected Output:**
```
======================================================================
Token Validation Check
======================================================================
Timestamp: 2026-01-12T08:31:00

✓ BASE_URL: https://api-qa.creditmobility.net
✓ ACCESS_TOKEN: ********************Abc12345

Validating token...

✅ SUCCESS: Token is valid and active

Your token is working correctly and tests can run!
```

---

### Step 3: Run Tests with Token Validation

```powershell
# Run all tests (token validation happens automatically)
pytest -v

# Run specific test file
pytest test_csv_upload_positive.py -v

# Run with CI profile (faster for pipelines)
$env:HYPOTHESIS_PROFILE = "ci"
pytest -v
```

---

## 🔄 Token Rotation Process

### When to Rotate Tokens

Rotate your access token when:
- ✅ You receive a token expiration alert from CI/CD
- ✅ Tests start failing with 401 Unauthorized errors
- ✅ Weekly token health check fails
- ✅ Proactively, before the token expires (recommended)

### How to Rotate Tokens

#### **Step 1: Generate New Token**
Contact your API provider or use their portal to generate a new access token.

#### **Step 2: Update CI/CD Secrets**

**GitHub Actions:**
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on `ACCESS_TOKEN`
3. Click **Update secret**
4. Paste the new token
5. Click **Update secret**

**Azure DevOps:**
1. Go to **Pipelines** → Select your pipeline → **Edit**
2. Click **Variables**
3. Click on `ACCESS_TOKEN`
4. Update the value
5. Ensure **Keep this value secret** is checked
6. Click **OK** and **Save**

**GitLab CI:**
1. Go to **Settings** → **CI/CD** → **Variables**
2. Expand the **Variables** section
3. Find `ACCESS_TOKEN` and click **Edit**
4. Update the value
5. Ensure **Masked** is checked
6. Click **Update variable**

#### **Step 3: Verify Rotation**
Trigger a manual pipeline run to verify the new token works:

```bash
# GitHub Actions: Go to Actions tab → Select workflow → Run workflow
# Azure DevOps: Click "Run pipeline"
# GitLab CI: CI/CD → Pipelines → Run pipeline
```

---

## 🔔 Monitoring and Alerts

### Automated Alerts

The solution includes automated monitoring that will:

1. **Daily Health Checks**
   - Tests run daily at 2 AM UTC
   - Catches token expiration before business hours

2. **Weekly Status Reports**
   - Validates token every Monday
   - Creates GitHub issues if token is invalid

3. **Failed Pipeline Notifications**
   - Immediate alerts on token validation failures
   - Clear error messages with remediation steps

### Manual Token Check

You can manually check token status anytime:

```powershell
# Check token validity
python token_manager.py

# Exit code: 0 = valid, 1 = invalid/expired
echo $LASTEXITCODE  # PowerShell
echo $?             # Bash
```

---

## 🎯 Best Practices

### 1. **Proactive Rotation**
Don't wait for tokens to expire. Set a reminder to rotate tokens every 7-14 days.

### 2. **Document Token Source**
Keep a record of where/how to generate new tokens:
- API provider portal URL
- Contact person for token generation
- Any special permissions required

### 3. **Use Separate Tokens**
Use different tokens for different environments:
- Development: Short-lived tokens (7 days)
- QA/Staging: Medium-lived tokens (14 days)
- Production: Long-lived tokens (30 days) with strict rotation schedule

### 4. **Monitor Pipeline Logs**
Check pipeline logs regularly for token validation messages:
```
✅ Token validation successful: Token is valid and active
```

### 5. **Test Token Locally First**
Before updating CI/CD secrets, validate the new token locally:
```powershell
$env:ACCESS_TOKEN = "new-token-here"
python token_manager.py
```

### 6. **Keep Backups**
Maintain the previous working token for 24 hours after rotation as a rollback option.

---

## 🐛 Troubleshooting

### Issue: "ACCESS_TOKEN not set in environment"

**Solution:**
```powershell
# Verify environment variables are set
echo $env:ACCESS_TOKEN
echo $env:BASE_URL

# Set them if missing
$env:ACCESS_TOKEN = "your-token"
$env:BASE_URL = "https://api-qa.creditmobility.net"
```

### Issue: "Token validation timed out"

**Possible Causes:**
- Network connectivity issues
- VPN required but not connected
- API endpoint is down
- Firewall blocking requests

**Solution:**
```powershell
# Test network connectivity
Invoke-WebRequest -Uri $env:BASE_URL -Method HEAD

# Check if VPN is required
# Verify BASE_URL is correct
```

### Issue: "401 Unauthorized" in tests

**Solution:**
1. Verify token is not expired:
   ```powershell
   python token_manager.py
   ```

2. If expired, generate and update new token (see Token Rotation Process above)

3. Ensure token has correct permissions for API endpoints

### Issue: Tests pass locally but fail in CI/CD

**Possible Causes:**
- CI/CD secrets not configured correctly
- Secrets contain extra whitespace
- Wrong BASE_URL for environment

**Solution:**
1. Verify secrets in CI/CD settings (no trailing spaces)
2. Check BASE_URL matches the environment
3. Review pipeline logs for exact error messages

---

## 📊 Quick Reference

### Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `BASE_URL` | API base URL | `https://api-qa.creditmobility.net` |
| `ACCESS_TOKEN` | API access token | `eyJhbG...` (JWT format) |
| `HYPOTHESIS_PROFILE` | Test profile | `ci`, `fast`, `thorough` |

### Commands
| Command | Purpose |
|---------|---------|
| `python token_manager.py` | Validate current token |
| `pytest -v` | Run all tests with validation |
| `pytest -v -m smoke` | Run smoke tests only |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Success - token is valid |
| 1 | Failure - token expired/invalid or missing config |

---

## 🤝 Support

If you encounter issues not covered in this guide:

1. Check pipeline logs for detailed error messages
2. Run `python token_manager.py` locally to diagnose
3. Verify all environment variables are set correctly
4. Contact the API provider for new token generation
5. Review recent changes to API authentication requirements

---

## 📝 Change Log

- **v1.0** - Initial token management implementation
  - Added `token_manager.py` utility
  - Enhanced `conftest.py` with validation hook
  - Created GitHub Actions workflows
  - Created Azure DevOps pipeline
  - Comprehensive documentation

---

**Last Updated:** January 2026  
**Maintained By:** API Automation Team
