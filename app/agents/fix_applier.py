
from pathlib import Path
from datetime import datetime
import difflib
import shutil
import textwrap


def apply_fix(
    file_path: str,
    old_code: str,
    new_code: str,
    approved: bool = False
):
    """
    Safely apply an approved code replacement.

    Supports indentation differences while preserving
    the original file's indentation.
    """

    if not approved:
        return {
            "success": False,
            "message": "User approval is required."
        }

    path = Path(file_path).resolve()

    if not path.exists() or not path.is_file():
        return {
            "success": False,
            "message": "Target source file does not exist."
        }

    if not old_code.strip() or not new_code.strip():
        return {
            "success": False,
            "message": "Old code and new code cannot be empty."
        }

    try:
        original_content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as e:
        return {
            "success": False,
            "message": f"Could not read source file: {e}"
        }

    # Normalize the AI-provided original snippet.
    normalized_old = textwrap.dedent(
        old_code
    ).strip("\n")

    old_lines = normalized_old.splitlines()
    source_lines = original_content.splitlines(keepends=True)

    if not old_lines:
        return {
            "success": False,
            "message": "Original code snippet is empty."
        }

    # Find matching source blocks while ignoring
    # differences in common indentation.
    matches = []

    for start in range(len(source_lines) - len(old_lines) + 1):

        candidate = source_lines[
            start:start + len(old_lines)
        ]

        candidate_text = "".join(candidate)

        normalized_candidate = textwrap.dedent(
            candidate_text
        ).strip("\n")

        if normalized_candidate.splitlines() == old_lines:
            matches.append((start, candidate))

    if len(matches) == 0:
        return {
            "success": False,
            "message": (
                "Original code was not found, even after "
                "normalizing indentation. File unchanged."
            )
        }

    if len(matches) > 1:
        return {
            "success": False,
            "message": (
                "Multiple matching code blocks found. "
                "Refusing ambiguous modification."
            )
        }

    start, matched_lines = matches[0]

    # Determine the indentation difference between
    # the original source and AI-provided snippet.
    source_first_line = matched_lines[0].rstrip("\r\n")
    old_first_line = old_lines[0]

    source_indent = source_first_line[
        :len(source_first_line) -
        len(source_first_line.lstrip())
    ]

    old_indent = old_first_line[
        :len(old_first_line) -
        len(old_first_line.lstrip())
    ]

    if not source_indent.startswith(old_indent):
        return {
            "success": False,
            "message": "Could not safely determine indentation."
        }

    extra_indent = source_indent[len(old_indent):]

    # Normalize the replacement, then restore the
    # indentation required by the original source.
    normalized_new = textwrap.dedent(
        new_code
    ).strip("\n")

    new_lines = normalized_new.splitlines()

    adjusted_new_lines = [
        extra_indent + line if line.strip() else line
        for line in new_lines
    ]

    # Preserve the source file's newline convention.
    newline = "\r\n" if "\r\n" in original_content else "\n"

    replacement = newline.join(adjusted_new_lines)

    if matched_lines[-1].endswith(("\n", "\r")):
        replacement += newline

    # Replace only the uniquely matched block.
    updated_lines = (
        source_lines[:start]
        + [replacement]
        + source_lines[start + len(old_lines):]
    )

    updated_content = "".join(updated_lines)

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    backup_path = path.with_name(
        f"{path.name}.{timestamp}.bak"
    )

    temp_path = path.with_name(
        f"{path.name}.{timestamp}.tmp"
    )

    try:
        shutil.copy2(path, backup_path)

        try:
            temp_path.write_text(
                updated_content,
                encoding="utf-8"
            )

            temp_path.replace(path)

        finally:
            if temp_path.exists():
                temp_path.unlink()

        return {
            "success": True,
            "message": "Approved fix applied successfully.",
            "file": str(path),
            "backup": str(backup_path),
            "diff": "".join(
                difflib.unified_diff(
                    original_content.splitlines(keepends=True),
                    updated_content.splitlines(keepends=True),
                    fromfile="original",
                    tofile="updated"
                )
            )
        }

    except OSError as e:

        try:
            if backup_path.exists():
                shutil.copy2(backup_path, path)
        except OSError:
            pass

        return {
            "success": False,
            "message": f"Could not apply fix: {e}"
        }
