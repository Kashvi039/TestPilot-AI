
from pathlib import Path


def verify_fix(runner, project_path: str):

    """
    Rerun tests and verify whether a proposed fix worked.
    Actual test results determine verification.
    """

    path = Path(project_path).resolve()

    # STEP 1: Validate project directory

    if not path.exists() or not path.is_dir():
        return {
            "verified": False,
            "status": "INVALID_PROJECT",
            "message": "Project directory does not exist.",
            "test_result": None
        }

    # STEP 2: Execute tests again

    try:
        print("\nRerunning tests to verify the fix...")

        result = runner.run_tests(path)

    except Exception as e:
        return {
            "verified": False,
            "status": "EXECUTION_ERROR",
            "message": f"Could not execute tests: {str(e)}",
            "test_result": None
        }

    # STEP 3: Display results

    print("\n========== FIX VERIFICATION ==========")

    print("Test status:", result.status)
    print("Passed:", result.passed)
    print("Failed:", result.failed)
    print("Skipped:", result.skipped)

    total_tests = (
        result.passed +
        result.failed +
        result.skipped
    )

    # STEP 4: Check execution errors

    if result.error is not None:
        return {
            "verified": False,
            "status": "EXECUTION_ERROR",
            "message": (
                "Test execution encountered an error: "
                f"{result.error}"
            ),
            "test_result": result
        }

    if result.status not in ["COMPLETED", "FAILED"]:
        return {
            "verified": False,
            "status": "EXECUTION_ERROR",
            "message": (
                f"Unexpected test execution status: {result.status}"
            ),
            "test_result": result
        }

    # STEP 5: Check whether tests were collected

    if total_tests == 0:
        return {
            "verified": False,
            "status": "NO_TESTS_FOUND",
            "message": "No tests were collected.",
            "test_result": result
        }

    # STEP 6: Check failed tests

    if result.failed > 0:
        return {
            "verified": False,
            "status": "VERIFICATION_FAILED",
            "message": (
                f"{result.failed} test(s) are still failing. "
                "The proposed fix is not verified."
            ),
            "test_result": result
        }

    # STEP 7: Ensure at least one test passed

    if result.passed == 0:
        return {
            "verified": False,
            "status": "NO_TESTS_PASSED",
            "message": (
                "No tests passed. Fix cannot be verified."
            ),
            "test_result": result
        }

    # STEP 8: Successful verification

    print("\nAll collected tests passed!")
    print("Fix successfully verified.")

    return {
        "verified": True,
        "status": "VERIFIED",
        "message": (
            "All collected tests passed. "
            "The fix is successfully verified."
        ),
        "test_result": result
    }
