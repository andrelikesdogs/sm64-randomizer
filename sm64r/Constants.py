from pathlib import Path
import os
import json
import sys

from .Parsers.Level import Level

application_path = None
if getattr(sys, 'frozen', False):
  #print("frozen")
  #print("exec: ", sys.executable)
  #print("argv:", sys.argv[0])
  application_path = os.path.realpath(os.path.dirname(sys.executable))
else:
  #print("unfrozen")
  application_path = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))

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
LVL_RR=Level(0x44A140, 0x44ABC0, 0x0F, "Rainbow Ride") # 15

LVL_VANISH_CAP=Level(0x461220, 0x4614D0, 0x12, "Vanish Cap") # 22
LVL_METAL_CAP=Level(0x4BE9E0, 0x4BEC30, 0x1C, "Metal Cap") # 20
LVL_WING_CAP=Level(0x4C2700, 0x4C2920, 0x1D, "Wing Cap") # 21

LVL_BOWSER_1=Level(0x45BF60, 0x45C600, 0x11, "Bowser in the Dark World") # Bowser 1 "BIDW", # 16
LVL_BOWSER_1_BATTLE=Level(0x4C41C0, 0x4C4320, 0x1E, "Bowser in the Dark World Battle")
LVL_BOWSER_2=Level(0x46A840, 0x46B090, 0x13, "Bowser in the Fire Sea") # Bowser 2 "BIFS", # 17
LVL_BOWSER_2_BATTLE=Level(0x4CE9F0, 0x4CEC00, 0x21, "Bowser in the Fire Sea Battle")
LVL_BOWSER_3=Level(0x477D00, 0x4784A0, 0x15, "Bowser in the Sky") # Bowser 3 "BITS", # 18
LVL_BOWSER_3_BATTLE=Level(0x4D14F0, 0x4D1910, 0x22, "Bowser in the Sky Battle")

LVL_SECRET_AQUARIUM=Level(0x46C1A0, 0x46C3A0, 0x14, "Secret Aquarium") # 24
LVL_SECRET_PEACH_SLIDE=Level(0x4B7F10, 0x4B80D0, 0x1B, "Secret Slide") # 19
LVL_SECRET_RAINBOW=Level(0x4CD930, 0x4CDBD0, 0x1F, "Rainbow Bonus") # 23

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
  LVL_BOWSER_1_BATTLE,
  LVL_BOWSER_2, 
  LVL_BOWSER_2_BATTLE,
  LVL_BOWSER_3,
  LVL_BOWSER_3_BATTLE,


  # Secrets
  LVL_SECRET_AQUARIUM,
  LVL_SECRET_PEACH_SLIDE,
  LVL_SECRET_RAINBOW,
]

LEVEL_SHORT_CODES = {
  LVL_BOB: 'BOB',
  LVL_WF: 'WF',
  LVL_JRB: 'JRB',
  LVL_CCM: 'CCM',
  LVL_BBH: 'BBH',
  LVL_HMC: 'HMC',
  LVL_LLL: 'LLL',
  LVL_SSL: 'SSL',
  LVL_DDD: 'DDD',
  LVL_SL: 'SL',
  LVL_WDW: 'WDW',
  LVL_TTM: 'TTM',
  LVL_THI: 'THI',
  LVL_TTC: 'TTC',
  LVL_RR: 'RR',
  LVL_BOWSER_1: 'BIDW',
  LVL_BOWSER_2: 'BIFS',
  LVL_BOWSER_3: 'BITS',
  LVL_SECRET_AQUARIUM: 'AQUARIUM',
  LVL_SECRET_PEACH_SLIDE: 'SLIDE',
  LVL_SECRET_RAINBOW: 'OTR',
  LVL_VANISH_CAP: 'VC',
  LVL_METAL_CAP: 'MC',
  LVL_WING_CAP: 'WC'
}

""" Castle Levels, inside, outside and courtyard """
CASTLE_LEVELS=[LVL_CASTLE_GROUNDS, LVL_CASTLE_INSIDE, LVL_CASTLE_COURTYARD]

""" Mission Levels from BOB to TTC + RR """
MISSION_LEVELS=[LVL_BOB, LVL_WF, LVL_JRB, LVL_CCM, LVL_BBH, LVL_HMC, LVL_LLL, LVL_SSL, LVL_DDD, LVL_SL, LVL_WDW, LVL_TTM, LVL_THI, LVL_TTC, LVL_RR]

""" Levels to obtain certain caps """
CAP_LEVELS=[LVL_WING_CAP, LVL_METAL_CAP, LVL_VANISH_CAP]

