
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


Priority = Literal["low", "medium", "high", "urgent"]
Status = Literal["open", "ack", "resolved", "escalated"]

class Ticket(BaseModel):

    # makes it so pydantic can validate based on attributes of other objects
    #       for example, SQLAlchemy db models
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant: str
    title: str = Field(min_length=5)
    priority: Priority
    status: Status = "open"


"""
    Data Transfer Object (DTO)
        - used to create objects that align to a variation of an existing model
        - when the shape of the data you work with, doesn't match the shape of the data you send to other systems

        - in our case: 
            - POST /api/v1/tickets cannot send in an ID that Ticket would expect

        - **technically** this isn't a **real** dto..
            - DTOs are supposed to have absolutely ZERO logic at all and this has logic to validate the values
            - BUT programmers use them like this all the time so the defintion has gotten blurred
"""
class CreateTicketDto(BaseModel):

    # FORBIDDING any extra values being passed in to the object
    #   extra properties are typically just ignored, but with extra="forbid" you get ValidationError
    model_config = ConfigDict(extra="forbid")

    tenant: str
    title: str = Field(min_length=5)
    priority: Priority
    # new tickets should always be "open" which is the default value of Ticket

class UpdateTicketDto(BaseModel):

    model_config = ConfigDict(extra="forbid")

    tenant: str
    title: str = Field(min_length=5)
    priority: Priority
    status: Status