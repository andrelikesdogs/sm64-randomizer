from Constants import ALL_LEVELS, CAP_LEVELS, MISSION_LEVELS, BOWSER_STAGES, LVL_BOB, SPECIAL_LEVELS, LVL_MAIN_SCR, LVL_CASTLE_GROUNDS
from randoutils import format_binary
import sys
from Entities.Object3D import Object3D
#from Parsers.LevelScript import LevelScriptParser

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
  (0x130031DC, 0xC3), # Bob-Omb Buddy
  (0x1300478C, 0x66),
  #(None, 0xDF), # Chuckya
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
  (0x13002F74, 0x00), # Mario Start 1
]

BSCRIPT_START = 0x10209C

class LevelRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  @staticmethod
  def can_shuffle(obj : Object3D):
    if obj.source == "MARIO_SPAWN":
      return True
    else:
      for (target_bscript_address, target_model_id) in WHITELIST_SHUFFLING:
        if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
          return True
      return False

  def shuffle_enemies(self):
    for (level, parsed) in self.rom.levelscripts.items():
      if level in SPECIAL_LEVELS:
        continue

      # randomize positions
      positions = []
      objects = []
      for obj in parsed.objects:
        if LevelRandomizer.can_shuffle(obj):
          #print(obj.position)
          positions.append(obj.position)
          objects.append(obj)

      shuffle(positions)
      for idx, obj in enumerate(objects):
        position = positions[idx]
        obj.set(self.rom, 'position', position)
    '''
    for level in self.level_scripts:
      positions = []
      objects = []

      if self.level_scripts[level].mario_spawn:
        mario_spawn = self.level_scripts[level].mario_spawn
        positions.append(mario_spawn[1])
        objects.append(mario_spawn)
      
      for obj in self.level_scripts[level].objects:
        if LevelRandomizer.can_shuffle(obj.model_id, obj.behaviour):
          positions.append(obj.position)
          objects.append(obj)
      
      shuffle(positions)
      for idx, obj in enumerate(objects):
        position = positions[idx]

        if type(obj) is Object3D:
          obj.change_position(self.rom, position)
        elif type(obj) is tuple: # temp mario thing:
          #print(level.name, "rando mario")
          (area_id, translate, rotation, mem_address) = obj
          #print("changing", translate, "to", position)
          #print(position)
          self.rom.write_integer(mem_address + 4, position[0], 2, True)
          self.rom.write_integer(mem_address + 6, position[1], 2, True)
          self.rom.write_integer(mem_address + 8, position[2], 2, True)

    pass

    '''  