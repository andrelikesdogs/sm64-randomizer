from operator import itemgetter
from sm64r.Randoutils import format_binary
import struct

offset_mem = 0x80000000

def bin_padded(num, length):
  return bin(num)[2:].rjust(length, '0')

def sign_extend(address, bits):
    sign_bit = 1 << (bits - 1)
    return abs((address & (sign_bit - 1)) - (address & sign_bit))

def algn_mem(addr):
  return addr - offset_mem

def get_mem_from_base_and_offset(emu, base, offset):
  #print("sign extending", offset)
  #print(bin_padded(offset, 32))
  #print(bin_padded(sign_extend(offset, 32), 32))
  #print("offset, shifted and extended:")

  # Example Debug
  #  0x1000     LUI          {'rt': 8, 'imm': 32820} hex(0x8034) => shifted => 0x80340000
  #  0x1008     ADDIU        {'rs': 8, 'rt': 8, 'imm': 42368} hex(0xA580) => sign extended
  #  0x1014     SW           {'base': 8, 'rt': 0, 'offset': 0}



  #print(f"binary register entry for {base}:", bin(emu.gpr[base])[2:].rjust(32, '0'))
  #print("before shift", hex(emu.gpr[base]))
  #print("before offset extend", hex(offset))
  base_shifted = emu.gpr[base]
  offset_extend = sign_extend(offset, 16)
  #print("addr shifted", hex(base_shifted))
  #print("offset sign extended", hex(offset_extend))

  addr = base_shifted + offset_extend
  #addr = ((emu.gpr[base] << 16) | )
  #print(bin(addr)[2:].rjust(32, '0'), hex(addr), addr)
  #print("offset", bin(sign_extend(offset, 16)))
  #print("hex addr minus offset", hex(offset_mem - addr), offset_mem - addr)
  return addr

get_rt = itemgetter('rt')
get_rs = itemgetter('rs')
get_rd = itemgetter('rd')
get_base = itemgetter('base')
get_offset = itemgetter('offset')
get_imm = itemgetter('imm')
get_ft = itemgetter('ft')
get_fs = itemgetter('fs')
get_fd = itemgetter('fd')

def LB(self, params):
  """ Load Byte
  # Load a byte from memory as a signed value
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_byte(mem_address)
  self.gpr[rt] = value

def LBU(self, params):
  """ Load Byte Unsigned
  # Load a byte from memory as an unsigned value
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_byte(mem_address)
  self.gpr[rt] = value

def LD(self, params):
  """ Load Doubleword
  # Load a doubleword (8 bytes) from memory
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_double_word(mem_address)
  self.gpr[rt] = value

def LDL(self, params):
  """ Load Doubleword Left
  # Load most-siginificant part of a doubleword form an unaligned memory address
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_double_word_left(mem_address)
  self.gpr[rt] = value

def LDR(self, params):
  """ Load Doubleword right
  # Load least-siginificant part of a doubleword form an unaligned memory address
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_double_word_right(mem_address)
  self.gpr[rt] = value

def LHU(self, params):
  """ Load half-word unsigned
  # Load a halfword from memory as an unsigned value
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_half_word(mem_address)
  self.gpr[rt] = value

def LH(self, params):
  """ Load half-word unsigned
  # Load a halfword from memory as an unsigned value
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_half_word(mem_address)
  self.gpr[rt] = value

def LW(self, params):
  """ Load Word
  # Load a word from memory as a signed value
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_word(mem_address)
  self.gpr[rt] = value

def SB(self, params):
  """ Store Byte
  # Stores a byte from register to memory
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_byte(mem_address, self.gpr[rt])

def SH(self, params):
  """ Store Half-Word
  # Stores a half-word from register to memory
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_half_word(mem_address, self.gpr[rt])

def SD(self, params):
  """ Store Double-Word
  # Stores double word (64 bit) from register to memory
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_double_word(mem_address, self.gpr[rt])

def SW(self, params):
  """ Store Word
  # Stores a value from register to memory
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_word(mem_address, self.gpr[rt])

