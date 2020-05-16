from sm64r.Randoutils import format_binary

opcode_params = {
  "LB": ["base", "rt", "offset"], # Load Byte (LB rt, offset, base)
  "LBU": ["base", "rt", "offset"], # Load Byte Unsigned (LBU rt, offset, base)
  "LD": ["base", "rt", "offset"], # Load Doubleword
  "LDL": ["base", "rt", "offset"], # Load Doubleword Left
  "LDR": ["base", "rt", "offset"], # Load Doubleword Right
  "LH": ["base", "rt", "offset"], # Load Halfword
  "LHU": ["base", "rt", "offset"], # Load Halfword Unsigned
  "LL": ["base", "rt", "offset"], # Load Linked word
  "LLD": ["base", "rt", "offset"], # Load Linked Doubleword
  "LW": ["base", "rt", "offset"], # Load Word
  "LWL": ["base", "rt", "offset"], # Load Word Left
  "LWR": ["base", "rt", "offset"], # Load Word Right
  "LWU": ["base", "rt", "offset"], # Load Word Unsigned
  "SB": ["base", "rt", "offset"], # Store Byte
  "SC": ["base", "rt", "offset"], # Store Conditional word
  "SCD": ["base", "rt", "offset"], # Store Conditional Doubleword
  "SD": ["base", "rt", "offset"], # Store Doubleword
  "SDL": ["base", "rt", "offset"], # Store Doubleword Left
  "SDR": ["base", "rt", "offset"], # Store Doubleword Right
  "SH": ["base", "rt", "offset"], # Store Halfword
  "SW": ["base", "rt", "offset"], # Store Word
  "SWL": ["base", "rt", "offset"], # Store Word Left
  "SWR": ["base", "rt", "offset"], # Store Word Right
  "SYNC": [], # SYNChronize shared memory
  "ADD": ["rs", "rt", "rd"], # ADD word
  "ADDI": ["rs", "rt", "imm"], # ADD Immediate word
  "ADDIU": ["rs", "rt", "imm"], # Add Immediate Unsigned word
  "ADDU": ["rs", "rt", "rd"], # Add Unsigned word
  "AND": ["rs", "rt", "rd"], # AND
  "ANDI": ["rs", "rt", "imm"], # AND Immediate
  "DADD": ["rs", "rt", "rd"], # Doubleword ADD
  "DADDI": ["rs", "rt", "imm"], # Doubleword ADD Immediate
  "DADDIU": ["rs", "rt", "imm"], # Doubleword ADD Immediate Unsigned
  "DADDU": ["rs", "rt", "rd"], # Doubleword ADD Unsigned
  "DDIV": ["rs", "rt"], # Doubleword DIVide
  "DDIVU": ["rs", "rt"], # Doubleword DIVide Unsigned
  "DIV": ["rs", "rt"], # DIVide word
  "DIVU": ["rs", "rt"], # DIVide Unsigned word
  "DMULT": ["rs", "rt"], # Doubleword MULTiply
  "DMULTU": ["rs", "rt"], # Doubleword MULTiply Unsigned
  "DSLL": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Left Logical
  "DSLL32": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Left Logical +32
  "DSLLV": ["rs", "rt", "rd", "pad5"], # Doubleword Shift Left Logical Variable
  "DSRA": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Right Arithmetic
  "DSRA32": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Right Arithmetic +32
  "DSRAV": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Right Arithmetic Variable
  "DSRL": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Right Logical
  "DSRL32": ["pad5", "rt", "rd", "sa"], # Doubleword Shift Right Logical +32
  "DSRLV": ["pad5", "rt", "rd", "rs"], # Doubleword Shift Right Logical Variable
  "DSUB": ["rs", "rt", "rd"], # Doubleword SUBtract
  "DSUBU": ["rs", "rt", "rd"], # Doubleword SUBtract Unsigned
  "LUI": ["pad5", "rt", "imm"], # Load Upper Immediate
  "MFHI": ["pad10", "rd"], # Move From HI register
  "MFLO": ["pad10", "rd"], # Move From LO register
  "MTHI": ["rs", "pad15"], # Move To HI register
  "MTLO": ["rs", "pad15"], # Move To LO register
  "MULT": ["rs", "rt"], # MULTiply word
  "MULTU": ["rs", "rt"], # MULTiply Unsigned word
  "NOR": ["rs", "rt", "rd"], # Not OR
  "OR": ["rs", "rt", "rd"], # OR
  "ORI": ["rs", "rt", "imm"], # OR Immediate
  "SLL": ["pad5", "rt", "rd"], # Shift word Left Logical
  "SLLV": ["rs", "rt", "rd"], # Shift word Left Logical Variable
  "SLT": ["rs", "rt", "rd"], # Set on Less Than
  "SLTI": ["rs", "rt", "imm"], # Set on Less Than Immediate
  "SLTIU": ["rs", "rt", "imm"], # Set on Less Than Immediate Unsigned
  "SLTU": ["rs", "rt", "rd"], # Set on Less Than Unsigned
  "SRA": ["pad5", "rt", "rd", "sa"], # Shift word Right Arithmetic
  "SRAV": ["rs", "rt", "rd"], # Shift word Right Arithmetic Variable
  "SRL": ["pad5", "rt", "rd", "sa"], # Shift word Right Logical
  "SRLV": ["rs", "rt", "rd"], # Shift word Right Logical Variable
  "SUB": ["rs", "rt", "rd"], # SUBtract word
  "SUBU": ["rs", "rt", "rd"], # SUBtract Unsigned word
  "XOR": ["rs", "rt", "rd"], # eXclusive OR
  "XORI": ["rs", "rt", "imm"], # eXclusive OR Immediate
  "BEQ": ["rs", "rt", "offset"], # Branch on =
  "BEQL": ["rs", "rt", "offset"], # Branch on EQual Likely
  "BGEZ": ["rs", "pad5", "offset"], # Branch on >= Zero
  "BGEZAL": ["rs", "pad5", "offset"], # Branch on >= Zero And Link
  "BGEZALL": ["rs", "pad5", "offset"], # Branch on >= Zero And Link Likely
  "BGEZL": ["rs", "pad5", "offset"], # Branch on >= Equal to Zero Likely
  "BGTZ": ["rs", "pad5", "offset"], # Branch on > Zero
  "BGTZL": ["rs", "pad5", "offset"], # Branch on > Zero Likely
  "BLEZ": ["rs", "pad5", "offset"], # Branch on <= Equal to Zero
  "BLEZL": ["rs", "pad5", "offset"], # Branch on <= Zero Likely
  "BLTZ": ["rs","pad5",  "offset"], # Branch on < Zero
  "BLTZAL": ["rs", "pad5", "offset"], # Branch on < Zero And Link
  "BLTZALL": ["rs", "pad5", "offset"], # Branch on < Zero And Link Likely
  "BLTZL": ["rs", "pad5", "offset"], # Branch on < Zero Likely
  "BNE": ["rs", "rt", "offset"], # Branch on <>
  "BNEL": ["rs", "rt", "offset"], # Branch on <> Likely
  "J": ["target"], # Jump
  "JAL": ["target"], # Jump And Link (return address in ra)
  "JALR": ["rs", "rd"], # Jump And Link Register (return address in rd)
  "JR": ["rs"], # Jump Register
  "BREAK": ["offset"], # BREAKpoint
  "SYSCALL": ["offset"], # SYStem CALL
  "TEQ": ["rs", "rt"], # Trap if =
  "TEQI": ["rs", "pad5", "imm"], # Trap if = Immediate
  "TGE": ["rs", "rt"], # Trap if >=
  "TGEI": ["rs", "pad5", "imm"], # Trap if >= Immediate
  "TGEIU": ["rs", "pad5", "imm"], # Trap if >= Immediate Unsigned
  "TGEU": ["rs", "rt"], # Trap if >= Unsigned
  "TLT": ["rs", "rt"], # Trap if <
  "TLTI": ["rs", "pad5", "imm"], # Trap if < Immediate
  "TLTIU": ["rs", "pad5", "imm"], # Trap if < Immediate Unsigned
  "TLTU": ["rs", "rt"], # Trap if < Unsigned
  "TNE": ["rs", "rt"], # Trap if <>
  "TNEI": ["rs", "pad5", "imm"], # Trap if <> Immediate
  "CACHE": ["base", "op", "offset"], # CACHE
  "ERET": ["pad1", "bits_19"], # undefined
  "MFC0": ["pad5", "rt", "fs"], # Move Word From CP0
  "MTC0": ["pad5", "rt", "fs"], # Move Word To CP0
  "TLBP": ["pad1", "bits_19"], # ["Probe TLB for Matching Entry"], # undefined
  "TLBR": ["pad1", "bits_19"], # ["Read Indexed TLB Entry"], # undefined
  "TLBWI": ["pad1", "bits_19"], # ["Write Indexed TLB Entry"], # undefined
  "TLBWR": ["pad1", "bits_19"], # ["Write Random TLB Entry"], # undefined
  "BC1F": ["offset"], # Branch on FP False
  "BC1FL": ["offset"], # Branch on FP False Likely
  "BC1T": ["offset"], # Branch on FP True
  "BC1TL": ["offset"], # Branch on FP True Likely
  "CFC1": ["pad5", "rt", "fs"], # Move control word From Floating-Point
  "CTC1": ["pad5", "rt", "fs"], # Move control word To Floating-Point
  "DMFC1": ["pad5", "rt", "fs"], # Doubleword Move From Floating-Point
  "DMTC1": ["pad5", "rt", "fs"], # Doubleword Move To Floating-Point
  "LDC1": ["base", "ft", "offset"], # Load Doubleword to Floating-Point
  "LWC1": ["base", "ft", "offset"], # Load Word to Floating-Point
  "MFC1": ["pad5", "rt", "fs"], # Move Word From Floating-Point
  "MTC1": ["pad5", "rt", "fs"], # Move Word To Floating-Point
  "SDC1": ["base", "ft", "offset"], # Store Doubleword from Floating-Point
  "SWC1": ["base", "offset"], # Store Word from Floating-Point
  "NOP": [], # Assembles to SLL => # r0, r0, 0
  "MOVE": ["rd", "rs"], # Assembles to ADD
  "NEG": ["rd", "rt"], # Assembles to SUB
  "NEGU": ["rd", "rs"], # Assembles to SUBU
  "BNEZ": ["rs", "offset"], # Assembles to BNE
  "BNEZL": ["rs", "offset"], # Assembles to BNEL
  "BEQZ": ["rs", "offset"], # Assembles to BEQ
  "BEQZL": ["rs", "offset"], # Assembles to BEQL
  "B": ["offset"], # Assembles to BEQ
  "BAL": ["offset"], # Assembles to BGEZAL r0, offset
  "LI": ["rt", "imm"], # Assembles to ORI
  "ABS.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ABSolute value
  "ADD.fmt": ["fmt", "ft", "fs", "fd"], # floating-point ADD
  "CVT.D.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ConVerT to Double floating-point
  "CVT.L.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ConVerT to Long fixed-point
  "CVT.S.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ConVerT to Single floating-point
  "CVT.W.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ConVerT to Word fixed-point
  "FLOOR.L.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point FLOOR convert to Long fixed-point
  "FLOOR.W.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point FLOOR convert to Word fixed-point
  "CEIL.L.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point CEILing convert to Long fixed-point
  "CEIL.W.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point CEILing convert to Word fixed-point
  "MOV.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point MOVe
  "MUL.fmt": ["fmt", "ft", "fs", "fd"], # floating-point MULtiply
  "NEG.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point NEGate
  "DIV.fmt": ["fmt", "ft", "fs", "fd"], # floating-point DIVide
  "C.cond.fmt": ["fmt", "ft", "fs"], # floating-point floating point Compare
  "ROUND.L.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ROUND to Long fixed-point
  "ROUND.W.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point ROUND to Word fixed-point
  "TRUNC.L.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point TRUNCate to Long fixed-point
  "TRUNC.W.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point TRUNCate to Word fixed-point
  "SQRT.fmt": ["fmt", "pad5", "fs", "fd"], # floating-point SQuare RooT
  "SUB.fmt": ["fmt", "ft", "fs", "fd"], # floating-point SUBtract
}

