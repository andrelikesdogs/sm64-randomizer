from Constants import ALL_LEVELS, CAP_LEVELS, MISSION_LEVELS, BOWSER_STAGES, LVL_BOB, SPECIAL_LEVELS, LVL_MAIN_SCR, LVL_CASTLE_GROUNDS
from Rom import ROM
import sys
from Parsers.LevelScript import LevelScriptParser

from random import shuffle

WHITELIST_SHUFFLING = [
  (None, 0xBC), # Bob-Omb
  (None, 0xC0), # Goomba,
  (0x13004770, None), # Goomba Triplet
  (0x13001298, 0x75), # Coin Triplet
  (0x130001F4, 0x56), # King Bob-Omb
  (0x13002BB8, 0x67), # King Whomp
  (None, 0x68), # Koopa (The Quick, Normal, etc)
  (0x130005B4, 0x10), # Rotating Platform WF
  (0x13002AA4, None), # Tree Behaviour
  (None, 0x65), # Scuttlebug
  (None, 0x19), # Tree (Snow)
  (None, 0x17), # Tree (In Courses)
  (None, 0x18), # Tree (Courtyard)
  (None, 0x1B), # Tree (SSL)
  (0x13001548, 0x59), # Heave-Ho
  (None, 0x78), # Heart
  (0x13004348, 0xDB), # Red Coin
  (0x13003E8C, 0x7A), # Red Coin Star
  (0x13002EC0, 0x01), # Mario Spawn
  (0x13005468, 0x69), # Skeeter (WDW Bug thing)
  (0x13000BC8, 0x58), # Thwomp
  (0x13000B8C, 0x58), # Thwomp 2
  (0x13001FBC, 0x64), # Piranha
  (0x13005120, 0x64), # Fire-Spitting
  (0x13002EF8, 0xDD), # Toad
  (0x130009A4, 0x75), # Single Coin
  (0x13000964, None), # Coins (x3)
  (0x13000984, None), # Coins (x10)
  (0x130008EC, None), # Coins (Formations)
  (0x13005440, 0x58), # Clam in JRB
  (0x13004634, None), # Pokey
  (0x13004668, 0x55), # Pokeys Head
  (None, 0x7C), # Sign
  (None, 0x74), # Coin Type 1
  (None, 0x75), # Coin Type 2
  (None, 0x74), # Coin Type 3
  (None, 0x75), # Multiple Coins
  (None, 0xD4), # One-Up
  (0x130020E8, 0x57), # Lost Penguin
  (0x13004148, 0xD4), # Homing-One-Up
  (None, 0xDF), # Chuckya
  (0x13000054, None), # Eye-Ball
  (0x13001108, None), # Flamethrower
  (0x130046DC, 0xDC), # Fly-Guy
  (None, 0x89), # Item-Box
  (0x13003700, 0x65), # Ice Bully (Big)
  (0x130036C8, 0x64), # Ice Bully (Small)
  (None, 0x81), # Breakable Box
  (None, 0x82), # Grabbable Box
  (0x13001650, 0x00), # Bouncing Box
  (0x130027E4, 0x65), # Boo
  (0x130027D0, 0x00), # Boo (x3)
  (0x13002794, 0x65), # Big Boo
  (0x130007F8, 0x7A), # Star
  (0x13001B70, 0x00), # Checkerboard Elevator (Logic: DON'T TOUCH FOR VANISH CAP LEVEL)
]

BSCRIPT_START = 0x10209C

class LevelRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

    self.level_scripts = {}
    #for level in ALL_LEVELS:
    level = LVL_CASTLE_GROUNDS
    with open(f"dumps/level_scripts/{level.name}.txt", "w+") as dump_target:
      self.level_scripts[level] = LevelScriptParser.parse_for_level(self.rom, level)
      print(f'{level.name} has {len(self.level_scripts[level].objects)} objects')

      special_objs = list(filter(lambda x: x.source == "SPECIAL_MACRO_OBJ", self.level_scripts[level].objects))
      macro_objs = list(filter(lambda x: x.source == "MACRO_OBJ", self.level_scripts[level].objects))
      normal_objs = list(filter(lambda x: x.source == "PLACE_OBJ", self.level_scripts[level].objects))
      print(f' - {len(special_objs)} Special 0x2E Objects')
      print(f' - {len(macro_objs)} Macro 0x39 Objects')
      print(f' - {len(normal_objs)} Normal 0x24 Objects')
      dump_target.write(self.level_scripts[level].dump())

  @staticmethod
  def can_shuffle(model_id, bscript_address):
    for (target_bscript_address, target_model_id) in WHITELIST_SHUFFLING:
      if (target_model_id is None or target_model_id == 0x00 or target_model_id == model_id) and (target_bscript_address is None or target_bscript_address == bscript_address):
        return True
    return False

  def shuffle_enemies(self):
    pass

    '''  
    shuffle(objs_pos)
    shuffle(mem_pos)
    print(f'{LVL_MAIN_SCR.name}: {len(objs_pos)}')
    for obj_index, obj_pos in enumerate(objs_pos):
      pos = mem_pos[obj_index]
      for vec_idx, vec in enumerate(obj_pos):
        self.rom.target.seek(pos + 2 + (vec_idx * 2))
        self.rom.target.write(vec.to_bytes(2, self.rom.endianess, signed=True))'''