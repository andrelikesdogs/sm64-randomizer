// ******** Cmd 00: Load and Jump ******** //
.macro .ls_00, seg, romStart, romEnd, segJump
	.byte 0x00, 0x10, 0x00, seg
	.word romStart, romEnd, segJump
.endmacro
.macro .ls_loadAndJump, seg, romStart, romEnd, segJump
	.ls_00 seg, romStart, romEnd, segJump
.endmacro

// ******** Cmd 01: Load and Jump ******** //
.macro .ls_01, seg, romStart, romEnd, segJump
	.byte 0x00, 0x10, 0x00, seg
	.word romStart, romEnd, segJump
.endmacro
.macro .ls_loadAndJump2, seg, romStart, romEnd, segJump
	.ls_01 seg, romStart, romEnd, segJump
.endmacro

// ******** Cmd 02: End levelscript ******** //
.macro .ls_02
	.word 0x02040000
.endmacro
.macro .ls_end
	.ls_02 
.endmacro

// ******** Cmd 03: Delay Frames ******** //
.macro .ls_03, numFrames
	.halfword 0x0304, numFrames
.endmacro
.macro .ls_delayFrames, numFrames
	.ls_03 numFrames
.endmacro

// ******** Cmd 04: Delay Frames ******** //
.macro .ls_04, numFrames
	.halfword 0x0404, numFrames
.endmacro
.macro .ls_delayFrames2, numFrames
	.ls_04 numFrames
.endmacro

// ******** Cmd 05: Jump to address ******** //
.macro .ls_05, jumpAddress
	.word 0x05080000, jumpAddress
.endmacro
.macro .ls_jumpToAddress, jumpAddress
	.ls_05 jumpAddress
.endmacro

// ******** Cmd 06: Push stack ******** //
.macro .ls_06, pushAddress
	.word 0x06080000, pushAddress
.endmacro
.macro .ls_pushStack, pushAddress
	.ls_06 pushAddress
.endmacro

// ******** Cmd 07: Pop stack ******** //
.macro .ls_07
	.word 0x07040000
.endmacro
.macro .ls_popStack
	.ls_07 
.endmacro

// ******** Cmd 08: Push Stack + 16 ******** //
.macro .ls_08, stack16
	.halfword 0x0804, stack16
.endmacro
.macro .ls_pushStack16, stack16
	.ls_08 stack16 
.endmacro

// ******** Cmd 09: Pop Stack + 16 ******** //
.macro .ls_09
	.word 0x09040000
.endmacro
.macro .ls_popStack16
	.ls_09
.endmacro

// ******** Cmd 0A: Push Script + 0x00 ******** //
.macro .ls_0a
	.word 0x0A040000
.endmacro
.macro .ls_pushScript
	.ls_0a
.endmacro

// ******** Cmd 0B: Conditional Pop ******** //
.macro .ls_0b, op, arg
	.byte 0x0B, 0x08, op, 0x00
	.word arg
.endmacro
.macro .ls_condPop, op, arg
	.ls_0b, op, arg
.endmacro

// ******** Cmd 0C: Conditional Jump ******** //
.macro .ls_0c, op, arg, jumpAddress
	.byte 0x0C, 0x0C, op, 0x00
	.word arg, jumpAddress
.endmacro
.macro .ls_condJump, op, arg, jumpAddress
	.ls_0c op, arg, jumpAddress
.endmacro

// ******** Cmd 0D: Conditional Push ******** //
.macro .ls_0d, op, arg
	.byte 0x0D, 0x08, op, 0x00
	.word arg
.endmacro
.macro .ls_condPush, op, arg
	.ls_0d op, arg
.endmacro

// ******** Cmd 0E: Conditional Skip ******** //
.macro .ls_0e, op, arg
	.byte 0x0E, 0x08, op, 0x00
	.word arg
.endmacro
.macro .ls_condSkip, op, arg
	.ls_0e op, arg
.endmacro

// ******** Cmd 0F: Skip Next ******** //
.macro .ls_0f
	.word 0x0F040000
.endmacro
.macro .ls_skipNext
	.ls_0a
