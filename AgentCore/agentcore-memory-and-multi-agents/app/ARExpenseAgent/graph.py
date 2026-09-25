

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage, SystemMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from model.load import get_model
from prompts import SYSTEM_PROMPT

MAX_TOOL_TURNS = 3

# graph state
class ExpenseState(TypedDict):

    messages: Annotated[list[AnyMessage], add_messages]
    tool_turns: int

# nodes

# wrapping assistant node in a function that takes in the desired tools
def _make_assistant_node(tools): 
    def _assistant_node(state: ExpenseState) -> dict:

        turns = state.get("tool_turns", 0)
        model = get_model()

        # only going to tell the model about the tools if we are under the tool use limit
        if turns < MAX_TOOL_TURNS:
            runnable = model.bind_tools(tools)
        else :
            runnable = model

        conversation = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]

        reply : BaseMessage = runnable.invoke(conversation)
        return {"messages": [reply]}

    return _assistant_node

def _make_tools_node(tools):
    async def _tools(state: ExpenseState) -> dict:

        _tool_node = ToolNode(tools)

        # tools in the MCP server (aka Gateway) require an API request - which is an async operation
        result = await _tool_node.ainvoke(state)
        return {
            "messages": result["messages"],
            "tool_turns": state.get("tool_turns", 0) + 1
        }

    return _tools

def _route_after_assistant(state: ExpenseState) -> str:

    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END

def build_graph(checkpointer=None, tools=None):

    graph = StateGraph(ExpenseState)
    graph.add_node("assistant", _make_assistant_node(tools))
    graph.add_node("tools", _make_tools_node(tools))

    graph.add_edge(START, "assistant")

    graph.add_conditional_edges(
        "assistant",
        _route_after_assistant,
        {
            "tools": "tools",
            END: END
        }
    )

    graph.add_edge("tools", "assistant")

    return graph.compile(checkpointer=checkpointer, name="expense-copilot")