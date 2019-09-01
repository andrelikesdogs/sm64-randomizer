.defineLabel F3D_GEOMODE_ZBUFFER,			0x00000001
.defineLabel F3D_GEOMODE_USE_SHADING,		0x00000004
.defineLabel F3D_GEOMODE_SMOOTH_SHADING,	0x00000200
.defineLabel F3D_GEOMODE_CULLTRI_FRONT,		0x00001000
.defineLabel F3D_GEOMODE_CULLTRI_BACK,		0x00002000
.defineLabel F3D_GEOMODE_FOG,				0x00010000
.defineLabel F3D_GEOMODE_LIGHTING,			0x00020000
.defineLabel F3D_GEOMODE_TEXGEN,			0x00040000
.defineLabel F3D_GEOMODE_TEXGEN_LINEAR,		0x00080000

.defineLabel F3D_TEXFMT_RGBA,	0x00
.defineLabel F3D_TEXFMT_YUV,	0x01
.defineLabel F3D_TEXFMT_CI,		0x02
.defineLabel F3D_TEXFMT_IA,		0x03
.defineLabel F3D_TEXFMT_I,		0x04

.defineLabel F3D_TEXSIZE_4b,	0x00
.defineLabel F3D_TEXSIZE_8b,	0x01
.defineLabel F3D_TEXSIZE_16b,	0x02
.defineLabel F3D_TEXSIZE_32b,	0x03

/*
Vertex Structure (from cpuHacka101's notes)

xxxxyyyyzzzz0000uuuuvvvvrrggbbaa
-xxxx: X Position of vertex
-yyyy: Y Position of vertex
-zzzz: Z Position of vertex
-uuuu: X texture stretch along vertex
-vvvv: Y texture stretch along vertex
-rr: Red channel of vertex, used for vertex colors and/or normals
-gg: Green channel of vertex, used for vertex colors and/or normals
-bb: Blue channel of vertex, used for vertex colors and/or normals
-aa: Alpha channel of vertex, used in vertex colors, ignored in vertex normals
*/
.macro .f3d_vertex, x, y, z, u, v, nx_r, ny_g, nz_b, alpha
	.halfword x, y, z, 0x0000, u, v
	.byte nx_r, ny_g, nz_b, alpha
.endmacro

// Generic Fast3D macro
.macro .f3d, upperWord, lowerWord
	.word upperWord, lowerWord
.endmacro

// Generic Fast3D macro
.macro .f3d_dw, value
	.doubleword value
.endmacro

// ******** Cmd 00: No Operation ******** //
.macro .f3d_00
	.f3d_dw 0x0000000000000000
.endmacro
.macro .f3d_nop
	.f3d_00
.endmacro

// ******** Cmd 01: G_MTX ******** //
.macro .f3d_01, params, segAddr
	.byte 0x01, params, 0x00, 0x00
	.word segAddr
.endmacro
.macro .f3d_mtx, params, segAddr
	.f3d_01 params, segAddr
.endmacro

// ******** Cmd 03: F3D_MOVEMEM ******** //
.macro .f3d_03, size, index, offset, segAddr
	.byte 0x03, size, index, offset
	.word segAddr
.endmacro
.macro .f3d_movemem, size, index, offset, segAddr
	.f3d_03 size, index, offset, segAddr
.endmacro

// ******** Cmd 04: F3D_VTX ******** //
.macro .f3d_04, amount, index, segAddr
	.byte 0x04, (((amount - 1) << 4) | index) & 0xFF
	.halfword (amount * 0x10)
	.word segAddr
.endmacro
.macro .f3d_vtx, amount, index, segAddr
	.f3d_04 amount, index, segAddr
.endmacro

// ******** Cmd 06: F3D_DL ******** //
; dontStoreAddress is either 0x00 (false) or 0x01 (true)
; see: http://wiki.cloudmodding.com/oot/F3DZEX/Opcode_Details#0xDE_.E2.80.94_G_DL
.macro .f3d_06, dontStoreAddress, segAddr
	.byte 0x06, dontStoreAddress, 0x00, 0x00
	.word segAddr
.endmacro
.macro .f3d_dl, segAddr
	.f3d_06 0x00, segAddr
.endmacro
// Branch to list and don't store address
.macro .f3d_branch, segAddr
	.f3d_06 0x01, segAddr
.endmacro

// ******** Cmd B6: F3D_CLEARGEOMETRYMODE ******** //
.macro .f3d_b6, parameters
	.f3d 0xB6000000, parameters
.endmacro
.macro .f3d_clearGeometryMode, parameters
	.f3d_b6 parameters
