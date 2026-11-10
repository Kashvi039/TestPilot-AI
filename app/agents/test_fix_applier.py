
from pathlib import Path
from tempfile import TemporaryDirectory

from app.agents.fix_applier import apply_fix


def run_tests():

    print("\n========== FIX APPLIER TESTS ==========")

    # TEST 1: APPROVED FIX

    print("\nTEST 1: Applying an approved fix")

    with TemporaryDirectory() as temp_dir:

        file_path = Path(temp_dir) / "binary_search.py"

        original_code = """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return -1

    return -1
"""

        file_path.write_text(original_code, encoding="utf-8")

        result = apply_fix(
            file_path=str(file_path),
            old_code="""if arr[mid] == target:
    return -1""",
            new_code="""if arr[mid] == target:
    return mid""",
            approved=True
        )

        print(result["message"])
        print("Success:", result["success"])

        if result["success"]:
            print("\nUpdated code:")
            print(file_path.read_text(encoding="utf-8"))

            print("Backup exists:", Path(result["backup"]).exists())
            print("\nGenerated diff:")
            print(result["diff"])

    # TEST 2: WITHOUT APPROVAL

    print("\nTEST 2: Applying without approval")

    with TemporaryDirectory() as temp_dir:

        file_path = Path(temp_dir) / "binary_search.py"
        file_path.write_text("return -1\n", encoding="utf-8")

        result = apply_fix(
            file_path=str(file_path),
            old_code="return -1",
            new_code="return mid",
            approved=False
        )

        print(result["message"])
        print("Success:", result["success"])

        print(
            "File unchanged:",
            file_path.read_text(encoding="utf-8") == "return -1\n"
        )

    # TEST 3: ORIGINAL CODE DOES NOT MATCH

    print("\nTEST 3: Incorrect original code")

    with TemporaryDirectory() as temp_dir:

        file_path = Path(temp_dir) / "binary_search.py"
        file_path.write_text("return mid\n", encoding="utf-8")

        result = apply_fix(
            file_path=str(file_path),
            old_code="return -1",
            new_code="return 0",
            approved=True
        )

        print(result["message"])
        print("Success:", result["success"])

        print(
            "File unchanged:",
            file_path.read_text(encoding="utf-8") == "return mid\n"
        )

    print("\n========== TESTS COMPLETED ==========")


if __name__ == "__main__":
    run_tests()
