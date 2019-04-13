from Rom import ROM

class Object3D:
  source: str # SPECIAL_MACRO_OBJ, PLACE_OBJ, MACRO_OBJ, MARIO_SPAWN
  model_id: str
  position: tuple = (0, 0, 0) # (X, Y, Z)
  rotation: tuple = (0, 0, 0) # (X, Y, Z)
  behaviour: int = None # addr
  bparams: list = []
  mem_address: int = None
  memory_mapping: dict

  def __init__(self, source : str, model_id : str = None, position : tuple = None, rotation : tuple = None, behaviour : int = None, *bparams, **kwargs):
    self.source = source
    self.model_id = model_id
    self.position = position
    self.rotation = rotation
    self.behaviour = behaviour
    self.memory_mapping = {}

    for key, value in kwargs.items():
      setattr(self, key, value)

    for param in bparams:
      self.bparams.append(param)
    
  def set_addr(self, var : str, start : int, end : int):
    self.memory_mapping[var] = (int(start), int(end))

  def addr_for(self, var : str):
    return self.memory_mapping[var]