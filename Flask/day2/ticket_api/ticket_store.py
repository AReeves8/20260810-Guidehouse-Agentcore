""" where you handle business logic in your app. DO NOT add business logic to your endpoints. """



from ticket_api.data import TICKETS
from ticket_api.models import Ticket, CreateTicketDto, UpdateTicketDto, Priority
from pydantic import TypeAdapter

priorityAdapter = TypeAdapter(Priority)


def _tickets() -> list[Ticket]:
    return [Ticket.model_validate(row) for row in TICKETS]


def list_tickets() -> list[Ticket]:
    """ returns all tickets """

    return _tickets()

def find_ticket_by_id(ticket_id: str) -> Ticket | None:
    """ returns a single ricket matching the given id. returns None if no matching id is found. """
    tickets = _tickets()
    for ticket in tickets:
        if ticket.id == ticket_id:
            return ticket
    
    # could raise an exception instead of returning None
    return None

def find_tickets_by_priority(ticket_priority: str) -> list[Ticket]:
    """ find all tickets with the matching priority. empty list if none found. """

    # check that the priority given is a valid value
    # if the type cannot be converted correctly, a ValidationError should be raised
    valid_priority = priorityAdapter.validate_python(ticket_priority)
   
    results = []
    tickets = _tickets()
    for ticket in tickets:
        if ticket.priority == valid_priority:
            results.append(ticket)

    return results

def create_ticket(ticket: dict):

    valid_ticket = CreateTicketDto.model_validate(ticket)

    # simulate DB creating ticket ID
    id = f"TKT-{len(_tickets()) + 1}"

    # ** spreads out the properties that are in the given object
    new_ticket = Ticket(id=id, **valid_ticket.model_dump())

    # simulate save to DB
    TICKETS.append(new_ticket.model_dump())

    # return ticket with new ID
    return new_ticket

def update_ticket(id: str, ticket: dict) -> Ticket:

    valid_ticket = UpdateTicketDto.model_validate(ticket)
    tickets = _tickets()
    updated_ticket = Ticket(id=id, **valid_ticket.model_dump())
    for t in tickets:
        if t.id == id:

            # removing existing ticket
            TICKETS.remove(t.model_dump())

            # updating ticket values in the list
            t.tenant = valid_ticket.tenant
            t.title = valid_ticket.title
            t.priority = valid_ticket.priority
            t.status = valid_ticket.status

            # adding ticket back with new values
            TICKETS.append(t.model_dump())
            updated_ticket = t

    # return ticket with new values
    return updated_ticket

def delete_ticket(id: str):

    tickets = _tickets()
    for t in tickets:
        if t.id == id:
            TICKETS.remove(t.model_dump())
            return True         # return true if delete was successful
    return False                # return false if it coudln't be deleted
