# SM64 Randomizer Configuration Files

All files in this folder (/Config) will be loaded by the program to determine which configuration should be used for which ROM. For the vanilla ROM, all regions and endianesses it will be `sm64.vanilla.yml`. Check that file to understand the Syntax and the format of the configuration file.

The order in which these files are loaded is sorted alphabetically. If you require configuration files with the same checksums, start the one with higher priority with a character higher in the alphabet.

# Documentation

## `name`: `string`
Sets a name for the configuration file, this name will be shown in the CLI to help users figure out which configuration was used for their ROM.

## `rom`: `object`
Starts the definition of ROM specific configurations

### `rom[].checksum`: `int,int[]`
Checksum(s) that will match this specific ROM configuration as hex numbers, i.e. `0x0000001`. If any of these checksums match, it will use this configuration.

### `rom[].name`: `string`
Name of this ROM configuration, can include information about Endianess, Region, ROM-Type (Extended, Vanilla) to further narrow down which configuration was used. This information is only visible when using the CLI.

### `rom[].macro_table_address`: `int`
Start of Macro Object Preset Table. This table is used to determine which macro preset id corresponds to which object. If you're unsure about this, it is most likely the same as the default. Check `sm64.vanilla.yml`

### `rom[].special_macro_table_address`: `int`
Start of Special Macro Object Preset Tabel. This table is sued to determine which special macro preset id corresponds to which object. If you're unsure about this, it is most likely the same as the default. Check `sm64.vanilla.yml`

### `rom[].defined_segments[]`
This section defines segments that are loaded by default. This varries by region. If you're unsure about this, it is most likely the same as the default. Check `sm64.vanilla.yml`

### `rom[].defined_segments[].segment`: `int`
Segment ID of the segment that will be auto-loaded in this particular ROM.

### `rom[].defined_segments[].read_addresses`: `bool`
Should the addresses defined as `start` and `end` be used to look up the addresses that define the segment, or are the addresses themselves the addresses that define this segment. If `read_addresses` is true, it will read the defined `start` and `end` addresses to determine the start and end.

### `rom[].defined_segments[].start`: `int`
Start of segment

### `rom[].defined_segments[].end`: `int`
End of segment

