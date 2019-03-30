from Level import Level

""" All level addresses in SM64 """
LEVEL_POSITIONS = {
  # Special
  "MAIN": Level(0x108A10,	0x108A40, "Main Entry"),
  "GAME_OVER": Level(0x269EA0, 0x26A3A0, "Game Over"),
  "MAIN_MENU": Level(0x2A6120, 0x2A65B0, "Main Menu"),
  "MAIN_SCRIPTS": Level(0x2ABCA0, 0x2AC6B0, "Main Scripts"),

  # Main Levels
  "BBH": Level(0x3828C0, 0x383950, "Big Boo's Haunt"),
  "BOB": Level(0x405A60, 0x405FB0, "Bob-omb Battlefield"),
  "CCM": Level(0x395C90, 0x396340, "Cool, Cool Mountain"),
  "HMC": Level(0x3E6A00, 0x3E76B0, "Hazy Maze Cave"),
  "SL": Level(0x40E840, 0x40E840, "Big Boo's Haunt"),
  "WDW": Level(0x419F90, 0x41A760, "Wet-Dry World"),
  "WF": Level(0x49DA50, 0x49E710, "Whomp's Fortress"),
  "JRB": Level(0x423B20, 0x4246D0, "Jolly Roger Bay"),
  "THI": Level(0x42C6E0, 0x42CF20, "Tiny-Huge"),
  "TTC": Level(0x437400, 0x437870, "Tick Tock Clock"),
  "RR": Level(0x44A140, 0x44ABC0, "Rainbow Ride"),
  "DDD": Level(0x495A60, 0x496090, "Dire, Dire Docks"),
  "LLL": Level(0x48C9B0, 0x48D930, "Lethal Lava Land"),
  "TTM": Level(0x4EB1F0, 0x4EC000, "Tall, Tall Mountain"),
  "SSL": Level(0x3FB990, 0x3FC2B0, "Shifting Sand Land"),
  "OTR": Level(0x4CD930, 0x4CDBD0, "Over the Rainbow"),
  # Castle
  "CASTLE_GROUNDS": Level(0x4545E0, 0x454E00, "Castle Grounds"),
  "INSIDE_CASTLE": Level(0x3CF0D0, 0x3D0DC0, "Castle Inside"),
  # Cap Levels
  "VANISH_CAP": Level(0x461220, 0x4614D0, "Vanish Cap"),
  "METAL_CAP": Level(0x4BE9E0, 0x4BEC30, "Metal Cap"),
  "WING_CAP": Level(0x4C2700, 0x4C2920, "Wing Cap"),
  # Bowser Levels
  "BIFS": Level(0x46A840, 0x46B090, "Bowser in the Fire Sea"),
  "BITS": Level(0x477D00, 0x4784A0, "Bowser in the Sky"),
  "BIDW": Level(0x45BF60, 0x45C600, "Bowser in the Dark World"),
  # Secrets
  "SECRET_AQUARIUM": Level(0x46C1A0, 0x46C3A0, "Secret Aquarium"),
  "SECRET_SLIDE": Level(0x4B7F10, 0x4B80D0, "Secret Slide"),
}

""" Playable levels in order of the games intended order """
PLAYABLE_LEVELS = [
  LEVEL_POSITIONS['BOB'], # Bob-omb Battlefield
  LEVEL_POSITIONS['WF'], # Whomp's Fortress
  LEVEL_POSITIONS['JRB'], # Jolly Roger Bay
  LEVEL_POSITIONS['CCM'], # Cool, Cool Mountain
  LEVEL_POSITIONS['BBH'], # Big Boo's Haunt
  LEVEL_POSITIONS['HMC'], # Hazy Maze Cave
  LEVEL_POSITIONS['LLL'], # Lethal Lava Land
  LEVEL_POSITIONS['SSL'], # Shifting Sand Land
  LEVEL_POSITIONS['DDD'], # Dire, Dire Docks
  #LEVEL_POSITIONS['SF'], # Snowman's Land
  LEVEL_POSITIONS['WDW'], # Wet-Dry World
  LEVEL_POSITIONS['TTM'], # Tall, Tall Mountain
  LEVEL_POSITIONS['TTC'], # Tick Tock Clock
  LEVEL_POSITIONS['RR'] # Rainbow Ride
]

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