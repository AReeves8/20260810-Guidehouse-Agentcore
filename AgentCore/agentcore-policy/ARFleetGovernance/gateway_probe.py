import argparse
import json
import sys
import os
from dotenv import load_dotenv

import httpx
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


load_dotenv()

SIGNING_SERVICE = "bedrock-agentcore"
GATEWAY_URL = os.environ["GATEWAY_URL"]
AWS_REGION = os.environ["AWS_REGION"]
TARGET_NAME = os.environ["GATEWAY_TARGET_NAME"]


def signed_post(url, payload, region):
    """ Sign a JSON_RPC request with SigV4 and send to the gateway. """

    body = json.dumps(payload)      # serialize the payload into a JSON string

    credentials = boto3.Session().get_credentials()
    if credentials is None:
        sys.exit("No AWS credentials. Check AWS_PROFILE.")

    request = AWSRequest(
        method="POST",
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            
            # MCP servers respond with either JSON or an HTTP event-stream
            "Accept": "application/json, text/event-stream"
        }
    )
    SigV4Auth(credentials.get_frozen_credentials(), SIGNING_SERVICE, AWS_REGION).add_auth(request)

    response = httpx.post(
        url, 
        content=body,
        headers=dict(request.headers),
        timeout=30.0
    )
    return response


def parse_body(response):
    """ Parse the response wether it's JSON or an Event Stream 
    
        event streams look like:
            
            event: message, 
            data: {
                ... JSON-RPC response ...
            }
    """
    text = response.text

    # handles case that response is JSON
    if text.lstrip().startswith("{"):
        return json.loads(text)             

    # handles case that response is an event stream
    for line in text.splitlines():
        if line.startswith("data"):
            return json.loads(line[len("data"):].strip())

    # handles case that response is not JSON or Event Stream
    return {"_raw": text}


def rpc(url, region, method, params):
    """ One JSON-RPC reqeust round-trip. """

    # formatting payload for JSON-RPC
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    response = signed_post(url, payload, region)

    return response.status_code, parse_body(response)


def main():

    # setting up Command Line Arguments for this file
    parser = argparse.ArgumentParser(description="Probe an AgentCore Gateway directly.")
    parser.add_argument("command", choices=["list", "call"])
    parser.add_argument("tool", nargs="?")
    parser.add_argument("--service")
    parser.add_argument("--env", dest="environment")
    parser.add_argument("--replicas", type=int)
    parser.add_argument("--snapshot", dest="snapshotId")
    args = parser.parse_args()

    # handling command options
    if args.command == "list":
        status, message = rpc(GATEWAY_URL, AWS_REGION, "tools/list", {})
        tools = message.get("result", {}).get("tools", [])

        print("===== TOOLS =====")
        for tool in tools:
            print(tool["name"])
        print("=================")

    elif args.command == "call":   
        if not args.tool:
            sys.exit("call command needs a tool specified")

        supplied_values = {
            "service": args.service,
            "environment": args.environment,
            "replicas": args.replicas,
            "snapshotId": args.snapshotId,
        }
        arguments = {k: v for k, v in supplied_values.items() if v is not None}

        raw_tool = f"{TARGET_NAME}___{args.tool}"

        status, message = rpc(GATEWAY_URL, AWS_REGION, "tools/call", {"name": raw_tool, "arguments": arguments})
        print("===== CALL RESPONSE =====")
        print(f"Status: {status}")
        print(f"Response: {message}")
        print("=========================")


if __name__ == "__main__":
    main()