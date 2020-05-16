import os
import sys
import numpy as np
import struct

from sm64r.Randoutils import format_binary
from sm64r.Parsers.OpcodeHandlers import handle_op

# Notes so im not being dumb

# On Sign Extension
"""
Signed and Zero Extension
An integer register on the MIPS is 32 bits. When a value is loaded from memory with fewer than 32 bits, the remaining bits must be assigned.
Sign extension is used for signed loads of bytes (8 bits using the lb instruction) and halfwords (16 bits using the lh instruction). Sign extension replicates the most significant bit loaded into the remaining bits.
Zero extension is used for unsigned loads of bytes (lbu) and halfwords (lhu). Zeroes are filled in the remaining bits.
"""

# On L- Operations
"""
Operation: 32- bit processors
vAddr ← sign_extend(offset) + GPR[base]
(pAddr, uncached) ← AddressTranslation (vAddr, DATA, LOAD) pAddr ← pAddr(PSIZE-1).. 2 || (pAddr1..0 xor ReverseEndian2) memword ← LoadMemory (uncached, BYTE, pAddr, vAddr, DATA) byte ← vAddr1..0 xor BigEndianCPU2
GPR[rt] ← sign_extend(memword7+8*byte..8*byte)
"""

# On Offset/Base in Mem Instructions
"""
Base is the literal address of the base register.
Offset is an immediate added to the base with sign extension.
Lw t0, 0x0 (T1)
0x0 is my offset
(T1) is my base
Remember sign extension is a thing, so
Lui at, 0x8034
Lw t1, 0xb170 (at)
Loads from 0x8033b170. AT is the base, 0xFFFFB170 is my offset
"""