## `levels`
This will define which levels this ROM contains and also their paintings, if they have one. It is also used to determine which levels have special properties, like `overworld`, `slide` and many others. see [level properties](#level-properties)

### `levels[].name`: `string`
The name of the level. Displayed as information for the user and to make this file human readable.

### `levels[].course_id`: `int`
The internal course-id. Not the games course numbers.

### `levels[].properties`: `object`
Properties that this level contains. These can disable/enable certain functionality, alter rules, ensure order, define the painting for this level and many more. See [level properties](#level-properties).

### `levels[].exclude`: `object`
Properties that this level **can not** contain. See `levels[].properties`

### `levels[].areas[]`
If a level contains different areas with different properties, those can be defined here as well. 

### `levels[].areas[].id`: `int`
ID of the area, so it can be identified by the program.

### `levels[].areas[].name`: `string`
Name of the area, for human readability and user information in the CLI.

### `levels[].areas[].properties`
Properties that this area contains. These disable/enable certain functionality, alter rules, ensure order, define the painting for this level and many more. See [level properties](#level-properties).

### `levels[].areas[].exclude`: `object`
Properties that this level **can not** contain. See `levels[].properties`

## `object_randomization`
Start of nested object definition table. This sections consists of `rules`, defining which rules to enforce for this group, `match`, defining which objects it should match with and `objects`, defining more specific objects or types of objects that need special properties too.

### `object_randomization.rules`
Which rules to enforce for this object definition group. See [rules](#rules) for a complete list and documentation of rules.

### `object_randomization.match`
Which objects will match this object definition group. This key is optional and without it, object definition groups can be used to group together multiple objects that should all have the same or similar rules. See [matching](#matching) for a complete list of ways to match different kinds of objects.

### `object_randomization.for`: `string[]`
You can use this property to "copy" a set of rules here. Use the full name of the object definition group you want to include here.

### `object_randomization.objects[]`
This allows you to nest more objects. `object_randomization` is the root definition, defining default rules. All rules further down the table will overwrite rules defined closer to the root.

# Level Properties

## `overworld`: `bool`
This will enable this level to be searched for level entries. All levels containing this property will be searched.

## `shuffle_warps`: `array`
This will enable this level to be searched for specific warps to specific levels, that can be shuffled with other warps. For example to shuffle between only the cap-levels in vanilla.

### `shuffle_warps[].to[]`
Warps to _which_ levels can be found with this property?

### `shuffle_warps[].to[].course_id`: `int`
Defines the course-id that should be matched.

### `shuffle_warps[].to[].area_id`: `int
Defines the area-id that should be matched.

### `shuffle_warps[].with[].course_id`: `int`
Defines the course-id that it can be shuffled with. The program will select one of the entries in `with`

### `shuffle_warps[].with[].area_id`: `int`
Defines the area-id that it can be shuffled with. It will only match complete sets, so if your `with` entry is 
```yml
- course_id: 0x01
  area_id: 0x01
```
it will use the whole set of `course_id` and `area_id`

## `shuffle_painting`: `object`
This will enable painting shuffling. The paintings are hardcoded right now. This will soon be altered to include the texture positions that need to be exchanged. For now, the valid values are:

The painting of a level can be defined, if the level can be associated to one. This will allow the randomizer to shuffle the various defined paintings in the game, to either: randomize them unrelated to the current randomized level entries, change them according to the randomized level entries, or fully replace them with a custom painting, if applicable. See [paintings](#paintings)

- `painting_bob`
- `painting_ccm`
- `painting_wf`
- `painting_jrb`
- `painting_lll`
- `painting_ssl`
- `painting_wdw`
- `painting_thi`
- `painting_ttm`
- `painting_ttc`
- `painting_sl`

## `slide`: `bool`
This will enable special checks and rules for slide levels, such as:
- Spawn must remain about the same height, otherwise you start in the middle of the slide.
- Coin/Object spawns are less restrictive about slope placement, so it can still be placed on the slide.

## `fly_stage`: `bool`
This will enable special checks and rules for level with a wing-cap available, or where a wing-cap is your main method of movement.
- Spawns can be over death-floor

## `disable_water_check`: `bool`
Use this in level where water can be changed, to allow the program to place objects underwater.
- Disables underwater rules

## `requires_key`: `int`
Defines which "key" is needed for this level, if it were unshuffled. In combination with `key_receive` you can define which levels need to be available before *this* level can be reached.

## `key_receive`: `int`
Defines that this level will reward the player with a "key" after completion. Can be used to ensure correct order of levels.

## `continues_level`: `int`
Defines that this level will _continue_ as another level, i.e. bowser and bowser-fight levels. This is to ensure that the exit warps in the _continued_ level are also changed to the same exit warps as the current level. The value passed is the `course_id` of the target level.

## `disabled`: `object, bool`
The `disabled` as a boolean property disables all randomization properties for this level or area. Includes `object_randomization`, `painting_shuffle` and `entry_shuffle`

If an array of properties is defined, only those will be disabled.

## `end_game`: `bool`
Defines that this marks the end of the game.

# Rules

## `drop_to_floor`: `bool,string`
If set to string `force`, it will `drop_to_floor` even underwater. Otherwise underwater this rule will be ignored, so things float at any height in water.

This will set this object to drop down onto floor level when its position will be defined.

## `no_floor_required`: `bool`
If this property is set, the floor check will be skipped if no floor is found

## `max_slope`: `float`
Defines the maximum slope allowed. `1.0` is a wall. `0.0` is completely flat floor. A value of `0.0` will ensure only completely flat floors are considered as valid positions.

## `min_y`: `int`
Minimum absolute `y` coordinate of this object. Useful to limit spawning to be above a certain height. Use Quad64 to look up positions.

## `max_y`: `int`
Maximum absolute `y` coordinate of this object. Useful to limit spawning to be below a certain height. Use Quad64 to look up positions.

## `bounding_box`: `[int, int, int]`
Defines a bounding box for this object to check if it might clip into floor/walls. The order is `length` x `width` x `height`

## `spawn_height`: `[int, int]`
Defines the minimum and maximum spawn height allowed. The program will select a value between these two. For reference: Triple-Jump height is ~550

## `underwater`: `bool,string`
Allowed properties: `allowed`, `only`, `never`
If this property is set to `true` it will be `allowed` - if this property is set to `false` it will be `never`
`allowed` - Can be both above and underwater
`only` - Can only be underwater
`never` - Can never be underwater

# Matching

## `[default]`: `int,int[]`
If no other properties are necessary, you can directly define the behaviour address this object is supposed to match with. i.e.:
```yml
- match: 0x13002250
```

or to define multiple:
```yml
- match:
  - 0x13002250
  - 0x13002251
```

## `behaviour`: `int,int[]`
Can match one or more behaviour script addresses as integers. Same as `[default]`

## `source`: `string`
Allowed values:
- `PLACE_OBJ` spawned with the `0x20` command
- `MACRO_OBJ` spawned with the `0x39` command
- `SPECIAL_MACRO_OBJ` spawned with the `0x2E` command
- `MARIO_SPAWN` marios spawn inside this level via level command `0x2B`

## `course_property`: `string`
Matches specific property keys from a course.
See [level properties](#level-properties)

## `bparam[n]`: `any`
This is to match specific behaviour parameters. There is 4 in total from [1-4]. Only `0x20 (PLACE_OBJ)` objects will have all 4. Look up Behaviour Scripts for SM64 to find which behaviour parameters do what.


## Misc. Information

#### Debugging Mode
Using the Environment variable "SM64R" you can select different debugging modes. The allowed modes are

* `PRINT` - Enables more verbose output
* `PLOT` - Plots level geometries using plot.ly. Install requirements-dev to use.

#### Positioning of Objects, Bounds, etc.
When taking the position from the plot.ly graphs, be sure to convert all positions from the labels like so:

in Plotly: `[X, Y, Z]`
in Config: `[-X, Z, Y]`

i.e. when taking the position from `[100, 200, 300]` plot.ly use it in the config as `[-100, 300, 200]`

This issue is occouring because plot.ly and sm64 use different conventions for the order and directions of vectors. :shrug: