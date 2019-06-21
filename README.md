<p align="center"> 
  <img src="https://i.imgur.com/pf687MH.png" alt="SM64 Randomizer Generator">
  <a href="https://discord.gg/2ZYfhcB" target="_blank">
    <p align="center">
      <img src="https://i.imgur.com/0DkN9vW.png" alt="Join our Discord Server" height="64" /><br />
      Join our Discord Server for development updates, discussion and support
    </p>
  </a>
</p>


# Super Mario 64 ROM Randomizer Generator

This is a work in progress project to build an [OoT-Randomizer](https://www.ootrandomizer.com/)-style randomizer for Super Mario 64, that is highly configurable and easy to use.

# Features

- Works on all endianess' (`.z64`, `.n64`, `.v64`) and all regions (America, Europe, China, Japan, Japan Shindou).
- Works on ROMhacks (**Please note:** Romhacks can be vastly different. Please contact us in the discord if you have any trouble.)
- Randomizes Level Entries - Every Level will be a different one
- Randomizes Castle Paintings - To visually match the entrance of the level it now leads to. (*Levels without a castle painting will show as a brick wall.*)
- Randomizes Dialog
- Randomizes Music
- Randomizes Mario's Outfit
- Randomizes Coin Colors
- Randomizes Objects in Level
- Disables Cutscenes
- Disables Level Intros
- Disable Keydoors
- ...many more to come


The application is supported on everdrive. To ensure everdrive compatibility, please change the name to a shorter one, as that seems to cause issues. For further help, please visit the Discord Server.


Also auto extends ROM to work with the randomizer. If this fails, extend your ROM manually and use either [sm64extender](https://www.smwcentral.net/?p=viewthread&t=77343) or [Super Mario 64 ROM Extender](http://qubedstudios.rustedlogic.net/Mario64Tools.htm).

# Web
For extremely simple usage, simply use our existing web generator, found here: https://andre-meyer.github.io/sm64-randomizer/

![SM64 Randomizer Generator Web Edition](https://i.imgur.com/78OiLPZ.png)

### Usage
Follow instructions on the website. Upload your original SM64 rom, select the settings and press "Queue for generation" you'll quickly receive your randomized ROM.

# GUI
The randomizer includes a simple GUI for easy setup without any knowledge about the command line. Simply download the latest [release](/releases/latest) and open `SM64 Randomizer GUI`.

![SM64 Randomizer GUI](https://i.imgur.com/erEk4Dh.png)

### Install
1. Download the [latest release](/releases/latest)
2. Extract **all files** in a folder of your liking
3. Run SM64 Randomizer Generator.exe

### Usage
1. Select an Input ROM
2. Select an Output (will be automatically guessed to <rom>.out.<ending>)
3. Select your settings
- Choose a custom seed to share with friends who use the same tool
- Copy the settings string to copy your current settings to share with friends. Does not include seed.
4. Press "Generate"
5. Run output file on your emulator/console. :tada:

# CLI
For expert users who want to tinker with configurations, settings and test various roms, it's easier to use the program in CLI mode. To do this, run the application with additional arguments, and it will automatically work as a terminal tool. (For server owners: No graphical interface is required, if more than one argument is given.)

### Install
1. Download the [latest release](/releases/latest)
2. Extract **all files** in a folder of your liking
3. Run SM64 Randomizer Generator.exe in your terminal

### Usage
```
python main.py ./Super_Mario_64_(U)_[!].z64 --shuffle-levels --shuffle-mario-color --shuffle-paintings match --seed 123
```

_Note: Works on all versions of the game, as well as **ROM Hacks** (with some tweaking, contact us in [Discord](https://discord.gg/2ZYfhcB) for help)_

Output will be a file with the same name, ending in `.out.z64`. Run this on your emulator/console.

```
  Super Mario 64 Randomizer  (Version: 0.7.0)

usage: main.py [-h] [--no-extend] [--alignment ALIGNMENT] [--out OUT]
               [--version] [--seed SEED]
               [--shuffle-paintings {vanilla,match,random}]
               [--shuffle-entries] [--shuffle-mario-outfit] [--shuffle-music]
               [--shuffle-objects] [--shuffle-colors] [--shuffle-text]
               [--disable-cutscenes] [--disable-starwarp]
               [--stardoor-requirements {vanilla,random,open}]
               [--keydoor-requirements {vanilla,open}]
               rom

positional arguments:
  rom

optional arguments:
  -h, --help            show this help message and exit
  --no-extend           disable auto-extend of ROM, which might fail on some
                        systems
  --alignment ALIGNMENT
                        Specify the byte alignment. If you know this value,
                        you have a higher change of successfully randomizing
                        romhacks.
  --out OUT             target of randomized rom
  --version             show program's version number and exit
  --seed SEED           Allows you to play the same version as a friend,
                        simply enter the same seed as them and you will be
                        playing the exact same ROM.
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
  --keydoor-requirements {vanilla,open}
                        Changes how the locked keydoors in the castle work.
                        Vanilla means you will require the usual keys from the
                        Bowser fights. Open means they're simply open from the
                        start.
```

# Contributing: Getting Started
To work on this repository, follow the following steps. Please also definitely join the [discord](https://discord.gg/2ZYfhcB) for help.
1. `git clone` this repository
2. Make sure you somehow have python >3.6 (Mac OSX I suggest `brew install`, Linux I suggest `apt install python3`, windows I suggest the installer)
3. Create a `venv` via `python3 -m venv .` while inside the folder
4. Install dependencies via `pip install -r requirements-dev.txt`

# Special Thanks
- [hack64](http://hack64.net/)'s wonderful SM64 hacking resources, clean, easy to use and great in-depth details
- [SimpleFlips](https://www.youtube.com/user/SimpleFlips) Discord-Server for help with SM64 hacking/weirdness (especially Felegg)
- Durkhaz for the amazing logo
- CJay for server hosting of the generator
- Beta Testers and people from the [discord](https://discord.gg/2ZYfhcB)
- [smwcentral](https://www.smwcentral.net/)'s community and forum
