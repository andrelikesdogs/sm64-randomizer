# Super Mario 64 ROM Randomizer

This is a work in progress project to build an [https://github.com/AmazingAmpharos/OoT-Randomizer](OoT-Randomizer)-style randomizer for Super Mario 64.

# Usage CLI
To use this package, download the repository and run using **python >= 3.5**, passing your Vanilla SM64 ROM or an Extended ROM:
```
python main.py ./Super_Mario_64_(U)_[!].z64
```
_Note: Only accepts z64 format. Currently only supports North American version_

Output will be a file with the same name, ending in `.out.z64`. Run this in your emulator.

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

## Sources
- http://hack64.net/
- https://www.smwcentral.net/
