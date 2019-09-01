// Note: All macro names are not case-sensitive

.macro .f_CalSaveChecksum, ramAddr, numBytes, upper16
	li a0, ramAddr
	li a1, numBytes
	jal 0x8027939C
	li.l a2, upper16
.endmacro

.macro .f_CheckCurrObjBehavior, behAddr
	li.u a0, behAddr
	jal 0x802A14FC
	li.l a0, behAddr
.endmacro

.macro .f_CheckObjBehavior, objPtr, behAddr
	li a0, objPtr
	li.u a1, behAddr
	jal 0x802A1554
	li.l a1, behAddr
.endmacro

// Needed to clear .f_PlayTransition
.macro .f_ClearTransition
	sb r0, 0x8033BAB3
.endmacro

.macro .f_ConfigureTimer, option
	jal 0x802495E0
	li.l a0, option
.endmacro

.macro .f_CreateBreakParticles, count, mdlID, size_f, param
	li a0, count
	li a1, mdlID
	li a2, float(size_f)
	jal 0x802AE0CC
	li.l a3, param
.endmacro

.macro .f_CreateStar, x_f, y_f, z_f
	li a0, float(x_f)
	mtc1 a0, f12
	li a0, float(y_f)
	mtc1 a0, f14
	li.u a2, float(z_f)
	jal 0x802F2B88
	li.l a2, float(z_f)
.endmacro

.macro .f_cosf_imm, angle_rad_f
	li a0, float(angle_rad_f)
	jal 0x80325310
	mtc1 a0, f12
.endmacro

.macro .f_cosf, reg_f
	jal 0x80325310
	mov.s f12, reg_f
.endmacro

.macro .f_DeactivateObject, obj1_ptr
	lw.u a0, obj1_ptr
	jal 0x802A0568 // DeactivateObject
	lw.l a1, obj1_ptr
.endmacro

.macro .f_DistanceFromObject3D, obj1_ptr, obj2_ptr
	lw a0, obj1_ptr
	lw.u a1, obj2_ptr
	jal 0x8029E2F8 // DistanceFromObject3D
	lw.l a1, obj2_ptr
.endmacro

.macro .f_DistanceFromObject3D_imm, obj1_ptr, obj2_ptr
	li a0, obj1_ptr
	li.u a1, obj2_ptr
	jal 0x8029E2F8 // DistanceFromObject3D
	li.l a1, obj2_ptr
.endmacro

.macro .f_DmaCopy, ramAddr, romStart, romEnd
	li a0, ramAddr
	li a1, romStart
	li.u a2, romEnd
	jal 0x80278504
	li.l a2, romEnd
.endmacro

.macro .f_ExplodeCurrObject
	jal 0x802E6AF8
	nop
.endmacro

.macro .f_HideCurrObj
	jal 0x8029F620
	nop
.endmacro

.macro .f_IsMarioGroundPounding
	jal 0x802A3754
	nop
.endmacro

.macro .f_IsMarioStepping
	jal 0x802A3CFC
	nop
.endmacro

.macro .f_memcpy, dst, src, numBytes
	li a0, strPtr
	li a1, strPtr
	jal 0x803273F0
	li.l a2, numBytes
.endmacro

.macro .f_memset, dst, value, numBytes
	li a0, dst
	li a1, value
	li a2, numBytes
	beqz a2, memset_End
	move a3, a0
	@@memset_Loop:
	addiu a2, a2, 0xFFFF
	addiu a3, a3, 0x01
	bnez a2, memset_Loop
	sb a1, 0xFFFF(a3)
	@@memset_End:
	move v0, r0
.endmacro

.macro .f_osEepromRead, eepGroup, eepRAM 
	li a0, 0x8033AF78
	li a2, eepRAM
	jal 0x80329150
	li.l a1, eepGroup
.endmacro

.macro .f_osEepromWrite, eepGroup, eepRAM 
	li a0, 0x8033AF78
	li a2, eepRAM
	jal 0x80328AF0
	li.l a1, eepGroup
.endmacro

.macro .f_osEepromLongRead, eepGroup, eepRAM, numBytes 
	li a0, 0x8033AF78
	li a1, eepGroup
	li a2, eepRAM
	jal 0x80324690
	li.l a3, numBytes 
.endmacro

.macro .f_osEepromLongWrite, eepGroup, eepRAM, numBytes 
	li a0, 0x8033AF78
	li a1, eepGroup
	li a2, eepRAM
	jal 0x803247D0
	li.l a3, numBytes 
.endmacro

.macro .f_osViBlack, setBlackout
	jal 0x80323340
	li.l a0, setBlackout
.endmacro

