.PHONY: clean strore_requirements install_requirements create_conda_env start_conda

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = outofsight
PACKAGE_NAME = outsight
OS = Linux
PYTHON_INTERPRETER = python3  # python3 for Linux
PYTHON_VERSION = 3.9.5


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
store_conda_requirements:
# pip list --format=freeze > requirements.txt
	conda env export --name $(PROJECT_NAME) --no-builds --file $(PROJECT_NAME)/conda_env.yml

install_os_requirements:
ifeq ($(OS), Linux)
	apt-get update
	apt-get install ffmpeg libsm6 libxext6  -y
	apt-get install -y wget
	apt update
	apt install tesseract-ocr -y
	wget https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata -O /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata 2> /dev/null

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
	conda env create --name $(PROJECT_NAME) --file conda_env.yml python=$(PYTHON_VERSION)

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

## Create documentation
doc:
	cd $(PACKAGE_NAME) && mkdir -p docs && cd ..
	pdoc -o $(PACKAGE_NAME)/docs $(PACKAGE_NAME)