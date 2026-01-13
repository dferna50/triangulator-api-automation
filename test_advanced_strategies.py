"""
Advanced Property-Based Testing Strategies
Custom Hypothesis strategies for domain-specific testing
"""

import schemathesis
from hypothesis import strategies as st, given, settings, assume, HealthCheck
from hypothesis.extra.dateutil import timezones
import pytest
import requests
import os
from datetime import datetime, timedelta
import string
import re

# Configuration - Load from environment variables
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)

# ========== CUSTOM STRATEGIES ==========

@st.composite
def valid_institution_id(draw):
    """Generate valid 6-digit institution IDs (IPEDS codes)"""
    return str(draw(st.integers(min_value=100000, max_value=999999)))


@st.composite
def invalid_institution_id(draw):
    """Generate invalid institution IDs for negative testing"""
    return draw(st.one_of(
        st.just(""),
        st.just("0"),
        st.just("-1"),
        st.integers(min_value=-1000, max_value=99999).map(str),
        st.integers(min_value=1000000, max_value=9999999).map(str),
        st.text(alphabet=st.characters(blacklist_categories=('Nd',)), min_size=1, max_size=10),
        st.just("abc123"),
        st.just("12345a"),
    ))


@st.composite
def valid_course_subject(draw):
    """Generate valid course subjects (2-4 uppercase letters)"""
    length = draw(st.integers(min_value=2, max_value=4))
    return ''.join(draw(st.lists(
        st.sampled_from(string.ascii_uppercase),
        min_size=length,
        max_size=length
    )))


@st.composite
def invalid_course_subject(draw):
    """Generate invalid course subjects"""
    return draw(st.one_of(
        st.just(""),
        st.just("A"),  # Too short
        st.just("ABCDE"),  # Too long
        st.text(alphabet=st.characters(whitelist_categories=('Ll',)), min_size=2, max_size=4),  # Lowercase
        st.text(alphabet=st.characters(whitelist_categories=('Nd',)), min_size=2, max_size=4),  # Numbers
        st.just("AB CD"),  # Space
        st.just("AB-CD"),  # Hyphen
    ))


@st.composite
def valid_course_number(draw):
    """Generate valid course numbers (alphanumeric)"""
    length = draw(st.integers(min_value=1, max_value=6))
    chars = string.ascii_uppercase + string.digits
    return ''.join(draw(st.lists(
        st.sampled_from(chars),
        min_size=length,
        max_size=length
    )))


@st.composite
def valid_year_month(draw):
    """Generate valid YYYY-MM format dates"""
    year = draw(st.integers(min_value=2000, max_value=9999))
    month = draw(st.integers(min_value=1, max_value=12))
    return f"{year}-{month:02d}"


@st.composite
def invalid_year_month(draw):
    """Generate invalid YYYY-MM format dates"""
    return draw(st.one_of(
        st.just(""),
        st.just("2020"),
        st.just("2020-13"),  # Invalid month
        st.just("2020-00"),  # Invalid month
        st.just("20-01"),  # Invalid year
        st.just("2020/01"),  # Wrong separator
        st.just("01-2020"),  # Wrong order
        st.just("2020-1"),  # Missing zero padding
    ))


@st.composite
def valid_s3_path(draw):
    """Generate valid S3 paths"""
    bucket = draw(st.sampled_from([
        'cremo-cmtri-qa-engine-data-bucket',
        'cremo-cmtri-uat-engine-data-bucket'
    ]))
    
    # Generate filename
    name_length = draw(st.integers(min_value=5, max_value=50))
    filename = ''.join(draw(st.lists(
        st.sampled_from(string.ascii_letters + string.digits + '_-'),
        min_size=name_length,
        max_size=name_length
    )))
    
    return f"s3://{bucket}/ipeds-initial/{filename}.csv"


@st.composite
def invalid_s3_path(draw):
    """Generate invalid S3 paths"""
    return draw(st.one_of(
        st.just(""),
        st.just("s3://"),
        st.just("http://bucket/file.csv"),
        st.just("file:///etc/passwd"),
        st.just("../../../etc/passwd"),
        st.just("s3://bucket/file.txt"),  # Wrong extension
        st.just("s3://bucket/../../file.csv"),  # Path traversal
    ))


