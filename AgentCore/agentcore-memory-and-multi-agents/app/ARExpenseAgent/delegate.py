import json
import os
import uuid

import boto3
from config import AWS_REGION, WORKER_ARN
from langchain_core.tools import tool


_client = boto3.client(
    "bedrock-agentcore",
    region_name=AWS_REGION
)

@tool
def ask_policy_agent(question: str) -> str:
    """Ask the travel-policy specialist agent a question about expense policy.

    Use this for questions about spending limits, policy exceptions, and what
    requires approval. Pass the traveller's question in plain English.
    """

    if not WORKER_ARN:
        return "The policy agent is not configured (POLICY_AGENT_ARN is unset)."

    response = _client.invoke_agent_runtime(
        agentRuntimeArn=WORKER_ARN,
        runtimeSessionId=str(uuid.uuid4()),
        contentType="application/json",
        accept="application/json",
        payload=json.dumps({"prompt": question}).encode(),
    )

    # `response` is a streaming body; read it once.
    body = response["response"].read().decode()

    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict):
            return str(parsed.get("result") or parsed.get("response") or body)
    except (ValueError, TypeError):
        pass
    return body