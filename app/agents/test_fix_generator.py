
from pprint import pprint

from app.agents.fix_generator import generate_fix


project_name = "Binary Search"
language = "Python"
framework = "Pytest"
test_name = "test_target_present"

failure_message = """
Expected: 4
Actual: -1

The binary_search function returned -1
even though the target exists at index 4.
"""

source_code = """
File: sample_programs/python_programs/binary_search.py

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return -1

        elif arr[mid] < target:
            low = mid + 1

        else:
            high = mid - 1

    return -1
"""

investigation = """
ROOT CAUSE:
When the target is found, the function returns -1 instead of mid.

SUGGESTED FIX:
Replace return -1 with return mid inside the equality condition.

CONFIDENCE:
High.
"""


print("\n========== STRUCTURED FIX GENERATOR TEST ==========")

fix = generate_fix(
    project_name=project_name,
    language=language,
    framework=framework,
    test_name=test_name,
    failure_message=failure_message,
    source_code=source_code,
    investigation=investigation
)

print("\n========== GENERATED FIX DATA ==========")

pprint(fix)

print("\n========== FIELD VALIDATION ==========")

print("Can fix:", fix["can_fix"])
print("File:", fix["file_path"])
print("Old code:", repr(fix["old_code"]))
print("New code:", repr(fix["new_code"]))
print("Reason:", fix["reason"])

print("\n========================================")