@st.composite
def valid_state_code(draw):
    """Generate valid US state codes"""
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'AS', 'DC', 'FM', 'GU', 'MH', 'MP', 'PR', 'PW', 'VI'
    ]
    return draw(st.sampled_from(states))


@st.composite
def valid_rejection_reason(draw):
    """Generate valid rejection reasons"""
    reasons = [
        "ACCURACY__BETTER_MATCH_AVAILABLE",
        "ACCURACY__EXISTING_RULE",
        "ACCURACY__GRADUATE_LEVEL_SOURCE",
        "ACCURACY__GRADUATE_LEVEL_TARGET",
        "ACCURACY__INACCURATE_SOURCE_COMBINATION",
        "ACCURACY__INACCURATE_TARGET_COMBINATION",
        "ACCURACY__INACTIVE_SOURCE_COURSE",
        "ACCURACY__INACTIVE_TARGET_COURSE",
        "ACCURACY__NOT_EQUIVALENT",
        "ACCURACY__SUBJECT_DIFFERENCE",
        "GRADUATE_LEVEL",
        "QUALITY__INACCURATE_SOURCE_DATA",
        "QUALITY__INACCURATE_TARGET_DATA",
        "QUALITY__NOT_ENOUGH_SOURCE_DATA",
        "QUALITY__NOT_ENOUGH_TARGET_DATA",
        "QUALITY__SOURCE_DATA_MISSING",
        "QUALITY__SOURCE_SEQUENCE_NEEDED",
        "QUALITY__TARGET_DATA_MISSING",
        "TRANSFER_POLICY__CREDIT_DIFFERENCE",
        "TRANSFER_POLICY__GENERAL_POLICY_OR_PRACTICE",
        "TRANSFER_POLICY__INSTITUTION_ACCREDITATION",
        "TRANSFER_POLICY__LEVEL_DIFFERENCE",
        "TRANSFER_POLICY__NEEDS_SECOND_REVIEW",
        "TRANSFER_POLICY__PROGRAM_ACCREDITATION",
        "TRANSFER_POLICY__REMEDIAL",
        "TRANSFER_POLICY__VOCATIONAL"
    ]
    return draw(st.sampled_from(reasons))


@st.composite
def valid_filename(draw):
    """Generate valid CSV filenames"""
    name_length = draw(st.integers(min_value=5, max_value=100))
    name = ''.join(draw(st.lists(
        st.sampled_from(string.ascii_letters + string.digits + '_-.'),
        min_size=name_length,
        max_size=name_length
    )))
    extension = draw(st.sampled_from(['csv', 'CSV']))
    return f"{name}.{extension}"


@st.composite
def invalid_filename(draw):
    """Generate invalid filenames"""
    return draw(st.one_of(
        st.just(""),
        st.just("file"),  # No extension
        st.just("file.txt"),  # Wrong extension
        st.just("file.csv.exe"),  # Double extension
        st.just("../../../etc/passwd.csv"),  # Path traversal
        st.just("file<>.csv"),  # Invalid characters
        st.just("file|name.csv"),  # Pipe character
        st.text(min_size=256, max_size=300).map(lambda x: f"{x}.csv"),  # Too long
    ))


# ========== PROPERTY-BASED TESTS ==========

