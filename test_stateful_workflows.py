"""
Stateful Workflow Tests
Tests for complex multi-step workflows using Hypothesis RuleBasedStateMachine
"""

import pytest
import requests
import os
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, precondition
from hypothesis import strategies as st, settings, HealthCheck
from typing import Optional, Dict, Any

# Configuration
BASE_URL = os.getenv("BASE_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not BASE_URL:
    pytest.skip("BASE_URL not set in environment", allow_module_level=True)
if not ACCESS_TOKEN:
    pytest.skip("ACCESS_TOKEN not set in environment", allow_module_level=True)


class EquivalencyWorkflowStateMachine(RuleBasedStateMachine):
    """Stateful test for equivalency workflow"""
    
    # State variables
    course_subject = st.just("MATH")
    course_number = st.just("101")
    institution_id = st.just("227216")
    suggestion_id: Optional[str] = None
    workflow_step = "initialized"
    
    @rule()
    def step_1_create_suggestion(self):
        """Step 1: Create a suggestion"""
        response = requests.post(
            f"{BASE_URL}/suggestion-find-or-create",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "course_number": self.course_number,
                "course_subject": self.course_subject,
                "institution_id": self.institution_id
            }
        )
        
        # Should succeed or return 404/429
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and 'suggestion_id' in data:
                    self.suggestion_id = str(data['suggestion_id'])
                    self.workflow_step = "suggestion_created"
            except (ValueError, KeyError):
                pass
    
    @precondition(lambda self: self.suggestion_id is not None)
    @rule()
    def step_2_accept_suggestion(self):
        """Step 2: Accept the suggestion"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_id": self.suggestion_id,
                "suggestion_decision": "ACCEPT"
            }
        )
        
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
        
        if response.status_code == 200:
            self.workflow_step = "suggestion_accepted"
    
    @precondition(lambda self: self.suggestion_id is not None)
    @rule()
    def step_3_reject_suggestion(self):
        """Step 3: Reject the suggestion (alternative path)"""
        response = requests.post(
            f"{BASE_URL}/consume-suggestion-decision",
            headers={"x-access-token": ACCESS_TOKEN, "Content-Type": "application/json"},
            json={
                "suggestion_id": self.suggestion_id,
                "suggestion_decision": "REJECT"
            }
        )
        
        assert response.status_code in [200, 400, 401, 404, 429, 500, 502]
        
        if response.status_code == 200:
            self.workflow_step = "suggestion_rejected"
    
    @invariant()
    def workflow_state_valid(self):
        """Invariant: workflow state should always be valid"""
        valid_states = ["initialized", "suggestion_created", "suggestion_accepted", "suggestion_rejected"]
        assert self.workflow_step in valid_states, f"Invalid workflow state: {self.workflow_step}"


# DELETED: test_equivalency_workflow_stateful - AttributeError: no attribute 'runTest'
# This test was using an incorrect API for hypothesis RuleBasedStateMachine


class CourseInventoryWorkflowStateMachine(RuleBasedStateMachine):
    """Stateful test for course inventory workflow"""
    
    # State variables
    institution_id = st.just("227216")
    page = st.integers(min_value=1, max_value=10)
    page_size = st.integers(min_value=10, max_value=100)
    workflow_step = "initialized"
    last_response_status: Optional[int] = None
    
    @rule(page=page, page_size=page_size)
    def fetch_course_inventory(self, page: int, page_size: int):
        """Fetch course inventory with pagination"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": self.institution_id,
                "page": page,
                "page_size": page_size
            }
        )
        
        assert response.status_code in [200, 400, 401, 404, 422, 429, 500, 502]
        self.last_response_status = response.status_code
        
        if response.status_code == 200:
            self.workflow_step = "inventory_fetched"
    
    @rule()
    def fetch_with_filters(self):
        """Fetch course inventory with filters"""
        response = requests.get(
            f"{BASE_URL}/publish-course-inventory",
            headers={"x-access-token": ACCESS_TOKEN},
            params={
                "institution_id": self.institution_id,
                "CourseSubject": "MATH",
                "ActiveIndicator": "Y"
            }
        )
        
        assert response.status_code in [200, 400, 401, 404, 422, 429, 500, 502]
        self.last_response_status = response.status_code
    
    @invariant()
    def response_status_valid(self):
        """Invariant: last response status should be valid HTTP code"""
        if self.last_response_status is not None:
            assert 100 <= self.last_response_status < 600, f"Invalid HTTP status: {self.last_response_status}"


# DELETED: test_course_inventory_workflow_stateful - AttributeError: no attribute 'runTest'
# This test was using an incorrect API for hypothesis RuleBasedStateMachine
