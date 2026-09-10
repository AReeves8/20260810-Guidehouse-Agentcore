"""Configuration read from the environment, and nothing else.

This file is short and it is the reason the whole week works. The identical
image, the identical wheel, the identical source tree runs on a laptop, on an
EC2 instance, on Elastic Beanstalk, and on ECS Fargate -- and the only thing
that differs between them is the environment they are handed.

That is the twelfth-factor rule stated concretely: **config that varies
between deployments lives in the environment, not in the code.** The moment a
connection string appears in a source file you have created a build that can
only run in one place, and a secret that lives in version control forever.

DEPLOY_TARGET has no functional purpose. It exists so that each deployment can
say where it is running, which turns "the deploy worked" from a claim into a
row in a shared database.
"""

import os

from dotenv import load_dotenv

# Loads .env for local development. In every AWS deployment this call finds no
# file and does nothing, because real environment variables are already set --
# which is exactly the behaviour we want and worth pointing out rather than
# hiding: the same line is correct in both worlds.
load_dotenv()

# os.environ[...] rather than .get(...) -- a missing database URL should stop
# the process at import, loudly, instead of producing a container that starts
# healthy and fails on the first request that touches the database.
DATABASE_URL = os.environ["DATABASE_URL"]

# .get() with a default here, deliberately inconsistent with the line above:
# this one is a label, not a dependency. Missing it should not stop a deploy.
DEPLOY_TARGET = os.environ.get("DEPLOY_TARGET", "unknown")
