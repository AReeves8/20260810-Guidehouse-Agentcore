"""
SQLAlchemy ORM Models
    - Object Relational Mapping
        - 1:1 map your object properties to columns in a DB
        - they also map related entities
        - give default functionality for db interactions
"""
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ticket_api.extensions import db

class TicketRecord(db.Model):

    # the name of the corresponding db table
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")

    # each ticket will contain a list of associated comments
    # relationship DOES NOT define a column - only asks SQLAlchemy to grab related objects
    comments: Mapped[list["TicketComment"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

class TicketComment(db.Model):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default= lambda: datetime.now(timezone.utc))

    # establishing the Foreign Key to the tickets table
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)

    ticket: Mapped["TicketRecord"] = relationship(back_populates="comments")