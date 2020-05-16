
import struct
import re

from sm64r.Parsers.Assembly import AssemblerParser
from sm64r.Parsers.OpcodeEmulation import OpcodeEmulation
from sm64r.Rom import ROM
from sm64r.Randoutils import format_binary, format_bits, reverse_byte

rom_path = "Super Mario 64.z64"
rom_out = "Super Mario 64.ext.out.z64"

behaviour_locations = [
  #(0xF0000, 0x1FFFFF) # just bhv scripts
  (0x1000, 0x1FFFFF)
]

known_star_locations = {
  # 'BOB: Koopa the Quick': (3030, 4500, -4600), # short
  # 'BOB: King Bob-Omb': (2000.0,4500.0,-4500.0), # 0x605e8 ?
  # 'WF: Whomp Boss': (180.0, 3880.0, 340.0), # 0x82910
  # 'SSL: Eyerok': (0.0, -900.0, -3700.0),
  #'SSL: Klepto': (-5550.0, 300.0, -930.0), # 0xcc480
  # 'LLL: Big Bully': (0.0, 950.0, -6800.0),
  'SL: Ice Bully': (130.0, 1600.0, -4335.0), # 0xa6954 ?
  #'THI: Wiggler': (0.0, 2048.0, 0.0), # 0xbcfe4
  # 'THI: Koopa the Quick': (7100, -1300, -6000), # short
  #'THI: Pirana Plants': (-6300.0, -1850.0, -6300.0),
  #'PSS: Peach Slide': (-6358.0, -4300.0, 4700.0), # 0xb7d4
  #'CCM: Penguin Baby': (3500.0, -4300.0, 4650.0),
  #'CCM: Snowman Assembly': (-4700.0, -1024.0, 1890.0),
  #'CCM: Leave Slide': (2500.0, -4350.0, 5750.0), # 0x6d3b4
  #'CCM: Racing Penguin': (-7339.0, -5700.0, -6774.0),
  #'JRB: 4 Treasure Chests': (-1800.0, -2500.0, -1700.0),
  #'BBH: Hallway/Staircase Big Boo': (980.0, 1100.0, 250.0), # 0x7fbb4
  #'BBH: Merry-Go-Round Big Boo': (-1600.0, -2100.0, 205.0),
  #'BBH: Mr. I': (1370.0, 2000.0, -320.0),
  #'BBH: Roof Balcony Big Boo': (700.0, 3200.0, 1900.0), # 0x7fbf0
  # 'LLL: Big Bully with Minions': (3700.0, 600.0, -5500.0), # 0xa6cc0
  'TTM: Cage Star': (2500.0, -1200.0, 1300.0),
  #'DDD: Manta Ray': (-3180.0, -3600.0, 120.0),
  #'DDD: 4 Treasure Chests': (-1900.0, -4000.0, -1400.0),
  #'DDD: Water Rings': (3400.0, -3200.0, -500.0),
}

# 00 00 00 07 D0 
# 00 00 00 7D 00
with ROM(rom_path, rom_out) as rom_orig:
  rom_orig.verify_header()
  new_rom_path = rom_orig.try_extend()

  with ROM(new_rom_path, rom_out) as rom:
    rom.verify_header()
    rom.read_configuration()
    rom.print_info()

    '''
    for (bstart, bend) in behaviour_locations:
      raw_bhv = rom.read_bytes(bstart, bend - bstart)
      str_bhv = raw_bhv.hex()
      
      print(f"Read {len(raw_bhv)} bytes from behaviour script location")

      for star_name, star_location in known_star_locations.items():
        pos_bytes = []
        for pos_comp in star_location:
          if type(pos_comp) is float:
            pos_bytes.append(struct.pack('>f', pos_comp))
          if type(pos_comp) is int:
            pos_bytes.append(struct.pack('>h', pos_comp))
        
        #print(list(map(lambda x: hex(x), pos_comp))) # debug
        re_bytes = list(map(lambda x: re.compile(x.hex().lstrip('0'), re.I), pos_bytes))
        found_locations = [[], [], []]

        for comp_idx, re_byte in enumerate(re_bytes):
          for m in re_byte.finditer(str_bhv):
            found_locations[comp_idx].append(bstart + m.start())
        

        print('Matches:', len(found_locations[0]), len(found_locations[1]), len(found_locations[2]))

        if len(found_locations[0]) == 1:
          print(star_name)
          print(star_location)
          print(found_locations)
        
    '''

    opcode_search = 0x0c0bcae2 # jal	0x2f2b88
    opcode_regex = re.compile("c0bcae2", re.I)

    star_create_calls = []
    for (bstart, bend) in behaviour_locations:
      raw_bhv = rom.read_bytes(bstart, bend - bstart)
      str_bhv = raw_bhv.hex()
      print(f"{len(str_bhv)} bytes read")

      for match in opcode_regex.finditer(str_bhv):
        # match.start / 2 because string representation is binary representation * 2 in length
        print(f'Found "create_star" call: {hex(int(match.start()/2) + bstart)}')
        star_create_calls.append(int(match.start()/2))
    

    #asm_parse = AssemblerParser(rom)
    #asm_parse.set_cursor(0x2f2b88)
    #instructions = asm_parse.parse_until(0x2f2b88 + (36 * 4))
    #for instruction in instructions:
    #    print(hex(instruction['position']).ljust(10, ' '), instruction['opcode'].rjust(10, ' '), instruction['registers_changed'])
    #print('=' * 40)

    #000040 - boot assembly
    #001000	0E6258 game assembly
    
    asm_parse = AssemblerParser(rom)
    asm_parse.set_cursor(0x001000)
    instructions = asm_parse.parse_until(0xE6258)

    # instructions used to call create_star
    # FPR12: X
    # FPR14: Y
    # (R06): Z


    emulation = OpcodeEmulation(rom)
    emulation.load_instructions(instructions)

    emulation.add_breakpoints(list(map(lambda x: x + bstart, star_create_calls)))

    #emulation_states_during_starcreation_calls = []
    emulation.run()
    #for state in emulation.run():
    #  emulation_states_during_starcreation_calls.append(state)
    #emulation.output_state()

    #for state in emulation_states_during_starcreation_calls:
    #  print(f"- State at {hex(state['position'])}: " + "-"*40)
    #  emulation.debug_registers(state["gpr"], state["cp0"])

    '''
    for star_create_call in star_create_calls:
      asm_parse = AssemblerParser(rom)
      asm_parse.set_cursor_with_instruction_offset(star_create_call + bstart, -100)
      instructions = asm_parse.parse_until(star_create_call + bstart)

      # instructions used to call create_star
      # FPR12: X
      # FPR14: Y
      # (R06): Z


      emulation = OpcodeEmulation(rom)
      emulation.load_instructions(instructions)

      emulation.run()
      emulation.output_state()

      for instruction in instructions:
        pass
        #print(hex(instruction['position']).ljust(10, ' '), instruction['opcode'].rjust(10, ' '), instruction['params'])
    '''