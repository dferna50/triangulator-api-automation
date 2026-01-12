# Token Validation Script for Windows PowerShell
# This script validates your API access token before running tests

param(
    [string]$BaseUrl = $env:BASE_URL,
    [string]$AccessToken = $env:ACCESS_TOKEN,
    [switch]$SetEnvVars,
    [switch]$Help
)

function Show-Help {
    Write-Host ""
    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host "  Token Validation Script" -ForegroundColor Cyan
    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\validate_token.ps1                  # Validate current environment variables"
    Write-Host "  .\validate_token.ps1 -SetEnvVars      # Interactive setup with validation"
    Write-Host "  .\validate_token.ps1 -Help            # Show this help message"
    Write-Host ""
    Write-Host "Environment Variables Required:" -ForegroundColor Yellow
    Write-Host "  BASE_URL      - API base URL (e.g., https://api-qa.creditmobility.net)"
    Write-Host "  ACCESS_TOKEN  - Your API access token"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  # Set variables manually then validate"
    Write-Host "  `$env:BASE_URL = 'https://api-qa.creditmobility.net'"
    Write-Host "  `$env:ACCESS_TOKEN = 'your-token-here'"
    Write-Host "  .\validate_token.ps1"
    Write-Host ""
    Write-Host "  # Interactive setup"
    Write-Host "  .\validate_token.ps1 -SetEnvVars"
    Write-Host ""
}

function Set-EnvironmentVariables {
    Write-Host ""
    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host "  Interactive Environment Setup" -ForegroundColor Cyan
    Write-Host "==================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Get BASE_URL
    $currentBaseUrl = $env:BASE_URL
    if ($currentBaseUrl) {
        Write-Host "Current BASE_URL: $currentBaseUrl" -ForegroundColor Gray
    }
    $newBaseUrl = Read-Host "Enter BASE_URL (press Enter to keep current)"
    if ($newBaseUrl) {
        $env:BASE_URL = $newBaseUrl.Trim()
        Write-Host "✓ BASE_URL updated" -ForegroundColor Green
    } elseif (-not $currentBaseUrl) {
        Write-Host "✗ BASE_URL is required!" -ForegroundColor Red
        return $false
    }
    
    # Get ACCESS_TOKEN
    $currentToken = $env:ACCESS_TOKEN
    if ($currentToken) {
        $maskedToken = "*" * 20 + $currentToken.Substring([Math]::Max(0, $currentToken.Length - 8))
        Write-Host "Current ACCESS_TOKEN: $maskedToken" -ForegroundColor Gray
    }
    $newToken = Read-Host "Enter ACCESS_TOKEN (press Enter to keep current)"
    if ($newToken) {
        $env:ACCESS_TOKEN = $newToken.Trim()
        Write-Host "✓ ACCESS_TOKEN updated" -ForegroundColor Green
    } elseif (-not $currentToken) {
        Write-Host "✗ ACCESS_TOKEN is required!" -ForegroundColor Red
        return $false
    }
    
    Write-Host ""
    Write-Host "Environment variables configured!" -ForegroundColor Green
    return $true
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Interactive setup if requested
if ($SetEnvVars) {
    $success = Set-EnvironmentVariables
    if (-not $success) {
        exit 1
    }
    $BaseUrl = $env:BASE_URL
    $AccessToken = $env:ACCESS_TOKEN
}

# Main validation logic
Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Token Validation Check" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Check if variables are set
if (-not $BaseUrl) {
    Write-Host "❌ ERROR: BASE_URL is not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it using:" -ForegroundColor Yellow
    Write-Host "  `$env:BASE_URL = 'https://api-qa.creditmobility.net'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or run with -SetEnvVars flag for interactive setup:" -ForegroundColor Yellow
    Write-Host "  .\validate_token.ps1 -SetEnvVars" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

if (-not $AccessToken) {
    Write-Host "❌ ERROR: ACCESS_TOKEN is not set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Set it using:" -ForegroundColor Yellow
    Write-Host "  `$env:ACCESS_TOKEN = 'your-token-here'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Or run with -SetEnvVars flag for interactive setup:" -ForegroundColor Yellow
    Write-Host "  .\validate_token.ps1 -SetEnvVars" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "✓ BASE_URL: $BaseUrl" -ForegroundColor Green
$maskedToken = "*" * 20 + $AccessToken.Substring([Math]::Max(0, $AccessToken.Length - 8))
Write-Host "✓ ACCESS_TOKEN: $maskedToken" -ForegroundColor Green
Write-Host ""

# Run Python validation
Write-Host "Validating token with API..." -ForegroundColor Yellow
Write-Host ""

try {
    $result = python token_manager.py
    $exitCode = $LASTEXITCODE
    
    Write-Host $result
    Write-Host ""
    
    if ($exitCode -eq 0) {
        Write-Host "==================================================================" -ForegroundColor Green
        Write-Host "  ✅ VALIDATION SUCCESSFUL" -ForegroundColor Green
        Write-Host "==================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your token is valid and tests can run!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Yellow
        Write-Host "  • Run tests: pytest -v" -ForegroundColor Gray
        Write-Host "  • Run smoke tests: pytest -v -m smoke" -ForegroundColor Gray
        Write-Host "  • Run specific test: pytest test_csv_upload_positive.py -v" -ForegroundColor Gray
        Write-Host ""
        exit 0
    } else {
        Write-Host "==================================================================" -ForegroundColor Red
        Write-Host "  ❌ VALIDATION FAILED" -ForegroundColor Red
        Write-Host "==================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Action Required:" -ForegroundColor Yellow
        Write-Host "  1. Generate a new access token from your API provider" -ForegroundColor Gray
        Write-Host "  2. Update the token: `$env:ACCESS_TOKEN = 'new-token'" -ForegroundColor Gray
        Write-Host "  3. Run this script again to verify: .\validate_token.ps1" -ForegroundColor Gray
        Write-Host ""
        Write-Host "For CI/CD Pipelines:" -ForegroundColor Yellow
        Write-Host "  • Update the ACCESS_TOKEN secret in your pipeline settings" -ForegroundColor Gray
        Write-Host "  • See TOKEN_MANAGEMENT.md for detailed instructions" -ForegroundColor Gray
        Write-Host ""
        exit 1
    }
} catch {
    Write-Host "❌ ERROR: Failed to run token validation" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure Python is installed and token_manager.py exists" -ForegroundColor Yellow
    exit 1
}
