from langchain.tools import tool

from policy import POLICIES_NEEDING_APPROVAL, POLICY_LIMITS, next_exception_id

@tool
def get_expense_policy(category: str) -> str:
    """ Look up the spending limit for one expense category. 

        Call this BEFORE telling a traveller hether something is allowed. Never state a limit from memory. 
        Always look up values. The numbers change per fiscal quarter so your training data may be incorrect. 

        Valid categories: lodging, meals, airfare, rideshare, conference 
    """

    key = category.strip().lower()
    limit = POLICY_LIMITS.get(key)

    if limit is None:
        known_categories = ", ".join(sorted(POLICY_LIMITS))
        return f"No category named '{category}. Known categories: {known_categories}"

    note = ""
    if key in POLICIES_NEEDING_APPROVAL:
        note = f"This category requires manager approval no matter what."

    return f"The limit for {key} is ${limit}. {note}"

@tool
def file_exception_request(category: str, amount_usd: float, reason: str) -> str:
    """File a policy-exception request for an over-limit expense.

    Call this ONLY after the traveller has explicitly agreed to file one. Do
    not file speculatively and do not file to "check" anything -- this creates
    a real request that a manager has to act on.

    `reason` must be the traveller's own justification. If they have not given
    one, ask for it first rather than inventing one.
    """

    key = category.strip().lower()
    limit = POLICY_LIMITS.get(key)

    if limit is None:
        return f"Cannot file: '{category}' is not a real expense category."

    if not reason or not reason.strip():
        return "Cannot file: a written justification from the traveller is required."

    request_id = next_exception_id()
    overage = round(amount_usd - limit, 2)
    return (
        f"Filed {request_id}: {key} at ${amount_usd:.2f} against a ${limit} limit "
        f"(${overage:.2f} over). Reason on file: {reason.strip()} "
        f"Status: PENDING_MANAGER_REVIEW."
    )

TOOLS = [get_expense_policy, file_exception_request]