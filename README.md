<p align="center"> 
  <img src="https://i.imgur.com/pf687MH.png" alt="SM64 Randomizer">
  <a href="https://discordapp.com/invite/NwNZ3qb" target="_blank">
    <p align="center">
      <img src="https://i.imgur.com/0DkN9vW.png" alt="Join our Discord Server" height="64" /><br />
      Join our Discord Server for development updates, discussion and support
    </p>
  </a>
</p>


# Super Mario 64 ROM Randomizer

This is a work in progress project to build an [https://www.ootrandomizer.com/](OoT-Randomizer)-style randomizer for Super Mario 64, that is highly customizable and fast to use.

# Features

- Works on all versions of the game, even **ROMHacks**.
- Randomizes Level Entries - Every Level will be a different one
- Randomizes Castle Paintings - To visually match the entrance of the level it now leads to. (*Levels without a castle painting will show as a brick wall.*)
- Randomizes Dialog
- Randomizes Music
- Randomizes Mario's Outfit
- Randomizes Coin Colors
- Randomizes Objects in Level
- ...many more to come

Also auto extends ROM to work with the randomizer. *Unfortunately this only works on Windows and Mac OSX right now. Please open a PR if you want this functionality on other OSes*
To extend your ROM manually, use either [sm64extender](https://www.smwcentral.net/?p=viewthread&t=77343) or [Super Mario 64 ROM Extender](http://qubedstudios.rustedlogic.net/Mario64Tools.htm).

# GUI
The randomizer includes a simple GUI for easy setup without any knowledge about the command line. Simply download the latest [release](/releases/latest) and open `SM64 Randomizer GUI`.

![SM64 Randomizer GUI](https://i.imgur.com/erEk4Dh.png)


# Usage CLI
To use this package:
- Download [a release](/releases/latest), which includes a GUI and the CLI.
- Download or `git clone` the repository and run using **python >= 3.5**, passing your SM64 ROM:
```
python main.py ./Super_Mario_64_(U)_[!].z64 --shuffle-levels --shuffle-mario-color --shuffle-paintings match --seed 123
```
_Note: Works on all versions of the game, as well as **ROM Hacks**_

Output will be a file with the same name, ending in `.out.z64`. Run this in your emulator.

```
usage: main.py [-h] [--no-extend] [--out OUT] [--seed SEED] [--version]
               [--shuffle-paintings {vanilla,match,random}]
               [--shuffle-entries] [--shuffle-mario-outfit] [--shuffle-music]
               [--shuffle-objects] [--shuffle-colors] [--shuffle-text]
               rom

positional arguments:
  rom

optional arguments:
  -h, --help            show this help message and exit
  --no-extend           disable auto-extend of ROM, which might fail on some
                        systems
  --out OUT             target of randomized rom
  --seed SEED           define a custom seed to have the same experience as
                        someone else
  --version             show program's version number and exit
  --shuffle-paintings {vanilla,match,random}
                        Change the behaviour of how the paintings in the
                        castle are shuffled ("match" - matches randomized
                        levels, i.e. painting = level, "random" -
                        independently randomize paintings, "off" - leave
                        paintings untouched)
  --shuffle-entries     Shuffles the levelentries. When you enter a level, you
                        will end up at a random one.
  --shuffle-mario-outfit
                        Randomizes parts of Marios Outfit.
  --shuffle-music       Randomizes most songs in the game.
  --shuffle-objects     Shuffles Objects in Levels
  --shuffle-colors      Shuffle various colors in the game
  --shuffle-text        Shuffle Dialog text, for signs, npc dialog, level
                        dialog and prompts.
```

## Special Thanks
- wonderful SM64 hacking resources, clean, easy to use and great explanations: http://hack64.net/
- simpleflips discord for help with SM64 weirdness (especially Felegg)
- durkhaz for the logo
- Beta Testers
- https://www.smwcentral.net/
