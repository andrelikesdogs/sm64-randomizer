import struct
import re

from Rom import ROM

rom_path = "Super Mario 64.z64"
rom_out = "Super Mario 64.ext.out.z64"

behaviour_locations = [
  (0xF0000, 0x1FFFFF)
]

known_star_locations = {
  'BOB: Koopa the Quick': (3030, 4500, -4600), # short
  'THI: Koopa the Quick': (7100, -1300, -6000), # short
  'BOB: King Bob-Omb': (2000.0,4500.0,-4500.0),
  'WF: Whomp Boss': (180.0, 3880.0, 340.0),
  'SSL: Eyerok': (0.0, -900.0, -3700.0),
  'LLL: Big Bully': (0.0, 950.0, -6800.0),
  'SL: Ice Bully': (130.0, 1600.0, -4335.0),
  'THI: Pirana Plants': (-6300.0, -1850.0, -6300.0),
  'CCM: Racing Penguin': (-7339.0, -5700.0, -6774.0),
  'THI: Wiggler': (0.0, 2048.0, 0.0),
  'PSS: Peach Slide': (-6358.0, -4300.0, 4700.0),
  'CCM: Penguin Baby': (3500.0, -4300.0, 4650.0),
  'JRB: 4 Treasure Chests': (-1800.0, -2500.0, -1700.0),
  'BBH: Hallway/Staircase Big Boo': (980.0, 1100.0, 250.0),
  'SSL: Klepto': (-5550.0, 300.0, -930.0),
  'BBH: Merry-Go-Round Big Boo': (-1600.0, -2100.0, 205.0),
  'BBH: Mr. I': (1370.0, 2000.0, -320.0),
  'BBH: Roof Balcony Big Boo': (700.0, 3200.0, 1900.0),
  'LLL: Big Bully with Minions': (3700.0, 600.0, -5500.0),
  'TTM: Cage Star': (2500.0, -1200.0, 1300.0),
  'DDD: Manta Ray': (-3180.0, -3600.0, 120.0),
  'CCM: Snowman Assembly': (-4700.0, -1024.0, 1890.0),
  'CCM: Leave Slide': (2500.0, -4350.0, 5750.0),
  'DDD: Water Rings': (3400.0, -3200.0, -500.0),
}

def get_half_shift_bytes(bytes_in):
  str_bytes = bytes_in.hex()
  str_bytes = "0" + str_bytes + "0"

  print(str_bytes)

  return bytes.fromhex(str_bytes)


# 00 00 00 07 D0 
# 00 00 00 7D 00
with ROM(rom_path, rom_out) as rom_orig:
  rom_orig.verify_header()
  new_rom_path = rom_orig.try_extend()

  with ROM(new_rom_path, rom_out) as rom:
    rom.verify_header()
    rom.read_configuration()
    rom.print_info()

    for (bstart, bend) in behaviour_locations:
      raw_bhv = rom.read_bytes(bstart, bend - bstart)
      str_bhv = raw_bhv.hex()
      
      print(f"Read {len(raw_bhv)} bytes from behaviour script location")

      for star_name, star_location in known_star_locations.items():
        print(star_name)
        print(star_location)
        pos_bytes = []
        for pos_comp in star_location:
          if type(pos_comp) is float:
            pos_bytes.append(struct.pack('>f', pos_comp))
          if type(pos_comp) is int:
            pos_bytes.append(struct.pack('>h', pos_comp))
        
        re_bytes = list(map(lambda x: re.compile(x.hex().lstrip('0'), re.I), pos_bytes))
        found_locations = [[], [], []]

        for comp_idx, re_byte in enumerate(re_bytes):
          for m in re_byte.finditer(str_bhv):
            found_locations[comp_idx].append(bstart + m.start())
        

        print('Matches:', len(found_locations[0]), len(found_locations[1]), len(found_locations[2]))
        #print(found_locations)
        



