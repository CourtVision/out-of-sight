## build: docker build -f Dockerfile -t outsight-image .
## run: docker run -v io-volume:/./io --name outsight-container outsight-image -w all -d False
## debug: docker run -i -t  --name outsight-container outsight-image bash
## docker start  && docker exec -t -i outsight-container bash  OR  docker start -i  outsight-container

## Volumes 
## docker volume create io-volume
## docker volume inspect io-volume
## Windows: \\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\

## docker cp container_id:./bar/foo.txt .
## docker cp foo.txt mycontainer:/foo.txt


# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.9-slim
FROM continuumio/miniconda3

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install linux & conda requirements
COPY . /
COPY /outsight/conda_env.yml .

RUN apt-get update && apt-get install make
RUN make install_requirements
RUN make create_conda_env

# Make RUN commands use the new environment
# https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "outofsight", "/bin/bash", "-c"]

ENTRYPOINT ["conda", "run", "-n", "outofsight", "python", "/outsight/app.py"]