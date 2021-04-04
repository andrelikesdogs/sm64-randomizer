from random import choice
from sm64r.Randoutils import format_binary
import math

# Skyboxes
SKYBOX_IDS = [
  0x00, # Bob-Omb's Battlefield
  0x01, # Lethal Lava Land
  0x02, # Wet Dry World
  0x03, # Rainbow Ride
  0x04, # Cool, Cool Mountain
  0x05, # Shifting Sand Land
  0x06, # Big Boo's Haunt
  0x07, # Bowser 1 Course
  0x08, # Jolly Roger Bay
  0x09, # Bowser 3 Course
]

SKYBOX_POSITIONS = {
  0x00: 0xB35715,
  0x01: 0xBA22D5,
  0x02: 0xBC2C15,
  0x03: 0xBEAD55,
  0x04: 0xB5D855,
  0x05: 0xC12E95,
  0x06: 0xC3AFD5,
  0x07: 0xC57915,
  0x08: 0xB85995,
  0x09: 0xC7FA55
}

SKYBOX_INDICES = {
  0x00: 36,
  0x01: 282,
  0x02: 170,
  0x03: 236,
  0x04: 87,
  0x05: 119,
  0x06: 68,
  0x07: 250,
  0x08: 188,
  0x09: 315,
}

class SkyboxRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
  
  def randomize_skyboxes(self):
    sky_positions = {}

    # match via bank indices
    for (sky_index, bank_index) in SKYBOX_INDICES.items():
      sky_positions[sky_index] = self.rom.segments_sequentially[bank_index]

    for level in self.rom.config.levels:
      random_texture_id = choice(SKYBOX_IDS)

      segments_loaded = self.rom.levelscripts[level].commands_by_id[0x17]
      for segment_cmd in segments_loaded:
        bank = segment_cmd.data[1]
        #print(hex(bank))
        if bank == 0xa:
          (start, end) = sky_positions[random_texture_id]
          '''
          # output changes
          changelist = list(segment_cmd.data)
          changelist[2:6] = start.to_bytes(4, self.rom.endianess)
          changelist[6:12] = end.to_bytes(4, self.rom.endianess)

          print(format_binary(segment_cmd.data), " to ", format_binary(bytes(changelist)))
          '''
          self.rom.write_integer(segment_cmd.position + 2, start, 4)
          self.rom.write_integer(segment_cmd.position + 6, end, 4)

      geo_layouts = self.rom.levelscripts[level].geometry_layouts
      for geo_layout in geo_layouts:
        if 0x19 in geo_layout.commands_by_id:
          for (position, prev_command) in geo_layout.commands_by_id[0x19]:
            if prev_command[4:8] == bytes([0x80, 0x27, 0x63, 0xD4]):
              '''
              # output changes
              changelist = list(prev_command)
              changelist[3] = random_texture_id
              print(format_binary(prev_command), " to ", format_binary(bytes(changelist)))
              '''
              self.rom.write_integer(position + 3, random_texture_id)
