
import ast
import re
from pathlib import Path


def extract_file_references(failure_message: str):
    """Extract file paths and line numbers from traceback."""

    if not failure_message:
        return []

    pattern = re.compile(
        r'(?P<file>(?:[A-Za-z]:)?[^\r\n]*?\.py)'
        r':(?P<line>\d+)'
    )

    references = []

    for match in pattern.finditer(failure_message):
        references.append({
            "file": match.group("file").strip(),
            "line": int(match.group("line"))
        })

    return references


def resolve_source_file(file_reference: str, project_path: Path):
    """Resolve a file reference inside the permitted project directory."""

    project_path = Path(project_path).resolve()
    allowed_root = project_path.parent.resolve()

    reference = Path(file_reference)

    candidates = (
        [reference]
        if reference.is_absolute()
        else [
            project_path / reference,
            project_path.parent / reference
        ]
    )

    for candidate in candidates:
        try:
            resolved = candidate.resolve()

            if (
                resolved.is_relative_to(allowed_root)
                and resolved.is_file()
            ):
                return resolved

        except (OSError, ValueError):
            continue

    return None


def extract_code_snippet(
    file_path: Path,
    line_number: int,
    context_lines: int = 5
):
    """Extract code surrounding a particular line."""

    try:
        lines = Path(file_path).read_text(
            encoding="utf-8",
            errors="replace"
        ).splitlines()

    except OSError:
        return ""

    if line_number < 1 or line_number > len(lines):
        return ""

    start = max(0, line_number - 1 - context_lines)
    end = min(len(lines), line_number + context_lines)

    return "\n".join(
        f"{index + 1}: {lines[index]}"
        for index in range(start, end)
    )




def read_complete_source(file_path: Path):
    try:
        return Path(file_path).read_text(
            encoding="utf-8",
            errors="replace"
        )
    except OSError as error:
        print("Source read error:", error)
        return ""

def extract_imported_files(test_file: Path, project_path: Path):
    """Find local Python modules imported by a test file."""

    project_path = Path(project_path).resolve()
    test_file = Path(test_file).resolve()

    try:
        source = test_file.read_text(
            encoding="utf-8",
            errors="replace"
        )
        tree = ast.parse(source)

    except (OSError, SyntaxError):
        return []

    imported_files = []

    for node in ast.walk(tree):

        module_names = []

        if isinstance(node, ast.Import):
            module_names.extend(
                alias.name.split(".")[0]
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom) and node.module:
            module_names.append(
                node.module.split(".")[0]
            )

        for module_name in module_names:

            module_file = (
                project_path / f"{module_name}.py"
            ).resolve()

            if (
                module_file.is_relative_to(project_path)
                and module_file.is_file()
                and module_file not in imported_files
            ):
                imported_files.append(module_file)

    return imported_files


def extract_source_context(
    failure_message: str,
    project_path: Path,
    context_lines: int = 5
):
    """Extract traceback code and locally imported implementation code."""

    project_path = Path(project_path).resolve()

    references = extract_file_references(failure_message)

    extracted_context = []
    seen = set()

    for reference in references:

        resolved_file = resolve_source_file(
            reference["file"],
            project_path
        )

        if resolved_file is None:
            continue

        key = (resolved_file, reference["line"])

        if key in seen:
            continue

        seen.add(key)

        snippet = extract_code_snippet(
            resolved_file,
            reference["line"],
            context_lines
        )

        if snippet:
            extracted_context.append({
                "file": str(resolved_file),
                "line": reference["line"],
                "type": "traceback",
                "code": snippet
            })

        # Find implementation files imported by the test file
        imported_files = extract_imported_files(
            resolved_file,
            project_path
        )

        for imported_file in imported_files:

            import_key = (imported_file, 1)

            if import_key in seen:
                continue

            seen.add(import_key)

            implementation_code = imported_file.read_text(
                encoding="utf-8",
                errors="replace"
            )

            if implementation_code:
                extracted_context.append({
                    "file": str(imported_file),
                    "line": 1,
                    "type": "imported_implementation",
                    "code": implementation_code
                })

    return extracted_context
