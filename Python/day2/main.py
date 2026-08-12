
"""
broke tickets.py into separate pieces
those pieces can now be imported and used here
"""

#from support_api.filters import *       # generally considered bad practice - only import what you need
from support_api.data import SAMPLE_TICKETS
from support_api.filters import filter_tickets, count_by_priority
from support_api.models import EscalatedTicket


print("\n--- Filtered Tickets ---")

print(filter_tickets(SAMPLE_TICKETS, priority="urgent"))

print("\n--- Tickets by Priority ---")
print(count_by_priority(SAMPLE_TICKETS))

print("\n--- TICKET OBJECTS ---")

my_escalated_ticket = EscalatedTicket(
    SAMPLE_TICKETS[2]["id"], 
    SAMPLE_TICKETS[2]["tenant"],
    SAMPLE_TICKETS[2]["title"],
    SAMPLE_TICKETS[2]["priority"],
    "escalated",
    "Manager"
)
print(my_escalated_ticket)
print(type(my_escalated_ticket))