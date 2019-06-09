from random import randint, choice
import logging

MARIO_GEO_ADDRESS_START = 0x127C90
MARIO_GEO_ADDRESS_END = 0x122E2C

RAM_COPY_OFFSET = 0x8016F000
RAM_COPY_END = 0x801A72F8

MEM_COLOR_ADDRESSES = {
  'OVERALLS': 0x823B64,
  'HAT_AND_SHIRT': 0x823B7C,
  'GLOVES': 0x823B94,
  'SHOES': 0x823BAC,
  'SKIN': 0x823BC4,
  'HAIR': 0x823BDC
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

'''
# Model Part Offsets
MEM_ADDRESSES = {
  'REAR': 0x127F04,
  'TORSO': 0x127F30,
  'HEAD': (0x127CC0, 0x127CC8, 0x127CD0, 0x127CD8, 0x127CE0, 0x127CE8, 0x127CF0, 0x127CF8)
  'LEFT_UPPER_ARM': 0x127F6C,
  'LEFT_LOWER_ARM': 0x127F7C,
  'LEFT_FIST': (0x127E00, 0x127E14, 0x127E20, 0x127E2C, 0x127E38),
  'RIGHT_UPPER_ARM': 0x127FB0,
  'RIGHT_LOWER_ARM': 0x127FC0,
  'RIGHT_FIST': (0x127E78, 0x127E98),
  'LEFT_UPPER_LEG': 0x127FFC,
  'LEFT_LOWER_LEG': 0x12800C,
  'LEFT_FOOT': 0x12801C,
  'RIGHT_LOWER_LEG': 0x128054,
  'RIGHT_UPPER_LEG': 0x128044,
  'RIGHT_FOOT': 0x128084
}
'''

class MarioRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def randomize_color(self, enable_dumb_colors=False):
    logging.info("Randomizing Mario\'s Colors")
    if self.rom.rom_type != 'EXTENDED':
      logging.error('Can not modify Mario\'s color on a non-extended ROM. Please load an extended ROM')
      return
    
    for (part, mem_address) in MEM_COLOR_ADDRESSES.items():
      if enable_dumb_colors:
        color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
      else:
        color = choice(SENSIBLE_COLORS[part])
      #print(f'{part} is now {color}')

      self.rom.target.seek(mem_address, 0)
      self.rom.target.write(bytes([*color]))


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
