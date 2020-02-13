from random import randint
import colorsys
import logging

class ColorRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

    (start_segment_0x2, _) = self.rom.segments_sequentially[2]

    self.coin_addresses = {
      'YELLOW': start_segment_0x2 + 0x56cc,
      'BLUE': start_segment_0x2 + 0x570c,
      'RED': start_segment_0x2 + 0x574c
    }
    
  def randomize_coin_colors(self):
    logging.info("Randomizing Coin Colors")
    hsl_offset = randint(0, 360)
    hsl_dist = 120
    hsl_index = 0

    coin_colors = []

    for coin_type in self.coin_addresses.keys():
      # hue shift for coin colors, to ensure difference in color
      hue = (hsl_offset + (hsl_dist * hsl_index)) % 360
      hsl_index += 1
      saturation = 50.0
      luminence = 50.0
      (r, g, b) = colorsys.hls_to_rgb(hue / 360.0, luminence / 100.0, saturation / 100.0) #randint(120, 255), randint(120, 255), randint(120, 255)
      logging.info(f'Coin Type: {coin_type} color: rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})')
      coin_colors.append((coin_type, (int(r * 255), int(g * 255), int(b * 255))))
    
    for (coin_type, color) in coin_colors:
      (r, g, b) = color
      cursor = self.coin_addresses[coin_type]
      for _ in range(4):
        self.rom.write_integer(cursor, r)
        self.rom.write_integer(cursor + 1, g)
        self.rom.write_integer(cursor + 2, b)
        cursor += 0x10 # 0xE padding between entries

