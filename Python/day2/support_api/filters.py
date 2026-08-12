# comprehensions 
#   - building a new collection in one line by looping over an iterable and (optionally) filtering it

def urgent_ids(tickets):
    return [t["id"] for t in tickets if t["priority"] == "urgent"]

    # does the same thing, just longer:
    # result = []
    # for t in tickets:
    #     if t["priority"] == "urgent" :
    #         result.append(t["id"])
    # return result

# sets - no duplicates allowed - automatically filters out dupes
#   - set comprehension uses curly braces instead of square brackets
def tenants_registered(tickets):
    return {t["tenant"] for t in tickets}

# * - not a parm, but creates a marker for every param after it
#       - every param listed after must be passed by keyword

# also, can assign default values to params

def filter_tickets(tickets, *, tenant = None, priority = None, status = None):
    result = tickets

    # filter based on which params were given

    if tenant is not None: 
        result = [t for t in result if t["tenant"] == tenant]
    if priority is not None: 
        result = [t for t in result if t["priority"] == priority]
    if status is not None: 
        result = [t for t in result if t["status"] == status]

    return result


def count_by_priority(tickets):
    tally = {}      # empty dict

    for t in tickets:
        # second param of get() is a default value to return if the given key doesn't exist
        tally[t["priority"]] = tally.get(t["priority"], 0) + 1

    return tally