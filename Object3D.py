from typing import NamedTuple
from Rom import ROM

class Object3D(NamedTuple):
  source: str # SPECIAL_MACRO_OBJ, PLACE_OBJ, MACRO_OBJ
  model_id: str
  position: tuple = (0, 0, 0) # (X, Y, Z)
  rotation: tuple = (0, 0, 0) # (X, Y, Z)
  behaviour: int = None # addr
  b1_param: int = None
  b2_param: int = None
  b3_param: int = None
  b4_param: int = None
  mem_address: int = None

  def change_position(self, position, rom : ROM):
    if self.mem_address is None:
      raise Exception("This Object is not memory mapped. Can not alter")
    
    if self.source == "MACRO_OBJ":
      for idx, comp in enumerate(position):
        rom.write_integer(self.mem_address + idx * 2, comp, 2, True)