from pathlib import Path
import shutil
import os

from randoutils import pretty_print_table
from Level import Level
from Constants import LEVEL_SCRIPT_FUNCS

class ROM:
  def __init__(self, path, out_path):
    self.path = path
    self.out_path = out_path

    self.region = None
    self.endianess = None
    self.file_stats = None
    self.rom_type = None

  def __enter__(self):
    self.file_stats = os.stat(self.path)
    self.file = open(self.path, 'rb')
    shutil.copyfile(self.path, self.out_path)
    self.target = open(self.out_path, 'b+r')
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.file.close()
    self.target.close()

  def verify_header(self):
    self.file.seek(0)
    header = self.file.read(0x40)
    
    # read endianess
    endian_bytes = header[0:2]
    if endian_bytes == bytes([0x80, 0x37]):
      self.endianess = 'big'
    elif endian_bytes == bytes([0x37, 0x80]):
      self.endianess = 'mixed'
    elif endian_bytes == bytes([0x40, 0x12]):
      self.endianess = 'little'
    else:
      raise Exception('invalid endianess in ROM')

    # read region
    region_byte = header[0x3E]
    region_byte_alt = header[0x3F]

    if region_byte == 0x45:
      self.region = 'NORTH_AMERICA'
    elif region_byte == 0x50:
      self.region = 'EUROPE'
    elif region_byte == 0x4A:
      if region_byte_alt < 3:
        self.region = 'JAPAN'
      else:
        self.region = 'JAPAN_SHINDOU'
    elif region_byte == 0x00:
      self.region = 'CHINESE'
    else:
      raise Exception('invalid region in ROM')

    if self.file_stats.st_size == 25165824:
      self.rom_type = 'EXTENDED'
    elif self.file_stats.st_size == 8388608:
      self.rom_type = 'VANILLA'
    else:
      print("Warning: Could not determine ROM-Type from size")

    #return header in KNOWN_HEADERS

  def print_info(self):
    pretty_print_table("ROM Properties", {
      'Loaded ROM': self.file.name,
      'Output ROM': self.target.name,
      'ROM Endianness': self.endianess.upper(),
      'ROM Region': self.region,
      'ROM Type': self.rom_type
    })

  def read_cmds_from_level_block(self, level: Level, filter=[]):
    (start_position, end_position) = level.address
    self.file.seek(start_position, 0)

    cmd = None
    cmd_count = 0
    cursor = start_position
    while True:
      cmd_count = cmd_count + 1

      # if this function is used recursively, this would get lost
      self.file.seek(cursor, 0)
      cmd = self.file.read(1)[0]
      cmd_length = max(self.file.read(1)[0] - 2, 0)
      if cmd == 0x02:
        #print("Ending Level Sequence (0x02 END_LEVEL)")
        break

      cursor = cursor + cmd_length + 2
      #print('position: ' + str(cursor))

      if not len(filter) or cmd in filter:
        # read data and output
        cmd_data = self.file.read(cmd_length)
        yield (cmd, cmd_data, cursor - cmd_length)

      if cursor > end_position:
        #print("Ending Level Sequence (end of bytes)")
        break

  def read_geo_from_block(self, start, end):
    self.file.seek(start, 0)


'''
  def verify_levels(self):
    for (start_position, end_position) in LEVEL_POSITIONS:
      print(self.file.seek(start_position))

      # read cmd code
      cmd = ''
      while cmd != 0x02:
        cmd = int.from_bytes(self.file.read(1), 'big')
        cmd_length = int.from_bytes(self.file.read(1), 'big')

        # move pos by cmd length (minus 2 bytes for the cmd and length)
        self.file.seek(cmd_length - 2, 1)'''

'''
  def alter_level_music(self, level_index, music_id):
    (start_position, end_position) = LEVEL_POSITIONS[level_index]
    print(self.file.seek(start_position))

    # read cmd code
    cmd = ''
    while cmd != 0x02:
      cmd = int.from_bytes(self.file.read(1), 'little')
      cmd_length = int.from_bytes(self.file.read(1), 'little')

      cmd_name = LEVEL_CMD_TITLES[cmd] or 'UNKNOWN'

      if cmd == 0x36:
        # move cursor to sequence id pos
        sequence_id_pos = self.file.seek(3, 1)
        print(cmd, cmd_length, int.from_bytes(self.file.read(1), 'little'))
        self.target.seek(sequence_id_pos)
        self.target.write(music_id.to_bytes(1, 'little'))
        break

      # move pos by cmd length (minus 2 bytes for the cmd and length)
      self.file.seek(cmd_length - 2, 1)'''