.endmacro

// ******** Cmd B7: F3D_SETGEOMETRYMODE ******** //
.macro .f3d_b7, parameters
	.f3d 0xB7000000, parameters
.endmacro
.macro .f3d_setGeometryMode, parameters
	.f3d_b7 parameters
.endmacro

// ******** Cmd B8: F3D_ENDDL ******** //
.macro .f3d_b8
	.f3d_dw 0xB800000000000000
.endmacro
.macro .f3d_enddl
	.f3d_b8
.endmacro

// ******** Cmd BB: G_TEXTURE ******** //
.macro .f3d_bb, enable, scaleS_f, scaleT_f, level, tile 
	.byte 0xBB, 0x00, (((level & 0x7) << 3) | (tile & 0x7)), enable
	.halfword int(float(scaleS_f) * 0xFFFF), int(float(scaleT_f) * 0xFFFF)
.endmacro
.macro .f3d_texture, enable, scaleS_f, scaleT_f, level, tile 
	.f3d_bb enable, scaleS_f, scaleT_f, level, tile 
.endmacro

// ******** Cmd BF: G_TRI1 ******** //
.macro .f3d_bf, v0, v1, v2
	.word 0xBF000000
	.byte 0x00, v0*0x0A, v1*0x0A, v2*0x0A
.endmacro
.macro .f3d_tri1, v0, v1, v2
	.f3d_bf v0, v1, v2
.endmacro


// ******** Cmd E6: G_RDPLOADSYNC ******** //
.macro .f3d_e6
	.f3d_dw 0xE600000000000000
.endmacro
.macro .f3d_rdpLoadSync
	.f3d_e6
.endmacro

// ******** Cmd E7: G_RDPPIPESYNC ******** //
.macro .f3d_e7
	.f3d_dw 0xE700000000000000
.endmacro
.macro .f3d_rdpPipeSync
	.f3d_e7
.endmacro

// ******** Cmd E8: G_RDPTILESYNC ******** //
.macro .f3d_e8
	.f3d_dw 0xE800000000000000
.endmacro
.macro .f3d_rdpTileSync
	.f3d_e8
.endmacro

// ******** Cmd E8: G_RDPFULLSYNC ******** //
.macro .f3d_e9
	.f3d_dw 0xE900000000000000
.endmacro
.macro .f3d_rdpFullSync
	.f3d_e9
.endmacro

// ******** Cmd F0: G_LOADTLUT ******** //
.macro .f3d_f0, tile, num_colors
	.word 0xF0000000
	.byte tile
	.halfword (((num_colors-1) & 0x3FF) << 6)
	.byte 0x00
.endmacro
.macro .f3d_loadTLUT, tile, num_colors
	.f3d_f0 tile, num_colors
.endmacro

// ******** Cmd F2: G_SETTILESIZE ******** //
.macro .f3d_f2, width, height
	.word 0xF2000000
	.word ((width-1) << 14) | ((height-1) << 2)
.endmacro
.macro .f3d_setTileSize, width, height
	.f3d_f2 width, height
.endmacro

// ******** Cmd F3: G_LOADBLOCK ******** //
.macro .f3d_f3, tile, uls, ult, texels, dxt
	.byte 0xF3, (uls >> 4) & 0xFF, (uls & 0xF) | (ult >> 8), ult & 0xFF
	.byte tile, ((texels - 1) >> 4) & 0xFF, (((texels - 1) & 0xF) << 4) | (dxt >> 8), dxt & 0xFF
.endmacro
.macro .f3d_loadBlock, tile, uls, ult, texels, dxt
	.f3d_f3 tile, uls, ult, texels, dxt
.endmacro

// ******** Cmd F5: G_SETTILE ******** //
.macro .f3d_f5, fmt, siz, line, tmem, tile, pal, cmT, maskT, shiftT, cmS, maskS, shiftS
	.byte 0xF5
	.byte ((fmt & 7) << 5) | ((siz & 3) << 3) | (line >> 7)
	.byte ((line & 0x7F) << 1) | ((tmem >> 8) & 1)
	.byte (tmem & 0xFF)
	.byte (tile & 7)
	.byte ((pal & 0xF) << 4) | ((cmT & 0x3) << 2) | ((maskT & 0xF) >> 2)
	.byte ((maskT & 0x3) << 6) | ((shiftT & 0xF) << 2) | (cmS & 0x3)
	.byte ((maskS & 0xF) << 4) | (shiftS & 0xF)
