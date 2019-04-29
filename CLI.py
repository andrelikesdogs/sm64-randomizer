from __version__ import __version__
print(f'  Super Mario 64 Randomizer  (Version: {__version__})\n')

import sys
import os
import argparse
import time
import traceback
from pathlib import Path
from random import seed

from Rom import ROM
from Debug import Debug
from Spoiler import SpoilerLog
from randoutils import pretty_print_table

from RandomModules.Music import MusicRandomizer
from RandomModules.Mario import MarioRandomizer
from RandomModules.Levels import LevelRandomizer
from RandomModules.Colors import ColorRandomizer
from RandomModules.Warps import WarpRandomizer
from RandomModules.Text import TextRandomizer

from Constants import ALL_LEVELS, MISSION_LEVELS, LVL_CASTLE_INSIDE


parser = argparse.ArgumentParser()
parser.add_argument("rom", type=str)
parser.add_argument("--out", type=str, help="target of randomized rom")
parser.add_argument("--seed", type=int, default=round(time.time() * 256 * 1000), help="define a custom seed to have the same experience as someone else")
parser.add_argument("--shuffle-levels", help="enables the shuffling of levels", action="store_true")
parser.add_argument("--shuffle-paintings", default="match", choices=["match", "random", "off"], help="change the behaviour of painting shuffle (\"match\" - matches randomized levels, i.e. paintings = level, \"random\" - independently randomize paintings, \"off\" - leave paintings untouched)")
parser.add_argument("--shuffle-mario-color", help="enables randomized mario colors", action="store_true")
parser.add_argument("--shuffle-music", help="randomizes every song in every level", action="store_true")
parser.add_argument("--shuffle-objects", help="shuffles objects in levels", action="store_true")
parser.add_argument("--shuffle-colors", help="shuffles colors for various things", action="store_true")
parser.add_argument("--shuffle-dialog", help="shuffles dialog texts. might look weird for prompts", action="store_true")
parser.add_argument
args = parser.parse_args()

argument_labels = {
  "rom": "Input ROM",
  "out": "Output ROM",
  "seed": "RNG Seed",
  "shuffle_levels": "Enable Level Randomizer",
  "shuffle_paintings": "Enable Painting Randomizer",
  "shuffle_mario_color": "Enable Random Color for Mario",
  "shuffle_music": "Enables random music in all levels",
  "shuffle_objects": "Randomize object positions in levels",
  "shuffle_colors": "Randomizes colors of various things",
  "shuffle_dialog": "Random Dialog Texts (Cutscenes, Signs, etc)."
}

used_seed = None

seed(args.seed)

rom_path = Path(args.rom)
out_path = args.out or Path(rom_path.name[0:-4] + ".out.z64")

if not rom_path.exists():
  raise Exception("invalid file, does not exist")

try:
  with ROM(rom_path, out_path) as rom:
    try:
      rom.verify_header()
      pretty_print_table("Your Settings", {argument_labels[label]: value for (label, value) in vars(args).items()})
      rom.print_info()
    except Exception as err:
      print(err)
      print("invalid rom, does not match known headers. make sure you use the z64 format")
      sys.exit(2)

    music_random = MusicRandomizer(rom)
    if args.shuffle_music:
      music_random.shuffle_music(ALL_LEVELS)

    mario_random = MarioRandomizer(rom)
    if args.shuffle_mario_color:
      mario_random.randomize_color()

    warp_random = WarpRandomizer(rom)
    if args.shuffle_levels:
      warp_random.shuffle_level_entries(args.shuffle_paintings)
    
    level_randomizer = LevelRandomizer(rom)
    if args.shuffle_objects:
      level_randomizer.shuffle_enemies()

    text_randomizer = TextRandomizer(rom)
    if args.shuffle_dialog:
      text_randomizer.shuffle_dialog_pointers()

    color_randomizer = ColorRandomizer(rom)
    if args.shuffle_colors:
      color_randomizer.randomize_coin_colors()
    
  SpoilerLog.output()
  print(f'Completed! Your randomized ROM File can be found as "{os.path.relpath(out_path)}"')
except Exception as err:
  print(f'Unfortunately, the randomizer encountered an error, seen below:')
  print(err)
  print("Stacktrace:".center(40, '-'))
  traceback.print_exc()
