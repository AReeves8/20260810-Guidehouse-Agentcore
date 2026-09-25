from collections import OrderedDict
from typing import Any, cast

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from graph import build_graph
from graph import ExpenseState
from gateway import gateway_tools
from memory import get_manager, load_history, save_turn, recall
from tools import TOOLS
from delegate import ask_policy_agent

app = BedrockAgentCoreApp()
log = app.logger

# Module-level checkpointer preserves conversation history across invocations.
# InMemorySaver keeps every thread_id (= session_id) checkpoint in memory
# forever, so we bound it to 64 active threads with LRU eviction (the
# least-recently-used thread is deleted and its history reset) to keep a
# long-running process from growing without limit. For durable history, swap in
# a persistent checkpointer (e.g. SqliteSaver/AsyncSqliteSaver with a file path).
_CHECKPOINT_LIMIT = 64
_checkpointer = InMemorySaver()
_thread_ids = OrderedDict()
_memory_manager = get_manager()


def touch_thread(thread_id):
    if thread_id in _thread_ids:
        _thread_ids.move_to_end(thread_id)
        return
    while len(_thread_ids) >= _CHECKPOINT_LIMIT:
        evicted, _ = _thread_ids.popitem(last=False)
        _checkpointer.delete_thread(evicted)
    _thread_ids[thread_id] = True



@app.entrypoint
async def invoke(payload: dict[str, Any], context):
    """ handle POST /invocations
            expect body to be: { "prompt" : "some user prompt" }
    """
    # check to make sure we recieved a non-empty string as our prompt
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return {
            "error": "Expected a non-empty string field 'prompt'."
        }

    # grab the session_id from the request context
    # *** expecting the client to provide a session_id ***
    #       
    # the AgentCore SDK will construct the context based on the HTTP Request. 
    #   the value for the header 'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id' will be mapped to context's session_id
    session_id = getattr(context, "session_id", None)    

    # grab the actor ID from the body of the request
    actor_id = payload.get("actor_id", "default-actor-id")

    # load in the conversation history from memory
    history = load_history(_memory_manager, actor_id, str(session_id)) if _memory_manager else []
    messages = [*history, HumanMessage(content=prompt)]

    # make sure that our graph threads line up with our session ids
    touch_thread(session_id)    

    # build the graph on each invocation - so each invocation gets a fresh callout to the gateway to find the available tools
    async with gateway_tools() as remote_tools:
        log.info("gateway offered %d tools", len(remote_tools))

        graph = build_graph(checkpointer=_checkpointer, tools=TOOLS + remote_tools + [ask_policy_agent])

        # graph has an async node now so make sure we can handle that
        result = await graph.ainvoke(
            cast("ExpenseState",
            {
                "messages": messages,
                "tool_turns": 0
            }),
            config={ "configurable": { "thread_id": session_id } }
        )

    log.info("[session=%s] answered with %d messages", session_id, len(result["messages"]))
    answer = result["messages"][-1]

    if _memory_manager:
        save_turn(_memory_manager, actor_id, str(session_id), prompt, answer.content)
        memory_records = recall(manager=_memory_manager, actor_id=actor_id, session_id=str(session_id))
        log.info(memory_records)

    # formatting the HTTP response
    return {
        "result": answer,
        "session_id": session_id
    }


if __name__ == "__main__":

    # what starts up the server on port 8080
    app.run()
