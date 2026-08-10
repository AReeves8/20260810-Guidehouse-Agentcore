SAMPLE_TICKETS = [
    {"id": "TKT-1", "tenant": "acme-corp",  "title": "Login fails on SSO",   "priority": "urgent", "status": "open"},
    {"id": "TKT-2", "tenant": "globex",     "title": "CSV export broken",    "priority": "low",    "status": "resolved"},
    {"id": "TKT-3", "tenant": "acme-corp",  "title": "Double billing issue", "priority": "urgent", "status": "open"},
    {"id": "TKT-4", "tenant": "initech",    "title": "Slow dashboard load",  "priority": "medium", "status": "ack"},
    {"id": "TKT-5", "tenant": "globex",     "title": "Password reset email", "priority": "high",   "status": "escalated"},
    {"id": "TKT-6", "tenant": "acme-corp",  "title": "Typo on invoice PDF",  "priority": "low",    "status": "open"},
]


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

# lists are mutable and the default value is given at function definition, not each time it is called
def add_tags_broken(tags = []):

    # will add the new value to the list EVERY time this function is called
    tags.append("new value")
    return tags

# fix: just check if it has no value to begin with
def add_tags_fixed(tags = None):
    if tags is None:
        tags = []
    tags.append("new value")
    return tags


# def - used to define functions
def main():
    print("--- Urgent Ticket IDs ---")
    print(urgent_ids(SAMPLE_TICKETS))

    print("\n--- Tenants that Submitted Tickets ---")
    print(tenants_registered(SAMPLE_TICKETS))

    print("\n--- Filtered Tickets ---")
    # not enough to just pass in "acme-corp" since we used the * marker in the function definition
    print(filter_tickets(SAMPLE_TICKETS, priority=""))

    print("\n--- Tickets by Priority ---")
    print(count_by_priority(SAMPLE_TICKETS))

    print("\n--- Checking Default Params ---")
    print(add_tags_broken())
    print(add_tags_broken())
    print(add_tags_broken())
    print(add_tags_fixed())
    print(add_tags_fixed())
    print(add_tags_fixed())



# check the context this file is running in 
#   if this file is running on its own, then __name__ will be __main__
if __name__ == "__main__" :
    main()