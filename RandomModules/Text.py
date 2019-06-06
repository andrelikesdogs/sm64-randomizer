import sys
import string
from random import shuffle
from Entities.TextEntryDialog import TextEntryDialog
from typing import NamedTuple
from randoutils import format_binary

DATA_DIALOG_START = 0x803156
TBL_DIALOG_START = 0x81311E
TBL_DIALOG_END = TBL_DIALOG_START + 170 * 16
TBL_LEVEL_NAMES = 0x8140BE
TBL_ACT_NAMES = 0x814A82

TEXT_TO_IGNORE = [25, 26, 27, 28, 29]

SM64_ENCODING_CHARS = {
  0x50: '[UP]',
  0x51: '[DOWN]',
  0x52: '[LEFT]',
  0x53: '[RIGHT]',
  0x54: '[A]',
  0x55: '[B]',
  0x56: '[C]',
  0x57: '[Z]',
  0x58: '[R]',
  0x6F: ',',
  0xD0: '  ',
  0xD1: "[THE]",
  0xD2: "[YOU]",
  0x9E: ' ',
  0x9F: '-',
  0xE1: '(',
  0xE2: ')(',
  0xE3: ')',
  0xE4: '+',
  0xE5: '&',
  0xE6: ':',
  0xF2: '!',
  0xF4: '?',
  0xF5: '"',
  0xF6: '"',
  0xF7: '~',
  0xF9: '$',
  0xFA: '[STAR]',
  0xFB: '[X]',
  0xFC: '[.]',
  0xFD: '[STAR_UNOBTAINED]',
  0xFE: '\n',
  0xFF: '[END]'
}
idx = 0

for i in range(10):
  SM64_ENCODING_CHARS[idx] = str(i)
  idx += 1

for char in string.ascii_uppercase:
  SM64_ENCODING_CHARS[idx] = char
  idx += 1

for char in string.ascii_lowercase + '\'.':
  SM64_ENCODING_CHARS[idx] = char
  idx += 1

keys = list(sorted(SM64_ENCODING_CHARS.keys()))

for key in keys:
  pass
#  print(hex(key), SM64_ENCODING_CHARS[key])

class TextRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def read_text_at_offset(self, offset):
    # 0x111A13 0x7D34
    cursor = DATA_DIALOG_START + offset
    char = None
    text = []
    charcodes = []

    while char != '[END]':
      charcode = self.rom.read_integer(cursor)
      #print(charcode)

      if charcode not in SM64_ENCODING_CHARS:
        charcode = 0x9E

      charcodes.append(charcode)
      char = SM64_ENCODING_CHARS[charcode]
      text.append(char)
      cursor += 1
      
    return ''.join(text)
    
  def read_dialog_table_entries(self):
    cursor = TBL_DIALOG_START 
    entry_id = 0
    entries = []

    while cursor < TBL_DIALOG_END:
      table_entry = self.rom.read_bytes(cursor, 14)
      offset = self.rom.read_integer(cursor + 14, 2)

      text_at_entry = self.read_text_at_offset(offset)
      entries.append(TextEntryDialog(entry_id, text_at_entry, offset, mem_address_pointer=cursor, mem_address_text=DATA_DIALOG_START+offset))
      entry_id += 1
      cursor += 16
      
    return entries

  def shuffle_dialog_pointers(self):
    self.dialog_entries = self.read_dialog_table_entries()
    shuffled_entries = self.dialog_entries.copy()

    shuffle(shuffled_entries)

    for entry_index, entry in enumerate(self.dialog_entries):
      new_entry = shuffled_entries[entry_index]
      entry.set(self.rom, "offset", new_entry.offset)
  
    
'''
  def read_entries(self):
    entries = []
    cursor = DIALOG_START

    while cursor < DIALOG_END:
      char = None
      entry = []

      while char != SM64_ENCODING_CHARS[0xFF]:
        char_int = self.rom.read_integer(cursor)
        if char_int in SM64_ENCODING_CHARS:
          char = SM64_ENCODING_CHARS[char_int]
          #print(char)
          entry.append(char)
        
        cursor += 1
      
      print(''.join(entry))
      entries.append(entry)'''