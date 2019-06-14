import Constants
from Parsers.CollisionPresets import CollisionPresetParser

CASTLE_DOORS_TO_REPLACE = [
  (0x22, 0x13000B0C), # 0 Star Door
  (0x23, 0x13000B0C), # 1 Star Door
  (0x24, 0x13000B0C), # 3 Star Door
]

KEY_DOORS = [
  (0x25, 0x13000AFC), # Keyhole Door
]

CASTLE_DOOR_LEVEL_MAPPING = {
  # Ground Floor
  0xe79e35: [Constants.LVL_BOB],
  0xe79e5d: [Constants.LVL_CCM],
  0xe79e53: [Constants.LVL_JRB, Constants.LVL_SECRET_AQUARIUM],
  0xe79e3f: [Constants.LVL_SECRET_PEACH_SLIDE],
  0xe79e49: [Constants.LVL_WF], 

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
    # Replace all castle doors with macro object doors, in order to be able to change bparams
    # Delete all doors in castle and keep track of properties
    castle_levelscript = self.rom.levelscripts[Constants.LVL_CASTLE_INSIDE]

    needs_replacing = []
    for object3d in castle_levelscript.objects:
      for (target_model_id, target_behaviour_script) in CASTLE_DOORS_TO_REPLACE:
        if (target_model_id is None or object3d.model_id == target_model_id) and (target_behaviour_script is None or object3d.behaviour == target_behaviour_script):
          object3d.remove(self.rom)
          needs_replacing.append(object3d)
          #object3d.remove(self.rom)
          

    # Add new macro preset for door
    preset_parser = CollisionPresetParser.get_instance(self.rom)

    # 0x47 will be the new default door - previously unused
    preset_parser.overwrite_macro_entry(0x47, 0x22, 0x13000B0C, 0, 0)
    
    macro_table_area_mapping = {
      0x1: 0xE8326B,
      0x2: 0xE832E7,
      0x3: 0xE832F3,
    }

    for object3d in needs_replacing:
      if object3d.area_id != 0x3:
        continue

      # peach slide door is turned wrong way??
      rot_y = object3d.rotation[1]
      if object3d.mem_address == 0xe79e3f:
        pass
      
      print(object3d)
      
      macro_table_address = macro_table_area_mapping[object3d.area_id]
      castle_levelscript.add_macro_object(
        macro_table_address,
        0x47, # new door preset
        rot_y, # rot y
        object3d.position[0], # x
        object3d.position[1], # y
        object3d.position[2], # z
        10, # required stars
      )
    
    # Add new macro entries to Castle Inside
    #           ROM Address  Hex Address
    #  Area 1   15217259     0xE8326B     
    #  Area 2   15217383     0xE832E7
    #  Area 3   15217395     0xE832F3

    # JRB Door
    #castle_levelscript.add_macro_object(0xE8326B, 0x47, 225, 1075, 205, -229, 10, 0)
    #castle_levelscript.add_macro_object(0xE8326B, 0x47, 0, -1050, -50, 750, 10, 0)
    #castle_levelscript.add_macro_object(0xE8326B, 0x47, 90, -950, -50, 750, 10, 0)
    #castle_levelscript.add_macro_object(0xE8326B, 0x47, 180, -1050, -50, 700, 10, 0)
    #castle_levelscript.add_macro_object(0xE8326B, 0x47, 270, -950, -50, 700, 10, 0)

    #area_1_macro_table = castle_levelscript.macro_tables[0xE8326B]
    #area_2_macro_table = castle_levelscript.macro_tables[0xE832E7]
    #area_3_macro_table = castle_levelscript.macro_tables[0xE832F3]



    pass

  def open_keydoors(self):
    castle_levelscript = self.rom.levelscripts[Constants.LVL_CASTLE_INSIDE]
    for object3d in castle_levelscript.objects:
      for (target_model_id, target_behaviour_script) in KEY_DOORS:
        if (target_model_id is None or object3d.model_id == target_model_id) and (target_behaviour_script is None or object3d.behaviour == target_behaviour_script):
          object3d.set(self.rom, 'bparams', (0, object3d.bparams[1], 0, 0))


  def open_level_stardoors(self):
    self.replace_all_doors()
    pass

  def shuffle_level_stardoors(self):
    self.replace_all_doors()
    pass

  def shuffle_area_star_requirements(self):
    pass