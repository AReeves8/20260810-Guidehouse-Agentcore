"""Let the deployed agent reach the governed gateway.

Dependencies
------------
    uv add mcp langchain-mcp-adapters httpx

"""

import contextlib
import os
import httpx

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SIGNING_SERVICE = "bedrock-agentcore"
_UNSIGNABLE = {"connection", "host", "content-length"}
_TIMEOUT_SECONDS = 60.0

class SigV4HttpxAuth(httpx.Auth):
    """Sign every outbound request with SigV4."""

    requires_request_body = True

    def __init__(self, region: str) -> None:
        credentials = boto3.Session().get_credentials()
        if credentials is None:
            raise RuntimeError(
                "No AWS credentials available. Inside a Runtime this means the "
                "execution role failed to resolve; locally, set AWS_PROFILE."
            )
        self._signer = SigV4Auth(credentials, SIGNING_SERVICE, region)

    def auth_flow(self, request: httpx.Request):
        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=request.content or b"",
            headers={
                k: v for k, v in request.headers.items() if k.lower() not in _UNSIGNABLE
            },
        )
        self._signer.add_auth(aws_request)
        for key, value in aws_request.headers.items():
            request.headers[key] = value
        yield request


def gateway_url():
    """ retrieve the gateway URL set by the AgentCore CLI """
    for key, value in os.environ.items():
        if key.startswith("AGENTCORE_GATEWAY_") and key.endswith("_URL"):
            return value if value.rstrip("/").endswith("/mcp") else value.rstrip("/") + "/mcp"
    
    return ""


@contextlib.asynccontextmanager
async def fleet_tools():
    """Yield the gateway tools this caller is currently permitted to use."""

    url = gateway_url()
    if not url:
        yield []
        return

    region = os.environ.get("AWS_REGION", "us-east-1")

    async with contextlib.AsyncExitStack() as stack:
        try:
            http_client = await stack.enter_async_context(
                httpx.AsyncClient(
                    timeout=_TIMEOUT_SECONDS,
                    auth=SigV4HttpxAuth(region),
                    follow_redirects=True,
                )
            )
            read, write, _ = await stack.enter_async_context(
                streamable_http_client(url, http_client=http_client)
            )
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            tools = await load_mcp_tools(session)

        except Exception as exc:
            
            print(f"[fleet_client] gateway unavailable, continuing without tools: {exc!r}")
            tools = []

        yield tools
