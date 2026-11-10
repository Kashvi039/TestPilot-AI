
import uuid
from pathlib import Path

import chromadb


# --------------------------------------------------
# CHROMADB CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

CHROMA_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

failure_collection = client.get_or_create_collection(
    name="testpilot_failures",
    metadata={
        "description": (
            "Historical failures from multiple projects and languages"
        )
    }
)


# --------------------------------------------------
# STORE FAILURE
# --------------------------------------------------

def store_failure(
    project_name: str,
    language: str,
    framework: str,
    test_name: str,
    failure_message: str,
    stack_trace: str = "",
    source_code: str = "",
    investigation: str = "",
    resolution: str = ""
):

    failure_id = str(uuid.uuid4())

    document = f"""
Project: {project_name}
Language: {language}
Framework: {framework}
Test Name: {test_name}

Failure Message:
{failure_message}

Stack Trace:
{stack_trace}

Source Code:
{source_code}

AI Investigation:
{investigation}

Verified Resolution:
{resolution}
"""

    metadata = {
        "project_name": project_name,
        "language": language,
        "framework": framework,
        "test_name": test_name
    }

    failure_collection.add(
        ids=[failure_id],
        documents=[document],
        metadatas=[metadata]
    )

    print("Failure stored successfully!")

    return failure_id


# --------------------------------------------------
# RETRIEVE SIMILAR FAILURES
# --------------------------------------------------

def retrieve_similar_failures(
    project_name: str,
    language: str,
    failure_message: str,
    source_code: str = "",
    n_results: int = 3
):
    """
    Retrieve historically similar failures from ChromaDB.

    Uses ChromaDB's configured embedding function.
    """

    try:

        total_records = failure_collection.count()

        if total_records == 0:
            return "No historical failures are available."

        query_text = f"""
Project: {project_name}
Language: {language}

Failure Message:
{failure_message}

Source Code:
{source_code}
"""

        results = failure_collection.query(
            query_texts=[query_text],
            n_results=min(n_results, total_records),
            include=["documents", "metadatas", "distances"]
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return "No similar historical failures found."

        retrieved_context = []

        for index, document in enumerate(documents):

            metadata = (
                metadatas[index]
                if metadatas and metadatas[index]
                else {}
            )

            distance = (
                distances[index]
                if distances and distances[index] is not None
                else "Unknown"
            )

            retrieved_context.append(
                f"""
Historical Failure {index + 1}

Project: {metadata.get('project_name', 'Unknown')}
Language: {metadata.get('language', 'Unknown')}
Framework: {metadata.get('framework', 'Unknown')}
Test: {metadata.get('test_name', 'Unknown')}
Similarity distance: {distance}

{document}
"""
            )

        return "\n\n".join(retrieved_context)

    except Exception as e:

        print("Historical failure retrieval failed:", str(e))

        return (
            "Historical failure retrieval was unavailable."
        )
