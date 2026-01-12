import json

with open('reports/report.json', 'r') as f:
    data = json.load(f)

failed_tests = []
for test in data.get('tests', []):
    if test.get('outcome') == 'failed':
        failed_tests.append({
            'nodeid': test['nodeid'],
            'lineno': test.get('lineno'),
            'call': test.get('call', {}),
        })

print(f"Total failed tests: {len(failed_tests)}\n")
print("="*80)
for i, test in enumerate(failed_tests, 1):
    print(f"\n{i}. {test['nodeid']}")
    print(f"   Line: {test['lineno']}")
    if 'longrepr' in test['call']:
        print(f"   Error: {test['call']['longrepr'][:200]}...")
