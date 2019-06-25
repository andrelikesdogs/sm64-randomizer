from Parsers.Level import Level, LevelCommand
from Parsers.CollisionPresets import CollisionPresetParser, SPECIAL_CD_WITH_PARAMS
from Entities.Object3D import Object3D
from Entities.Warp import Warp
from Entities.LevelGeometry import LevelGeometry
from Constants import LVL_MAIN
import Constants
import sys
from math import floor

from randoutils import format_binary

instances = {}
addresses_checked = []

MACRO_ROT_Y_MUL = 2.8125
SPCL_MACRO_ROT_Y_MUL = 1.40625

class LevelScriptParser:
  @staticmethod
  def parse_from_offset(rom : 'ROM', start : int, end : int = None, layer = 0, level : Level = None):
    if start in instances:
      return instances[start]
    else:
      instances[start] = LevelScriptParser(rom, start, end, layer, level)
      return instances[start]

  @staticmethod
  def parse_for_level(rom : 'ROM', level : Level):
    (start, end) = rom.get_segment(0x15)
    return LevelScriptParser(rom, start, end, 0, level)

  def __init__(self, rom : 'ROM', start : int, end : int = None, layer = 0, level : Level = None):
    #print("LevelScriptParser loaded for " + level.name)
    self.rom = rom
    self.address_start = start
    self.address_end = end or start + 0xFFFFFFFF # Todo: Actual segment length missing
    self.objects = []
    self.warps = []

    self.commands = []
    self.mario_spawn = None
    self.layer = layer
    self.level = level
    self.current_area = 0x0
    self.water_boxes = []

    self.macro_tables = {}
    self.macro_object_tables = {}
    
    self.special_macro_tables = {}
    self.special_macro_object_tables = {}

    self.level_geometry = LevelGeometry(level)
    self.level_collisions = []

    self.checked_offsets = []

    self.process(self.address_start, self.address_end)

  def process(self, start, end):
    #print(f'Decoding LevelScript: {hex(start)} to {hex(int(end))} (#{self.layer})')
    self.layer += 1
    self.checked_offsets.append(start)
    cmd_id = None
    length = None
    command = None

    cursor = start

    try:
      while cursor < end:
        cmd_id = self.rom.read_integer(cursor)
        length = self.rom.read_integer() - 2

        if length < 0:
          cursor += 1
          continue
        if length == 0:
          return
        
        data = self.rom.read_bytes(cursor + 2, length)
        command = LevelCommand.from_id(cmd_id, length=length, data=data, position=cursor + 2)
        
        self.commands.append((self.layer, command))
        if command.identifier == 0x00 or command.identifier == 0x01:
          """ 0x00 LOAD_RAW_DATA_AND_JUMP_PLUS_CALL or 0x01 LOAD_RAW_DATA_AND_JUMP_PLUS_CALL """
          
          segment_id = self.rom.read_integer(cursor + 3)
          segment_addr = self.rom.read_integer(cursor + 4, 4)
          segment_end = self.rom.read_integer(cursor + 8, 4)
          #print(command.name, hex(command.identifier), hex(length+2), format_binary(data))
          self.rom.set_segment(segment_id, segment_addr, segment_end)

          segment_jmp_offset = self.rom.read_integer(cursor + 12, 4)
          #print("jump offset", hex(segment_jmp_offset))
          jmp_segment_start = self.rom.read_segment_addr(segment_jmp_offset)

          # Make sure we're not parsing this section already
          if jmp_segment_start == None:
            pass
            #print("Warning: jmp offset segment not found")
          elif jmp_segment_start in self.checked_offsets:
            pass
            #print("Warning: Infinite Loop Detected")
          else:
            #print(f"{hex(command.identifier)} Jump to Segment", hex(cursor), hex(segment_id))
            self.process(jmp_segment_start, jmp_segment_start + 0xFFFF)
            self.layer -= 1
          
        elif command.identifier == 0x05:
          """ 0x05 JUMP_TO_ADDRESS """
          segment_jmp_offset = self.rom.read_integer(cursor + 4, 4)
          jmp_segment_start = self.rom.read_segment_addr(segment_jmp_offset)

          # Make sure we're not parsing this section already
          if jmp_segment_start == None:
            pass
            #print("Warning: jmp offset segment not found")
          elif jmp_segment_start in self.checked_offsets:
            pass
            #print("Warning: Infinite Loop Detected")
          else:
            #print(f"{hex(command.identifier)} Jump to Segment", hex(cursor), hex(segment_jmp_offset))
            self.process(jmp_segment_start, jmp_segment_start + 0xFFFF)
            self.layer -= 1
          break
        elif command.identifier == 0x06:
          """ 0x06 PUSH """
          
          segment_jmp_offset = self.rom.read_integer(cursor + 4, 4)
          jmp_segment_start = self.rom.read_segment_addr(segment_jmp_offset)

          # Make sure we're not parsing this section already
          if jmp_segment_start == None:
            pass
            #print("Warning: jmp offset segment not found")
          elif jmp_segment_start in self.checked_offsets:
            pass
            #print("Warning: Infinite Loop Detected")
          else:
            #print(f"{hex(command.identifier)} Jump to Segment", hex(cursor), hex(segment_jmp_offset))
            result = self.process(jmp_segment_start, jmp_segment_start + 0xFFFF)
            if result == 0x02:
              break
            self.layer -= 1
        
        elif command.identifier == 0x07:
          """ 0x07 POP """
        
          if self.layer > 1:
            # only allow POP if we're currently in a stack
            break

        elif command.identifier == 0x0C:
          """ 0x0C CONDITIONAL_JUMP """
        
          level_id = self.rom.read_integer(cursor + 7)

          # All 0x0C Conditional Jumps are *mostly* used to jump to the right levels address.
          # That's why we can make this behaviour act according to the currently targeted level.
          if self.level is not None and self.level.level_id is not None and level_id == self.level.level_id:
            segment_jmp_offset = self.rom.read_integer(cursor + 8, 4)
            jmp_segment_start = self.rom.read_segment_addr(segment_jmp_offset)

            # Make sure we're not parsing this section already
            if jmp_segment_start is None:
              print("Warning: jmp offset segment not found")
            elif jmp_segment_start in self.checked_offsets:
              print("Warning: Infinite Loop Detected")
            else:
              self.process(jmp_segment_start, jmp_segment_start + 0xFFFFFF)
              self.layer -= 1
          
          #break
        elif command.identifier == 0x17: 
          """ 0x17 ROM_TO_SEGMENT """

          segment_id = self.rom.read_integer(cursor + 3)
          segment_addr = self.rom.read_integer(cursor + 4, 4)
          segment_end = self.rom.read_integer(cursor + 8, 4)
          
          self.rom.set_segment(segment_id, segment_addr, segment_end)
        elif command.identifier == 0x18 or command.identifier == 0x1A:
          """ 0x18 MIO0_DECOMPRESS or 0x1A MIO0_DECOMPRESS_TEXTURES """
          #print(command.name, hex(command.identifier), hex(length+2), format_binary(data))
          segment_id = self.rom.read_integer(cursor + 3)
          begin_mio0 = self.rom.read_integer(cursor + 4, 4)
          segment_end = self.rom.read_integer(cursor + 8, 4)
          segment_addr = self.rom.read_integer(begin_mio0 + 12) + begin_mio0

          self.rom.set_segment(segment_id, segment_addr, segment_end, mio0=True)
        elif command.identifier == 0x2E:
          if self.rom.rom_type == 'EXTENDED':
            """ 0x2E LOAD_COLLISION """
            segment_addr = self.rom.read_integer(cursor + 4, 4)
            segment_start = self.rom.read_segment_addr(segment_addr)

            if segment_start:
              #print(f'reading 0x2E from segment {hex(self.rom.read_segment_id(segment_addr))}: {hex(start)} to {hex(end)}')
              segment_end = self.rom.read_segment_end(segment_addr)
              self.process_special_objects_level(segment_start, segment_end)
        elif command.identifier == 0x24:
          """ 0x24 PLACE_OBJECT """
          # Example: 24 18 01 56  06 64 10 92  EA 41 00 00  FF 6D 00 00  00 00 00 00  13 00 01 F4
          model_id = self.rom.read_integer(cursor + 3)
          position = (self.rom.read_integer(cursor + 4, 2, True), self.rom.read_integer(cursor + 6, 2, True), self.rom.read_integer(cursor + 8, 2, True))
          rotation = (self.rom.read_integer(cursor + 10, 2, True), self.rom.read_integer(cursor + 12, 2, True), self.rom.read_integer(cursor + 14, 2, True))
          (b1, b2, b3, b4) = tuple([self.rom.read_integer(cursor + 16 + n) for n in range(4)])
          b_script = self.rom.read_integer(cursor + 20, 4)

          self.objects.append(Object3D("PLACE_OBJ", self.current_area, model_id, position, self.level, rotation, b_script, [b1, b2, b3, b4], cursor + 2))
        elif command.identifier == 0x39:
          if self.rom.rom_type == 'EXTENDED':
            """ 0x39 PLACE_MACRO_OBJECTS """
            #print(self.level.name)
            #print("Found Macro")
            #print(format_binary(data))
            # Length < 6 makes no sense
            if length >= 6:
              segment_addr = self.rom.read_integer(cursor + 4, 4)
              segment_start = self.rom.read_segment_addr(segment_addr)
              #print(hex(segment_start) if segment_start else None, hex(segment_addr))
              if segment_start:
                segment_end = self.rom.read_segment_end(segment_addr)
                self.process_macro_objects(segment_start, segment_end)
        elif command.identifier == 0x1F:
          """ 0x1F START_AREA_AND_LOAD_GEODATA """
          area_id = self.rom.read_integer(cursor + 2)
          area_segment_addr = self.rom.read_integer(cursor + 4, 4)
          segment_start = self.rom.read_segment_addr(segment_addr)
          segment_id = self.rom.read_segment_id(segment_addr)

          #if segment_start and segment_id:
            #self.rom.set_segment(segment_id, segment_start, segment_start + 0xFFFF, area_id)
          
          #print("Loading Area", hex(area_id))
          self.current_area = area_id
        elif command.identifier == 0x26:
          """ 0x26 CONNECT_WARPS """
          warp_id = self.rom.read_integer(cursor + 2)
          to_course_id = self.rom.read_integer(cursor + 3)
          to_area_id = self.rom.read_integer(cursor + 4)
          to_warp_id = self.rom.read_integer(cursor + 5)
          has_checkpoint = self.rom.read_integer(cursor + 6) == 0x80
          self.warps.append(Warp("NORMAL", warp_id, to_area_id, to_course_id, to_warp_id, self.current_area, has_checkpoint, mem_address = cursor + 2))
        elif command.identifier == 0x27:
          """ 0x27 SETUP_PAINTING_WARP """
          warp_id = self.rom.read_integer(cursor + 2)
          to_course_id = self.rom.read_integer(cursor + 3)
          to_area_id = self.rom.read_integer(cursor + 4)
          to_warp_id = self.rom.read_integer(cursor + 5)
          has_checkpoint = self.rom.read_integer(cursor + 6) == 0x80
          self.warps.append(Warp("PAINTING", warp_id, to_area_id, to_course_id, to_warp_id, self.current_area, has_checkpoint, mem_address = cursor + 2))
        elif command.identifier == 0x2B:
          """ 0x2B SET_MARIOS_DEFAULT_POSITION """
          spawn_area_id = self.rom.read_integer(cursor + 2)
          rotation_y = self.rom.read_integer(cursor + 4, 2, True)
          position = (self.rom.read_integer(cursor + 6, 2, True), self.rom.read_integer(cursor + 8, 2, True), self.rom.read_integer(cursor + 10, 2, True))
          self.objects.append(Object3D("MARIO_SPAWN", spawn_area_id, None, position, self.level, (None, rotation_y, None), mem_address = cursor + 2))
          #print(self.level.name, spawn_area_id, rotation_y, position)
        elif command.identifier == 0x20:
          """ 0x20 END_AREA """
          #print("Ending Area", hex(self.current_area))
          self.current_area = None
        elif command.identifier == 0x02: 
          """ END_LEVEL_DATA """
          break

        cursor = cursor + length + 2
    except Exception as err:
      #print(err)
      #print("Decoder Failed in Layer: ", self.layer)
      #print(hex(cmd_id))
      #print("Last Start Offset:", hex(start))
      #print("Current Cursor:", hex(cursor))
      raise err

    return command.identifier if command else None

  def load_area(self, data):
    #print("Trying to load area", hex(data))
    pass
  
  def remove_macro_object(self, object3d : Object3D):
    if object3d not in self.macro_object_tables:
      raise Exception(f"Object has no entry in macro table list: {str(object3d)}")
    
    start = self.macro_object_tables[object3d]
    macro_table = self.macro_tables[start]

    index_to_remove = None
    idx = 0
    for entry in macro_table["entries"]:
      if entry["object3d"] == object3d:
        index_to_remove = idx
        break
      idx += 1
    
    del macro_table["entries"][index_to_remove]
    self.update_macro_objects(start)

  def update_macro_objects(self, start):
    if start not in self.macro_tables:
      raise Exception(f"{hex(start)} was not found in macro table entries")
    macro_table = self.macro_tables[start]

    cursor = start
    for index, entry in enumerate(macro_table["entries"]):
      self.rom.write_byte(cursor, entry["bytes"])

      if index > macro_table["entry_count_original"]:
        print("about to overwrite...:")
        print(format_binary(self.rom.read_bytes(cursor, 10)))
      cursor += 10
    
    # end with 0x1E preset
    self.rom.write_byte(cursor, bytes([0x00, 0x1E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    #print(f'Level {self.level.name} has {len(macro_table["entries"])} macro objects')
    #print(f'Start at {hex(start)} til {hex(cursor)}')
  
  def add_macro_object(self, start, preset_id, rot_y, x, y, z, bparam1 = 0x0, bparam2 = 0x0):
    if start not in self.macro_tables:
      raise Exception(f"{hex(start)} was not found in macro table entries")
    macro_table = self.macro_tables[start]

    preset_table = CollisionPresetParser.get_instance(self.rom).entries
    preset_data = preset_table[preset_id]

    object3d = Object3D("MACRO_OBJ", self.current_area, preset_data.model_id, (x, y, z), self.level, (0, rot_y, 0), preset_data.behaviour_addr, bparams=[bparam1, bparam2])
    x_bytes = x.to_bytes(2, self.rom.endianess, signed=True)
    y_bytes = y.to_bytes(2, self.rom.endianess, signed=True)
    z_bytes = z.to_bytes(2, self.rom.endianess, signed=True)

  # preset_id = preset_and_rot & 0x1FF # last 9 bit
  # rot_y = preset_and_rot & 0xFE00 # first 7 bit
    
    rot_y = int(float(rot_y) / MACRO_ROT_Y_MUL)

    rot_clamped = (rot_y & 0x7F) << 9
    preset_id_clamped = (preset_id & 0x01FF)
    preset_and_rot = rot_clamped | preset_id_clamped
    preset_and_rot_bytes = preset_and_rot.to_bytes(2, self.rom.endianess)

    macro_row = preset_and_rot_bytes + x_bytes + y_bytes + z_bytes + bytes([bparam1]) + bytes([bparam2])
    
    macro_table["entries"].append(
      dict(
        object3d=object3d,
        bytes=macro_row
      )
    )
    self.update_macro_objects(start)

  def process_macro_objects(self, start, end):
    if not start:
      return
    
    #print(f'Processing Macro Objects from {self.level.name}: {hex(start)} to {hex(end)}')
    objects_found = []
    cursor = start

    macro_table = dict(
      start=start,
      entry_count_original=None,
      entries=[]
    )
    #print(self.level.name)
    #print("reading macro objects", start)
    preset_table = CollisionPresetParser.get_instance(self.rom).entries
    entry_pos = 0
    while cursor < end:
      macro_row = self.rom.read_bytes(cursor, 10)
      preset_and_rot = self.rom.read_integer(cursor, 2)
      #print("Macro", hex(start), hex(cursor), format_binary(self.rom.read_bytes(cursor, 10)))

      preset_id = preset_and_rot & 0x1FF # last 9 bit
      rot_y = preset_and_rot & 0xFE00 # first 7 bit
      rot_y = rot_y * MACRO_ROT_Y_MUL
      
      if preset_id == 0 or preset_id == 0x1E:
        break
      
      object3d = None
      if preset_id not in preset_table:
        #print(preset_id)
        #print(hex(preset_and_rot))
        #print(hex(start), hex(cursor), format_binary(self.rom.read_bytes(cursor, 20)))
        raise Exception("Invalid Preset ID! Not found in entries")
      else:
        preset = preset_table[preset_id]
        position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))
        bparam1 = self.rom.read_integer(None, 1)
        bparam2 = self.rom.read_integer(None, 1)
        object3d = Object3D("MACRO_OBJ", self.current_area, preset.model_id, position, self.level, (None, rot_y, None), preset.behaviour_addr, mem_address = cursor, bparams=[bparam1 if bparam1 > 0 else preset.default_b1, bparam2 if bparam2 > 0 else preset.default_b2])
        objects_found.append(object3d)
        macro_table["entries"].append(dict(
          object3d=object3d,
          bytes=macro_row
        ))
        self.macro_object_tables[object3d] = start
        entry_pos += 1

      cursor += 10
    macro_table["entry_count_original"] = len(macro_table["entries"])
    self.macro_tables[start] = macro_table
    self.objects.extend(objects_found)
    #self.update_macro_objects(start) # selfcheck

  def remove_special_macro_object(self, object3d):
    if object3d not in self.special_macro_object_tables:
      raise Exception(f"Object has no entry in special macro table list: {str(object3d)}")
    
    start = self.special_macro_object_tables[object3d]
    special_macro_table = self.special_macro_tables[start]

    index_to_remove = None
    idx = 0
    for entry in special_macro_table["entries"]:
      if entry["object3d"] == object3d:
        index_to_remove = idx
        break
      idx += 1
    
    print(special_macro_table["entries"][index_to_remove]["object3d"].behaviour_name, "deleted")
    del special_macro_table["entries"][index_to_remove]

    self.update_special_objects_table(start)

  def update_special_objects_table(self, start):
    if start not in self.special_macro_tables:
      raise Exception(f'{hex(start)} was not found in special object macro table entries')

    special_macro_table = self.special_macro_tables[start]

    cursor = start

    # write start bytes
    self.rom.write_byte(cursor, b'\x00\x40')
    cursor += 2

    # write vertice count
    self.rom.write_integer(cursor, len(special_macro_table["vertices"]), 2)
    cursor += 2

    #print("start vertices", hex(cursor - start))
    # write vertices
    for (x, y, z) in special_macro_table["vertices"]:
      self.rom.write_integer(cursor, x, 2, True)
      self.rom.write_integer(cursor + 2, y, 2, True)
      self.rom.write_integer(cursor + 4, z, 2, True)
      cursor += 6

    #print("start collision", hex(cursor - start))
    # write collision data entries
    for collision_entry in special_macro_table["collision_entries"]:
      # write type
      self.rom.write_byte(cursor, collision_entry["collision_type"])
      cursor += 2

      # write amount
      self.rom.write_integer(cursor, len(collision_entry["triangle_bytes"]), 2)
      cursor += 2

      entry_length = collision_entry["entry_length"]

      for triangle_bytes in collision_entry["triangle_bytes"]:
        self.rom.write_byte(cursor, triangle_bytes)
        cursor += entry_length

    # write random stop byte ???
    self.rom.write_byte(cursor, b'\x00\x41')
    cursor += 2

    #print("start objects", hex(cursor - start))
    #print(special_macro_table["entries"])

    object_entries = special_macro_table["entries"]
    if not len(object_entries):
      # place the weird default obj
      object_entries = [dict(
        length=10,
        object3d=None,
        bytes=b'\x00\x00\xe8\x01\x16f\xe8\x01\x00\x00\x00B'
      )]

    # write objects start byte
    self.rom.write_byte(cursor, b'\x00\x43')
    cursor += 2

    # write object count
    self.rom.write_integer(cursor, len(object_entries), 2)
    cursor += 2

    for entry in object_entries:
      #print("writing", entry["object3d"])
      self.rom.write_byte(cursor, entry["bytes"])
      cursor += entry["length"]
  
    #print("start water boxes", hex(cursor - start))
    if len(special_macro_table["waterboxes"]):
      # write water box start bytes
      self.rom.write_byte(cursor, b'\x00\x44')
      cursor += 2

      # write water box count
      self.rom.write_integer(cursor, len(special_macro_table["waterboxes"]), 2)
      cursor += 2

      for waterbox in special_macro_table["waterboxes"]:
        self.rom.write_byte(cursor, waterbox["bytes"])
        cursor += 12

    # write end bytes
    self.rom.write_byte(cursor, b'\x00\x42')

    # pad end
    #while cursor < special_macro_table["end"]:
    #self.rom.write_byte(cursor, b'\x00')
    #cursor += 1

    
    # dump changes on special_macro_list update in .bin format
    # old reads from input
    #old = self.rom.read_bytes(special_macro_table["start"], special_macro_table["end"] - special_macro_table["start"])

    # new reads manually from output
    #self.rom.target.seek(special_macro_table["start"]) #, special_macro_table["end"])
    #new = self.rom.target.read(special_macro_table["end"] - special_macro_table["start"])

    #with open("old_dump.bin", "wb+") as old_file:
    #  old_file.write(old)
    #with open("new_dump.bin", "wb+") as new_file:
    #  new_file.write(new)
    #sys.exit(0)
  

  def process_special_objects_level(self, start, end):
    cursor = start
    objects_found = []

    checksum = self.rom.read_bytes(cursor, 2)

    if checksum != b'\x00\x40':
      raise Exception("Invalid special object table")
    
    vertice_count = self.rom.read_integer(cursor + 2, 2)
    vertices = []

    special_macro_table = dict(
      start=start,
      vertice_count=vertice_count,
      vertices=[],
      collision_entries=[],
      entries=[],
      waterboxes=[]
    )

    # checksum read + vertice read
    cursor += 4

    # read vertices
    for _ in range(vertice_count):
      vertices.append((
        self.rom.read_integer(cursor, 2, True),
        self.rom.read_integer(cursor + 2, 2, True),
        self.rom.read_integer(cursor + 4, 2, True)
      ))
      cursor += 6

    # read collision data
    while cursor < end:
      cd_type = self.rom.read_bytes(cursor, 2)
      cd_type_int = self.rom.read_integer(cursor, 2)
      cursor += 2

      if cd_type == b'\x00\x41': break

      amount = self.rom.read_integer(cursor, 2)
      cursor += 2

      entry_length = 8 if cd_type_int in SPECIAL_CD_WITH_PARAMS else 6
      
      collision_entry = dict(
        collision_type=cd_type,
        entry_length=entry_length,
        triangle_bytes=[]
      )

      triangles = []
      triangle_bytes = []

      for _ in range(amount):
        indices = (
          self.rom.read_integer(cursor, 2),
          self.rom.read_integer(cursor + 2, 2),
          self.rom.read_integer(cursor + 4, 2)
        )
        triangle_bytes.append(self.rom.read_bytes(cursor, entry_length))
        cursor += entry_length

        triangles.append(indices)
      #print(self.level.name)
      #print(f'{len(triangles)} {hex(cd_type_int)} ({format_binary(cd_type)})')
      self.level_geometry.add_area(self.current_area, vertices, triangles, cd_type_int)
      collision_entry["triangle_bytes"] = triangle_bytes
      special_macro_table["collision_entries"].append(collision_entry)
    
    special_macro_table["vertices"] = vertices

    # read object definitions
    while cursor < end:
      special_type = self.rom.read_bytes(cursor, 2)
      #print("Collision Data Type", format_binary(special_type))
      if special_type == b'\x00\x43':
        """ Defines Macro Objects """
        preset_table = CollisionPresetParser.get_instance(self.rom).special_entries
        amount = self.rom.read_integer(cursor + 2, 2)
        #print(f'Defining {amount} special objs')
        #print(format_binary(self.rom.read_bytes(cursor, 20)))
        preset_id = None
        cursor += 4
        count = 0
        while count < amount:
          preset_id = self.rom.read_integer(cursor, 2)
          preset = preset_table[preset_id] if preset_id in preset_table else None

          if preset is None:
            print("preset not found")

          length = 8
          entry_bytes = None
          model_id = None
          position = None
          entry = None
          if preset:
            length = preset.length
            entry_bytes = self.rom.read_bytes(cursor, length + 2)

            model_id = preset.model_id
            position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))
            rotation = (None, None, None)
            bparams = []

            if length >= 10:
              rot_y = self.rom.read_integer(None, 2, True)
              rot_y = int(float(rot_y) * SPCL_MACRO_ROT_Y_MUL)
              rotation = (None, rot_y, None)
            
            if length >= 12:
              (b1, b2) = (self.rom.read_integer(), self.rom.read_integer())
              bparams = [b1, b2]

            entry = Object3D("SPECIAL_MACRO_OBJ", self.current_area, model_id, position, self.level, rotation, preset.behaviour_addr, bparams=bparams, mem_address = cursor)
          
            self.special_macro_object_tables[entry] = start
            objects_found.append(entry)
            count += 1

          special_macro_table["entries"].append(dict(
            length=length,
            model_id=model_id,
            object3d=entry,
            position=position,
            bytes=entry_bytes
          ))

          #print(format_binary(self.rom.read_bytes(cursor, length)))
          cursor += length
      elif special_type == b'\x00\x44':
        """ Defines Water Boxes """
        amount = self.rom.read_integer(cursor + 2, 2)
        cursor += 4
        #print(f"Wants to place {amount} water boxes. Not implemented")

        for water_box_index in range(amount):
          water_box_id = self.rom.read_integer(cursor, 2)
          water_box_bytes = self.rom.read_bytes(cursor, 12)
          water_box_start_x = self.rom.read_integer(cursor + 2, 2, True)
          water_box_start_z = self.rom.read_integer(cursor + 4, 2, True)

          water_box_end_x = self.rom.read_integer(cursor + 6, 2, True)
          water_box_end_z = self.rom.read_integer(cursor + 8, 2, True)
          
          water_box_y = self.rom.read_integer(cursor + 10, 2, True)
          water_box_type = "NO_EFFECT"

          if water_box_id < 0x32:
            water_box_type = "WATER"
          elif water_box_id == 0x32 or water_box_id == 0xF0:
            water_box_type = "TOXIC"
          
          water_box = dict(
            box_id=water_box_id,
            start=(min(water_box_start_x, water_box_end_x), min(water_box_y, -8192), min(water_box_start_z, water_box_end_z)),
            end=(max(water_box_start_x, water_box_end_x), max(water_box_y, -8192), max(water_box_start_z, water_box_end_z)),
            type=water_box_type,
            area_id=self.current_area
          )
          self.water_boxes.append(water_box)
          special_macro_table["waterboxes"].append(dict(
            bytes=water_box_bytes
          ))
          cursor += 12
      elif special_type == b'\x00\x42' or special_type == b'\x00\x41':
        #print("Reached Terminate Type")
        break
      else:
        #print(format_binary(self.rom.read_bytes(cursor - 4, 20)))
        raise Exception("CD Data CMD")
      
    special_macro_table["end"] = cursor
    self.special_macro_tables[start] = special_macro_table
    self.objects = self.objects + objects_found
    #print(f"Done parsing special level objects: {len(objects_found)}")

  def dump(self):
    output = ""

    for (indent, command) in self.commands:
      output += "  " * (indent-1) + str(command) + "\n"

    return output

  def find_all(self, id):
    for (indent, item) in self.commands:
      if type(item) is LevelScriptParser:
        return item.find_all(id)
      else:
        if item.identifier == id:
          yield item