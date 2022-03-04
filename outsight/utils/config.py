import os
import yaml
import logging
logger = logging.getLogger(__name__)

def parse_configuration(path: str) -> dict:   
    """
    Parses the attributes from the YAML CONFIG file.

    Args:
    ------------
        path (str): Location of the CONFIG file

    Returns:
    ------------
        config (dict)  
    """
    is_yaml = str(str(path).split(".")[-1]).lower() == "yaml"   
    if path.exists() and is_yaml:

        print("CONFIG.yaml file found and read.")
        logger.info("CONFIG.yaml file found and read.")  
        with open(path, 'r') as stream:
            config = yaml.safe_load(stream)
    #       if config:
    #          for option, value in config.items():
    #             os.environ[str(option)] = str(value)   
        return config   #None
    
    else:
        print("No valid CONFIG file found.")
        logger.info("No valid CONFIG file found.")  