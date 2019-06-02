from typing import List, Tuple

class TweaksFunctionality:
  def __init__(self, rom):
    self.rom = rom
  
  def add_asm_patch(self, changes : List[Tuple[int, bytes]]):
    self.rom.mark_checksum_dirty()

    for (position, data) in changes:
      self.rom.write_byte(position, data)