
from pathlib import Path

from app.database import SessionLocal
from app.models import Project


def register_project(name, project_path, language):
    db = SessionLocal()

    try:
        absolute_path = str(Path(project_path).resolve())

        existing_project = db.query(Project).filter(
            Project.path == absolute_path
        ).first()

        if existing_project:
            print("Project already registered!")
            print("Project ID:", existing_project.id)
            return

        project = Project(
            name=name,
            path=absolute_path,
            default_language=language
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        print("Project registered successfully!")
        print("Project ID:", project.id)
        print("Project Name:", project.name)
        print("Project Path:", project.path)
        print("Language:", project.default_language)

    except Exception as e:
        db.rollback()
        print("Error registering project:", e)

    finally:
        db.close()


if __name__ == "__main__":
    register_project(
        name="Binary Search",
        project_path="sample_programs/python_programs",
        language="python"
    )
