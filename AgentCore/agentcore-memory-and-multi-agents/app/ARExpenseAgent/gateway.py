import os
import contextlib
from typing import Generator
import boto3
import httpx
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession

from config import AWS_REGION

# specifies the 'signingName' SigV4 uses
SIGNING_SERVICE = "bedrock-agentcore"

# a few headers that httpx sets that we DO NOT want SigV4 to sign
UNSIGNABLE = {"connection", "host", "content-length"}

# httpx defaults to 5 seconds, not enough for sending an API request to gateway that may also be sending API request(s) to other services
TIMEOUT_SECONDS = 60.0


class SigV4HttpxAuth(httpx.Auth):
    """ configuring how to sign each outbound request """

    # tell httpx to load the body of the request before calling it's own auth_flow
    # important because we NEED our body signed with SigV4 as well
    requires_request_body = True

    def __init__(self, region: str) -> None:

        # load AWS credentials
        credentials = boto3.Session().get_credentials()

        if credentials is None:
            raise RuntimeError("No AWS credentials. Locally, set AWS_PROFILE. Deployed, the execution role failed to resolve.")

        self._signer = SigV4Auth(credentials, SIGNING_SERVICE, region)

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        """ interrupt the original request, 
            send to AWS for SigV4 signing, 
            copy back over AWS headers to the original request, 
            then let the original request fly 
        """
        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=request.content or "",
            headers={
                key: value for key, value in request.headers.items() if key.lower() not in UNSIGNABLE
            }
        )

        # add_auth is going to add some AWS related headers 
        #       Authorization, X-Amz-Date, X-Amz-Security-Token (only when you have temp credentials, like an execution role)
        # so we need to copy those back onto the request
        self._signer.add_auth(aws_request)
        for key, value in aws_request.headers.items():
            request.headers[key] = value

        yield request


def gateway_url() -> str | None:
    """ go out and find the Gateway URL from env
    
        The agentcore CLI will inject env vars
            AGENTCORE_GATEWAY_<NAME>_URL
            AGENTCORE_GATEWAY_<NAME>_AUTH_TYPE
    """

    # grab the URL from the env - would fail if you had multiple gateways since we aren't searching by name
    for key, value in os.environ.items():
        if key.startswith("AGENTCORE_GATEWAY_") and key.endswith("_URL"):
            return value
    return None

@contextlib.asynccontextmanager
async def gateway_tools():
    """ reaching out to gateway to find what tools exist and returning them as tools langchain can use """

    url = gateway_url()
    if url is None:
        # yield an empty list of tools if there is no gateway url
        # that way the graph can still run, just with its local tools only
        yield []

    # AsyncClient owns TCP connection and our SigV4 auth
    async with httpx.AsyncClient(
        timeout=TIMEOUT_SECONDS,
        auth=SigV4HttpxAuth(AWS_REGION),
        follow_redirects=True
    ) as http_client:

        # streamable_http_client owns MCP transport over the TCP connection
        async with streamable_http_client(
            str(url), 
            http_client=http_client
        ) as (read, write, _):

            # ClientSession owns the session that is connected to the gateway
            async with ClientSession(read, write) as session:
                await session.initialize()      # initialize the MCP server session

                # load_mcp_tools converts MCP tools into LangChain tools
                yield await load_mcp_tools(session)