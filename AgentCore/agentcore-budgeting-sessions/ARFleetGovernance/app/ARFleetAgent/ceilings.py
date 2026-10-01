
from config import MAX_TOOL_CALLS, MAX_SESSION_TOKENS



class CeilingExceededError(RuntimeError):
    """ Raised when a session hits a resource limit """


class SessionBudget:
    """ Per-session counters for tool calls and tokens """

    def __init__(self) -> None:
        self._tool_calls = {}
        self._tokens = {}

    def record_tool_call(self, session_id) -> int:
        count = self._tool_calls.get(session_id, 0) + 1
        self._tool_calls[session_id] = count

        if count > MAX_TOOL_CALLS:
            raise CeilingExceededError(
                f"tool-call ceiling reached ({count} > {MAX_TOOL_CALLS}) for session {session_id}"
            )

        return count

    def record_tokens(self, session_id, tokens: int) -> int:
        total = self._tokens.get(session_id, 0) + tokens
        self._tokens[session_id] = total

        if total > MAX_SESSION_TOKENS:
            raise CeilingExceededError(
                f"token ceiling reached ({total} > {MAX_SESSION_TOKENS}) for session {session_id}"
            )

        return total

    def usage(self, session_id):
        return {
            "tool_calls_usage": self._tool_calls.get(session_id, 0),
            "tool_calls_ceiling": MAX_TOOL_CALLS,
            "tokens_usage": self._tokens.get(session_id, 0),
            "tokens_ceiling": MAX_SESSION_TOKENS,
        }


def tokens_from_message(message):
    """ Pull token usage out of a message """
    
    total = 0
    
    # current versions should use "usage_metadata" but older versions might use "response_metadata"
    usage = getattr(message, "usage_metadata", None)
    if isinstance(usage, dict):

        # track ALL tokens at once, rather than splitting input/output tokens
        total += usage.get("total_tokens") or 0

    return total


def make_budget_hook(budget: SessionBudget, session_id):
    """ post_model_hook for create_react_agent """

    def hook(state):
        messages = (state or {}).get("messages") or []
        latest_msg = messages[-1]

        # tracking tokens from each message
        budget.record_tokens(session_id, tokens_from_message(latest_msg))

        # tracking tool calls from each message
        for _ in getattr(latest_msg, "tool_calls", None) or []:
            budget.record_tool_call(session_id)

        return {}

    return hook

