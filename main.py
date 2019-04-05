import argparse
import sys
import time
from pathlib import Path
from random import seed

from __version__ import __version__

from Rom import ROM
from Debug import Debug

from RandomModules.Music import MusicRandomizer
from RandomModules.CastlePaintings import CastlePaintingsRandomizer
from RandomModules.Mario import MarioRandomizer

from Constants import ALL_LEVELS, MISSION_LEVELS, LVL_CASTLE_INSIDE

print(f'  Super Mario 64 Randomizer  (Version: {__version__})\n')

parser = argparse.ArgumentParser()
parser.add_argument("rom")
parser.add_argument("--out", help="target of randomized rom")
parser.add_argument("--seed", help="define a custom seed to have the same experience as someone else")
args = parser.parse_args()

used_seed = None

if args.seed:
  used_seed = args.seed
  seed(used_seed)
else:
  used_seed = round(time.time() * 256 * 1000)
  seed(used_seed)

rom_path = Path(args.rom)
out_path = args.out or Path(rom_path.name[0:-4] + ".out.z64")

if not rom_path.exists():
  raise Exception("invalid file, does not exist")

with ROM(rom_path, out_path) as rom:
  try:
    rom.verify_header()
    rom.print_info()
  except Exception as err:
    print(err)
    print("invalid rom, does not match known headers. make sure you use the z64 format")
    sys.exit(2)

  print(f'using seed {used_seed}')

  #debugger = Debug(rom)
  #debugger.list_segment_areas()
  
  #print([hex(b) for b in debugger.read_data(0x3D00B8, 0x3D0DD0)[:200]])
  #debugger.geo_layout_reader(0x3D00B8, 0x3D00B8 + 0x472) #0x3D0DD0)

  music_random = MusicRandomizer(rom)
  music_random.shuffle_music(ALL_LEVELS)

  mario_random = MarioRandomizer(rom)
  mario_random.randomize_color()

  castle_warp_random = CastlePaintingsRandomizer(rom)
  castle_warp_random.shuffle_paintings()
