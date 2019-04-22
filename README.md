# Super Mario 64 ROM Randomizer

This is a work in progress project to build an [https://github.com/AmazingAmpharos/OoT-Randomizer](OoT-Randomizer)-style randomizer for Super Mario 64.

# Features
(* Requires Extended ROM)

- Randomize Level Music
- Randomize Paintings (Entries and Art*)
- Randomize Marios Color*
- Use custom seed (pass `--seed <string>`)
- ...many more to come

# Extended ROM

Extended ROMs include previously compressed content of the ROM uncompressed at the end of the ROM. This is needed to change certain behaviour.

To extend your rom, use either [sm64extender](https://www.smwcentral.net/?p=viewthread&t=77343) or [Super Mario 64 ROM Extender](http://qubedstudios.rustedlogic.net/Mario64Tools.htm).

# Usage CLI
To use this package, download the repository and run using **python >= 3.5**, passing your Vanilla SM64 ROM or an Extended ROM:
```
python main.py ./Super_Mario_64_(U)_[!].z64
```
_Note: Only accepts z64 format. Currently only supports North American version_

Output will be a file with the same name, ending in `.out.z64`. Run this in your emulator.

```
usage: main.py [-h] [--out OUT] [--seed SEED] [--level-shuffle LEVEL_SHUFFLE]
               [--painting-shuffle {match,random,off}]
               [--mario-color-shuffle MARIO_COLOR_SHUFFLE]
               rom

positional arguments:
  rom

optional arguments:
  -h, --help            show this help message and exit
  --out OUT             target of randomized rom
  --seed SEED           define a custom seed to have the same experience as
                        someone else
  --level-shuffle LEVEL_SHUFFLE
                        enables the shuffling of levels
  --painting-shuffle {match,random,off}
                        change the behaviour of painting shuffle ("match" -
                        matches randomized levels, i.e. paintings = level,
                        "random" - independently randomize paintings, "off" -
                        leave paintings untouched)
  --mario-color-shuffle MARIO_COLOR_SHUFFLE
                        enables randomized mario colors
```

## Special Thanks
- Wonderful SM64 Hacking Resources, clean, easy to use and great explanations: http://hack64.net/
- Simpleflips Discord for help with SM64 weirdness (especially Felegg)
- https://www.smwcentral.net/