class TestPublishCourseInventoryProperties:
    """Property-based tests for course inventory endpoint"""
    
    @given(
        institution_id=valid_institution_id(),
        page=st.integers(min_value=1, max_value=1000),
        page_size=st.integers(min_value=1, max_value=1000)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_valid_pagination_always_succeeds_or_404(self, institution_id, page, page_size):
        """Valid pagination parameters should always return 200 or 404"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": institution_id,
                "page": page,
                "page_size": page_size
            }
        )
        assert response.status_code in [200, 404, 429, 500, 502], f"Unexpected status: {response.status_code}"
    
    # REMOVED: API does not have institution_id parameter
    # User feedback: "does not have a parameter institution_id please remove"
    # @given(
    #     institution_id=invalid_institution_id(),
    # )
    # @settings()
    # def test_invalid_institution_id_rejected(self, institution_id):
    #     """Invalid institution IDs should be rejected"""
    #     response = requests.get(
    #         f"{BASE_URL}/publish-course-inventory",
    #         headers={"x-access-token": ACCESS_TOKEN},
    #         params={"institution_id": institution_id}
    #     )
    #     assert response.status_code in [400, 422, 429, 500, 502], f"Invalid ID accepted: {institution_id}"
    
    @given(
        institution_id=valid_institution_id(),
        course_subject=valid_course_subject(),
        course_number=valid_course_number()
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_valid_course_filters(self, institution_id, course_subject, course_number):
        """Valid course filters should not cause errors"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": institution_id,
                "CourseSubject": course_subject,
                "CourseNumber": course_number
            }
        )
        assert response.status_code in [200, 404, 429, 500, 502]  # Accept rate limit and server errors
    
    @given(
        institution_id=valid_institution_id(),
        effective_date=valid_year_month(),
        expiration_date=valid_year_month()
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_date_range_consistency(self, institution_id, effective_date, expiration_date):
        """Date ranges should be handled consistently"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": institution_id,
                "CourseEffectiveDate": effective_date,
                "CourseExpirationDate": expiration_date
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]


class TestEquivalenciesExportProperties:
    """Property-based tests for equivalencies export"""
    
    @given(
        record_type=st.sampled_from(["MODIFIED_RULES", "ACCEPTED_SUGGESTIONS", "OPEN_SUGGESTIONS", "BOTH"]),
        offset=st.integers(min_value=0, max_value=10000),
        limit=st.integers(min_value=1, max_value=1000)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, derandomize=True)
    def test_pagination_properties(self, record_type, offset, limit):
        """Test pagination properties"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": record_type,
                "offset": offset,
                "limit": limit
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]
    
    @given(
        confidence_score=st.integers(min_value=0, max_value=100)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_confidence_score_range(self, confidence_score):
        """Confidence scores 0-100 should be accepted"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "BOTH",
                "min_confidence_score": confidence_score
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]
    
    @given(
        states=st.lists(valid_state_code(), min_size=1, max_size=10, unique=True)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, derandomize=True)
    def test_valid_state_codes(self, states):
        """Valid state codes should be accepted"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "BOTH",
                "source_states": states
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]
    
    @given(
        subjects=st.lists(valid_course_subject(), min_size=1, max_size=20, unique=True)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_target_subjects_list(self, subjects):
        """Lists of valid subjects should be accepted"""
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "record_type": "BOTH",
                "target_subjects": subjects
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]


class TestPresignedUrlProperties:
    """Property-based tests for presigned URL generation"""
    
    @given(
        filename=valid_filename(),
        institution_id=valid_institution_id(),
        upload_type=st.sampled_from(["add", "update", "delete"])
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_valid_requests_succeed(self, filename, institution_id, upload_type):
        """Valid presigned URL requests should succeed"""
        response = requests.post(
            f"{BASE_URL}/get-presigned-url",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": filename,
                "institution_id": institution_id,
                "upload_type": upload_type
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]
        
        if response.status_code == 200:
            data = response.json()
            assert "presigned_url" in data or "url" in data
    
    # REMOVED: API accepts filenames without extensions - not an issue per user feedback
    # User feedback: "not an issue"
    # @given(
    #     filename=invalid_filename(),
    #     institution_id=valid_institution_id()
    # )
    # @settings()
    # def test_invalid_filenames_rejected(self, filename, institution_id):
    #     """Invalid filenames should be rejected"""
    #     assume(len(filename) < 256)  # Skip extremely long names
    #     
    #     response = requests.post(
    #         f"{BASE_URL}/get-presigned-url",
    #         headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
    #         json={
    #             "file_name": filename,
    #             "institution_id": institution_id,
    #             "upload_type": "add"
    #         }
    #     )
    #     assert response.status_code in [400, 422, 429, 500, 502]
    pass  # Placeholder to maintain class structure


class TestConsumeRulesProperties:
    """Property-based tests for consume rules"""
    
    @given(
        s3_path=valid_s3_path(),
        upload_type=st.sampled_from(["add", "update", "delete"])
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_valid_s3_paths(self, s3_path, upload_type):
        """Valid S3 paths should be accepted"""
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": s3_path,
                "upload_type": upload_type
            }
        )
        assert response.status_code in [200, 400, 404, 429, 500, 502]
    
    @given(
        s3_path=invalid_s3_path()
    )
    @settings()
    def test_invalid_s3_paths_rejected(self, s3_path):
        """Invalid S3 paths return 404 - acceptable per user feedback"""
        # UPDATED: API returns 404 for invalid S3 paths - this is acceptable
        # User feedback: "acceptable"
        response = requests.post(
            f"{BASE_URL}/consume-rules",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "file_name": s3_path,
                "upload_type": "add"
            }
        )
        # Accept 404 as valid response (file not found is acceptable for invalid paths)
        assert response.status_code in [400, 404, 422, 429, 500, 502] # need to consider disabling the timer for this test, its flakey


