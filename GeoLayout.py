from Constants import GEO_SCRIPT_FUNCS
from Rom import ROM
import typing

CMD_LENGTH = {
  0x00: 8,
  0x01: 4,
  0x02: 8,
  0x03: 4,
  0x04: 4,
  0x05: 4,
  0x06: None,
  0x07: None,
  0x08: 12, # figure out
  0x09: 4,
  0x0A: lambda data: 12 if data[1] > 0 else 8,
  0x0B: 4,
  0x0C: 4,
  0x0D: 8,
  0x0E: 8,
  0x0F: 14,
  0x10: 16,
  0x11: lambda data: 12 if data[1] > 0 else 8,
  0x12: lambda data: 12 if data[1] > 0 else 8,
  0x13: lambda data: 12, # figure out
  0x14: lambda data: 12 if data[1] > 0 else 8,
  0x15: 8,
  0x16: 8,
  0x17: 4,
  0x18: 8,
  0x19: 8,
  0x1A: 8,
  0x1D: lambda data: 12 if data[1] & 0x80 > 0 else 8,
  0x1E: 8,
  0x1F: 16,
  0x20: 4
}

class GeoLayoutParser:
  def __init__(self, rom: ROM, address_start : int, address_end : int):
    self.rom = rom

    self.address_start = address_start
    self.address_end = address_end

    self.rom.file.seek(address_start, 0)
    self.data = self.rom.file.read(address_end - address_start)

    self.commands = []
    self.was_processed = False

  def process(self):
    cursor_pos = 0
    indent = 0
    while cursor_pos < len(self.data):
      # determine number of bytes to be read
      cmd = self.data[cursor_pos]

      if cmd is None:
        print("GEO Layout EOF")
        break

      if cmd not in CMD_LENGTH:
        print(f'{hex(self.address_start + cursor_pos).ljust(10, "0")}: {hex(cmd)}')
        print('next few bytes:')
        print([hex(b) for b in self.data[cursor_pos:cursor_pos+30]])
        raise Exception("No idea where we are")

      cmd_length = None
      if type(CMD_LENGTH[cmd]) is int:
        cmd_length = CMD_LENGTH[cmd]
      elif callable(CMD_LENGTH[cmd]):
        cmd_length = CMD_LENGTH[cmd](self.data[cursor_pos:cursor_pos+16])
      else:
        print(hex(cmd))
        raise Exception("No idea how long this command is")

      if cmd == 0x04:
        indent = indent + 1
      if cmd == 0x05:
        indent = indent - 1

      #print(GEO_SCRIPT_FUNCS[cmd])
      #print([hex(b) for b in self.data[cursor_pos:cursor_pos + cmd_length]])
      self.commands.append((indent, cursor_pos, self.data[cursor_pos:cursor_pos + cmd_length]))
      cursor_pos = cursor_pos + cmd_length

    self.was_processed = True

  def replace_command_values(self, cmd, index, value, filter_lambda=lambda d: True):
    if not self.was_processed:
      raise Exception("GeoLayouts weren't processed. Please call 'process()' prior to manipulating the data.")
    count = 0
    for (_, pos, command) in self.commands:
      if command[0] == cmd and command[4:8] == bytes([0x80, 0x2D, 0x5B, 0x98]) and command[2] == 1: print([hex(p) for p in command])
      if command[0] == cmd and filter_lambda(command):
        count = count + 1
        self.rom.target.seek(self.address_start + pos)
        data = self.rom.target.read(8)
        print([f'>{hex(b)}' if i == index else hex(b) for i, b in enumerate(data)])
        self.rom.target.seek(self.address_start + pos + index)
        self.rom.target.write(bytes([value]))

    
    return count

  def dump(self):
    for (indent, pos, command) in self.commands:
      print(f'{hex(self.address_start + pos).ljust(8, "0")}:{" " * 2 * indent}{[hex(c) for c in command]}')