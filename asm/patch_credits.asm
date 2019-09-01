// [ARMIPS 0.9 w/ SM64 Macro Library] "Hello World" Example by Davideesk

.orga 0x861C0 ; Set ROM address
.area 0x90 ; Set data import limit to 0x90 bytes
addiu sp, sp, 0xFFE8
sw ra, 0x14 (sp)

// Prints "Hello World" at the screen pos (0x60, 0x20)
.f_PutMiniString 0x60, 0x60, 0x802CB250

lw ra, 0x14 (sp)
jr ra
addiu sp, sp, 0x18
.endarea

.orga 0x86250 ; 0x802CB250
.sm64text "test"