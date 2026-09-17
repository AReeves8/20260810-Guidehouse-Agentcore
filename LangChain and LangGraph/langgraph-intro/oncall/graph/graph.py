
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from oncall.schemas import Triage, Diagnosis, RemediationPlan, StatusUpdate
from oncall.graph.state import IncidentState
from oncall.graph.nodes.investigation import triage_node, investigate_node, tools_node, route_after_investigation
from oncall.graph.nodes.diagnosis import diagnose_node, reframe_node, retrieve_node, route_after_diagnose
from oncall.graph.nodes.remediation import human_approval_node, plan_remediation_node, route_after_approval, route_after_plan
from oncall.graph.nodes.resolution import close_node, escalate_node, execute_node, write_status_node


# using the serializer to convert pydantic models to and from JSON
SERDE = JsonPlusSerializer(allowed_msgpack_modules=[Triage, Diagnosis, RemediationPlan, StatusUpdate])


def build_graph():

    graph = StateGraph(IncidentState)

    # --- NODES ---
    graph.add_node("triage", triage_node)
    graph.add_node("investigate", investigate_node)
    graph.add_node("tools", tools_node)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("diagnose", diagnose_node)
    graph.add_node("reframe", reframe_node)

    graph.add_node("plan_remediation", plan_remediation_node)
    graph.add_node("human_approval", human_approval_node)
    
    graph.add_node("escalate", escalate_node)
    graph.add_node("execute", execute_node)
    graph.add_node("write_status", write_status_node)
    graph.add_node("close", close_node)


    # --- EDGES ---
    graph.add_edge(START, "triage")
    graph.add_edge("triage", "investigate")

    graph.add_conditional_edges(
        "investigate", 
        route_after_investigation,
        {"tools": "tools", "retrieve": "retrieve"}
    )

    graph.add_edge("tools", "investigate")
    graph.add_edge("retrieve", "diagnose")

    graph.add_conditional_edges(
        "diagnose",
        route_after_diagnose,
        {
            "plan_remediation": "plan_remediation",
            "reframe": "reframe",
            "escalate": "escalate"
        }
    )

    graph.add_edge("reframe", "retrieve")

    graph.add_conditional_edges(
        "plan_remediation",
        route_after_plan,
        {
            "human_approval": "human_approval",
            "escalate": "escalate",
            "execute": "execute",
            "write_status": "write_status"
        }
    )

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "escalate": "escalate",
            "execute": "execute"
        }
    )

    graph.add_edge("execute", "write_status")
    graph.add_edge("escalate", "write_status")
    graph.add_edge("write_status", "close")
    graph.add_edge("close", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    print(app.get_graph().draw_mermaid())