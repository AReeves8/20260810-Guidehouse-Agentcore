""" where you handle business logic in your app. DO NOT add business logic to your endpoints. """

from pydantic import TypeAdapter
from sqlalchemy import select, text

from ticket_api.tickets.models import Ticket, CreateTicketDto, UpdateTicketDto, Priority
from ticket_api.tickets.db_models import TicketRecord, TicketComment
from ticket_api.extensions import db

priorityAdapter = TypeAdapter(Priority)


def list_tickets() -> list[Ticket]:
    """ returns all tickets """

    # stmt creates the sql query
    stmt = select(TicketRecord).order_by(TicketRecord.id)

    # running the query - return type is Result[Tuple[TicketRecord]] so you have to parse out the Tuple
    rows = db.session.execute(stmt)

    # can do rows = db.session.execute(stmt).scalars() 
    # to get a return type of ScalarResult[TicketRecord] where you won't have to parse out anything

    # return pydantic validated records
    # each row is a Tuple so grabbing the first value (the record) out of it
    return [Ticket.model_validate(row[0]) for row in rows]

    # if you did .scalars():
    # return [Ticket.model_validate(row) for row in rows]


def find_ticket_by_id(ticket_id: int) -> Ticket | None:
    """ returns a single ricket matching the given id. returns None if no matching id is found. """

    # could find by PK like this:
    # stmt = select(TicketRecord).where(TicketRecord.id == ticket_id)
    # row = db.session.execute(stmt)


    # but there's a shortcut to lookup by PK
    row = db.session.get(TicketRecord, ticket_id)

    # returning the validated record or None if the PK doesn't exist
    return Ticket.model_validate(row) if row is not None else None


def find_tickets_by_priority(ticket_priority: str) -> list[Ticket]:
    """ find all tickets with the matching priority. empty list if none found. """

    # check that the priority given is a valid value
    # if the type cannot be converted correctly, a ValidationError should be raised
    valid_priority = priorityAdapter.validate_python(ticket_priority)

    stmt = select(TicketRecord).where(TicketRecord.priority == valid_priority)
    rows = db.session.execute(stmt)
   
    return [Ticket.model_validate(row[0]) for row in rows]


def create_ticket(ticket: dict):

    valid_ticket = CreateTicketDto.model_validate(ticket)

    record = TicketRecord(**valid_ticket.model_dump())

    # add will attempt to put the record in the DB and let you know if anything fails
    db.session.add(record)

    # commit is split up into its own step. commit actually puts the record in the DB
    db.session.commit()

    return Ticket.model_validate(record)


def update_ticket(ticket_id: int, ticket: dict) -> Ticket | None:

    valid_ticket = UpdateTicketDto.model_validate(ticket)

    # find the record in the DB
    record = db.session.get(TicketRecord, ticket_id)
    if record is None:
        return None     # return none if no record found

    # update all the values
    record.tenant = valid_ticket.tenant
    record.title = valid_ticket.title
    record.priority = valid_ticket.priority
    record.status = valid_ticket.status

    # commit the updated values
    db.session.commit()

    # return ticket with new values
    return Ticket.model_validate(record)

def delete_ticket(ticket_id: int):

    # find the record in the DB
    record = db.session.get(TicketRecord, ticket_id)
    if record is None:
        return False 
    
    db.session.delete(record)

    db.session.commit()
    return True
