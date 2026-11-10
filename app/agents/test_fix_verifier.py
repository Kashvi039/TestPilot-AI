
from pathlib import Path

from app.runners.pytest_runner import PytestRunner
from app.agents.fix_verifier import verify_fix


BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROJECT_PATH = (
    BASE_DIR / "sample_programs" / "python_programs"
)


def main():

    print("\n========== TESTING FIX VERIFIER ==========")

    runner = PytestRunner()

    result = verify_fix(
        runner=runner,
        project_path=str(PROJECT_PATH)
    )

    print("\n========== VERIFICATION RESULT ==========")

    print("Verified:", result["verified"])
    print("Status:", result["status"])
    print("Message:", result["message"])

    print("\n==========================================")


if __name__ == "__main__":
    main()
