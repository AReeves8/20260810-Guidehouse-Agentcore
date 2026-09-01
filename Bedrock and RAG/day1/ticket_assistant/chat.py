""" interactive chat with Bedrock model using Converse API and tool calls where necessary """

from ticket_assistant.converse import converse, text_of, usage_of, format_user_message
from ticket_assistant.tools import TOOL_CONFIG, run_tool

MAX_TOOL_REQUESTS = 5
SYSTEM_PROMPT = (
    "You are a support engineer's assistant for an e-commerce company."
    "Use your tools to check facts rather than guessing."
    "If you do not know something and no tool can tell you, say so plainly."
    "Keep answers concise."
)


def main() -> None:
    messages: list[dict] = []
    total_input_tokens = 0
    total_output_tokens = 0


    print("Ticket assistant. Type /quit to exit, /tokens for usage, and /reset to start a new conversation")

    while True:
        try: 
            prompt = input("msg> ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if not prompt:
            continue
        if prompt == "/quit":
            return
        if prompt == "/tokens":
            print(f"Total Input Tokens: {total_input_tokens}; Total Output Tokens: {total_output_tokens}")
            continue
        if prompt == "/reset":
            messages = []
            total_input_tokens = 0
            total_output_tokens = 0
            continue

        # add user's new message to maintained list
        messages.append(format_user_message(prompt))

        for _ in range(MAX_TOOL_REQUESTS):
            response = converse(messages, system=SYSTEM_PROMPT, tool_config=TOOL_CONFIG)
            usage = usage_of(response)

            # track token usage
            total_output_tokens += usage["output_tokens"]
            total_input_tokens += usage["input_tokens"]

            # add our assistant response to maintained message list
            assistant_message = response["output"]["message"]
            messages.append(assistant_message)

            # check if the response calls for a tool - breaking out of loop if not
            if response["stopReason"] != "tool_use":
                print(f"bot> {text_of(response)}")
                break

            # handle the tool call(s) that the model asked for
            tool_uses = [bot["toolUse"] for bot in assistant_message["content"] if "toolUse" in bot]
            messages.append(
                {
                    "role": "user", 
                    "content": [run_tool(tool) for tool in tool_uses]
                }
            )
                
        else:
            print("bot> (Gave up after 5 tool calls)\n")


if __name__ == "__main__":
    main()