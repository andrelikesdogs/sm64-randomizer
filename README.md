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

This is a work in progress project to build an [OoT-Randomizer](https://www.ootrandomizer.com/)-style randomizer for Super Mario 64, that is highly configurable and easy to use.

# Features

- Works on all versions of the game, even **ROMHacks**.
- Randomizes Level Entries - Every Level will be a different one
- Randomizes Castle Paintings - To visually match the entrance of the level it now leads to. (*Levels without a castle painting will show as a brick wall.*)
- Randomizes Dialog
- Randomizes Music
- Randomizes Mario's Outfit
- Randomizes Coin Colors
- Randomizes Objects in Level
- Disables Cutscenes
- Disables Level Intros
- Disable Out-of-Level Starwarp
- ...many more to come

Also auto extends ROM to work with the randomizer. If this fails, extend your ROM manually and use either [sm64extender](https://www.smwcentral.net/?p=viewthread&t=77343) or [Super Mario 64 ROM Extender](http://qubedstudios.rustedlogic.net/Mario64Tools.htm).

# Usage GUI
The randomizer includes a simple GUI for easy setup without any knowledge about the command line. Simply download the latest [release](/releases/latest) and open `SM64 Randomizer GUI`.

![SM64 Randomizer GUI](https://i.imgur.com/erEk4Dh.png)

1. Select an Input ROM
2. Select an Output (will be automatically guessed to <rom>.out.<ending>)
3. Select your settings
- Choose a custom seed to share with friends who use the same tool
- Copy the settings string to copy your current settings to share with friends. Does not include seed.
4. Press "Generate"
5. Run output file on your emulator/console. :tada:

# Usage CLI
To use this package:
- Download [a release](/releases/latest), which includes a GUI and the CLI.
- Download or `git clone` the repository and run using **python >= 3.5**, passing your SM64 ROM:
```
python main.py ./Super_Mario_64_(U)_[!].z64 --shuffle-levels --shuffle-mario-color --shuffle-paintings match --seed 123
```
_Note: Works on all versions of the game, as well as **ROM Hacks** (with some tweaking, contact us in Discord for help)_

Output will be a file with the same name, ending in `.out.z64`. Run this on your emulator/console.

```
usage: main.py [-h] [--no-extend] [--out OUT] [--seed SEED] [--version]
               [--shuffle-paintings {vanilla,match,random}]
               [--shuffle-entries] [--shuffle-mario-outfit] [--shuffle-music]
               [--shuffle-objects] [--shuffle-colors] [--shuffle-text]
               [--disable-cutscenes] [--disable-starwarp]
               [--stardoor-requirements {vanilla,random,open}]
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
  --disable-cutscenes   Disables some of the games cutscenes. (Peach Intro,
                        Lakitu Intro, Bowser-Text on Entry)
  --disable-starwarp    Disables automatically leaving the level when you
                        collect a star. This way, all stars act like a
                        100-Coin star or a Bowser 8-Reds Star
  --stardoor-requirements {vanilla,random,open}
                        Changes how the doors to levels require different
                        amounts of stars to be collected beforehand. Random
                        means all doors require stars, but the amount will be
                        random. Open simply means all doors are open from the
                        start.
```

## Special Thanks
- [hack64](http://hack64.net/)'s wonderful SM64 hacking resources, clean, easy to use and great in-depth details
- [SimpleFlips](https://www.youtube.com/user/SimpleFlips) Discord-Server for help with SM64 hacking/weirdness (especially Felegg)
- Durkhaz for the amazing logo
- CJay for server hosting of the generator
- Beta Testers and people from the [discord](https://discordapp.com/invite/NwNZ3qb)
- [smwcentral](https://www.smwcentral.net/)'s community and forum