### Start Pseudo Opcodes
# These would need to be implemented in order to compile from source
# but because we're only disassembling, we'll remove them for now
#"LI": ["or ADDIU"], # rt, r0, imm
#"LI": ["or LUI"], # rt, high_16
#"LI": ["ORI"], # rt, rt, low_16 (if imm is 32 bit)
#"S.S": ["ft"], # offset Assembles to SWC1 =>  ft, offset
#"L.S": ["ft"] # offset Assembles to LWC1 => ft, offset

# rs 5 bit - register specifier
# rt 5 bit - register target
# rd 5 bit - destination register specifier
# sa 5 bit - shift amount
# fs 5 bit - floating point source register specifier 
# ft 5 bit - floating point target (source/destination)
# fd 5 bit - floating point destination register specifier
# base 5 bit - value
# imm 16 bit - immediate value
# offset 16 bit - branch displacement or address displacement
# target 26 bit - jump target instruction index ( * 4 = address)

opcode_tbl = [
  ["SPECIAL", "REGIMM", "J", "JAL", "BEQ", "BNE", "BLEZ", "BGTZ"],
  ["ADDI", "ADDIU", "SLTI", "SLTIU", "ANDI", "ORI", "XORI", "LUI"],
  ["COP0", "COP1", "---", "---", "BEQL", "BNEL", "BLEZL", "BGTZL"],
  ["DADDI", "DADDIU", "LDL", "LDR", "---", "---", "---", "---"],
  ["LB", "LH", "LWL", "LW", "LBU", "LHU", "LWR", "LWU"],
  ["SB", "SH", "SWL", "SW", "SDL", "SDR", "SWR", "CACHE"],
  ["LL", "LWC1", "LWC2", "PREF", "LLD", "LDC1", "LDC2", "LD"],
  ["SC", "SWC1", "SWC2", "---", "SCD", "SDC1", "SDC2", "SD"]
]

