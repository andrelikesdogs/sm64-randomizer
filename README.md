<p align="center"> 
  <img src="https://i.imgur.com/pf687MH.png" alt="SM64 Randomizer">
</p>

# Super Mario 64 ROM Randomizer

This is a work in progress project to build an [https://github.com/AmazingAmpharos/OoT-Randomizer](OoT-Randomizer)-style randomizer for Super Mario 64.

# Features
(* Requires Extended ROM)

- Randomize level music
- Randomize level entries (entries and paintings)
- Randomize mario's outfit
- Randomize object colors
- Randomize text (cutscenes, signs, prompts, etc)
- Nice GUI to setup things without using the CLI tool.
- Use custom seed (pass `--seed <string>`)
- ...many more to come

# GUI
The randomizer includes a simple GUI for easy setup without any knowledge about CLI tools.

![SM64 Randomizer GUI](https://i.imgur.com/erEk4Dh.png)

# Extended ROM

Extended ROMs include previously compressed content of the ROM uncompressed at the end of the ROM. This is needed to change certain behaviour.

To extend your rom, use either [sm64extender](https://www.smwcentral.net/?p=viewthread&t=77343) or [Super Mario 64 ROM Extender](http://qubedstudios.rustedlogic.net/Mario64Tools.htm).

# Usage CLI
To use this package, download the repository and run using **python >= 3.5**, passing your Vanilla SM64 ROM or an Extended ROM:
```
python main.py ./Super_Mario_64_(U)_[!].z64 --shuffle-levels --shuffle-mario-color --shuffle-paintings match --seed 123
```
_Note: Only accepts z64 format. Currently only supports North American version_

Output will be a file with the same name, ending in `.out.z64`. Run this in your emulator.

```
usage: main.py [-h] [--out OUT] [--seed SEED] [--shuffle-levels]
               [--shuffle-paintings {match,random,off}]
               [--shuffle-mario-color] [--shuffle-music] [--shuffle-objects]
               [--shuffle-colors] [--shuffle-dialog]
               rom

positional arguments:
  rom

optional arguments:
  -h, --help            show this help message and exit
  --out OUT             target of randomized rom
  --seed SEED           define a custom seed to have the same experience as
                        someone else
  --shuffle-levels      enables the shuffling of levels
  --shuffle-paintings {match,random,off}
                        change the behaviour of painting shuffle ("match" -
                        matches randomized levels, i.e. paintings = level,
                        "random" - independently randomize paintings, "off" -
                        leave paintings untouched)
  --shuffle-mario-color
                        enables randomized mario colors
  --shuffle-music       randomizes every song in every level
  --shuffle-objects     shuffles objects in levels
  --shuffle-colors      shuffles colors for various things
  --shuffle-dialog      shuffles dialog texts. might look weird for prompts
```

## Special Thanks
- Wonderful SM64 Hacking Resources, clean, easy to use and great explanations: http://hack64.net/
- simpleflips Discord for help with SM64 weirdness (especially Felegg)
- durkhaz for the logo
- https://www.smwcentral.net/
