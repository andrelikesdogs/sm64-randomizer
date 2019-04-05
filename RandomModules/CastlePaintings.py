from randoutils import hexlify
from random import shuffle
      
from GeoLayout import GeoLayoutParser

from Rom import ROM
from Constants import ALL_LEVELS, LVL_CASTLE_INSIDE, LEVEL_ID_MAPPING, SPECIAL_WARP_IDS, WARP_ID_LOSE, WARP_ID_WIN, WARP_ID_RECOVER, PAINTING_IDS

OFFSET_LVL_GEO = (0x3CF0D0, 0x3D0DC0)

class CastlePaintingsRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

  def find_warps_for(self, level):
    return self.rom.read_cmds_from_level_block(level, [0x26])

  def find_warps_out_for(self, warp_ids, level_area):
    for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, [0x26]):
      (warp_id, lvl_id, lvl_area, dest) = data[0:4]
      
      if warp_id in warp_ids and level_area == lvl_area:
        yield (cmd, data, pos)

  def find_painting_warps(self):
    return self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, [0x27])

  def shuffle_paintings(self):
    print("- Shuffling all Castle Paintings")
    parser = GeoLayoutParser(self.rom, 0x3D0190, 0x3d0535)
    parser.process()
    parser.dump()
    
    painting_level_mapping = {}
    painting_area_mapping = {}
    painting_target_ids = {}
    painting_art_mapping = {}

    course_exits = []
    painting_entries = []

    for (cmd, data, pos) in self.find_painting_warps():
      warp_id = data[0]
      painting_level_id = data[1]

      if painting_level_id not in LEVEL_ID_MAPPING:
        continue

      level = LEVEL_ID_MAPPING[painting_level_id]

      # save all painting mem-positions, so we can redirect all of them
      if level in painting_level_mapping:
        painting_level_mapping[level].append(pos)
        continue
      
      painting_pos = None
      target_art_id = None
      if level in PAINTING_IDS:
        # determine which art currently is used
        target_art_id = PAINTING_IDS[level]

      painting_art_mapping[level] = target_art_id
        
      painting_level_mapping[level] = [pos]

      painting_level_area = None
      warp_id_lose = None
      warp_id_win = None
      warp_id_recover = None

      warp_id_lose_pos = []
      warp_id_win_pos = []
      warp_id_recover_pos = []

      # warps found inside target level
      for (warp_in_cmd, warp_in_data, warp_in_pos) in self.find_warps_for(level):
        (warp_id, lvl_id, lvl_area, warp_dest) = warp_in_data[0:4]
        if warp_id in [WARP_ID_LOSE, WARP_ID_WIN]:
          # the warp out of this level with either a win or a lose condition, tells us 
          # the area that the painting is in. this is important because warp-ids are not unique
          # and will instead be reused with a different area_id
          if painting_level_area is None:
            painting_level_area = lvl_area
            painting_area_mapping[level] = lvl_area
          elif painting_level_area != lvl_area:
            print(level.name)
            raise Exception("Level found with multiple exits")
          
        if warp_id == WARP_ID_LOSE:
          warp_id_lose = warp_dest
          warp_id_lose_pos.append(warp_in_pos)
        if warp_id == WARP_ID_WIN:
          warp_id_win = warp_dest
          warp_id_win_pos.append(warp_in_pos)
        if warp_id == WARP_ID_RECOVER:
          warp_id_recover = warp_dest
          warp_id_recover_pos.append(warp_in_pos)
      
      painting_target_ids[level] = (warp_id_win, warp_id_lose, warp_id_recover)

      course_exits.append((level, warp_id_win_pos, warp_id_lose_pos, warp_id_recover_pos))

    for level, painting_warp_pos in painting_level_mapping.items():
      #print(painting_warp_pos)
      for p in painting_warp_pos:
        self.rom.target.seek(p)
        #print([hex(b) for b in self.rom.target.read(4)])
      #print(level.name, painting_warp_pos)
      painting_entries.append((painting_area_mapping[level], painting_art_mapping[level], painting_warp_pos, painting_target_ids[level]))

    shuffle(course_exits)

    for idx, (target_level_area, target_art_id, painting_warp_pos, warp_ids) in enumerate(painting_entries):
      course_exit = course_exits[idx]
      (target_level, win_warp_mem_pos, lose_warp_mem_pos, rec_warp_mem_pos) = course_exit
      (win_id, lose_id) = warp_ids[0:2]
      #print(len(win_warp_mem_pos), len(lose_warp_mem_pos), len(rec_warp_mem_pos))
      # update painting
      for painting_mem_pos in painting_warp_pos:
        self.rom.target.seek(painting_mem_pos + 1, 0)
        self.rom.target.seek(painting_mem_pos + 1, 0)
        self.rom.target.write(bytes([target_level.level_id]))

      # update exits
      for mem_pos in win_warp_mem_pos:
        self.rom.target.seek(mem_pos + 2)

        self.rom.target.seek(mem_pos + 2) # +2, change lvl_area and dest_warp
        self.rom.target.write(bytes([target_level_area, win_id]))

      for mem_pos in lose_warp_mem_pos:
        self.rom.target.seek(mem_pos + 2)

        self.rom.target.seek(mem_pos + 2) # +2, change lvl_area and dest_warp
        self.rom.target.write(bytes([target_level_area, lose_id]))

      for mem_pos in rec_warp_mem_pos:
        self.rom.target.seek(mem_pos + 2)
        
        self.rom.target.seek(mem_pos + 2) # +2, change lvl_area and dest_warp
        self.rom.target.write(bytes([target_level_area, lose_id])) # might screw up

      # update painting
      """
        for (art_cmd, art_data, art_pos) in self.rom.read_cmds_from_level_block(LVL_CASTLE_INSIDE, filter=[0x18]):
          (art_type, art_id, c1, c2, c3, c4) = art_data
          print([hex(b) for b in art_data])

          # only these bytes are relevant for setting the painting art
          if art_type == 0x0 and art_id == target_art_id and bytes([c1, c2, c3, c4]) == bytes([0x80, 0x2D, 0x5B, 0x98]):
            print(f'found art for {level.name}')
            # determine memory position for art
            painting_pos = art_pos + 1
            break
        """

      #if target_art_id:
        #new_art_id = painting_art_mapping[target_level]
        #print(f'replacing id {target_art_id}\'s painting with {target_level.name}\'s ID: {hex(new_art_id)}')
        #occourences = parser.replace_command_values(0x18, 3, new_art_id, filter_lambda=(lambda data: data[4:8] == bytes([0x80, 0x2D, 0x5B, 0x98]) and data[2] == 1 and data[3] == target_art_id))
        #print(f'replaced {occourences} paintings')