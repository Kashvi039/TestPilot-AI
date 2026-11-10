
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langgraph.types import Command

from app.database import SessionLocal
from app.models import Project
from app.schemas.execution import ExecutionRequest, ApprovalRequest
from app.orchestrator import TestOrchestrator
from app.graph.failure_graph import failure_graph
from app.run_service import save_test_run


router = APIRouter(
    prefix="/api/executions",
    tags=["Test Execution"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def find_pending_approval(snapshot):
    """Return the first pending LangGraph interrupt, if present."""

    for task in snapshot.tasks:
        if task.interrupts:
            return task.interrupts[0].value

    return None


# ==========================================
# START EXECUTION
# ==========================================

@router.post("/")
def start_execution(
    request: ExecutionRequest,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == request.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        orchestrator = TestOrchestrator()

        result = orchestrator.execute(
            language=request.language,
            project_path=project.path,
            thread_id=thread_id
        )

        snapshot = failure_graph.get_state(config)

        approval_data = find_pending_approval(snapshot)

        if approval_data is not None:

            return {
                "status": "APPROVAL_REQUIRED",
                "message": "AI fix is waiting for your approval.",
                "thread_id": thread_id,
                "project_id": project.id,
                "passed": result.passed,
                "failed": result.failed,
                "skipped": result.skipped,
                "duration": result.duration,
                "proposed_fix": approval_data
            }

        final_state = snapshot.values or {}

        return {
            "status": final_state.get(
                "final_status", "COMPLETED"
            ),
            "message": "Test execution completed.",
            "thread_id": thread_id,
            "project_id": project.id,
            "passed": result.passed,
            "failed": result.failed,
            "skipped": result.skipped,
            "duration": result.duration
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(e)}"
        )


# ==========================================
# APPROVE / REJECT FIX
# ==========================================

@router.post("/{thread_id}/approval")
def approve_fix(
    thread_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):

    project = db.query(Project).filter(
        Project.id == request.project_id
    ).first()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        snapshot = failure_graph.get_state(config)

        if not snapshot.tasks:
            raise HTTPException(
                status_code=409,
                detail="Workflow has already completed."
            )

        approval_data = find_pending_approval(snapshot)

        if approval_data is None:
            raise HTTPException(
                status_code=409,
                detail="Workflow is not waiting for approval."
            )

        # Resume the SAME interrupted workflow.
        final_state = failure_graph.invoke(
            Command(resume=request.approved),
            config=config
        )

        final_status = final_state.get(
            "final_status", "UNKNOWN"
        )

        if final_state.get("verified", False):

            verification = final_state.get(
                "verification", {}
            )

            verified_result = verification.get(
                "test_result"
            )

            if verified_result is not None:
                save_test_run(
                    project.id,
                    verified_result
                )

        return {
            "message": (
                "Fix approved and workflow resumed."
                if request.approved
                else "Fix rejected and workflow completed."
            ),
            "thread_id": thread_id,
            "approved": request.approved,
            "final_status": final_status,
            "verified": final_state.get("verified", False),
            "rollback_success": final_state.get(
                "rollback_success", False
            )
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Approval processing failed: {str(e)}"
        )
