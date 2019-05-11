from typing import NamedTuple
from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping

class Warp(BaseMemoryRecord):
  to_area_id: int
  to_course_id: int
  to_warp_id: int
  warp_id: int
  type: str = "NORMAL" # INSTANT, NORMAL, PAINTING
  area_id: int
  has_checkpoint: bool = False
  memory_address: int = None

  def __init__(self, warp_type : str, warp_id : int, to_area_id : int, to_course_id : int, to_warp_id : int, area_id : int, has_checkpoint : bool = False, mem_address : int = None):
    super().__init__()

    self.warp_id = warp_id
    self.to_course_id = to_course_id
    self.to_area_id = to_area_id
    self.to_warp_id = to_warp_id
    self.type = warp_type
    self.has_checkpoint = has_checkpoint
    self.memory_address = mem_address
    self.area_id = area_id

    self.add_mapping('warp_id', 'uint', mem_address)
    self.add_mapping('to_course_id', 'uint', mem_address + 1)
    self.add_mapping('to_area_id', 'uint', mem_address + 2)
    self.add_mapping('to_warp_id', 'uint', mem_address + 3)