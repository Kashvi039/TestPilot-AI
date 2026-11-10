
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from app.agents.fix_applier import apply_fix
from app.agents.fix_verifier import verify_fix
from app.runners.pytest_runner import PytestRunner


def run_rollback_test():

    print("\n========== AUTOMATIC ROLLBACK TEST ==========")

    with TemporaryDirectory() as temp_dir:

        # ==========================================
        # STEP 1: CREATE TEMPORARY PROJECT
        # ==========================================

        project_path = Path(temp_dir) / "demo_project"
        project_path.mkdir()

        source_file = project_path / "binary_search.py"
        test_file = project_path / "test_binary_search.py"

        # ==========================================
        # STEP 2: CREATE CORRECT SOURCE CODE
        # ==========================================

        original_code = """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1
"""

        source_file.write_text(
            original_code,
            encoding="utf-8"
        )

        # ==========================================
        # STEP 3: CREATE TEST CASES
        # ==========================================

        test_code = """from binary_search import binary_search


def test_target_present():
    assert binary_search([1, 3, 5, 7], 5) == 2


def test_first_element():
    assert binary_search([1, 3, 5, 7], 1) == 0


def test_last_element():
    assert binary_search([1, 3, 5, 7], 7) == 3


def test_target_absent():
    assert binary_search([1, 3, 5, 7], 4) == -1
"""

        test_file.write_text(
            test_code,
            encoding="utf-8"
        )

        runner = PytestRunner()

        # ==========================================
        # STEP 4: VERIFY ORIGINAL CODE
        # ==========================================

        print("\nSTEP 1: Running tests on original code...")

        initial_result = runner.run_tests(project_path)

        print("Passed:", initial_result.passed)
        print("Failed:", initial_result.failed)

        assert initial_result.failed == 0, (
            "Original code should pass all tests."
        )

        print("Original code is working correctly.")

        # ==========================================
        # STEP 5: APPLY INTENTIONALLY WRONG PATCH
        # ==========================================

        print("\nSTEP 2: Applying an incorrect patch...")

        application_result = apply_fix(
            file_path=str(source_file),

            old_code="""if arr[mid] == target:
    return mid""",

            new_code="""if arr[mid] == target:
    return 0""",

            approved=True
        )

        print(application_result["message"])

        assert application_result["success"], (
            "Incorrect patch should apply successfully."
        )

        backup_path = application_result["backup"]

        # ==========================================
        # STEP 6: VERIFY THE INCORRECT PATCH
        # ==========================================

        print("\nSTEP 3: Verifying the incorrect patch...")

        verification = verify_fix(
            runner=runner,
            project_path=str(project_path)
        )

        print("Verified:", verification["verified"])
        print("Status:", verification["status"])

        assert not verification["verified"], (
            "Incorrect patch should fail verification."
        )

        print("Incorrect patch detected successfully.")

        # ==========================================
        # STEP 7: RESTORE ORIGINAL SOURCE CODE
        # ==========================================

        print("\nSTEP 4: Restoring original source code...")

        shutil.copy2(backup_path, source_file)

        restored_code = source_file.read_text(
            encoding="utf-8"
        )

        assert restored_code == original_code, (
            "Rollback did not restore the exact original code."
        )

        print("Original source code restored successfully.")

        # ==========================================
        # STEP 8: RUN TESTS AFTER ROLLBACK
        # ==========================================

        print("\nSTEP 5: Running tests after rollback...")

        final_result = runner.run_tests(project_path)

        print("Passed:", final_result.passed)
        print("Failed:", final_result.failed)

        assert final_result.failed == 0, (
            "Tests should pass after rollback."
        )

        print("\n========== ROLLBACK TEST PASSED ==========")
        print("Incorrect patch was detected.")
        print("Original code was restored.")
        print("All tests passed after restoration.")


if __name__ == "__main__":
    run_rollback_test()
