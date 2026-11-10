from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, func
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    path = Column(String(500), nullable=False, unique=True)
    default_language = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    language = Column(String(50), nullable=False)
    framework = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False)

    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    skipped = Column(Integer, default=0)

    duration = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)

    test_run_id = Column(
        Integer,
        ForeignKey("test_runs.id"),
        nullable=False
    )

    test_name = Column(String(255), nullable=False)
    outcome = Column(String(30), nullable=False)

    duration = Column(Float, default=0.0)

    failure_message = Column(String, nullable=True)
