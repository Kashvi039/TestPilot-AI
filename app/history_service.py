
from app.database import SessionLocal
from app.models import Project, TestRun, TestResult


def list_projects():
    db = SessionLocal()

    try:
        projects = db.query(Project).order_by(Project.id).all()

        print("\n========== REGISTERED PROJECTS ==========")

        if not projects:
            print("No projects registered.")
            return

        for project in projects:
            print(
                f"ID: {project.id} | "
                f"Name: {project.name} | "
                f"Language: {project.default_language}"
            )

    except Exception as e:
        print("Error retrieving projects:", e)

    finally:
        db.close()


def get_project_history(project_id):
    db = SessionLocal()

    try:
        # Retrieve all executions for the selected project
        runs = (
            db.query(TestRun)
            .filter(TestRun.project_id == project_id)
            .order_by(TestRun.created_at.desc())
            .all()
        )

        print("\n========== TEST EXECUTION HISTORY ==========")

        if not runs:
            print("No test execution history found for this project.")
            return

        for run in runs:

            print("\n====================================")
            print("Run ID:", run.id)
            print("Language:", run.language)
            print("Framework:", run.framework)
            print("Status:", run.status)
            print("Passed:", run.passed)
            print("Failed:", run.failed)
            print("Skipped:", run.skipped)
            print("Duration:", round(run.duration, 3), "seconds")
            print("Created At:", run.created_at)

            # Retrieve individual test results for this execution
            test_results = (
                db.query(TestResult)
                .filter(TestResult.test_run_id == run.id)
                .all()
            )

            print("\nIndividual Test Results:")

            if not test_results:
                print("No individual test results found.")

            for test in test_results:
                print("\nTest Name:", test.test_name)
                print("Outcome:", test.outcome)
                print("Duration:", round(test.duration, 3), "seconds")

                if test.outcome == "FAILED":
                    print("Failure Message:", test.failure_message)

    except Exception as e:
        print("Error retrieving test history:", e)

    finally:
        db.close()


if __name__ == "__main__":

    # Step 1: Display all registered projects
    list_projects()

    # Step 2: Ask the user to select a project
    try:
        project_id = int(input("\nEnter Project ID: "))

        # Step 3: Display execution history
        get_project_history(project_id)

    except ValueError:
        print("Invalid input! Please enter a numeric Project ID.")
