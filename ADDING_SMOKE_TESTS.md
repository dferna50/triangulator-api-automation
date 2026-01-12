# Adding Smoke Tests (Optional)

## Current Status

Your test suite doesn't currently have any tests marked with `@pytest.mark.smoke`. The CI/CD pipelines have been configured to run all tests directly.

## Why Add Smoke Tests?

Smoke tests are a **small subset of critical tests** that:
- ✅ Run very quickly (< 1 minute)
- ✅ Validate core functionality
- ✅ Provide fast feedback in CI/CD
- ✅ Can run before the full suite

## How to Add Smoke Markers

### Step 1: Identify Critical Tests

Choose 3-5 tests that validate the most important functionality:
- Basic API connectivity
- Authentication
- Core endpoint responses

### Step 2: Add the Marker

Add `@pytest.mark.smoke` to critical tests:

```python
@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.csv_upload
def test_upload_valid_file_add_mode(self):
    """TC-CSV-001: Upload valid CSV file with 'add' upload type"""
    # ... test code ...
```

### Example: Mark 3-5 Critical Tests

```python
# test_csv_upload_positive.py

class TestCSVUploadPositive:
    
    @pytest.mark.smoke  # ← Add this
    @pytest.mark.integration
    @pytest.mark.csv_upload
    def test_upload_valid_file_add_mode(self):
        """Critical: Validate basic CSV upload works"""
        # ...
    
    @pytest.mark.smoke  # ← Add this
    @pytest.mark.integration
    @pytest.mark.csv_upload
    def test_step1_get_presigned_url_success(self):
        """Critical: Validate we can get presigned URLs"""
        # ...

# test_data_validation.py

class TestCSVFormatValidation:
    
    @pytest.mark.smoke  # ← Add this
    @pytest.mark.data_validation
    def test_csv_valid_headers(self):
        """Critical: Validate CSV format validation works"""
        # ...
```

### Step 3: Update CI/CD Workflows (Optional)

If you want to run smoke tests before the full suite, update the workflows:

#### GitHub Actions (`.github/workflows/api-tests.yml`)

```yaml
    - name: Run Smoke Tests
      env:
        BASE_URL: ${{ secrets.BASE_URL }}
        ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
        HYPOTHESIS_PROFILE: ci
      run: |
        pytest -v -m smoke --tb=short
    
    - name: Run Full Tests
      if: success()
      env:
        BASE_URL: ${{ secrets.BASE_URL }}
        ACCESS_TOKEN: ${{ secrets.ACCESS_TOKEN }}
        HYPOTHESIS_PROFILE: ci
      run: |
        pytest -v --tb=short --maxfail=5 -x
```

#### Azure DevOps (`azure-pipelines.yml`)

```yaml
    - script: |
        pytest -v -m smoke --tb=short --junitxml=junit/smoke-results.xml
      env:
        BASE_URL: $(BASE_URL)
        ACCESS_TOKEN: $(ACCESS_TOKEN)
        HYPOTHESIS_PROFILE: $(HYPOTHESIS_PROFILE)
      displayName: 'Run Smoke Tests'
    
    - script: |
        pytest -v --tb=short --maxfail=10 -x --junitxml=junit/test-results.xml
      env:
        BASE_URL: $(BASE_URL)
        ACCESS_TOKEN: $(ACCESS_TOKEN)
        HYPOTHESIS_PROFILE: $(HYPOTHESIS_PROFILE)
      displayName: 'Run Full Tests'
```

#### GitLab CI (`.gitlab-ci.yml`)

```yaml
smoke_tests:
  stage: test
  image: python:3.12
  needs: ["validate_token"]
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest -v -m smoke --tb=short --junitxml=report-smoke.xml
  artifacts:
    reports:
      junit: report-smoke.xml

full_tests:
  stage: test
  needs: ["smoke_tests"]
  # ... rest of config
```

### Step 4: Test Locally

```powershell
# Run only smoke tests
pytest -v -m smoke

# Should show something like:
# collected 242 items / 237 deselected / 5 selected
```

## Best Practices

1. **Keep it minimal:** 3-5 tests maximum
2. **Fast execution:** Total smoke tests should run in < 60 seconds
3. **Critical paths only:** Most important workflows
4. **Use existing markers too:** Combine with `@pytest.mark.integration`, etc.

## Current Workflow Behavior

**Without smoke markers:**
- Runs all 242 tests directly
- Takes full execution time
- Uses `pytest -v --tb=short --maxfail=5 -x`

**With smoke markers (if you add them):**
- Runs 3-5 smoke tests first (~30 seconds)
- If smoke tests pass, runs full suite
- If smoke tests fail, stops early (saves time)

## Do You Need Smoke Tests?

**You might NOT need them if:**
- ✅ Your full test suite runs quickly (< 5 minutes)
- ✅ You're okay with full suite runtime in CI/CD
- ✅ All tests are equally important

**You SHOULD add them if:**
- ✅ Full test suite takes > 10 minutes
- ✅ You want faster feedback loops
- ✅ Some tests are more critical than others
- ✅ You want quick validation before full suite

---

**Current Status:** Smoke tests are **optional** and not currently configured. Your pipelines work correctly without them.


tedt 