
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.failure_investigator import (
    FailureState,
    investigate_failure
)

from app.agents.fix_node import generate_fix_node
from app.agents.approval_node import approval_node
from app.agents.apply_node import apply_fix_node
from app.agents.verify_node import verify_fix_node
from app.agents.rollback_node import rollback_node


# ==========================================
# STEP 1: CREATE WORKFLOW
# ==========================================

builder = StateGraph(FailureState)


# ==========================================
# STEP 2: REGISTER NODES
# ==========================================

builder.add_node(
    "failure_investigator",
    investigate_failure
)

builder.add_node(
    "fix_generator",
    generate_fix_node
)

builder.add_node(
    "human_approval",
    approval_node
)

builder.add_node(
    "fix_applier",
    apply_fix_node
)

builder.add_node(
    "fix_verifier",
    verify_fix_node
)

builder.add_node(
    "rollback",
    rollback_node
)


# ==========================================
# STEP 3: DEFINE ROUTING FUNCTIONS
# ==========================================

def route_after_investigation(state: FailureState):

    investigation = state.get("investigation", "")

    if (
        not investigation
        or "could not be completed" in investigation.lower()
        or "error:" in investigation.lower()
    ):
        return "end"

    return "fix_generator"


def route_after_fix_generation(state: FailureState):

    if state.get("can_fix", False):
        return "human_approval"

    return "end"


def route_after_approval(state: FailureState):

    if state.get("approved", False):
        return "fix_applier"

    return "end"


def route_after_application(state: FailureState):

    application_result = state.get(
        "application_result", {}
    )

    if application_result.get("success", False):
        return "fix_verifier"

    return "end"


def route_after_verification(state: FailureState):

    if state.get("verified", False):
        return "end"

    # Rollback only if a patch was applied successfully.
    if state.get("backup_path") and state.get("target_file"):
        return "rollback"

    return "end"


# ==========================================
# STEP 4: CONNECT WORKFLOW
# ==========================================

builder.add_edge(
    START,
    "failure_investigator"
)

builder.add_conditional_edges(
    "failure_investigator",
    route_after_investigation,
    {
        "fix_generator": "fix_generator",
        "end": END
    }
)

builder.add_conditional_edges(
    "fix_generator",
    route_after_fix_generation,
    {
        "human_approval": "human_approval",
        "end": END
    }
)

builder.add_conditional_edges(
    "human_approval",
    route_after_approval,
    {
        "fix_applier": "fix_applier",
        "end": END
    }
)

builder.add_conditional_edges(
    "fix_applier",
    route_after_application,
    {
        "fix_verifier": "fix_verifier",
        "end": END
    }
)

builder.add_conditional_edges(
    "fix_verifier",
    route_after_verification,
    {
        "rollback": "rollback",
        "end": END
    }
)

builder.add_edge(
    "rollback",
    END
)


# ==========================================
# STEP 5: ADD CHECKPOINTING
# ==========================================

# Preserves workflow state when human approval is required.
memory = MemorySaver()


# ==========================================
# STEP 6: COMPILE WORKFLOW
# ==========================================

failure_graph = builder.compile(
    checkpointer=memory
)

print("TestPilot AI repair graph compiled successfully.")