opcode_tbl_func = [
  ["NOP", "---", "SRL", "SRA", "SLLV", "---", "SRLV", "SRAV"],
  ["JR", "JALR", "---", "---", "SYSCALL", "BREAK", "---", "SYNC"],
  ["MFHI", "MTHI", "MFLO", "MTLO", "DSLLV", "---", "DSRLV", "DSRAV"],
  ["MULT", "MULTU", "DIV", "DIVU", "DMULT", "DMULTU", "DDIV", "DDIVU"],
  ["ADD", "ADDU", "SUB", "SUBU", "AND", "OR", "XOR", "NOR"],
  ["---", "---", "SLT", "SLTU", "DADD", "DADDU", "DSUB", "DSUBU"],
  ["TGE", "TGEU", "TLT", "TLTU", "TEQ", "---", "TNE", "---"],
  ["DSL", "---", "DSLR", "DSRA", "DSLL32", "---", "DSRL32", "DSRA32"]
]

opcode_tbl_cop0 = [
  ["MFC0", "---", "---", "---", "MTC0", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["TLB", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
]

opcode_tbl_cop1 = [
  ["MFC1", "DMFC1", "CFC1", "---", "MTC1", "DMTC1", "CTC1"],
  ["BC1", "---", "---", "---", "---", "---", "---", "----"],
  ["S_FPU", "D_FPU", "---", "---", "W_FPU", "L_FPU", "---", "----"],
  ["---", "---", "---", "---", "---", "---", "---", "----"],
]

opcode_tbl_tlb = [
  ["---", "TLBR", "TLBWI", "---", "---", "---", "TLBWR", "---"],
  ["TLBP", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["ERET", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
]

opcode_tbl_regimm = [
  ["BLTZ", "BGEZ", "BLTZL", "BGEZL", "---", "---", "---", "---"],
  ["TGEI", "TGEIU", "TLTI", "TLTIU", "TEQI", "---", "TENEI", "---"],
  ["BLTZAL", "BGEZAL", "BLTZALL", "BGEZALL", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"]
]

opcode_tbl_bc1 = [
  ["BC1F", "BC1T"],
  ["BC1FL", "BC1TL"]
]

opcode_tbl_s_fpu = [ # single float
  ["ADD.S", "SUB.S", "MUL.S", "DIV.S", "SQRT.S", "ABS.S", "MOV.S", "NEG.S"],
  ["ROUND.L.S", "TRUNC.L.S", "CEIL.L.S", "FLOOR.L.S", "ROUND.W.S", "TRUNC.W.S", "CEIL.W.S", "FLOOR.W.S"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "CVT.D.S", "---", "---", "CVT.W.S", "CVT.L.S", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["C.F.S", "C.UN.S", "C.EQ.S", "C.UEQ.S", "C.OLT.S", "C.ULT.S", "C.OLE.S", "C.ULE.S"],
  ["C.SF.S", "C.NGLE.S", "C.SEQ.S", "C.NGL.S", "C.LT.S", "C.NGE.S", "C.LE.S", "C.NGT.S"]
]

opcode_tbl_d_fpu = [ # double float
  ["ADD.D", "SUB.D", "MUL.D", "DIV.D", "SQRT.D", "ABS.D", "MOV.D", "NEG.D"],
  ["ROUND.L.D", "TRUNC.L.D", "CEIL.L.D", "FLOOR.L.D", "ROUND.W.D", "TRUNC.W.D", "CEIL.W.D", "FLOOR.W.D"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["CVT.S.D", "---", "---", "---", "CVT.W.D", "CVT.L.D", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["C.F.D", "C.UN.D", "C.EQ.D", "C.UEQ.D", "C.OLT.D", "C.ULT.D", "C.OLE.D", "C.ULE.D"],
  ["C.DF.D", "C.NGLE.D", "C.DEQ.D", "C.NGL.D", "C.LT.D", "C.NGE.D", "C.LE.D", "C.NGT.D"]
]

opcode_tbl_w_fpu = [ # word fixed point
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["CVT.S.W", "CVT.D.W", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
]

opcode_tbl_l_fpu = [ # long fixed point
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["CVT.S.L", "CVT.D.L", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
  ["---", "---", "---", "---", "---", "---", "---", "---"],
]

registers = [
  'R0',
  'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9',
  'S0', 'S1', 'S2', 'S3', 'S4' 'S5', 'S6', 'S7',
  'A0', 'A1', 'A2', 'A3',
  'RA',
  'V0', 'V1',
  'SP',
  'AT'
]

param_sizes = {
  "rs": 5,
  "rt": 5,
  "rd": 5,
  "sa": 5,
  "fs": 5,
  "ft": 5,
  "fd": 5,
  "op": 5,
  "base": 5,
  "imm": 16,
  "offset": 16,
  "target": 26,
  "fmt": 5,
}

fpu_tables = dict(
  S = opcode_tbl_s_fpu,
  D = opcode_tbl_d_fpu,
  W = opcode_tbl_w_fpu,
  L = opcode_tbl_l_fpu
)

ASM_COPY_OFFSET = 0x80246000

class AssemblerParser:
  def __init__(self, rom):
    self.rom = rom
    self.parsed_instructions = []
  
  def set_cursor_with_instruction_offset(self, pos, num_instructions):
    self.set_cursor(pos + (num_instructions * 4))

  def set_cursor(self, pos):
    self.cursor = pos

  def extract_param_from_instruction(self, instruction, pos, length, debug=False):
    instruction_int = int.from_bytes(instruction, self.rom.endianess)

    p_mask = pow(2, length) - 1
    
    """
    # 0000 0000 1011 0000
    #        ^-----^ desired bits 
    #  
    # - Create mask with length of param, i.e. 0x111111
    # - Shift mask over desired bits by 32 - pos, pos is left aligned, AND result
    #
    # 0000 0000 1011 0000 < instruction
    # 0000 0011 1111 0000 < shifted cpoy mask
    # 0000 0000 1011 0000 < copy mask AND'd
    # 0000 0000 0000 1011 < shifted back
    #             ^-----^ value
    """
    shift_left = max(0, (32 - length - pos))
    shift_right = max(0, (32 - length - pos))

    if debug:
      pass
      # complete instruction set
      #print(length, bin(p_mask)[2:].rjust(4 * 8, '0'))
      #print(bin(instruction_int)[2:].rjust(4 * 8, '0'))
      # copy-mask
      #print(bin(p_mask)[2:].rjust(4 * 8, '0'))
      # copy mask shifted
      #print(bin(p_mask << shift_left)[2:].rjust(4 * 8, '0'))
      # copy mask shifted back
      #print(bin((p_mask << shift_left) >> shift_right)[2:].rjust(4 * 8, '0'))
      # complete instruction set AND shifted copy mask
      #print(bin((instruction_int & p_mask << shift_left) >> shift_right)[2:].rjust(4 * 8, '0'))
      #print("shifting left", shift_left)
      #print("shifting right", shift_right)
      #print("-" * 10)
    
    data = (instruction_int & p_mask << shift_left) >> shift_right
    return data

  def find_instruction_for_ram_addr(self, addr):
    ram_to_rom = addr - ASM_COPY_OFFSET
    offset_to_instruction_index = int(ram_to_rom / 4) # 4 bytes per instruction
    
    return self.parsed_instructions[offset_to_instruction_index]

  def parse_params(self, opcode, instruction):
    if opcode.endswith('.S') or opcode.endswith('.D') or opcode.endswith('.W') or opcode.endswith('.L'):
      # all FPU opcodes have same signature, they're only defined once with ".fmt"
      #print(opcode, " as ", opcode[:-2] + ".fmt")
      opcode = opcode[:-2] + ".fmt"

    if opcode.startswith("C."):
      # all FPU conditional opcodes have same signature, they're only defined once with "C.cond.fmt"
      #print(opcode, " as ", "C.cond.fmt")
      opcode = "C.cond.fmt"


    if opcode not in opcode_params:
      print(f'Invalid param parse at {hex(self.cursor)} no param definition for opcode {opcode} - {format_binary(instruction)}')
      return

    bit_read_pos = 6
    
    #print(opcode_params[opcode])
    changed_registers = dict()
    for param in opcode_params[opcode]:
      #print(f"reading {opcode}: {param} at index {bit_read_pos}")
      save = True
      param_length = 0

      if param.startswith("pad"):
        param_move_cursor = int(param[3:])
        save = False
        bit_read_pos += param_move_cursor
      elif param.startswith("bits_"):
        bit_read_pos += param_length
      elif param in param_sizes.keys():
        param_length = param_sizes[param]
      else:
        print('unknown param size key', param)
      #print(f"new cursor pos {bit_read_pos} (added {param_length})")

      if param_length > 0 and save:
        changed_registers[param] = self.extract_param_from_instruction(instruction, bit_read_pos, param_length)
      bit_read_pos += param_length
      
    return changed_registers
  
  def parse_until(self, end):
    ptr = min(self.cursor -4, end)
    stop = max(self.cursor -4, end)
    print("parsing at", ptr)
    while ptr < stop:
      ptr += 4
      self.cursor = ptr

      instruction = self.rom.read_bytes(self.cursor, 4)

      opcode_a = (instruction[0] & 0xE0) >> 5 # 0 .. 2
      opcode_b = ((instruction[0] & 0x1C) << 3) >> 5 # 3 .. 5
      
      if opcode_a > 7 or opcode_b > 7:
        print(f'Instruction at {hex(self.cursor)} invalid opcode - {format_binary(instruction)}')
        continue
      
      opcode = opcode_tbl[opcode_a][opcode_b]
        
      if opcode == 'SPECIAL':
        func_opcode_hi = self.extract_param_from_instruction(instruction, 29, 3)
        func_opcode_lo = self.extract_param_from_instruction(instruction, 26, 3)
        opcode = opcode_tbl_func[func_opcode_lo][func_opcode_hi]

      if opcode == "REGIMM": # param encoded in rt
         # bits 20...16
        regimm_opcode_lo = self.extract_param_from_instruction(instruction, 16, 2)
        regimm_opcode_hi = self.extract_param_from_instruction(instruction, 12, 3)
        #print(opcode)
        #print(bin(regimm_opcode_lo))
        #print(bin(regimm_opcode_hi))
        opcode = opcode_tbl_regimm[regimm_opcode_hi][regimm_opcode_lo]
      
      if opcode == "COP0": # param encoded in fmt
        cop0_opcode_hi = self.extract_param_from_instruction(instruction, 8, 3)
        cop0_opcode_lo = self.extract_param_from_instruction(instruction, 6, 2)
        
        opcode = opcode_tbl_cop0[cop0_opcode_lo][cop0_opcode_hi]

      if opcode == "COP1": # param encoded in fmt
        cop1_opcode_hi = self.extract_param_from_instruction(instruction, 8, 3)
        cop1_opcode_lo = self.extract_param_from_instruction(instruction, 6, 2)
        #print(opcode)
        #print(bin(int.from_bytes(instruction, self.rom.endianess))[2:].rjust(4*8, '0'))
        #print(bin(cop1_opcode_lo))
        #print(bin(cop1_opcode_hi))
        opcode = opcode_tbl_cop1[cop1_opcode_lo][cop1_opcode_hi]
      
      if opcode == "BC1": # param encoded in nd and tf
        bc1_opcode_hi = self.extract_param_from_instruction(instruction, 16, 1)
        bc1_opcode_lo = self.extract_param_from_instruction(instruction, 15, 1)
        #print(opcode)
        #print(bin(int.from_bytes(instruction, self.rom.endianess))[2:].rjust(4*8, '0'))
        #print(bin(bc1_opcode_lo))
        #print(bin(bc1_opcode_hi))
        opcode = opcode_tbl_bc1[bc1_opcode_lo][bc1_opcode_hi]
      
      if opcode.endswith("_FPU"):
        fpu_type = opcode[0]
        
        fpu_table = fpu_tables[fpu_type]
        func_opcode_hi = self.extract_param_from_instruction(instruction, 29, 3)
        func_opcode_lo = self.extract_param_from_instruction(instruction, 26, 3)
        
        #print(opcode)
        #print(bin(int.from_bytes(instruction, self.rom.endianess))[2:].rjust(4*8, '0'))
        #print(bin(func_opcode_hi))
        #print(bin(func_opcode_lo))
        
        opcode = fpu_table[func_opcode_lo][func_opcode_hi]
        #print(hex(self.cursor), opcode, "<------------")
      
      if opcode == "TLB":
        func_opcode_hi = self.extract_param_from_instruction(instruction, 29, 3)
        func_opcode_lo = self.extract_param_from_instruction(instruction, 26, 3)
        opcode = opcode_tbl_tlb[func_opcode_lo][func_opcode_hi]


      #print(opcode)
      params = self.parse_params(opcode, instruction)
      #print(hex(self.cursor).ljust(10, ' '), opcode.rjust(10, ' '), params)
      self.parsed_instructions.append(
        dict(
          position=self.cursor,
          opcode=opcode,
          instruction=instruction,
          params=params,
        )
      )
    return self.parsed_instructions

'''
      last_data = None
      odd_even_counter = 0
      register_values = {}
      for i in range(40): # go back this many opcode instructions
        cursor = int(star_create_call - (i * 4))
        inst = raw_bhv[cursor:cursor+4]

        opcode_a = ((inst[0] & 0xE0) >> 5) # 0..3 first 3 bits
        opcode_b = ((inst[0] & 0x1C) << 3) >> 5 # 3..6 3 bits after

        if opcode_b > 7 or opcode_a > 7:
          print('invalid function opcode - out of range')
          continue

        register = ((inst[0] & 0xF8) >> 3)
        data = (inst[1:3])

        if register > len(registers):
          print('invalid register - out of range:', hex(register))
          continue

        register_str = registers[register]
        #print('A', format_bits(opcode_a))
        #print('B', format_bits(opcode_b))
        #print(format_binary(inst))
        #print(opcode_a)
        #print(opcode_b)

        opcode_str = opcode_tbl[opcode_a][opcode_b]
        if opcode_a == 0 and opcode_b == 0:
          #print("SPECIAL!")
          #print(format_bits(inst[3]))
          func_opcode_a = (inst[3] & 0x7)
          func_opcode_b = (inst[3] & 0x38)
          #print(func_opcode_a, func_opcode_b)

          if func_opcode_b > 7 or func_opcode_a > 7:
            print('invalid function opcode - out of range')
            continue
          opcode_str = opcode_tbl_func[func_opcode_a][func_opcode_b]

        if opcode_str == 'LUI':
          register_values[register_str] = data
        if opcode_str == 'ORI'
          register_values[register_str] = data
        #print(hex(cursor + behaviour_locations[0][0]), opcode_str, register_str, format_binary(inst))
      print('-' * 40)
      #break
      '''