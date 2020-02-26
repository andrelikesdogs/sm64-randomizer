from sm64r.Randoutils import format_binary

COMMAND_LENGTHS = {
  0x00: 8,
  0x01: 4,
  0x02: 8,
  0x03: 4,
  0x04: 4,
  0x05: 4,
  0x06: 4,
  0x07: 4,
  0x08: 12,
  0x09: 4,
  0x0A: None, # min 8
  0x0B: 4,
  0x0C: 4,
  0x0D: 8,
  0x0E: 8,
  0x0F: 20, # 0x14
  0x10: 16, # 0x10
  0x11: None, # min 8
  0x12: None, # min 8
  0x13: 12,
  0x14: None, # min 8
  0x15: 8,
  0x16: 8,
  0x17: 4,
  0x18: 8,
  0x19: 8,
  0x1A: 8,
  0x1D: None, # min 8
  0x1E: 8,
  0x1F: 16, # 0x10
  0x20: 4
}

class GeoLayoutParser:
  def __init__(self, rom, addr_id, addr_start, addr_end, area_id, source = "Unknown"):
    self.rom = rom
    self.addr_id = addr_id
    self.addr_start = addr_start
    self.addr_end = addr_end
    self.source = source
    self.area_id = area_id

    #print(f'Parsing GeoLayout ID: {(self.addr_id)}: {hex(self.addr_start)} - {hex(self.addr_end)}')

    self.commands_by_id = {}

    self.cursor = self.addr_start
    self.depth = 0
    self.process()
  
  def process(self):
    while True:
      cmd_byte = self.rom.read_integer(self.cursor)

      if cmd_byte in COMMAND_LENGTHS:
        cmd_length = COMMAND_LENGTHS[cmd_byte]
        if cmd_length is None:
          # dynamic length
          if cmd_byte == 0x0A:
            use_asm = self.rom.read_integer(self.cursor + 1)
            cmd_length = 12 if use_asm > 0 else 8
          if cmd_byte == 0x11 or cmd_byte == 0x12 or cmd_byte == 0x14:
            has_segment_addr = (self.rom.read_integer(self.cursor + 1) & 0xF0) == 8
            cmd_length = 12 if has_segment_addr else 8
          if cmd_byte == 0x1D:
            ms_bit = self.rom.read_integer(self.cursor + 1) & 0x1
            cmd_length = 12 if ms_bit else 8
        else:
          # static length
          pass
          
        if cmd_length is None:
          raise ValueError(f"Could not determine dynamic length for geolayout cmd {hex(cmd_byte)}")

        #print(format_binary(self.rom.read_bytes(self.cursor, cmd_length)))

        if cmd_byte not in self.commands_by_id:
          self.commands_by_id[cmd_byte] = []
        self.commands_by_id[cmd_byte].append((self.cursor, self.rom.read_bytes(self.cursor, cmd_length)))

        #print("  " * self.depth, format_binary(self.rom.read_bytes(self.cursor, cmd_length)))
        self.cursor += cmd_length

        if cmd_byte == 0x00:
          all_zero = self.rom.read_integer(self.cursor, 4) == 0
          if all_zero:
            ''' 0x00: Branch and Store '''
            segmented_addr = self.rom.read_integer(self.cursor + 4, 4)
            target_addr = self.rom.read_segment_addr(segmented_addr)

            if target_addr:
              self.cursor_prev = self.cursor
              self.cursor = target_addr
              #print(self.cursor)
              self.depth += 1
              #print("branching...")
              self.process()

              self.cursor = self.cursor_prev
              self.depth -= 1
            else:
              print(format_binary(self.rom.read_bytes(self.cursor, 8)))
              raise ValueError(f"Geometry Layout Command 0x00 segment is unresolved at {hex(self.cursor)}. Probably reading garbage")
          else:
            print(format_binary(self.rom.read_bytes(self.cursor, 8)))
            raise ValueError(f"Geometry Layout Command 0x00 is unlinked at {hex(self.cursor)}. Probably reading garbage")
        
        if cmd_byte == 0x01:
          break
      else:
        print(format_binary(self.rom.read_bytes(self.cursor, 8)))
        raise ValueError("Entered invalid geometry layout. Probably reading garbage")
        
      if self.addr_end and self.cursor >= self.addr_end:
        break
