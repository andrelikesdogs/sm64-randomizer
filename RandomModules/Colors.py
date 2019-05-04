from random import randint
import logging

COIN_COLOR_MEM_POS = {
  'YELLOW': [(0x0AB7AD8, 0x0AB7AD9, 0x0AB7ADA), (0x0AB7AE8, 0x0AB7AE9, 0x0AB7AEA), (0x0AB7AF8, 0x0AB7AF9, 0x0AB7AFA), (0x0AB7B08, 0x0AB7B09, 0x0AB7B0A)],
  'BLUE': [(0x0AB7B18, 0x0AB7B19, 0x0AB7B1A), (0x0AB7B28, 0x0AB7B29, 0x0AB7B2A), (0x0AB7B38, 0x0AB7B39, 0x0AB7B3A), (0x0AB7B48, 0x0AB7B49, 0x0AB7B4A)],
  'RED': [(0x0AB7B58, 0x0AB7B59, 0x0AB7B5A), (0x0AB7B68, 0x0AB7B69, 0x0AB7B6A), (0x0AB7B78, 0x0AB7B79, 0x0AB7B7A), (0x0AB7B88, 0x0AB7B89, 0x0AB7B8A)]
}

class ColorRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def randomize_coin_colors(self):
    logging.info("Randomizing Coin Colors")
    for coin_type, mem_addresses in COIN_COLOR_MEM_POS.items():
      (r, g, b) = randint(120, 255), randint(120, 255), randint(120, 255)
      #print(f'Coin Type: {coin_type} color: rgb({r}, {g}, {b})')
      for mem_address in mem_addresses:
        self.rom.write_integer(mem_address[0], r)
        self.rom.write_integer(mem_address[1], g)
        self.rom.write_integer(mem_address[2], b)