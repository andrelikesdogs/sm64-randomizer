.defineLabel .bs_Interaction_MarioHang, 		0x00000001
.defineLabel .bs_Interaction_MarioPickup, 		0x00000002
.defineLabel .bs_Interaction_Door, 				0x00000004
.defineLabel .bs_Interaction_Coin, 				0x00000010
.defineLabel .bs_Interaction_Pole, 				0x00000040
.defineLabel .bs_Interaction_ObjectPunch, 		0x00000200
.defineLabel .bs_Interaction_BlowAwayMario, 	0x00000400
.defineLabel .bs_Interaction_DoorWarp, 			0x00000800
.defineLabel .bs_Interaction_Star, 				0x00001000
.defineLabel .bs_Interaction_HoleWarp, 			0x00002000
.defineLabel .bs_Interaction_Cannon, 			0x00004000
.defineLabel .bs_Interaction_HealMario, 		0x00010000
.defineLabel .bs_Interaction_Bully, 			0x00020000
.defineLabel .bs_Interaction_Flame, 			0x00040000
.defineLabel .bs_Interaction_KoopaShell, 		0x00080000
.defineLabel .bs_Interaction_Message, 			0x00800000
.defineLabel .bs_Interaction_MarioSpin, 		0x01000000
.defineLabel .bs_Interaction_MarioFall, 		0x02000000
.defineLabel .bs_Interaction_ShrinkWarp, 		0x08000000
.defineLabel .bs_Interaction_ShockMario, 		0x20000000
.defineLabel .bs_Interaction_Normal, 			0x40000000
// I know that I'm missing a few, they will be added in a later version

// ******** Cmd 00: Start Behavior ******** //
.macro .bs_00, objType
	.byte 0x00, objType, 0x00, 0x00
.endmacro
.macro .bs_startBehavior, objType
	.bs_00 objType
.endmacro

// ******** Cmd 01: State Loop ******** //
.macro .bs_01, value
	.halfword 0x0100, value
.endmacro
.macro .bs_stateLoop, value
	.bs_01  value
.endmacro

// ******** Cmd 02: Jump and Link ******** //
.macro .bs_02, segAddr
	.word 0x02000000, segAddr
.endmacro
.macro .bs_jumpAndLink, segAddr
	.bs_02 segAddr
.endmacro

// ******** Cmd 03: Return from CMD 02 ******** //
.macro .bs_03
	.word 0x03000000
.endmacro
.macro .bs_returnFromJump
	.bs_03
.endmacro

// ******** Cmd 04: Jump ******** //
.macro .bs_04, segAddr
	.word 0x04000000, segAddr
.endmacro
.macro .bs_jump, segAddr
	.bs_04 segAddr
.endmacro

// ******** Cmd 05: Loop N ******** //
.macro .bs_05, loopCount
	.halfword 0x0500, loopCount
.endmacro
.macro .bs_loopN, loopCount
	.bs_05 loopCount
.endmacro

// ******** Cmd 06: End Loop N ******** //
.macro .bs_06
	.word 0x06000000
.endmacro
.macro .bs_endLoopN
	.bs_06
.endmacro

// ******** Cmd 07: Infinite Loop ******** //
.macro .bs_07
	.word 0x07000000
.endmacro
.macro .bs_infLoop
	.bs_07
.endmacro

// ******** Cmd 08: Loop Start ******** //
.macro .bs_08
	.word 0x08000000
.endmacro
.macro .bs_startLoop
	.bs_08
.endmacro

// ******** Cmd 09: Loop End ******** //
.macro .bs_09
	.word 0x09000000
.endmacro
.macro .bs_endLoop
	.bs_09
.endmacro

// ******** Cmd 0A: End of Behavior (No Operation) ******** //
.macro .bs_0A
	.word 0x0A000000
.endmacro
.macro .bs_endBehavior
	.bs_0A
.endmacro

// ******** Cmd 0B: End of Behavior (No Operation) ******** //
.macro .bs_0B
	.word 0x0B000000
.endmacro
.macro .bs_endBehavior2
	.bs_0B
.endmacro

// ******** Cmd 0C: Call Function ******** //
.macro .bs_0C, asmAddr
	.word 0x0C000000, asmAddr
.endmacro
.macro .bs_callFunction, asmAddr
	.bs_0C asmAddr
.endmacro

// ******** Cmd 0D: Update Object ******** //
.macro .bs_0D, address, value
	.byte 0x0D, address
	.halfword value
.endmacro
.macro .bs_updateObject, address, value
	.bs_0D address, value
.endmacro

// ******** Cmd 0E: Sight Distance? ******** //
.macro .bs_0E, address, value
	.byte 0x0E, address
	.halfword value
.endmacro
.macro .bs_sightDistance, address, value
	.bs_0E address, value
.endmacro

// ******** Cmd 0F: Texture Animate ******** //
.macro .bs_0F, address, value
	.byte 0x0F, address
	.halfword value
.endmacro
.macro .bs_animateTexture, address, value
	.bs_0F address, value
.endmacro

// ******** Cmd 10: Special Parameter ******** //
.macro .bs_10, address, value
	.byte 0x10, address
	.halfword value
