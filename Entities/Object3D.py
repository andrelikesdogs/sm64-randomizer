from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping

class Object3D(BaseMemoryRecord):
  source: str # SPECIAL_MACRO_OBJ, PLACE_OBJ, MACRO_OBJ, MARIO_SPAWN
  model_id: str
  position: tuple = (0, 0, 0) # (X, Y, Z)
  rotation: tuple = (0, 0, 0) # (X, Y, Z)
  behaviour: int = None # addr
  bparams: list = []
  mem_address: int = None
  memory_mapping: dict = {}

  def __init__(self, source, model_id, position, rotation = None, behaviour = None, bparams = [], mem_address = None):
    super().__init__()

    self.source = source
    self.model_id = model_id
    self.position = position
    self.rotation = rotation
    self.behaviour = behaviour
    self.memory_address = mem_address
    
    if mem_address is not None:
      if source == 'MARIO_SPAWN' or source == 'PLACE_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 4, mem_address + 12)
      elif source == 'SPECIAL_MACRO_OBJ' or source == 'MACRO_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 3, mem_address + 11)
      else:
        pass