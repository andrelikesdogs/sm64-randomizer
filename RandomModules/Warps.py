from Constants import LVL_CASTLE_COURTYARD, LVL_CASTLE_INSIDE, LVL_CASTLE_GROUNDS, LVL_THI, ALL_LEVELS, LEVEL_ID_MAPPING, LEVEL_SHORT_CODES, LVL_BOWSER_1, LVL_BOWSER_1_BATTLE, LVL_BOWSER_2, LVL_BOWSER_2_BATTLE, LVL_BOWSER_3, LVL_BOWSER_3_BATTLE
import Constants
from Spoiler import SpoilerLog
from RandomModules.Textures import TextureAtlas
from random import shuffle, choice
import logging

# Rainbow Clouds, Wing Cap, Vanish Cap, Rainbow Bonus, Secret Aquarium, Peach Slide
COURSES_WITH_NO_PAINTING = [0x12, 0x1D, 0x1B, 0x1F, 0x14, 0x11, 0x13, 0x04]

WARP_BEHAVIOURS = {
  0x13002F80: ['FAILURE'], # Painting Exit Failure
  0x13002F7C: ['SUCCESS'], # Painting Exit Success
  0x13002F70: ['RESTORE'], # Painting Exit Restore
  0x13002F88: ['FAILURE', 'SUCCESS'], # Ceiling Exit
  0x13002F90: ['FAILURE'], # Hole Exit
  0x13002F8C: ['SUCCESS'], # Hole Exit
  0x13002F84: ['RESTORE'], # Restore to Lobby
}

# The levels listed in this section have warps to different areas, that need to lead back to the same warp. This is only the case in THI in vanilla SM64
MUST_MATCH_AREA_LEVELS = [LVL_THI]

# These levels have sub-levels, that need to be exited/left through the same warp. This is only the case in bowser levels in vanilla SM64
LEVEL_CONNECTED_WARPS = {
  LVL_BOWSER_1: [LVL_BOWSER_1_BATTLE],
  LVL_BOWSER_2: [LVL_BOWSER_2_BATTLE],
  LVL_BOWSER_3: [LVL_BOWSER_3_BATTLE],
}

# This list enforces that certain levels come before other levels, in the order of which rooms are accessible. Obviously only works for SM64
ENFORCE_ORDER = {
  # Bowser 1 must be before SSL, DDD, BITFS
  LVL_BOWSER_1: Constants.BASEMENT_LEVELS,
  LVL_BOWSER_2: [*Constants.FIRST_FLOOR_LEVELS, *Constants.SECOND_FLOOR_LEVELS],
}

class WarpRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def _pick_best_fitting_warp(self, target_group_name, warp, warps_available):
    if target_group_name in list(warps_available.keys()):
      return choice(warps_available[target_group_name])

    target_key = choice(list(warps_available.keys()))
    return choice(warps_available[target_key])

  def shuffle_level_entries(self, painting_mode : str):
    # levels that contain entries to levels
    entry_levels = [LVL_CASTLE_COURTYARD, LVL_CASTLE_GROUNDS, LVL_CASTLE_INSIDE]
    entry_level_course_ids = [level.level_id for level in entry_levels]

    # anim warps are warps in the overworld that simply connect to themselves.
    # they confuse me but i suspect they only handle animation stuff

    anim_warps = [] # Warp, Warp, Warp
    ow_warps = {} # { (Level, Area): ([Entry Warp, Entry Warp], (Anim Exit, Anim Exit)), (Entry, Anim Exits), (Entry, Anim Exits)
    lvl_warps = {} # { (Level, Area): FAIL: [ Warp, Warp ], SUCCESS: Warp, Warp }

    # go through all levels that contain entries (all castle levels)
    for level in entry_levels:
      # go through all warps, take note of the special animated warps
      # they can be identified by their warp_id leading to their target_warp_id
      for warp in self.rom.levelscripts[level].warps:
        # painting warps and warp-ids that match levels without a painting a grouped by
        # target-level and target-area-id to ensure we don't break THI
        if warp.type == 'PAINTING' or  warp.to_course_id in COURSES_WITH_NO_PAINTING:
          target_level = LEVEL_ID_MAPPING[warp.to_course_id]
          key = (target_level, warp.to_area_id)

          ow_warps.setdefault(key, ([], {})) # level entries (paintings, holes, etc), anim exits (lead to themselves)

          ow_warps[key][0].append(warp)
        else:
          # special target == dest warps
          if warp.warp_id == warp.to_warp_id:
            anim_warps.append(warp)
    
    anim_warp_ids = [warp.warp_id for warp in anim_warps]

    # now collects all exits from the levels we have the entries of
    warp_types = {
      0xf0: "SUCCESS",
      0xf1: "FAILURE",
      #0xf3: "RECOVER", # ye let's not shuffle this for now
    }
    for key in ow_warps.keys():
      (level, area_id) = key

      lvl_warps[key] = {}

      # get all warps inside the level that target this level and this area_id
      for warp in self.rom.levelscripts[level].warps:
        # 1. warp must lead to one of the anim exits from the overworld
        # 2. warp must lead to one of the OW levels
        # 3. warp must be of one of the warp types
        if warp.to_warp_id in anim_warp_ids and warp.to_course_id in entry_level_course_ids and warp.warp_id in warp_types:
          if level not in MUST_MATCH_AREA_LEVELS or warp.area_id == area_id:
            warp_type = warp_types[warp.warp_id]

            # add a specific warp-type to the exits list
            lvl_warps[key].setdefault(warp_type, []).append(warp)
            
            # add all the anim warps that this warp refers to
            ow_warps[key][1].setdefault(warp_type, []).extend([anim_warp for anim_warp in anim_warps if anim_warp.warp_id == warp.to_warp_id])

    # Debug View of all Warps found
    for ((level, area), (entry_warps, anim_warp_groups)) in ow_warps.items():
      logging.debug(f'Level: {level.name} Area: {hex(area)}')

      logging.debug("  Exits")
      for (warp_group, exit_warps) in lvl_warps[(level, area)].items():
        logging.debug(" " * 2 + str(warp_group))
        logging.debug(" " * 4 + repr([(hex(warp.to_warp_id), hex(warp.memory_address)) for warp in exit_warps]))
      logging.debug('')
      logging.debug("  Entries:")
      logging.debug(repr([(hex(warp.warp_id), hex(warp.memory_address)) for warp in entry_warps]))
      logging.debug('')
      logging.debug("  Anim Warps:")
      for (anim_warp_group, entry_anim_warps) in anim_warp_groups.items():
        logging.debug(" " * 2 + str(anim_warp_group))
        logging.debug(" " * 4 + repr([(hex(warp.to_warp_id), hex(warp.memory_address)) for warp in entry_anim_warps]))
      logging.debug('-' * 50)

    valid_warps = False
    target_warp_levels = list(lvl_warps.keys())
    #shuffle(target_warp_levels)

    while not valid_warps:
      shuffle(target_warp_levels)

      idx = 0
      valid_warps = True
      for ((original_level, original_area), ow_entry_exit_sets) in ow_warps.items():
        (target_level, target_area) = target_warp_levels[idx]

        # ensure correct order
        if target_level in ENFORCE_ORDER.keys():
          logging.info(f'ensuring validity with level {target_level.name}')
          # bowser in the fire sea for example can't be on the first floor, because that's the boss that gives you the key for the first floor
          if original_level in ENFORCE_ORDER[target_level]:
            logging.info(f'{target_level.name} cant be in {original_level}, because it cant be reached without it')
            valid_warps = False
            break
        idx += 1

    idx = 0
    for (original_level_area, (entries, anim_exits)) in ow_warps.items():
      level_area_target = target_warp_levels[idx]
      SpoilerLog.add_entry('warps', f'{original_level_area[0].name} leads to {level_area_target[0].name}')
      #print(f'{original_level_area[0].name} now leads to {level_area_target[0].name} ({len(entries)} entries updating)')
      for entry_warp in entries:
        #print(hex(level_area_target[0].level_id))
        entry_warp.set(self.rom, "to_course_id", level_area_target[0].level_id)
        entry_warp.set(self.rom, "to_area_id", level_area_target[1])

      orig_exits = lvl_warps[original_level_area]
      level_exits = lvl_warps[level_area_target]

      # replace all exit warps in the target level with ones leading to the original entry
      for (group_name, warps) in level_exits.items():
        logging.info(f'{level_area_target[0].name.ljust(40, " ")} (Area {hex(level_area_target[1])}): {group_name}: Animation Warps replacing {len(warps)} entries')
        for warp in warps:
          target_warp = self._pick_best_fitting_warp(group_name, warp, orig_exits)
          warp.set(self.rom, "to_course_id", target_warp.to_course_id)
          warp.set(self.rom, "to_warp_id", target_warp.to_warp_id)
          warp.set(self.rom, "to_area_id", target_warp.to_area_id)
      
      # set painting
      if painting_mode == 'match':
        if original_level_area[0] in LEVEL_SHORT_CODES and level_area_target[0] in LEVEL_SHORT_CODES:
          from_code = f'painting_{LEVEL_SHORT_CODES[original_level_area[0]].lower()}'
          to_code = f'painting_{LEVEL_SHORT_CODES[level_area_target[0]].lower()}'

          if TextureAtlas.has_texture(from_code):
            if TextureAtlas.has_texture(to_code):
              TextureAtlas.copy_texture_from_to(self.rom, from_code, to_code)
            else:
              TextureAtlas.copy_texture_from_to(self.rom, from_code, 'painting_unknown')

      idx += 1

'''
    original_warps = list(warp_connections.items())
    target_warps = list(warp_connections.items())
    shuffle(target_warps)

    for idx, (level, area) in enumerate(target_warps):
      original_warp = original_warps[idx]
      print(f'{original_warp[0][0].name} now leads to {level[0].name}')
      pass
      

    for level_exits in lvl_warps:
      for level_exit in level_exits:
        pass

    print(len(lvl_warps))
    print(len(ow_warps_by_level_by_area.keys()))
    #print('\n'.join([str(item) for item in ow_warps_cleaned_dict.items()]))'''