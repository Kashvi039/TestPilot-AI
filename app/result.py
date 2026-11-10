
from dataclasses import dataclass, field


@dataclass
class TestCaseResult:
    test_name: str
    outcome: str
    duration: float = 0.0
    investigation: str | None = None
    failure_message: str | None = None


@dataclass
class TestRunResult:
    language: str
    framework: str
    status: str

    passed: int = 0
    failed: int = 0
    skipped: int = 0

    duration: float = 0.0

    stdout: str = ""
    stderr: str = ""
    error: str | None = None

    test_cases: list[TestCaseResult] = field(default_factory=list)
