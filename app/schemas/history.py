
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TestResultResponse(BaseModel):
    id: int
    test_name: str
    outcome: str
    duration: float
    failure_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TestRunResponse(BaseModel):
    id: int
    project_id: int
    language: str
    framework: str
    status: str
    passed: int
    failed: int
    skipped: int
    duration: float
    created_at: datetime
    test_results: list[TestResultResponse] = []

    model_config = ConfigDict(from_attributes=True)
