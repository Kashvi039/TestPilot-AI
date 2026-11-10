
from langgraph.types import interrupt

from app.agents.failure_investigator import FailureState


def approval_node(state: FailureState):

    print("\n========== HUMAN APPROVAL NODE ==========")

    fix_data = state.get("fix_data", {})

    if not state.get("can_fix", False):

        return {
            "approved": False,
            "final_status": "FIX_NOT_AVAILABLE"
        }

    # Prepare patch details for the frontend
    approval_data = {
        "message": "AI-generated fix requires your approval.",
        "file_path": fix_data.get("file_path"),
        "old_code": fix_data.get("old_code", ""),
        "new_code": fix_data.get("new_code", ""),
        "reason": fix_data.get("reason", "")
    }

    # Pause workflow and wait for API approval
    approved = interrupt(approval_data)

    if approved is True:

        print("\nFix approved by user.")

        return {
            "approved": True,
            "final_status": "FIX_APPROVED"
        }

    print("\nFix rejected by user.")

    return {
        "approved": False,
        "final_status": "FIX_REJECTED"
    }
