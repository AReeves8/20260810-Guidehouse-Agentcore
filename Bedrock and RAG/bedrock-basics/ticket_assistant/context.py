"""  
    CONTEXT ENGINEERING
        - different strategies for maintaining conversation context
            - keep everything 
                - model has full context into everything going on. 
                - really useful for short conversations. 
            - sliding window
                - only keep the last X messages
                - control how much is being sent to the model each time
                - control failures in a predictable way
                - really good for conversations that change topics frequently or quickly
            - summarization
                - summarize old messages and keep new ones
                - details can be lost in favor of keeping key facts

        - as messsages increase
            - cost increases, 
            - latency increases, 
            - quality decreases
"""

from ticket_assistant.converse import converse, text_of, usage_of

# Strategy 1: Keep Everything
def full_history(messages: list[dict]) -> list[dict]:
    return messages


# Strategy 2: Sliding Window
def sliding_window(messages: list[dict], keep_turns: int = 3) -> list[dict]:
    """ make sure to keep user/assistant pairs - bedrock will fail if you start a conversation with the assistant side """

    keep_messages = keep_turns * 2

    # quick check if conversation has exceeded maximum length yet
    if len(messages) <= keep_messages:
        return messages

    # trim the list (start at the end of the list, count back X amount of items, split until the end of the list)
    trimmed = messages[-keep_messages:]

    # making sure we didn't split on a non-user message
    if trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]

    return trimmed


# Strategy 3: Summarization
def summarize_older(messages: list[dict], keep_turns: int = 2) -> list[dict]:

    keep_messages = keep_turns * 2
    
    # quick check if conversation has exceeded maximum length yet
    if len(messages) <= keep_messages:
        return messages

    # split messages at the cutoff 
    older, recent = messages[:-keep_messages], messages[-keep_messages:]

    summary = _summarize_conversation(older)

    # inject the summary into the conversation with a false response from model to maintain user/assistant pairs
    rebuilt = [
        {"role": "user", "content": [{"text": f"[Summary of earlier conversation]\n{summary}"}]},
        {"role": "assistant", "content": [{"text": f"Understood. Continuing from there."}]}
    ]

    # making sure we didn't split on a non-user message
    if recent and recent[0]["role"] != "user":
        recent = recent[1:]

    return rebuilt + recent

    

def _summarize_conversation(messages: list[dict]) -> str:
    """ having the model summarize the conversation """

    transcript = "".join(f"{m["role"]}: {''.join(c.get('text', '') for c in m["content"])}" for m in messages)

    response = converse(
        [{
            "role": "user", 
            "content": [{"text": f"Summarize this conversation in under 60 words preserving IDs, names, and decisions.\n\n{transcript}"}]
        }],
        system="You compress conversation history. Preserve specifics; drop pleasantries.",
        max_tokens=150,
        temperature=0.0
    )

    return text_of(response)


if __name__ == "__main__":
    from ticket_assistant.fixtures import format_conversation

    history = format_conversation()

    print("--- FULL HISTORY ---")
    response = converse(full_history(history))
    print(text_of(response))
    print(usage_of(response))


    print("\n--- SLIDING WINDOW ---")
    response = converse(sliding_window(history))
    print(text_of(response))
    print(usage_of(response))


    print("\n--- SUMMARIZE OLDER ---")
    response = converse(summarize_older(history))
    print(text_of(response))
    print(usage_of(response))

