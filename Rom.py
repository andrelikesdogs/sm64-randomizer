from pathlib import Path
import shutil

from Level import Level
from Constants import LEVEL_SCRIPT_FUNCS

KNOWN_HEADERS = [
  b'\x807\x12@\x00\x00\x00\x0f\x80$`\x00\x00\x00\x14DcZ+\xff\x8b\x02#&\x00\x00\x00\x00\x00\x00\x00\x00SUPER MARIO 64      \x00\x00\x00\x00\x00\x00\x00NSME\x00'
]
HEADER_SIZE=0x40

class ROM:
  def __init__(self, path, out_path):
    self.path = path
    self.out_path = out_path

  def __enter__(self):
    self.file = open(self.path, 'rb')
    print(f'INPUT: {self.path}')
    shutil.copyfile(self.path, self.out_path)
    print(f'OUTPUT: {self.out_path}')
    self.target = open(self.out_path, 'b+r')
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.file.close()
    self.target.close()

  def verify_header(self):
    self.file.seek(0)
    header = self.file.read(HEADER_SIZE)

    return header in KNOWN_HEADERS

  def read_cmds_from_level_block(self, level: Level, filter=[]):
    (start_position, end_position) = level.address
    self.file.seek(start_position, 0)

    cmd = None
    cmd_count = 0
    cursor = start_position
    while True:
      cmd_count = cmd_count + 1

      # if this function is used recursively, this would get lost
      self.file.seek(cursor, 0)
      cmd = self.file.read(1)[0]
      cmd_length = max(self.file.read(1)[0] - 2, 0)
      if cmd == 0x02:
        #print("Ending Level Sequence (0x02 END_LEVEL)")
        break

      cursor = cursor + cmd_length + 2
      #print('position: ' + str(cursor))

      if not len(filter) or cmd in filter:
        # read data and output
        cmd_data = self.file.read(cmd_length)
        #print([hex(b) for b in cmd_data])
        yield (cmd, cmd_data, cursor + 2)
      else:
        # skip forward
        self.file.seek(cmd_length, 1)

      if cursor > end_position:
        #print("Ending Level Sequence (end of bytes)")
        break
    #print(f'{cmd_count} level commands found')


'''
  def verify_levels(self):
    for (start_position, end_position) in LEVEL_POSITIONS:
      print(self.file.seek(start_position))

      # read cmd code
      cmd = ''
      while cmd != 0x02:
        cmd = int.from_bytes(self.file.read(1), 'big')
        cmd_length = int.from_bytes(self.file.read(1), 'big')

        # move pos by cmd length (minus 2 bytes for the cmd and length)
        self.file.seek(cmd_length - 2, 1)'''

'''
  def alter_level_music(self, level_index, music_id):
    (start_position, end_position) = LEVEL_POSITIONS[level_index]
    print(self.file.seek(start_position))

    # read cmd code
    cmd = ''
    while cmd != 0x02:
      cmd = int.from_bytes(self.file.read(1), 'little')
      cmd_length = int.from_bytes(self.file.read(1), 'little')

      cmd_name = LEVEL_CMD_TITLES[cmd] or 'UNKNOWN'

      if cmd == 0x36:
        # move cursor to sequence id pos
        sequence_id_pos = self.file.seek(3, 1)
        print(cmd, cmd_length, int.from_bytes(self.file.read(1), 'little'))
        self.target.seek(sequence_id_pos)
        self.target.write(music_id.to_bytes(1, 'little'))
        break

      # move pos by cmd length (minus 2 bytes for the cmd and length)
      self.file.seek(cmd_length - 2, 1)'''