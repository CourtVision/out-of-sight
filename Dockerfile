## build as: docker build -t outsight-image .
## run as: docker run --rm --name outsight-container outsight-image -w all - d False
## docker exec -t -i outsight-container  /bin/bash

# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.9-slim
FROM continuumio/miniconda3

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY /outsight/requirements.txt .
COPY Makefile .
RUN apt-get update && apt-get install make
RUN make install_requirements
RUN make create_conda_env

WORKDIR /app
COPY . /app

# Make RUN commands use the new environment
# https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "outofsight", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "-n", "outofsight", "python", "/outsight/app.py"]