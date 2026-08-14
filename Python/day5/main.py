import logging
import asyncio
from support_api.store import load_tickets
from support_api.config import AppSettings
from support_api.filters import filter_tickets
from support_api.enrichment import language_detection, sentiment_analysis, enrich

# configuring logger for the app
logging.basicConfig(level=AppSettings().log_level, format="%(levelname)s %(name)s: %(message)s")

async def main() :
    print("\n-------------------------------------\n")
    valid_tickets, error_tickets = load_tickets()

    print("--- Valid Tickets ---")
    print(valid_tickets)

    print("\n--- Error Tickets ---")
    print(error_tickets)

    print("\n--- Filtering Tickets ---")
    print(filter_tickets(valid_tickets, tenant="acme-corp", category="auth"))

    print("\n--- Independent Operations ---")
    for ticket in valid_tickets:
        language = await language_detection(ticket.title)
        sentiment = await sentiment_analysis(ticket.title)
        print(f"Ticket {ticket.id} is in {language} and has {sentiment} sentiment.")

    print("\n--- Concurrent Operations ---")
    for ticket in valid_tickets:
        ticket_enrichment = await enrich(ticket)
        print(ticket_enrichment)

    print("\n--- Concurrent Operations Extreme ---")
    # running all enrichments concurrently
    results = await asyncio.gather(*(enrich(ticket) for ticket in valid_tickets))
    for result in results:
        print(result)


if __name__ == "__main__" :

    # using asyncio to run our asynchronous main method
    asyncio.run(main())
