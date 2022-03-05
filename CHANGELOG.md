# 0.10.0

- Change random point algorithm to use points on available floor triangles, if a floor is required for placement.
- Fixes slope calculation, it actually works correctly now.
- Config fixes:
  - Peach-Slide: Don't randomize star-box.
  - All levels: Don't randomize vanish cap, it can make a level impossible.
  - Fix floor type "WATER_FLOWING" from metal cap level not being a viable floor for placement.
  - Fix heights/spawnheights and bounding boxes for coin formation. Still not perfect.

# 0.9.0

- Implemented automated build system
  - Fixed priority system of which rules to apply. The more specific a rule is, the more priority it will have. For example, a rule matching BOB will have less priority than a rule matching Goombas in BOB.
  - Fix distance_to calculations (takes forever though)
  - Cleanup

# 0.8.0

- Complete rewrite of how configurations work. Please see the `/Config` folder which contains `sm64.vanilla.yml`.
  - Improved support for many different romhacks, by allowing different configurations based on _checksums_.
  - Improved configurability of object placement, as they now support nested rules, rules under specific circumstances, grouping and many more.
  - Implemented "key" logic, to define certain levels as `requires_key` and others as `key_receive` - the value passed will be compared during randomization, to determine if the order is within logic.
  - Implemented matching for behaviour parameters, to shuffle coin formations.
  - Implemented logic for levels that have levels nested within them, but are not "overworld" levels, like HMC, which contains Metal Cap. All cap levels are now shuffled between each other.
  - Implemented "continues_level" which makes the randomizer treat the levels as being the same. This is to fix problems when beating Bowser battles.
  - All previous rules with additions from the SM64 Randomizer Discord were added to the new configuration.
  - For more information on how to write and alter configurations, consult the Configuration documentation, here: `/Config/README.md`
- Implemented _blacklisted_ regions for levels, to indicate areas _behind_ loading triggers. This is to avoid issues with unreachable objects.
- Implemented Bounding Box and Bounding Sphere checks, to improve the quality of placements for certain enemies like Mr. I and Bob-Omb King.
- Remove Texture for the tree shadows in castle grounds, so shuffled trees don't look weird.

### Older versions

Check [releases](github.com/andrelikesdogs/sm64-randomizer/releases) for older changelogs.