.macro .f_PlaySound, argument
	li.u a0, argument
	jal 0x802CA190
	li.l a0, argument
.endmacro

.macro .f_PlayTransition, image, time, red, green, blue
	li a0, blue
	sb a0, 0x10(sp)
	li a0, image
	li a1, time
	li a2, red
	jal 0x8027B1A0
	li.l a3, green
.endmacro

.macro .f_PrintByte, x, y, strAddr, valueAddr
	li a0, x 
	li a1, y
	lb a3, valueAddr
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintUByte, x, y, strAddr, valueAddr
	li a0, x 
	li a1, y
	lbu a3, valueAddr
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintShort, x, y, strAddr, valueAddr
	li a0, x 
	li a1, y
	lh a3, valueAddr
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintUShort, x, y, strAddr, valueAddr
	li a0, x 
	li a1, y
	lhu a3, valueAddr
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintInt, x, y, strAddr, valueAddr
	li a0, x 
	li a1, y
	lw a3, valueAddr
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintImm, x, y, strAddr, value
	li a0, x 
	li a1, y
	li a3, value
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PutMiniString, x, y, strAddr//setup string
	.orga 0x1203b50
	addiu sp, sp, -0x20
	sw ra, 0x14 (SP)
	sh a1, 0x18 (SP)
	sh a0, 0x1a (SP)
	jal 0x802d7384
	sw a2, 0x1c (SP)
	lw a2, 0x1C (SP)
	lh a1, 0x18 (SP)
	lh a0, 0x1a (SP)
	lui at, 0x8034
	lw v0, 0xb06c (AT)
	lui t6, 0x0600
	sw t6, 0x0 (V0)
	li t7, 0x02011cc8 //ia8 text string begin
	sw t7, 0x4 (V0)
	lui t6, 0xfb00
	sw t6, 0x8 (V0)
	lui t7, 0xffff
	ori t7, t7, 0xffff //place holder ENV color
	sw t7, 0xc (v0)
	lui t8, 0xb900
	ori t8, t8, 0x031d
	sw t8, 0x10 (V0)
	lui t7, 0x0050
	ori t7, t7, 0x4240
	sw t7, 0x14 (V0)
	addiu v0, v0, 0x18
	sw v0, 0xb06c (AT)
	lw ra, 0x14 (SP)
	jr ra
	addiu sp, sp, 0x20


	jal 0x80403b50 //setup string
	nop
	jal 0x802d77dc
	ori a2, s7, 0x7000
	jal 0x80403c00 //end string
	nop

	//end string
	.orga 0x1203c00
	lui at, 0x8034
	lw v0, 0xb06c (AT)
	lui t6, 0x0600
	sw t6, 0x0 (V0)
	li t7, 0x02011d50 //ia8 text end
	sw t7, 0x4 (V0)
	addiu v0, v0, 0x8
	sw v0, 0xb06c (AT)
	jr ra
	nop
.endmacro

.macro .f_PrintReg, x, y, strAddr, register
	li a0, x 
	li a1, y
	move a3, register
	la.u a2, strAddr 
	jal 0x802D62D8
	la.l a2, strAddr 
.endmacro

.macro .f_PrintXY, x, y, strAddr 
	li a0, x 
	li a1, y
	la.u a2, strAddr 
	jal 0x802D66C0
	la.l a2, strAddr 
.endmacro

.macro .f_RandomRange, offset, multipler
	li a0, offset
	jal 0x802FA964
	li.l a1, multipler
.endmacro

.macro .f_RandomRange2, offset, multipler, mod
	li a0, offset
	li a1, multipler
	jal 0x802FA964
	li.l a2, mod
.endmacro

// Returns V0 = u16 value from 0x0000 to 0xFFFF
.macro .f_RandomU16
	jal 0x80383BB0
	nop
.endmacro

// Returns F0 = float value from 0.0 to 1.0
.macro .f_RandomFloat
	jal 0x80383CB4
	nop
.endmacro

// Returns V0 = either 1 or -1
.macro .f_RandomSign
	jal 0x80383D1C
	nop
.endmacro

.macro .f_RotateTorwardsMario, obj_C8, obj_160, speed
	lw a0, obj_C8
	lw a1, obj_160
	jal 0x8029E530
	li.l a2, speed
.endmacro

.macro .f_SaveFileData, fileNumber
	li.l a0, 0x01
	lui at, 0x8034
	sb a0, 0xB4A5(at)
	sb a0, 0xB4A6(at)
	jal 0x80279840
	li.l a0, fileNumber
.endmacro

.macro .f_SaveMenuData
	li a0, 0x01
	lui at, 0x8034
	jal 0x802794A0
	sb a0, 0xB4A5(at)
