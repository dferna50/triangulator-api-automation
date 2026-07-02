"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from datetime import datetime
from typing import Dict
from hypothesis import settings, Phase
import logging
import requests

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
    tokens_to_validate = []
    
    if os.getenv("ACCESS_TOKEN"):
        tokens_to_validate.append((os.getenv("ACCESS_TOKEN"), None, None))
    if os.getenv("ORG_ACCESS_TOKEN"):
        tokens_to_validate.append((os.getenv("ORG_ACCESS_TOKEN"), "182290", "IPEDS"))
        
    if not base_url or not tokens_to_validate:
        return  # Will be caught by fixtures
    
    # Perform token validation
    try:
        from token_manager import TokenManager
        logger.info("Validating access tokens before test execution...")
        
        for token, inst_id, coding_scheme in tokens_to_validate:
            manager = TokenManager(base_url, token)
            # Use getattr to safely call the updated signature if available
            if hasattr(manager, 'validate_token'):
                try:
                    is_valid, message = manager.validate_token(institution_id=inst_id, coding_scheme=coding_scheme)
                except TypeError:
                    is_valid, message = manager.validate_token()
                    
                if is_valid:
                    logger.info(f"✅ Token validation successful: {message}")
                else:
                    logger.error(f"❌ Token validation failed: {message}")
                    logger.error("=" * 70)
                    logger.error("CRITICAL: Access token is expired or invalid!")
                    pytest.exit("Access token validation failed - tests cannot proceed", returncode=1)
                
        _token_validated = True
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


@pytest.fixture(autouse=True)
def monitor_test_performance(request):
    """Monitor test execution time"""
    start_time = datetime.now()
    
    yield
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log slow tests
    if duration > 10:
        print(f"\n⚠️  Slow test: {request.node.name} took {duration:.2f}s")


# ========== DYNAMIC TOKEN PARAMETERIZATION ==========

def get_auth_scenarios():
    scenarios = []
    standard_token = os.getenv("ACCESS_TOKEN")
    if standard_token:
        scenarios.append({"name": "StandardToken", "token": standard_token, "params": {}})
        
    org_token = os.getenv("ORG_ACCESS_TOKEN")
    if org_token:
        scenarios.extend([
            {"name": "OrgToken-Pima", "token": org_token, "params": {"institution_id": "105525", "coding_scheme": "IPEDS"}},
            {"name": "OrgToken-Nevada", "token": org_token, "params": {"institution_id": "182290", "coding_scheme": "IPEDS"}},
            {"name": "OrgToken-Arizona", "token": org_token, "params": {"institution_id": "104151", "coding_scheme": "IPEDS"}}
        ])
    # Fallback if neither is set (let fixtures handle errors)
    if not scenarios:
        scenarios.append({"name": "NoToken", "token": "", "params": {}})
    return scenarios

AUTH_SCENARIOS = get_auth_scenarios()

# Store original request globally
_original_request = requests.Session.request

@pytest.fixture(params=AUTH_SCENARIOS, ids=[s["name"] for s in AUTH_SCENARIOS], autouse=True)
def auth_context(request, monkeypatch):
    """
    Parametrizes every test across available authentication contexts.
    Monkeypatches requests.Session.request to automatically inject the token and parameters.
    """
    scenario = request.param
    token = scenario["token"]
    
    # Inject into environment for any test that reads directly
    monkeypatch.setenv("CURRENT_TEST_TOKEN", token)
    inst_id = scenario["params"].get("institution_id")
    coding_scheme = scenario["params"].get("coding_scheme")
    if inst_id:
        monkeypatch.setenv("CURRENT_INSTITUTION_ID", inst_id)
        monkeypatch.setenv("CURRENT_CODING_SCHEME", coding_scheme)
    else:
        monkeypatch.delenv("CURRENT_INSTITUTION_ID", raising=False)
        monkeypatch.delenv("CURRENT_CODING_SCHEME", raising=False)
        
    # Monkeypatch requests
    def patched_request(self, method, url, **kwargs):
        base_url = os.getenv("BASE_URL")
        # Ensure we only monkeypatch requests meant for our API (e.g. skip S3 uploads)
        if base_url and not url.startswith(base_url):
            return _original_request(self, method, url, **kwargs)
            
        if token:
            headers = kwargs.get("headers")
            if headers is None:
                headers = {}
            else:
                # Create a copy so we don't mutate shared references
                headers = dict(headers)
                
            headers["x-access-token"] = token
            kwargs["headers"] = headers
            
        if inst_id:
            params = kwargs.get("params")
            if params is None:
                params = {}
            elif isinstance(params, dict):
                params = dict(params)
            
            if isinstance(params, dict):
                params["institution_id"] = inst_id
                params["coding_scheme"] = coding_scheme
                kwargs["params"] = params
                
            json_data = kwargs.get("json")
            if json_data and isinstance(json_data, dict) and "institution_id" in json_data:
                json_data = dict(json_data)
                json_data["institution_id"] = inst_id
                kwargs["json"] = json_data
                
        return _original_request(self, method, url, **kwargs)
        
    monkeypatch.setattr(requests.Session, "request", patched_request)
    
    return scenario

try:
    import schemathesis
    @schemathesis.hooks.register("before_call")
    def inject_auth(context, case):
        token = os.getenv("CURRENT_TEST_TOKEN")
        if token:
            case.headers = case.headers or {}
            case.headers["x-access-token"] = token
            
        inst_id = os.getenv("CURRENT_INSTITUTION_ID")
        if inst_id:
            case.query = case.query or {}
            case.query["institution_id"] = inst_id
            case.query["coding_scheme"] = os.getenv("CURRENT_CODING_SCHEME")
except ImportError:
    pass

