# Triangulator API Automation

This repository contains the automated test suite for the **Credit Mobility Triangulator API**. It is built using Python, `pytest`, `Schemathesis`, and `Hypothesis` to provide deep, property-based testing and validation across multiple institutional contexts.

## Architecture & Tooling

- **Language**: Python 3.12+
- **Core Framework**: `pytest`
- **Generative Testing**: `Schemathesis` & `Hypothesis`
- **Execution**: PowerShell (`run_tests.ps1`) for local runs; GitHub Actions for CI.

## Setup & Configuration

1. **Clone the Repository**
2. **Environment Variables**: Create a `.env` file in the root directory. The following variables are required:
   - `BASE_URL`: The root URL of the Triangulator API (e.g., `https://api-qa.creditmobility.net`).
   - `ACCESS_TOKEN`: The standard JWT token for default authentication.
   - `ORG_ACCESS_TOKEN`: The organization-level JWT token used for multi-institution testing (e.g. Pima, Nevada-Reno, Arizona State).
3. **Virtual Environment**: 
   The `run_tests.ps1` script will automatically create a virtual environment (`venv`) and install all required dependencies from `requirements.txt` upon first run.

## Running Tests Locally (Windows)

The recommended way to run the test suite locally is via the provided PowerShell script `run_tests.ps1`. This script automatically loads variables from your `.env` file, validates your API tokens, and enables parallel test execution across 4 workers.

```powershell
# Run the entire test suite
.\run_tests.ps1 -TestType all

# Generate an HTML report (saved to reports/report.html)
.\run_tests.ps1 -TestType all -HtmlReport

# Run specific test modules
.\run_tests.ps1 -TestType smoke
.\run_tests.ps1 -TestType stateful
```

### Available Test Types:
- `all`: Runs the entire suite.
- `schema`: Tests API schema compliance.
- `security`: Runs targeted security tests (SQL Injection, XSS, broken auth).
- `property`: Runs advanced property-based generation tests.
- `stateful`: Tests end-to-end multi-step stateful workflows (e.g., S3 CSV uploads).
- `smoke`: Runs quick smoke tests to verify core connectivity.

## CI/CD Pipeline

The test suite is fully integrated into GitHub Actions via `.github/workflows/api-tests.yml`. 
- **Triggers**: Runs automatically on `push`, `pull_request` to `main/develop`, on a daily cron schedule, and can be triggered manually via `workflow_dispatch`.
- **Secrets**: The pipeline requires `BASE_URL`, `ACCESS_TOKEN`, and `ORG_ACCESS_TOKEN` to be configured as GitHub Repository Secrets.
- **Reporting**: HTML and JSON test reports are automatically published as workflow artifacts upon completion.

## Test Strategy & Conventions

1. **Authentication Contexts**: 
   - Tests automatically parameterize across different authentication contexts: standard single-institution tokens and organization-level tokens (targeting specific `institution_id` values).
   - Token validation happens automatically at startup (`pytest_sessionstart`). Tests will fail fast before any API calls are made if tokens are expired or invalid.
2. **Stateful Workflows**:
   - The test suite natively handles complex flows, like the 3-step CSV upload process: `GET /get-presigned-url` → Upload to S3 → `POST /consume-rules`.
3. **Hypothesis Profiles**:
   - Test generation volume is controlled via the `HYPOTHESIS_PROFILE` environment variable (defaults to `ci`). This controls the depth of property-based testing.

## Contribution Guidelines

When adding new tests or expanding the suite:
- Keep test files self-contained. Ensure each test file defines its own request helpers for maximum isolation (e.g., `make_get_request`, `make_post_request`).
- Do not rely on hardcoded state that may expire or become inconsistent.
- Always validate against both standard and organizational token structures if hitting institution-specific endpoints.
