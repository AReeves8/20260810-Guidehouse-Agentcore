""" a dedicated space to load in the ENV file """

import os

from dotenv import load_dotenv

# pulls in .env file into app context
load_dotenv()

# save .env variables to variables in the app that we can import in other places
AWS_PROFILE = os.environ["AWS_PROFILE"]
AWS_REGION = os.environ["AWS_REGION"]
BUCKET_NAME = os.environ["SUPPORT_AI_BUCKET_NAME"]
LAMBDA_FUNCTION_NAME = os.environ["SUPPORT_AI_LAMBDA_FUNCTION_NAME"]