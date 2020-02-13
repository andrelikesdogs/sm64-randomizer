from pathlib import Path
import shutil
import os
from io import BytesIO
from platform import system, architecture
import subprocess
import time
import trimesh
import sys
import binascii

from .Randoutils import pretty_print_table, generate_debug_materials, generate_obj_for_level_geometry
from .Level import Level
from .Parsers.LevelScript import LevelScriptParser
from .Constants import ALL_LEVELS, application_path
from .Config import Config
from .RandomModules.Textures import TextureAtlas
from .Constants import application_path


class ROM:
  def __init__(self, path, out_path, alignment=1):
    self.path = path
    self.out_path = out_path

    self.config = None

    self.region = None
    self.endianess = None
    self.file_stats = None
    self.rom_type = None
    self.header = None
    self.checksum = None
    self.alignment = alignment
    self.require_checksum_fix = False

    self.macro_table_position = None
    self.special_macro_table_position = None

    self.segments = {}
    self.segments_sequentially = []
    self.levelscripts = {}

    self.segment_idx = 0

  def __enter__(self):
    self.file_stats = os.stat(self.path)
    self.file = open(self.path, 'rb')
    shutil.copyfile(self.path, self.out_path)
    self.target = open(self.out_path, 'b+r')
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.file.close()
    self.target.close()

    # apply checksum fix after saving, if necessary
    if self.require_checksum_fix:
      print("Applying checksum fix...")
      try:
        operating_sys = system()
        if operating_sys == 'Darwin':
          subprocess.check_call([os.path.join(application_path, '3rdparty/n64cksum_mac_x64'), str(self.out_path)])
        elif operating_sys == 'Windows':
          subprocess.check_call([os.path.join(application_path, '3rdparty/n64cksum_win_x86'), str(self.out_path)])
        elif operating_sys == 'Linux':
          subprocess.check_call([os.path.join(application_path, '3rdparty/n64cksum_ubuntu_x64'), str(self.out_path)])
        else:
          raise Exception(f"No n64checksum binary for this operating system: {operating_sys}")
        print("Success!")
      except Exception as err:
        print("Unfortunately, the checksum fix failed. Please manually fix your ROMs checksum. Feel free to report this issue to github.com/andre-meyer/sm64-randomizer/issues")
        raise err

  def swap_mixed_to_big(self):
    #print("Converting from Mixed to Big Endianess")

    self.file.seek(0)
    data = self.file.read()

    mem_rom = BytesIO()
    
    for i in range(0, len(data), 2):
      mem_rom.write(bytes([data[i + 1]]))
      mem_rom.write(bytes([data[i]]))

    self.file.close()
    self.file = mem_rom

  def verify_header(self, repeated=False):
    self.file.seek(0)
    header = self.file.read(0x40)
    
    # read endianess
    endian_bytes = header[0:2]
    if endian_bytes == bytes([0x80, 0x37]):
      # Big Endianess (z64)
      self.endianess = 'big'
    elif endian_bytes == bytes([0x37, 0x80]):
      # Mixed Endianess (Converts to Big) (n64/v64)
      self.swap_mixed_to_big()
      self.endianess = 'big'

      if not repeated:
        return self.verify_header(True)
    elif endian_bytes == bytes([0x40, 0x12]):
      # Little Endianess
      self.endianess = 'little' # (n64)
    else:
      raise Exception('invalid endianess in ROM')

    # b'Zc\xff+'
    # b'cZ+\xff'

    self.header = header[0x10:0x14]
    if self.endianess in ['big', 'little']:
      self.checksum = int.from_bytes(self.header, self.endianess)

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
    else:
      self.rom_type = 'VANILLA'
    
  def try_extend(self, alignment=1):
    # make copy
    path = Path(self.path)
    
    ext_path = None
    try:
      ext_path = path.with_suffix(f'.ext{path.suffix}')
    except:
      print(f"Could not read \"{path.name}\"")
      sys.exit(1)
    print("Creating Extended ROM inplace")
    shutil.copy(path, ext_path)

    # close initial file
    self.file.close()

    operating_sys = system()
    args = ['-s', '24', '-a', str(alignment), str(path), str(ext_path)]
    if operating_sys == 'Darwin':
      subprocess.check_call([os.path.join(application_path, '3rdparty/sm64extend_mac_x64'), *args])
    elif operating_sys == 'Linux':
      subprocess.check_call([os.path.join(application_path, '3rdparty/sm64extend_ubuntu_x64'), *args])
    elif operating_sys == 'Windows':
      subprocess.check_call([os.path.join(application_path, '3rdparty/sm64extend_win_x86.exe'), *args])
    else:
      raise Exception("Sorry, no sm64extend is available for your OS. Please raise an issue on our github, and we'll try to add it!")
    
    return str(ext_path)

  def mark_checksum_dirty(self):
    self.require_checksum_fix = True

  def read_levels(self):
    # sorted levels by course_id for reliable sequential segment reference
    ow_levels = []
    non_ow_levels = []
    for level in self.config.levels:
      # split overworld and non-overworld for warp gathering
      if "overworld" in level.properties:
        ow_levels.append(level)
      else:
        non_ow_levels.append(level)

    ow_levels.sort(key=lambda x: x.course_id)
    non_ow_levels.sort(key=lambda x: x.course_id)

    levels_to_process = [
      # Hardcoded entries
      Level(0x00, "Main Entry"),
      Level(0x26, "Main Menu"),
      *ow_levels,
      *non_ow_levels
    ]

    # !!! attention: if you touch this all sequential references will be different !!!
    # 0x0 level to read scripts first, idk if it makes sense actually
    for level in levels_to_process:
      #if level.offset is not None:
      #  self.levelscripts[level] = LevelScriptParser.parse_from_offset(self, level.offset, None, 0, level=level)
      #else:
      self.levelscripts[level] = LevelScriptParser.parse_for_level(self, level)
      self.levelscripts[level].level_geometry.process()

      if 'SM64R' in os.environ:
        if os.environ['SM64R'] == 'EXPORT':
          for (area_id, mesh) in self.levelscripts[level].level_geometry.area_geometries.items():
            with open(os.path.join("dumps", "level_geometry", f"{level.name}_{hex(area_id)}.stl"), "wb+") as obj_output:
              mesh.export(obj_output, 'stl')
        if os.environ['SM64R'] == 'PLOT':
          self.levelscripts[level].level_geometry.plot()
      
      if 'SM64R' in os.environ and os.environ['SM64R'] == 'DUMP':
        if not os.path.exists(os.path.join("dumps", "level_scripts")):
          os.makedirs(os.path.join("dumps", "level_scripts"))
        
        if not os.path.exists(os.path.join("dumps", "level_plots")):
          os.makedirs(os.path.join("dumps", "level_plots"))

        if not os.path.exists(os.path.join("dumps", "level_geometry")):
          os.makedirs(os.path.join("dumps", "level_geometry"))
        
        with open(os.path.join("dumps", "level_scripts", f"{level.name}.txt"), "w+") as dump_target:
          dump_target.write(self.levelscripts[level].dump())
          #print(f'{level.name} has {len(self.level_scripts[level].objects)} objects')

          #special_objs = list(filter(lambda x: x.source == "SPECIAL_MACRO_OBJ", self.level_scripts[level].objects))
          #macro_objs = list(filter(lambda x: x.source == "MACRO_OBJ", self.level_scripts[level].objects))
          #normal_objs = list(filter(lambda x: x.source == "PLACE_OBJ", self.level_scripts[level].objects))
          #print(f' - {len(special_objs)} Special 0x2E Objects')
          #print(f' - {len(macro_objs)} Macro 0x39 Objects')
          #print(f' - {len(normal_objs)} Normal 0x24 Objects')
        
        with open(os.path.join("dumps", "level_geometry", "debug.mtl"), "w+") as mtl_debug:
          mtl_debug.write(generate_debug_materials())
        
  def print_info(self):
    pretty_print_table("ROM Properties", {
      'Loaded ROM': self.file.name,
      'Output ROM': self.target.name,
      'Checksum': hex(self.checksum),
      'ROM Endianness': self.endianess.upper(),
      'ROM Region': self.region,
      'ROM Type': self.rom_type,
      'Config File': self.config.filename,
      'Config Used': self.config.rom_settings["name"]
    })

  def read_configuration(self):
    configuration = Config.find_configuration(self.checksum)

    if not configuration:
      raise TypeError(f"Could not find a configuration for the loaded rom. Checksum: {hex(self.checksum)}")

    print("Loaded Configuration")
    print(configuration)

    for defined_segment in configuration.rom_settings["defined_segments"]:
      segment_id = defined_segment["segment"]
      segment_start = None
      segment_end = None

      if "read_addresses" in defined_segment:
        segment_start = self.read_integer(defined_segment["start"], 4)
        segment_end = self.read_integer(defined_segment["end"], 4)
      else:
        segment_start = defined_segment["start"]
        segment_end = defined_segment["end"]
        
      self.set_segment(segment_id, segment_start, segment_end)
    
    self.config = configuration
    self.macro_table_position = configuration.rom_settings["macro_table_address"]
    self.special_macro_table_position = configuration.rom_settings["special_macro_table_address"]

  def set_segment(self, segment_num, segment_start, segment_end, mio0=False):
    segment_positions = (segment_start, segment_end)

    self.segments_sequentially.append(segment_positions)
    self.segments[segment_num] = segment_positions
  
  def match_segments(self, address):
    """ Matches segments with an address. This can be used to find in which segment a hardcoded address will be, if used with an unaligned extended ROM.
    
    Arguments:
        address {int} -- Address to find segment information for
    """
    #print(f"matching for {hex(address)} in {len(self.segments_sequentially)} segments")
    found_at = []
    for segment_idx, (address_start, address_end) in enumerate(self.segments_sequentially):
      if address >= address_start and address < address_end:
        offset = address - address_start
        print(f'{hex(address)} found in segment index #{segment_idx}, offset: {hex(offset)}')
        found_at.append((segment_idx, offset))
    
    if not len(found_at):
      print("not found")

  def read_cmds_from_level_block(self, level, filter=[]):
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
        break

  def read_segment_addr(self, addr):
    segment_address = addr & 0x00FFFFFF
    segment_id = (addr & 0xFF000000) >> 24

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

  def write_bytes(self, position, data : bytes):
    self.target.seek(position, 0)
    self.target.write(data)

  def write_integer(self, position, num : int, length : int = 1, signed = False):
    self.target.seek(position, 0)
    self.target.write(num.to_bytes(length, self.endianess, signed=signed ))

  def write_word(self, position, string : str):
    self.target.seek(position, 0)
    self.target.write(string)
