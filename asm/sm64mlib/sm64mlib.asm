.defineLabel SM64MLIB_VERSION_MAJOR, 0
.defineLabel SM64MLIB_VERSION_MINOR, 2

// Pointers/Structures
.defineLabel SM64_CURR_OBJ_PTR, 	0x80361160
.defineLabel SM64_FIRST_OBJ_PTR, 	0x8033D488
.defineLabel SM64_MARIO_STRUCT, 	0x8033B170
.defineLabel SM64_MARIO_OBJ_PTR, 	0x80361158
.defineLabel SM64_LEVEL_STRUCT, 	0x8033B90C
.defineLabel SM64_SEGMENT_TABLE,	0x8033B400
.defineLabel SM64_EEPROM,			0x80207700

// Variables
.defineLabel SM64_MARIO_ACTION,		0x8033B17C ; (word) current action
.defineLabel SM64_MARIO_PRV_ACTION,	0x8033B180 ; (word) previous action
.defineLabel SM64_MARIO_STARS,		0x8033B264 ; (halfword) displayed star count
.defineLabel SM64_MARIO_COINS,		0x8033B218 ; (halfword) coin count
.defineLabel SM64_MARIO_LIVES,		0x8033B21D ; (byte) life count
.defineLabel SM64_MARIO_POWER,		0x8033B21E ; (halfword) power count
.defineLabel SM64_CURR_FILE,		0x8032DDF4 ; (halfword) current File ID (File A = 1, File B = 2, etc.)
.defineLabel SM64_CURR_LEVEL,		0x8032DDF8 ; (halfword) current Level ID
.defineLabel SM64_CURR_COURSE,		0x8033BAC6 ; (halfword) current Course ID
.defineLabel SM64_CURR_ACT,			0x80331620 ; (byte) current Act ID
// NOTE: Course IDs & Level IDs are two completely seperate things!

// Analog stick values for controllers 1 & 2
.defineLabel ANALOG1_XAXIS, 0x8033AF90 ; (signed halfword) Controller 1 Right/Left
.defineLabel ANALOG1_YAXIS, 0x8033AF92 ; (signed halfword) Controller 1 Up/Down
.defineLabel ANALOG2_XAXIS, 0x8033AFBC ; (signed halfword) Controller 2 Right/Left
.defineLabel ANALOG2_YAXIS, 0x8033AFBE ; (signed halfword) Controller 2 Up/Down

.defineLabel ANALOG_SUG_MINLIMIT, 0x08 ; Suggested minimum value that analog should be tested for
.defineLabel ANALOG_SUG_MAXLIMIT, 0x48 ; Suggested maximum value that analog should be tested for
// NOTE: You need to add a negative symbol if testing Left or Down direction(s)

// N64 Buttons
.defineLabel BUTTON_CRIGHT, 0x01
.defineLabel BUTTON_CLEFT, 	0x02
.defineLabel BUTTON_CDOWN, 	0x04
.defineLabel BUTTON_CUP, 	0x08
.defineLabel BUTTON_R, 		0x10
.defineLabel BUTTON_L, 		0x20
.defineLabel BUTTON_DRIGHT, 0x100
.defineLabel BUTTON_DLEFT, 	0x200
.defineLabel BUTTON_DDOWN, 	0x400
.defineLabel BUTTON_DUP, 	0x800
.defineLabel BUTTON_START, 	0x1000
.defineLabel BUTTON_Z, 		0x2000
.defineLabel BUTTON_B, 		0x4000
.defineLabel BUTTON_A, 		0x8000

.defineLabel BUTTON_PRESSED, 0x00 ; Input will only occur once, even if the button is held down
.defineLabel BUTTON_HELD,	 0x01 ; Input will keep occuring as long as the button is held down

// Boolean values
.ifndef FALSE
	.defineLabel FALSE, 0x00
.endif
.ifndef TRUE
	.defineLabel TRUE, 	0x01
.endif

// Mario actions
.defineLabel MARIO_ACTION_MOVING,	0x04000440 
.defineLabel MARIO_ACTION_JUMP,		0x03000880 
.defineLabel MARIO_ACTION_DUBJUMP,	0x03000881 
.defineLabel MARIO_ACTION_TRIJUMP,	0x03000882 
.defineLabel MARIO_ACTION_GROUNDP,	0x008008A9 
.defineLabel MARIO_ACTION_CROUCH,  	0x0C008220 
.defineLabel MARIO_ACTION_IDLE, 	0x0C400201
.defineLabel MARIO_ACTION_YAWN, 	0x0C000202
.defineLabel MARIO_ACTION_SLEEP, 	0x0C000203

// Allows the user to write the generic sm64 text for
// menus without needing a tool to convert ascii text
.macro .sm64text, str
	.loadtable "./sm64mlib/sm64text.tbl"
	.string str
.endmacro

.macro .sm64mlib_requireVersion, major, minor
	.if SM64MLIB_VERSION_MAJOR < major
		.error "ERROR: You are using an out of data version of sm64mlib!"
		.error "Current Version = " + SM64MLIB_VERSION_MAJOR + "." \
		+ SM64MLIB_VERSION_MINOR +", Required Version = " + major + "." + minor
	.elseif SM64MLIB_VERSION_MINOR < minor
		.error "ERROR: You are using an out of data version of sm64mlib!"
		.error "Current Version = " + SM64MLIB_VERSION_MAJOR + "." \
		+ SM64MLIB_VERSION_MINOR +", Required Version = "+ major +"."+ minor
	.endif
.endmacro

.relativeinclude on
	.include "sm64check.asm"
	.include "levelscripts.asm"
	.include "geoscripts.asm"
	.include "fast3dscripts.asm"
	.include "behscripts.asm"
	.include "sm64functions.asm"
	.include "colors.asm"
.relativeinclude off
