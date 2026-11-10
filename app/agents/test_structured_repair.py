
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

from app.agents.fix_generator import generate_fix
from app.agents.fix_applier import apply_fix


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SOURCE_FILE = (
    BASE_DIR
    / "sample_programs"
    / "python_programs"
    / "binary_search.py"
)


def main():

    print("\n========== STRUCTURED REPAIR TEST ==========")

    # STEP 1: Read the original source file

    if not SOURCE_FILE.exists():
        print("Source file not found.")
        return

    original_code = SOURCE_FILE.read_text(encoding="utf-8")

    # STEP 2: Generate a structured fix

    fix = generate_fix(
        project_name="Binary Search",
        language="Python",
        framework="Pytest",
        test_name="test_target_present",
        failure_message=(
            "Expected index 4 but received -1."
        ),
        source_code=(
            f"File: {SOURCE_FILE}\n\n{original_code}"
        ),
        investigation=(
            "The function returns -1 when the target is found. "
            "It should return mid."
        )
    )

    print("\nGenerated fix:")
    print(fix)

    if not fix["can_fix"]:
        print("\nAI could not generate a safe fix.")
        return

    # STEP 3: Use a temporary copy of the source file

    with TemporaryDirectory() as temp_dir:

        temp_file = Path(temp_dir) / "binary_search.py"

        shutil.copy2(SOURCE_FILE, temp_file)

        # STEP 4: Apply the proposed patch

        result = apply_fix(
            file_path=str(temp_file),
            old_code=fix["old_code"],
            new_code=fix["new_code"],
            approved=True
        )

        print("\nPatch application result:")
        print(result["message"])

        if not result["success"]:
            print("Repair test failed.")
            return

        # STEP 5: Display modified temporary file

        print("\nUpdated temporary source code:")
        print(temp_file.read_text(encoding="utf-8"))

        print("\nBackup created:", Path(result["backup"]).exists())

    print("\nOriginal project file was not modified.")
    print("\n========== REPAIR TEST COMPLETED ==========")


if __name__ == "__main__":
    main()
