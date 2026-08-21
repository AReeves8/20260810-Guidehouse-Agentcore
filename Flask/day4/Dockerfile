# baseImage is some existing image in Docker Hub that you will build on top of
# - want your baseImages to be small so they don't include a bunch of unneeding things
FROM python:3.14-slim

# create a directory inside the container for our code to live in
#   this also moves us into the directory
#       equivalent of doing "mkdir" and "cd" in one line
WORKDIR /app

# copy code from project (local machine) to the container working directory
#   source starts at the location of the Dockerfile on your machine
#   dest starts at current directory of container (which we specified is /app with the above command)
COPY . .

# install all needed directories into the container
# RUN lets you run any kind of cli command
RUN pip install --no-cache-dir .

# use ENV to set environment variables
# FLASK_APP can be used instead of having to put --app on command when running flask app
ENV FLASK_APP=ticket_api.app

# telling Docker to keep a port open in the container to allow traffic through
EXPOSE 5000

# upgrading the DB to match any existing migrations that would have been copied over in COPY
# then running the flask app inside the container and on port 5000
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=5000"]