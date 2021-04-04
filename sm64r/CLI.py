import sys
import os
import argparse
import time
import traceback
import json
import hashlib
from pathlib import Path
from random import seed, randint
from typing import List

from __version__ import __version__

from .Rom import ROM
from .Spoiler import SpoilerLog
from .Randoutils import pretty_print_table

from .RandomModules.Music import MusicRandomizer
from .RandomModules.Mario import MarioRandomizer
from .RandomModules.Objects import ObjectRandomizer
from .RandomModules.Colors import ColorRandomizer
from .RandomModules.Warps import WarpRandomizer
from .RandomModules.Text import TextRandomizer
from .RandomModules.Textures import TextureAtlas
from .RandomModules.Stardoors import StardoorRandomizer
from .RandomModules.Instruments import InstrumentRandomizer
from .RandomModules.Skybox import SkyboxRandomizer
from .Enhancements.GameplayEnhancements import Gameplay
from .Enhancements.TextureChanges import TextureChanges

from .Constants import ALL_LEVELS, MISSION_LEVELS, LVL_CASTLE_INSIDE, application_path

randomizer_params = []
with open(os.path.join(application_path, "Data", "configurableParams.json"), "r") as json_params_file:
  randomizer_params = json.loads(json_params_file.read())

parser = argparse.ArgumentParser()
parser.add_argument("rom", type=str)
parser.add_argument("--no-extend", default=False, help="disable auto-extend of ROM, which might fail on some systems", action="store_true")
parser.add_argument("--alignment", type=int, default=8, help="Specify the byte alignment. If you know this value, you have a higher change of successfully randomizing romhacks.")
parser.add_argument("--out", type=str, help="target of randomized rom")
parser.add_argument('--version', action='version', version=f'v{__version__}')

argument_labels = {
  "rom": "Input ROM",
  "out": "Output ROM",
  "no_extend": "Disable automatic extending",
  "alignment": "Byte Alignment"
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
  rom_path = Path(opt_args.rom)
  out_path = opt_args.out or rom_path.with_suffix(f'.out{rom_path.suffix}')

  if not rom_path.exists():
    raise Exception("invalid file, does not exist")

  if not opt_args.seed:
    print("Choosing random seed")
    opt_args.seed = randint(1e10, 10e10)
  
  with ROM(rom_path, out_path, opt_args.alignment) as rom:
    try:
      rom.verify_header()
    except Exception as err:
      print("Could not read ROM header")
      print(err)
      print(traceback.format_exc())
      sys.exit(2)

    if rom.rom_type == 'VANILLA' and not opt_args.no_extend:
      print("The specified ROM file is not extended yet, we\'ll try to extend it for you")
      new_rom = None

      target_alignment = opt_args.alignment if opt_args.alignment is not None else 8
      try:
        new_rom = rom.try_extend(target_alignment)
      except Exception as err:
        print("Unfortunately, the ROM could not be extended. Please see the log below to figure out why. The Randomizer will continue using the vanilla rom. Please note not all functionality is available in this mode.")
        print(err)
        print(traceback.format_exc())

      new_args = {**vars(opt_args)}
      new_args['rom'] = new_rom
      new_args['no_extend'] = True # don't extend twice
      new_args['alignment'] = target_alignment
      run_with_parsed_args(argparse.Namespace(**new_args))
      return

    pretty_print_table("Your Settings", {argument_labels[label]: value for (label, value) in vars(opt_args).items()})
    rom.read_configuration()
    rom.print_info()

    # convert seed here! otherwise we might return the hashed seed and heck everything up    
    opt_args.seed = int(hashlib.sha1(bytes(str(opt_args.seed), 'utf8')).hexdigest(), 16) % (10**12)
    seed(opt_args.seed)

    rom.read_levels()
    textures = None

    if rom.rom_type == 'EXTENDED':
      # initialize texture atlas and dynamic positions
      textures = TextureAtlas(rom)
      textures.add_dynamic_positions()
      textures.load_default_unknown_texture()
    
    # Segment Finder
    # rom.match_segments(0xD78271)
    # rom.match_segments(0xA8181C) # texture for question mark

    start_time = time.time()

    music_random = MusicRandomizer(rom)
    if opt_args.shuffle_music:
      music_random.shuffle_music(ALL_LEVELS)
      seed(opt_args.seed)

    mario_random = MarioRandomizer(rom)
    if opt_args.shuffle_mario_outfit:
      mario_random.randomize_color()
      seed(opt_args.seed)

    warp_random = WarpRandomizer(rom)
    if opt_args.shuffle_entries:
      if opt_args.shuffle_paintings:
        textures.add_level_paintings()
        seed(opt_args.seed)

        if opt_args.shuffle_paintings == 'replace-unknown':
          if not textures:
            print("Sorry, please use an extended ROM to utilize custom paintings.")
          else:
            textures.add_vanilla_portrait_custom_paintings()

      warp_random.shuffle_level_entries(vars(opt_args))
      seed(opt_args.seed)

      if "SM64R" in os.environ and "WARPS" in os.environ["SM64R"]:
        warp_random.plot_network()
    
    instrument_randomizer = InstrumentRandomizer(rom)
    if opt_args.shuffle_instruments:
      instrument_randomizer.shuffle_instruments()
      seed(opt_args.seed)

    text_randomizer = TextRandomizer(rom)
    if opt_args.shuffle_text:
      text_randomizer.shuffle_dialog_pointers()
      seed(opt_args.seed)

    color_randomizer = ColorRandomizer(rom)
    if opt_args.shuffle_colors:
      color_randomizer.randomize_coin_colors()
      seed(opt_args.seed)

    gameplay_stuff = Gameplay(rom)
    if opt_args.disable_cutscenes:
      gameplay_stuff.disable_all_cutscenes()
    if opt_args.disable_starwarp:
      gameplay_stuff.disable_starwarp()
    
    stardoor_randomizer = StardoorRandomizer(rom)
    if opt_args.stardoor_requirements != "vanilla":
      if opt_args.stardoor_requirements == "open":
        stardoor_randomizer.open_level_stardoors()
      elif opt_args.stardoor_requirements == "random":
        stardoor_randomizer.shuffle_level_stardoors()
      
    if opt_args.keydoor_requirements != "vanilla":
      stardoor_randomizer.open_keydoors()

    skybox_randomizer = SkyboxRandomizer(rom)
    if opt_args.shuffle_skybox:
      skybox_randomizer.randomize_skyboxes()

    object_randomizer = ObjectRandomizer(rom)
    if opt_args.shuffle_objects:
      object_randomizer.shuffle_objects()
      seed(opt_args.seed)

      texture_changer = TextureChanges(rom)
      texture_changer.remove_tree_shadows()

    if 'SM64R' in os.environ and 'PLOT' in os.environ['SM64R']:
      for (_, parsed) in rom.levelscripts.items():
        parsed.level_geometry.plot()
      #rom.levelscripts

  SpoilerLog.output()
  print(f'It took {round(time.time() - start_time)}s to complete')
  print(f'Completed! Your randomized ROM File can be found as "{str(Path(out_path).absolute())}"')

#run_with_args()