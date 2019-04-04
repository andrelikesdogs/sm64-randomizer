from Level import Level

LVL_MAIN=Level(0x108A10,	0x108A40, None, "Main Entry")
LVL_GAME_OVER=Level(0x269EA0, 0x26A3A0, None, "Game Over")
LVL_MAIN_MENU=Level(0x2A6120, 0x2A65B0, 0x26, "Main Menu")
LVL_MAIN_SCR=Level(0x2ABCA0, 0x2AC6B0, None, "Main Scripts")

LVL_CASTLE_GROUNDS=Level(0x4545E0, 0x454E00, 0x10, "Castle Grounds") # 0
LVL_CASTLE_INSIDE=Level(0x3CF0D0, 0x3D0DC0, 0x06, "Castle Inside") # 0
LVL_CASTLE_COURTYARD=Level(0x4AF670, 0x4AF930, 0x1A, "Castle Courtyard") # 0

LVL_BOB=Level(0x405A60, 0x405FB0, 0x09, "Bob-omb Battlefield") # 1
LVL_WF=Level(0x49DA50, 0x49E710, 0x18, "Whomp's Fortress") # 2
LVL_JRB=Level(0x423B20, 0x4246D0, 0x0C, "Jolly Roger Bay") # 3
LVL_CCM=Level(0x395C90, 0x396340, 0x05, "Cool, Cool Mountain") # 4
LVL_BBH=Level(0x3828C0, 0x383950, 0x04, "Big Boo's Haunt") # 5
LVL_HMC=Level(0x3E6A00, 0x3E76B0, 0x07, "Hazy Maze Cave") # 6
LVL_LLL=Level(0x48C9B0, 0x48D930, 0x16, "Lethal Lava Land") # 7
LVL_SSL=Level(0x3FB990, 0x3FC2B0, 0x08, "Shifting Sand Land") # 8
LVL_DDD=Level(0x495A60, 0x496090, 0x17, "Dire, Dire Docks") # 9
LVL_SL=Level(0x40E840, 0x40ED70, 0x0A, "Snowman's Land") # 10
LVL_WDW=Level(0x419F90, 0x41A760, 0x0B, "Wet-Dry World") # 11
LVL_TTM=Level(0x4EB1F0, 0x4EC000, 0x24, "Tall, Tall Mountain") # 12
LVL_THI=Level(0x42C6E0, 0x42CF20, 0x0D, "Tiny-Huge Island") # 13
LVL_TTC=Level(0x437400, 0x437870, 0x0E, "Tick Tock Clock") # 14
LVL_RR=Level(0x44A140, 0x44ABC0, 0x1F, "Rainbow Ride") # 15

LVL_VANISH_CAP=Level(0x461220, 0x4614D0, 0x12, "Vanish Cap") # 22
LVL_METAL_CAP=Level(0x4BE9E0, 0x4BEC30, 0x1C, "Metal Cap") # 20
LVL_WING_CAP=Level(0x4C2700, 0x4C2920, 0x1D, "Wing Cap") # 21

LVL_BOWSER_1=Level(0x45BF60, 0x45C600, 0x11, "Bowser in the Dark World") # Bowser 1 "BIDW", # 16
LVL_BOWSER_2=Level(0x46A840, 0x46B090, 0x13, "Bowser in the Fire Sea") # Bowser 2 "BIFS", # 17
LVL_BOWSER_3= Level(0x477D00, 0x4784A0, 0x15, "Bowser in the Sky") # Bowser 3 "BITS", # 18

LVL_SECRET_AQUARIUM=Level(0x46C1A0, 0x46C3A0, 0x14, "Secret Aquarium") # 24
LVL_SECRET_PEACH_SLIDE=Level(0x4B7F10, 0x4B80D0, 0x1B, "Secret Slide") # 19
LVL_SECRET_RAINBOW=Level(0x4CD930, 0x4CDBD0, None, "Over the Rainbow") # 23

""" All courses, mostly in order """
ALL_LEVELS = [
  # Special
  LVL_MAIN,
  LVL_GAME_OVER,
  LVL_MAIN_MENU,
  LVL_MAIN_SCR,

  # Castle
  LVL_CASTLE_GROUNDS,
  LVL_CASTLE_INSIDE,
  LVL_CASTLE_COURTYARD,

  # Main Levels
  LVL_BOB,
  LVL_WF,
  LVL_JRB,
  LVL_CCM,
  LVL_BBH,
  LVL_HMC,
  LVL_LLL,
  LVL_SSL,
  LVL_DDD,
  LVL_SL,
  LVL_WDW,
  LVL_TTM,
  LVL_THI,
  LVL_TTC,
  LVL_RR,
  
  # Cap Levels
  LVL_VANISH_CAP,
  LVL_METAL_CAP,
  LVL_WING_CAP,

  # Bowser Levels
  LVL_BOWSER_1,
  LVL_BOWSER_2, 
  LVL_BOWSER_3,

  # Secrets
  LVL_SECRET_AQUARIUM,
  LVL_SECRET_PEACH_SLIDE,
  LVL_SECRET_RAINBOW,
]

