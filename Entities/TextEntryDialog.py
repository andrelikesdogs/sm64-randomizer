from typing import NamedTuple
from Entities.BaseMemoryRecord import BaseMemoryRecord, MemoryMapping

class TextEntryDialog(BaseMemoryRecord):
  memory_address_text: int = None
  memory_address_pointer: int = None
  text: str = None
  entry_id: int = None

  def __init__(self, entry_id, text, offset, mem_address_pointer : int = None, mem_address_text : int = None):
    super().__init__()

    self.entry_id = entry_id
    self.text = text
    self.memory_address_pointer = mem_address_pointer
    self.memory_address_text = mem_address_text
    self.offset = offset

    self.add_mapping("offset", "uint", mem_address_pointer + 14, mem_address_pointer + 16)