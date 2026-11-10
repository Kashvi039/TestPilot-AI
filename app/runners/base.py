from abc import ABC, abstractmethod
from pathlib import Path

from app.result import TestRunResult


class BaseTestRunner(ABC):

    @abstractmethod
    def run_tests(self, project_path: Path) -> TestRunResult:
        pass