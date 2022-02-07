.PHONY: clean strore_requirements install_requirements create_conda_env start_conda

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = outofsight
OS = Linux
PYTHON_INTERPRETER = python3  # python3 for Linux
PYTHON_VERSION = 3.9.5


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
store_requirements:
	pip list --format=freeze > requirements.txt

install_requirements:
ifeq ($(OS), Linux)
	apt-get update && apt-get install tesseract-ocr -y
    #$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
    #$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
endif

## Set up python interpreter environment
create_conda_env:
ifeq ($(OS), Windows)
	conda init 
else 
	conda init bash
endif
	conda config --append channels conda-forge
	conda create --name $(PROJECT_NAME) --file requirements.txt python=$(PYTHON_VERSION)

# Activate project conda environment
# https://pythonspeed.com/articles/activate-conda-dockerfile/
# start_conda:
#	conda init bash
#	conda activate $(PROJECT_NAME)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	echo ">>> Junk files cleaned."

## Install linux libs
#.ONESHELL:
#ec2_setup:
#	sudo apt-get update
#	sudo apt-get install -y openjdk-8-jre
#	cd $(HOME)
#	sudo apt-get install -y pandoc
#	sudo apt-get install -y graphviz