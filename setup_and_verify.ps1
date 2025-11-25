# Setup and Verify 207 Tests
# This script helps you set up environment and verify test count

param(
    [switch]$LoadEnv = $false,
    [switch]$Verify = $false,
    [switch]$RunSample = $false,
    [switch]$ShowHelp = $false
)

$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Show-Help {
    Write-Host ""
    Write-Host "Setup and Verify 207 Tests" -ForegroundColor $InfoColor
    Write-Host "=" * 70 -ForegroundColor $InfoColor
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $InfoColor
    Write-Host "  .\setup_and_verify.ps1 [-LoadEnv] [-Verify] [-RunSample] [-ShowHelp]"
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor $InfoColor
    Write-Host "  -LoadEnv    Load environment variables from .env file"
    Write-Host "  -Verify     Verify test count (should be 207)"
    Write-Host "  -RunSample  Run a sample test to verify setup"
    Write-Host "  -ShowHelp   Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $InfoColor
    Write-Host "  .\setup_and_verify.ps1 -LoadEnv -Verify"
    Write-Host "  .\setup_and_verify.ps1 -LoadEnv -RunSample"
    Write-Host "  .\setup_and_verify.ps1 -Verify"
    Write-Host ""
}

if ($ShowHelp) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor $InfoColor
Write-Host "API Test Suite - Setup and Verification" -ForegroundColor $InfoColor
Write-Host ("=" * 70) -ForegroundColor $InfoColor
Write-Host ""

# Load environment variables
if ($LoadEnv) {
    Write-Host "Loading environment variables from .env..." -ForegroundColor $InfoColor
    
    if (Test-Path ".env") {
        Get-Content .env | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($key, $value, 'Process')
                Write-Host "  ✅ Set $key" -ForegroundColor $SuccessColor
            }
        }
        Write-Host ""
    } else {
        Write-Host "  ⚠️  .env file not found" -ForegroundColor $WarningColor
        Write-Host "  Please set environment variables manually:" -ForegroundColor $WarningColor
        Write-Host '    $env:BASE_URL = "https://api-qa.creditmobility.net"' -ForegroundColor $WarningColor
        Write-Host '    $env:ACCESS_TOKEN = "your_token_here"' -ForegroundColor $WarningColor
        Write-Host ""
    }
}

# Check environment variables
Write-Host "Checking environment variables..." -ForegroundColor $InfoColor
$baseUrl = $env:BASE_URL
$accessToken = $env:ACCESS_TOKEN

if ($baseUrl) {
    Write-Host "  ✅ BASE_URL: $baseUrl" -ForegroundColor $SuccessColor
} else {
    Write-Host "  ❌ BASE_URL not set" -ForegroundColor $ErrorColor
}

if ($accessToken) {
    $maskedToken = $accessToken.Substring(0, [Math]::Min(20, $accessToken.Length)) + "..."
    Write-Host "  ✅ ACCESS_TOKEN: $maskedToken" -ForegroundColor $SuccessColor
} else {
    Write-Host "  ❌ ACCESS_TOKEN not set" -ForegroundColor $ErrorColor
}

Write-Host ""

# Verify test count
if ($Verify) {
    Write-Host "Verifying test count..." -ForegroundColor $InfoColor
    
    if (-not $baseUrl -or -not $accessToken) {
        Write-Host "  ⚠️  Environment variables not set. Tests will be skipped." -ForegroundColor $WarningColor
        Write-Host "  Use -LoadEnv to load from .env file" -ForegroundColor $WarningColor
        Write-Host ""
    }
    
    Write-Host "  Running: pytest --collect-only" -ForegroundColor $InfoColor
    $output = & pytest --collect-only 2>&1 | Out-String
    
    if ($output -match '(\d+)\s+tests?\s+collected') {
        $count = $matches[1]
        if ($count -eq "207") {
            Write-Host "  ✅ Test count: $count (CORRECT)" -ForegroundColor $SuccessColor
        } else {
            Write-Host "  ⚠️  Test count: $count (Expected: 207)" -ForegroundColor $WarningColor
        }
    } elseif ($output -match 'no tests collected') {
        Write-Host "  ⚠️  No tests collected (environment variables not set?)" -ForegroundColor $WarningColor
    } else {
        Write-Host "  ⚠️  Could not parse test count" -ForegroundColor $WarningColor
        Write-Host "  Output: $($output.Substring(0, [Math]::Min(200, $output.Length)))" -ForegroundColor $WarningColor
    }
    Write-Host ""
}

# Run sample test
if ($RunSample) {
    Write-Host "Running sample test..." -ForegroundColor $InfoColor
    
    if (-not $baseUrl -or -not $accessToken) {
        Write-Host "  ❌ Cannot run test - environment variables not set" -ForegroundColor $ErrorColor
        Write-Host "  Use -LoadEnv to load from .env file" -ForegroundColor $WarningColor
        Write-Host ""
    } else {
        Write-Host "  Running: pytest test_explicit_scenarios.py::TestPublishCourseInventoryExplicit::test_pci_001_valid_parameters -v" -ForegroundColor $InfoColor
        Write-Host ""
        
        & pytest test_explicit_scenarios.py::TestPublishCourseInventoryExplicit::test_pci_001_valid_parameters -v
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "  ✅ Sample test PASSED" -ForegroundColor $SuccessColor
        } else {
            Write-Host ""
            Write-Host "  ❌ Sample test FAILED (exit code: $LASTEXITCODE)" -ForegroundColor $ErrorColor
        }
        Write-Host ""
    }
}

# Show summary
Write-Host ("=" * 70) -ForegroundColor $InfoColor
Write-Host "Summary" -ForegroundColor $InfoColor
Write-Host ("=" * 70) -ForegroundColor $InfoColor

if ($baseUrl -and $accessToken) {
    Write-Host "✅ Environment: Ready" -ForegroundColor $SuccessColor
} else {
    Write-Host "❌ Environment: Not configured" -ForegroundColor $ErrorColor
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor $InfoColor
Write-Host "  1. Set environment variables (if not done):" -ForegroundColor $InfoColor
Write-Host "     .\setup_and_verify.ps1 -LoadEnv" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "  2. Verify test count:" -ForegroundColor $InfoColor
Write-Host "     .\setup_and_verify.ps1 -Verify" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "  3. Run sample test:" -ForegroundColor $InfoColor
Write-Host "     .\setup_and_verify.ps1 -RunSample" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "  4. Run full test suite:" -ForegroundColor $InfoColor
Write-Host "     .\run_tests.ps1 -TestType all -HtmlReport" -ForegroundColor $InfoColor
Write-Host ""
Write-Host ("=" * 70) -ForegroundColor $InfoColor
Write-Host ""
