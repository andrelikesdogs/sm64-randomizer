from randoutils import hexlify
from random import shuffle
      
from GeoLayout import GeoLayoutParser

from Rom import ROM
from Constants import ALL_LEVELS, LVL_CASTLE_INSIDE, LVL_BOB, LVL_CCM, LEVEL_ID_MAPPING, MISSION_LEVELS, SPECIAL_WARP_IDS, WARP_ID_LOSE, WARP_ID_WIN, WARP_ID_RECOVER, PAINTING_OFFSETS

PAINTINGS_EXT_ROM_OFFSET = 0xE0BB07
PAINTING_BYTE_SIZE = int(32*64*16 / 8) # 4096

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
    print("Randomizing Castle Level Entries")

    painting_level_mapping = {}
    painting_area_mapping = {}
    painting_target_ids = {}

    course_exits = []
    painting_entries = []

    art_bytes = {}
    if self.rom.rom_type == "EXTENDED":
      # save all paintings
      for level in MISSION_LEVELS:
        if level in PAINTING_OFFSETS:
          (upper_part, lower_part) = PAINTING_OFFSETS[level]
          self.rom.file.seek(PAINTINGS_EXT_ROM_OFFSET + upper_part, 0)
          upper_bytes = self.rom.file.read(PAINTING_BYTE_SIZE)
          self.rom.file.seek(PAINTINGS_EXT_ROM_OFFSET + lower_part, 0)
          lower_bytes = self.rom.file.read(PAINTING_BYTE_SIZE)

          art_bytes[level] = {
            "address": (upper_part, lower_part),
            "bytes": (upper_bytes, lower_bytes)
          }

    #print([[hex(c) for c in b["address"]] for b in art_bytes.values()])

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
      painting_entries.append((painting_area_mapping[level], level, painting_warp_pos, painting_target_ids[level]))

    shuffle(course_exits)

    for idx, (target_level_area, orig_level, painting_warp_pos, warp_ids) in enumerate(painting_entries):
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

      if orig_level in art_bytes and target_level in art_bytes:
        (p1, p2) = art_bytes[orig_level]["address"]
        (b1, b2) = art_bytes[target_level]["bytes"]
        self.rom.target.seek(PAINTINGS_EXT_ROM_OFFSET + p1, 0)
        self.rom.target.write(b1)
        self.rom.target.seek(PAINTINGS_EXT_ROM_OFFSET + p2, 0)
        self.rom.target.write(b2)
