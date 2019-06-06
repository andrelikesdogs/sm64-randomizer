import Constants

CASTLE_DOORS_TO_REPLACE = [
  (0x22, 0x13000B0C), # 0 Star Door
  (0x23, 0x13000B0C), # 1 Star Door
  (0x24, 0x13000B0C), # 3 Star Door
]

CASTLE_DOOR_LEVEL_MAPPING = {
  # Ground Floor
  0xe79e35: [Constants.LVL_BOB],
  0xe79e5d: [Constants.LVL_CCM],
  0xe79e53: [Constants.LVL_JRB, Constants.LVL_SECRET_AQUARIUM],
  0xe79e49: [Constants.LVL_SECRET_PEACH_SLIDE],
  0xe79e3f: [Constants.LVL_WF], 

  # First Floor
  0xe7f59b: [Constants.LVL_SL],
  0xe7f587: [Constants.LVL_THI],
  0xe7f591: [], # SL Mirror

  # Basement
  0xe8307b: [Constants.LVL_HMC],

  # Second Floor
}


# 3rd Star Door:
# The third and final star door leading to BITS does not conform with the others. It is always open
# but instead shows a text-box before opening when under the selected amount of stars (bparam1).
# The stairs will be unpassable as long as the star count is below 70.
# This limit is hardcoded in the game, here:
# 
#           |         ROM |          RAM |
# ----------------------------------------
# Address   |  0x8024A3A8 |     0x0053AB |
# ----------------------------------------

STAR_DOOR_LEVEL_MAPPING = {
  (0x3CF0E8, 0x3CF100): [Constants.LVL_BOWSER_1], # 8 Star Door
  (0x3CF51C, 0x3CF504): [Constants.LVL_RR, Constants.LVL_TTC, Constants.LVL_SECRET_RAINBOW], # 50 Star Door
  (0x3CF534, 0x3CF54C): [Constants.LVL_BOWSER_3], # 70 Star Door
}

STARS_PER_LEVEL = {
  Constants.LVL_BOB: 7,
  Constants.LVL_WF: 7,
  Constants.LVL_JRB: 7,
  Constants.LVL_CCM: 7,
  Constants.LVL_BBH: 7,
  Constants.LVL_HMC: 7,
  Constants.LVL_LLL: 7,
  Constants.LVL_SSL: 7,
  Constants.LVL_DDD: 7,
  Constants.LVL_SL: 7,
  Constants.LVL_WDW: 7,
  Constants.LVL_TTM: 7,
  Constants.LVL_THI: 7,
  Constants.LVL_TTC: 7,
  Constants.LVL_RR: 7,
  Constants.LVL_SECRET_PEACH_SLIDE: 2,
  Constants.LVL_SECRET_AQUARIUM: 1,
  Constants.LVL_BOWSER_1: 1,
  Constants.LVL_BOWSER_2 : 1,
  Constants.LVL_BOWSER_3: 1,
  Constants.LVL_METAL_CAP: 1,
  Constants.LVL_VANISH_CAP: 1,
  Constants.LVL_WING_CAP: 1,
  # 3 Toads
  # 2 MIPS
}

class StardoorRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def replace_all_doors(self):
    return
    
    # Replace all castle doors with 0x24 doors, in order to be able to change bparams
    castle_levelscript = self.rom.levelscripts[Constants.LVL_CASTLE_INSIDE]

    needs_replacing = []
    for object3d in castle_levelscript.objects:
      if object3d.source == 'MACRO_OBJ':
        object3d.remove(self.rom)
      
      #print(object3d.source, hex(object3d.model_id), object3d.behaviour_name)
      for (target_model_id, target_behaviour_script) in CASTLE_DOORS_TO_REPLACE:
        if (target_model_id is None or object3d.model_id == target_model_id) and (target_behaviour_script is None or object3d.behaviour == target_behaviour_script):
          needs_replacing.append(object3d)

    
    print(list(map(lambda x: (hex(x.mem_address + 0x109), hex(x.mem_address)), needs_replacing)))

    pass

  def open_level_stardoors(self):
    self.replace_all_doors()
    pass

  def shuffle_level_stardoors(self):
    self.replace_all_doors()
    pass

  def shuffle_area_star_requirements(self):
    pass