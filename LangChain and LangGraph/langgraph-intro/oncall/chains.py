
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda

from .llm import get_chat_model
from .schemas import Triage, StatusUpdate, IncidentBrief

from operator import itemgetter


# system prompts for invoking our models

TRIAGE_PROMPT = """ You are the first-pass triage system step in an on-call rotation. 

You receive monitoring alerts and assess them. you are not fixing anything and you are not notifying anyone. 
Your job is to provide an assessment that a humman will read before deciding what to do.

Rules:
    - Judge only from the alert text. Do not assume any facts that are not stated.
    - "Customer-facing" means someone outside the company would notice, not that a service is important internally.
    - If the alert text does not point at a cause, do not invent one.
"""

STATUS_PROMPT = """ You write public status-page updates for a software company. 

Your reader is a customer who wants to know if the service they are trying to use or action they are trying to perform 
is broken and if it is being worked on. You are not writing to an engineer, only to customers who do not need to know internal 
business information.

Rules:
    - Never name an internal service, host, queue, database, deployment id, etc.
    - Never state a cause, not even a likely one.
    - Never give an ETA on when something will be fixed.
    - Describe the impact in terms of what the customer cannot do right now.
"""


def build_triage_chain() -> Runnable:

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", TRIAGE_PROMPT), 
            ("human", "Alert:\n{alert}")
        ]
    )

    # making sure the model (ai) responds in a format defined by our model (pydantic)
    structured_model = get_chat_model().with_structured_output(Triage)

    return prompt | structured_model


def build_status_update_chain() -> Runnable:

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", STATUS_PROMPT), 
            ("human", "Alert:\n{alert}")
        ]
    )

    # making sure the model (ai) responds in a format defined by our model (pydantic)
    structured_model = get_chat_model(temperature=0.4).with_structured_output(StatusUpdate)

    return prompt | structured_model


def build_incident_brief_chain() -> Runnable:

    # running both chains at the same time, in parallel
    fan_out = RunnableParallel(
        alert=itemgetter("alert"),      # used to grab the value for a given key out of the chain
        triage=build_triage_chain(),
        status_update=build_status_update_chain()
    )

    # a runnable for creating IncidentBrief objects 
    merge = RunnableLambda(lambda parts: IncidentBrief.model_validate(parts))

    # if the chain cannot create the IncidentBrief object, then retry automatically
    return (fan_out | merge).with_retry(stop_after_attempt=3)


if __name__ == "__main__":
    from .fixtures import ALERTS


    chain = build_incident_brief_chain()
    alerts = [{"alert": a} for a in ALERTS]

    briefs: list[IncidentBrief] = chain.batch(alerts, config={"max_concurrency": 3})

    for i, brief in enumerate(briefs):
        print(f"\n=== BRIEF {i+1} ===")
        print(f"[{brief.triage.severity}] - {brief.triage.service}")
        print(f"customer-facing? {brief.triage.customer_facing}")
        print(f"cause?           {brief.triage.suspected_cause}")
        print(f"\nHeadline:        {brief.status_update.headline}")
        print(f"Body:            {brief.status_update.body}")