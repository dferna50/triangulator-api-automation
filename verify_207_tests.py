"""
Verification script to confirm 207 tests are properly configured
"""
import subprocess
import sys
import pandas as pd
from pathlib import Path

print("="*70)
print("API TEST SUITE VERIFICATION - 207 TESTS")
print("="*70)

# 1. Verify pytest can collect tests
print("\n1. Collecting tests with pytest...")
try:
    result = subprocess.run(
        ["pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Parse output for test count
    output = result.stdout + result.stderr
    if "collected" in output.lower():
        for line in output.split('\n'):
            if "collected" in line.lower():
                print(f"   ✅ {line.strip()}")
                break
    else:
        print(f"   ⚠️  Could not parse test count")
        print(f"   Output: {output[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verify Excel file
print("\n2. Verifying Excel file...")
try:
    df = pd.read_excel('API-Testcases-Complete.xlsx')
    print(f"   ✅ Excel file loaded: {len(df)} test cases")
    
    # Count automated tests
    automated = len(df[df['Automation Status'].str.contains('✅', na=False)])
    print(f"   ✅ Automated test cases: {automated}")
    print(f"   ✅ Coverage: {automated/len(df)*100:.1f}%")
except Exception as e:
    print(f"   ❌ Error loading Excel: {e}")

# 3. Verify test files exist
print("\n3. Verifying test files...")
test_files = [
    'test_schemathesis_comprehensive.py',
    'test_explicit_scenarios.py',
    'test_data_validation.py',
    'test_advanced_strategies.py',
    'test_integration.py',
    'test_performance.py',
    'test_resilience.py',
    'test_observability.py'
]

for test_file in test_files:
    if Path(test_file).exists():
        print(f"   ✅ {test_file}")
    else:
        print(f"   ❌ {test_file} - NOT FOUND")

# 4. Count tests per file
print("\n4. Test count per file...")
file_counts = {
    'test_schemathesis_comprehensive.py': 92,
    'test_explicit_scenarios.py': 49,
    'test_data_validation.py': 17,
    'test_advanced_strategies.py': 14,
    'test_integration.py': 12,
    'test_performance.py': 9,
    'test_resilience.py': 8,
    'test_observability.py': 6
}

total = 0
for file, expected in file_counts.items():
    try:
        result = subprocess.run(
            ["pytest", file, "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout + result.stderr
        
        # Extract count
        for line in output.split('\n'):
            if "collected" in line.lower():
                actual = line.split()[0]
                total += int(actual)
                status = "✅" if int(actual) == expected else "⚠️"
                print(f"   {status} {file}: {actual} tests (expected {expected})")
                break
    except Exception as e:
        print(f"   ❌ {file}: Error - {e}")

print(f"\n   📊 TOTAL: {total} tests")

# 5. Verify pytest.ini markers
print("\n5. Verifying pytest.ini configuration...")
try:
    with open('pytest.ini', 'r', encoding='utf-8') as f:
        content = f.read()
        markers = ['client_report', 'data_validation', 'resilience', 
                   'integration', 'observability', 'performance']
        
        for marker in markers:
            if marker in content:
                print(f"   ✅ Marker '{marker}' configured")
            else:
                print(f"   ❌ Marker '{marker}' NOT FOUND")
except Exception as e:
    print(f"   ❌ Error reading pytest.ini: {e}")

# 6. Final summary
print("\n" + "="*70)
print("VERIFICATION SUMMARY")
print("="*70)
print(f"Expected Tests:  207")
print(f"Collected Tests: {total}")
print(f"Status:          {'✅ PASS' if total == 207 else '⚠️  MISMATCH'}")
print("="*70)

# 7. Next steps
print("\n📋 NEXT STEPS:")
print("   1. Run full test suite:")
print("      .\\run_tests.ps1 -TestType all -HtmlReport")
print("\n   2. Run client-facing tests only:")
print("      pytest -m client_report -v --html=reports/client-tests.html")
print("\n   3. Generate test count report:")
print("      pytest --collect-only 2>&1 | findstr \"collected\"")
print("\n   4. View this verification:")
print("      python verify_207_tests.py")
print("="*70)
