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

DEBUG_HIT_INDICES = {}

class RandomizeObjectsWhitelist:
  def __init__(self, whitelist):
    self.object_whitelist = whitelist
    
  def matches_with(self, matching, object3d):
    matches = 0

    # don't match empty sets
    if not len(matching.keys()):
      return (matches, False)

    if "behaviours" in matching:
      if object3d.behaviour is None:
        return (matches, False)
      elif object3d.behaviour not in matching["behaviours"]:
        return (matches, False)
      else:
        matches += 1


    if "model_id" in matching:
      if object3d.model_id is None:
        return (matches, False)
      elif matching["model_id"] != object3d.model_id:
        return (matches, False)
      else:
        matches += 1
      
    if "source" in matching:
      if matching["source"] != object3d.source:
        return (matches, False)
      else:
        matches += 1

    if "course_id" in matching:
      if object3d.level is None or object3d.level.course_id is None:
        return (matches, False)
      elif matching["course_id"] != object3d.level.course_id:
        return (matches, False)
      else:
        matches += 1

    if "course_property" in matching:
      # course property check for current area and for current level
      found_in_level_or_area = False
      matching_property = matching["course_property"]

      # areas
      if object3d.area_id in object3d.level.areas:
        if matching_property in object3d.level.areas[object3d.area_id].properties:
          found_in_level_or_area = True

      # level
      if matching_property in object3d.level.properties:
        found_in_level_or_area = True

      if not found_in_level_or_area:
        return (matches, False)
      else:
        matches += 1
    
    if "bparam1" in matching:
      if object3d.bparams[0] != matching["bparam1"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam2" in matching:
      if object3d.bparams[1] != matching["bparam2"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam3" in matching:
      if object3d.bparams[2] != matching["bparam3"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam4" in matching:
      if object3d.bparams[3] != matching["bparam4"]:
        return (matches, False)
      else:
        matches += 1

    if "area_id" in matching:
      if matching["area_id"] != object3d.area_id:
        return (matches, False)
      else:
        matches += 1

    return (matches, True)
  
  def get_shuffle_properties(self, object3d : Object3D):
    best_match = None
    best_match_count = 0
    for whitelist_entry in self.object_whitelist:
      if whitelist_entry["match"] is None:
        continue

      if whitelist_entry["exclude"] is not None:
        _, match_exclude = self.matches_with(whitelist_entry["exclude"], object3d)

        if match_exclude:
          continue
      
      # the more precise the matching, the more priority it will have
      matches, did_match = self.matches_with(whitelist_entry["match"], object3d)
      if did_match and matches > best_match_count:
        '''
        if best_match is not None and object3d.behaviour == 0x13002aa4:
          print("replacing rule ", best_match)
          print("with rule ", whitelist_entry)
        '''
        best_match = whitelist_entry
        best_match_count = matches
    return best_match