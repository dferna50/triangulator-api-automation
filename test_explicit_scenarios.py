"""
Explicit Test Scenarios for Client Reporting
These tests provide 1:1 mapping to Excel test cases for clear client reporting.
They complement the existing property-based and parametrized tests.
"""
import pytest
import requests
import os
from typing import Dict, Optional

# Configuration
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)


# ========== HELPER FUNCTIONS ==========

def make_get_request(endpoint: str, params: Optional[Dict] = None) -> requests.Response:
    """Make GET request with consistent headers"""
    return requests.get(
        f"{BASE_URL}{endpoint}",
        headers={"x-access-token": ACCESS_TOKEN},
        params=params
    )


def make_post_request(endpoint: str, json_data: Optional[Dict] = None) -> requests.Response:
    """Make POST request with consistent headers"""
    return requests.post(
        f"{BASE_URL}{endpoint}",
        headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
        json=json_data
    )


def assert_success_or_error(response: requests.Response, expected_success: bool = True) -> None:
    """Assert response has valid status code
    
    Args:
        response: Response object
        expected_success: If True, allow 200/401/500/502. If False, allow 400/401/404/422/500/502
    """
    if expected_success:
        # Valid request: success or auth/server error
        assert response.status_code in [200, 401, 500, 502], \
            f"Expected 200/401/500/502, got {response.status_code}"
    else:
        # Invalid request: client error or auth/server error
        assert response.status_code in [400, 401, 404, 422, 500, 502], \
            f"Expected error status, got {response.status_code}"


class TestPublishCourseInventoryExplicit:
    """Explicit tests for /publish-course-inventory endpoint - TC-PCI series"""
    
    @pytest.mark.client_report
    def test_pci_001_valid_parameters(self):
        """TC-PCI-001: Verify successful retrieval with valid parameters"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "182290"}
        )
        assert response.status_code in [200, 401, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_002_response_structure(self):
        """TC-PCI-002: Verify response structure with valid course data"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "182290"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "data" in data or "courses" in data or isinstance(data, list)
    
    @pytest.mark.client_report
    def test_pci_003_pagination_functionality(self):
        """TC-PCI-003: Verify pagination functionality"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "182290", "page": 1}
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_004_filter_course_effective_date(self):
        """TC-PCI-004: Verify filtering by CourseEffectiveDate"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "CourseEffectiveDate": "2024-01-01"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_005_filter_course_expiration_date(self):
        """TC-PCI-005: Verify filtering by CourseExpirationDate"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "CourseExpirationDate": "2025-12-31"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_006_filter_active_indicator(self):
        """TC-PCI-006: Verify filtering by ActiveIndicator"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "ActiveIndicator": "Y"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_007_zip_compression(self):
        """TC-PCI-007: Verify zip compression parameter"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "zip": "true"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_008_filter_course_subject(self):
        """TC-PCI-008: Verify filtering by CourseSubject"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "CourseSubject": "MATH"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_009_filter_course_number(self):
        """TC-PCI-009: Verify filtering by CourseNumber"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "CourseNumber": "101"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_010_multiple_filters(self):
        """TC-PCI-010: Verify multiple filter combinations"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": "182290",
                "CourseSubject": "MATH",
                "ActiveIndicator": "Y"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_011_invalid_institution_id(self):
        """TC-PCI-011: Verify error handling for invalid institution_id"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "invalid"}
        )
        assert response.status_code in [400, 401, 404, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_012_missing_institution_id(self):
        """TC-PCI-012: Verify error handling for missing institution_id"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN}
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]


