
from pathlib import Path

from app.agents.failure_investigator import FailureState
from app.agents.fix_applier import apply_fix


def apply_fix_node(state: FailureState):

    print("\n========== FIX APPLIER NODE ==========")

    # ==========================================
    # STEP 1: CHECK USER APPROVAL
    # ==========================================

    if not state.get("approved", False):

        print("Fix was not approved. No file will be modified.")

        return {
            "application_result": {
                "success": False,
                "message": "User approval is required."
            },
            "final_status": "FIX_REJECTED"
        }

    # ==========================================
    # STEP 2: GET GENERATED FIX
    # ==========================================

    fix_data = state.get("fix_data", {})

    if not fix_data.get("can_fix", False):

        return {
            "application_result": {
                "success": False,
                "message": "No valid fix is available."
            },
            "final_status": "FIX_NOT_AVAILABLE"
        }

    # ==========================================
    # STEP 3: VALIDATE PROJECT PATH
    # ==========================================

    project_path = Path(
        state["project_path"]
    ).resolve()

    proposed_path = Path(
        fix_data.get("file_path", "")
    )

    if proposed_path.is_absolute():
        target_file = proposed_path.resolve()
    else:
        target_file = (project_path / proposed_path).resolve()

    if (
        not target_file.is_relative_to(project_path)
        or not target_file.is_file()
    ):

        print("Rejected: Invalid target file.")

        return {
            "application_result": {
                "success": False,
                "message": (
                    "Target file is outside the registered project "
                    "or does not exist."
                )
            },
            "final_status": "INVALID_TARGET_FILE"
        }

    # ==========================================
    # STEP 4: APPLY APPROVED PATCH
    # ==========================================

    print("\nApplying approved patch...")
    print("Target file:", target_file)

    try:

        application_result = apply_fix(
            file_path=str(target_file),
            old_code=fix_data["old_code"],
            new_code=fix_data["new_code"],
            approved=True
        )

        print(application_result["message"])

        if not application_result["success"]:

            return {
                "application_result": application_result,
                "final_status": "PATCH_APPLICATION_FAILED"
            }

        # ==========================================
        # STEP 5: RETURN APPLICATION DETAILS
        # ==========================================

        print("Patch applied successfully.")

        return {
            "target_file": str(target_file),
            "application_result": application_result,
            "backup_path": application_result["backup"],
            "final_status": "PATCH_APPLIED"
        }

    except Exception as e:

        print("Patch application error:", str(e))

        return {
            "application_result": {
                "success": False,
                "message": str(e)
            },
            "final_status": "PATCH_APPLICATION_FAILED",
            "error": str(e)
        }
