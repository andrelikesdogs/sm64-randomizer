.defineLabel RGBA16_RED, 0xF801
.defineLabel RGBA16_GREEN, 0x07C1
.defineLabel RGBA16_BLUE, 0x003F
.defineLabel RGBA16_BLACK, 0x0001
.defineLabel RGBA16_MIDGRAY, 0x39CF
.defineLabel RGBA16_WHITE, 0xFFFF
.defineLabel RGBA16_TRANSPARENT, 0x0000

.macro .CI4_palette, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16 
	.halfword c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16
.endmacro

