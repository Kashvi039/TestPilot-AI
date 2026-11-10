from app.runners.pytest_runner import PytestRunner


class RunnerRegistry:

    def __init__(self):

        self.runners = {
            "python": PytestRunner()
        }

    def get_runner(self, language: str):

        runner = self.runners.get(language.lower())

        if runner is None:
            raise ValueError(
                f"No runner available for {language}"
            )

        return runner