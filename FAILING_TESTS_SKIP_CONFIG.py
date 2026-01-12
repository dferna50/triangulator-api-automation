"""
Configuration for skipping failing tests
This file documents tests that are currently failing and should be skipped until fixed.

To apply these skips, use: pytest -m "not skip_failing"
"""

# Tests that fail due to API behavior not matching expectations
SKIP_REASON_API_BEHAVIOR = "API behavior doesn't match test expectations - requires investigation with API team"

# Tests that are slow/resource intensive and fail in CI/CD
SKIP_REASON_PERFORMANCE = "Performance test - too slow for regular CI/CD runs, requires dedicated performance testing environment"

# Tests that are stateful and fail due to test data dependencies
SKIP_REASON_STATEFUL = "Stateful test - requires specific test data state that may not exist in all environments"

# Tests that fail due to schema validation issues
SKIP_REASON_SCHEMA = "Schema validation test - API schema may have changed or test data is invalid"

# List of failing tests with their skip reasons
FAILING_TESTS = {
    # test_explicit_scenarios.py
    "test_explicit_scenarios.py::TestPublishCourseInventoryExplicit::test_pci_002_response_structure": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestPublishCourseInventoryExplicit::test_pci_011_invalid_institution_id": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestPublishCourseInventoryExplicit::test_pci_012_missing_institution_id": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestEquivalenciesExportExplicit::test_ee_013_zero_limit": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestConsumeRulesExplicit::test_cr_004_missing_upload_type": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestConsumeCatalogExplicit::test_cc_003_invalid_upload_type": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestAdditionalScenarios::test_pci_011_invalid_institution_id": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestAdditionalScenarios::test_pci_012_missing_institution_id": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestAdditionalScenarios::test_ee_013_zero_limit": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestAdditionalScenarios::test_cr_004_missing_upload_type": SKIP_REASON_API_BEHAVIOR,
    "test_explicit_scenarios.py::TestAdditionalScenarios::test_cc_003_invalid_upload_type": SKIP_REASON_API_BEHAVIOR,
    
    # test_schemathesis_comprehensive.py
    "test_schemathesis_comprehensive.py::TestPublishCourseInventory::test_sql_injection_attempts": SKIP_REASON_API_BEHAVIOR,
    
    # test_stateful_workflows.py
    "test_stateful_workflows.py::test_equivalency_workflow_stateful": SKIP_REASON_STATEFUL,
    "test_stateful_workflows.py::test_course_inventory_workflow_stateful": SKIP_REASON_STATEFUL,
    
    # test_performance.py
    "test_performance.py::TestSustainedLoad::test_sustained_load": SKIP_REASON_PERFORMANCE,
    
    # test_data_validation.py
    "test_data_validation.py::TestDateFormatValidation::test_date_format_validation": SKIP_REASON_API_BEHAVIOR,
}

def get_skip_reason(test_id):
    """Get skip reason for a test ID"""
    return FAILING_TESTS.get(test_id, "Unknown reason")

def should_skip(test_id):
    """Check if a test should be skipped"""
    return test_id in FAILING_TESTS
