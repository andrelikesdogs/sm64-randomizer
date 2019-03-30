from Rom import ROM
from Constants import LEVEL_POSITIONS, LEVEL_SCRIPT_FUNCS

class LevelScript:
  def __init__(self, rom : ROM):
    self.rom = rom

  def get_cmds_in_level(self, level_position, filter=[]):
    (start_position, end_position) = level_position
    file = self.rom.file
    file.seek(start_position)

    cmd = None
    while cmd != 0x02:
      cmd = int.from_bytes(file.read(1), 'little')
      cmd_length = int.from_bytes(file.read(1), 'little')
      cmd_name = LEVEL_SCRIPT_FUNCS[cmd] if cmd in LEVEL_SCRIPT_FUNCS else "{0:x}".format(cmd)

      if not len(filter) or cmd_name in filter:
        cmd_data = file.read(cmd_length-2)
        yield (cmd_name, cmd_data)

      if file.tell() > end_position:
        print("Ending Level Sequence (end of bytes)")
        break

  def read_level_script(self, level_position):
    (start_position, end_position) = level_position
    file = self.rom.file
    file.seek(start_position)

    cmd = 0x0
    while cmd != 0x02:
      cmd = int.from_bytes(file.read(1), 'little')
      cmd_length = int.from_bytes(file.read(1), 'little')


      # move cursor
      file.seek(max(cmd_length-2, 1), 1)

      if file.tell() > end_position:
        print("Ending Level Sequence (end of bytes)")
        break

  def collect_poly_ids(self, level_positions):
    poly_ids = []

    for level_position in level_positions:
      for (cmd, data) in self.get_cmds_in_level(level_position, filter=["LOAD_POLY_WITHOUT_GEO", "LOAD_POLY_WITH_GEO"]):
        poly_ids.append(data[1])

    print(poly_ids)

    for level_position in LEVEL_POSITIONS.values():
      print("NEW LEVEL")
      #print(level_position)
      for (cmd, data) in self.get_cmds_in_level(level_position, filter=["PLACE_OBJECT"]):
        print(data.hex())
        act = data[0]
        poly_id = data[1]

        print({ "act": act, "poly_id": poly_id })

        x = int.from_bytes(data[2:4], 'little', signed=True)
        y = int.from_bytes(data[5:7], 'little', signed=True)
        z = int.from_bytes(data[8:10], 'little', signed=True)
        rx = int.from_bytes(data[11:13], 'little', signed=True)
        ry = int.from_bytes(data[14:16], 'little', signed=True)
        rz = int.from_bytes(data[17:19], 'little', signed=True)

        print((x, y, z), (rx, ry, rz))
        print('\n')

        #print('bb:')
        #print(data[20:24])
        #print('bs:')
        #print(data[25:28])
    