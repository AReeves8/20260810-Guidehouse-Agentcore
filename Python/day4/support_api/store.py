"""
store.py - module used to load tickets from a file and store them somewhere
    creating our own exceptions to use during that process
"""
import json
from pathlib import Path
from pydantic import ValidationError
from support_api.models import Ticket
from support_api.config import AppSettings
from support_api.decorators import timed


class TicketStoreError(Exception) :
    """ base exception for all errors in this module """

class FixtureNotFoundError(TicketStoreError) :
    """ raise when the ticket fixture file does not exist """

class InvalidFixtureFormatError(TicketStoreError):
    """ raise when ticket data cannot be loaded in due to format issues """

@timed
def load_tickets(path: Path | None = None) -> tuple[list[Ticket], list[dict[str, list[str]]]] :

    print(f"\n--- FUNCTION NAME: {load_tickets.__name__} ---")

    # if we aren't given a path, grab the one from AppSettings in config.py
    resolved_path = path if path is not None else AppSettings().data_path

    try:
        raw_text = resolved_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        # raise ... from ...
        # translate one exception into another exception
        raise FixtureNotFoundError(f"No ticket fixture at {resolved_path}") from e

    # json into Python object. if the data isn't in json format, you can get errors
    try:
        rows = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise InvalidFixtureFormatError(f"Tickets data could not be loaded in from {resolved_path}") from e

    # creating lists to store both valid and error tickets
    valid_tickets: list[Ticket] = []
    error_tickets: list[dict[str, list[str]]] = []

    for row in rows:
        try: 
            valid_tickets.append(Ticket.model_validate(row))
        except ValidationError as e:
            err_msgs = [f"{e['loc']} : {e['msg']}" for e in e.errors()]
            error_tickets.append({"id": row.get("id", "<no id>"), "errors": err_msgs})

    return valid_tickets, error_tickets
    