.endmacro

// ******** Cmd 10: No Operation ******** //
.macro .ls_10
	.word 0x10040000
.endmacro
.macro .ls_nop
	.ls_10
.endmacro

// ******** Cmd 11: Set Accumulator From ASM ******** //
.macro .ls_11, a0, func
	.halfword 0x1108, a0
	.word func
.endmacro
.macro .ls_callFunc, a0, func
	.ls_11 a0, func
.endmacro

// ******** Cmd 12: Actively Set Accumulator ******** //
.macro .ls_12, a0, func
	.halfword 0x1208, a0
	.word func
.endmacro
.macro .ls_callFuncLoop, a0, func
	.ls_12 a0, func
.endmacro

// ******** Cmd 13: Set Accumulator ******** //
.macro .ls_13, accum
	.halfword 0x1304, accum
.endmacro
.macro .ls_setAccum, accum
	.ls_13 accum
.endmacro

// ******** Cmd 14: Push Pool State ******** //
.macro .ls_14
	.word 0x14040000
.endmacro
.macro .ls_pushPoolState
	.ls_14
.endmacro

// ******** Cmd 15: Pop Pool State ******** //
.macro .ls_15
	.word 0x15040000
.endmacro
.macro .ls_popPoolState
	.ls_15
.endmacro

// ******** Cmd 16: Load ROM to RAM ******** //
.macro .ls_16, ramAddr, romStart, romEnd
	.word 0x16100000, ramAddr, romStart, romEnd
.endmacro
.macro .ls_romToRam, ramAddr, romStart, romEnd
	.ls_16 ramAddr, romStart, romEnd
.endmacro

// ******** Cmd 17: Load ROM to Segment ******** //
.macro .ls_17, ramSeg, romStart, romEnd
	.byte 0x17, 0x0C, 0x00, ramSeg
	.word romStart, romEnd
.endmacro
.macro .ls_romToSeg, ramSeg, romStart, romEnd
	.ls_17 ramSeg, romStart, romEnd
.endmacro

// ******** Cmd 18: Decompress MIO0 to Segment ******** //
.macro .ls_18, ramSeg, romStart, romEnd
	.byte 0x18, 0x0C, 0x00, ramSeg
	.word romStart, romEnd
.endmacro
.macro .ls_mio0ToSeg, ramSeg, romStart, romEnd
	.ls_18 ramSeg, romStart, romEnd
.endmacro

// ******** Cmd 19: Create Mario Demo ******** //
.macro .ls_19, setting
	.byte 0x19, 0x04, 0x00, setting
.endmacro
.macro .ls_createMarioDemo, setting
	.ls_19 setting
.endmacro

// ******** Cmd 1A: Decompress MIO0 Textures ******** //
.macro .ls_1a, ramSeg, romStart, romEnd
	.byte 0x1A, 0x0C, 0x00, ramSeg
	.word romStart, romEnd
.endmacro
.macro .ls_mio0TexToSeg, ramSeg, romStart, romEnd
	.ls_1a ramSeg, romStart, romEnd
.endmacro

// ******** Cmd 1B: Start Load Sequence ******** //
.macro .ls_1b
	.word 0x1B040000
.endmacro
.macro .ls_startLoad
	.ls_1b
.endmacro

// ******** Cmd 1C: ??? ******** //
.macro .ls_1c
	.word 0x1C040000
.endmacro

// ******** Cmd 1D: End Load Sequence ******** //
.macro .ls_1d
	.word 0x1D040000
.endmacro
.macro .ls_endLoad
	.ls_1d
.endmacro

// ******** Cmd 1E:  ??? ******** //
.macro .ls_1e
	.word 0x1E040000
.endmacro

// ******** Cmd 1F: Start Area ******** //
.macro .ls_1f, area, segAddr
	.byte 0x1F, 0x08, area, 0x00
	.word segAddr
.endmacro
.macro .ls_startArea, area, segAddr
	.ls_1f area, segAddr
.endmacro

// ******** Cmd 20: End Area ******** //
.macro .ls_20
	.word 0x20040000
