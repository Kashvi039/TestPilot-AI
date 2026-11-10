
from app.rag.vector_store import store_failure
from app.rag.retriever import retrieve_similar_failures


# ==========================================
# STEP 1: STORE HISTORICAL FAILURES
# ==========================================

# Python project failure
store_failure(
    project_name="Ecommerce Application",
    language="python",
    framework="pytest",
    test_name="test_user_login",
    failure_message="Login fails because the authentication token is not validated.",
    stack_trace="AuthenticationError: Invalid token",
    source_code="if token: allow_access()",
    investigation="Token validation is missing.",
    resolution="Validate token signature and expiry before granting access."
)


# Java project failure
store_failure(
    project_name="Banking Application",
    language="java",
    framework="junit",
    test_name="test_transaction",
    failure_message="Transaction fails because the database connection is not closed.",
    stack_trace="SQLException: Connection leak detected",
    source_code="Connection connection = dataSource.getConnection();",
    investigation="Database connection is not closed.",
    resolution="Use try-with-resources to close the connection."
)


# ==========================================
# STEP 2: SEARCH FOR SIMILAR FAILURES
# ==========================================

results = retrieve_similar_failures(
    failure_message="Authentication fails because the access token is invalid.",
    top_k=3
)


# ==========================================
# STEP 3: DISPLAY RETRIEVED FAILURES
# ==========================================

print("\n========== UNIVERSAL RAG RESULTS ==========")

if not results:
    print("No historical failures found.")

else:
    for index, failure in enumerate(results, start=1):

        metadata = failure.get("metadata") or {}

        print(f"\n---------- RESULT {index} ----------")

        print(
            "Project:",
            metadata.get("project_name", "Unknown")
        )

        print(
            "Language:",
            metadata.get("language", "Unknown")
        )

        print(
            "Framework:",
            metadata.get("framework", "Unknown")
        )

        print(
            "Test Name:",
            metadata.get("test_name", "Unknown")
        )

        print(
            "Similarity Distance:",
            round(failure["distance"], 4)
        )

        print("\nHistorical Failure:")
        print(failure["document"])


print("\n========== RAG EXECUTION COMPLETED ==========")
