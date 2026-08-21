import random

from faker import Faker

from ticket_api.app import create_app
from ticket_api.extensions import db
from ticket_api.tickets.db_models import TicketComment, TicketRecord

fake = Faker()
random.seed(11)  

TENANTS = ["acme-corp", "globex", "initech"]
PRIORITIES = ["low", "medium", "high", "urgent"]
STATUSES = ["open", "ack", "resolved", "escalated"]


def build_tickets(count: int = 30) -> list[TicketRecord]:
    # No `id=` here — Postgres assigns it via the auto-increment column
    return [
        TicketRecord(
            tenant=random.choice(TENANTS),
            title=fake.sentence(nb_words=6).rstrip("."),
            priority=random.choice(PRIORITIES),
            status=random.choice(STATUSES),
        )
        for _ in range(count)
    ]


def build_comments(tickets: list[TicketRecord]) -> list[TicketComment]:
    # ticket.id is only safe to read here because main() flushes the session first
    return [
        TicketComment(ticket_id=ticket.id, body=fake.sentence(nb_words=10))
        for ticket in tickets
        for _ in range(random.randint(0, 3))
    ]


def main():
    app = create_app()
    # db.session (and every other Flask-SQLAlchemy call) needs an active
    # application context even when nothing is handling an HTTP request —
    # `app.app_context()` provides that outside of a real request.
    with app.app_context():
        if db.session.query(TicketRecord).first() is not None:
            print("tickets table is not empty — skipping seed")
            return

        tickets = build_tickets()
        try:
            db.session.add_all(tickets)
            # flush() sends the pending INSERTs to Postgres and populates
            # every ticket's auto-increment id — WITHOUT committing the
            # transaction yet. This is what lets build_comments() below
            # reference real ticket_id values, while the whole batch
            # (tickets + comments) still commits together as ONE
            # transaction on the next line, not two.
            db.session.flush()
            db.session.add_all(build_comments(tickets))
            db.session.commit()
        except Exception:
            # If anything in the batch fails, roll back the WHOLE
            # transaction rather than leaving half the tickets committed
            # and half not — an all-or-nothing seed, the same discipline
            # a real "insert this whole order" transaction needs.
            db.session.rollback()
            raise
        print(f"seeded {len(tickets)} tickets")


if __name__ == "__main__":
    main()