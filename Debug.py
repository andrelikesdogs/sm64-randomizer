from Rom import ROM

from Constants import ALL_LEVELS

class Debug:
  def __init__(self, rom : ROM):
    self.rom = rom

  def list_course_ids(self):
    print(ALL_LEVELS)
    for level in ALL_LEVELS:
      print(level.name)
      for (cmd, data, pos) in self.rom.read_cmds_from_level_block(level, filter=[0x0C]):
        print([hex(byte) for byte in data])

  def read_data(self, address_start, address_end):
    self.rom.file.seek(address_start)

    return self.rom.file.read(address_end - address_start)

  def decompress_mio0(self, address_start, address_end):
    # read header
    self.rom.file.seek(address_start, 0)
    signature = self.rom.file.read(4)

    if signature != b'MIO0':
      raise Exception("invalid signature in header")

    block_size = address_end - address_start
    decompressed_length = int.from_bytes(self.rom.file.read(4), self.rom.endianess)
    compressed_offset = int.from_bytes(self.rom.file.read(4), self.rom.endianess)
    uncompressed_offset = int.from_bytes(self.rom.file.read(4), self.rom.endianess)
    uncompressed_length = block_size - uncompressed_offset
    compressed_length = (uncompressed_offset - compressed_offset + 0x10)

    #print(f'reading {decompressed_length} bytes of compressed data')
    #print(f'offset {compressed_offset}, length: {compressed_length}')

    layout_start = self.rom.file.tell()
    #print(layout_start)
    layout_end = address_start + compressed_offset
    #print(layout_end)

    layout_length = layout_end - layout_start
    layout_cursor = layout_start

    self.rom.file.seek(layout_end)
    compressed_data = self.rom.file.read(compressed_length)
    uncompressed_data = self.rom.file.read(uncompressed_length)

    self.rom.file.seek(layout_start)
    output = bytearray()
    output_index = 0
    uncomp_index = 0
    comp_index = 0

    bit_pos = 0
    
    while output_index < decompressed_length:
      # reading layout bit in 1 byte groups
      layout_bytes = self.rom.file.read(1)[0]
      layout_cursor = layout_cursor + 1
      layout_bits = [(layout_bytes & (0x1 << i)) >> i for i in range(8)]
      layout_bits.reverse()
      
      for bit in layout_bits:
        is_uncompressed = bit == 0b1

        if output_index >= decompressed_length:
          break

        if is_uncompressed:
          output.append(uncompressed_data[uncomp_index])
          uncomp_index = uncomp_index + 1
          output_index = output_index + 1
        else:
          # 0 - read compressed data
          #print(comp_index, compressed_length)
          comp_data = compressed_data[comp_index:comp_index + 2]
          # 2 bytes for length and offset
          comp_index = comp_index + 2

          # upper-bits on first half-byte
          length = ((comp_data[0] & 0xF0) >> 4) + 3
          if length < 3 or length > 18:
            raise Exception("unplausible value, length var mismatch")

          # lower-bits on first half-byte + second byte + 1
          idx = ((comp_data[0] & 0xF) << 8) + comp_data[1] + 1
          if idx < 1 or idx > 4096:
            raise Exception("unplausible value, idx var mismatch")

          for i in range(length):
            output.append(output[output_index - idx])
            output_index = output_index + 1
          

        bit_pos = bit_pos + 1
    
      if False: #output_index % 50 == 0 or output_index == decompressed_length:
        print(output_index == decompressed_length)
        # debug stats
        print("layout", bit_pos / 8 / layout_length * 100)
        print("uncompressed", uncomp_index / uncompressed_length * 100)
        print("compressed", comp_index / compressed_length * 100)
        print("output", output_index / decompressed_length * 100)
        print("output valid:", output_index == len(output))
        print(output_index, decompressed_length)
        print('\n')
        
    print([hex(b) for b in output[0:10]])
    return output