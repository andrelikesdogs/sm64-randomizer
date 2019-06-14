from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping
from Constants import BEHAVIOUR_NAMES

class Object3D(BaseMemoryRecord):
  source: str # SPECIAL_MACRO_OBJ, PLACE_OBJ, MACRO_OBJ, MARIO_SPAWN
  model_id: str
  current_area: int
  level: "Level" = None
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
      print(self.model_id)
      return f'Unknown (Model-ID: #{hex(self.model_id)}'

    if self.source == 'MARIO_SPAWN':
      return f'Mario\'s Spawn Point'

    return f'Unknown (Source: {self.source})'

  def remove(self, rom):
    if self.source == 'PLACE_OBJ':
      rom.write_byte(self.mem_address + 1, bytes([0x00])) # Set Model-ID to 0
    if self.source == 'MACRO_OBJ':
      rom.levelscripts[self.level].remove_macro_object(self)
    if self.source == 'SPECIAL_MACRO_OBJ':
      rom.levelscripts[self.level].remove_special_macro_object(self)


  def __init__(self, source, area_id, model_id, position, level, rotation = None, behaviour = None, bparams = [], mem_address = None):
    super().__init__()

    self.source = source
    self.area_id = area_id
    self.model_id = model_id
    self.position = position
    self.level = level
    self.rotation = rotation
    self.behaviour = behaviour
    self.behaviour_name = self.generate_name()
    self.bparams = bparams
    self.mem_address = mem_address
    
    if mem_address is not None:
      if source == 'PLACE_OBJ':
        self.add_mapping('position', ('int', 'int', 'int'), mem_address + 2, mem_address + 8)
        self.add_mapping('bparams', ('int', 'int', 'int', 'int'), mem_address + 14, mem_address + 18)
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
    return self.generate_name() + '\n' + f'Source: {self.source}, In-Area: {self.area_id}, Model-ID: {self.model_id}, position: {repr(self.position)}, rotation: {repr(self.rotation)}, bparams: {repr(self.bparams)}, bscript: {hex(self.behaviour or 0)}, mem_pos: {hex(self.mem_address)}'
    #return f'Object3D: Source: {self.source}, Model-ID: {self.model_id}, position: {repr(self.position)}, rotation: {repr(self.rotation)}, bparams: {repr(self.bparams)}, bscript: {hex(self.behaviour or 0)}, mem_pos: {hex(self.mem_address)}'