class OpcodeEmulation:
  def __init__(self, rom):
    self.rom = rom
    self.ptr = 0
    self.instructions = []
    self.breakpoints = []

    self.rom_data = self.rom.file.read()
    print(f"Read {len(self.rom_data)} bytes of ROM data")

    self.reset_memory()
    self.reset_registers()
  def reset_memory(self):
    self.mem = np.zeros(0x80000000, dtype=np.uint8)

  def reset_registers(self):
    # Main CPU registers:
    # -------------------
    # 00h = r0/reg0     08h = t0/reg8     10h = s0/reg16    18h = t8/reg24
    # 01h = at/reg1     09h = t1/reg9     11h = s1/reg17    19h = t9/reg25
    # 02h = v0/reg2     0Ah = t2/reg10    12h = s2/reg18    1Ah = k0/reg26
    # 03h = v1/reg3     0Bh = t3/reg11    13h = s3/reg19    1Bh = k1/reg27
    # 04h = a0/reg4     0Ch = t4/reg12    14h = s4/reg20    1Ch = gp/reg28
    # 05h = a1/reg5     0Dh = t5/reg13    15h = s5/reg21    1Dh = sp/reg29
    # 06h = a2/reg6     0Eh = t6/reg14    16h = s6/reg22    1Eh = s8/reg30
    # 07h = a3/reg7     0Fh = t7/reg15    17h = s7/reg23    1Fh = ra/reg31
    # 
    # COP0 registers:
    # ---------------
    # 00h = Index       08h = BadVAddr    10h = Config      18h = *RESERVED* 
    # 01h = Random      09h = Count       11h = LLAddr      19h = *RESERVED*
    # 02h = EntryLo0    0Ah = EntryHi     12h = WatchLo     1Ah = PErr
    # 03h = EntryLo1    0Bh = Compare     13h = WatchHi     1Bh = CacheErr
    # 04h = Context     0Ch = Status      14h = XContext    1Ch = TagLo
    # 05h = PageMask    0Dh = Cause       15h = *RESERVED*  1Dh = TagHi
    # 06h = Wired       0Eh = EPC         16h = *RESERVED*  1Eh = ErrorEPC
    # 07h = *RESERVED*  0Fh = PRevID      17h = *RESERVED*  1Fh = *RESERVED*


    self.gpr = np.zeros(32, dtype=np.uint32)
    self.cp0 = np.zeros(32, dtype=np.uint64)

  def load_instructions(self, instructions):
    self.ptr -= len(self.instructions)
    self.instructions = instructions

  def add_breakpoints(self, positions):
    self.breakpoints = positions

  def tick(self):
    current_instruction = self.instructions[self.ptr]
    self.ptr += 1

    handle_op(self, current_instruction)

    if current_instruction["position"] in self.breakpoints:
      print(f"Breakpoint at {hex(current_instruction['position'])}")
      self.debug_registers()

      while True:
        k = input("Enter c to continue, d to dump memory, x to cancel")

        if k == 'd':
          self.dump_memory(current_instruction["position"])
        if k == 'c':
          break
        if k == 'x':
          sys.exit(0)

  def dump_memory(self, pos):
    if not os.path.exists(os.path.join("dumps", "mem_dumps")):
      os.makedirs(os.path.join("dumps", "mem_dumps"))

    mem_dump_file = os.path.join("dumps", "mem_dumps", f"dump_{hex(pos)}.bin")
    print(f'dumping to... "dump_{hex(pos)}.bin"')
    self.mem.tofile(mem_dump_file)

  def run(self):
    #if "SM64R" in os.environ and "CPU" in os.environ["SM64R"]:
    #  import curses
    #  curses.wrapper(self.run_debug)
    #  return

    try:
      while self.ptr < len(self.instructions):
        self.tick()

        #print(current_instruction["position"], self.breakpoints)
    except Exception as err:
      print("Emulation failed")
      print("Memory Output")
      print(self.mem)
      raise err
  
  '''
  def run_debug(self, stdscr):
    import curses

    stdscr.clear()
    stdscr.refresh()

    k = None

    curses.start_color()
    #curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    #curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    #curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Loop where k is the last character pressed
    while (k != ord('q')):
      if self.ptr < len(self.instructions):
        # end of cpu
        break
        pass

      # Initialization
      stdscr.clear()
      height, width = stdscr.getmaxyx()

      if k == ord('a'):
        self.tick()

      # Refresh the screen
      stdscr.refresh()

      # Wait for next input
      k = stdscr.getch()
  '''
  
  def debug_registers(self, gpr=None, cp0=None):
    if gpr is None:
      gpr = self.gpr
    if cp0 is None:
      cp0 = self.cp0

    def try_float(value):
      conv_methods = [
        lambda x: struct.unpack('>e', int(value).to_bytes(2, self.rom.endianess, signed=True))[0],
        lambda x: struct.unpack('>f', int(value).to_bytes(4, self.rom.endianess, signed=True))[0],
        lambda x: struct.unpack('>d', int(value).to_bytes(8, self.rom.endianess, signed=True))[0],
      ]

      f = None
      for m in conv_methods:
        try:
          f = m(value)
          
          return str(f)
        except OverflowError:
          continue

      
      if not f:
        return hex(value)

      return f


    cells_per_line = 2
    for i in range(0, 32, cells_per_line):
      indices = list(range(cells_per_line))
      registers = list(map(lambda x: f"R{str(i+x).rjust(2, '0')}: {format_binary(int(gpr[i+x]).to_bytes(8, self.rom.endianess, signed=True)).rjust(32)}", indices))
      print(" ".join(registers))

    for i in range(0, 32, cells_per_line):
      indices = list(range(cells_per_line))
      registers = list(map(lambda x: f"FPR{str(i+x).rjust(2, '0')}: {format_binary(int(cp0[i+x]).to_bytes(8, self.rom.endianess, signed=True)).rjust(32)}", indices))
      print(" ".join(registers))

  # Memory Methods
  def addr_parse(self, addr):
    # Credits for memory map go to contributors to shoutwiki:
    # http://en64.shoutwiki.com/wiki/Memory_map_detailed

    addr_type = None # Description of address region type
    addr_in_memory = None # Position aligned for corresponding memory area
    addr_source = None # Which source should be read

    if addr >= 0x0 and addr < 0x03EFFFFF:
      addr_type = "RDRAM"
      addr_source = self.mem
      addr_in_memory = addr
      #addr_in_memory = addr
      #addr_source = self.mem
    elif addr >= 0x03F00000 and addr < 0x03FFFFFF:
      addr_type = "RDRAM REGISTER"
      #addr_in_memory = addr
      #addr_source = self.mem
    elif addr >= 0x04000000 and addr < 0x0400FFFF:
      addr_type = "SP REGISTERS"
      #addr_in_memory = addr
      #addr_source = self.mem
    elif addr >= 0x04100000 and addr < 0x041FFFFF:
      addr_type = "DP COMMAND REGISTERS"
    elif addr >= 0x04200000 and addr < 0x042FFFFF:
      addr_type = "DP SPAN REGISTERS"
    elif addr >= 0x04300000 and addr < 0x043FFFFF:
      addr_type = "MIPS REGISTERS"
    elif addr >= 0x04400000 and addr < 0x044FFFFF:
      addr_type = "VIDEO INTERFACE REGISTERS"
    elif addr >= 0x04500000 and addr < 0x045FFFFF:
      addr_type = "AUDIO INTERFACE REGISTERS"
    elif addr >= 0x04600000 and addr < 0x046FFFFF:
      addr_type = "PERIPHERAL ACCESS"
    elif addr >= 0x04700000 and addr < 0x047FFFFF:
      addr_type = "RDRAM INTERFACE REGISTERS"
    elif addr >= 0x04800000 and addr < 0x048FFFFF:
      addr_type = "SERIAL INTERFACE REGISTERS"
    elif addr >= 0x04900000 and addr < 0x04FFFFFF:
      addr_type = "UNUSED"
      print("Unlikely access to unused memory, addr parsing error?")
    elif addr >= 0x05000000 and addr < 0x05FFFFFF:
      addr_type = "CARTRIDE DOMAIN 2 ADDR 1" # sram "could be here"?
    elif addr >= 0x06000000 and addr < 0x0FFFFFFF:
      addr_type = "CARTRIDE DOMAIN 1 ADDR 1" # n64ddrive
    elif addr >= 0x10000000 and addr < 0x1719DA4:
      addr_type = "ROM"
      addr_source = self.rom_data
      addr_in_memory = addr - 0x10000000 # maps to start of ROM
    elif addr >= 0x1719DA5 and addr < 0x1FBFFFFF:
      addr_type = "ROM (Unused)"
    elif addr >= 0x1FC00000 and addr < 0x1FC007BF:
      addr_type = "PIF BOOT ROM"
    elif addr >= 0x1FC007C0 and addr < 0x1FC007FF:
      addr_type = "PIF RAM"
    elif addr >= 0x1FC00800 and addr < 0x1FCFFFFF:
      addr_type = "RESERVED"
      print("Unlikely access to reserved memory, addr parsing error?")
    elif addr >= 0x1FD00000 and addr < 0x7FFFFFFF:
      addr_type = "UNKNOWN"
      print("Unlikely access to unknown memory, addr parsing error?")
    elif addr >= 0x80000000 and addr < 0x9FFFFFFF:
      addr_type = "KSEG0 CACHED"
      addr_in_memory = addr - 0x80000000
      addr_source = self.mem
    elif addr >= 0xA0000000 and addr < 0xBFFFFFFF:
      addr_type = "KSEG1 UNCACHED"
      addr_in_memory = addr - 0xA0000000
      addr_source = self.mem
    elif addr >= 0xC0000000 and addr < 0xDFFFFFFF:
      addr_type = "KSEG2 TLB MAPPED"
      addr_in_memory = addr - 0xC0000000
      addr_source = self.mem
    elif addr >= 0xE0000000 and addr < 0xFFFFFFFF:
      addr_type = "KSEG3 TLB MAPPED"
      addr_in_memory = addr - 0xE0000000
      addr_source = self.mem
    else:
      raise Exception("Memory access out of bounds. Memory address parsing error :(")
    
    if addr_source is None:
      print(f"Not accessing {hex(addr)}: {addr_type}")
    else:
      print(f"Memory Access [{addr_type}]: {hex(addr)} -> {hex(addr_in_memory)}")
    
    return (addr_type, addr_in_memory, addr_source)


  # Write
  def mem_write_byte(self, addr, value): # 8 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      mem_source[mem_addr] = value & 0xFF
  
  def mem_write_half_word(self, addr, value): # 16 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(2):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_word(self, addr, value): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(4):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_word_left(self, addr, value): # 16 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(2,4):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_word_right(self, addr, value): # 16 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(2):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_double_word(self, addr, value): # 64 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(8):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_double_word_left(self, addr, value): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(4,8):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))

  def mem_write_double_word_right(self, addr, value): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      for i in range(4):
        mem_source[mem_addr+i] = value & (0xFF << (i*8))
  
  # Read
  def mem_read_byte(self, addr): # 8 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      return int(mem_source[mem_addr])
    return 0

  def mem_read_half_word(self, addr): # 16 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      b = []
      for i in range(2):
        b.append(int(mem_source[mem_addr+i]))

      return int.from_bytes(b, self.rom.endianess)
    return 0

  def mem_read_word(self, addr): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      b = []
      for i in range(4):
        b.append(int(mem_source[mem_addr+i]))

      return int.from_bytes(b, self.rom.endianess)
    return 0

  def mem_read_double_word(self, addr): # 64 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      b = []
      for i in range(8):
        b.append(int(mem_source[mem_addr+i]))

      return int.from_bytes(b, self.rom.endianess)
    return 0

  def mem_read_double_word_Left(self, addr): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      b = []
      for i in range(4, 8):
        b.append(int(mem_source[mem_addr+i]))

      return int.from_bytes(b, self.rom.endianess)
    return 0

  def mem_read_double_word_right(self, addr): # 32 bit
    (addr_type, mem_addr, mem_source) = self.addr_parse(addr)

    if mem_source is not None:
      b = []
      for i in range(4):
        b.append(int(mem_source[mem_addr+i]))

      return int.from_bytes(b, self.rom.endianess)
    return 0