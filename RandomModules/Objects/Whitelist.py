from Constants import application_path
from Entities import Object3D
from pathlib import Path
import json
import os

### Rules that are implemented
#  Name           | Description                     | Properties
# -------------------------------------------------------------------
# DROP_TO_FLOOR   | Drop onto floor below?          | bool|string - True, "FORCE"
# UNDERWATER      | Can this object be underwater?  | string - "ALLOWED", "ONLY", "NEVER"
# MAX_SLOPE       | Max slope allowed benath        | float - Max Slope allowed
#                 | (0 = wall, 1 = floor)           |
# DISABLED        | Use to overwrite and            | bool - True
#                 | disable a rule                  |
# SPAWN_HEIGHT    | Sets range in which height      | [int, int] - List of min and max height
#                 | this object can spawn           |
# MIN-Y           | spawn above specific y          | int - Min Height
# MAX-Y           | spawn under specific y          | int - Max Height

VALID_RULE_NAMES = [
  "DROP_TO_FLOOR", "UNDERWATER", "MAX_SLOPE", "DISABLED", "SPAWN_HEIGHT", "MIN_Y", "MAX_Y", "DISTANCE_TO", "DISABLE", "NO_FLOOR_REQUIRED", "BOUNDING_BOX"
]

HEX_VALUES = ["course_id", "area_id", "behaviour", "model_id", "bparam1", "bparam2", "bparam3", "bparam4"]

VALID_MATCH_TYPES = [*HEX_VALUES, "source"]

DEFAULT_RULES = dict(
  DROP_TO_FLOOR=True,
  MAX_SLOPE=0.8,
  UNDERWATER="ALLOWED"
)

DEBUG_HIT_INDICES = {}

class WhitelistEntry:
  name: str = "Invalid Entry"
  match: dict
  rules: dict
  priority: int = 1

  def __init__(self, name : str, match : dict, rules : dict, priority : int):
    self.name = name
    self.match = match
    self.rules = rules
    self.priority = priority

  def __str__(self):
    return f"<Whitelist Entry: \"{self.name}\" Matching: {repr(self.rules)}>"

class RandomizeObjectsWhitelist:
  def __init__(self):
    self.whitelist = []
    
    random_whitelist_dir = os.path.join(application_path, "Config", "randomizeObjects")
    for filename in os.listdir(random_whitelist_dir):
      file = Path(filename)

      if file.suffix == '.json':
        file_path = Path(os.path.join(random_whitelist_dir, file))

        with open(file_path, "r") as json_whitelist:
          entries = json.loads(json_whitelist.read())

          for entry_index, entry in enumerate(entries):
            if "name" not in entry:
              raise ValueError(f"Error in randomizeObjects.json: Please specify a (unique) name for entry #{entry_index}")
            if "match" not in entry:
              raise ValueError(f"Error in randomizeObjects.json: Please specify a matching property for \"{entry['name']}\"")
            
            normalized_match = {}
            for key, value in entry["match"].items():
              new_value = value
              if key not in VALID_MATCH_TYPES:
                raise ValueError(f"Error in randomizeObjects.json: Invalid matching type \"{key}\"")
              if key in HEX_VALUES:
                if str(value).startswith("0x"):
                  new_value = int(str(value), base=16)
                else:
                  new_value = int(value)
              normalized_match[key] = new_value
            #print(normalized_match)
            rules = {**DEFAULT_RULES}

            if "rules" in entry:
              rules = {
                **rules,
                **entry["rules"]
              }

            for rule in list(rules.keys()):
              if rule not in VALID_RULE_NAMES:
                raise ValueError(f"Error in randomizeObjects.json: Invalid rule \"{rule}\"")
            
            rule_priority = 1
            if "priority" in entry:
              rule_priority = int(entry["priority"])

            whitelist_entry = WhitelistEntry(entry["name"], normalized_match, rules, rule_priority)
            self.whitelist.append(whitelist_entry)
    pass

  def matches_with(self, object3d, entry : WhitelistEntry):
    matching = entry.match

    if "behaviour" in matching:
      if object3d.behaviour is None:
        return False
      if matching["behaviour"] != object3d.behaviour:
        return False

    if "model_id" in matching:
      if object3d.model_id is None:
        return False
      if matching["model_id"] != object3d.model_id:
        return False
      
    if "source" in matching and matching["source"] != object3d.source:
      return False

    if "course_id" in matching:
      if object3d.level is None or object3d.level.level_id is None:
        return False
      if matching["course_id"] != object3d.level.level_id:
        return False
    
    if "bparam1" in matching:
      if object3d.bparams[0] != matching["bparam1"]:
        return False

    if "bparam2" in matching:
      if object3d.bparams[1] != matching["bparam2"]:
        return False

    if "bparam3" in matching:
      if object3d.bparams[2] != matching["bparam3"]:
        return False

    if "bparam4" in matching:
      if object3d.bparams[3] != matching["bparam4"]:
        return False

    if "area_id" in matching and matching["area_id"] != object3d.area_id:
      return False

    return True
  
  def get_shuffle_properties(self, object3d : Object3D):
    possible_matches = []
    for entry_index, entry in enumerate(self.whitelist):
      if self.matches_with(object3d, entry):
        if entry_index not in DEBUG_HIT_INDICES:
          DEBUG_HIT_INDICES[entry_index] = 0
        DEBUG_HIT_INDICES[entry_index] += 1

        possible_matches.append(entry)
    
    if not len(possible_matches):
      return False

    # matches without "behaviour", "source" or "model_id" don't work alone
    without_extension_matches = list(filter(lambda entry: "model_id" in entry.match or "behaviour" in entry.match or "source" in entry.match, possible_matches))
    if not len(without_extension_matches):
      return False

    # sort matches by prio
    sorted_matches = list(sorted(possible_matches, key=lambda possible_match: possible_match.priority))

    rules = {**sorted_matches[0].rules}

    for entries in sorted_matches:
      rules = {**rules, **entries.rules}

    return rules
