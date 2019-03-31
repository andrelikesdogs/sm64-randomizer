
from random import shuffle

from Rom import ROM
from Constants import ALL_LEVELS, LVL_CASTLE_INSIDE, LEVEL_ID_MAPPING, WARP_ID_LOSE, WARP_ID_WIN, SPECIAL_WARP_IDS

class CastlePaintingsRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

  def find_all_painting_warps(self):
    # warps from painting include >6 warps:
    # level: castle inside
    # - painting warp (enter level)
    # - painting warp (???)
    # - painting warp (???)
    # level: target level
    # - victory warp (leave level) (ID 0xf0)
    # - defeat warp (leave level) (ID 0xf1)
    # - safe recover (leave level) (ID0xf3)
    # level: castle inside
    # - victory warp (leave level) (ID 0xf0)
    # - defeat warp (leave level) (ID 0xf1)
    # - safe recover (leave level) (ID0xf3)

    levels_found_in_paintings = []
    painting_warps = []
    connected_warps = []
    for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, filter=[0x27]):
      warp_id = data[0]
      (level_id, level_area, dest_warp) = data[1:4]

      if level_id not in LEVEL_ID_MAPPING:
        print(f'level id {level_id} is not known, cant randomize this painting')
        continue

      if level_id not in levels_found_in_paintings:
        painting_warps.append((warp_id, level_id, level_area, dest_warp, pos))
        levels_found_in_paintings.append(level_id)

    for painting_warp in painting_warps:
      level_id = painting_warp[1]


      # warps in castle to level
      castle_warps = []

      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, filter=[0x26]):
        warp_id = data[0]
        (cstl_level_id, cstl_level_area, cstl_dest_warp) = data[1:4]

        if level_id == cstl_level_id:
          print("found castle warp")
          castle_warps.append((cstl_level_id, cstl_level_area, cstl_dest_warp, pos))

      # warps in level back to castle
      level_warps = []
      has_win_warp = False
      has_lose_warp = False

      for (cmd, data, pos ) in self.rom.read_cmds_from_level_block(LEVEL_ID_MAPPING[level_id], filter=[0x26]):
        warp_id = data[0]
        (lvl_level_id, lvl_level_area, lvl_dest_warp) = data[1:4]

        if warp_id in SPECIAL_WARP_IDS:
          print("found level warp")
          level_warps.append((lvl_level_id, lvl_level_area, lvl_dest_warp, pos))

          if warp_id == WARP_ID_LOSE:
            has_lose_warp = True
          if warp_id == WARP_ID_WIN:
            has_win_warp = True

      if has_lose_warp and has_win_warp:
        connected_warps.append((castle_warps, level_warps))

    return (painting_warps, connected_warps)

  def shuffle_paintings(self):
    print("- Shuffling all Castle Paintings")
    # todo: list ids so we can shuffle only some of them

    (paintings, connected) = self.find_all_painting_warps()

    shuffle(connected)

    for idx in range(len(paintings)):
      painting = paintings[idx]
      (castle_warps, level_warps) = connected[idx]

      original_course = painting[1]
      target_course = castle_warps[0][1]

      print(f'{LEVEL_ID_MAPPING[original_course].name} now leads to {LEVEL_ID_MAPPING[target_course].name}')

      # change painting to point to different course

    print(paintings)
    print(connected)

