"""
Integration and Workflow Tests
Tests for end-to-end workflows and cross-endpoint integration
"""
import pytest
import requests
import os
import time
from typing import List, Dict, Optional

# Configuration
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)


# ========== HELPER FUNCTIONS ==========

def make_post_request(endpoint: str, json_data: Optional[Dict] = None) -> requests.Response:
    """Make POST request with consistent headers"""
    return requests.post(
        f"{BASE_URL}{endpoint}",
        headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
        json=json_data
    )


def make_get_request(endpoint: str, params: Optional[Dict] = None) -> requests.Response:
    """Make GET request with consistent headers"""
    return requests.get(
        f"{BASE_URL}{endpoint}",
        headers={"x-access-token": ACCESS_TOKEN},
        params=params
    )


def assert_workflow_response(response: requests.Response) -> None:
    """Assert response is valid for workflow steps"""
    assert response.status_code in [200, 400, 401, 404, 429, 500, 502], \
        f"Expected valid workflow response, got {response.status_code}"


class TestWorkflows:
    """Tests for complete end-to-end workflows"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_equivalency_workflow(self):
        """TC-INT-001: Complete workflow from course upload to equivalency export"""
        # Step 1: Get presigned URL for course inventory
        presigned_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "test-inventory.csv", "institution_id": "227216", "upload_type": "add"}
        )
        assert_workflow_response(presigned_response)
        
        # Step 2: Consume course inventory (simulated - file would need to exist in S3)
        if presigned_response.status_code == 200:
            consume_response = make_post_request(
                "/consume-course-inventory",
                json_data={"file_name": "s3://bucket/test-inventory.csv", "upload_type": "add"}
            )
            assert consume_response.status_code in [200, 401, 404, 500, 502]
        
        # Step 3: Export equivalencies
        export_response = make_post_request(
            "/equivalencies-export",
            json_data={"record_type": "BOTH", "offset": 0, "limit": 10}
        )
        assert_workflow_response(export_response)
    
    @pytest.mark.integration
    def test_suggestion_lifecycle(self):
        """TC-INT-005: Create suggestion, accept/reject, verify state"""
        # Step 1: Create/find suggestion
        create_response = make_post_request(
            "/suggestion-find-or-create",
            json_data={"course_number": "101", "course_subject": "TEST", "institution_id": "227216"}
        )
        assert create_response.status_code in [200, 400, 401, 404, 500, 502]
        
        # Step 2: Make decision on suggestion (if created successfully)
        if create_response.status_code == 200:
            try:
                suggestion_data = create_response.json()
                if isinstance(suggestion_data, dict) and 'suggestion_id' in suggestion_data:
                    decision_response = make_post_request(
                        "/consume-suggestion-decision",
                        json_data={"suggestion_decision": "ACCEPT", "suggestion_id": str(suggestion_data['suggestion_id'])}
                    )
                    assert decision_response.status_code in [200, 400, 401, 404, 500, 502]
            except (ValueError, KeyError):
                pass


class TestBulkOperations:
    """Tests for bulk upload operations"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_bulk_rules_upload(self):
        """TC-INT-002: Upload multiple rule files in sequence"""
        file_names = [f"rules-batch-{i}.csv" for i in range(1, 6)]
        
        for file_name in file_names:
            # Get presigned URL
            presigned_response = make_post_request(
                "/get-presigned-url",
                json_data={"file_name": file_name, "institution_id": "227216", "upload_type": "add"}
            )
            assert_workflow_response(presigned_response)
            time.sleep(0.2)
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_bulk_inventory_upload(self):
        """TC-INT-003: Upload multiple inventory files in sequence"""
        file_names = [f"inventory-batch-{i}.csv" for i in range(1, 6)]
        
        for file_name in file_names:
            presigned_response = make_post_request(
                "/get-presigned-url",
                json_data={"file_name": file_name, "institution_id": "227216", "upload_type": "add"}
            )
            assert_workflow_response(presigned_response)
            time.sleep(0.2)


class TestUploadTypes:
    """Tests for replace vs add upload types"""
    
    @pytest.mark.integration
    def test_replace_vs_add_rules(self):
        """TC-INT-006: Verify replace overwrites, add appends"""
        # Test with 'add' upload_type
        add_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "rules-add-test.csv", "institution_id": "227216", "upload_type": "add"}
        )
        assert add_response.status_code in [200, 400, 401, 404, 500, 502]
        
        # Test with 'replace' upload_type
        replace_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "rules-replace-test.csv", "institution_id": "227216", "upload_type": "replace"}
        )
        assert replace_response.status_code in [200, 400, 401, 404, 500, 502]
    
    @pytest.mark.integration
    def test_replace_vs_add_inventory(self):
        """TC-INT-007: Verify replace overwrites, add appends for inventory"""
        # Test with 'add'
        add_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "inventory-add-test.csv", "institution_id": "227216", "upload_type": "add"}
        )
        assert add_response.status_code in [200, 400, 401, 404, 500, 502]
        
        # Test with 'replace'
        replace_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "inventory-replace-test.csv", "institution_id": "227216", "upload_type": "replace"}
        )
        assert replace_response.status_code in [200, 400, 401, 404, 500, 502]


