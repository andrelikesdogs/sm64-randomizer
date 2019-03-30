import argparse
import sys
import time
from pathlib import Path
from random import seed

from __version__ import __version__

from Rom import ROM

from RandomModules.Music import MusicRandomizer
from RandomModules.CastlePaintings import CastlePaintingsRandomizer

from Constants import LEVEL_POSITIONS, PLAYABLE_LEVELS

print(f'  Super Mario 64 Randomizer  (Version: {__version__})')

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
  used_seed = time.time() * 256
  seed(used_seed)

rom_path = Path(args.rom)
out_path = args.out or Path(rom_path.name[0:-4] + ".out.z64")

if not rom_path.exists():
  raise Exception("invalid file, does not exist")

with ROM(rom_path, out_path) as rom:
  if not rom.verify_header():
    raise Exception("invalid rom, does not match known headers. make sure you use the z64 format")

  music_random = MusicRandomizer(rom)
  music_random.shuffle_music(LEVEL_POSITIONS.values())

  castle_warp_random = CastlePaintingsRandomizer(rom)
  castle_warp_random.shuffle_paintings()
  #castle_warp_random.shuffle_paintings(LEVEL_POSITIONS.values())
  
