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
parser.add_argument("--no-extend", default=False, help="disable auto-extend of ROM, which might fail on some systems", action="store_true")
parser.add_argument("--out", type=str, help="target of randomized rom")
parser.add_argument("--seed", type=int, default=round(time.time() * 256 * 1000), help="define a custom seed to have the same experience as someone else")
parser.add_argument("--shuffle-paintings", default="match", choices=["match", "random", "off"], help="change the behaviour of painting shuffle (\"match\" - matches randomized levels, i.e. paintings = level, \"random\" - independently randomize paintings, \"off\" - leave paintings untouched)")
parser.add_argument("--shuffle-entries", help="enables random level entries, mixing paintings, level entries and secret level entries", action="store_true")
parser.add_argument("--shuffle-mario-color", help="enables randomized mario colors", action="store_true")
parser.add_argument("--shuffle-music", help="randomizes every song in every level", action="store_true")
parser.add_argument("--shuffle-objects", help="shuffles objects in levels", action="store_true")
parser.add_argument("--shuffle-colors", help="shuffles colors for various things", action="store_true")
parser.add_argument("--shuffle-dialog", help="shuffles dialog texts. might look weird for prompts", action="store_true")

argument_labels = {
  "rom": "Input ROM",
  "out": "Output ROM",
  "no_extend": "Disable automatic extending",
  "seed": "RNG Seed",
  "shuffle_paintings": "Enable Painting Randomizer",
  "shuffle_mario_color": "Enable Random Color for Mario",
  "shuffle_music": "Enables random music in all levels",
  "shuffle_objects": "Randomize object positions in levels",
  "shuffle_colors": "Randomizes colors of various things",
  "shuffle_dialog": "Random Dialog Texts (Cutscenes, Signs, etc).",
  "shuffle_entries": "Random Level Entries"
}

def run_with_args(opt_args):
  seed(opt_args.seed)

  rom_path = Path(opt_args.rom)
  out_path = opt_args.out or Path(rom_path.name[0:-4] + ".out.z64")

  if not rom_path.exists():
    raise Exception("invalid file, does not exist")

  try:
    with ROM(rom_path, out_path) as rom:
      pretty_print_table("Your Settings", {argument_labels[label]: value for (label, value) in vars(opt_args).items()})

      try:
        rom.verify_header()
      except Exception as err:
        print(err)
        print("invalid rom, does not match known headers. make sure you use the z64 format")
        sys.exit(2)

      if rom.rom_type == 'VANILLA' and not opt_args.no_extend:
        print("The specified ROM file is not extended yet, we\'ll try to extend it for you")
        try:
          new_rom = rom.try_extend()
          new_args = {**vars(opt_args)}
          new_args['rom'] = new_rom
          return run_with_args(argparse.Namespace(**new_args))
        except Exception as err:
          print("Unfortunately, the ROM could not be extended. Please see the log below to figure out why. The Randomizer will continue using the vanilla rom. Please note not all functionality is available in this mode.")
          print(err)
      rom.print_info()
      
      rom.set_initial_segments()
      rom.read_levels()

      music_random = MusicRandomizer(rom)
      if opt_args.shuffle_music:
        music_random.shuffle_music(ALL_LEVELS)

      mario_random = MarioRandomizer(rom)
      if opt_args.shuffle_mario_color:
        mario_random.randomize_color()

      warp_random = WarpRandomizer(rom)
      if opt_args.shuffle_entries:
        warp_random.shuffle_level_entries(opt_args.shuffle_paintings)
      
      level_randomizer = LevelRandomizer(rom)
      if opt_args.shuffle_objects:
        level_randomizer.shuffle_objects()

      text_randomizer = TextRandomizer(rom)
      if opt_args.shuffle_dialog:
        text_randomizer.shuffle_dialog_pointers()

      color_randomizer = ColorRandomizer(rom)
      if opt_args.shuffle_colors:
        color_randomizer.randomize_coin_colors()
      
    SpoilerLog.output()
    print(f'Completed! Your randomized ROM File can be found as "{os.path.relpath(out_path)}"')
  except Exception as err:
    print(f'Unfortunately, the randomizer encountered an error, seen below:')
    print(err)
    print("Stacktrace:".center(40, '-'))
    traceback.print_exc()

run_with_args(parser.parse_args())