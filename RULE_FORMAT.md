# Object Randomization Ruleset

To enable quick and easy shuffle properties for different objects in the game, a data-driven solution was added to the tool to aid for easier collaboration.

This is the list of rules that the tool will understand and act upon. Every rule consists of atleast 3 properties:
- `name` - A unique name for this object, for human readability
- `match` - Determine when this rule will be active (On which Object, in which Level?)
- `rules` - A list of restrictions that need to be enforced when this rule is active
- `priority` (optional) - An integer value indicating the importance of this rule. See blow.


### Object searching via `match`
To identify an object that will be randomized multiple different ways of identification are available
- `behaviour` - The behaviour address of the object. Specify in hex format as string. i.e. `0x13000821A`
- `model_id` - Model IDs are specific to the level they were loaded in, but can further narrow a search. Specify in hex format as string. i.e. `0x6C`
- `source` - A source determine in which way this object was spawned, with one exception being marios spawn. Possible values: `MARIO_SPAWN`, `PLACE_OBJ` (`0x24`), `MACRO_OBJ`, `SPECIAL_MACRO_OBJ`
- `area_id` - Matches objects that are defined within a specific area. Specify in hex format as string, i.e. `0x01`
- `course_id` - Matches objects that are defined in certain levels, to only apply in one specific level. Specify in hex format as string, i.e. `0x1C`

### Object ruleset prioritisation
Priorities determine the importance of this ruleset being enforced. The highest integer number for the applicable ruleset matches will be used. For example:
- Object "Item Box" has a ruleset with priority 1. This is to ensure it spawns above ground and never in water.
- The Level Wet-Dry World requires objects to be able to spawn in water, because technically the whole level is submerged in water. This will use priority 5. (Leave space for more edge-cases)
- The Item Box with a vanish-cap can not spawn inside the cage, or it will be unreachable and so will be everything inside the cage. This will use priority 10.

### Object randomization rules
Below is a list of all possible rules that can be used.

- `DROP_TO_FLOOR` - This object needs to be placed on the floor directly
- `DISABLE` - Disable randomization for this object, as if it were not included in the list at all
- `SPAWN_HEIGHT` - Define which heights this object can spawn in
  - `options.min_height` - Minimum required height
  - `options.max_height` - Maximum height allowed
- `MAX_SLOPE` - Limits the slope that can be found underneath the object (whetever it is floating above it or not)
  - `value` - Maximum slope allowed as a floating point number. `1` is completely flat. `0` is a wall.
- `NOT_UNDERWATER` - Can never spawn underwater
- `ONLY_UNDERWATER` - Can only spawn underwater
- `ALLOW_UNDERWATER` - Allowed but not required

### Examples
