from collections import OrderedDict
from typing import Any, cast

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from graph import build_graph
from graph import ExpenseState

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
_graph = build_graph(checkpointer=_checkpointer)
_thread_ids = OrderedDict()


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

    # make sure that our graph threads line up with our session ids
    touch_thread(session_id)    

    result = _graph.invoke(
        cast("ExpenseState",
        {
            "messages": [HumanMessage(content=prompt)],
            "tool_turns": 0
        }),
        config={ "configurable": { "thread_id": session_id } }
    )

    log.info("[session=%s] answered with %d messages", session_id, len(result["messages"]))
    answer = result["messages"][-1]

    # formatting the HTTP response
    return {
        "result": answer,
        "session_id": session_id
    }


if __name__ == "__main__":

    # what starts up the server on port 8080
    app.run()
