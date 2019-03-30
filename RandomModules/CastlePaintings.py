from Rom import ROM

from random import shuffle
from Constants import LEVEL_POSITIONS

class CastlePaintingsRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

  def find_all_painting_warps(self):
    warp_ids = []
    targets = []
    for (cmd, data, pos) in self.rom.read_cmds_from_level_block(LEVEL_POSITIONS["INSIDE_CASTLE"], filter=[0x27]):
      warp_ids.append((data[0], pos))
      targets.append(data[1:3])
    
    return (warp_ids, targets)

  def shuffle_paintings(self):
    print("- Shuffling all Castle Paintings")
    # todo: list ids so we can shuffle only some of them

    (warp_ids, targets) = self.find_all_painting_warps()

    #shuffle(warp_ids)
    shuffle(targets)

    for warp_index in range(len(warp_ids)):
      (warp_id, rom_pos) = warp_ids[warp_index]
      target_data = targets[warp_index] # course_id, course_area, warp_id

      #print("redirecting warp_id")

      self.rom.target.seek(rom_pos + 1, 0)
      self.rom.target.write(target_data)
