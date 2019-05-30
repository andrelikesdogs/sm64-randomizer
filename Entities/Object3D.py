from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping
from Constants import BEHAVIOUR_NAMES

class Object3D(BaseMemoryRecord):
  source: str # SPECIAL_MACRO_OBJ, PLACE_OBJ, MACRO_OBJ, MARIO_SPAWN
  model_id: str
  position: tuple = (0, 0, 0) # (X, Y, Z)
  rotation: tuple = (0, 0, 0) # (X, Y, Z)
  behaviour: int = None # addr
  behaviour_name: str = None
  bparams: list = []
  mem_address: int = None
  memory_mapping: dict = {}

  def generate_name(self):
    if self.behaviour and hex(self.behaviour) in BEHAVIOUR_NAMES:
      behaviour_name = BEHAVIOUR_NAMES[hex(self.behaviour)]
      return f'{behaviour_name} (#{hex(self.behaviour)})'
    
    if self.model_id:
      return f'Unknown (Model-ID: #{hex(self.model_id)}'

    if self.source == 'MARIO_SPAWN':
      return f'Mario\'s Spawn Point'

    return f'Unknown (Source: {self.source})'

  def __init__(self, source, model_id, position, rotation = None, behaviour = None, bparams = [], mem_address = None):
    super().__init__()

    self.source = source
    self.model_id = model_id
    self.position = position
    self.rotation = rotation
    self.behaviour = behaviour
    self.behaviour_name = self.generate_name()
    self.mem_address = mem_address
    
    if mem_address is not None:
      if source == 'PLACE_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 2, mem_address + 8)
      elif source == source == 'MARIO_SPAWN':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 4, mem_address + 10)
      elif source == 'MACRO_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 2, mem_address + 8)
      elif source == 'SPECIAL_MACRO_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 2, mem_address + 8)
      else:
        pass
    
    #print(self)
  
  def __str__(self):
    return f'Object3D: Source: {self.source}, Model-ID: {self.model_id}, position: {repr(self.position)}, rotation: {repr(self.rotation)}, bparams: {repr(self.bparams)}, bscript: {hex(self.behaviour or 0)}, mem_pos: {hex(self.mem_address)}'