.endmacro
.macro .ls_endArea
	.ls_20
.endmacro

// ******** Cmd 21: Load Polygon Without Geo Layout ******** //
.macro .ls_21, layer, id, segAddr
	.byte 0x21, 0x08, layer << 4, id
	.word segAddr
.endmacro
.macro .ls_loadModelDL, layer, id, segAddr
	.ls_21 layer, id, segAddr
.endmacro

// ******** Cmd 22: Load Polygon With Geo Layout ******** //
.macro .ls_22, id, segAddr
	.byte 0x22, 0x08, 0x00, id
	.word segAddr
.endmacro
.macro .ls_loadModel, id, segAddr
	.ls_22 id, segAddr
.endmacro

// ******** Cmd 23: ??? ******** //
.macro .ls_23, a, bbb, cccccccc, dddddddd
	.byte 0x23, 0x0C, a << 4 | bbb >> 8, bbb
	.word cccccccc, dddddddd
.endmacro

// ******** Cmd 24: Create new 3D object ******** //
.macro .ls_24, acts, mdlID, x, y, z, rx, ry, rz, b1, b2, behSegOff
	.byte 0x24, 0x18, acts, mdlID
	.halfword x, y, z, rx, ry, rz, b1, b2
	.word behSegOff
.endmacro
.macro .ls_newObj, acts, mdlID, x, y, z, rx, ry, rz, b1, b2, behSegOff
	.ls_24 acts, mdlID, x, y, z, rx, ry, rz, b1, b2, behSegOff
.endmacro
.macro .ls_newObj_p, acts, mdlID, x, y, z, behSegOff
	.ls_24 acts, mdlID, x, y, z, 0, 0, 0, 0, 0, behSegOff
.endmacro
.macro .ls_newObj_pb, acts, mdlID, x, y, z, b1, b2, behSegOff
	.ls_24 acts, mdlID, x, y, z, 0, 0, 0, b1, b2, behSegOff
.endmacro

.defineLabel .ls_Act1, 0x01
.defineLabel .ls_Act2, 0x02
.defineLabel .ls_Act3, 0x04
.defineLabel .ls_Act4, 0x08
.defineLabel .ls_Act5, 0x10
.defineLabel .ls_Act6, 0x20
.defineLabel .ls_AllActs, 0x1F

// ******** Cmd 25: Create Mario Object ******** //
.macro .ls_25, mdlID, params, behSegOff
	.byte 0x25, 0x0C, 0x00, mdlID
	.word params, behSegOff
.endmacro
.macro .ls_newMarioObject, mdlID, params, behSegOff
	.ls_25 mdlID, params, behSegOff
.endmacro

// ******** Cmd 26: Connect Warps ******** //
.macro .ls_26, warpFromID, warpToID, courseID, courseArea
	.byte 0x26, 0x08, warpFromID, courseID, courseArea, warpToID, 0x00, 0x00
.endmacro
.macro .ls_connectWarps, warpFromID, warpToID, courseID, courseArea
	.ls_26 warpFromID, warpToID, courseID, courseArea
.endmacro

// ******** Cmd 27: Setup painting warp ******** //
.macro .ls_27, warpFromID, warpToID, courseID, courseArea
	.byte 0x27, 0x08, warpFromID, courseID, courseArea, warpToID, 0x00, 0x00
.endmacro
.macro .ls_paintingWarp, warpFromID, warpToID, courseID, courseArea
	.ls_27 warpFromID, warpToID, courseID, courseArea
.endmacro

// ******** Cmd 28: Setup instant warp ******** //
.macro .ls_28, col, area, tX, tY, tZ
	.byte 0x28, 0x0C, col, area
	.halfword tX, tY, tZ, 0x0000
.endmacro

// ******** Cmd 29: ??? ******** //
// ******** Cmd 2A: ??? ******** //
.macro .ls_2a
	.word 0x2A040000
.endmacro

// ******** Cmd 2B: Set Mario's default position ******** //
.macro .ls_2b, area, ry, x, y, z
	.byte 0x2B, 0x0C, area, 0x00
	.halfword ry, x, y, z
