from typing import List, Dict

from .Area import Area

class Level:
  def __init__(self, course_id : int, name : str, properties : Dict = None, areas : List[Area] = None, offset : int = None):
    self.course_id = course_id
    self.name = name
    self.properties = properties or {}
    self.offset = offset

    self.areas = areas or []

  def __str__(self):
    return f'<Level {hex(self.course_id)}: {self.name}>' #: {repr(self.properties)}, {[str(area) for area in self.areas]}'