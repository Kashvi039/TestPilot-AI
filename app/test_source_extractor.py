
from pathlib import Path

from app.source_extractor import extract_source_context


# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_PATH = (
    BASE_DIR / "sample_programs" / "python_programs"
)

# Simulate a traceback reference
failure_message = """
AssertionError:
python_programs\\test_binary_search.py:8
"""

# Extract source context
results = extract_source_context(
    failure_message=failure_message,
    project_path=PROJECT_PATH,
    context_lines=5
)

# Display results
print("\n========== SOURCE EXTRACTION TEST ==========")

if results:

    for result in results:

        print("\nFile:", result["file"])
        print("Line:", result["line"])
        print("\nExtracted Code:")
        print(result["code"])

else:
    print("No source code references found.")

print("\n============================================")
