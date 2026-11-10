
import shutil
from pathlib import Path

from app.agents.failure_investigator import FailureState


def rollback_node(state: FailureState):

    print("\n========== ROLLBACK NODE ==========")

    # ==========================================
    # STEP 1: CHECK VERIFICATION RESULT
    # ==========================================

    if state.get("verified", False):

        print("Fix is verified. Rollback is not required.")

        return {
            "rollback_success": False,
            "final_status": "FIX_VERIFIED"
        }

    # ==========================================
    # STEP 2: GET BACKUP INFORMATION
    # ==========================================

    backup_path = state.get("backup_path")
    target_file = state.get("target_file")

    if not backup_path or not target_file:

        print("Rollback failed: backup information is missing.")

        return {
            "rollback_success": False,
            "final_status": "ROLLBACK_FAILED",
            "error": "Backup path or target file is missing."
        }

    backup = Path(backup_path).resolve()
    target = Path(target_file).resolve()

    # ==========================================
    # STEP 3: VALIDATE BACKUP
    # ==========================================

    if not backup.is_file():

        print("Rollback failed: backup file does not exist.")

        return {
            "rollback_success": False,
            "final_status": "ROLLBACK_FAILED",
            "error": "Backup file does not exist."
        }

    if not target.is_file():

        print("Rollback failed: target file does not exist.")

        return {
            "rollback_success": False,
            "final_status": "ROLLBACK_FAILED",
            "error": "Target file does not exist."
        }

    # ==========================================
    # STEP 4: RESTORE ORIGINAL FILE
    # ==========================================

    try:

        print("\nRestoring original source file...")

        shutil.copy2(backup, target)

        print("Original source file restored successfully.")

        # ==========================================
        # STEP 5: VERIFY RESTORATION
        # ==========================================

        print("Checking restored file...")

        with backup.open("rb") as backup_file:
            backup_content = backup_file.read()

        with target.open("rb") as target_file_obj:
            restored_content = target_file_obj.read()

        if backup_content != restored_content:

            print("Restoration verification failed.")

            return {
                "rollback_success": False,
                "final_status": "ROLLBACK_FAILED",
                "error": "Restored file does not match backup."
            }

        print("Restoration verified successfully.")

        return {
            "rollback_success": True,
            "final_status": "FIX_ROLLED_BACK"
        }

    except Exception as e:

        print("CRITICAL: Rollback failed:", str(e))

        print("Original backup remains at:", backup)

        return {
            "rollback_success": False,
            "final_status": "ROLLBACK_FAILED",
            "error": str(e)
        }
