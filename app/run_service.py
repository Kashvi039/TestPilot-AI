
from app.database import SessionLocal
from app.models import TestRun, TestResult


def save_test_run(project_id, result):
    db = SessionLocal()

    try:
        # Step 1: Create the overall test execution record
        test_run = TestRun(
            project_id=project_id,
            language=result.language,
            framework=result.framework,
            status=result.status,
            passed=result.passed,
            failed=result.failed,
            skipped=result.skipped,
            duration=result.duration
        )

        db.add(test_run)

        # Generate the TestRun ID
        db.flush()

        # Step 2: Save individual test-case results
        for test_case in result.test_cases:

            test_result = TestResult(
                test_run_id=test_run.id,
                test_name=test_case.test_name,
                outcome=test_case.outcome,
                duration=test_case.duration,
                failure_message=test_case.failure_message
            )

            db.add(test_result)

        # Step 3: Commit everything together
        db.commit()

        db.refresh(test_run)

        print("Test execution saved successfully!")
        print("Test Run ID:", test_run.id)
        print("Individual test results saved:", len(result.test_cases))

        return test_run.id

    except Exception as e:
        db.rollback()
        print("Error saving test execution:", e)
        raise

    finally:
        db.close()
