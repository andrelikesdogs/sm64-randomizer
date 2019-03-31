from Rom import ROM

from Constants import ALL_LEVELS

class Debug:
  def __init__(self, rom : ROM):
    self.rom = rom

  def list_course_ids(self):
    print(ALL_LEVELS)
    for level in ALL_LEVELS:
      print(level)
      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(level, filter=[0x0C]):
        print([hex(byte) for byte in data])