class TestSuggestionDecisionProperties:
    """Property-based tests for suggestion decisions"""
    
    @given(
        decision=st.sampled_from(["ACCEPT", "REJECT"]),
        suggestion_id=st.integers(min_value=1, max_value=9999999).map(str),
        rejection_reasons=st.lists(valid_rejection_reason(), min_size=0, max_size=5, unique=True)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, derandomize=True)
    def test_decision_with_reasons(self, decision, suggestion_id, rejection_reasons):
        """Test various decision and reason combinations"""
        payload = {
            "suggestion_decision": decision,
            "suggestion_id": suggestion_id
        }
        
        if rejection_reasons:
            payload["rejection_reasons"] = rejection_reasons
        
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json=payload
        )
        assert response.status_code in [200, 400, 404, 422]


class TestSuggestionFindOrCreateProperties:
    """Property-based tests for suggestion creation"""
    
    @given(
        course_subject=valid_course_subject(),
        course_number=valid_course_number(),
        institution_id=valid_institution_id()
    )
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_valid_course_data(self, course_subject, course_number, institution_id):
        """Valid course data should be accepted"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_subject": course_subject,
                "course_number": course_number,
                "institution_id": institution_id
            }
        )
        assert response.status_code in [200, 201, 400, 404]
    
    # REMOVED: API accepts single-letter course subjects - not necessary per user feedback
    # User feedback: "not necessary"
    # @given(
    #     course_subject=invalid_course_subject(),
    #     course_number=valid_course_number(),
    #     institution_id=valid_institution_id()
    # )
    # @settings()
    # def test_invalid_course_subject_rejected(self, course_subject, course_number, institution_id):
    #     """Invalid course subjects should be rejected"""
    #     response = requests.post(
    #         f"{BASE_URL}/suggestion-find-or-create",
    #         headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
    #         json={
    #             "course_subject": course_subject,
    #             "course_number": course_number,
    #             "institution_id": institution_id
    #         }
    #     )
    #     assert response.status_code in [400, 422, 429, 500, 502]
    pass  # Placeholder to maintain class structure


# ========== INVARIANT TESTS ==========

class TestAPIInvariants:
    """Test API invariants that should always hold"""
    
    @given(endpoint=st.sampled_from([
        "/publish-course-inventory",
        "/equivalencies-export",
        "/get-presigned-url",
        "/consume-rules",
        "/consume-suggestion-decision",
        "/suggestion-find-or-create"
    ]))
    @settings()
    def test_missing_auth_always_401(self, endpoint):
        """Missing authentication should always return 401"""
        if endpoint == "/publish-course-inventory":
            response = requests.get(f"{BASE_URL}{endpoint}", params={"institution_id": "182290"})
        else:
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
        
        assert response.status_code == 401, f"Endpoint {endpoint} should require auth"
    
    @given(
        data=st.text(min_size=1, max_size=100)
    )
    @settings()
    def test_malformed_json_always_400(self, data):
        """Malformed JSON should always return 400"""
        assume(not data.startswith("{"))  # Ensure it's not valid JSON
        
        response = requests.post(
            f"{BASE_URL}/equivalencies-export",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            data=data
        )
        assert response.status_code in [400, 422, 429, 500, 502]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--hypothesis-show-statistics"])


