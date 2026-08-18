""" where you handle business logic in your app. DO NOT add business logic to your endpoints. """



from ticket_api.data import TICKETS



def list_tickets() -> list[dict]:
    """ returns all tickets """

    return TICKETS

def find_ticket_by_id(ticket_id: str) -> dict | None:
    """ returns a single ricket matching the given id. returns None if no matching id is found. """

    for ticket in TICKETS:
        if ticket["id"] == ticket_id:
            return ticket
    
    # could raise an exception instead of returning None
    return None

def find_tickets_by_priority(ticket_priority: str) -> list[dict]:
    """ find all tickets with the matching priority. empty list if none found. """

    results = []
    for ticket in TICKETS:
        if ticket["priority"] == ticket_priority:
            results.append(ticket)

    return results

def create_ticket(ticket: dict):

    # simulate DB creating ticket ID
    ticket["id"] = f"TKT-{len(TICKETS) + 1}"

    # simulate save to DB
    TICKETS.append(ticket)

    # return ticket with new ID
    return ticket

def update_ticket(id: str, ticket: dict):

    for t in TICKETS:
        if t["id"] == id:

            # updating ticket values in the list
            t["tenant"] = ticket["tenant"]
            t["title"] = ticket["title"]
            t["priority"] = ticket["priority"]
            t["status"] = ticket["status"]

    # return ticket with new values
    return ticket

def delete_ticket(id: str):

    for t in TICKETS:
        if t["id"] == id:
            TICKETS.remove(t)
            return True         # return true if delete was successful
    return False                # return false if it coudln't be deleted