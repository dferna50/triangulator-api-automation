"""
Token Management Utility for CI/CD Pipeline
Handles token validation and provides helper functions for token management
"""

import os
import sys
import requests
from datetime import datetime
from typing import Optional, Tuple


class TokenManager:
    """Manages API access tokens with validation and expiration checking"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        
    def validate_token(self, institution_id: str = "182290", coding_scheme: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validates the access token by making a test API call
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            params = {"institution_id": institution_id, "page": 1, "page_size": 1}
            if coding_scheme:
                params["coding_scheme"] = coding_scheme
                
            # Test with a lightweight endpoint
            response = requests.get(
                f"{self.base_url}/publish-course-inventory",
                headers={"x-access-token": self.token},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Token is valid and active"
            elif response.status_code == 401:
                return False, "Token is expired or invalid (401 Unauthorized)"
            elif response.status_code == 403:
                return False, "Token does not have required permissions (403 Forbidden)"
            else:
                return False, f"Token validation returned unexpected status: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Token validation timed out - check network connectivity"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to API - check BASE_URL and network"
        except Exception as e:
            return False, f"Token validation failed with error: {str(e)}"
    
    @staticmethod
    def load_from_env() -> Optional['TokenManager']:
        """
        Load token manager from environment variables
        
        Returns:
            TokenManager or None if required vars are missing
        """
        base_url = os.getenv("BASE_URL")
        token = os.getenv("ACCESS_TOKEN")
        
        if not base_url or not token:
            return None
            
        return TokenManager(base_url, token)


def check_token_validity() -> int:
    """
    CLI command to check token validity
    Returns 0 if valid, 1 if invalid
    """
    print("=" * 70)
    print("Token Validation Check")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load configuration
    base_url = os.getenv("BASE_URL")
    tokens_to_validate = []
    
    if os.getenv("ACCESS_TOKEN"):
        tokens_to_validate.append((os.getenv("ACCESS_TOKEN"), "ACCESS_TOKEN", None, None))
    if os.getenv("ORG_ACCESS_TOKEN"):
        tokens_to_validate.append((os.getenv("ORG_ACCESS_TOKEN"), "ORG_ACCESS_TOKEN", "182290", "IPEDS"))
    
    if not base_url:
        print("❌ ERROR: BASE_URL environment variable is not set")
        print("   Set it using: $env:BASE_URL = 'https://your-api-url.com'")
        return 1
        
    if not tokens_to_validate:
        print("❌ ERROR: ACCESS_TOKEN and ORG_ACCESS_TOKEN environment variables are not set")
        print("   Set at least one using: $env:ACCESS_TOKEN = 'your-token-here'")
        return 1
    
    print(f"✓ BASE_URL: {base_url}")
    for token, name, _, _ in tokens_to_validate:
        print(f"✓ {name}: {'*' * 20}{token[-8:] if len(token) > 8 else '***'}")
    print()
    
    all_valid = True
    
    for token, name, inst_id, coding_scheme in tokens_to_validate:
        print(f"Validating {name}...")
        manager = TokenManager(base_url, token)
        is_valid, message = manager.validate_token(institution_id=inst_id if inst_id else "182290", coding_scheme=coding_scheme)
        
        if is_valid:
            print(f"✅ SUCCESS: {message}")
        else:
            print(f"❌ FAILURE: {message}")
            all_valid = False
            
    print()
    if all_valid:
        print("Your tokens are working correctly and tests can run!")
        return 0
    else:
        print("Action Required:")
        print("1. Generate a new access token from your API provider")
        print("2. Update the environment variables")
        return 1


if __name__ == "__main__":
    sys.exit(check_token_validity())
