import yaml
import os
from pathlib import Path

from Constants import application_path

class Config:
  found = None

  def __init__(self, name):
    pass
  
  @staticmethod
  def load_configurations():
    if Config.found is not None:
      return Config.found
    
    Config.found = []
    for file in os.listdir(os.path.join(application_path, 'Config')):
      config_file = Path(os.path.join(application_path, 'Config', file))

      if config_file.suffix == '.yml' or config_file.suffix == '.yaml':
        with open(config_file, 'r') as config:
          parsed = yaml.load(config.read())
          Config.found.append(parsed)
    
    return Config.found

  @staticmethod
  def find_configuration(checksum):
    Config.load_configurations()

    if Config.found is None:
      raise TypeError("No configurations found. Check our /Config folder")

    for config in Config.found:
      print(config)
      
  
  @staticmethod
  def from_checksum(checksum):
    pass