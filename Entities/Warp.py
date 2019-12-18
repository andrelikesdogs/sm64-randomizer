from typing import NamedTuple
from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping

class Warp(BaseMemoryRecord):
  to_area_id: int
  to_course_id: int
  to_warp_id: int
  warp_id: int
  type: str = "NORMAL" # INSTANT, NORMAL, PAINTING
  anim_type: str = None
  area_id: int
  has_checkpoint: bool = False
  memory_address: int = None

  def __init__(self, warp_type : str, warp_id : int, to_area_id : int, to_course_id : int, to_warp_id : int, course_id : int, area_id : int, has_checkpoint : bool = False, mem_address : int = None):
    super().__init__()

    self.warp_id = warp_id
    self.to_course_id = to_course_id
    self.to_area_id = to_area_id
    self.to_warp_id = to_warp_id
    self.type = warp_type
    self.has_checkpoint = has_checkpoint
    self.memory_address = mem_address
    self.course_id = course_id
    self.area_id = area_id

    self.add_mapping('warp_id', 'uint', mem_address)
    self.add_mapping('to_course_id', 'uint', mem_address + 1)
    self.add_mapping('to_area_id', 'uint', mem_address + 2)
    self.add_mapping('to_warp_id', 'uint', mem_address + 3)

  def __str__(self):
    return f"<Warp address: {hex(self.memory_address)} ID: {hex(self.warp_id)} found in {hex(self.course_id)} (Area {hex(self.area_id)}), to course {hex(self.to_course_id)} (Area {hex(self.to_area_id)}) to warp {hex(self.to_warp_id)}>"