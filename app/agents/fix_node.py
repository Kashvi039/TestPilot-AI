
from pathlib import Path

from app.agents.fix_generator import generate_fix
from app.agents.failure_investigator import FailureState


def generate_fix_node(state: FailureState):
    print("\n========== FIX GENERATOR NODE ==========")

    project_name = state.get("project_name", "")
    language = state.get("language", "python")
    framework = state.get("framework", "pytest")
    test_name = state.get("test_name", "")
    failure_message = state.get("failure_message", "")
    source_code = state.get("source_code", "")
    investigation = state.get("investigation", "")
    target_file = state.get("target_file", "")
    project_path = state.get("project_path", "")

    print("Project path:", project_path)
    print("Target file:", target_file)
    print("Source characters:", len(source_code))

    if not source_code.strip():
        return {
            "can_fix": False,
            "final_status": "FIX_NOT_AVAILABLE",
            "error": "Source code is missing."
        }

    if not target_file or not Path(target_file).is_file():
        return {
            "can_fix": False,
            "final_status": "FIX_NOT_AVAILABLE",
            "error": f"Target file does not exist: {target_file}"
        }

    if not project_path:
        return {
            "can_fix": False,
            "final_status": "FIX_NOT_AVAILABLE",
            "error": "Project path is missing."
        }

    fix_data = generate_fix(
        project_name=project_name,
        language=language,
        framework=framework,
        test_name=test_name,
        failure_message=failure_message,
        source_code=source_code,
        investigation=investigation,
        target_file=target_file,
        project_path=project_path
    )

    print("\n========== FIX GENERATOR DEBUG ==========")
    print("Fix data:", fix_data)
    print("Can fix:", fix_data.get("can_fix"))
    print("Reason:", fix_data.get("reason"))
    print("=========================================")

    if not fix_data.get("can_fix", False):
        return {
            "fix_data": fix_data,
            "can_fix": False,
            "final_status": "FIX_NOT_AVAILABLE"
        }

    return {
        "fix_data": fix_data,
        "target_file": fix_data.get("file_path", target_file),
        "can_fix": True,
        "final_status": "FIX_PENDING_APPROVAL"
    }
