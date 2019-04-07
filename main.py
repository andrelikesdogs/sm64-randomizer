#!/usr/bin/env python
import sys

if __name__ != '__main__':
  print("Dont import this")
  sys.exit(2)

import os
import argparse
import time
from pathlib import Path
from random import seed

from __version__ import __version__

from Rom import ROM
from Debug import Debug
from randoutils import pretty_print_table

from RandomModules.Music import MusicRandomizer
from RandomModules.CastlePaintings import CastlePaintingsRandomizer
from RandomModules.Mario import MarioRandomizer

from Constants import ALL_LEVELS, MISSION_LEVELS, LVL_CASTLE_INSIDE

print(f'  Super Mario 64 Randomizer  (Version: {__version__})\n')

if len(sys.argv) <= 1:
  # assume we want to start the GUI
  print("starting gui...")
  import gui
  sys.exit(0)

parser = argparse.ArgumentParser()
parser.add_argument("rom", type=str)
parser.add_argument("--out", type=str, help="target of randomized rom")
parser.add_argument("--seed", type=int, default=round(time.time() * 256 * 1000), help="define a custom seed to have the same experience as someone else")
parser.add_argument("--level-shuffle", type=bool, default=True, help="enables the shuffling of levels")
parser.add_argument("--painting-shuffle", type=str, default="match", choices=["match", "random", "off"], help="change the behaviour of painting shuffle (\"match\" - matches randomized levels, i.e. paintings = level, \"random\" - independently randomize paintings, \"off\" - leave paintings untouched)")
parser.add_argument("--mario-color-shuffle", type=bool, default=True, help="enables randomized mario colors")
parser.add_argument
args = parser.parse_args()

argument_labels = {
  "rom": "Input ROM",
  "out": "Output ROM",
  "seed": "RNG Seed",
  "level_shuffle": "Enable Level Randomizer",
  "painting_shuffle": "Enable Painting Randomizer",
  "mario_color_shuffle": "Enable Random Color for Mario"
}

used_seed = None

seed(args.seed)

rom_path = Path(args.rom)
out_path = args.out or Path(rom_path.name[0:-4] + ".out.z64")

if not rom_path.exists():
  raise Exception("invalid file, does not exist")



  #debugger = Debug(rom)
  #debugger.list_segment_areas()
  
  #print([hex(b) for b in debugger.read_data(0x3D00B8, 0x3D0DD0)[:200]])
  #debugger.geo_layout_reader(0x3D00B8, 0x3D00B8 + 0x472) #0x3D0DD0)

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
    music_random.shuffle_music(ALL_LEVELS)

    mario_random = MarioRandomizer(rom)
    mario_random.randomize_color()

    castle_warp_random = CastlePaintingsRandomizer(rom)
    castle_warp_random.shuffle_paintings(args.painting_shuffle)
  
  print(f'Completed! Your randomized ROM File can be found as "{os.path.relpath(out_path)}"')
except Exception as err:
  print(f'Unfortunately, the randomizer encountered an error, seen below:')
  print(err)
