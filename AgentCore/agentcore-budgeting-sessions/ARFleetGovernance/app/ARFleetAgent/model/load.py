from langchain_aws import ChatBedrockConverse

from config import AWS_REGION, BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS

def load_model() -> ChatBedrockConverse:
    """ Build Bedrock chat mmodel from environment variables. """

    return ChatBedrockConverse(
        model=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        max_tokens=BEDROCK_MAX_TOKENS,
        temperature=0.0
    )
