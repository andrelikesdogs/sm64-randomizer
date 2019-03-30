from random import shuffle
from typing import List

from Level import Level
from Constants import LEVEL_POSITIONS, SONG_NAMES
from Rom import ROM

class MusicRandomizer:
  def __init__(self, rom : ROM):
    self.rom = rom

  def find_music_seqs(self, levels: List[Level]):
    music_seq_ids = []
    music_seq_pos = []
    for level in levels:
      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(level, filter=[0x36, 0x37]):
        sequence_id = None
        offset = 3 if cmd == 0x36 else 1
        sequence_id = data[offset]
        
        # only consider music that are in range 0 to 0x22
        valid = sequence_id < 0x22

        #print(level.name + ' has song ' + (SONG_NAMES[sequence_id] if sequence_id < len(SONG_NAMES) else str(sequence_id)))
        if valid:
          music_seq_ids.append(sequence_id)
          music_seq_pos.append((pos + offset, level))
    
    return (music_seq_ids, music_seq_pos)

  def shuffle_music(self, levels : List[Level]):
    print("- Shuffling all Music")
    (ids, pos) = self.find_music_seqs(levels)

    shuffle(ids)
    shuffle(pos)

    for seq_index in range(len(ids) - 1):
      (position, level) = pos[seq_index]
      seq_id = ids[seq_index]

      #print(f'{level.name} is now using music from {SONG_NAMES[seq_id]}')

      # write new music
      self.rom.target.seek(position, 0)
      self.rom.target.write(seq_id.to_bytes(1, 'little'))
