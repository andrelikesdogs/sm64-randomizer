from sm64r.Entities.Object3D import Object3D
from sm64r.Constants import BEHAVIOUR_NAMES

from sm64r.Randoutils import format_binary

import struct

class HardcodedStar(Object3D):
  area_id: int
  level: "Level"
  memory_mapping: dict = {}
  meta: dict = {}

  def read_axis_value(self, axis, axis_config):
    axis_read_strategy = axis_config["strategy"] or 'rom_stored_mem'
    if axis_read_strategy == "rom_stored_mem":
      # The value is stored in memory, but it's loaded from a specific ROM position
      value_bytes = self.rom.read_bytes(axis_config["mem_pos"], 4)
      value = struct.unpack('>f', value_bytes)[0]

      value_configured_big_int = axis_config["value"]
      value_configured = struct.unpack('>f', value_configured_big_int.to_bytes(4, self.rom.endianess))[0]

      if value != value_configured:
        print(f"The value that was read is not the one defined in the configuration, this configuration will not be used: {value} vs {value_configured}")
        return

      print(f"Value successfully read as '{value}'")
    if axis_read_strategy == "lui_ori_change":
      lui_inst = self.rom.asm_parser.find_instruction_for_ram_addr(axis_config['asm_pos']['LUI'])
      ori_inst = self.rom.asm_parser.find_instruction_for_ram_addr(axis_config['asm_pos']['ORI'])

      val_upper = lui_inst["params"]["imm"] << 16
      val_lower = ori_inst["params"]["imm"]

      value = val_upper | val_lower
      value_bytes = value.to_bytes(4, self.rom.endianess)

      value_configured_big_int = axis_config["value"]
      value_configured = struct.unpack('>f', value_configured_big_int.to_bytes(4, self.rom.endianess))[0]
      value = struct.unpack('>f', value_bytes)[0]

      if value != value_configured:
        print(f"The value that was read is not the one defined in the configuration, this configuration will not be used: {value} vs {value_configured}")
        return

      print(f"Value successfully read as '{value}'")

  def write_axis_values(self, position_tuple):
    # this is different from how the config is written
    # all outside facing positions are z up/down
    axes = ['x', 'z', 'y']

    for idx, position_value in enumerate(position_tuple):
      axis = axes[idx]
      axis_config = self.position_config[axis]
      #print(axis, axis_config, position_value)

      axis_strategy = axis_config["strategy"]

      if axis_strategy == 'rom_stored_mem':
        # write float number directly to stored mem pos
        value_to_save = struct.pack('>f', position_value)
        self.rom.write_bytes(axis_config["mem_pos"], value_to_save)
      if axis_strategy == 'lui_ori_change':
        lui_inst = self.rom.asm_parser.find_instruction_for_ram_addr(axis_config['asm_pos']['LUI'])
        ori_inst = self.rom.asm_parser.find_instruction_for_ram_addr(axis_config['asm_pos']['ORI'])

        lui_int = int.from_bytes(lui_inst["instruction"], self.rom.endianess)
        ori_int = int.from_bytes(ori_inst["instruction"], self.rom.endianess)

        float_as_int = int.from_bytes(struct.pack('>f', position_value), self.rom.endianess)
        value_upper = (float_as_int & (0xFFFF << 16)) >> 16
        value_lower = float_as_int & 0xFFFF
        #print(hex(float_as_int), hex(value_upper), hex(value_lower))
        #lui_int

        # clear imm
        lui_int = lui_int & ~(lui_int & 0xFFFF)
        ori_int = ori_int & ~(ori_int & 0xFFFF)

        #print(format_binary(lui_int.to_bytes(4, self.rom.endianess)))
        #print(format_binary(ori_int.to_bytes(4, self.rom.endianess)))

        # add new imm
        lui_int = lui_int | value_upper
        ori_int = ori_int | value_lower

        # write to ROM
        #print(f'writing to {hex(lui_inst["position"])} and {hex(ori_inst["position"])}')
        self.rom.write_bytes(lui_inst['position'], lui_int.to_bytes(4, self.rom.endianess))
        self.rom.write_bytes(ori_inst['position'], ori_int.to_bytes(4, self.rom.endianess))

        self.rom.mark_checksum_dirty()


    print("writing to hardcoded star", self.level, position_tuple)
    pass

  def __init__(self, rom, name, properties):
    self.rom = rom
    self.position_config = properties["position"]
    self.course_id = properties["course_id"]
    self.level = self.rom.config.levels_by_course_id[self.course_id]
    self.area_id = properties["area_id"]
    self.name = name
    self.source = "HARDCODED_STAR"

    for axis in self.position_config.keys():
      self.read_axis_value(axis, self.position_config[axis])
    
    self.add_mapping('position', self.write_axis_values, 0, 0)

  def __str__(self):
    return f'<Hardcoded Star "{self.name}" in Level "{self.level.name}" (Area {hex(self.area_id)})"'

  @staticmethod
  def from_constants_definition(rom, constant_def_name):
    if "star_positions" not in rom.config.constants:
      raise ValueError(f'Hardcoded Star definition "{constant_def_name}" used, but no star positions entry was defined in the constants file.')
    
    if constant_def_name not in rom.config.constants["star_positions"]:
      raise ValueError(f'Hardcoded Star defintion "{constant_def_name}" not defined in constants.star_positions.')

    properties = rom.config.constants["star_positions"][constant_def_name]

    if "position" not in properties:
      raise ValueError(f'Hardcoded Star definition "{constant_def_name}" does not define memory locations for the coordinate. Please read the documentation within the sm64.vanilla.constants.yml file.')

    for axis in ['x', 'y', 'z']:
      if axis not in properties["position"]:
        raise ValueError(f'Hardcoded Star definition "{constant_def_name}" has not defined the axis "{axis}" - please add it to the constant config entry.')

    return HardcodedStar(rom, constant_def_name, properties)