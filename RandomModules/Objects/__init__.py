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
    self.whitelist = RandomizeObjectsWhitelist()
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

    floor_properties = self.check_floor(obj.area_id, levelscript, position, rules)

    if "NO_FLOOR_REQUIRED" not in rules:
      if floor_properties is False:
        return False

    if "MIN_Y" in rules:
      if position[1] < rules["MIN_Y"]:
        return False

    if "MAX_Y" in rules:
      if position[1] > rules["MAX_Y"]:
        return False

    if "DISTANCE_TO" in rules:
      origin_position = rules["DISTANCE_TO"]["origin"]
      distance = math.sqrt(
        (position[0] - origin_position[0]) ** 2 +
        (position[1] - origin_position[1]) ** 2 +
        (position[2] - origin_position[2]) ** 2
      )
      
      if "max_distance" in rules["DISTANCE_TO"]:
        if distance > rules["DISTANCE_TO"]["max_distance"]:
          return False

      if "min_distance" in rules["DISTANCE_TO"]:
        if distance > rules["DISTANCE_TO"]["min_distance"]:
          return False

    if "MAX_SLOPE" in rules and floor_properties is not False:
      floor_slope = floor_properties["triangle_normal"][1]

      # 1 = Floor. 0 = Wall.
      if floor_slope < abs(float(rules["MAX_SLOPE"])):
        return False
    
    if "UNDERWATER" in rules:
      underwater_status = rules["UNDERWATER"]

      if underwater_status == "ONLY":
        if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          return False
      elif underwater_status == "NEVER":
        if self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          return False
      elif underwater_status == "ALLOWED":
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

    if "DROP_TO_FLOOR" in rules:
      # this object is supposed to be dropped onto the floor
      if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position) or rules["DROP_TO_FLOOR"] == "FORCE":
        # if objest is in water, don't modify the position, except when forced
        position = self.drop_position(obj.area_id, levelscript, position, rules)
      
    if "SPAWN_HEIGHT" in rules:
      # object can spawn in the air, decide on a height and validate
      if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position) or rules["DROP_TO_FLOOR"] == "FORCE":
        min_height, max_height = tuple(rules["SPAWN_HEIGHT"])

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
    area_mesh = levelscript.level_geometry.area_geometries[area_id]

    (bounds_min, bounds_max) = area_mesh.bounds
    (x, y, z) = bounds_min

    if levelscript.level == Constants.LVL_THI:
      pass

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
        randomizing_rules = self.whitelist.get_shuffle_properties(object3d)
        
        if "SM64R_DEBUG" in os.environ and "PRINT" in os.environ["SM64R_DEBUG"].split(','):
          pass
          #print_progress_bar(object_idx, len(levelscript.objects), f'Placing Objects', f'{level.name}: ({object_idx} placed)')
          
        # randomization not defined, thus not allowed - continue to next one
        if not randomizing_rules:
          #print(object3d, 'not in whitelist')
          continue

        # randomization disabled - continue to next one
        if "DISABLE" in randomizing_rules:
          continue

        found_valid_point = False
        tries = 0


        while not found_valid_point:
          tries += 1

          if tries > 1000:
            print()
            print(f"Warning: No valid position found for {object3d.behaviour_name} in {level.name} (Area: {hex(object3d.area_id)}) after 1000 tries, bailing.")
            break

          # 1. Generate a random point
          potential_position = self.generate_random_point_for(levelscript, object3d, randomizing_rules)

          # 2. Check for a valid "preposition" - basic checks to ensure some viability
          if not self.is_valid_position(levelscript, object3d, potential_position, randomizing_rules):
            continue

          # 3. Modify the position - certain rules will adjust the final position of the object by ie dropping it to the floor
          new_position = self.modify_position(levelscript, object3d, potential_position, randomizing_rules)

          # 4. Verify final position
          if not self.is_valid_position(levelscript, object3d, new_position, randomizing_rules):
            continue
          
          found_valid_point = True
          object_randomization_count += 1
          object3d.set(self.rom, "position", new_position)
        
    print(f"Randomized {object_randomization_count} objects")

    # unused whitelist entries
    for index, entry in enumerate(self.whitelist.whitelist):
      if index not in DEBUG_HIT_INDICES:
        print(f"WARNING: Whitelist Entry \"{entry.name}\" was never used.")
