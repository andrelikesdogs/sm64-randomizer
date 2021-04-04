import random
import sys
import numpy as np
import logging
import trimesh
import os
import math
from time import time

from sm64r.Constants import ALL_LEVELS, CAP_LEVELS, MISSION_LEVELS, BOWSER_STAGES, SPECIAL_LEVELS, BEHAVIOUR_NAMES
from sm64r.Randoutils import format_binary, print_progress_bar

from .Whitelist import RandomizeObjectsWhitelist, DEBUG_HIT_INDICES
from sm64r.Entities.Object3D import Object3D
from sm64r.Parsers.LevelScript import LevelScriptParser

from random import shuffle

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
    self.reject_reasons_by_module = {}
    self.current_reject_log = None

    if os.path.exists("sm64_rando_reject.log"):
      os.unlink("sm64_rando_reject.log")
  
  def start_reject_log(self, for_object3d, in_level, area_id):
    if self.current_reject_log is not None:
      raise AssertionError("already started a reject-log - flush previous one")
      
    self.current_reject_log = dict(
      object3d=for_object3d,
      level=in_level,
      area_id=area_id
    )

  def flush_last_reject_log(self):
    if self.current_reject_log is None:
      return
    #  raise AssertionError("no reject log active - start reject log")
    
    if len(self.reject_reasons_by_module.keys()) > 0:
      with open("sm64_rando_reject.log", "a") as reject_log:
        level = self.current_reject_log["level"]
        area_id = self.current_reject_log["area_id"]
        obj = self.current_reject_log["object3d"]
        reject_log.write(f"< Reject-Log for: {obj.behaviour_name} {level.name} ({hex(level.course_id)}) (Area: {hex(area_id)})>\n")

        for module in self.reject_reasons_by_module:
          reject_log.write(f"  {module} Module\n")

          for reason in self.reject_reasons_by_module[module]:
            reject_log.write(f"    {reason}: Occurred x{self.reject_reasons_by_module[module][reason]}\n")
          reject_log.write("\n")
    
    self.current_reject_log = None
    self.reject_reasons_by_module = {}
    
  def log_reason_for_reject(self, module, reason):
    if module not in self.reject_reasons_by_module:
      self.reject_reasons_by_module[module] = {}

    if reason not in self.reject_reasons_by_module[module]:
      self.reject_reasons_by_module[module][reason] = 1
    else:
      self.reject_reasons_by_module[module][reason] += 1

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

    # cache the check at this pos
    call_signature = hash(tuple(position)) + hash(repr(rules)) + hash(area_id)

    # TODO: check for all corners of a bounding box, if that rule exists

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

      result = dict(
        position=location,
        collision_type=collision_type,
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
      self.log_reason_for_reject("drop_position", "no floor underneath object")
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

  def is_valid_position(self, levelscript : LevelScriptParser, obj : Object3D,position, rules : list, is_pre_position : bool = False):
    """ Validate if this position is valid for the given object, position and for the rules that are given to this method.
    
    Arguments:
        levelscript {LevelScriptParser} -- Levelscript for the Level that contains this object3d
        obj {Object3D} -- Target object that is going to be randomized
        position {list} -- Position that is requested
        rules {list} -- List of rules this randomization must obey
    """

    if not self.check_walls(obj.area_id, levelscript, position, rules):
      self.log_reason_for_reject("is_valid_position", "object failed wall check")
      return False

    if self.inside_forbidden_boundary(obj.area_id, levelscript, position):
      self.log_reason_for_reject("is_in_waterbox", "object found in forbidden boundary")
      return False

    floor_properties = self.check_floor(obj.area_id, levelscript, position, rules)

    # check for floor if the rule is set and True
    if "no_floor_required" not in rules or rules["no_floor_required"] != True:
      if floor_properties is False:
        self.log_reason_for_reject("is_valid_position", "object floor required but none found")
        return False

    # check the floor type if the rule is set and the floor exists and the floor type isn't "all"
    if "no_floor_required" not in rules and "floor_types_allowed" in rules and floor_properties is not False:
      if rules["floor_types_allowed"] == "all":
        if floor_properties["collision_type"] not in self.rom.config.constants["collision_types"].values():
          self.log_reason_for_reject("is_valid_position", f'object floor type is "all" but "{hex(floor_properties["collision_type"])}" is unknown')
          return False

      if rules["floor_types_allowed"] not in self.rom.config.collision_groups:
        self.log_reason_for_reject("is_valid_position", f'unknown {rules["floor_types_allowed"]} floor type')
        return False
      else:
        if floor_properties["collision_type"] not in self.rom.config.collision_groups[rules["floor_types_allowed"]].values():
          self.log_reason_for_reject("is_valid_position", 'object floor type was not allowed')
          return False

    if "disable_planes" in obj.level.properties:
      for entry in obj.level.properties["disable_planes"]:
        plane_type = list(entry.keys())[0]
        (start, end) = entry[plane_type]
        lower = min(start, end)
        upper = max(start, end)

        if plane_type == "y_range":
          if position[1] > lower and position[1] < upper:
            #print(position, " is between ", (lower, upper))
            self.log_reason_for_reject("is_valid_position", "in level disable plane")
            return False

    if "min_y" in rules:
      if position[1] < rules["min_y"]:
        #print("min_y", position, rules["min_y"])
        self.log_reason_for_reject("is_valid_position", "object position below min_y")
        return False

    if "max_y" in rules:
      if position[1] > rules["max_y"]:
        #print("max_y", position, rules["max_y"])
        self.log_reason_for_reject("is_valid_position", "object position above max_y")
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
            self.log_reason_for_reject("is_valid_position", "object too far away from origin")
            return False

        if "min_distance" in distance_rules:
          if distance > distance_rules["min_distance"]:
            self.log_reason_for_reject("is_valid_position", "object too close to origin")
            return False
      
    if "max_floor_steepness" in rules and floor_properties is not False:
      floor_slope = floor_properties["triangle_normal"][1]

      # 1 = Floor. 0 = Wall.
      slope_allowed = abs(float(rules["max_floor_steepness"]) - 1.0)
      # validate steep-ness (must be this steep)
      if floor_slope < slope_allowed: 
        self.log_reason_for_reject("is_valid_position", "floor too steep")
        return False
    
    if "underwater" in rules:
      underwater_status = rules["underwater"]

      if underwater_status == "only":
        if not self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          self.log_reason_for_reject("is_valid_position", "can only be in water but was not in waterbox")
          return False
      elif underwater_status == "never":
        if self.is_in_water_box(obj.area_id, levelscript.water_boxes, position):
          self.log_reason_for_reject("is_valid_position", "can never be in water but was in waterbox")
          return False
      elif underwater_status == "allowed" or underwater_status == True:
        pass

    if not is_pre_position and "bounding_cylinder" in rules:
      cylinder_def = rules["bounding_cylinder"]
      radius = cylinder_def[0]
      height = cylinder_def[1] if len(cylinder_def) > 1 else 100
      orig_x = cylinder_def[2] if len(cylinder_def) > 2 else 0
      orig_y = cylinder_def[3] if len(cylinder_def) > 3 else 0
      orig_z = cylinder_def[4] if len(cylinder_def) > 4 else 0

      target_position = [
        position[0] + orig_x,
        position[1] + orig_y,
        position[2] + orig_z
      ]

      # positions here are in weird hand (y is up/down)
      for face_index, (start, end) in enumerate(levelscript.level_geometry.area_face_aabbs[obj.area_id]):
        # check height
        if (start[1] > target_position[1] or end[1] > target_position[1]) or (start[1] < (target_position[1] + height) or end[1] < (target_position[1] + height)):
          # atleast one vert is within cylinder
          #print(face_index, len(levelscript.level_geometry.area_faces[obj.area_id]))
          tri_verts = levelscript.level_geometry.area_faces[obj.area_id][face_index]
          for vert in list(map(lambda x: levelscript.level_geometry.area_vertices[obj.area_id][x], tri_verts)):
            # y is ignored to calc without height differences, as they were previously checked
            distance = math.sqrt(
              (target_position[0] - vert[0]) ** 2 +
              (target_position[2] - vert[2]) ** 2
            )

            if distance < radius:
              #print(distance, radius)
              self.log_reason_for_reject("is_valid_position", "bounding cylinder intersection encountered")
              return False

    if not is_pre_position and "bounding_box" in rules:
      extents = [ # x, z, y
        -rules["bounding_box"][0], # x neg
        rules["bounding_box"][2], # y and z swap
        rules["bounding_box"][1]
      ]

      y_rot = (obj.rotation[1] * math.pi / 180)

      # rotate points
      vertices = [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1,
                  1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1]
      vertices = np.array(vertices, order='C', dtype=np.float64).reshape((-1, 3))
      
      vertices -= 0.5
      vertices *= extents
      
      translation_matrix = trimesh.transformations.translation_matrix(position)
      rotation_matrix = trimesh.transformations.rotation_matrix(y_rot, [0, 1, 0])

      concat_matrix = trimesh.transformations.concatenate_matrices(translation_matrix, rotation_matrix)

      translated_points = trimesh.transform_points(vertices, concat_matrix)
      
      #t = trimesh.transformations.translation_matrix(position)
      #r = trimesh.transformations.rotation_matrix(y_rot, [0, 1, 0])
      
      #bounding_pos = trimesh.transformations.concatenate_matrices(t, r)
      
      #bounding_box = trimesh.creation.box(extents=extents, transform=bounding_pos)

      # this will overwrite existing bounding meshes for the same obj
      #levelscript.level_geometry.add_object_bounding_mesh(obj, obj.area_id, bounding_box)

      #levelscript.level_geometry.area_collision_managers[obj.area_id].in_collision(f'{obj.name} bounding box', bounding_box, bounding_pos)

      # intersection check with world
      for (start, end) in levelscript.level_geometry.area_face_aabbs[obj.area_id]:
        for point in translated_points:
          if (point[0] > start[0] and point[0] < end[0]) and (point[1] > start[1] and point[1] < end[1]) and (point[2] > start[2] and point[2] < end[2]):
            self.log_reason_for_reject("is_valid_position", "bounding box intersection encountered")

            if 'SM64R' in os.environ and 'PLOT' in os.environ['SM64R']:
              t = trimesh.transformations.translation_matrix(position)
              r = trimesh.transformations.rotation_matrix(y_rot, [0, 1, 0])
              bounding_pos = trimesh.transformations.concatenate_matrices(t, r)
              bounding_box = trimesh.creation.box(extents=extents, transform=bounding_pos)
              #print(bounding_box.vertices)
              #print(translated_points)

              tri_extents = [
                abs(start[0] - end[0]),
                abs(start[1] - end[1]),
                abs(start[2] - end[2])
              ]
              tri_position = [
                (start[0] if start[0] > end[0] else end[0]) - (tri_extents[0]/2),
                (start[1] if start[1] > end[1] else end[1]) - (tri_extents[1]/2),
                (start[2] if start[2] > end[2] else end[2]) - (tri_extents[2]/2),
              ]

              tri_box = trimesh.creation.box(extents=tri_extents, transform=trimesh.transformations.translation_matrix(tri_position))

              #self.debug_placement(levelscript, obj, bounding_box, tri_box)
            
            return False

      '''# check if intersects with WORLD
      intersections = levelscript.level_geometry.area_geometries[obj.area_id].intersection(
        bounding_box
      )

      if not intersections.is_empty:
        self.log_reason_for_reject("is_valid_position", "bounding box intersection encountered")
        self.debug_placement(levelscript, obj, bounding_box)
        return False
      '''
      

      #return bounding_box
      #pass

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

    if "no_floor_required" not in rules:
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

  def debug_placement(self, levelscript : LevelScriptParser, obj : Object3D, *boundary):
    levelscript.level_geometry.plot_placement(obj, *boundary)

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
      raise ValueError(
        f"""{area_id} not found in geometry but only in an excluded area, that means it is not a valid object and should not be selected.\n
        This probably means a rule is matching too many objects, like a star selector object."""
      )
    area_mesh = levelscript.level_geometry.area_geometries[area_id]

    (bounds_min, bounds_max) = area_mesh.bounds
    (x, y, z) = bounds_min

    # position for boundary is slightly overshot, probably because of some shit i forgot to write here while it happened
    if abs(bounds_min[0] - bounds_max[0]) > 0:
      x = random.randrange(bounds_min[0] + 1000, bounds_max[0] - 1000)
    
    if abs(bounds_min[1] - bounds_max[1]) > 0:
      y = random.randrange(bounds_min[1], bounds_max[1])

    if abs(bounds_min[2] - bounds_max[2]) > 0:
      z = random.randrange(bounds_min[2] + 1000, bounds_max[2] - 1000)
      
    return [x, y, z]

  def shuffle_objects(self):
    object_randomization_count = 0

    try:
      for level, levelscript in self.rom.levelscripts.items():
        for object_idx, object3d in enumerate(levelscript.objects):
          self.start_reject_log(object3d, level, object3d.area_id)
          object3d.meta["randomization"] = "UNTOUCHED"
          levelscript.level_geometry.add_object_point_of_interest(object3d)

          if "disabled" in level.properties:
            # level is disabeld
            self.flush_last_reject_log()
            continue

          whitelist_entry = self.whitelist.get_shuffle_properties(object3d)
          
          if "SM64R" in os.environ and "PRINT" in os.environ["SM64R"].split(','):
            print_progress_bar(object_idx, len(levelscript.objects), f'Placing Objects', f'{level.name}: ({object_idx} placed)')
            
          # randomization not defined, thus not allowed - continue to next one
          if not whitelist_entry:
            self.flush_last_reject_log()
            continue

          randomizing_rules = whitelist_entry["rules"]

          # randomization disabled - continue to next one
          if "disabled" in randomizing_rules and randomizing_rules["disabled"] == True:
            #print(object3d.level.name, object3d, "is disabled")
            self.flush_last_reject_log()
            continue

          found_valid_point = False
          tries = 0

          try_start = time()
          while not found_valid_point:
            if time() - try_start > 10:
              object3d.meta["randomization"] = "SKIPPED"
              #print()
              print(f"Used Rule: {whitelist_entry['name']}")
              print(f"Warning: No valid position found for {object3d.behaviour_name} in {level.name} ({hex(level.course_id)}) (Area: {hex(object3d.area_id)}) after 10s, bailing.")
              self.flush_last_reject_log()
              break
            
            # 1. Generate a random point inside the bounds of the current level(area)
            possible_position = self.generate_random_point_for(levelscript, object3d, randomizing_rules)

            # 2. Check for a valid "preposition" - basic checks to ensure some viability
            if not self.is_valid_position(levelscript, object3d, possible_position, randomizing_rules, True):
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
            self.flush_last_reject_log()
    except KeyboardInterrupt:
      self.flush_last_reject_log()
      print("Cancelled Object Randomization")

    print(f"Randomized {object_randomization_count} objects")

    # unused whitelist entries
    """
    for index, entry in enumerate(self.whitelist.whitelist):
      if index not in DEBUG_HIT_INDICES:
        print(f"WARNING: Whitelist Entry \"{entry.name}\" was never used.")
    """