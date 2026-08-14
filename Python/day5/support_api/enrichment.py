"""
simulate text enrichment calls
    sentiment analysis
    language detection
    etc.
"""

import asyncio
from support_api.decorators import timed
from support_api.models import Ticket


@timed
async def sentiment_analysis(title: str) :

    # await is used to block python from continuing to run and wait for a response from the asynchronous operation
    await asyncio.sleep(0.5)        # simulate the time it would take to call an external service

    if "positive" in title.lower():
        return "Positive"
    if "negative" in title.lower():
        return "Negative"
    return "Neutral"

@timed
async def language_detection(title : str) :

    # await is used to block python from continuing to run and wait for a response from the asynchronous operation
    await asyncio.sleep(0.5)        # simulate the time it would take to call an external service

    if "privet" in title.lower():
        return "Russian"
    if "konnichiwa" in title.lower():
        return "Japanese"
    if "nihao" in title.lower():
        return "Chinese"
    if "hola" in title.lower():
        return "Spanish"

    return "English"

@timed
async def enrich(ticket: Ticket):
    """
    use asyncio.gather() to run multiple operations CONCURRENTLY

    if you run both independently, then you have to wait for each to finish
        so if each takes ~.5 seconds to finish, then the each ticket takes ~1 second to process. 
    """
    language, sentiment = await asyncio.gather(
        language_detection(ticket.title),
        sentiment_analysis(ticket.title)
    )

    return f"Ticket {ticket.id} is in {language} and has {sentiment} sentiment."