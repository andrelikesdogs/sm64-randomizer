from typing import NamedTuple

SPECIAL_CD_WITH_PARAMS = [0x04, 0x0E, 0x24, 0x25, 0x27, 0x2C, 0x2D]

class PresetEntry(NamedTuple):
  preset_id: int
  length: int
  default_b1: int
  default_b2: int
  model_id: int
  behaviour_addr: int

class CollisionPresetParser:
  instance = None

  def __init__(self, rom):
    self.rom = rom
    self.entries = {}
    self.special_entries = {}
    
    self.preset_id_offset = self.rom.macro_table_position
    self.special_preset_id_offset = self.rom.special_macro_table_position

    self.read_entries()
    self.read_special_entries()

  @staticmethod
  def get_instance(rom : 'ROM'):
    if CollisionPresetParser.instance is None:
      CollisionPresetParser.instance = CollisionPresetParser(rom)
    return CollisionPresetParser.instance

  @staticmethod
  def get_special_obj_len(idx : int):
    # Taken from Quad64, thank you :pray:
    # https://github.com/DavidSM64/Quad64/blob/master/src/Scripts/LevelScripts.cs#L818:L829
    
    if idx > 0x64 and idx < 0x79: return 10
    if idx > 0x78 and idx < 0x7E: return 8
    if idx > 0x7D and idx < 0x83: return 10
    if idx > 0x88 and idx < 0x8E: return 10
    if idx > 0x82 and idx < 0x8A: return 12
    if idx == 0x40: return 10
    if idx == 0x64: return 12
    if idx == 0xC0: return 8
    if idx == 0xE0: return 12
    if idx == 0xCD: return 12
    if idx == 0x00: return 10
    return 8

  def overwrite_macro_entry(self, preset_id, model_id, behaviour, default_b1, default_b2):
    self.entries[preset_id] = PresetEntry(preset_id, 8, default_b1, default_b2, model_id, behaviour)

    if preset_id < 31 or preset_id > 366:
      raise ValueError(f"Preset-ID is out of range for macro objects ({hex(preset_id)})")

    preset_position = self.preset_id_offset + (preset_id - 31) * 8
    self.rom.write_integer(preset_position, behaviour, 4)
    self.rom.write_integer(preset_position + 4, model_id, 2)
    self.rom.write_integer(preset_position + 6, default_b1)
    self.rom.write_integer(preset_position + 6, default_b2)
    self.rom.mark_checksum_dirty()


  def read_entries(self):
    cursor = self.preset_id_offset
    count = 0
    while count < 366:
      preset_id = 31 + count
      b_addr = self.rom.read_integer(cursor, 4)
      model_id = self.rom.read_integer(None, 2)
      default_b1, default_b2 = (self.rom.read_integer(), self.rom.read_integer())

      self.entries[preset_id] = PresetEntry(preset_id, 8, default_b1, default_b2, model_id, b_addr)

      cursor += 8
      count += 1


  def read_special_entries(self):
    cursor = self.special_preset_id_offset
    while True:
      preset_id = self.rom.read_integer(cursor)
      default_b1 = self.rom.read_integer()
      default_b2 = self.rom.read_integer()
      model_id = self.rom.read_integer()
      b_addr = self.rom.read_integer(None, 4)

      if preset_id == 0xFF:
        break

      length = CollisionPresetParser.get_special_obj_len(preset_id)

      self.special_entries[preset_id] = PresetEntry(preset_id, length, default_b1, default_b2, model_id, b_addr)

      cursor += 8