
from app.graph.failure_graph import failure_graph

print("\n========== TESTPILOT LANGGRAPH TEST ==========")

print("\nGraph compiled successfully.")

graph_structure = failure_graph.get_graph()

print("\nRegistered workflow nodes:")

for node in graph_structure.nodes:
    print("-", node)

expected_nodes = {
    "failure_investigator",
    "fix_generator",
    "human_approval",
    "fix_applier",
    "fix_verifier",
    "rollback"
}

actual_nodes = set(graph_structure.nodes.keys())

missing_nodes = expected_nodes - actual_nodes

if missing_nodes:
    print("\nMissing nodes:", missing_nodes)
    raise AssertionError("Some workflow nodes are missing.")

print("\nAll expected workflow nodes are registered.")

print("\n========== GRAPH STRUCTURE TEST PASSED ==========")
