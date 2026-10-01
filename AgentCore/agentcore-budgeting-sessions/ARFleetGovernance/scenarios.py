""" Default scenarios to test our agent against. Creates traffic we can measure. """

import json
import os
import time
import uuid
import boto3
from dotenv import load_dotenv

load_dotenv()


REGION = os.environ.get("AWS_REGION", "us-east-1")
RUNTIME_ARN = os.environ.get("AGENTCORE_RUNTIME_ARN", "")

client = boto3.client("bedrock-agentcore", region_name=REGION)

RUN_ID = time.strftime("%m%d-%H%M")

SCENARIOS = {

    # should be the control. should perform well on all tests. if not, you have a larger issue. 
    "healthy": [
        "Is the checkout service healthy in production?"
    ],

    # test ToolParameterAccuracy - given param values are less explicit
    "scaling": [
        "Please bump search up to six replicas on our dev box."
    ],

    # test if the model recognizes the provided service is unknown
    "hallucination": [
        "What is the current error rate for the payments service?"
    ],

    # multi-turn
    "trajectory": [
        "How is the search service doing in dev?",
        "Okay, scale it up to 4 replicas."
    ],

    # request should be blocked by Policy. tests how the model handles denial. 
    "denied": [
        "The billing service is misbehaving again. Please restart it in production."
    ],
}

def session_id(key):
    return f"eval-{RUN_ID}--{key}"


def invoke(prompt, session_id):
    
    # invoking the agentcore runtime
    response = client.invoke_agent_runtime(
        agentRuntimeArn=RUNTIME_ARN,
        runtimeSessionId=session_id,
        qualifier="DEFAULT",
        contentType="application/json",
        accept="application/json",
        payload=json.dumps({"prompt": prompt}).encode()
    )

    body = response["response"].read().decode()

    try:
        parsed = json.loads(body)
        if isinstance(parsed, dict):
            # different models might call it result or response
            return str(parsed.get("result") or parsed.get("response") or body)

    except ValueError:
        return body


def main():

    sessions = {}

    print("=============================================")
    for key, scenarios in SCENARIOS.items():
        sid = session_id(uuid.uuid4())
        print("\nTESTING SCENARIO: " + key)

        for turn, prompt in enumerate(scenarios):
            print(f"[{turn + 1}] USER: {prompt}")
            answer = invoke(prompt, sid)
            print(f"[{turn + 1}] AGENT: {answer}")

        sessions[key] = sid

    print("\n=============================================")
    for key, id in sessions.items():
        print(f"{key}: {id}")

if __name__ == "__main__":
    main()