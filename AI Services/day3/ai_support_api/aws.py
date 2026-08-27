""" creating the boto3 client that will connect to AWS with our credentials and return running sessions """


import boto3
from functools import lru_cache
from ai_support_api.config import AWS_PROFILE, AWS_REGION


@lru_cache(maxsize=1)       # caching only one return value from this function
def get_session() -> boto3.Session:
    """ ONE SHARED AWS session for the entire app """

    return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)

# having a cache without a max size can still be helpful to retain results
@lru_cache(maxsize=None)
def get_client(service_name: str):
    """ return a boto3 client for a given AWS Service """

    return get_session().client(service_name)