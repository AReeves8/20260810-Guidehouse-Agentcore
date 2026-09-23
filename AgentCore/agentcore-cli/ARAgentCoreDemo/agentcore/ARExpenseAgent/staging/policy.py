""" Company Travel Policies for Expenses """

# nightly/daily rates for typical expenses
POLICY_LIMITS = {
    "lodging": 300,
    "meals": 100,
    "airfare": 700,
    "rideshare": 100,
    "conference": 2000
}

POLICIES_NEEDING_APPROVAL = { "conference" }


# track requests for exceptions to the policies
_EXCEPTION_SEQ = {"n": 2742}

def next_exception_id() -> str:
    """ generate the next execption id in the sequence """

    _EXCEPTION_SEQ["n"] += 1
    return f"EXC-{_EXCEPTION_SEQ["n"]}"