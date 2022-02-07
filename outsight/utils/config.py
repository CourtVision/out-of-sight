import os
import yaml

def parse_configuration(path):   
    """
    Parses the attributes from the YAML CONFIG file and forwards them to the golbal attributes.

    Args:
    ------------
        path: Location of the CONFIG file.

    Returns:
    ------------
        None:  

    """
    
    is_file = os.path.isfile(path)
    is_yaml = str(path.split(".")[-1]).lower() == "yaml"   
    if is_file and is_yaml: 
        print("CONFIG file found and read.")  
        with open(path, 'r') as stream:
            config = yaml.safe_load(stream)
    #       if config:
    #          for option, value in config.items():
    #             os.environ[str(option)] = str(value)   
        return config   #None