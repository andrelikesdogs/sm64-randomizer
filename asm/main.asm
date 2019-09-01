SAG_FILEPATH equ "/Users/andremeyer/Documents/Own/mario-64-rom-hacking/sm64-randomizer/Super Mario 64.ext.z64"
SAG_FILEPOS equ 0x0
SAG_IMPORTPATH equ "/Users/andremeyer/Documents/Own/mario-64-rom-hacking/sm64-randomizer/Super Mario 64.ext.z64"

.Open SAG_IMPORTPATH, SAG_FILEPOS

.n64

.include "sm64mlib/sm64mlib.asm"
.include "patch_credits.asm"

.Close
