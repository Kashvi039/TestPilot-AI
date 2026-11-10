
from app.rag.vector_store import failure_collection


def retrieve_similar_failures(
    failure_message: str,
    stack_trace: str = "",
    source_code: str = "",
    language: str | None = None,
    framework: str | None = None,
    top_k: int = 3
):
    """
    Retrieve historically similar failures across projects.

    Language and framework filters are optional.
    By default, search across all supported languages.
    """

    total_records = failure_collection.count()

    if total_records == 0:
        return []

    # Build a search query using available failure information
    query = f"""
    Failure Message: {failure_message}
    Stack Trace: {stack_trace}
    Relevant Source Code: {source_code}
    """

    # Apply filters only when explicitly provided
    filters = []

    if language:
        filters.append({"language": language})

    if framework:
        filters.append({"framework": framework})

    where_filter = None

    if len(filters) == 1:
        where_filter = filters[0]
    elif len(filters) > 1:
        where_filter = {"$and": filters}

    # Search ChromaDB
    search_args = {
        "query_texts": [query],
        "n_results": min(top_k, total_records)
    }

    if where_filter:
        search_args["where"] = where_filter

    results = failure_collection.query(**search_args)

    # Convert results into a convenient list
    retrieved_failures = []

    for i, document in enumerate(results["documents"][0]):
        retrieved_failures.append({
            "document": document,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_failures
