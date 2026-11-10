
from pathlib import Path

from app.runners.registry import RunnerRegistry
from app.run_service import save_test_run
from app.database import SessionLocal
from app.models import Project

from app.graph.failure_graph import failure_graph
from app.rag.vector_store import store_failure
from app.source_extractor import extract_source_context


class TestOrchestrator:

    def __init__(self):
        self.registry = RunnerRegistry()

    def execute(self, language: str, project_path: str, thread_id: str):

        path = Path(project_path).resolve()

        if not path.exists() or not path.is_dir():
            raise ValueError("Invalid project directory")

        # Find registered project
        db = SessionLocal()

        try:
            project = db.query(Project).filter(
                Project.path == str(path)
            ).first()

            if project is None:
                raise ValueError(
                    "Project is not registered in TestPilot AI"
                )

            project_id = project.id
            project_name = project.name

        finally:
            db.close()

        # Execute tests
        runner = self.registry.get_runner(language)

        print(f"\nStarting {language} test execution...")

        result = runner.run_tests(path)

        print("\nTest execution completed!")
        print(f"Passed: {result.passed}")
        print(f"Failed: {result.failed}")
        print(f"Skipped: {result.skipped}")

        save_test_run(project_id, result)

        if result.failed == 0:
            print("\nNo failed tests. AI repair skipped.")
            return result

        print("\nStarting LangGraph AI repair workflow...")

        for test_case in result.test_cases:

            if str(test_case.outcome).strip().lower() not in [
                "failed", "failure"
            ]:
                continue

            print(f"\nInvestigating: {test_case.test_name}")

            failure_message = (
                test_case.failure_message
                or result.stderr
                or result.error
                or "No failure message available."
            )

            # Extract complete source context
            print("\nExtracting relevant source code...")

            try:
                source_contexts = extract_source_context(
                    failure_message=failure_message,
                    project_path=path,
                    context_lines=5
                )

                # Prefer imported implementation over test file
                implementation = next(
                    (
                        item for item in source_contexts
                        if item["type"] == "imported_implementation"
                    ),
                    None
                )

                if implementation is None:
                    implementation = next(
                        (
                            item for item in source_contexts
                            if item["type"] == "traceback"
                        ),
                        None
                    )

                if implementation is None:
                    print("No implementation source found.")
                    continue

                target_file = str(
                    Path(implementation["file"]).resolve()
                )

                source_code = implementation["code"]

                print("\nSource extraction completed!")
                print("Target file:", target_file)
                print("Source characters:", len(source_code))

            except Exception as e:
                print("Source extraction failed:", e)
                continue

            if not source_code.strip():
                print("Source code is empty. Skipping repair.")
                continue

            # Store failure in RAG
            try:
                store_failure(
                    project_name=project_name,
                    language=language,
                    framework=result.framework,
                    test_name=test_case.test_name,
                    failure_message=failure_message,
                    source_code=source_code,
                    investigation="",
                    resolution=""
                )

                print("Failure stored in ChromaDB!")

            except Exception as e:
                print("ChromaDB storage failed:", e)

            # Prepare LangGraph state
            initial_state = {
                "project_name": project_name,
                "project_path": str(path),
                "language": language,
                "framework": result.framework,
                "test_name": test_case.test_name,
                "failure_message": failure_message,
                "source_code": source_code,
                "target_file": target_file,
                "investigation": "",
                "fix_data": {},
                "can_fix": False,
                "approved": False,
                "application_result": {},
                "backup_path": "",
                "verification": {},
                "verified": False,
                "rollback_success": False,
                "final_status": "",
                "error": ""
            }

            print("\n========== LANGGRAPH WORKFLOW ==========")

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            try:
                final_state = failure_graph.invoke(
                    initial_state,
                    config=config
                )

            except Exception as e:
                print("LangGraph workflow failed:", e)
                continue

            # Display investigation
            investigation = final_state.get(
                "investigation", ""
            )

            test_case.investigation = investigation

            print("\n========== AI INVESTIGATION ==========")
            print(investigation)

            final_status = final_state.get(
                "final_status", "UNKNOWN"
            )

            print("\n========== REPAIR WORKFLOW RESULT ==========")
            print("Final status:", final_status)

            # Save verified execution
            if final_state.get("verified", False):

                verification = final_state.get(
                    "verification", {}
                )

                verified_result = verification.get("test_result")

                if verified_result is not None:
                    result = verified_result

                    save_test_run(
                        project_id,
                        verified_result
                    )

                    print("Verified results saved.")

                break

            if final_state.get("rollback_success", False):
                print("Incorrect patch rolled back successfully.")
                break

            if final_status == "ROLLBACK_FAILED":
                print("CRITICAL: Automatic rollback failed.")
                break

            stop_statuses = {
                "FIX_REJECTED",
                "PATCH_APPLIED",
                "FIX_VERIFIED",
                "VERIFICATION_FAILED",
                "FIX_ROLLED_BACK",
                "ROLLBACK_FAILED",
                "PATCH_APPLICATION_FAILED",
                "INVALID_TARGET_FILE",
                "VERIFICATION_ERROR",
                "FIX_NOT_AVAILABLE",
                "FIX_GENERATION_FAILED"
            }

            if final_status in stop_statuses:
                break

        return result
