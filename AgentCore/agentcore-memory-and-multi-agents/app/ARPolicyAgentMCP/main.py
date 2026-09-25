from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ARPolicyAgentMCP", host="0.0.0.0", stateless_http=True)

_LIMITS = {
    "lodging": (300, "per night"),
    "meals": (75, "per day"),
    "airfare": (850, "round trip, domestic"),
    "rideshare": (60, "per trip"),
}

_QUALIFYING_REASONS = ("conference", "block rate", "sold out", "safety", "client site")


@mcp.tool()
def get_policy_limit(category: str) -> str:
    """Return the spending limit for an expense category.

    Valid categories: lodging, meals, airfare, rideshare.
    """

    key = category.strip().lower()
    if key not in _LIMITS:
        return f"Unknown category '{category}'. Valid categories: {', '.join(sorted(_LIMITS))}."
    
    amount, unit = _LIMITS[key]
    return f"The {key} limit is ${amount} {unit}."


@mcp.tool()
def check_exception_eligibility(category: str, amount: float, reason: str) -> str:
    """Decide whether an over-limit expense qualifies for a policy exception.

    Pass the category, the amount actually spent, and the traveller's stated
    reason. Returns whether an exception is available and what it requires.
    """
    key = category.strip().lower()
    if key not in _LIMITS:
        return f"Unknown category '{category}'. Valid categories: {', '.join(sorted(_LIMITS))}."

    limit = _LIMITS[key][0]
    if amount <= limit:
        return f"${amount:.2f} is within the ${limit} {key} limit. No exception needed."

    matched = [reason_text for reason_text in _QUALIFYING_REASONS if reason_text in reason.lower()]
    if matched:
        return (
            f"${amount:.2f} exceeds the ${limit} {key} limit, but '{matched[0]}' is a "
            f"qualifying reason. Eligible for an exception -- requires manager approval."
        )
    return (
        f"${amount:.2f} exceeds the ${limit} {key} limit and '{reason}' is not a "
        f"qualifying reason. Not eligible for an automatic exception."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
