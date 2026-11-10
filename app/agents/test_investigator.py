
from app.graph.failure_graph import failure_graph


# Simulate a new failure from a different project
input_data = {
    "project_name": "Authentication Demo",
    "language": "Python",
    "framework": "Pytest",

    "test_name": "test_authentication",

    "failure_message": (
        "Authentication fails because the access token is invalid."
    ),

    "source_code": """
def authenticate(token):
    if token:
        return True
    return False
    """,

    "investigation": ""
}


# Execute the LangGraph workflow
result = failure_graph.invoke(input_data)


print("\n========== TESTPILOT AI INVESTIGATION ==========")
print(result["investigation"])