def SWL(self, params):
  """ Store Word
  # Store the most-significant part of a word to an unaligned memory address
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_word_left(mem_address, self.gpr[rt])

def SWR(self, params):
  """ Store Word
  # Store the least-significant part of a word to an unaligned memory address
  """
  rt = get_rt(params)
  base = get_base(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  mem_address = get_mem_from_base_and_offset(self, base, offset)
  self.mem_write_word_right(mem_address, self.gpr[rt])

def LUI(self, params):
  """ Load Upper Immediate
  # Load a constant into upper half of a word
  """
  rt = get_rt(params)
  imm = get_imm(params)

  #print(f"gpr[{rt}] = {bin(self.gpr[rt])[2:].rjust(32, '0')}")
  #print(f"imm = {bin(imm)[2:].rjust(32, '0')}")
  #print(f"gpr[{rt}] = {bin(imm << 16)[2:].rjust(32, '0')}")
  #print("storing", hex(abs(imm << 16)))
  self.gpr[rt] = abs(imm << 16)

def ORI(self, params):
  """ OR Immediate
  # Bitwise logical OR with a constant
  """
  rt = get_rt(params)
  rs = get_rs(params)
  imm = get_imm(params)

  #print(f"gpr[{rs}] = {bin(self.gpr[rs])[2:].rjust(32, '0')}")
  #print(f"imm = {bin(imm)[2:].rjust(32, '0')}")
  #print(f"gpr[{rt}] = {bin(self.gpr[rs] | imm)[2:].rjust(32, '0')}")
  self.gpr[rt] = self.gpr[rs] | imm

def LWC1(self, params):
  """ Load Word to Floating-Point
  # Loads a word from memory into a floating point register
  """
  base = get_base(params)
  ft = get_ft(params)
  offset = get_offset(params)

  mem_address = get_mem_from_base_and_offset(self, base, offset)

  value = self.mem_read_word(mem_address)
  self.cp0[ft] = value

def MTC1(self, params):
  """ Load a Word to Floating Point
  # Copies a word from GPR to FPU general register
  """
  rt = get_rt(params)
  fs = get_fs(params)

  self.cp0[fs] = self.gpr[rt]

def ADDIU(self, params):
  """ Add Immediate Unsigned word
  # Adds a constant to a 32-bit integer
  """
  rt = get_rt(params)
  rs = get_rs(params)
  imm = get_imm(params)

  self.gpr[rt] = self.gpr[rs] + imm

def ADDI(self, params):
  """ Add Immediate signed word
  # Adds a constant to a 32-bit integer
  """
  rt = get_rt(params)
  rs = get_rs(params)
  imm = get_imm(params)

  self.gpr[rt] = self.gpr[rs] + sign_extend(imm, 32)

def ADDU(self, params):
  """ Add unsigned word
  # Adds another register to register
  """
  rt = get_rt(params)
  rs = get_rs(params)
  rd = get_rd(params)

  self.gpr[rd] = self.gpr[rs] + self.gpr[rt]

def OR(self, params):
  """ Logical OR
  # Does a bitwise logical OR on rs | rt
  """
  rs = get_rs(params)
  rt = get_rt(params)
  rd = get_rd(params)

  #print(f"rs = {bin(rs)[2:].rjust(32, '0')}")
  #print(f"rt = {bin(rt)[2:].rjust(32, '0')}")
  #print(f"gpr[{rd}] = {bin(rs | rt)[2:].rjust(32, '0')}")
  self.gpr[rd] = rs | rt

def ANDI(self, params):
  """ Add Immediate signed word
  # Adds a constant to a 32-bit integer
  """
  rt = get_rt(params)
  rs = get_rs(params)
  imm = get_imm(params)

  self.gpr[rt] = self.gpr[rs] | imm

def MFC1(self, params):
  """ Move Word from Floating Point to General Purpose
  # Copies a word from FPU to GPR
  """
  rt = get_rt(params)
  fs = get_fs(params)

  self.gpr[rt] = self.cp0[fs]

def CVT_S_W(self, params):
  """ Convert to Single from Word
  # Convert from Floating Point or fixed point to Single Floating Point (32 bit)
  """
  fs = get_fs(params)
  fd = get_fd(params)

  value = float(self.cp0[fs])
  self.cp0[fd] = int.from_bytes(struct.pack('>f', value), self.rom.endianess, signed=True)

def CVT_S_D(self, params):
  """ Convert to Single from Word
  # Convert from Floating Point or fixed point to Single Floating Point (32 bit)
  """
  fs = get_fs(params)
  fd = get_fd(params)

  value = float(self.cp0[fs])
  self.cp0[fd] = int.from_bytes(struct.pack('>f', value), self.rom.endianess, signed=True)

def CVT_S_L(self, params):
  """ Convert to Single from Word
  # Convert from Floating Point or fixed point to Single Floating Point (32 bit)
  """
  fs = get_fs(params)
  fd = get_fd(params)

  value = float(self.cp0[fs])
  self.cp0[fd] = int.from_bytes(struct.pack('>f', value), self.rom.endianess, signed=True)

def ADD_S(self, params):
  """ Add Single-Precision Floating Point
  # Add cp0 register to another cp0 register with double floating point values 
  """
  ft = get_ft(params)
  fs = get_fs(params)
  fd = get_fd(params)

  self.cp0[fd] = fs + ft

def ADD_D(self, params):
  """ Add Double-Precision Floating Point
  # Add cp0 register to another cp0 register with double floating point values 
  """
  ft = get_ft(params)
  fs = get_fs(params)
  fd = get_fd(params)

  self.cp0[fd] = fs + ft

available_ops = globals()
def handle_op(self, instruction):
  safe_opcode = instruction["opcode"].replace(".", "_")

  opcode_has_handler = safe_opcode in available_ops
  
  params_in_hex = {}

  for (param, value) in instruction["params"].items():
    params_in_hex[param] = hex(value)

  print('\033[92m' if opcode_has_handler else '\033[93m', hex(instruction["position"]).ljust(10, ' '), instruction["opcode"].ljust(12, ' '), params_in_hex, '\033[0m')
  if opcode_has_handler:
    #print(params)
    available_ops[safe_opcode](self, instruction["params"])