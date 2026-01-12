import json
import ast
import os

# Load failed tests from pytest cache
with open('.pytest_cache/v/cache/lastfailed', 'r') as f:
    failed_tests = json.load(f)

print(f"Total tests in lastfailed cache: {len(failed_tests)}")
print("="*100)

# Analyze each test
test_files = {}
for test_path in failed_tests.keys():
    file_name = test_path.split("::")[0]
    test_name = "::".join(test_path.split("::")[1:]) if "::" in test_path else ""
    
    if file_name not in test_files:
        test_files[file_name] = []
    test_files[file_name].append(test_name)

# Check if tests are commented out or active
for file_name, tests in test_files.items():
    print(f"\n📄 {file_name}")
    print("-"*100)
    
    if not os.path.exists(file_name):
        print(f"  ⚠️  File does not exist!")
        continue
    
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for test in tests:
        # Extract just the method name
        if "::" in test:
            parts = test.split("::")
            method_name = parts[-1]
        else:
            method_name = test
        
        # Check if it's commented out
        if f"# def {method_name}" in content or f"#def {method_name}" in content:
            print(f"  ✓ {test} - COMMENTED OUT (Already handled)")
        elif f"def {method_name}" in content:
            print(f"  ❌ {test} - ACTIVE (Needs investigation)")
        else:
            print(f"  ⚠️  {test} - NOT FOUND (May have been renamed/removed)")
