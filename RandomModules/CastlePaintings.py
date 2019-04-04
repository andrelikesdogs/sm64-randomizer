from randoutils import hexlify
from random import shuffle

from Rom import ROM
from Constants import ALL_LEVELS, LVL_CASTLE_INSIDE, LVL_BOB, LEVEL_ID_MAPPING, SPECIAL_WARP_IDS, WARP_ID_LOSE, WARP_ID_WIN, WARP_ID_RECOVER



class CastlePaintingsRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

  def find_warps_in(self, level):
    return self.rom.read_cmds_from_level_block(level, [0x26])

  def find_warps_out(self, warp_ids, level_area):
    print(warp_ids, level_area)
    for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, [0x26]):
      (warp_id, lvl_id, lvl_area, dest) = data[0:4]
      if warp_id in warp_ids and level_area == lvl_area:
        yield (cmd, data, pos)

  def find_painting_warps(self):
    return self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, [0x27])

  def find_all_painting_warps(self):
    painting_warps = {}
    targets = []

    # go through all levels, search for their warps (in and out)
    for level in ALL_LEVELS:
      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(level, filter=[0x26]):
        warp_id = data[0]
        (level_id, level_area, dest_warp) = data[1:4]

        if warp_id == WARP_ID_WIN:
          win_warps_out.append((level_id, level_area, dest_warp, pos))
        if warp_id == WARP_ID_LOSE:
          lose_warps_out.append((level_id, level_area, dest_warp, pos))
        if warp_id == WARP_ID_RECOVER:
          recover_warps_out.append((level_id, level_area, dest_warp, pos))

      win_warps_in = []
      lose_warps_in = []
      recover_warps_in = []
      # find all out-warps
      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, filter=[0x26]):
        warp_id = data[0]
        (level_id, level_area, dest_warp) = data[1:4]

        for win_warp_out in win_warps_out:
          # out-warps destinations point to in-warps. there is no other reference.
          if warp_id == win_warp_out[2]:
            win_warps_in.append((level_id, level_area, dest_warp, pos))
        
        for lose_warp_out in lose_warps_out:
          if warp_id == lose_warp_out[2]:
            lose_warps_in.append((level_id, level_area, dest_warp, pos))

        for recover_warp_out in recover_warps_out:
          if warp_id == recover_warp_out[2]:
            recover_warps_in.append((level_id, level_area, dest_warp, pos))
        
      # if it has a win/lose warp in and out, we can randomize this painting
      if len(win_warps_in) > 0 and len(win_warps_out) > 0 and len(lose_warps_in) > 0 and len(lose_warps_out) > 0:
        print(f'{level.name}s painting can be randomized')
        for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, filter=[0x27]):
          warp_id = data[0]
          (level_id, level_area, dest_warp) = data[1:4]

          if level_id == level.level_id:
            
            if (level_id, level_area) not in painting_warps:
              targets.append((level_id, level_area, dest_warp, (win_warps_out, lose_warps_out, recover_warps_out)))
              painting_warps[(level_id, level_area)] = {
                "painting_warps": [],
                "in_warps": (win_warps_in, lose_warps_in, recover_warps_in)
              }

            painting_warps[(level_id, level_area)]["painting_warps"].append((level_id, level_area, dest_warp, pos))
    
    return (painting_warps, targets)
      
  def shuffle_paintings(self):
    print("- Shuffling all Castle Paintings")
    
    painting_level_mapping = {}

    for (cmd, data, pos) in self.find_painting_warps():
      painting_level_id = data[1]
      #print([hex(b) for b in data])

      if painting_level_id not in LEVEL_ID_MAPPING:
        continue

      level = LEVEL_ID_MAPPING[painting_level_id]

      # save all painting mem-positions, so we can redirect all of them
      painting_data = tuple([*data[0:4], pos])
      if level in painting_level_mapping:
        painting_level_mapping[level].append(painting_data)
        continue
      
      painting_level_mapping[level] = [painting_data]

      painting_level_area = None
      warp_id_lose = None
      warp_id_win = None
      warp_id_recover = None

      warp_id_lose_pos = []
      warp_id_win_pos = []
      warp_id_recover_pos = []

      for (cmd, warp_in_data, pos) in self.find_warps_in(level):
        (warp_id, lvl_id, lvl_area, warp_dest) = warp_in_data[0:4]
        if warp_id in [WARP_ID_LOSE, WARP_ID_WIN]:
          # the warp to win/lose is always the picture
          if painting_level_area is None:
            painting_level_area = lvl_area
          elif painting_level_area != lvl_area:
            print(level.name)
            raise Exception("Level found with multiple exits")
            
          if warp_id == WARP_ID_LOSE:
            warp_id_lose = warp_id
            warp_id_lose_pos.append(pos)
          if warp_id == WARP_ID_WIN:
            warp_id_win = warp_id
            warp_id_win_pos.append(pos)
          if warp_id == WARP_ID_RECOVER:
            warp_id_recover = warp_id
            warp_id_recover_pos.append(pos)
      
      print(f'{level.name} (Area {painting_level_area}) has\n- {len(warp_id_win_pos)} win exits\n -{len(warp_id_lose_pos)} lose exits\n -{len(warp_id_recover_pos)} recover exits')

      for (cmd, warp_out_data, pos) in self.find_warps_out([warp_id_lose, warp_id_win, warp_id_recover], painting_level_area):
        print([hex(b) for b in warp_out_data])
        pass


  def old_shit(self):
    (paintings, targets) = self.find_all_painting_warps()
    shuffle(targets)

    for idx in range(len(paintings)):
      (target_level_id, target_level_area, target_dest_warp, out_warps) = targets[idx]
      painting_level = list(paintings.keys())[idx]
      painting_data = paintings[painting_level]
      level = LEVEL_ID_MAPPING[painting_level[0]]
      level_area = painting_level[1]

      print(f'{LEVEL_ID_MAPPING[level.level_id].name} (Area: {hex(level_area)}) now leads to {LEVEL_ID_MAPPING[target_level_id].name} (Area {hex(target_level_area)})')
      
      for painting_warp in painting_data["painting_warps"]:
        (painting_level_id, painting_level_area, painting_dest_warp, mem_pos) = painting_warp
        self.rom.target.seek(mem_pos + 1, 0)
        self.rom.target.write(bytes([target_level_id, target_level_area, target_dest_warp]))
      
      for warp_category_index, warp_category in enumerate(out_warps):
        for warp_index, out_warp in enumerate(out_warps[warp_category_index]):

          for in_warp in painting_data["in_warps"][warp_category_index]:
            #print(f'has out warp index {warp_category_index}-{warp_index}')
            (out_warp_lvl_id, out_warp_lvl_area, out_warp_dest_warp, out_warp_mem_pos) = out_warp

            if in_warp is not None:
              #print(f'has in warp index {warp_category_index}-{warp_index}')
              in_warp = (in_warp_lvl_id, in_warp_lvl_area, in_warp_dest_warp, in_warp_mem_pos) = in_warp

              #print("changing out warps")
              #print([hex(out_warp_lvl_id), hex(out_warp_lvl_area), hex(out_warp_dest_warp)])
              #print("to")
              #print([hex(in_warp_lvl_id), hex(in_warp_lvl_area), hex(in_warp_dest_warp)])
              self.rom.target.seek(out_warp_mem_pos, 0)
              prev = self.rom.target.read(1)[0]
              print("overwrote warp in level")
              print(hex(prev), [hex(out_warp_lvl_id), hex(out_warp_lvl_area), hex(out_warp_dest_warp)])
              print(hex(prev), [hex(in_warp_lvl_id), hex(in_warp_lvl_area), hex(in_warp_dest_warp)])
              self.rom.target.write(bytes([in_warp_lvl_id, in_warp_lvl_area, in_warp_dest_warp]))

      '''
      for warp_category_index, warp_category in enumerate(painting_data["in_warps"]):
        for warp_index, in_warp in enumerate(painting_data["in_warps"][warp_category_index]):
          #print(out_warps)
          #print(warp_category_index)
          #print(warp_index)
          for out_warp in out_warps[warp_category_index]:
            #print(f'has out warp index {warp_category_index}-{warp_index}')
            (out_warp_lvl_id, out_warp_lvl_area, out_warp_dest_warp, out_warp_mem_pos) = out_warp

            if in_warp is not None:
              #print(f'has in warp index {warp_category_index}-{warp_index}')
              in_warp = (in_warp_lvl_id, in_warp_lvl_area, in_warp_dest_warp, in_warp_mem_pos) = in_warp

              #print("changing out warps")
              #print([hex(out_warp_lvl_id), hex(out_warp_lvl_area), hex(out_warp_dest_warp)])
              #print("to")
              #print([hex(in_warp_lvl_id), hex(in_warp_lvl_area), hex(in_warp_dest_warp)])
              self.rom.target.seek(out_warp_mem_pos, 0)
              prev = self.rom.target.read(1)[0]
              print("overwrote warp in level")
              print(hex(prev), [hex(out_warp_lvl_id), hex(out_warp_lvl_area), hex(out_warp_dest_warp)])
              print(hex(prev), [hex(in_warp_lvl_id), hex(in_warp_lvl_area), hex(in_warp_dest_warp)])
              self.rom.target.write(bytes([out_warp_lvl_id, out_warp_lvl_area, out_warp_dest_warp]))'''

      print("all done")
      #(castle_warps, level_warps) = connected[idx]

      #original_course = painting[1]
      #target_course = castle_warps[0][1]

      # change painting to point to different course


