from random import shuffle, choice
from sm64r.Randoutils import format_binary

INSTRUMENT_SET_LENGTHS = [
  6, # NLST 0 - SFX - 8000hz
  9, # NLST 1 - SFX, Footsteps - 8000hz
  3, # NLST 2 - SFX, Water - 8000hz
  10, # NLST 3 - SFX, Sand (?) - 8000hz
  16, # NLST 4 - SFX - 8000hz
  16, # NLST 5 - SFX
  16, # NLST 6 - SFX
  15, # NLST 7 - SFX, Misc
  27, # NLST 8 - Mario
  7, # NLST 9 - SFX
  24, # NLST 10 - SFX, Voices
  12, # NLST 11 - Music, Snow Theme
  16, # NLST 12 - Music, Unusued
  13, # NLST 13 - Music, Race Theme (Slides, KtQ)
  7, # NLST 14 - Music, Inside Castle
  4, # NLST 15 - Music, SSL, LLL
  10, # NLST 16 - Music, Haunted House Theme
  14, # NLST 17 - Music, Title Theme
  12, # NLST 18 - Music, Bowser Battle Theme
  16, # NLST 19 - Music, Water (JRB, DDD) Theme
  5, # NLST 20 - Music, Piranha Plant Sleeping
  10, # NLST 21 - Music, HMC
  2, # NLST 22 - Star Select
  13, # NLST 23 - Music, Wing Cap
  15, # NLST 24 - Music, Metal Cap
  13, # NLST 25 - Music, Bowser Course Theme
  13, # NLST 26 - Music, Fanfares
  12, # NLST 27 - Music, Boss Fight
  7, # NLST 28 - Music, Looping Stairs
  6, # NLST 29 - Music, Final Boss Fight, Church Organs
  4, # NLST 30 - Music, Unused
  13, # NLST 31 - Music, Star Catch (?)
  9, # NLST 32 - Music, Toad
  4, # NLST 33 - Music, Ghost Merry-Go-Round
  12, # NLST 34 - Music, Bob-Omb Battleifeld
  8, # NLST 35 - Music, Unusued
  10, # NLST 36 - Music, File Select
  16, # NLST 37 - Music, Credits
]

class InstrumentRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def shuffle_instruments(self):
    '''
    # Lookup Table Method
    instrument_table = self.rom.read_bytes(0x7cc620, 0x23 * 2) # 0x25 instrument sets (half bytes)

    instrument_table = list(map(lambda x: [0xf0 & x, 0x0f & x], list(instrument_table)))
    print(instrument_table)

    print(format_binary(instrument_table))
    '''

    # Instrument Table Method
    sequence_instrument_table = list(self.rom.read_bytes(0x7cc674, 37))

    instruments_tuples = [(seq_pair & 0xf0, seq_pair & 0x0f) for seq_pair in sequence_instrument_table]

    current_idx = 0
    tries = 0
    while current_idx < len(instruments_tuples):
      if tries > 1000:
        #print(f'couldnt find new inst set for seq index ${hex(current_idx)}')
        break
      new_inst_set = choice(instruments_tuples) # pick one at a time, allowing duplicates
      old_inst_set = instruments_tuples[current_idx]

      # check if it chose the default
      identical = new_inst_set[1] == old_inst_set[1]

      # are both from music or are both from sfx
      sfx_type_match = (new_inst_set[1] > 10 and old_inst_set[1] > 10) or (new_inst_set[1] < 10 and old_inst_set[1] < 10)

      # correct instrument lengths
      inst_lengths_gte = INSTRUMENT_SET_LENGTHS[new_inst_set[1]] >= INSTRUMENT_SET_LENGTHS[old_inst_set[1]]
      #is_short_instrument_set = INSTRUMENT_SET_LENGTHS[new_inst_set[1]] < 5
      
      if not identical and sfx_type_match and inst_lengths_gte:
        # use old inst for #0 and new one for #1 because #0 is not really changing much
        #print(f'instrument change: [{hex(old_inst_set[0])} {hex(old_inst_set[1])}] to [{hex(old_inst_set[0])} {hex(new_inst_set[1])}]')
        self.rom.write_byte(0x7cc674 + current_idx, bytes([old_inst_set[0] | new_inst_set[1]]))
        current_idx = current_idx + 1
        tries = 0
      tries = tries + 1