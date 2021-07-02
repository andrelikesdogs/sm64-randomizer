from pathlib import Path
import json
import os

from sm64r.Constants import application_path
from sm64r.Entities import Object3D

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
      if len(object3d.bparams) < 1 or object3d.bparams[0] != matching["bparam1"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam2" in matching:
      if len(object3d.bparams) < 2 or object3d.bparams[1] != matching["bparam2"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam3" in matching:
      if len(object3d.bparams) < 3 or object3d.bparams[2] != matching["bparam3"]:
        return (matches, False)
      else:
        matches += 1

    if "bparam4" in matching:
      if len(object3d.bparams) < 4 or object3d.bparams[3] != matching["bparam4"]:
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

    # check against all matching/whitelist entries
    for whitelist_entry in self.object_whitelist:
      if whitelist_entry["match"] is None:
        continue

      # if whitelist entry has an exclude property, see if we can skip this entry
      if whitelist_entry["exclude"] is not None:
        _, match_exclude = self.matches_with(whitelist_entry["exclude"], object3d)

        if match_exclude:
          continue
      
      # the more precise the matching, the more priority it will have
      matches, did_match = self.matches_with(whitelist_entry["match"], object3d)

      # increase priority for matches from "for" rules
      if "from_for" in whitelist_entry and whitelist_entry["from_for"]:
        matches += 1

      if did_match and matches > best_match_count:
        best_match = whitelist_entry
        best_match_count = matches
    return best_match