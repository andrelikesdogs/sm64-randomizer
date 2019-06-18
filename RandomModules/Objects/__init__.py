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
"""
# List of items that can be shuffled within the game
# This list consists of a model-id and behaviour address. If one of them is None, any will match
WHITELIST_SHUFFLING = [
  (None, 0xBC), # Bob-Omb
  (0x13003174, None), # Bob-Omb
  (0x1300472C, None), # Goomba,
  (0x13004770, None), # Goomba Triplet
  (0x13001298, None), # Coin Triplet
  (0x130001F4, None), # King Bob-Omb
  (0x13002BB8, None), # King Whomp
  (0x130039D4, None), # Moneybag
  (None, 0x68), # Koopa (The Quick, Normal, etc)
  #(0x130005B4, None), # Rotating Platform WF
  (0x13002AA4, None), # Tree Behaviour
  (None, 0x65), # Scuttlebug
  (None, 0x19), # Tree (Snow)
  (None, 0x17), # Tree (In Courses)
  (None, 0x18), # Tree (Courtyard)
  (None, 0x1B), # Tree (SSL)
  (0x13001548, None), # Heave-Ho
  (None, 0x78), # Heart
  (0x13004348, None), # Red Coin
  (0x13003E8C, None), # Red Coin Star
  (0x13002EC0, None), # Mario Spawn
  (0x13005468, None), # Skeeter (WDW Bug thing)
  (0x13000BC8, None), # Thwomp
  (0x13000B8C, None), # Thwomp 2
  (0x1300525C, None), # Grindel
  (0x13001FBC, None), # Piranha
  (0x13005120, None), # Fire-Spitting
  (0x13002EF8, None), # Toad
  (0x130009A4, None), # Single Coin
  (0x13000964, None), # Coins (x3)
  (0x13000984, None), # Coins (x10)
  (0x130008EC, None), # Coins (Formations)
  (0x13005440, 0x58), # Clam in JRB
  (0x13004634, None), # Pokey
  (0x13004668, 0x55), # Pokeys Head
  # (0x13002588, None), # Blue Coin # Invisible coin shuffling is a bad idea
  (None, 0x7C), # Sign
  (0x13003EAC, 0xD7),
  (None, 0x74), # Coin Type 1
  (None, 0x75), # Coin Type 2
  (None, 0x74), # Coin Type 3
  (None, 0x75), # Multiple Coins
  (None, 0xD4), # One-Up
  (0x13001F3C, None), # Koopa Shell
  (0x130020E8, 0x57), # Lost Penguin
  (0x13002E58, None), # Wandering Penguin
  (0x13004148, 0xD4), # Homing-One-Up
  (0x130031DC, 0xC3), # Bob-Omb Buddy (With Message)
  (0x13003228, None), # Bob-Omb Buddy (Opening Canon)
  (0x1300478C, 0x66),
  (0x13000528, 0xDF), # Chuckya
  (0x13000054, None), # Eye-Ball
  (0x13001108, None), # Flamethrower
  (0x1300518C, None), # Flamethrower
  (0x130046DC, 0xDC), # Fly-Guy
  (None, 0x89), # Item-Box
  (0x13004698, None), # Bat
  (0x130046DC, None), # Fly-Guy
  (0x13004918, None), # Lakitu
  (0x13004954, None), # Evil Lakitu
  (0x130049C8, None), # Spiny
  (0x13004A00, None), # Mole
  (0x13004A58, None), # Mole in Hole
  (0x13003700, 0x65), # Ice Bully (Big)
  (0x130036C8, 0x64), # Ice Bully (Small)
  (0x13001650, 0x00), # Bouncing Box
  (0x130027E4, 0x65), # Boo
  (0x130027D0, 0x00), # Boo (x3)
  (0x13002794, 0x65), # Big Boo
  (0x130007F8, 0x7A), # Star
  (0x13003E3C, 0x7A), # Star
  #(0x13001B70, 0x00), # Checkerboard Elevator (Logic: DON'T TOUCH FOR VANISH CAP LEVEL)
  (0x13002F74, 0x00), # Mario Start 1
  (0x13003354, None), # Amp
  (0x13003388, None), # Amp 2
  (0x130033BC, None), # Butterflies
  (0x1300442C, None), # TTC: Pendulum
  (0x130054B8, None), # TTC: Pendulum
  (0x13004FD4, None), # BBH: Haunted Chair
  (0x13005024, None), # BBH: Piano
  (0x1300506C, None), # BBH: Bookend
]

# Allowed variance in object height, for example to have a star be slightly above ground
ITEM_HEIGHT_VARIANCE = {
  (None, 0x89): [200, 500], # Star
  (None, 0x7A): [200, 500], # Star
  (0x13002250, None): [100, 500], # Item Block
  (0x13004348, None): [100, 200], # Red Coin
  (0x130009A4, None): [100, 200], # Single Coin
  (0x13002588, None): [100, 200], # Blue Coin
}

# Items that can not be placed in water, or they won't work anymore. i.e. Item-Boxes underwater are not breakable
CANT_BE_IN_WATER = [
  (None, 0x89), # Item Box
  (0x13003700, None), # Ice Bully (Big) - otherwise you win instantly
  (0x130031DC, 0xC3), # Bob-Omb Buddy (With Message)
  (0x13003228, None) # Bob-Omb Buddy (Opening Canon)
]
"""
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

