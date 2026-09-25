import os 
from bedrock_agentcore.memory import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole
from bedrock_agentcore.memory.models import MemoryRecord
from config import AWS_REGION

def memory_id() -> str | None:
    """ go out and find the Memory ID from env
    
        The agentcore CLI will inject env vars
            MEMORY_<NAME>_ID
    """

    # grab the ID from the env - would fail if you had multiple memories since we aren't searching by name
    for key, value in os.environ.items():
        if key.startswith("MEMORY_") and key.endswith("_ID"):
            return value
    return None

def get_manager() -> MemorySessionManager | None:
    """ Manages connections and sessions to memory stores """

    id = memory_id()
    if id is None:
        return None
    return MemorySessionManager(
        memory_id=id, 
        region_name=AWS_REGION
    )

def load_history(manager: MemorySessionManager, actor_id: str, session_id: str, k: int = 10) -> list:
    """ pull the last K turns of messages out of the short-term memory """
    
    output = []
    for turn in manager.get_last_k_turns(actor_id=actor_id, session_id=session_id, k=k):
        for message in turn: 

            # extract content and role from messages
            msg_dict = dict(message)
            text = (msg_dict.get("content") or {}).get("text", "")
            role = "user" if msg_dict.get("role") == "USER" else "assistant"

            # save to list, formatted as tuple
            if text:
                output.append((role,text))

    return output


def save_turn(manager: MemorySessionManager, actor_id: str, sesion_id: str, user_text: str, reply_text: str) -> None:
    """ use the manager to save a turn of messages to the short-term memory """

    manager.add_turns(
        actor_id=actor_id, 
        session_id=sesion_id,
        messages=[
            ConversationalMessage(user_text, MessageRole.USER),
            ConversationalMessage(reply_text, MessageRole.ASSISTANT),
        ]
    )


def recall(manager: MemorySessionManager, actor_id: str, session_id: str) -> list[MemoryRecord]:
    """ manually reach out to an actor's long-term memories across various strategies """

    output = []
    namespaces = [
        f"/users/{actor_id}/facts",                 # SEMANTIC
        f"/users/{actor_id}/preferences",           # USER_PREFERENCE
        f"/summaries/{actor_id}/{session_id}",      # SUMMARIZATION
        f"/episodes/{actor_id}/{session_id}",       # EPISODIC
    ]

    for namespace in namespaces:
        try: 
            records = manager.list_long_term_memory_records(namespace=namespace)
            output.append(records)
        except Exception:
            # exception should occur on an empty namespace - which is normal so just continue to next namespace
            continue

    return output