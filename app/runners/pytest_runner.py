
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from pathlib import Path

from app.runners.base import BaseTestRunner
from app.result import TestRunResult, TestCaseResult


class PytestRunner(BaseTestRunner):

    def run_tests(self, project_path: Path) -> TestRunResult:

        start_time = time.perf_counter()

        try:

            # ==========================================
            # STEP 1: CREATE REPORT DIRECTORY
            # ==========================================

            report_dir = project_path.parent / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)

            report_file = report_dir / "pytest-results.xml"

            # ==========================================
            # STEP 2: EXECUTE PYTEST
            # ==========================================

            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "--tb=long",
                    f"--junitxml={report_file}",
                    str(project_path)
                ],
                cwd=project_path.parent,
                capture_output=True,
                text=True,
                timeout=120
            )

            duration = time.perf_counter() - start_time

            # ==========================================
            # STEP 3: INITIALIZE RESULT COUNTERS
            # ==========================================

            passed = 0
            failed = 0
            skipped = 0

            test_cases = []

            # ==========================================
            # STEP 4: PARSE JUNIT XML REPORT
            # ==========================================

            if report_file.exists():

                tree = ET.parse(report_file)
                root = tree.getroot()

                if root.tag == "testsuite":
                    test_elements = root.findall("testcase")
                else:
                    test_elements = root.findall(".//testcase")

                for test in test_elements:

                    test_name = test.attrib.get(
                        "name", "Unknown"
                    )

                    test_duration = float(
                        test.attrib.get("time", 0.0)
                    )

                    failure = test.find("failure")
                    error = test.find("error")
                    skipped_element = test.find("skipped")

                    failure_message = None

                    # ==========================================
                    # STEP 5: EXTRACT COMPLETE FAILURE DETAILS
                    # ==========================================

                    if failure is not None:

                        outcome = "FAILED"

                        failure_message = (
                            f"Failure Message: "
                            f"{failure.attrib.get('message', '')}\n\n"
                            f"Failure Details:\n"
                            f"{failure.text or ''}"
                        )

                    elif error is not None:

                        outcome = "FAILED"

                        failure_message = (
                            f"Error Message: "
                            f"{error.attrib.get('message', '')}\n\n"
                            f"Error Details:\n"
                            f"{error.text or ''}"
                        )

                    elif skipped_element is not None:

                        outcome = "SKIPPED"

                    else:

                        outcome = "PASSED"

                    # ==========================================
                    # STEP 6: UPDATE COUNTERS
                    # ==========================================

                    if outcome == "PASSED":
                        passed += 1

                    elif outcome == "FAILED":
                        failed += 1

                    else:
                        skipped += 1

                    # ==========================================
                    # STEP 7: CREATE TEST CASE RESULT
                    # ==========================================

                    test_cases.append(
                        TestCaseResult(
                            test_name=test_name,
                            outcome=outcome,
                            duration=test_duration,
                            failure_message=failure_message
                        )
                    )

            # ==========================================
            # STEP 8: DETERMINE EXECUTION STATUS
            # ==========================================

            status = (
                "COMPLETED"
                if process.returncode == 0
                else "FAILED"
            )

            # ==========================================
            # STEP 9: RETURN TEST RUN RESULT
            # ==========================================

            return TestRunResult(
                language="Python",
                framework="Pytest",
                status=status,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=duration,
                stdout=process.stdout,
                stderr=process.stderr,
                test_cases=test_cases
            )

        # ==========================================
        # STEP 10: HANDLE EXECUTION ERRORS
        # ==========================================

        except subprocess.TimeoutExpired:

            return TestRunResult(
                language="Python",
                framework="Pytest",
                status="TIMEOUT",
                error="Test execution exceeded the time limit."
            )

        except ET.ParseError as exc:

            return TestRunResult(
                language="Python",
                framework="Pytest",
                status="ERROR",
                error=f"Could not parse XML report: {exc}"
            )

        except Exception as exc:

            return TestRunResult(
                language="Python",
                framework="Pytest",
                status="ERROR",
                error=str(exc)
            )
