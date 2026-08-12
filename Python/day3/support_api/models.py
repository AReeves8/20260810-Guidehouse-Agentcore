
"""
Pydantic Models
    add types to your models to ensure they are properly instantiated

    Literal - makes it so that a property must contain one of the given values
    Optional - the value can either be the given type or None
    BaseModel - what activates Pydantic validation on your class
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


Priority = Literal["low", "medium", "high", "urgent"]
Status = Literal["open", "ack", "resolved", "escalated"]
Category = Literal["billing", "auth", "performance", "data"]


class Ticket(BaseModel):

    # now define types for your models
    id: str
    tenant: str

    # use Pydantic Field function to add validation constraints to your properties
    title: str = Field(min_length=5, max_length=80)     

    priority: Priority

    # giving status a default value of open
    status: Status = "open"

    # make this field optional
    category: Optional[Category] = None
    

# inheritance - add parenthesis and "pass-in" parent class
class EscalatedTicket(Ticket):

    status: Status = "escalated"
    esescalated_to: str = "Manager"

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Ticket:
        if row.get("status") == "escalated":
            return cls.model_validate(row)
        return Ticket.model_validate(row)