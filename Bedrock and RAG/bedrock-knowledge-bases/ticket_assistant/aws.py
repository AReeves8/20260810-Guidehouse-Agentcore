from functools import lru_cache
import boto3
from ticket_assistant.config import AWS_PROFILE, AWS_REGION


@lru_cache(maxsize=1)
def get_session() -> boto3.Session:
    return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)


@lru_cache(maxsize=None)
def get_client(service_name: str):
    return get_session().client(service_name)


# retrieve client for bedrock runtime (aka Data Plane)
def bedrock_runtime():
    """ inferencing occurs """
    return get_client("bedrock-runtime")

# retrieve client for bedrock (aka Control Plane)
def bedrock_control():
    """ control plane contains config for your models, no actual inferencing """
    return get_client("bedrock")

# retrieve bedrock agent
def agent_runtime():
    """ handle knowledge bases as well as agent queries """
    return get_client("bedrock-agent-runtime")