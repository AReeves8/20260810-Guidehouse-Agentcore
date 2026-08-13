"""
upgrading filters.py to work with strict type checking

"""

from support_api.models import Ticket, Priority, Status, Category
from support_api.decorators import shout

def urgent_ids(tickets: list[Ticket]) -> list[str]:
    return [t.id for t in tickets if t.priority == "urgent"]

def tenants_registered(tickets: list[Ticket]) -> set[str]:
    return {t.tenant for t in tickets}

@shout
def filter_tickets(
        tickets: list[Ticket], 
        *, 
        tenant : str | None = None, 
        priority: Priority | None = None, 
        status: Status | None = None,
        category: Category | None = None):

    print(f"\n--- FUNCTION NAME: {filter_tickets.__name__} ---")

    result = tickets

    # filter based on which params were given
    if tenant is not None: 
        result = [t for t in result if t.tenant == tenant]
    if priority is not None: 
        result = [t for t in result if t.priority == priority]
    if status is not None: 
        result = [t for t in result if t.status == status]
    if category is not None: 
        result = [t for t in result if t.category == category]

    return result

def count_by_priority(tickets: list[Ticket]) -> dict[str, int]:
    tally: dict[str, int] = {}      # empty dict

    for t in tickets:
        # second param of get() is a default value to return if the given key doesn't exist
        tally[t.priority] = tally.get(t.priority, 0) + 1

    return tally