WINGCAP_LEVELS = [
  Constants.LVL_WING_CAP,
  Constants.LVL_SECRET_RAINBOW
]

COMPASS_NAMES = ["N", "E", "S", "W"]

DEATH_PLANE_START = -7000

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
      
      if distance > rules["DISTANCE_TO"]["max_distance"]:
        return False

    if "MAX_SLOPE" in rules and floor_properties is not False:
      floor_slope = floor_properties["triangle_normal"][1]

      # 1 = Floor. 0 = Wall.
      if floor_slope < float(rules["MAX_SLOPE"]):
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
      x = random.randrange(bounds_min[0], bounds_max[0])
    
    if abs(bounds_min[1] - bounds_max[1]) > 0:
      y = random.randrange(bounds_min[1], bounds_max[1])

    if abs(bounds_min[2] - bounds_max[2]) > 0:
      z = random.randrange(bounds_min[2], bounds_max[2])
      
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
            print(f"Warning: No valid position found for {object3d} after 1000 tries, bailing.")
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

"""
  @staticmethod
  def can_shuffle(obj : Object3D):
    if obj.source == "MARIO_SPAWN":
      return True
    else:
      # Hardcoded Static Wing-Cap Box for Wingcap Level
      if obj.level == Constants.LVL_WING_CAP and obj.behaviour == 0x13002250:
        return False
      
      for (target_bscript_address, target_model_id) in WHITELIST_SHUFFLING:
        if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
          return True
      return False

  def get_height_offset(self, obj : Object3D):
    for (target_bscript_address, target_model_id) in ITEM_HEIGHT_VARIANCE:
      if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
        (minimum, maximum) = tuple(ITEM_HEIGHT_VARIANCE[(target_bscript_address, target_model_id)])

        return random.randrange(minimum, maximum)
    return 1 # fallback to ensure it doesn't fail oob check or falls out of level

  def can_be_in_water(self, obj : Object3D):
    for (target_bscript_address, target_model_id) in CANT_BE_IN_WATER:
      if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
        return False
    return True

  def is_in_water_box(self, area_id, water_boxes, position):
    applicable_waterboxes = list(filter(lambda box: box["area_id"] == area_id, water_boxes))

    if not len(applicable_waterboxes):
      return False

    for water_box in applicable_waterboxes:
      if water_box["type"] != "WATER":
        continue
      #print("checking waterbox")
      if position[0] > water_box["start"][0] and position[0] < water_box["end"][0] and position[1] > water_box["start"][1] and position[1] < water_box["end"][1] and position[2] > water_box["start"][2] and position[2] < water_box["end"][2]:
        return True
    return False

  def get_floor_pos(self, level_script, area, position):
    mesh = level_script.level_geometry.area_geometries[area]

    if position[1] < DEATH_PLANE_START:
      # death plane
      #print("death plane")
      return False

    index_tri, index_ray, locations = mesh.ray.intersects_id(
      ray_origins=[position],
      ray_directions=[[0.0, -20000.0, 0.0]],
      return_locations=True,
      multiple_hits=False
    )

    if len(locations):
      first_floor_index = index_tri.item(0)

      if locations[0][1] < DEATH_PLANE_START:
        return False
      
      collision_type = level_script.level_geometry.get_collision_type_for_triangle(area, first_floor_index)
      #print(hex(collision_type))
      if collision_type not in WALKABLE_COLLISION_TYPES:
        return False
    else:
      return False
    
    return (locations[0], index_tri[0])

  def check_walls(self, level_script, area, position):
    mesh = level_script.level_geometry.area_geometries[area]
    position[1] += 5

    valid_position = True
    invalid_ray = []
    for ray_index, direction in enumerate(WALL_CHECK_DIRECTIONS_NORM):
      trace_pos = position
      #trace_pos[1] += 2
      tri_index, _ = mesh.ray.intersects_id(ray_origins=[trace_pos], ray_directions=[direction], multiple_hits=False)

      if len(tri_index) > 0:
        tri_index = tri_index[0]
        # hit a triangle, what is the normal?
        wall_dir = mesh.face_normals[tri_index]
        check_dir = direction

        angle = (check_dir[0] * wall_dir[0] + check_dir[1] * wall_dir[1] + check_dir[2] * wall_dir[2])
        if angle > 0:
          self.reject_reason_counts[f"wall_facing_away_{COMPASS_NAMES[ray_index]}"] += 1
          invalid_ray.append(ray_index)
          valid_position = False
          if "SM64R_DEBUG" not in os.environ or os.environ["SM64R_DEBUG"] != 'PLOT':
            break

    # debug stuff
    if "SM64R_DEBUG" in os.environ and os.environ["SM64R_DEBUG"] == 'VIEWER' and level_script.level == Constants.LVL_TTC:
      debug_tri_indices, debug_ray_indices, debug_locations = mesh.ray.intersects_id(ray_origins=[position, position, position, position], ray_directions=[*WALL_CHECK_DIRECTIONS], multiple_hits=False, return_locations=True)
      if len(debug_locations) > 0:
        print(level_script.level.name)
        for face_index, normal in enumerate(mesh.face_normals):
          tri_color = (10, 10, 10, 200)
          if normal[1] > 0.8:
            tri_color = (255, 0, 0, 255)
          #else:
          #  if normal[1] > 0.01:
          #    tri_color =(0, 255, 0, 200)
          #  elif normal[1] < -0.01:
          #    tri_color = (255, 0, 0, 200)
          
          mesh.visual.face_colors[face_index] = tri_color
        
        
        path_vertices = []
        path_entities = []

        for ray_index, direction in enumerate(WALL_CHECK_DIRECTIONS_NORM):
          path_vertices.append(
            position
          )
          path_vertices.append(
            debug_locations[ray_index] if ray_index in debug_ray_indices else position + (np.array(direction) * 1000)
          )
          path_entities.append(
            trimesh.path.entities.Line(points=[len(path_vertices) - 2, len(path_vertices) - 1])
          )

        normal_paths = []
        normal_entities = []
        for face_index, vertices in enumerate(mesh.triangles):
          #print(len(mesh.face_normals), len(face_indices))
          normal = mesh.face_normals[face_index]
          origin = np.mean(vertices, axis=0)
          direction = origin + normal * 100
          
          normal_paths.append(origin)
          normal_paths.append(direction)
          normal_entities.append(trimesh.path.entities.Line(points=[len(normal_paths) - 2, len(normal_paths) - 1]))
        
        scene = trimesh.Scene([
          mesh,
          trimesh.path.path.Path(vertices=normal_paths, entities=normal_entities),
          trimesh.path.path.Path(vertices=path_vertices, entities=path_entities),
        ])
        scene = scene.scaled(0.02)

        scene.show()
      # end debug stuff
  

    return valid_position

  def get_valid_position(self, level_script, object3d, position, rules):
    level = level_script.level

    # check if there's floor underneath
    result = self.get_floor_pos(level_script, object3d.area_id, position)

    is_in_water = self.is_in_water_box(object3d.area_id, level_script.water_boxes, position)

    can_be_in_water = self.can_be_in_water(object3d)

    ### Begin Level Fixes ###
    # Hardcoded fix for THI red coins spawning in wiggler
    if level_script.level == Constants.LVL_THI and object3d.area_id == 0x03:
      if position[1] > 1740:
        return False

    # Hardcoded fix for JRB Item-Box in Ship
    if level_script.level == Constants.LVL_JRB and object3d.area_id == 0x02:
      is_in_water = False
      can_be_in_water = True

    # Hardcoded fix for WDW Item-Box
    if level_script.level == Constants.LVL_WDW:
      is_in_water = False
      can_be_in_water = True

    ### End Level Fixes ###

    # Is this object in waterbox?
    if is_in_water:
      # can this object be inside a waterbox?
      if not can_be_in_water:
        #print(f'{object3d.behaviour_name} cant be in water')
        #print("is in water; invalid")
        self.reject_reason_counts["cant_be_in_water"] += 1
        return False

    mesh = level_script.level_geometry.area_geometries[object3d.area_id]

    # if its a level with a wingcap available
    if level in WINGCAP_LEVELS:
      if level == Constants.LVL_WING_CAP:
        if position[1] > -300:
          return False
        if position[1] < -3000:
          return False
      else:
        if position[1] > mesh.bounds[1][1] - 2000:
          # make sure it's below the highest point of the level or it's unobtainable
          return False
        if position[1] < mesh.bounds[0][1] + 1000:
          # make sure it's not touching the death floor
          return False
    else:
      if result is False:
        #print("no floor underneath")
        self.reject_reason_counts["no_floor_found"] += 1
        return False

      (floor_check_position, triangle_index) = result
      # if not in water, drop onto floor
      if not is_in_water:
        # drop onto floor
        position = floor_check_position

        is_dropped_in_water = self.is_in_water_box(object3d.area_id, level_script.water_boxes, position)
        if is_dropped_in_water and not can_be_in_water:
          #self.reject_reason_counts["cant_be_in_water"] += 1
          return False

        # only outside water, check if the floor might be too steep
        too_steep = mesh.face_normals[triangle_index][1] < 0.6

        if too_steep:
          self.reject_reason_counts["floor_too_steep"] += 1
          return False
      
      height_offset = self.get_height_offset(object3d)
      position[1] += height_offset

    # check for normals of walls nearby
    if not self.check_walls(level_script, object3d.area_id, position):
      return False

    return position
  
  def generate_random_point(self, obj, levelscript, rules):
    area_id = obj.area_id
    area_mesh = levelscript.level_geometry.area_geometries[area_id]

    (bounds_min, bounds_max) = area_mesh.bounds
    (x, y, z) = bounds_min

    if levelscript.level == Constants.LVL_THI:
      pass

    if abs(bounds_min[0] - bounds_max[0]) > 0:
      x = random.randrange(bounds_min[0], bounds_max[0])
    
    if abs(bounds_min[1] - bounds_max[1]) > 0:
      y = random.randrange(bounds_min[1], bounds_max[1])

    if abs(bounds_min[2] - bounds_max[2]) > 0:
      z = random.randrange(bounds_min[2], bounds_max[2])
      
    return [x, y, z]



  def shuffle_objects(self):
    idx = 0
    for (level, parsed) in self.rom.levelscripts.items():
      if level in SPECIAL_LEVELS:
        continue

      # debug only set BoB
      #if level != Constants.LVL_TTM:
      #  continue

      randomizable_objects = []
      object_whitelist_rules = []


      for object3d in parsed.objects:
        whitelist_entry = whitelist.get_shuffle_properties(object3d)

        if whitelist_entry is not False:
          randomizable_objects.append(object3d)
          object_whitelist_rules.append(whitelist_entry.rules)
      
      total = len(randomizable_objects)
      rejects = 0

      self.reject_reason_counts = {
        "cant_be_in_water": 0,
        "no_floor_found": 0,
        "floor_too_steep": 0,
        "wall_facing_away_N": 0,
        "wall_facing_away_S": 0,
        "wall_facing_away_W": 0,
        "wall_facing_away_E": 0
      }

      #for other_object in other_objects:
      #  parsed.level_geometry.add_debug_marker(other_object.position, other_object, color=(100, 100, 255))

      while len(randomizable_objects) > 0:
        obj = randomizable_objects.pop()
        rules = object_whitelist_rules.pop()

        point = self.generate_random_point(obj, parsed, rules)
        
        valid_pos = self.get_valid_position(parsed, obj, point, rules)
        if valid_pos is False:
          shufflable_objects.append(obj)
          rejects += 1
        else:
          obj.set(self.rom, 'position', tuple([int(p) for p in list(valid_pos)]))
          reasons_formated = ', '.join([f'{k}: {v}' for [k, v] in self.reject_reason_counts.items()])
          if "SM64R_DEBUG" in os.environ and "PRINT" in os.environ["SM64R_DEBUG"].split(','):
            print_progress_bar(total - len(shufflable_objects), total, f'Placing Objects', f'{level.name}: ({total - len(shufflable_objects)} placed, {rejects} rejected)')
          """