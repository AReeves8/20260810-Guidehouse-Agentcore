""" Company Travel Policies for Expenses """

# nightly/daily rates for typical expenses
POLICY_LIMITS = {
    "lodging": 180,
    "meals": 75,
    "airfare": 650,
    "rideshare": 60,
    "conference": 1200
}

POLICIES_NEEDING_APPROVAL = { "conference" }


# track requests for exceptions to the policies
_EXCEPTION_SEQ = {"n": 2742}

def next_exception_id() -> str:
    """ generate the next execption id in the sequence """

    _EXCEPTION_SEQ["n"] += 1
    return f"EXC-{_EXCEPTION_SEQ["n"]}"