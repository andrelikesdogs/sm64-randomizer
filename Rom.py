from pathlib import Path
import shutil
import os
from platform import system, architecture
import subprocess
import time

from randoutils import pretty_print_table, generate_debug_materials, generate_obj_for_level_geometry
from Parsers.Level import Level
from Parsers.LevelScript import LevelScriptParser
from Constants import ALL_LEVELS

class ROM:
  def __init__(self, path, out_path):
    self.path = path
    self.out_path = out_path

    self.region = None
    self.endianess = None
    self.file_stats = None
    self.rom_type = None

    self.segments = {}
    self.levelscripts = {}

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

    if self.file_stats.st_size > 8388608:
      self.rom_type = 'EXTENDED'
    elif self.file_stats.st_size == 8388608:
      self.rom_type = 'VANILLA'
    else:
      print("Warning: Could not determine ROM-Type from size")

  def try_extend(self):
    # make copy
    in_path_parts = str(self.path).split('.')
    ext_path_parts = [*in_path_parts[:-1], 'ext', in_path_parts[-1]]
    ext_path = '.'.join(ext_path_parts)
    print("Creating Extended ROM as ", ext_path)
    shutil.copy(self.path, ext_path)

    # close initial file
    #self.file.close()

    operating_sys = system()
    #arch = architecture()
    #bits = arch[0]
    args = ['-s', '24', str(self.path), ext_path]
    if operating_sys == 'Darwin':
      subprocess.check_call(['./3rdparty/sm64extend_mac_x64', *args])
    elif operating_sys == 'Windows':
      subprocess.check_call(['3rdparty/sm64extend_win_x86.exe', *args])
    else:
      raise Exception("Sorry, no sm64extend is available for your OS. Please raise an issue on our github, and we'll try to add it!")
    
    return ext_path

  def read_levels(self):
    for level in ALL_LEVELS:
      if 'DEBUG' in os.environ:
        if not os.path.exists(os.path.join("dumps", "level_scripts")):
          os.makedirs(os.path.join("dumps", "level_scripts"))
        
        with open(os.path.join("dumps", "level_scripts", "{level.name}.txt"), "w+") as dump_target:
          self.levelscripts[level] = LevelScriptParser.parse_for_level(self, level)
          dump_target.write(self.levelscripts[level].dump())
          #print(f'{level.name} has {len(self.level_scripts[level].objects)} objects')

          #special_objs = list(filter(lambda x: x.source == "SPECIAL_MACRO_OBJ", self.level_scripts[level].objects))
          #macro_objs = list(filter(lambda x: x.source == "MACRO_OBJ", self.level_scripts[level].objects))
          #normal_objs = list(filter(lambda x: x.source == "PLACE_OBJ", self.level_scripts[level].objects))
          #print(f' - {len(special_objs)} Special 0x2E Objects')
          #print(f' - {len(macro_objs)} Macro 0x39 Objects')
          #print(f' - {len(normal_objs)} Normal 0x24 Objects')

        if not os.path.exists(os.path.join("dumps", "level_geometry")):
          os.makedirs(os.path.join("dumps", "level_geometry"))
        
        with open(os.path.join("dumps", "level_geometry", "debug.mtl"), "w+") as mtl_debug:
          mtl_debug.write(generate_debug_materials())
          
        with open(os.path.join("dumps", "level_geometry", "{level.name}.obj"), "w+") as obj_output:
          data = generate_obj_for_level_geometry(self.levelscripts[level].level_geometry)
          obj_output.write(data)
          
      else:
        self.levelscripts[level] = LevelScriptParser.parse_for_level(self, level)

  def print_info(self):
    pretty_print_table("ROM Properties", {
      'Loaded ROM': self.file.name,
      'Output ROM': self.target.name,
      'ROM Endianness': self.endianess.upper(),
      'ROM Region': self.region,
      'ROM Type': self.rom_type
    })

  def set_initial_segments(self):
    self.set_segment(0x15, self.read_integer(0x2A622C, 4), self.read_integer(0x2A6230, 4))
    pass

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

  def set_segment(self, segment_num, segment_start, segment_end):
    self.segments[segment_num] = (segment_start, segment_end)
  
  def read_segment_addr(self, addr):
    segment_address = addr & 0x00FFFFFF
    segment_id = (addr & 0xFF000000) >> 24

    #print("Segment requested:", hex(segment_id), hex(segment_address))

    if segment_id == 0x0:
      return None

    if segment_id not in self.segments:
      return None

    (segment_start, _) = self.segments[segment_id]
    return segment_start + segment_address

  def read_segment_id(self, addr):
    return ((addr & 0xFF000000) >> 24)
  
  def read_segment_end(self, addr):
    segment_id = (addr & 0xFF000000) >> 24

    #print("Segment requested:", hex(segment_id), hex(segment_address))

    if segment_id == 0x0:
      return None

    if segment_id not in self.segments:
      return None

    (_, segment_end) = self.segments[segment_id]

    return segment_end

  def get_segment(self, seg_id):
    if seg_id not in self.segments:
      return None

    return self.segments[seg_id]

  ''' Read Methods '''
  def read_set_cursor(self, position):
    self.file.seek(position, 0)

  def read_byte(self, position = None):
    if position:
      self.file.seek(position, 0)
    return self.file.read(1)
  
  def read_bytes(self, position = None, length : int = 1):
    if position:
      self.file.seek(position, 0)
    return self.file.read(length)

  def read_integer(self, position = None, length : int = 1, signed = False):
    if position:
      self.file.seek(position, 0)

    if length == 1:
      return self.file.read(1)[0]
    else:
      data = self.file.read(length)
      return int.from_bytes(data, self.endianess, signed=signed)

  ''' Write Methods '''
  def write_byte(self, position, data : bytes):
    self.target.seek(position, 0)
    self.target.write(data)

  def write_integer(self, position, num : int, length : int = 1, signed = False):
    self.target.seek(position, 0)
    self.target.write(num.to_bytes(length, self.endianess, signed=signed ))

  def write_word(self, position, string : str):
    self.target.seek(position, 0)
    self.target.write(string)
