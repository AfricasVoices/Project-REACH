FROM python:3.6-slim

# Install the tools we need.
RUN apt-get update && apt-get install -y git
RUN pip install pipenv

# Set working directory
WORKDIR /app

# Install project dependencies.
ADD Pipfile.lock /app
ADD Pipfile /app
RUN pipenv sync

# Copy the rest of the project
ADD . /app

# Make a directory for intermediate data
RUN mkdir /data

# USER is an environment variable which needs to be set when constructing this container e.g. via
# docker run or docker container create. Use docker-run.sh to set these automatically.
CMD pipenv run python survey_merge_coded.py "$USER" /data/input.json  /data/coding \
    /data/output.json /data/output-interface/
