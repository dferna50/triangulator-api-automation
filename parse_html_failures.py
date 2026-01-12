import json
import html
from html.parser import HTMLParser

class DataExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data_blob = None
    
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attrs_dict = dict(attrs)
            if attrs_dict.get('id') == 'data-container':
                self.data_blob = attrs_dict.get('data-jsonblob')

with open('reports/pytest-report.html', 'r', encoding='utf-8') as f:
    content = f.read()

parser = DataExtractor()
parser.feed(content)

if parser.data_blob:
    # Unescape HTML entities
    json_str = html.unescape(parser.data_blob)
    data = json.loads(json_str)
    
    failed_tests = []
    for test_id, test_runs in data['tests'].items():
        for test_run in test_runs:
            if test_run['result'].lower() == 'failed':
                failed_tests.append({
                    'testId': test_id,
                    'result': test_run['result'],
                    'duration': test_run['duration'],
                    'log': test_run.get('log', 'No log available')[:500]
                })
    
    print(f"Total failed tests: {len(failed_tests)}\n")
    print("="*100)
    for i, test in enumerate(failed_tests, 1):
        print(f"\n{i}. Test: {test['testId']}")
        print(f"   Duration: {test['duration']}")
        print(f"   Error preview:\n{test['log']}\n")
        print("-"*100)