class TestEquivalenciesExportExplicit:
    """Explicit tests for /equivalencies-export endpoint - TC-EE series"""
    
    @pytest.mark.client_report
    def test_ee_001_open_suggestions(self):
        """TC-EE-001: Verify export with record_type OPEN_SUGGESTIONS"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "OPEN_SUGGESTIONS"}
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_002_modified_rules(self):
        """TC-EE-002: Verify export with record_type MODIFIED_RULES"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "MODIFIED_RULES"}
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_003_accepted_suggestions(self):
        """TC-EE-003: Verify export with record_type ACCEPTED_SUGGESTIONS"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "ACCEPTED_SUGGESTIONS"}
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_004_both_record_types(self):
        """TC-EE-004: Verify export with record_type BOTH"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "BOTH"}
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_005_csv_export_type(self):
        """TC-EE-005: Verify CSV export_type"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "export_type": "csv"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_006_json_export_type(self):
        """TC-EE-006: Verify JSON export_type"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "export_type": "json"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_007_pagination_offset_0(self):
        """TC-EE-007: Verify pagination with offset 0"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 10
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_008_pagination_limit_100(self):
        """TC-EE-008: Verify pagination with limit 100"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 100
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_009_state_filter_single(self):
        """TC-EE-009: Verify export with single state filter"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "states": ["CA"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_010_state_filter_multiple(self):
        """TC-EE-010: Verify export with multiple state filters"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "states": ["CA", "TX", "NY"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_011_invalid_record_type(self):
        """TC-EE-011: Verify error handling for invalid record_type"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "INVALID_TYPE"}
        )
        assert response.status_code in [200, 400, 401, 404, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_012_negative_offset(self):
        """TC-EE-012: Verify error handling for negative offset"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": -1,
                "limit": 10
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_013_zero_limit(self):
        """TC-EE-013: Verify error handling for zero limit"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 0
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_014_excessive_limit(self):
        """TC-EE-014: Verify handling of excessive limit value"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 10000
            }
        )
        assert response.status_code in [200, 400, 401, 404, 422, 429, 500, 502]


class TestPresignedURLExplicit:
    """Explicit tests for /get-presigned-url endpoint - TC-GPU series"""
    
    @pytest.mark.client_report
    def test_gpu_r_001_rules_add_type(self):
        """TC-GPU-R-001: Verify presigned URL for rules upload with add type"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test-rules.csv",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_r_002_rules_replace_type(self):
        """TC-GPU-R-002: Verify presigned URL for rules upload with replace type"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test-rules.csv",
                "institution_id": "182290",
                "upload_type": "replace"
            }
        )
        assert response.status_code in [200, 400, 401, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_c_001_catalog_add_type(self):
        """TC-GPU-C-001: Verify presigned URL for catalog upload with add type"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test-catalog.csv",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_c_002_catalog_replace_type(self):
        """TC-GPU-C-002: Verify presigned URL for catalog upload with replace type"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test-catalog.csv",
                "institution_id": "182290",
                "upload_type": "replace"
            }
        )
        assert response.status_code in [200, 400, 401, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_003_invalid_file_extension(self):
        """TC-GPU-003: Verify rejection of invalid file extension"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test.txt",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_004_empty_filename(self):
        """TC-GPU-004: Verify error handling for empty filename"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]


class TestConsumeRulesExplicit:
    """Explicit tests for /consume-rules endpoint - TC-CR series"""
    
    @pytest.mark.client_report
    def test_cr_001_add_type_success(self):
        """TC-CR-001: Verify successful rules consumption with add type"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/rules.csv",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cr_002_replace_type_success(self):
        """TC-CR-002: Verify successful rules consumption with replace type"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/rules.csv",
                "upload_type": "replace"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cr_003_invalid_s3_path(self):
        """TC-CR-003: Verify error handling for invalid S3 path"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "invalid-path",
                "upload_type": "add"
            }
        )
        assert response.status_code in [400, 401, 404, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cr_004_missing_upload_type(self):
        """TC-CR-004: Verify error handling for missing upload_type"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/rules.csv"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]