""" Bowser levels (before fight) """
BOWSER_STAGES=[LVL_BOWSER_1, LVL_BOWSER_2, LVL_BOWSER_3]

""" Special Levels that are not "really" playable """
SPECIAL_LEVELS=[LVL_MAIN, LVL_MAIN_MENU, LVL_GAME_OVER, LVL_MAIN_SCR]

""" Mapping LEVEL-ID -> LEVEL """
LEVEL_ID_MAPPING={level.course_id: level for level in ALL_LEVELS}

""" This is to ensure playability with key-doors """
GROUND_FLOOR_LEVELS = [
  LVL_BBH, LVL_BOB, LVL_CCM, LVL_WF, LVL_JRB, LVL_SECRET_AQUARIUM, LVL_SECRET_PEACH_SLIDE, LVL_WING_CAP, LVL_BOWSER_1
]
BASEMENT_LEVELS = [
  LVL_SSL, LVL_DDD, LVL_BOWSER_2, LVL_HMC, LVL_LLL, LVL_VANISH_CAP
]
FIRST_FLOOR_LEVELS = [
  LVL_SL, LVL_THI, LVL_WDW, LVL_TTM 
]
SECOND_FLOOR_LEVELS = [
  LVL_TTC, LVL_SECRET_RAINBOW, LVL_RR, LVL_BOWSER_3
]

LEVEL_ORDER = [
  *GROUND_FLOOR_LEVELS,
  *BASEMENT_LEVELS,
  *FIRST_FLOOR_LEVELS,
  *SECOND_FLOOR_LEVELS
]

GEO_SCRIPT_FUNCS = {
  0x00: "BRANCH_AND_STORE",
  0x01: "TERMINATE_GEO_LAYOUT",
  0x02: "BRANCH_GEO_LAYOUT",
  0x03: "RETURN_FROM_BRANCH",
  0x04: "OPEN_NODE",
  0x05: "CLOSE_NODE",
  0x06: "STORE_CURRENT_NODE_POINTER_TO_TABLE", # unused
  0x07: "SET_OR_AND_NODE_FLAGS", # unused
  0x08: "SET_SCREEN_RENDER_AREA",
  0x09: "SET_BACKGROUND_FRUSTUM_MATRIX",
  0x0A: "SET_CAMERA_FRUSTUM",
  0x0B: "START_GEO_LAYOUT",
  0x0C: "TOGGLE_Z_BUFFER",
  0x0D: "SET_RENDER_RANGE",
  0x0E: "SWITCH",
  0x0F: "UNKNOWN_0x0F",
  0x10: "TRANSLATE_AND_ROTATE",
  0x11: "TRANSLATE_NODE_AND_LOAD_DL_OR_START_GEO_LAYOUT",
  0x12: "ROTATE_NODE_AND_LOAD_DL_OR_START_GEO_LAYOUT",
  0x13: "LOAD_DL_WITH_OFFSET",
  0x14: "BILLBOARD_MODEL_AND_TRANSLATE_AND_LOAD_DL_OR_START_GEO_LAYOUT",
  0x15: "LOAD_DL",
  0x16: "START_GEO_LAYOUT_WITH_SHADOW",
  0x17: "SETUP_OBJ_RENDER",
  0x18: "LOAD_POLYGON_ASM",
  0x19: "SET_BACKGROUND_IMAGE",
  0x1A: "NO_OP", # unused
  0x1D: "SCALE_MODEL",
  0x1E: "NO_OP", # unused
  0x1F: "NO_OP", # unused
  0x20: "START_GEO_LAYOUT_WITH_RENDER_AREA"
}

PAINTING_IDS = {
  LVL_BOB: 0x00,
  LVL_CCM: 0x01,
  LVL_WF: 0x02,
  LVL_JRB: 0x03,
  LVL_LLL: 0x04,
  LVL_SSL: 0x05,
  LVL_HMC: 0x06,
  LVL_DDD: 0x07,
  LVL_WDW: 0x08,
  LVL_THI: 0x0D, # Huge Version
  LVL_TTM: 0x0A,
  LVL_TTC: 0x0B,
  LVL_SL: 0x0C
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

BEHAVIOUR_NAMES = {}

application_path
with open(os.path.join(application_path, "Data", "behaviorNames.json"), "r") as behavior_file:
  BEHAVIOUR_NAMES = json.loads(behavior_file.read())

  BEHAVIOUR_NAMES = dict({ hex(int(key, 16)): name for (key, name) in BEHAVIOUR_NAMES.items()})