.endmacro
.macro .bs_specialParameter, address, value
	.bs_10 address, value
.endmacro

// ******** Cmd 11: Bit-set ******** //
.macro .bs_11, address, value
	.byte 0x11, address
	.halfword value
.endmacro
.macro .bs_bitSet, address, value
	.bs_11 address, value
.endmacro

// ******** Cmd 12: Bit-clear ******** //
.macro .bs_12, address, value
	.byte 0x12, address
	.halfword value
.endmacro
.macro .bs_bitClear, address, value
	.bs_12 address, value
.endmacro

// ******** Cmd 13: Add RNG ******** //
.macro .bs_13, address, offset, shift
	.byte 0x13, address
	.halfword offset, shift, 0x0000
.endmacro
.macro .bs_addRNG, address, offset, shift
	.bs_13 address, offset, shift
.endmacro

// ******** Cmd 14: Float Multiply ******** //
.macro .bs_14, address, val1, val2
	.byte 0x14, address
	.halfword val1, val2, 0x0000
.endmacro
.macro .bs_floatMultiply, address, val1, val2
	.bs_14 address, val1, val2
.endmacro

// ******** Cmd 15: Float Multiply and Offset ******** //
.macro .bs_15, address, add, mul
	.byte 0x15, address
	.halfword add, mul, 0x0000
.endmacro
.macro .bs_floatMultiplyAndOffset, address, add, mul
	.bs_15 address, add, mul
.endmacro

// ******** Cmd 16: Float Add ******** //
.macro .bs_16, address, add, add2
	.byte 0x16, address
	.halfword add, add2, 0x0000
.endmacro
.macro .bs_floatAdd, address, add, add2
	.bs_16 address, add, add2
.endmacro

// ******** Cmd 17: Right Shift ******** //
.macro .bs_17, address, add, shift
	.byte 0x17, address
	.halfword add, shift, 0x0000
.endmacro
.macro .bs_rightShift, address, add, shift
	.bs_17 address, add, shift
.endmacro

// ******** Cmd 18: Unused (No Operation) ******** //
.macro .bs_18
	.word 0x18000000
.endmacro
.macro .bs_nop
	.bs_18
.endmacro

// ******** Cmd 19: Unused (No Operation) ******** //
.macro .bs_19
	.word 0x19000000
.endmacro

// ******** Cmd 1A: Unused (No Operation) ******** //
.macro .bs_1A
	.word 0x1A000000
.endmacro

// ******** Cmd 1B: Change Model ID ******** //
.macro .bs_1B, newModelID
	.halfword 0x1B00, newModelID
.endmacro
.macro .bs_changeModelID, newModelID
	.bs_1B newModelID
.endmacro

// ******** Cmd 1C: Load Child Object ******** //
.macro .bs_1C, childModelID, childSegBehavior
	.word 0x1C000000, childModelID, childSegBehavior
.endmacro
.macro .bs_loadChildObject, childModelID, childSegBehavior
	.bs_1C childModelID, childSegBehavior
.endmacro

// ******** Cmd 1D: Deactivate Object ******** //
.macro .bs_1D
	.word 0x1D000000
.endmacro
.macro .bs_deactivateObject
	.bs_1D
.endmacro

// ******** Cmd 1E: Drop to Ground ******** //
.macro .bs_1E
	.word 0x1E000000
.endmacro
.macro .bs_dropToGround
	.bs_1E
.endmacro

// ******** Cmd 1F: Wave calculation ******** //
.macro .bs_1F, address1, address2, address3
	.byte 0x1F, address1, address2, address3
.endmacro
.macro .bs_waveCalculation, address1, address2, address3
	.bs_1F address1, address2, address3
.endmacro

// ******** Cmd 20: Add Address Values (unused) ******** //
.macro .bs_20, address1, address2, address3
	.byte 0x20, address1, address2, address3
.endmacro
.macro .bs_addAddressValues, address1, address2, address3
	.bs_20 address1, address2, address3
.endmacro

// ******** Cmd 21: Set Billboarding ******** //
.macro .bs_21
	.word 0x21000000
.endmacro
.macro .bs_setBillboarding
	.bs_21
.endmacro

// ******** Cmd 22: Set 0x10 flag ******** //
.macro .bs_22
	.word 0x22000000
.endmacro
.macro .bs_setGraph10
	.bs_22
.endmacro

// ******** Cmd 23: Collision sphere size ******** //
.macro .bs_23, xz_plane, y_plane
	.halfword 0x2300, 0x0000, xz_plane, y_plane
.endmacro
.macro .bs_setCollisionSphereSize, xz_plane, y_plane
	.bs_23 xz_plane, y_plane
.endmacro

// ******** Cmd 24: Unused (No Operation) ******** //
.macro .bs_24
	.word 0x24000000
.endmacro

// ******** Cmd 25: State Cycle ******** //
.macro .bs_25, address
	.byte 0x25, address, 0x00, 0x00
.endmacro
.macro .bs_stateCycle, address
	.bs_25 address
.endmacro