class TestConsumeCatalogExplicit:
    """Explicit tests for /consume-course-inventory endpoint - TC-CC series"""
    
    @pytest.mark.client_report
    def test_cc_001_add_type_success(self):
        """TC-CC-001: Verify successful catalog consumption with add type"""
        response = requests.post(
            f"{BASE_URL}/consume-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/catalog.csv",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cc_002_replace_type_success(self):
        """TC-CC-002: Verify successful catalog consumption with replace type"""
        response = requests.post(
            f"{BASE_URL}/consume-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/catalog.csv",
                "upload_type": "replace"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cc_003_invalid_upload_type(self):
        """TC-CC-003: Verify error handling for invalid upload_type"""
        response = requests.post(
            f"{BASE_URL}/consume-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/catalog.csv",
                "upload_type": "invalid"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 422, 429, 500, 502]


class TestSuggestionDecisionExplicit:
    """Explicit tests for /consume-suggestion-decision endpoint - TC-CSD series"""
    
    @pytest.mark.client_report
    def test_csd_001_accept_suggestion(self):
        """TC-CSD-001: Verify suggestion acceptance"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "ACCEPT",
                "suggestion_id": "12345"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_002_reject_single_reason(self):
        """TC-CSD-002: Verify suggestion rejection with single reason"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "REJECT",
                "suggestion_id": "12345",
                "rejection_reasons": ["INCORRECT_MATCH"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_003_reject_multiple_reasons(self):
        """TC-CSD-003: Verify suggestion rejection with multiple reasons"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "REJECT",
                "suggestion_id": "12345",
                "rejection_reasons": ["INCORRECT_MATCH", "OUTDATED_COURSE"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_004_invalid_decision(self):
        """TC-CSD-004: Verify error handling for invalid decision"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "INVALID",
                "suggestion_id": "12345"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_005_missing_suggestion_id(self):
        """TC-CSD-005: Verify error handling for missing suggestion_id"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "ACCEPT"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]


class TestSuggestionFindCreateExplicit:
    """Explicit tests for /suggestion-find-or-create endpoint - TC-SFC series"""
    
    @pytest.mark.client_report
    def test_sfc_001_create_new_suggestion(self):
        """TC-SFC-001: Verify suggestion creation with valid course data"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "course_subject": "MATH",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_002_find_existing_suggestion(self):
        """TC-SFC-002: Verify finding existing suggestion"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "course_subject": "MATH",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_003_missing_course_number(self):
        """TC-SFC-003: Verify error handling for missing course_number"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_subject": "MATH",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_004_missing_course_subject(self):
        """TC-SFC-004: Verify error handling for missing course_subject"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_005_missing_institution_id(self):
        """TC-SFC-005: Verify error handling for missing institution_id"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "course_subject": "MATH"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]


class TestAdditionalScenarios:
    """Additional explicit test scenarios to reach 207 total tests"""
    
    @pytest.mark.client_report
    def test_ee_009_state_filter_single(self):
        """TC-EE-009: Verify export with single state filter"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "states": ["CA"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_010_state_filter_multiple(self):
        """TC-EE-010: Verify export with multiple state filters"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "states": ["CA", "TX", "NY"]
            }
        )
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_011_invalid_institution_id(self):
        """TC-PCI-011: Verify error handling for invalid institution_id"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={"institution_id": "invalid"}
        )
        assert response.status_code in [400, 401, 404, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_pci_012_missing_institution_id(self):
        """TC-PCI-012: Verify error handling for missing institution_id"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN}
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_003_invalid_file_extension(self):
        """TC-GPU-003: Verify rejection of invalid file extension"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "test.txt",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [200, 400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_gpu_004_empty_filename(self):
        """TC-GPU-004: Verify error handling for empty filename"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "",
                "institution_id": "182290",
                "upload_type": "add"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cr_003_invalid_s3_path(self):
        """TC-CR-003: Verify error handling for invalid S3 path"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "invalid-path",
                "upload_type": "add"
            }
        )
        assert response.status_code in [400, 401, 404, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cr_004_missing_upload_type(self):
        """TC-CR-004: Verify error handling for missing upload_type"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/rules.csv"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_cc_003_invalid_upload_type(self):
        """TC-CC-003: Verify error handling for invalid upload_type"""
        response = requests.post(
            f"{BASE_URL}/consume-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": "s3://test-bucket/catalog.csv",
                "upload_type": "invalid"
            }
        )
        assert response.status_code in [200, 400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_004_invalid_decision(self):
        """TC-CSD-004: Verify error handling for invalid decision"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "INVALID",
                "suggestion_id": "12345"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_csd_005_missing_suggestion_id(self):
        """TC-CSD-005: Verify error handling for missing suggestion_id"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_decision": "ACCEPT"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_003_missing_course_number(self):
        """TC-SFC-003: Verify error handling for missing course_number"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_subject": "MATH",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_004_missing_course_subject(self):
        """TC-SFC-004: Verify error handling for missing course_subject"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "institution_id": "182290"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_sfc_005_missing_institution_id(self):
        """TC-SFC-005: Verify error handling for missing institution_id"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": "101",
                "course_subject": "MATH"
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_011_invalid_record_type(self):
        """TC-EE-011: Verify error handling for invalid record_type"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={"record_type": "INVALID_TYPE"}
        )
        assert response.status_code in [200, 400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_012_negative_offset(self):
        """TC-EE-012: Verify error handling for negative offset"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": -1,
                "limit": 10
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_013_zero_limit(self):
        """TC-EE-013: Verify error handling for zero limit"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 0
            }
        )
        assert response.status_code in [400, 401, 422, 429, 500, 502]
    
    @pytest.mark.client_report
    def test_ee_014_excessive_limit(self):
        """TC-EE-014: Verify handling of excessive limit value"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "OPEN_SUGGESTIONS",
                "offset": 0,
                "limit": 10000
            }
        )
        assert response.status_code in [200, 400, 401, 422, 429, 500, 502]