.endmacro
.macro .f3d_setTile, fmt, siz, line, tmem, tile, pal, cmT, maskT, shiftT, cmS, maskS, shiftS
	.f3d_f5 fmt, siz, line, tmem, tile, pal, cmT, maskT, shiftT, cmS, maskS, shiftS
.endmacro

// ******** Cmd F6: G_FILLRECT ******** //
.macro .f3d_f6, lrx, lry, ulx, uly
	.word (0xF6 << 24) | (lrx << 12) | lry
	.word (ulx << 12) | uly
.endmacro
.macro .f3d_fillRect, lrx, lry, ulx, uly
	.f3d_f6 lrx, lry, ulx, uly
.endmacro

// ******** Cmd F7: G_SETFILLCOLOR ******** //
.macro .f3d_f7, fillValue
	.f3d 0xF7000000, fillValue
.endmacro
.macro .f3d_setFillColor, fillValue
	.f3d_f7 fillValue
.endmacro

// ******** Cmd F8: G_SETFOGCOLOR ******** //
.macro .f3d_f8, red, green, blue, alpha
	.word 0xF8000000
	.byte red, green, blue, alpha
.endmacro
.macro .f3d_setFogColor, red, green, blue, alpha
	.f3d_f8 red, green, blue, alpha
.endmacro

// ******** Cmd FB: G_SETENVCOLOR ******** //
.macro .f3d_fb, red, green, blue, alpha
	.word 0xFB000000
	.byte red, green, blue, alpha
.endmacro
.macro .f3d_setEnvColor, red, green, blue, alpha
	.f3d_fb red, green, blue, alpha
.endmacro

// ******** Cmd FC: G_SETCOMBINE ******** //
.macro .f3d_fc, a0, c0, Aa0, Ac0, a1, c1, b0, b1, Aa1, Ac1, d0, Ab0, Ad0, d1, Ab1, Ad1
	.byte 0xFC
	.byte ((a0 & 0xF) << 4) | ((c0 & 0x1F) >> 1)
	.byte ((c0 & 0x1) << 7) | ((Aa0 & 0x7) << 4) | ((Ac0 & 0x7) << 1) | ((a1 & 0xF) >> 3)
	.byte ((a1 & 0xF) << 5) | (c1 & 0x1F)
	.byte ((b0 & 0xF) << 4) | (b1 & 0xF)
	.byte ((Aa1 & 0x7) << 5) | ((Ac1 & 0x7) << 2) | ((d0 & 0x7) >> 1)
	.byte ((d0 & 0x07) << 7) | ((Ab0 & 0x7) << 4) | ((Ad0 & 0x7) << 1) | ((d1 & 0x7) >> 2)
	.byte ((d1 & 0x7) << 6) | ((Ab1 & 0x7) << 3) | (Ad1 & 0x7)
.endmacro
.macro .f3d_setCombineLERP, a0, c0, Aa0, Ac0, a1, c1, b0, b1, Aa1, Ac1, d0, Ab0, Ad0, d1, Ab1, Ad1
	.f3d_fc a0, c0, Aa0, Ac0, a1, c1, b0, b1, Aa1, Ac1, d0, Ab0, Ad0, d1, Ab1, Ad1
.endmacro

.macro .f3d_setCombine_Tex_Solid_NoFog
	.f3d_dw 0xFC127E24FFFFF9FC
.endmacro
.macro .f3d_setCombine_Tex_Alpha_NoFog
	.f3d_dw 0xFC121824FF33FFFF
.endmacro
.macro .f3d_setCombine_Tex_Solid_Fog
	.f3d_dw 0xFC127FFFFFFFF838
.endmacro
.macro .f3d_setCombine_Tex_Alpha_Fog
	.f3d_dw 0xFCFFFFFFFFFCF238
.endmacro
.macro .f3d_setCombine_Tex_Trans
	.f3d_dw 0xFC122E24FFFFFBFD
.endmacro
.macro .f3d_setCombine_Color_Solid
	.f3d_dw 0xFCFFFFFFFFFE7B3D
.endmacro
.macro .f3d_setCombine_Color_Trans
	.f3d_dw 0xFCFFFFFFFFFEFBFD
.endmacro

// ******** Cmd FD: G_SETTIMG ******** //
.macro .f3d_fd, fmt, siz, segAddr
	.byte 0xFD
	.byte ((fmt & 7) << 5) | ((siz & 3) << 3)
	.halfword 0x0000
	.word segAddr
.endmacro
.macro .f3d_setTImg, fmt, siz, segAddr
	.f3d_fd fmt, siz, segAddr
.endmacro