.endmacro
.macro .ls_setMarioDefaultPos, area, ry, x, y, z
	.ls_2b area, ry, x, y, z
.endmacro

// ******** Cmd 2C: ??? ******** //
.macro .ls_2c
	.word 0x2C040000
.endmacro

// ******** Cmd 2D: ??? ******** //
.macro .ls_2d
	.word 0x2D040000
.endmacro

// ******** Cmd 2E: Load Collision ******** //
.macro .ls_2e, segAddr
	.word 0x2E080000, segAddr
.endmacro
.macro .ls_loadCollision, segAddr
	.ls_2e segAddr
.endmacro

// ******** Cmd 2F: Render Area? ******** //
.macro .ls_2f, segAddr
	.word 0x2F080000, segAddr
.endmacro
.macro .ls_setRenderArea, segAddr
	.ls_2f segAddr
.endmacro

// ******** Cmd 30: Show dialog ******** //
.macro .ls_30, dialogID
	.byte 0x30, 0x04, 0x00, dialogID
.endmacro

// ******** Cmd 31: Set default terrain ******** //
.macro .ls_31, terrain
	.byte 0x31, 0x04, 0x00, terrain
.endmacro
.macro .ls_setDefaultTerrain, terrain
	.ls_31 terrain
.endmacro
.defineLabel .ls_ter_Normal, 0x00
.defineLabel .ls_ter_NormalB, 0x01
.defineLabel .ls_ter_Snow, 0x02
.defineLabel .ls_ter_Sand, 0x03
.defineLabel .ls_ter_BBH, 0x04
.defineLabel .ls_ter_WaterLevel, 0x05
.defineLabel .ls_ter_SlipperySlide, 0x06

// ******** Cmd 32: No Operation 2 ******** //
.macro .ls_32
	.word 0x32040000
.endmacro
.macro .ls_nop2
	.ls_32
.endmacro

// ******** Cmd 33: Fade Color ******** //
.macro .ls_33, enable, duration, r, g, b
	.byte 0x33, 0x08, enable, duration, r, g, b, 0x00
.endmacro
.macro .ls_fadeColor, enable, duration, r, g, b
	.ls_33 enable, duration, r, g, b
.endmacro

// ******** Cmd 34: Blackout Screen ******** //
.macro .ls_34, enable
	.byte 0x34, 0x04, enable, 0x00
.endmacro
.macro .ls_blackoutScreen, enable
	.ls_34 enable
.endmacro

// ******** Cmd 35: ??? ******** //
.macro .ls_35, isZero
	.byte 0x35, 0x04, isZero, 0x00
.endmacro

// ******** Cmd 36: Set Music with parameters ******** //
.macro .ls_36, p1, p2, p3, seq
	.byte 0x36, 0x08, p1, p2, p3, seq, 0x00, 0x00
.endmacro
.macro .ls_setMusicAdv, p1, p2, p3, seq
	.ls_36 p1, p2, p3, seq
.endmacro

// ******** Cmd 37: Set Music ******** //
.macro .ls_37, seq
	.byte 0x37, 0x04, 0x00, seq
.endmacro
.macro .ls_setMusic, seq
	.ls_37 seq
.endmacro

// ******** Cmd 38: ??? ******** //
.macro .ls_38, a0
	.halfword 0x3804, a0
.endmacro

// ******** Cmd 39: Place Macro Objects ******** //
.macro .ls_39, segAddr
	.word 0x39080000, segAddr
.endmacro
.macro .ls_setMacroObjects, segAddr
	.ls_39 segAddr
.endmacro

// ******** Cmd 3A: ??? ******** //

// ******** Cmd 3B: Create a Jet Stream ******** //
.macro .ls_3b, x, y, z, i
	.word 0x3B0C0000
	.halfword x, y, z, i
.endmacro
.macro .ls_newJetStream, x, y, z, i
	.ls_3b x, y, z, i
.endmacro

// ******** Cmd 3C: ??? ******** //
.macro .ls_3c, aa, bb
	.byte 0x3C, 0x04, aa, bb
.endmacro

