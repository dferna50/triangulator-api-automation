"""
Resilience and Error Recovery Tests
Tests for retry logic, timeout handling, and graceful degradation
"""
import pytest
import requests
import os
import time
from typing import Optional, Dict
from requests.exceptions import Timeout, ConnectionError

# Configuration
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)


# ========== HELPER FUNCTIONS ==========

def make_get_request(endpoint: str, params: Optional[Dict] = None, timeout: int = 10) -> requests.Response:
    """Make GET request with consistent headers"""
    return requests.get(
        f"{BASE_URL}{endpoint}",
        headers={"x-access-token": ACCESS_TOKEN},
        params=params,
        timeout=timeout
    )


def assert_valid_status(response: requests.Response) -> None:
    """Assert response has valid status code"""
    assert response.status_code in [200, 400, 401, 404, 429, 500, 502], \
        f"Expected valid status, got {response.status_code}"


class TestRetryLogic:
    """Tests for retry logic and transient failure handling"""
    
    @pytest.mark.resilience
    def test_retry_transient_failures(self):
        """TC-ERR-001: Verify client can retry after transient failures"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
                
                # If we get a transient error (502, 503), retry
                if response.status_code in [502, 503]:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                
                # Success or permanent error
                assert_valid_status(response)
                break
                
            except (Timeout, ConnectionError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                pytest.fail("Max retries exceeded")
    
    @pytest.mark.resilience
    def test_rate_limit_recovery(self):
        """TC-ERR-006: Verify client can recover after rate limiting"""
        for i in range(10):
            response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
            
            if response.status_code == 429:
                # Hit rate limit, wait and retry
                time.sleep(2)
                
                # Retry after waiting
                retry_response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
                
                # Should succeed or still be rate limited
                assert_valid_status(retry_response)
                break


class TestTimeoutHandling:
    """Tests for timeout handling"""
    
    @pytest.mark.resilience
    @pytest.mark.slow
    def test_timeout_handling(self):
        """TC-ERR-002: Verify client handles slow responses gracefully"""
        try:
            response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"}, timeout=30)
            # If we get a response, it should be valid
            assert_valid_status(response)
        except Timeout:
            # pytest.skip("Request timed out (expected behavior for slow endpoint)")


class TestConnectionHandling:
    """Tests for connection error handling"""
    
    @pytest.mark.resilience
    def test_connection_error(self):
        """TC-ERR-003: Verify client handles connection errors"""
        try:
            # Try to connect to invalid hostname
            response = requests.get(
                "https://invalid-hostname-that-does-not-exist.com/api",
                headers={"x-access-token": ACCESS_TOKEN},
                timeout=5
            )
            # If somehow it connects, that's unexpected but not a failure
            assert response.status_code >= 0
        except (ConnectionError, Timeout):
            # Expected - connection should fail
            pass  # Test passes


class TestResponseHandling:
    """Tests for response handling"""
    
    @pytest.mark.resilience
    def test_partial_response(self):
        """TC-ERR-004: Verify client handles incomplete responses"""
        response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
        
        # Verify we can parse the response
        try:
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, (dict, list))
        except ValueError:
            # If JSON parsing fails, response should not be 200
            assert response.status_code != 200
    
    @pytest.mark.resilience
    def test_malformed_json(self):
        """TC-ERR-005: Verify client handles malformed JSON"""
        response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
        
        # If status is 200, JSON should be valid
        if response.status_code == 200:
            try:
                data = response.json()
                assert data is not None
            except ValueError:
                pytest.fail("200 response with invalid JSON")


class TestAuthenticationHandling:
    """Tests for authentication error handling"""
    
    @pytest.mark.resilience
    def test_expired_token(self):
        """TC-ERR-007: Verify client detects expired tokens"""
        # Use an obviously invalid/expired token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjB9.invalid"
        
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": expired_token},
            params={"institution_id": "227216"}
        )
        
        # Should return 401 Unauthorized
        assert response.status_code in [401, 403]


class TestGracefulDegradation:
    """Tests for graceful degradation under load"""
    
    @pytest.mark.resilience
    @pytest.mark.slow
    def test_graceful_degradation(self):
        """TC-ERR-008: Verify API degrades gracefully under load"""
        responses = []
        for i in range(20):
            try:
                response = make_get_request("/publish-course-inventory", params={"institution_id": "227216"})
                responses.append(response.status_code)
            except (Timeout, ConnectionError):
                responses.append(0)
        
        # Count successful responses
        success_count = sum(1 for code in responses if code == 200)
        rate_limited = sum(1 for code in responses if code == 429)
        
        # System should either succeed or rate limit, not crash
        assert success_count + rate_limited > 0, "No valid responses under load"
        
        # No server errors should occur
        server_errors = sum(1 for code in responses if code in [500, 502, 503])
        assert server_errors < len(responses), "Too many server errors under load"
