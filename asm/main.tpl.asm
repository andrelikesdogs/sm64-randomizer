SAG_FILEPATH equ "#ROM_FILE"
SAG_FILEPOS equ #ROM_POS
SAG_IMPORTPATH equ "#ROM_FILE"

.Open SAG_IMPORTPATH, SAG_FILEPOS

.n64

.include "sm64mlib/sm64mlib.asm"
.include "patch_credits.asm"

.Close