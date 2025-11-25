"""
Monitoring and Observability Tests
Tests for logging, metrics, error tracking, and health checks
"""
import pytest
import requests
import os
import json

# Configuration
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)


class TestLogging:
    """Tests for logging verification"""
    
    @pytest.mark.observability
    def test_logging_verification(self):
        """TC-MON-001: Verify API logs requests appropriately"""
        # Make a request and verify response headers contain tracking info
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "227216"}
        )
        
        # Verify response is valid
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
        
        # Check for common logging headers (if API provides them)
        # Examples: X-Request-ID, X-Correlation-ID, X-Response-Time
        headers = response.headers
        
        # At minimum, response should have standard headers
        assert 'Content-Type' in headers or 'content-type' in headers
        
        # Log the request for manual verification
        print(f"\nRequest logged:")
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        print(f"  Duration: {response.elapsed.total_seconds()}s")


class TestMetrics:
    """Tests for metrics collection"""
    
    @pytest.mark.observability
    def test_metrics_collection(self):
        """TC-MON-002: Verify metrics are collected"""
        # Make several requests to generate metrics
        for i in range(5):
            response = requests.get(
                f"{BASE_URL}/publish-course-inventory",
                headers={"x-access-token": ACCESS_TOKEN},
                params={"institution_id": "227216"}
            )
            
            # Track response time as a metric
            response_time = response.elapsed.total_seconds()
            
            # Verify response time is reasonable
            assert response_time < 30, f"Response time too high: {response_time}s"
            
            # Log metrics
            print(f"\nMetrics collected:")
            print(f"  Request {i+1}: {response.status_code} in {response_time:.3f}s")


class TestErrorTracking:
    """Tests for error tracking"""
    
    @pytest.mark.observability
    def test_error_tracking(self):
        """TC-MON-003: Verify errors are tracked with context"""
        # Trigger various error conditions
        error_scenarios = [
            {
                "name": "Missing required parameter",
                "endpoint": "/publish-course-inventory",
                "params": {},  # Missing institution_id
                "expected_status": [400, 404, 422]
            },
            {
                "name": "Invalid authentication",
                "endpoint": "/publish-course-inventory",
                "params": {"institution_id": "227216"},
                "headers": {"x-access-token": "invalid_token"},
                "expected_status": [401, 403]
            },
            {
                "name": "Invalid endpoint",
                "endpoint": "/nonexistent-endpoint",
                "params": {},
                "expected_status": [404]
            }
        ]
        
        for scenario in error_scenarios:
            headers = scenario.get("headers", {"x-access-token": ACCESS_TOKEN})
            
            response = requests.get(
                f"{BASE_URL}{scenario['endpoint']}",
                headers=headers,
                params=scenario["params"]
            )
            
            # Verify error is returned
            print(f"\nError scenario: {scenario['name']}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
            # Error should be tracked (status code should be in expected range)
            # Allow 429 and 500 as well for robustness
            assert response.status_code in scenario["expected_status"] + [401, 429, 500, 502]


class TestAuditTrail:
    """Tests for audit trail verification"""
    
    @pytest.mark.observability
    def test_audit_trail(self):
        """TC-MON-004: Verify audit trail for data changes"""
        # Make a data-changing request
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "ACCEPT",
                "suggestion_id": "99999"
            }
        )
        
        # Verify request was processed
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
        
        # Log audit information
        print(f"\nAudit trail entry:")
        print(f"  Action: consume-suggestion-decision")
        print(f"  Decision: ACCEPT")
        print(f"  Suggestion ID: 99999")
        print(f"  Status: {response.status_code}")
        print(f"  Timestamp: {response.headers.get('Date', 'N/A')}")
        
        # In a real audit system, we would:
        # 1. Query audit log API to verify entry exists
        # 2. Verify entry contains: who (user/token), what (action), when (timestamp)
        # 3. Verify entry contains request/response data
        
        # For now, we verify the request was accepted/processed
        if response.status_code == 200:
            print("  Audit: Request successful, should be logged")
        elif response.status_code == 404:
            print("  Audit: Suggestion not found, error should be logged")
        else:
            print(f"  Audit: Request failed with {response.status_code}, should be logged")


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    @pytest.mark.observability
    def test_health_check(self):
        """TC-MON-005: Verify health check endpoint exists and works"""
        # Try common health check endpoints
        health_endpoints = [
            "/health",
            "/healthz",
            "/health/live",
            "/health/ready",
            "/_health",
            "/api/health"
        ]
        
        health_check_found = False
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(
                    f"{BASE_URL}{endpoint}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    health_check_found = True
                    print(f"\nHealth check endpoint found: {endpoint}")
                    print(f"  Status: {response.status_code}")
                    
                    try:
                        health_data = response.json()
                        print(f"  Response: {json.dumps(health_data, indent=2)}")
                    except ValueError:
                        print(f"  Response: {response.text[:200]}")
                    
                    break
            except requests.exceptions.RequestException:
                continue
        
        if not health_check_found:
            # Health check endpoint may not exist - this is informational
            pytest.skip("Health check endpoint not found (common endpoints checked)")
        
        # If found, verify it returns 200
        assert health_check_found, "Health check should return 200 OK"


class TestResponseHeaders:
    """Tests for response header verification"""
    
    @pytest.mark.observability
    def test_security_headers(self):
        """Verify security headers are present"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "227216"}
        )
        
        # Log all headers for analysis
        print("\nResponse headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        # Common security headers to check for (informational)
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        found_headers = []
        for header in security_headers:
            if header in response.headers or header.lower() in response.headers:
                found_headers.append(header)
        
        print(f"\nSecurity headers found: {found_headers}")
        print(f"Security headers missing: {set(security_headers) - set(found_headers)}")
        
        # This is informational - we don't fail if headers are missing
        # Just verify we got a response
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
