from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    project_id: int
    language: str = Field(min_length=1, max_length=50)


class ExecutionResponse(BaseModel):
    message: str
    project_id: int
    test_run_id: int | None = None
    thread_id: str | None = None
    status: str
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    proposed_fix: dict | None = None


class ApprovalRequest(BaseModel):
    project_id: int
    approved: bool