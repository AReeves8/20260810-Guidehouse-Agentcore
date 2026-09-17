""" State that will be used by every node in our graph """


from typing import TypedDict, Annotated, NotRequired
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
import operator

from oncall.schemas import Triage, Diagnosis, StatusUpdate, RemediationPlan

class IncidentState(TypedDict):

    # input
    alert: str
    messages: Annotated[list[AnyMessage], add_messages]

    # what the model has learned
    triage: NotRequired[Triage | None]
    evidence: Annotated[list[str], operator.add]
    tool_attempts: int

    # retrieval 
    search_query: NotRequired[str]
    retrieval_attempts: int
    diagnosis: NotRequired[Diagnosis | None]

    # plan
    plan: NotRequired[RemediationPlan | None] 
    approval: NotRequired[str | None]
    approval_note: NotRequired[str | None]

    # output
    status_update: NotRequired[StatusUpdate | None]
    outcome: NotRequired[str | None]

    # unnecessary in production - observability
    trace: Annotated[list[str], operator.add]