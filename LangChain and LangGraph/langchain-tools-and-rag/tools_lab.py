from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from oncall.llm import get_chat_model
from oncall.tools import ALL_TOOLS, TOOL_REGISTRY
from oncall.fixtures import ALERTS



# bind the tools to the model
model = get_chat_model()
bound_model = model.bind_tools(ALL_TOOLS)

SYSTEM_PROMPT = (
    "You are an on-call assistant. use the tools to gatehr facts before you answer. "
    "Do not speculate on the cause of an issue you have not checked.\n"
    "When you have enough information, you MUST write your final answer as ordinary text. "
    "Do not stop after using a tools without writing an answer."
)

messages = [
    SystemMessage(SYSTEM_PROMPT),
    HumanMessage(f"{ALERTS[0]}\n\nWhat is going on and what changed recently?")
]

first_response = bound_model.invoke(messages)

print("=== BREAKING DOWN FIRST RESPONSE ===")
print(f"Text: {first_response.text}")
print(f"Tools: {first_response.tool_calls}")
print(f"Stop: {first_response.response_metadata.get("stopReason")}")

messages.append(first_response)

# calling any tools the model asked for and adding the results to the conversation
for call in first_response.tool_calls:
    tool = TOOL_REGISTRY[call["name"]]
    result = tool.invoke(call["args"])
    messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))


second_response = bound_model.invoke(messages)

print("\n=== BREAKING DOWN SECOND RESPONSE ===")
print(f"Text: {second_response.text}")
print(f"Tools: {second_response.tool_calls}")
print(f"Stop: {second_response.response_metadata.get("stopReason")}")


# ...need to handle ANOTHER tool call... instead, let's put this into a loop

MAX_STEPS = 5

messages = [
    SystemMessage(SYSTEM_PROMPT),
    HumanMessage(f"{ALERTS[0]}\n\nWhat is going on and what changed recently?")
]



# LangChain makes using tools easier.. but we still need to manage them
# LangGraph can start to maange this tool loop for us
for step in range(0, MAX_STEPS):

    print("\n================================================")
    ai = bound_model.invoke(messages)
    messages.append(ai)

    if ai.tool_calls:
        print(f"Tools: {ai.tool_calls}")
        for call in ai.tool_calls:
            tool = TOOL_REGISTRY[call["name"]]
            result = tool.invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

        # skip everything else and go to next loop iteration
        continue

    text = ai.text
    stop_reason = ai.response_metadata.get("stopReason")
    print(f"Text: {text}")
    print(f"Stop: {stop_reason}")

    if stop_reason == "end_turn":
        break