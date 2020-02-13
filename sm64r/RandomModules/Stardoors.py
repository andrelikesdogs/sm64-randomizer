import sm64r.Constants as Constants
from sm64r.Parsers.CollisionPresets import CollisionPresetParser

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
    
    # In order to inject new objects into a level, we first need to implement an additional "PUSH"
    # for this we have to find a spot. We will be removing the first entry for 0x24 for each area,
    # replacing it with a push that will contain the removed objects, as well as many more that 
    # will be added by the randomizer.

    """
    first_objs_in_area = {}

    for object3d in castle_levelscript.objects:
      if object3d.source == "PLACE_OBJ" and object3d.area_id not in first_objs_in_area:
        first_objs_in_area[object3d.area_id] = object3d

    SEGMENT_ID = 19
    SEGMENT_SIZE = 2048

    level_script_pos = 0x01900030
    level_script_length = 0

    created_segments = []
    segment_offset = 0

    for area_id, first_obj in first_objs_in_area.items():
      new_segment_start = (SEGMENT_ID << 24) | (segment_offset * SEGMENT_SIZE)
      created_segments.append(new_segment_start)
      print(first_obj.mem_address)

      # write objects in new position
      self.rom.write_bytes(level_script_pos, prev_object_bytes)
      level_script_length += len(prev_object_bytes)

      self.rom.write_bytes(level_script_pos + 18, bytes([0x07, 0x04, 0x00, 0x00])) # POP
      level_script_length += 0x04

      # replace our target object with 0x06
      prev_object_bytes = self.rom.read_bytes(first_obj.mem_address - 2, 18)

      jump_cmd = bytes([0x06, 0x08, 0x00, 0x00, *new_segment_start.to_bytes(4, self.rom.endianess)])
      load_cmd = bytes([0x17, 0x0C, 0x00, SEGMENT_ID, *level_script_pos.to_bytes(4, self.rom.endianess), *(level_script_pos + level_script_length).to_bytes(4, self.rom.endianess)])
      self.rom.write_bytes(first_obj.mem_address - 2, jump_cmd + load_cmd)
      self.rom.write_bytes(new_segment_start, prev_object_bytes)

      segment_offset += 1
      break

    #### Macro Approach (Doesn't work - no bparams available???)
    for object3d in needs_replacing:
      macro_table_address = macro_table_area_mapping[object3d.area_id]
      castle_levelscript.add_macro_object(
        macro_table_address,
        0x47, # new door preset
        object3d.rotation[1], # rot y
        object3d.position[0], # x
        object3d.position[1], # y
        object3d.position[2], # z
        10, # required stars
        10,
      )
      break
       
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
    """

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