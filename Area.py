from typing import Dict

class Area:
  def __init__(self, area_id : int, name : str, properties : Dict):
    self.id = area_id
    self.name = name
    self.properties = properties
    
  def __str__(self):
    return f'<Area {hex(self.id)}: {self.name}>: {repr(self.properties)}'