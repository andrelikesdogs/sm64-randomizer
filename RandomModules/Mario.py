from Rom import ROM
from random import randint

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
  def __init__(self, rom : ROM):
    self.rom = rom

  def randomize_color(self):
    if self.rom.rom_type != 'EXTENDED':
      print('Can not modify Mario\'s color on a non-extended ROM. Please load an extended ROM')
      return
    
    for (part, mem_address) in MEM_COLOR_ADDRESSES.items():
      color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
      print(f'{part} is now {color}')

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
