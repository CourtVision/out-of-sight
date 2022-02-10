import os
import yaml
from pathlib import Path

def parse_configuration(path):   
    """
    Parses the attributes from the YAML CONFIG file and forwards them to the golbal attributes.

    Args:
    ------------
        path: Location of the CONFIG file.

    Returns:
    ------------
        config: dict  

    """
    is_yaml = str(str(path).split(".")[-1]).lower() == "yaml"   
    if path.exists() and is_yaml:

        print("CONFIG.yaml file found and read.")  
        with open(path, 'r') as stream:
            config = yaml.safe_load(stream)
    #       if config:
    #          for option, value in config.items():
    #             os.environ[str(option)] = str(value)   
        return config   #None
    
    else:
        print("No valid CONFIG file found")