
from app.agents.failure_investigator import FailureState
from app.agents.fix_verifier import verify_fix
from app.runners.registry import RunnerRegistry


def verify_fix_node(state: FailureState):

    print("\n========== FIX VERIFIER NODE ==========")

    # ==========================================
    # STEP 1: CHECK PATCH APPLICATION
    # ==========================================

    application_result = state.get("application_result", {})

    if not application_result.get("success", False):

        print("Cannot verify because patch application failed.")

        return {
            "verified": False,
            "verification": {
                "verified": False,
                "status": "APPLICATION_FAILED",
                "message": "Patch was not successfully applied."
            },
            "final_status": "APPLICATION_FAILED"
        }

    # ==========================================
    # STEP 2: SELECT TEST RUNNER
    # ==========================================

    try:

        registry = RunnerRegistry()

        runner = registry.get_runner(
            state["language"]
        )

        # ==========================================
        # STEP 3: EXECUTE TESTS
        # ==========================================

        verification = verify_fix(
            runner=runner,
            project_path=state["project_path"]
        )

        # ==========================================
        # STEP 4: CHECK ACTUAL TEST RESULTS
        # ==========================================

        verified = verification["verified"]

        print("\nVerification completed.")
        print("Status:", verification["status"])
        print("Verified:", verified)

        # ==========================================
        # STEP 5: UPDATE SHARED STATE
        # ==========================================

        return {
            "verification": verification,
            "verified": verified,
            "final_status": (
                "FIX_VERIFIED"
                if verified
                else "VERIFICATION_FAILED"
            )
        }

    except Exception as e:

        print("Verification error:", str(e))

        return {
            "verified": False,
            "verification": {
                "verified": False,
                "status": "VERIFICATION_ERROR",
                "message": str(e)
            },
            "final_status": "VERIFICATION_ERROR",
            "error": str(e)
        }
