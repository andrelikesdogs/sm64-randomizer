from random import randint, choice
from sm64r.Randoutils import clamp
import logging
import math

# SM64 USA (BE) ROM Position
# 0x823B64

MEM_COLOR_ADDRESSES = {
  'OVERALLS': 0x0,
  'HAT_AND_SHIRT': 0x20,
  'GLOVES': 0x38,
  'SHOES': 0x48,
  'SKIN': 0x60,
  'HAIR': 0x80
}

CLOTH_COLORS = [(255, 255, 255), (173, 36, 36), (9, 96, 168), (10, 193, 3), (99, 27, 98), (211, 155, 20), (204, 0, 91), (10, 160, 149), (105, 158, 0), (158, 60, 0), (82, 12, 206), (81, 81, 81), (193, 193, 0), (98, 63, 193)] # white, red, blue, lime, purple, gold, pink, turquoise, green, orange, smashluigitrousers, grey, yellow and lilac

SENSIBLE_COLORS = {
  'OVERALLS': CLOTH_COLORS,
  'HAT_AND_SHIRT': CLOTH_COLORS,
  'GLOVES': CLOTH_COLORS,
  'SHOES': [(119, 95, 6), (0, 0, 0), (120, 120, 120), (255, 255, 255), (112, 29, 0), (0, 112, 28), (22, 92, 112), (68, 57, 112), (112, 39, 89)], # brown, black, gray, white, redbrown, green, turquoise, purple and pink
  'SKIN': [(45, 34, 30), (60, 46, 40), (75, 57, 50), (90, 69, 60), (105, 80, 70), (120, 92, 80), (135, 103, 90), (150, 114, 100), (165, 126, 110), (180, 138, 120), (195, 149, 130), (210, 161, 140), (225, 172, 150), (240, 184, 160), (255, 195, 170), (255, 206, 108), (255, 174, 117), (255, 191, 135), (255, 220, 177)],
  'HAIR': [(9, 6, 9), (44, 34, 43), (58, 48, 38), (78, 67, 63), (80, 68, 69), (106, 78, 86), (85, 72, 56), (167, 133, 106), (184, 151, 120), (220, 208, 186), (222, 168, 153), (151, 121, 97), (233, 206, 168), (228, 220, 168), (165, 137, 70), (145, 85, 61), (83, 61, 53), (113, 99, 90), (182, 166, 158), (214, 196, 194), (183, 18, 164), (202, 191, 177), (141, 74, 67), (181, 82, 57), (229, 0, 7), (0, 229, 26), (0, 110, 229), (229, 160, 0), (0, 143, 175)],
}

class MarioRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

    (segment_0x1_start, _) = self.rom.segments_sequentially[1]
    self.bank_start = segment_0x1_start

  def randomize_color(self, enable_dumb_colors=False):
    logging.info("Randomizing Mario\'s Colors")
    if self.rom.rom_type != 'EXTENDED':
      logging.error('Can not modify Mario\'s color on a non-extended ROM. Please load an extended ROM')
      return
    
    for (part, mem_address) in MEM_COLOR_ADDRESSES.items():
      # read existing colors
      """
      (r, g, b) = tuple([self.rom.read_integer(mem_address + i) for i in range(3)])
      print(part, (r, g, b))
      (r2, g2, b2) = tuple([self.rom.read_integer(mem_address + 0x8 + i) for i in range(3)])
      print(part + " dark", (r2, g2, b2))
      """

      color_light = choice(SENSIBLE_COLORS[part])
      color_dark = tuple([clamp(v + 20, 0, 255) for v in color_light])
      # print(color_dark)
      # print(f'{part} is now {color}')

      self.rom.write_bytes(self.bank_start + mem_address, bytes([*color_light, 255])) # light
      self.rom.write_bytes(self.bank_start + mem_address + 0x8, bytes([*color_dark, 255])) # dark
    pass
    #self.rom.file.seek(0x114750)
    #read_range = 0x1279B0 - 0x114750
    #mario_dl = self.rom.file.read(read_range)

    #print([hex(b) for b in mario_dl[0:10]])

    #print([hex(b) for b in mario_dl])
    # extended rom pos: 823b64, 12a78b
    #self.rom.target.seek(0x127F28) # hp torso
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00, 0x04, 0x01, 0x03, 0x90]))
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x01, 0x03, 0x90]))

    #self.rom.target.seek(0x127EFC)
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0xCC, 0x98]))
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0xCC, 0x30]))

    #self.rom.target.seek(0x128A34)
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x01, 0x03, 0x70]))
    #self.rom.target.write(bytes([0x13, 0x01, 0x00, 0x44, 0x00, 0x00, 0x00, 0x00, 0x04, 0x01, 0x03, 0x70]))
    #while self.rom.file.tell() < MARIO_GEO_ADDRESS_END:
