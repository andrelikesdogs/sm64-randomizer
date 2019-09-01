.definelabel .gs_layer_solid, 0x01
.definelabel .gs_layer_alpha, 0x04
.definelabel .gs_layer_trans, 0x05

// ******** Cmd 00: Branch and Store ******** //
.macro .gs_00, segAddr
	.word 0x00000000, segAddr
.endmacro

// ******** Cmd 01: End Geometry Layout ******** //
.macro .gs_01
	.word 0x01000000
.endmacro
.macro .gs_end
	.gs_01 
.endmacro

// ******** Cmd 02: Branch Geometry Layout ******** //
.macro .gs_02, storeReturn, segAddr
	.if storeReturn
		.word 0x02010000
	.else
		.word 0x02000000
	.endif
	.word segAddr
.endmacro
.macro .gs_branch, storeReturn, segAddr
	.gs_02 storeReturn, segAddr
.endmacro

// ******** Cmd 03: Return from Branch ******** //
.macro .gs_03
	.word 0x03000000
.endmacro
.macro .gs_endbranch
	.gs_03 
.endmacro

// ******** Cmd 04: Open Node ******** //
.macro .gs_04
	.word 0x04000000
.endmacro
.macro .gs_node
	.gs_04
.endmacro

// ******** Cmd 05: Close Node ******** //
.macro .gs_05
	.word 0x05000000
.endmacro
.macro .gs_endnode
	.gs_05
.endmacro

// ******** Cmd 06: ??? ******** //
.macro .gs_06
.endmacro
// ******** Cmd 07: ??? ******** //
.macro .gs_07
.endmacro

// ******** Cmd 08: Set Screen Render Area ******** //
.macro .gs_08, a, x, y, w, h
	.byte 0x08, 0x00, 0x00, a
	.halfword x, y, w, h
.endmacro
.macro .gs_startLevelLayout, x, y, w, h
	.gs_08 0x0A, x, y, w, h
.endmacro

// ******** Cmd 09: ??? ******** //
.macro .gs_09, a
	.byte 0x09, 0x00, 0x00, a
.endmacro

// ******** Cmd 0A: Set Camera Frustum ******** //
.macro .gs_0a, useASM, fov, near, far, asmAddr
	.byte 0x0A, useASM
	.halfword fov, near, far
	.if useASM
		.word asmAddr
	.endif
.endmacro
.macro .gs_setCameraFrustum, near, far
	.gs_0a TRUE, 0x2D, near, far, 0x8029AA3C
.endmacro
.macro .gs_setCameraFrustumAdv, useASM, fov, near, far, asmAddr
	.gs_0a useASM, fov, near, far, asmAddr
.endmacro

// ******** Cmd 0B: Start Geometry Layout ******** //
.macro .gs_0b
	.word 0x0B000000
.endmacro
.macro .gs_startLayout
	.gs_0b
.endmacro

// ******** Cmd 0C: Enable/Disable Z-Buffer ******** //
.macro .gs_0c, enable
	.if enable
		.word 0x0C010000
	.else
		.word 0x0C000000
	.endif
.endmacro
.macro .gs_enableZBuffer, enable
	.gs_0c enable
.endmacro

// ******** Cmd 0D: Set Render Range ******** //
.macro .gs_0d, minDist, maxDist
	.word 0x0D000000
	.halfword minDist, maxDist
.endmacro
.macro .gs_setRenderRange, minDist, maxDist
	.gs_0d minDist, maxDist
.endmacro

// ******** Cmd 0E: Switch Case ******** //
.macro .gs_0e, amount, asmAddr
	.byte 0x0E, 0x00, 0x00, amount
	.word asmAddr
.endmacro
.macro .gs_switchCase, amount, asmAddr
	.gs_0e amount, asmAddr
.endmacro

// ******** Cmd 0F: ??? ******** //
.macro .gs_0f, t, x, y, z, u, v, w, asmAddr
	.halfword 0x0F00, t, x, y, z, u, v, w
	.word asmAddr
.endmacro

// ******** Cmd 10: Translate and Rotate ******** //
.macro .gs_10, a, b, x, y, z, rx, ry, rz
	.byte 0x10, a
	.halfword b, x, y, z, rx, ry, rz
.endmacro
.macro .gs_translate, x, y, z
	.gs_10, 0, 0, x, y, z, 0, 0, 0
.endmacro
.macro .gs_rotate, rx, ry, rz
	.gs_10, 0, 0, 0, 0, 0, rx, ry, rz
.endmacro
.macro .gs_translateRotate, x, y, z, rx, ry, rz
	.gs_10, 0, 0, x, y, z, rx, ry, rz
.endmacro

// ******** Cmd 11: ??? ******** //
.macro .gs_11
.endmacro

// ******** Cmd 12: ??? ******** //
.macro .gs_12
.endmacro

// ******** Cmd 13: Load Display List with position offset ******** //
.macro .gs_13, layer, segAddr, x, y, z
	.byte 0x13, layer
	.halfword x, y, z
	.word segAddr
.endmacro
.macro .gs_loadDLAdv, layer, segAddr, x, y, z
	.gs_13 layer, segAddr, x, y, z
.endmacro

// ******** Cmd 14: Billboard Model ******** //
.macro .gs_14
	.word 0x14000000, 0x00000000
.endmacro
.macro .gs_billboard
	.gs_14
.endmacro

// ******** Cmd 15: Load Display List ******** //
.macro .gs_15, layer, segAddr
	.byte 0x15, layer, 0x00, 0x00
	.word segAddr
.endmacro
.macro .gs_loadDL, layer, segAddr
	.gs_15 layer, segAddr
.endmacro

// ******** Cmd 16: Start Geo Layout with Shadow ******** //
.macro .gs_16, type, trans, scale
	.byte 0x16, 0x00, 0x00, type, 0x00, trans
	.halfword scale
.endmacro
.macro .gs_startLayoutWithShadow, type, trans, scale
	.gs_16 type, trans, scale
.endmacro

// ******** Cmd 17: Set Up Object Rendering? ******** //
.macro .gs_17
	.word 0x17000000
.endmacro
.macro .gs_load3dObjects
	.gs_17
.endmacro

// ******** Cmd 18: Load Polygons ASM ******** //
.macro .gs_18, asmAddr
	.word 0x18000000, asmAddr
.endmacro
.macro .gs_loadASM, asmAddr
	.gs_18 asmAddr
.endmacro

// ******** Cmd 19: Set Background ******** //
.macro .gs_19, id, asmAddr
	.halfword 0x1900, id
	.word asmAddr
.endmacro
.macro .gs_setBackgroundTexture, id, asmAddr
	.gs_19 id, asmAddr
.endmacro
.macro .gs_setBackgroundColor, color
	.gs_19 color, 0x00
.endmacro

// ******** Cmd 1A: No Operation ******** //
.macro .gs_1a
	.word 0x00, 0x00
.endmacro
.macro .gs_nop
	.gs_1a
.endmacro

// ******** Cmd 1B: ??? ******** //
.macro .gs_1b
.endmacro

// ******** Cmd 1C: ??? ******** //
.macro .gs_1c
.endmacro

// ******** Cmd 1D: Scale Model ******** //
.macro .gs_1d, a, b, scale, c
	.byte 0x1D, ((a & 0x0F) << 4) | (b & 0x0F)
	.halfword 0x0000
	.word scale
	.if a
		.word c
	.endif
.endmacro
.macro .gs_scale, scale
	.gs_1d 0, 0, scale, 0
.endmacro
.macro .gs_scale_p, percent
	.gs_1d 0, 0, int(percent*655.36), 0
.endmacro

// ******** Cmd 1E: No Operation ******** //
.macro .gs_1e
	.word 0x00, 0x00
.endmacro
.macro .gs_nop8
	.gs_1e
.endmacro

// ******** Cmd 1F: No Operation ******** //
.macro .gs_1f
	.word 0x00, 0x00, 0x00, 0x00
.endmacro
.macro .gs_nop16
	.gs_1f
.endmacro

// ******** Cmd 20: Start Geo Layout with Render Area ******** //
.macro .gs_20, renderArea
	.halfword 0x2000, renderArea
.endmacro
.macro .gs_startLayoutWithRenderArea, renderArea
	.gs_20 renderArea
.endmacro