// ******** Cmd 26: Loop? ******** //
.macro .bs_26, loopCount
	.byte 0x26, loopCount, 0x00, 0x00
.endmacro
.macro .bs_loop, loopCount
	.bs_26 loopCount
.endmacro

// ******** Cmd 27: Set Word ******** //
.macro .bs_27, address, value
	.byte 0x27, address, 0x00, 0x00
	.word value
.endmacro
.macro .bs_setWord, address, value
	.bs_27 address, value
.endmacro

// ******** Cmd 28: Animate ******** //
.macro .bs_28, amount
	.byte 0x28, amount, 0x00, 0x00
.endmacro
.macro .bs_animate, amount
	.bs_28 amount
.endmacro

// ******** Cmd 29: Load Child Object With Parameters ******** //
.macro .bs_29, childBehParam, childModelID, childSegBehavior
	.halfword 0x29000, childBehParam
	.word childModelID, childSegBehavior
.endmacro
.macro .bs_loadChildObjectWithParams, childBehParam, childModelID, childSegBehavior
	.bs_29 childBehParam, childModelID, childSegBehavior
.endmacro

// ******** Cmd 2A: Set collision ******** //
.macro .bs_2A, collisionSegAddress
	.word 0x2A000000, collisionSegAddress
.endmacro
.macro .bs_setCollision, collisionSegAddress
	.bs_2A collisionSegAddress
.endmacro

// ******** Cmd 2B: Set collision sphere ******** //
.macro .bs_2B, xz_plane, y_plane, obj_208
	.halfword 0x2B000, 0x0000, xz_plane, y_plane, obj_208
.endmacro
.macro .bs_setCollisionSphere, xz_plane, y_plane, obj_208
	.bs_2B xz_plane, y_plane, obj_208
.endmacro

// ******** Cmd 2C: Spawn Object ******** //
.macro .bs_2C, childModelID, childSegBehavior
	.word 0x2C000000, childModelID, childSegBehavior
.endmacro
.macro .bs_spawnObject, amount
	.bs_2C childModelID, childSegBehavior
.endmacro

// ******** Cmd 2D: Set Init Position ******** //
.macro .bs_2D
	.word 0x2D000000
.endmacro
.macro .bs_setInitPosition
	.bs_2D
.endmacro

// ******** Cmd 2E: Sight Distance ******** //
.macro .bs_2E, obj_200, obj_204
	.word 0x2E000000
	.halfword obj_200, obj_204
.endmacro
.macro .bs_setSightDistance, obj_200, obj_204
	.bs_2E obj_200, obj_204
.endmacro

// ******** Cmd 2F: Set Interation ******** //
.macro .bs_2F, interaction
	.word 0x2F000000, interaction
.endmacro
.macro .bs_setInteraction, interaction
	.bs_2F interaction
.endmacro


// ******** Cmd 30: Set Gravity ******** //
.macro .bs_30, obj_128, obj_E8, obj_158, obj_12C, obj_170, obj_174
	.word 0x30000000
	.halfword obj_128, obj_E8, obj_158, obj_12C, obj_170, obj_174, 0x0000, 0x0000
.endmacro
.macro .bs_setGravity, obj_128, obj_E8, obj_158, obj_12C, obj_170, obj_174
	.bs_30 obj_128, obj_E8, obj_158, obj_12C, obj_170, obj_174
.endmacro

// ******** Cmd 31: Set Obj->0x190 ******** //
// Obj->0x190 is some sort of flag that is related to interactions
.macro .bs_31, obj_190
	.word 0x31000000, obj_190
.endmacro
.macro .bs_setObj190, obj_190
	.bs_31 obj_190
.endmacro

// ******** Cmd 32: Scale Object ******** //
.macro .bs_32, scale
	.halfword 0x3200, scale
.endmacro
.macro .bs_scaleObject, scale
	.bs_32 scale
.endmacro

// ******** Cmd 33: Child Object Change ******** //
.macro .bs_33, address, clear
	.byte 0x33, address, 0x00, 0x00
	.word clear
.endmacro
.macro .bs_clearChildValue, address, clear
	.bs_33 address, clear
.endmacro

// ******** Cmd 34: Texture Animate Rate ******** //
.macro .bs_34, address, divideValue
	.byte 0x34, address
	.halfword divideValue
.endmacro
.macro .bs_textureAnimateRate, address, divideValue
	.bs_34 address, divideValue
.endmacro

// ******** Cmd 35: Clear Graph Flag ******** //
.macro .bs_35
	.word 0x35000000
.endmacro
.macro .bs_clearGraphFlag
	.bs_35
.endmacro

// ******** Cmd 36: Set Value ******** //
.macro .bs_36, address, value
	.byte 0x36, address, 0x00, 0x00
	.halfword value, 0x0000
.endmacro
.macro .bs_setValue, address, value
	.bs_36 address, value
.endmacro

// ******** Cmd 37: Spawn Something ******** //
.macro .bs_37, spawnASMFunction
	.word 0x37000000, spawnASMFunction
.endmacro
.macro .bs_spawnFromASM, spawnASMFunction
	.bs_37 spawnASMFunction
.endmacro


















