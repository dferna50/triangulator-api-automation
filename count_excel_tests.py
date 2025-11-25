import pandas as pd

df = pd.read_excel('API-Testcases-Complete.xlsx')
print(f'Total test cases: {len(df)}')

# Count by category
new_tests = df[df['Test Case ID'].str.startswith('TC-', na=False)]
original_tests = df[~df['Test Case ID'].str.startswith('TC-', na=False)]

print(f'Original tests: {len(original_tests)}')
print(f'New tests (TC-*): {len(new_tests)}')

# Show breakdown of new tests
print('\nNew test breakdown:')
for prefix in ['TC-PERF', 'TC-DATA', 'TC-ERR', 'TC-INT', 'TC-MON']:
    count = len(df[df['Test Case ID'].str.startswith(prefix, na=False)])
    print(f'  {prefix}: {count}')
