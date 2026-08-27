from ai_support_api.aws import get_client

def whoami():
    """ return the identity if the process is authenticated to AWS """

    identity = get_client("sts").get_caller_identity()
    return {
        "account": identity["Account"],
        "arn": identity["Arn"]
    }