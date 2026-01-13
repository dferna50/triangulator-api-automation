import re
import html

# Read the HTML file
with open('logs/pytest-report.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the data-jsonblob attribute
match = re.search(r'data-jsonblob="([^"]+)"', content)
if not match:
    print("No jsonblob found")
    exit(1)

# Unescape HTML entities
blob = html.unescape(match.group(1))

# Find all Failed tests in the blob
import json
try:
    data = json.loads(blob)
    failed_tests = []
    
    for test_id, test_data in data.get('tests', {}).items():
        if test_data and test_data[0].get('result') == 'Failed':
            failed_tests.append(test_id)
    
    print(f"Found {len(failed_tests)} failed tests:")
    for test in failed_tests:
        print(f"  - {test}")
        
except Exception as e:
    print(f"Error parsing JSON: {e}")
