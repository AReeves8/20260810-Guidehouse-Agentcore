
from oncall.graph.graph import build_graph
from oncall.fixtures import ALERTS
from oncall.graph.state import IncidentState

if __name__ == "__main__":

    app = build_graph()

    alert = ALERTS[0]

    initial_state: IncidentState = {
        "alert": alert,
        "messages": [],
        "evidence": [],
        "trace": [],
        "retrieval_attempts": 0,
        "tool_attempts": 0
    }


    for chunk in app.stream(initial_state, stream_mode="updates"):
        print("=================================")
        print(chunk)
        print()