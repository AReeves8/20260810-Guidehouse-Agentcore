""" calling AWS Comprehend with boto3 """ 

import json
from ai_support_api.aws import get_client
from ai_support_api.config import LAMBDA_FUNCTION_NAME


def analyze_sentiment(text: str) -> dict:
    """ use Amazon comprehend to determine overall tone of text """

    response = get_client("comprehend").detect_sentiment(
        Text=text,
        LanguageCode="en"
    )

    return {
        "sentiment": response["Sentiment"],

        # rounding the confidence value to 3 decimal places
        "scores": {k : round(v, 3) for k, v in response["SentimentScore"].items()}
    }


def priority_from_keywords(ticket_id: int, body: str) -> str:
    """ using our hand-built Lambda function to determine ticket priority """

    response = get_client("lambda").invoke(
        FunctionName=LAMBDA_FUNCTION_NAME, 

        # this is going to block your python app until you get a response from the lambda function
        InvocationType="RequestResponse",
        Payload=json.dumps({"ticket_id": ticket_id, "body": body}).encode("utf-8")
    ) 

    payload = json.loads(response["Payload"].read())
    return payload["priority"]


def priority_from_sentiment(text: str) -> str:
    """ use the Amazon comprehend sentiment analysis to decide ticket priority levels """

    result = analyze_sentiment(text)

    if result["sentiment"] == "NEGATIVE" and result["scores"]["Negative"] > 0.7:
        return "high"

    if result["sentiment"] == "MIXED":
        return "medium"

    return "low"


def triage_priority(ticket_id: int, body: str):
    """ call both priority determining functions and compare results """

    keyword_priority = priority_from_keywords(ticket_id, body)
    sentiment_priority = priority_from_sentiment(body)

    return {
        "ticket_id": ticket_id,
        "keyword_priority": keyword_priority,
        "sentiment_priority": sentiment_priority,
        "approaches_agree": keyword_priority == sentiment_priority
    }