
import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from app.rag.vector_store import retrieve_similar_failures


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")


# --------------------------------------------------
# LLM INITIALIZATION
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    groq_api_key=GROQ_API_KEY,
    temperature=0
)


# --------------------------------------------------
# LANGGRAPH STATE
# --------------------------------------------------

class FailureState(TypedDict, total=False):

    # Project information
    project_name: str
    project_path: str
    target_file: str

    # Test information
    language: str
    framework: str
    test_name: str
    failure_message: str

    # Source code
    source_code: str

    # AI investigation
    investigation: str

    # Generated patch
    fix_data: dict
    can_fix: bool

    # Human approval
    approved: bool

    # Patch application
    application_result: dict
    backup_path: str

    # Verification
    verification: dict
    verified: bool

    # Rollback
    rollback_success: bool

    # Workflow status
    final_status: str
    error: str


# --------------------------------------------------
# FAILURE INVESTIGATOR NODE
# --------------------------------------------------

def investigate_failure(state: FailureState):

    print("\n========== FAILURE INVESTIGATOR NODE ==========")

    try:

        project_name = state.get("project_name", "")
        language = state.get("language", "")
        framework = state.get("framework", "")
        test_name = state.get("test_name", "")

        failure_message = state.get(
            "failure_message", ""
        )

        source_code = state.get(
            "source_code", ""
        )

        target_file = state.get(
            "target_file", ""
        )

        print("\nInvestigating:", test_name)
        print("Target file:", target_file)
        print("Source length:", len(source_code))

        # ------------------------------------------
        # RETRIEVE HISTORICAL FAILURES
        # ------------------------------------------

        try:

            historical_context = retrieve_similar_failures(
                project_name=project_name,
                language=language,
                failure_message=failure_message,
                source_code=source_code
            )

        except Exception as e:

            print("RAG retrieval failed:", e)

            historical_context = (
                "No historical failure context available."
            )

        # ------------------------------------------
        # INVESTIGATION PROMPT
        # ------------------------------------------

        prompt = f"""
You are an expert software debugging engineer.

Analyze the failing test using the actual source code.

PROJECT:
{project_name}

LANGUAGE:
{language}

FRAMEWORK:
{framework}

FAILED TEST:
{test_name}

TARGET FILE:
{target_file}

FAILURE MESSAGE:
{failure_message}

ACTUAL SOURCE CODE:
{source_code}

HISTORICAL FAILURE CONTEXT:
{historical_context}

IMPORTANT RULES:

1. Inspect the actual source code before identifying a bug.
2. Never claim that a function is missing if it exists in the supplied source.
3. Quote the actual suspicious statement where possible.
4. Do not invent variable names or functions.
5. Explain the root cause.
6. Suggest the smallest possible correction.
7. State your confidence level honestly.

Use this structure:

1. ROOT CAUSE
2. SUSPICIOUS CODE
3. SUGGESTED FIX
4. HISTORICAL CONTEXT
5. CONFIDENCE

If the supplied source does not contain enough information,
explicitly explain what is missing.
"""

        # ------------------------------------------
        # CALL GROQ
        # ------------------------------------------

        response = llm.invoke(prompt)

        investigation = response.content

        if not isinstance(investigation, str):
            investigation = str(investigation)

        print("\nInvestigation completed.")

        return {
            "investigation": investigation
        }

    except Exception as e:

        print("Failure investigation failed:", str(e))

        return {
            "investigation": (
                "Failure investigation could not be completed."
            ),
            "error": str(e)
        }