.endmacro

.macro .f_SegmentedToVirtual, segAddr
	li.u a0, segAddr
	jal 0x80277F50
	li.l a0, segAddr
.endmacro

.macro .f_SetCurrObjAnimation, animIndex
	jal 0x8029F464
	li.l a0, animIndex
.endmacro

.macro .f_SetCurrObjModel, mdlID
	jal 0x802A04C0
	li.l a0, mdlID
.endmacro

.macro .f_SetCurrObjScale, scale_f
	li a0, float(scale_f)
	jal 0x8029F430
	mtc1 a0, f12
.endmacro

.macro .f_SetObjBehavior, objPtr, behAddr
	li a1, behAddr
	li.u a0, objPtr
	jal 0x802A14C4
	li.l a0, objPtr
.endmacro

.macro .f_SetObjScale, objPtr, sx_f, sy_f, sz_f
	li a1, float(sx_f)
	li a2, float(sy_f)
	li a3, float(sz_f)
	li.u a0, objPtr
	jal 0x8029F3D0
	li.l a0, objPtr
.endmacro

.macro .f_ShakeScreen, intensity
	jal 0x802A50FC
	li.l a0, intensity
.endmacro

.macro .f_sinf_imm, angle_rad_f
	li a0, float(angle_rad_f)
	jal 0x80325480
	mtc1 a0, f12
.endmacro

.macro .f_sinf, reg_f
	jal 0x80325480
	mov.s f12, reg_f
.endmacro

.macro .f_SpawnObj, parentPtr, mdlID, behAddr
	.if (parentPtr == SM64_CURR_OBJ_PTR) || (parentPtr == SM64_MARIO_OBJ_PTR)
		lw a0, parentPtr
		la a2, behAddr
		jal 0x8029EDCC
		li.l a1, mdlID
	.else
		.error "Sorry, .f_SpawnObj only supports SM64_CURR_OBJ_PTR and SM64_MARIO_OBJ_PTR at the moment!"
	.endif
.endmacro

.macro .f_SpawnObjXYZ, mdlID, behAddr, x_f, y_f, z_f
	lw a0, SM64_MARIO_OBJ_PTR
	la a2, behAddr
	jal 0x8029EDCC
	li a1, mdlID
	
	li a0, float(x_f)
	mtc1 a0, f12
	li a1, float(y_f)
	mtc1 a1, f14
	li a2, float(z_f)
	mtc1 a2, f16
	swc1 f12, 0xA0(v0) 
	swc1 f14, 0xA4(v0)
	swc1 f16, 0xA8(v0)
.endmacro

.macro .f_strchr, strPtr, char
	li a0, strPtr
	jal 0x80327444
	li.l a1, char
.endmacro

.macro .f_strlen, strPtr
	li.u a0, strPtr
	jal 0x8032741C
	li.l a0, strPtr
.endmacro

// Tests for buttons held down by controller 1
; buttons = buttons pressed by player
; heldDown = make this false if you want an action to only happen once
; branchFalseLabel = branch to label if false
.macro .f_TestInput, buttons, heldDown, branchFalseLabel
	.if heldDown
		lh at, 0x8033AFA0
	.else
		lw at, 0x8033AFA0
	.endif
	andi at, at, buttons
	li a0, buttons
	bne at, a0, branchFalseLabel
	nop
.endmacro

// Tests for buttons held down by controller 2
; buttons = buttons pressed by player
; heldDown = make this false if you want an action to only happen once
; branchFalseLabel = branch to label if false
.macro .f_TestInput2, buttons, heldDown, branchFalseLabel
	.if heldDown
		lh at, 0x8033AFBC
	.else
		lw at, 0x8033AFBC
	.endif
	andi at, at, buttons
	li a0, buttons
	bne at, a0, branchFalseLabel
	nop
.endmacro

.macro .f_TestForMarioAction, action, branchFalseLabel
	li a0, action
	lw a1, SM64_MARIO_ACTION
	bne a0, a1, branchFalseLabel
	nop
.endmacro

.macro .f_TestForNotMarioAction, action, branchFalseLabel
	li a0, action
	lw a1, SM64_MARIO_ACTION
	beq a0, a1, branchFalseLabel
	nop
.endmacro

.macro .f_UnhideCurrObj
	jal 0x8029F6BC
	nop
.endmacro

.macro .f_WarpMario, warpToID, delay
	lui at, 0x8034
	li a0, 0x01
	sh a0, 0xB252(at)
	li a0, delay
	sh a0, 0xB254(at)
	li a0, warpToID
	sh a0, 0xB256(at)
.endmacro