""" Castle Levels, inside, outside and courtyard """
CASTLE_LEVELS=[LVL_CASTLE_GROUNDS, LVL_CASTLE_INSIDE, LVL_CASTLE_COURTYARD]

""" Mission Levels from BOB to TTC + RR """
MISSION_LEVELS=[LVL_BOB, LVL_WF, LVL_JRB, LVL_CCM, LVL_BBH, LVL_HMC, LVL_LLL, LVL_SSL, LVL_DDD, LVL_SL, LVL_WDW, LVL_TTM, LVL_THI, LVL_TTC, LVL_RR]

""" Bowser levels (before fight) """
BOWSER_STAGES=[LVL_BOWSER_1, LVL_BOWSER_2, LVL_BOWSER_3]

""" Mapping LEVEL-ID -> LEVEL """
LEVEL_ID_MAPPING={level.level_id: level for level in ALL_LEVELS}

""" Names for all LEVEL segment functions in SM64 """
LEVEL_SCRIPT_FUNCS = {
  0x00: "LOAD_RAW_DATA_AND_JUMP",
  0x01: "LOAD_RAW_DATA_AND_JUMP_PLUS_CALL",
  0x02: "END_LEVEL_DATA",
  0x03: "DELAY_FRAMES",
  0x04: "DELAY_FRAMES_2",
  0x05: "JUMP_TO_ADDRESS",
  0x06: "PUSH",
  0x07: "POP",
  0x0A: "PUSH_SCRIPT_0X",
  0x0B: "CONDITIONAL_POP",
  0x0C: "CONDITIONAL_JUMP",
  0x0D: "CONDITIONAL_PUSH",
  0x0E: "CONDITIONAL_SKIP",
  0x0F: "SKIP_NEXT",
  0x10: "NOP",
  0x11: "SET_ACCU_FROM_ASM",
  0x12: "SET_ACCU_FROM_ROUTINE",
  0x13: "SET_ACCU",
  0x14: "PUSH_POOL",
  0x15: "POP_POOL",
  0x16: "ROM_TO_RAM",
  0x17: "ROM_TO_SEGMENT",
  0x18: "MIO0_DECOMPRESS",
  0x19: "CREATE_DEMO",
  0x1A: "MIO0_DECOMPRESS_TEXTURES",
  0x1B: "START_LOAD_SEQ",
  0x1C: "LEVEL_AND_MEMORY_CLEANUP",
  0x1D: "END_LOAD_SEQ",
  0x1E: "ALLOCATE_LEVEL_DATA_FROM_POOL",
  0x1F: "START_AREA",
  0x20: "END_AREA",
  0x21: "LOAD_POLY_WITHOUT_GEO",
  0x22: "LOAD_POLY_WITH_GEO",
  0x24: "PLACE_OBJECT",
  0x25: "LOAD_MARIO",
  0x26: "CONNECT_WARPS",
  0x27: "CONNECT_PAINTING",
  0x28: "CONNECT_INSTANT_WARP",
  0x2E: "LOAD_COLLISION",
  0x2F: "SETUP_RENDER_ROOM",
  0x30: "SHOW_DIALOG",
  0x31: "SET_DEFAULT_TERRAIN",
  0x33: "FADE_COLOR",
  0x36: "SET_MUSIC",
  0x37: "SET_MUSIC_SPECIAL",
  0x39: "PLACE_MACRO_OBJECTS",
  0x3B: "PLACE_JET_STREAM",
}

SONG_NAMES = [
  "No Music",
  "End Level",
  "SMB music title",
  "Bob-omb's Battlefield",
  "Inside Castle walls",
  "Dire Dire Docks",
  "Lethal Laval land",
  "Bowser battle",
  "Snow",
  "Slide",
  "Crash",
  "Piranha plant lullaby",
  "Hazy Maze",
  "Star select",
  "Wing cap",
  "Metal cap",
  "Bowser Message",
  "Bowser course",
  "Star catch",
  "Ghost Merry-go-round",
  "Start and End Race with Koopa the Quick",
  "Star appears",
  "Boss fight",
  "Take a Key",
  "Looping stairs",
  "Crashes",
  "Credits song",
  "Crashes",
  "Toad",
  "Peach message",
  "Intro Castle sequence",
  "End fanfare",
  "End music",
  "Menu",
  "Lakitu",
]

WARP_ID_WIN=0xf0
WARP_ID_LOSE=0xf1
WARP_ID_RECOVER=0xf3

SPECIAL_WARP_IDS = [WARP_ID_WIN, WARP_ID_LOSE, WARP_ID_RECOVER]
