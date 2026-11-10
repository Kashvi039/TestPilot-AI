
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectResponse


router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"]
)


# Create a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED
)
def register_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    # Validate project directory
    project_path = Path(project.path).expanduser()

    if not project_path.exists() or not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail="Project directory does not exist."
        )

    # Normalize path
    project_path = str(project_path.resolve())

    # Check for duplicate project path
    existing_project = db.query(Project).filter(
        Project.path == project_path
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail="This project is already registered."
        )

    # Create project record
    new_project = Project(
        name=project.name,
        path=project_path,
        default_language=project.default_language
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A project with this path already exists."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to register project."
        )

@router.get("/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.id.desc()).all()
    return projects
