from collections import OrderedDict
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, create_react_agent
from mcp.shared.exceptions import McpError
from langchain.tools import tool
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from fleet_client import fleet_tools

from config import MAX_GRAPH_STEPS
from ceilings import SessionBudget, CeilingExceededError, make_budget_hook

LangchainInstrumentor().instrument()

app = BedrockAgentCoreApp()
log = app.logger

_llm = None

def get_or_create_model():
    global _llm
    if _llm is None:
        _llm = load_model()
    return _llm


DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant. Use tools when appropriate.

"""


# Define a simple function tool
@tool
def add_numbers(a: int, b: int) -> int:
    """Return the sum of two numbers"""
    return a + b


def _gateway_error_message(e: McpError) -> str:
    """Return gateway failures (e.g. policy denials) to the model as a tool result"""

    log.warning(f"Gateway tool call failed: {e}")
    return f"Tool call failed: {e}. Do not retry this tool; explain the limitation to the user."


# Define a collection of tools used by the model
tools = [add_numbers]

# Module-level checkpointer preserves conversation history across invocations.
# InMemorySaver keeps every thread_id (= session_id) checkpoint in memory
# forever, so we bound it to 128 active threads with LRU eviction (the
# least-recently-used thread is deleted and its history reset) to keep a
# long-running process from growing without limit. For durable history, swap in
# a persistent checkpointer (e.g. SqliteSaver/AsyncSqliteSaver with a file path).
_CHECKPOINT_LIMIT = 128
_checkpointer = InMemorySaver()
_thread_ids = OrderedDict()
_budget = SessionBudget()

def touch_thread(thread_id):
    if thread_id in _thread_ids:
        _thread_ids.move_to_end(thread_id)
        return
    while len(_thread_ids) >= _CHECKPOINT_LIMIT:
        evicted, _ = _thread_ids.popitem(last=False)
        _checkpointer.delete_thread(evicted)
    _thread_ids[thread_id] = True



@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Agent.....")

    # Pull everything that does NOT need the gateway out first, so the
    # session below is held open for as short a time as possible.
    prompt = payload.get("prompt", "What can you help me with?")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    session_id = getattr(context, "session_id", "default-session")
    touch_thread(session_id)
    log.info(f"Agent input: {prompt}")


    try: 
        # The gateway tools borrow a live MCP session. They stop working the
        # moment it closes, so the graph is both BUILT and INVOKED in here.
        async with fleet_tools() as gateway_tools:
            log.info(f"Gateway tools: {[t.name for t in gateway_tools]}")

            graph = create_react_agent(
                get_or_create_model(),
                tools=ToolNode(
                    gateway_tools + tools, 
                    handle_tool_errors=_gateway_error_message
                ),
                prompt=DEFAULT_SYSTEM_PROMPT,
                checkpointer=_checkpointer,
                post_model_hook=make_budget_hook(_budget, session_id)
            )

            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=prompt)]},
                config={
                    "configurable": {
                        "thread_id": session_id
                    },
                    "recursion_limit": MAX_GRAPH_STEPS
                },
            )
    except Exception as e:

        # every exception inside "async with" gets added to an ExceptionGroup
        # a single ExceptionGroup can contain other ExceptionGroups. 
        # go through each exception and ExceptionGroup until we've found the one we're looking for
        stack = [e]
        while stack:
            current = stack.pop()
            if isinstance(current, CeilingExceededError):
                log.warning(f"ceiling hit: {current} | {_budget.usage(session_id)}")
                return {
                    "result": f"I stopped before finishing: {current}",
                    "stopped": "ceiling_exceeded"
                }
            stack.extend(getattr(current, "exceptions", ()))

        # handle generic case
        return {
            "result": f"I stopped before finishing: {e}",
            "stopped": "exception"
        }

    # Safe out here -- `result` is plain data, nothing calls the gateway.
    output = result["messages"][-1].content
    log.info(f"Agent output: {output}")
    return {"result": output}


if __name__ == "__main__":
    app.run()
