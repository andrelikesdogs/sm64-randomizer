.if readu8(SAG_FILEPATH, 0) != 0x80
.error "ERROR: Sorry, only big-endian ROMs (.z64) are supported."
.elseif readu8(SAG_FILEPATH, 1) != 0x37
.error "ERROR: Sorry, only big-endian ROMs (.z64) are supported."
.elseif readu8(SAG_FILEPATH, 2) != 0x12
.error "ERROR: Sorry, only big-endian ROMs (.z64) are supported."
.elseif readu8(SAG_FILEPATH, 3) != 0x40
.error "ERROR: Sorry, only big-endian ROMs (.z64) are supported."
.else ; Confirmed that ROM is big-endian.
	// Check that the ROM is from North America.
	.if readu8(SAG_FILEPATH, 0x3E) == 0x50
	.error "ERROR: Sorry, the european ROM is not supported."
	.elseif readu8(SAG_FILEPATH, 0x3E) == 0x4A
	.error "ERROR: Sorry, the japanese ROM is not supported."
	.elseif readu8(SAG_FILEPATH, 0x3E) != 0x45
	.error "ERROR: Sorry, your weird ROM is not supported."
	.endif
.endif

