
import json
import re
from pathlib import Path

from app.agents.failure_investigator import llm


def generate_fix(
    project_name: str,
    language: str,
    framework: str,
    test_name: str,
    failure_message: str,
    source_code: str,
    investigation: str,
    target_file: str = "",
    project_path: str = ""
):
    """
    Generate a minimal code patch using Groq.
    Validate the patch against the actual source file.
    Does not modify files.
    """

    try:
        if not target_file or not project_path:
            raise ValueError("Target file or project path is missing.")

        target = Path(target_file).resolve()
        project_root = Path(project_path).resolve()

        if not target.is_file():
            raise ValueError("Target file does not exist.")

        if not target.is_relative_to(project_root):
            raise ValueError("Target file is outside the project directory.")

        actual_source = target.read_text(encoding="utf-8")

        if actual_source != source_code:
            raise ValueError(
                "Source code does not match the current target file."
            )

        prompt = f"""
You are an expert Python debugging and code repair agent.

PROJECT: {project_name}
LANGUAGE: {language}
FRAMEWORK: {framework}
FAILED TEST: {test_name}

FAILURE:
{failure_message}

INVESTIGATION:
{investigation}

TARGET FILE:
{target}

COMPLETE ACTUAL SOURCE CODE:
{actual_source}

TASK:
Find the exact defective statement and generate the smallest safe patch.

RULES:
1. Copy old_code exactly from the source.
2. Do not add line numbers.
3. Preserve existing variable names.
4. Do not rewrite unrelated functions.
5. Do not invent file paths.
6. new_code must be a complete replacement for old_code.
7. If you cannot identify a safe correction, return can_fix=false.
8. Return valid JSON only.

Expected response:

{{
    "can_fix": true,
    "old_code": "exact original source snippet",
    "new_code": "corrected source snippet",
    "reason": "brief explanation"
}}

If no safe patch is possible:

{{
    "can_fix": false,
    "old_code": "",
    "new_code": "",
    "reason": "explanation"
}}
"""

        response = llm.invoke(prompt)
        content = response.content

        if not isinstance(content, str):
            content = str(content)

        content = content.strip()

        content = re.sub(
            r"^```(?:json)?\s*",
            "",
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(r"\s*```$", "", content)

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("AI did not return valid JSON.")

        fix_data = json.loads(content[start:end + 1])

        if not isinstance(fix_data, dict):
            raise ValueError("AI response must be a JSON object.")

        if not isinstance(fix_data.get("can_fix"), bool):
            raise ValueError("Invalid can_fix value.")

        if not fix_data["can_fix"]:
            return {
                "can_fix": False,
                "file_path": "",
                "old_code": "",
                "new_code": "",
                "reason": fix_data.get("reason", "No safe fix available.")
            }

        old_code = fix_data.get("old_code", "")
        new_code = fix_data.get("new_code", "")

        if not old_code.strip() or not new_code.strip():
            raise ValueError("Generated code snippets cannot be empty.")

        if old_code == new_code:
            raise ValueError("Patch does not change the source.")

        if actual_source.count(old_code) != 1:
            raise ValueError(
                "old_code must match exactly once in the source file."
            )

        return {
            "can_fix": True,
            "file_path": str(target),
            "old_code": old_code,
            "new_code": new_code,
            "reason": fix_data.get("reason", "")
        }

    except Exception as e:
        return {
            "can_fix": False,
            "file_path": "",
            "old_code": "",
            "new_code": "",
            "reason": f"Fix generation failed: {e}"
        }
