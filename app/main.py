
from pathlib import Path
from app.orchestrator import TestOrchestrator

if __name__ == "__main__":

    orchestrator = TestOrchestrator()

    result = orchestrator.execute(
        language="python",
        project_path=str(
            Path("sample_programs/python_programs").resolve()
        )
    )

    print("\n========== TESTPILOT AI REPORT ==========")
    print("Language:", result.language)
    print("Framework:", result.framework)
    print("Status:", result.status)
    print("Passed:", result.passed)
    print("Failed:", result.failed)
    print("Skipped:", result.skipped)
    print("Duration:", round(result.duration, 3), "seconds")

    if result.error:
        print("Error:", result.error)

    print("\n========== EXECUTION LOG ==========")
    print(result.stdout)

    if result.stderr:
        print(result.stderr)
