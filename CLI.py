import sys
import os
import argparse
import time
import traceback
import json
from pathlib import Path
from random import seed
from typing import List

from __version__ import __version__

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
from Functionality.Cutscenes import CutsceneFunctionality

from Constants import ALL_LEVELS, MISSION_LEVELS, LVL_CASTLE_INSIDE

randomizer_params = []
with open(os.path.join("Data", "configurableParams.json"), "r") as json_params_file:
  randomizer_params = json.loads(json_params_file.read())

parser = argparse.ArgumentParser()
parser.add_argument("rom", type=str)
parser.add_argument("--no-extend", default=False, help="disable auto-extend of ROM, which might fail on some systems", action="store_true")
parser.add_argument("--out", type=str, help="target of randomized rom")
parser.add_argument("--seed", type=int, default=round(time.time() * 256 * 1000), help="define a custom seed to have the same experience as someone else")
parser.add_argument('--version', action='version', version=f'v{__version__}')
argument_labels = {
  "rom": "Input ROM",
  "out": "Output ROM",
  "no_extend": "Disable automatic extending",
  "seed": "RNG Seed",
}
for field in randomizer_params:
  argument_args = []
  argument_kwargs = {}

  argument_args.append(f'--{field["name"]}')

  if field["type"] == 'select':
    argument_kwargs["choices"] = [option["value"] for option in field["options"]]
  elif field["type"] == 'checkbox':
    argument_kwargs["action"] = "store_true"
  
  if "default" in field:
    if type(field["default"]) is dict and "CLI" in field["default"]:
      argument_kwargs["default"] = field["default"]["CLI"]
    else:
      argument_kwargs["default"] = field["default"]

  if "help" in field:
    argument_kwargs["help"] = field["help"]

  if "label" in field:
    argparse_name = field["name"]
    argument_labels[field["name"].replace("-", "_")] = field["label"]
  
  parser.add_argument(*argument_args, **argument_kwargs)

def run_with_args(sys_args : List[str] = sys.argv[1:]):
  parsed_args = parser.parse_args(sys_args)
  return run_with_parsed_args(parsed_args)

def generate_output_path(rom_in : Path):
  return 

def run_with_parsed_args(opt_args : argparse.Namespace):
  seed(opt_args.seed)

  rom_path = Path(opt_args.rom)
  out_path = opt_args.out or rom_path.with_suffix(f'.out{rom_path.suffix}')

  if not rom_path.exists():
    raise Exception("invalid file, does not exist")

  with ROM(rom_path, out_path) as rom:
    try:
      rom.verify_header()
    except Exception as err:
      print(err)
      print("invalid rom, does not match known headers")
      sys.exit(2)

    if rom.rom_type == 'VANILLA' and not opt_args.no_extend:
      print("The specified ROM file is not extended yet, we\'ll try to extend it for you")
      new_rom = None

      try:
        new_rom = rom.try_extend()
      except Exception as err:
        print("Unfortunately, the ROM could not be extended. Please see the log below to figure out why. The Randomizer will continue using the vanilla rom. Please note not all functionality is available in this mode.")
        print(err)

      new_args = {**vars(opt_args)}
      new_args['rom'] = new_rom
      new_args['no_extend'] = True # don't extend twice
      run_with_parsed_args(argparse.Namespace(**new_args))
      return

    pretty_print_table("Your Settings", {argument_labels[label]: value for (label, value) in vars(opt_args).items()})
    rom.print_info()
    
    rom.set_initial_segments()
    rom.read_levels()

    music_random = MusicRandomizer(rom)
    if opt_args.shuffle_music:
      music_random.shuffle_music(ALL_LEVELS)

    mario_random = MarioRandomizer(rom)
    if opt_args.shuffle_mario_outfit:
      mario_random.randomize_color()

    warp_random = WarpRandomizer(rom)
    if opt_args.shuffle_entries:
      warp_random.shuffle_level_entries(opt_args.shuffle_paintings)
    
    level_randomizer = LevelRandomizer(rom)
    if opt_args.shuffle_objects:
      level_randomizer.shuffle_objects()

    text_randomizer = TextRandomizer(rom)
    if opt_args.shuffle_text:
      text_randomizer.shuffle_dialog_pointers()

    color_randomizer = ColorRandomizer(rom)
    if opt_args.shuffle_colors:
      color_randomizer.randomize_coin_colors()

    cutscene_func = CutsceneFunctionality(rom)
    if opt_args.disable_cutscenes:
      cutscene_func.disable_all_cutscenes()
    
    if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'PLOT':
      for (level_area, parsed) in rom.levelscripts.items():
        parsed.level_geometry.plot()
      #rom.levelscripts

  SpoilerLog.output()
  print(f'Completed! Your randomized ROM File can be found as "{str(Path(out_path).absolute())}"')

#run_with_args()