from Constants import ALL_LEVELS, CAP_LEVELS, MISSION_LEVELS, BOWSER_STAGES, SPECIAL_LEVELS, BEHAVIOUR_NAMES
import Constants
from randoutils import format_binary, print_progress_bar
import random
import sys
import numpy as np
import logging
import trimesh
import os
import math

from RandomModules.Objects.Whitelist import RandomizeObjectsWhitelist, DEBUG_HIT_INDICES
from Entities.Object3D import Object3D
from Parsers.LevelScript import LevelScriptParser

from random import shuffle

# Walkable collision types on which to place objects
WALKABLE_COLLISION_TYPES = [
  0x00, # environment default
  0x29, # default floor with noise
  0x2A, # slippery floor with noise
  0x14, # slightly slippery
  0x15, # anti slippery
  0x0B, # close camera
  0x30, # hard floor (always fall damage)
  0x1A, # varied noise
  0x21, # sand
  0x35, # hard and slippery
  0x36, # slide
  0x37, # non slippery in ice level
  0x65, # wide cam
  0x70, # BOB: camera thing
  0x75, # CCM: camera thing
  0x76, # surface with flags
  0x79, # CCM: camera thing
  
  ## may be harder
  #0x13, # slippery
  #0x2A, # slippery with noise
  0x0D, # water (stationary)
]

WALL_CHECK_DIRECTIONS = [
  [1000.0, 0.0, 0.0],
  [0.0, 0.0, 1000.0],
  [-1000.0, 0.0, 0.0],
  [0.0, 0.0, -1000.0]
]

WALL_CHECK_DIRECTIONS_NORM = [
  [1.0, 0.0, 0.0],
  [0.0, 0.0, 1.0],
  [-1.0, 0.0, 0.0],
  [0.0, 0.0, -1.0],
]

class ObjectRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
    self.whitelist = RandomizeObjectsWhitelist(rom.config.object_entries)
    self.object_wall_traces = {}
    self.object_floor_traces = {}
    self.reject_reason_counts = {}

  def check_walls(self, area_id : int, levelscript : LevelScriptParser, position : list, rules : list):
    """ Check nearby walls from a position, trying to find "reverse normals" - walls facing away, indicating a position behind a wall.
    
    Arguments:
        area_id {int} -- area_id to check
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        position {list} -- Position that will be used for object placement
        rules {list} -- List of rules this randomization must obey

    Returns:
        bool -- Valid position?
    """
    call_signature = hash(tuple(position)) + hash(repr(rules)) + hash(area_id)

    if call_signature in self.object_wall_traces:
      return self.object_wall_traces[call_signature]

    mesh = levelscript.level_geometry.area_geometries[area_id]
    position[1] += 5

    valid_position = True
    invalid_ray = []
    for ray_index, direction in enumerate(WALL_CHECK_DIRECTIONS_NORM):
      # for all compass directions
      trace_pos = position
      tri_index, _ = mesh.ray.intersects_id(ray_origins=[trace_pos], ray_directions=[direction], multiple_hits=False)
      # only care about the first triangle index this ray hit

      if len(tri_index) > 0:
        # we've hit a triangle, what is the normal?

        tri_index = tri_index[0]
        wall_dir = mesh.face_normals[tri_index]
        check_dir = direction

        angle = (check_dir[0] * wall_dir[0] + check_dir[1] * wall_dir[1] + check_dir[2] * wall_dir[2])
        # angle between the two positions. positive = facing towards, negative = facing away

        if angle > 0:
          valid_position = False
          break

    self.object_wall_traces[call_signature] = valid_position
    return valid_position    

  def check_floor(self, area_id : int, levelscript : LevelScriptParser, position : list, rules : list):
    """ Validate the floor beneath a position, to see if this position is valid for placement
    
    Arguments:
        area_id {int} -- area_id to check
        position {list} -- position to check
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        rules {list} -- The rules this object has to obey for placement
    """
    call_signature = hash(tuple(position)) + hash(repr(rules)) + hash(area_id)

    if call_signature in self.object_floor_traces:
      return self.object_floor_traces[call_signature]
    
    self.object_floor_traces[call_signature] = False
    mesh = levelscript.level_geometry.area_geometries[area_id]

    triangle_indices, ray_indices, locations = mesh.ray.intersects_id(
      ray_origins=[position],
      ray_directions=[[0.0, -20000.0, 0.0]],
      return_locations=True,
      multiple_hits=False
    )

    if len(locations):
      triangle_index = triangle_indices[0]
      ray_index = ray_indices[0]
      location = list(map(lambda x: int(round(x)), locations[0]))
      
      collision_type = levelscript.level_geometry.get_collision_type_for_triangle(area_id, triangle_index)

      if collision_type in WALKABLE_COLLISION_TYPES:
        result = dict(
          position=location,
          triangle_index=triangle_index,
          triangle_normal=mesh.face_normals[triangle_index]
        )
        self.object_floor_traces[call_signature] = result
    
    return self.object_floor_traces[call_signature]

  def drop_position(self, area_id : int, levelscript : LevelScriptParser, position : list, rules : list):
    """ Drop a position onto the floor below it
    
    Arguments:
        area_id {int} -- area_id to check
        position {list} -- position to check
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        rules {list} -- The rules this object has to obey for placement
    """

    floor_trace = self.check_floor(area_id, levelscript, position, rules)
    
    if floor_trace is not False:
      return floor_trace["position"]
    
    return position

  def inside_forbidden_boundary(self, area_id : int, levelscript : LevelScriptParser, position: list):
    """ Check if a potential position is inside any of the levels forbidden boundary boxes.
    
    Arguments:
        area_id {int} -- area_id to check
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains the position
        position {list} -- position to check
    
    Returns:
        [booleaan] -- True when inside any level or area boundary box.
    """
    for boundary in levelscript.level_geometry.level_forbidden_boundaries:
      if boundary.contains([position]):
        #print("Object position inside level loading zone")
        return True
    
    if area_id in levelscript.level_geometry.area_forbidden_boundaries:
      for boundary in levelscript.level_geometry.area_forbidden_boundaries[area_id]:
        if boundary.contains([position]):
          #print("Object position inside area loading zone")
          return True
    
    return False

  def is_in_water_box(self, area_id : int, water_boxes : list, position : list):
    """ Check if a position is inside a waterbox for the given area.
    
    Arguments:
        area_id {int} -- area_id to check
        water_boxes {list} -- List of waterboxes for the Level
        position {list} -- position to check
    
    Returns:
        bool -- Is the position in water?
    """

    applicable_waterboxes = list(filter(lambda box: box["area_id"] == area_id, water_boxes))

    if not len(applicable_waterboxes):
      return False

    for water_box in applicable_waterboxes:
      if water_box["type"] != "WATER":
        continue
        
      if position[0] > water_box["start"][0] and position[0] < water_box["end"][0] and position[1] > water_box["start"][1] and position[1] < water_box["end"][1] and position[2] > water_box["start"][2] and position[2] < water_box["end"][2]:
        return True
    return False

  def is_valid_position(self, levelscript : LevelScriptParser, obj : Object3D,position, rules : list):
    """ Validate if this position is valid for the given object, position and for the rules that are given to this method.
    
    Arguments:
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        obj {Object3D} -- Target object that is going to be randomized
        position {list} -- Position that is requested
        rules {list} -- List of rules this randomization must obey
    """

    if not self.check_walls(obj.area_id, levelscript, position, rules):
      return False

    if self.inside_forbidden_boundary(obj.area_id, levelscript, position):
      return False

    floor_properties = self.check_floor(obj.area_id, levelscript, position, rules)

    if "no_floor_required" not in rules or rules["no_floor_required"] != True:
      if floor_properties is False:
        return False

    if "min_y" in rules:
      if position[1] < rules["min_y"]:
        return False

    if "max_y" in rules:
      if position[1] > rules["max_y"]:
        return False

    if "distance" in rules:
      for distance_rules in rules["distance"]:
        origin = distance_rules["origin"]

        distance = math.sqrt(
          (position[0] - origin[0]) ** 2 +
          (position[1] - origin[1]) ** 2 +
          (position[2] - origin[2]) ** 2
        )

        if "max_distance" in distance_rules:
          if distance > distance_rules["max_distance"]:
            return False

        if "min_distance" in distance_rules:
          if distance > distance_rules["min_distance"]:
            return False
      
    if "max_slope" in rules and floor_properties is not False:
      floor_slope = floor_properties["triangle_normal"][1]

      # 1 = Floor. 0 = Wall.
      if floor_slope < abs(float(rules["max_slope"])):
        return False
    
    if "underwater" in rules:
      underwater_status = rules["underwater"]

      if underwater_status == "only":
        if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          return False
      elif underwater_status == "never":
        if self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          return False
      elif underwater_status == "allowed" or underwater_status == True:
        pass

    if "bounding_box" in rules:
      pass

    return True

  def modify_position(self, levelscript : LevelScriptParser, obj : Object3D, position, rules : list):
    """ Modifies the position of the target object, if possible. This means dropping it onto the floor, moving it away from something, moving it closer to something.
    
    Arguments:
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        obj {Object3D} -- Target object that is going to be randomized
        position {list} -- Potential position that is requested
        rules {list} -- List of rules this randomization must obey
    
    Returns:
        list -- new position, that needs to be validated for validity/sanity
    """

    if "drop_to_floor" in rules:
      # this object is supposed to be dropped onto the floor
      if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position) or rules["drop_to_floor"] == "force":
        # if objest is in water, don't modify the position, except when forced
        position = self.drop_position(obj.area_id, levelscript, position, rules)
      
    if "spawn_height" in rules:
      # object can spawn in the air, decide on a height and validate
      if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position) or rules["drop_to_floor"] == "force":
        min_height, max_height = tuple(rules["spawn_height"])

        position[1] += random.randint(min_height, max_height)

    return position

  def generate_random_point_for(self, levelscript : LevelScriptParser, obj : Object3D, rules : list):
    """ Generate a random point for the target object, within the bounding box of this objects area.
    
    Arguments:
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        obj {Object3D} -- Target object that is going to be randomized
        rules {list} -- List of rules this randomization must obey
    
    Returns:
        list -- position, that needs to be validated for validity/sanity
    """
    area_id = obj.area_id

    if area_id not in levelscript.level_geometry.area_geometries:
      print(obj)
      print(rules)
      raise ValueError(f"{area_id} not found in geometry. This probably means a rule is matching too many objects, like a star selector.")
    area_mesh = levelscript.level_geometry.area_geometries[area_id]

    (bounds_min, bounds_max) = area_mesh.bounds
    (x, y, z) = bounds_min

    if abs(bounds_min[0] - bounds_max[0]) > 0:
      x = random.randrange(bounds_min[0] + 1000, bounds_max[0] - 1000)
    
    if abs(bounds_min[1] - bounds_max[1]) > 0:
      y = random.randrange(bounds_min[1], bounds_max[1])

    if abs(bounds_min[2] - bounds_max[2]) > 0:
      z = random.randrange(bounds_min[2] + 1000, bounds_max[2] - 1000)
      
    return [x, y, z]

  def shuffle_objects(self):
    object_randomization_count = 0


    for level, levelscript in self.rom.levelscripts.items():
      for object_idx, object3d in enumerate(levelscript.objects):
        object3d.meta["randomization"] = "UNTOUCHED"
        levelscript.level_geometry.add_object_point_of_interest(object3d)

        if "disabled" in level.properties:
          # level is disabeld
          continue

        whitelist_entry = self.whitelist.get_shuffle_properties(object3d)
        
        if "SM64R_DEBUG" in os.environ and "PRINT" in os.environ["SM64R_DEBUG"].split(','):
          print_progress_bar(object_idx, len(levelscript.objects), f'Placing Objects', f'{level.name}: ({object_idx} placed)')
          
        # randomization not defined, thus not allowed - continue to next one
        if not whitelist_entry:
          continue

        randomizing_rules = whitelist_entry["rules"]

        # randomization disabled - continue to next one
        if "disabled" in randomizing_rules and randomizing_rules["disabled"] == True:
          continue

        found_valid_point = False
        tries = 0


        while not found_valid_point:
          tries += 1

          if tries > 1000:
            object3d.meta["randomization"] = "SKIPPED"
            #print()
            print(f"Used Rule: {whitelist_entry['name']}")
            print(f"Warning: No valid position found for {object3d.behaviour_name} in {level.name} ({hex(level.course_id)}) (Area: {hex(object3d.area_id)}) after 1000 tries, bailing.")
            break

          # 1. Generate a random point
          possible_position = self.generate_random_point_for(levelscript, object3d, randomizing_rules)

          # 2. Check for a valid "preposition" - basic checks to ensure some viability
          if not self.is_valid_position(levelscript, object3d, possible_position, randomizing_rules):
            continue

          # 3. Modify the position - certain rules will adjust the final position of the object by ie dropping it to the floor
          new_position = self.modify_position(levelscript, object3d, possible_position, randomizing_rules)

          # 4. Verify final position
          if not self.is_valid_position(levelscript, object3d, new_position, randomizing_rules):
            continue
          
          found_valid_point = True
          object_randomization_count += 1
          object3d.set(self.rom, "position", new_position)
          object3d.meta["randomization"] = "RANDOMIZED"

    print(f"Randomized {object_randomization_count} objects")

    # unused whitelist entries
    """
    for index, entry in enumerate(self.whitelist.whitelist):
      if index not in DEBUG_HIT_INDICES:
        print(f"WARNING: Whitelist Entry \"{entry.name}\" was never used.")
    """