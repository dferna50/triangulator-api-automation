"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from datetime import datetime
from typing import Dict
from hypothesis import settings, Verbosity, Phase
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Token validation on startup
_token_validated = False

# ========== HYPOTHESIS PROFILES ==========
# These control how many test examples Hypothesis generates

# CI Profile - Fast, for CI/CD pipelines
settings.register_profile(
    "ci",
    max_examples=10,           # ← Change this to increase tests
    deadline=5000,             # 5 seconds per example
    suppress_health_check=[],
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
)

# Fast Profile - Quick testing during development (DEFAULT)
settings.register_profile(
    "fast",
    max_examples=20,           # ← Change this to increase tests
    deadline=10000,            # 10 seconds per example
    suppress_health_check=[],
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
)

# Default Profile - Balanced testing
settings.register_profile(
    "default",
    max_examples=50,           # ← Change this to increase tests
    deadline=30000,            # 30 seconds per example
    suppress_health_check=[],
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
)

# Thorough Profile - Comprehensive testing for releases
settings.register_profile(
    "thorough",
    max_examples=200,          # ← Increased from 100 to 200
    deadline=None,             # No deadline
    suppress_health_check=[],
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
)

# Exhaustive Profile - Maximum testing (very slow!)
settings.register_profile(
    "exhaustive",
    max_examples=500,          # ← Change this to increase tests
    deadline=None,             # No deadline
    suppress_health_check=[],
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
)

# Load profile from environment or use 'fast' as default
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "fast"))

# ========== PYTEST CONFIGURATION ==========

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "security: Security-focused tests")
    config.addinivalue_line("markers", "property: Property-based tests")
    config.addinivalue_line("markers", "stateful: Stateful workflow tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "csv_upload: CSV upload workflow tests")


def pytest_sessionstart(session):
    """Validate access token before running any tests"""
    global _token_validated
    
    if _token_validated:
        return
    
    # Only validate if both env vars are set
    base_url = os.getenv("BASE_URL")
    token = os.getenv("ACCESS_TOKEN")
    
    if not base_url or not token:
        return  # Will be caught by fixtures
    
    # Perform token validation
    try:
        from token_manager import TokenManager
        logger.info("Validating access token before test execution...")
        
        manager = TokenManager(base_url, token)
        is_valid, message = manager.validate_token()
        
        if is_valid:
            logger.info(f"✅ Token validation successful: {message}")
            _token_validated = True
        else:
            logger.error(f"❌ Token validation failed: {message}")
            logger.error("=" * 70)
            logger.error("CRITICAL: Access token is expired or invalid!")
            logger.error("Action required:")
            logger.error("1. Generate a new access token from your API provider")
            logger.error("2. Update ACCESS_TOKEN environment variable")
            logger.error("3. For CI/CD: Update the secret in your pipeline settings")
            logger.error("=" * 70)
            pytest.exit("Access token validation failed - tests cannot proceed", returncode=1)
    except ImportError:
        logger.warning("token_manager module not found - skipping token validation")
    except Exception as e:
        logger.warning(f"Token validation encountered an error: {e}")


# ========== FIXTURES ==========

@pytest.fixture(scope="session")
def base_url() -> str:
    """Get API base URL from environment"""
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("BASE_URL not set in environment")
    return url


@pytest.fixture(scope="session")
def access_token() -> str:
    """Get access token from environment"""
    token = os.getenv("ACCESS_TOKEN")
    if not token:
        pytest.skip("ACCESS_TOKEN not set in environment")
    return token


@pytest.fixture(scope="session")
def auth_headers(access_token: str) -> Dict[str, str]:
    """Get authentication headers"""
    return {"x-access-token": access_token}


@pytest.fixture(scope="session")
def api_client(base_url: str, access_token: str):
    """Get API client instance"""
    from helpers import APIClient
    return APIClient(base_url, access_token)


@pytest.fixture(scope="session")
def retry_strategy():
    """Get retry strategy instance"""
    from helpers import RetryStrategy
    return RetryStrategy(max_retries=3, initial_delay=1.0)


@pytest.fixture(scope="session")
def test_data():
    """Get common test data constants"""
    from helpers import TestDataConstants
    return TestDataConstants()


@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    """Monitor test execution time"""
    start_time = datetime.now()
    
    yield
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log slow tests
    if duration > 10:
        print(f"\n⚠️  Slow test: {request.node.name} took {duration:.2f}s")
