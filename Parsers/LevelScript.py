from Parsers.Level import Level, LevelCommand
from Parsers.CollisionPresets import CollisionPresetParser, SPECIAL_CD_WITH_PARAMS
from Entities.Object3D import Object3D
from Entities.Warp import Warp
from Entities.LevelGeometry import LevelGeometry
from Constants import LVL_MAIN

from randoutils import format_binary

instances = {}
addresses_checked = []

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
    self.current_area = None

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

          #print("ROM_TO_SEGMENT", hex(command.identifier), hex(length+2), format_binary(data))
          self.rom.set_segment(segment_id, segment_addr, segment_end)
        elif command.identifier == 0x18 or command.identifier == 0x1A:
          """ 0x18 MIO0_DECOMPRESS or 0x1A MIO0_DECOMPRESS_TEXTURES """
          #print(command.name, hex(command.identifier), hex(length+2), format_binary(data))
          segment_id = self.rom.read_integer(cursor + 3)
          begin_mio0 = self.rom.read_integer(cursor + 4, 4)
          segment_end = self.rom.read_integer(cursor + 8, 4)
          segment_addr = self.rom.read_integer(begin_mio0 + 12) + begin_mio0

          self.rom.set_segment(segment_id, segment_addr, segment_end)
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

          self.objects.append(Object3D("PLACE_OBJ", model_id, position, rotation, b_script, [b1, b2, b3, b4], cursor + 2))
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
          self.warps.append(Warp("NORMAL", warp_id, to_area_id, to_course_id, to_warp_id, has_checkpoint, mem_address = cursor + 2))
        elif command.identifier == 0x27:
          """ 0x27 SETUP_PAINTING_WARP """
          warp_id = self.rom.read_integer(cursor + 2)
          to_course_id = self.rom.read_integer(cursor + 3)
          to_area_id = self.rom.read_integer(cursor + 4)
          to_warp_id = self.rom.read_integer(cursor + 5)
          has_checkpoint = self.rom.read_integer(cursor + 6) == 0x80
          self.warps.append(Warp("PAINTING", warp_id, to_area_id, to_course_id, to_warp_id, has_checkpoint, mem_address = cursor + 2))
        elif command.identifier == 0x2B:
          """ 0x2B SET_MARIOS_DEFAULT_POSITION """
          spawn_area_id = self.rom.read_integer(cursor + 2)
          rotation_y = self.rom.read_integer(cursor + 4, 2, True)
          position = (self.rom.read_integer(cursor + 6, 2, True), self.rom.read_integer(cursor + 8, 2, True), self.rom.read_integer(cursor + 10, 2, True))
          self.objects.append(Object3D("MARIO_SPAWN", None, position, (None, rotation_y, None), mem_address = cursor + 2))
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

  def process_macro_objects(self, start, end):
    if not start:
      return
    
    #print(f'Processing Macro Objects from {self.level.name}: {hex(start)} to {hex(end)}')
    objects_found = []
    cursor = start

    preset_table = CollisionPresetParser.get_instance(self.rom).entries
    while cursor < end:
      preset_and_rot = self.rom.read_integer(cursor, 2)
      #print("Macro", hex(start), hex(cursor), format_binary(self.rom.read_bytes(cursor, 10)))

      preset_id = preset_and_rot & 0x1FF # last 9 bit
      rot_y = preset_and_rot & 0xFE00 # first 7 bit
      
      if preset_id == 0 or preset_id == 0x1E or preset_id not in preset_table:
        break
        
      if preset_id not in preset_table:
        #print(preset_id)
        #print(hex(preset_and_rot))
        #print(hex(start), hex(cursor), format_binary(self.rom.read_bytes(cursor, 20)))
        raise Exception("Invalid Preset ID! Not found in entries")
      else:
        preset = preset_table[preset_id]
        position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))

        objects_found.append(Object3D("MACRO_OBJ", preset.model_id, position, (None, rot_y, None), preset.behaviour_addr, mem_address = cursor))
      cursor += 10

    self.objects = self.objects + objects_found
   #print(f'Level {self.level.name} has {len(objects_found)} macro objects')

  def process_special_objects_level(self, start, end):
    cursor = start
    objects_found = []

    checksum = self.rom.read_bytes(cursor, 2)

    if checksum != b'\x00\x40':
      raise Exception("Invalid special object table")
    
    vertice_count = self.rom.read_integer(cursor + 2, 2)
    vertices = []
    collision_tris = []

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

      triangles = []

      for _ in range(amount):
        indices = (
          self.rom.read_integer(cursor, 2),
          self.rom.read_integer(cursor + 2, 2),
          self.rom.read_integer(cursor + 4, 2)
        )

        cursor += 8 if cd_type_int in SPECIAL_CD_WITH_PARAMS else 6

        triangles.append(indices)
      #print(f'{len(triangles)} {hex(cd_type_int)} ({format_binary(cd_type)})')
      self.level_geometry.add_area(self.current_area, vertices, triangles, cd_type_int)

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
          if preset:
            length = preset.length
            entry = None
            if length == 8:
              model_id = preset.model_id
              position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))
              entry = Object3D("SPECIAL_MACRO_OBJ", model_id, position, None, preset.behaviour_addr, mem_address = cursor)
            elif length == 10:
              model_id = preset.model_id
              position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))
              rotation = (None, self.rom.read_integer(None, 2, True), None)
              entry = Object3D("SPECIAL_MACRO_OBJ", model_id, position, rotation, preset.behaviour_addr, mem_address = cursor)
            elif length == 12:
              model_id = preset.model_id
              position = (self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True), self.rom.read_integer(None, 2, True))
              rotation = (None, self.rom.read_integer(None, 2, True), None)
              (b1, b2) = (self.rom.read_integer(), self.rom.read_integer())
              entry = Object3D("SPECIAL_MACRO_OBJ", model_id, position, rotation, preset.behaviour_addr, [b1, b2], mem_address = cursor)
            else:
              raise Exception("Invalid Preset Length")

            objects_found.append(entry)
            count += 1

          #print(format_binary(self.rom.read_bytes(cursor, length)))
          cursor += length
      elif special_type == b'\x00\x44':
        """ Defines Water Boxes """
        amount = self.rom.read_integer(cursor + 2, 2)
        #print(f"Wants to place {amount} water boxes. Not implemented")
        # skip water boxes
        cursor = cursor + 4 + amount * 12
      elif special_type == b'\x00\x42' or special_type == b'\x00\x41':
        #print("Reached Terminate Type")
        break
      else:
        #print(format_binary(self.rom.read_bytes(cursor - 4, 20)))
        raise Exception("CD Data CMD")
      
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