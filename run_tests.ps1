# PowerShell script to run Schemathesis tests
# Usage: .\run_tests.ps1 [test_type]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "schema", "security", "property", "stateful", "smoke", "quick")]
    [string]$TestType = "all",
    
    [Parameter(Mandatory=$false)]
    [bool]$Parallel = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$Coverage,
    
    [Parameter(Mandatory=$false)]
    [switch]$HtmlReport,
    
    [Parameter(Mandatory=$false)]
    [int]$Workers = 5,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("ci", "fast", "default", "thorough", "exhaustive")]
    [string]$HypothesisProfile = "ci"
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"

Write-Host " Starting Schemathesis Test Suite" -ForegroundColor $InfoColor
Write-Host "Test Type: $TestType" -ForegroundColor $InfoColor
Write-Host "=" * 60 -ForegroundColor $InfoColor

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env file..." -ForegroundColor $InfoColor
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Set Hypothesis profile
$env:HYPOTHESIS_PROFILE = $HypothesisProfile
Write-Host "Hypothesis Profile: $HypothesisProfile" -ForegroundColor $InfoColor

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    .\venv\Scripts\Activate.ps1
}

# Check environment variables
if (-not $env:ACCESS_TOKEN) {
    Write-Host " ACCESS_TOKEN not set!" -ForegroundColor $ErrorColor
    Write-Host "Please set ACCESS_TOKEN environment variable or add it to .env file" -ForegroundColor Yellow
    exit 1
}

if (-not $env:BASE_URL) {
    Write-Host "  BASE_URL not set, using default" -ForegroundColor Yellow
    $env:BASE_URL = "https://api-qa.creditmobility.net"
}

# Create reports directory
New-Item -ItemType Directory -Force -Path "reports" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Build pytest command
$pytestCmd = "pytest"
$pytestArgs = @("-v", "--tb=short")

# Add test selection based on type
switch ($TestType) {
    "all" {
        Write-Host "Running all tests..." -ForegroundColor $InfoColor
    }
    "schema" {
        Write-Host "Running schema compliance tests..." -ForegroundColor $InfoColor
        $pytestArgs += "test_schemathesis_comprehensive.py::test_api_schema_compliance"
    }
    "security" {
        Write-Host "Running security tests..." -ForegroundColor $InfoColor
        $pytestArgs += "-m", "security"
    }
    "property" {
        Write-Host "Running property-based tests..." -ForegroundColor $InfoColor
        $pytestArgs += "test_advanced_strategies.py"
    }
    "stateful" {
        Write-Host "Running stateful workflow tests..." -ForegroundColor $InfoColor
        $pytestArgs += "test_stateful_workflows.py"
    }
    "smoke" {
        Write-Host "Running smoke tests..." -ForegroundColor $InfoColor
        $pytestArgs += "-m", "smoke", "-x"
    }
    "quick" {
        Write-Host "Running quick test suite..." -ForegroundColor $InfoColor
        $pytestArgs += "-m", "not slow", "--hypothesis-profile=quick"
    }
}

# Add parallel execution (enabled by default)
if ($Parallel) {
    Write-Host "Enabling parallel execution with $Workers workers..." -ForegroundColor $InfoColor
    $pytestArgs += "-n", $Workers
} else {
    Write-Host "Running tests sequentially (use -Parallel to enable parallel execution)..." -ForegroundColor Yellow
}

# Add coverage
if ($Coverage) {
    Write-Host "Enabling coverage reporting..." -ForegroundColor $InfoColor
    $pytestArgs += "--cov=.", "--cov-report=html:reports/coverage", "--cov-report=term"
}

# Add HTML report
if ($HtmlReport) {
    Write-Host "Enabling HTML report generation..." -ForegroundColor $InfoColor
    $pytestArgs += "--html=reports/report.html", "--self-contained-html"
}

# Add JSON report
$pytestArgs += "--json-report", "--json-report-file=reports/report.json"

# Add Hypothesis statistics
$pytestArgs += "--hypothesis-show-statistics"

# Run tests
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor $InfoColor
Write-Host "Executing: $pytestCmd $($pytestArgs -join ' ')" -ForegroundColor $InfoColor
Write-Host ("=" * 60) -ForegroundColor $InfoColor
Write-Host ""

$startTime = Get-Date

& python -m pytest $pytestArgs
$exitCode = $LASTEXITCODE
$endTime = Get-Date
$duration = $endTime - $startTime

# Print summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor $InfoColor
Write-Host "Test Execution Summary" -ForegroundColor $InfoColor
Write-Host ("=" * 60) -ForegroundColor $InfoColor
Write-Host "Duration: $($duration.ToString('mm\:ss'))" -ForegroundColor $InfoColor
Write-Host "Exit Code: $exitCode" -ForegroundColor $(if ($exitCode -eq 0) { $SuccessColor } else { $ErrorColor })

if ($exitCode -eq 0) {
    Write-Host "`n All tests passed!" -ForegroundColor $SuccessColor
} else {
    Write-Host "`n Some tests failed!" -ForegroundColor $ErrorColor
}

# Show report locations
if ($HtmlReport) {
    Write-Host "`n HTML Report: reports/report.html" -ForegroundColor $InfoColor
}
if ($Coverage) {
    Write-Host " Coverage Report: reports/coverage/index.html" -ForegroundColor $InfoColor
}
Write-Host " JSON Report: reports/report.json" -ForegroundColor $InfoColor

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor $InfoColor

exit $exitCode
