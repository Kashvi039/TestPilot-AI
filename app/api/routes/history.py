
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Project, TestRun, TestResult
from app.schemas.history import TestRunResponse


router = APIRouter(
    prefix="/api/history",
    tags=["Test History"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{project_id}", response_model=list[TestRunResponse])
def get_project_history(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    runs = (
        db.query(TestRun)
        .filter(TestRun.project_id == project_id)
        .order_by(TestRun.created_at.desc())
        .all()
    )

    response = []

    for run in runs:
        test_results = (
            db.query(TestResult)
            .filter(TestResult.test_run_id == run.id)
            .all()
        )

        run_data = {
            "id": run.id,
            "project_id": run.project_id,
            "language": run.language,
            "framework": run.framework,
            "status": run.status,
            "passed": run.passed,
            "failed": run.failed,
            "skipped": run.skipped,
            "duration": run.duration,
            "created_at": run.created_at,
            "test_results": test_results
        }

        response.append(run_data)

    return response
