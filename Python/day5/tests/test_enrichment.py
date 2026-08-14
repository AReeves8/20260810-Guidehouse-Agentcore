import pytest
from support_api.enrichment import enrich, language_detection, sentiment_analysis
from support_api.data import SAMPLE_TICKETS
from support_api.models import Ticket

def _tickets():
    return [Ticket.model_validate(row) for row in SAMPLE_TICKETS]

# pytest will force asyncio to run the coroutine inside of this test
@pytest.mark.asyncio
async def test_enrich_returns_language_and_sentiment():

    tickets = _tickets()

    # the first ticket should identify as Russian language and Positive sentiment
    result = await enrich(tickets[0])
    assert "Russian" in result
    assert "Positive" in result