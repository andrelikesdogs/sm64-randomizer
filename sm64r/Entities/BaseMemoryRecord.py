from typing import NamedTuple, Union
import math

class MemoryMapping(NamedTuple):
  address_start: int
  address_end : int
  data_type: Union[str, tuple] # uint, int, 

  @property
  def size(self):
    return self.address_end - self.address_start

class BaseMemoryRecord:
  memory_address = None
  memory_mapping = None

  def __init__(self):
    # if this is not done, all memory mappings share one dict instance
    self.memory_mapping = {}

  def set(self, rom : 'ROM', key, value):
    if key not in self.memory_mapping:
      raise ValueError(f'"{key}" has no memory mapping')

    memory_information = self.memory_mapping[key]

    if memory_information.data_type == 'uint':
      rom.write_integer(memory_information.address_start, value, memory_information.size, False)
      setattr(self, key, value)
    elif memory_information.data_type == 'int':
      rom.write_integer(memory_information.address_start, value, memory_information.size, True)
      setattr(self, key, value)
    elif type(memory_information.data_type) == tuple:
      size = math.floor(memory_information.size / len(memory_information.data_type))
      setattr(self, key, value)
      for index, value_type in enumerate(list(memory_information.data_type)):
        rom.write_integer(memory_information.address_start + index * size, value[index], size, value_type == 'int')
    else:
      raise TypeError(f'Datatype unknown, can\'t format this data for writing')

  def add_mapping(self, variable_key : str, data_type :str, start : int, end : int = None):
    if not end:
      end = start + 1
    
    self.memory_mapping[variable_key] = MemoryMapping(start, end, data_type)