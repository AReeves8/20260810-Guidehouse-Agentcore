
"""
broke tickets.py into separate pieces
those pieces can now be imported and used here
"""

#from support_api.filters import *       # generally considered bad practice - only import what you need
from support_api.data import SAMPLE_TICKETS
from support_api.filters import filter_tickets, count_by_priority
from support_api.models import EscalatedTicket, Ticket
from support_api.config import AppSettings
from pydantic import ValidationError


print("--- Tickets ---")
new_ticket = Ticket.model_validate(SAMPLE_TICKETS[0])
print(new_ticket)
print(type(new_ticket))


escalated_ticket = EscalatedTicket.from_row(SAMPLE_TICKETS[4])
print(escalated_ticket)
print(type(escalated_ticket))


# trying to create a ticket that we know should fail
print("\n--- Broken Ticket Check ---")
try:

    broken_ticket = Ticket.model_validate({
        "id": 12, 
        "tenant": "acme-corp",  
        "title": "abc",   
        "priority": "mega urgent", 
        "status": "lost forever",
        "category": "IT"
    })
    print(broken_ticket)
    print(type(broken_ticket))

except ValidationError as ex:
    print(ex)


tickets = [EscalatedTicket.from_row(row) for row in SAMPLE_TICKETS]

print("\n--- Real Filtered Tickets ---")
print(filter_tickets(tickets, status="resolved"))

print("\n--- Real Count By Priority ---")
print(count_by_priority(tickets))


print("\n--- App Settings ---")
print(AppSettings())