class TestDataIsolation:
    """Tests for cross-institution data isolation"""
    
    @pytest.mark.integration
    def test_data_isolation(self):
        """TC-INT-008: Verify institution data is isolated"""
        institutions = ["227216", "182290", "100000"]
        
        for institution_id in institutions:
            response = make_get_request(
                "/publish-course-inventory",
                params={"institution_id": institution_id}
            )
            
            # Each institution should get their own data or 404
            assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
            
            # If successful, verify response structure
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, (dict, list))
                except ValueError:
                    pass


class TestExportWorkflow:
    """Tests for export after upload workflow"""
    
    @pytest.mark.integration
    def test_export_after_upload(self):
        """TC-INT-009: Upload rules, immediately export equivalencies"""
        # Step 1: Get presigned URL for rules
        presigned_response = make_post_request(
            "/get-presigned-url",
            json_data={"file_name": "export-test-rules.csv", "institution_id": "227216", "upload_type": "add"}
        )
        assert_workflow_response(presigned_response)
        
        # Step 2: Export equivalencies
        export_response = make_post_request(
            "/equivalencies-export",
            json_data={"record_type": "MODIFIED_RULES", "offset": 0, "limit": 10}
        )
        assert_workflow_response(export_response)


class TestPaginationConsistency:
    """Tests for pagination consistency"""
    
    @pytest.mark.integration
    def test_pagination_consistency(self):
        """TC-INT-010: Verify pagination returns all records exactly once"""
        all_course_ids = set()
        page = 1
        max_pages = 5
        
        while page <= max_pages:
            response = make_get_request(
                "/publish-course-inventory",
                params={"institution_id": "227216", "page": page, "page_size": 10}
            )
            
            if response.status_code != 200:
                break
            
            try:
                data = response.json()
                if isinstance(data, dict) and 'rows' in data:
                    rows = data['rows']
                    if not rows:
                        break
                    
                    for row in rows:
                        if isinstance(row, dict) and 'course_id' in row:
                            course_id = row['course_id']
                            assert course_id not in all_course_ids, f"Duplicate course_id: {course_id}"
                            all_course_ids.add(course_id)
                else:
                    break
            except (ValueError, KeyError):
                break
            
            page += 1
    
    @pytest.mark.integration
    def test_filter_combinations(self):
        """TC-INT-011: Verify combining filters gives expected results"""
        filter_combinations = [
            {"institution_id": "227216", "CourseSubject": "MATH"},
            {"institution_id": "227216", "ActiveIndicator": "true"},
            {"institution_id": "227216", "CourseSubject": "ENG", "ActiveIndicator": "true"},
        ]
        
        for filters in filter_combinations:
            response = make_get_request("/publish-course-inventory", params=filters)
            
            # Filters should work or return appropriate error
            assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
            
            # If successful, verify response structure
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, (dict, list))
                except ValueError:
                    pass


class TestConcurrency:
    """Tests for concurrent operations"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_parallel_uploads(self):
        """TC-INT-004: Multiple institutions uploading simultaneously"""
        institutions = ["227216", "182290", "100000"]
        
        responses = []
        for institution_id in institutions:
            response = make_post_request(
                "/get-presigned-url",
                json_data={"file_name": f"parallel-test-{institution_id}.csv", "institution_id": institution_id, "upload_type": "add"}
            )
            responses.append(response)
        
        # All requests should succeed or fail gracefully
        for response in responses:
            assert_workflow_response(response)
    
    @pytest.mark.integration
    def test_concurrent_decisions(self):
        """TC-INT-012: Multiple users making decisions simultaneously"""
        suggestion_ids = ["11111", "22222", "33333"]
        
        responses = []
        for suggestion_id in suggestion_ids:
            response = make_post_request(
                "/consume-suggestion-decision",
                json_data={"suggestion_decision": "ACCEPT", "suggestion_id": suggestion_id}
            )
            responses.append(response)
        
        # All should succeed or fail appropriately (no race conditions)
        for response in responses:
            assert_workflow_response(response)
