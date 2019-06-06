from Constants import ALL_LEVELS, CAP_LEVELS, MISSION_LEVELS, BOWSER_STAGES, LVL_BOB, SPECIAL_LEVELS, LVL_MAIN_SCR, LVL_CASTLE_GROUNDS, BEHAVIOUR_NAMES
from randoutils import format_binary
import random
import sys
import numpy as np
from Entities.Object3D import Object3D
import logging
#from Parsers.LevelScript import LevelScriptParser

from random import shuffle

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
  (0x130030A4, None), # Blue Coin
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
  #(None, 0xDF), # Chuckya
  (0x13000054, None), # Eye-Ball
  (0x13001108, None), # Flamethrower
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
  (0x1300442C, None), # TTC: Pendulum
  (0x130054B8, None), # TTC: Pendulum
  (0x13004FD4, None), # BBH: Haunted Chair
  (0x13005024, None), # BBH: Piano
  (0x1300506C, None), # BBH: Bookend
]

BSCRIPT_START = 0x10209C

HEIGHT_OFFSETS = {
  (None, 0x89): 200,
  (0x130007F8, 0x7A): 200, 
  (0x13002250, None): 200,
  (None, 0x75): 300,
}

CANT_BE_IN_WATER = [
  (None, 0x89), # Star
  (0x13003700, None), # Ice Bully (Big) - otherwise you win instantly
  (0x130031DC, 0xC3), # Bob-Omb Buddy (With Message)
  (0x13003228, None) # Bob-Omb Buddy (Opening Canon)
]

WALKABLE_COLLISION_TYPES = [
  0x00, # environment default
  0x29, # default floor with noise
  0x14, # slightly slippery
  0x15, # anti slippery
  0x0B, # close camera
  0x30, # hard floor (always fall damage)

  ## may be harder
  #0x13, # slippery
  #0x2A, # slippery with noise
  0x0D, # water (stationary)
]

def signed_tetra_volume(a, b, c, d):
  return np.sign(np.dot(np.cross(b-a, c-a), d-a)/6.0)

def trace_geometry_intersections(level_geometry, ray, face_type = None):
  # algorithm that was used for this:
  # http://www.lighthouse3d.com/tutorials/maths/ray-triangle-intersection/
  # or maybe this
  # https://wiki2.org/en/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
  [q0, q1] = ray
  ray_origin = q0
  ray_vector = q1 - q0
  #print("origin", ray_origin)
  #print("dir", ray_vector)

  ray_is_vertical = ray_vector[0] == 0.0 and ray_vector[1] == 0.0

  faces = level_geometry.get_triangles(face_type) # [[[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]]]

  intersection_count = 0
  intersection_positions = []
  intersection_faces = []
  for face in faces:
    #print("next face", face.index)
    [p1, p2, p3] = face.vertices
    [xmin, xmax, ymin, ymax, zmin, zmax] = face.bounding_box

    # precheck bounds
    if ray_is_vertical:
      # for vertical rays we can quickly check if the coordinates are atleast in the bounding box of the tri
      if ray_origin[0] < xmin or ray_origin[0] > xmax or ray_origin[1] < ymin or ray_origin[1] > ymax:
        #print('oob precheck')
        continue

    edge_a = p2 - p1
    edge_b = p3 - p1

    h = np.cross(ray_vector, edge_b)
    a = np.dot(edge_a, h)

    if abs(a) < 0e-10:
      #print("parallel")
      continue
    
    f = 1.0/a
    s = ray_origin - p1
    u = f * (np.dot(s, h))

    if u < 0.0 or u > 1.0:
      #print("u outside 0-1")
      continue

    q = np.cross(s, edge_a)
    v = f * (np.dot(ray_vector, q))
    
    if v < 0.0 or u + v > 1.0:
      #print("v < 0 or u + v > 1")
      continue
    
    t = f * np.dot(edge_b, q)
    if t > 0e-10:
      #print("hit")
      intersection_count += 1
      intersection_positions.append(
        ray_origin + ray_vector * t
      )
      intersection_faces.append(face)
      continue
    #print("doesnt reach", t)

  return (intersection_count, intersection_positions, intersection_faces)

  """
  [q0, q1] = ray
  triangles = level_geometry.get_triangles() # [[[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]]]

  intersection_count = 0
  intersection_positions = []
  for triangle in triangles:
    [p1, p2, p3] = triangle
    signed_volume_a = signed_tetra_volume(q0, p1, p2, p3)
    signed_volume_b = signed_tetra_volume(q1, p1, p2, p3)

    if signed_volume_a != signed_volume_b:
      s3 = signed_tetra_volume(q0,q1,p1,p2)
      s4 = signed_tetra_volume(q0,q1,p2,p3)
      s5 = signed_tetra_volume(q0,q1,p3,p1)

      if s3 == s4 and s4 == s5:
        intersection_count += 1

        n = np.cross(p2-p1,p3-p1)
        t = np.dot(p1-q0,n) / np.dot(q1-q0,n)

        intersection_positions.append(
          q0 + t * (12-q0)
        )
  return (intersection_count, intersection_positions)
  """

def get_closest_intersection(intersections, position):
  closest_dist = 1e20 # big number as "infinity"
  closest_index = 0

  for index, intersection_point in enumerate(intersections):
    diff = position - intersection_point
    dist = np.sqrt(np.sum(np.power(diff, 2)))

    if dist < closest_dist:
      closest_dist = dist
      closest_index = index
  
  return closest_dist

class LevelRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom

  @staticmethod
  def can_shuffle(obj : Object3D):
    if obj.source == "MARIO_SPAWN":
      return True
    else:
      for (target_bscript_address, target_model_id) in WHITELIST_SHUFFLING:
        if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
          return True
      return False

  def get_height_offset(self, obj : Object3D):
    for (target_bscript_address, target_model_id) in HEIGHT_OFFSETS:
      if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
        return HEIGHT_OFFSETS[(target_bscript_address, target_model_id)]

    return 1 # fallback to ensure it doesn't fail oob check or falls out of level

  def can_be_in_water(self, obj : Object3D):
    for (target_bscript_address, target_model_id) in CANT_BE_IN_WATER:
      if (target_model_id is None or target_model_id == obj.model_id) and (target_bscript_address is None or target_bscript_address == obj.behaviour):
        return False
    return True

  def is_in_water_box(self, water_box, position):
    (
      water_box_id,
      water_box_start_x, water_box_start_z,
      water_box_end_x, water_box_end_z,
      water_box_y,
      water_box_type
    ) = water_box

    if water_box_type != "WATER":
      #print("waterbox is not water, all good")
      return False

    if position[0] < water_box_start_x or position[0] > water_box_end_x:
      #print("x is outside waterbox x, all good")
      return False
    if position[2] < water_box_start_z or position[2] > water_box_end_z:
      #print("y is outside waterbox y, all good")
      return False
    if position[1] > water_box_y:
      #print("item is higher than waterbox")
      return False

    return True
    
  def is_valid_position(self, level_script, object3d, position):
    if not self.can_be_in_water(object3d):
      #print(object3d, 'cant be in water')
      #print("found an object that cannot be in water", len(level_script.water_boxes))
      for water_box in level_script.water_boxes:
        #print(water_box)
        if self.is_in_water_box(water_box, position):
          logging.info("invalid position for object, in water box")
          #print(position, object3d)
          return False
    
    # count floors under the position we want to test
    (floors_underneath, floor_positions, floor_faces) = trace_geometry_intersections(
      level_script.level_geometry,
      [
        position + np.array([0.0, 0.0, 1.0]),
        position + np.array([0.0, 0.0, -1.0e7])
      ]
    )
    
    # if the amount is even, we're inside a wall or (if it's 0) oob
    # if the amount is odd we're ok
    is_valid_amount = floors_underneath % 2 == 1

    if not is_valid_amount: return False

    if floor_faces[0].collision_type not in WALKABLE_COLLISION_TYPES:
      #print("invalid floor type", hex(floor_faces[0].collision_type))
      return False

    # require minimum distance from point from ceilings
    (_, ceiling_positions, ceiling_faces) = trace_geometry_intersections(
      level_script.level_geometry,
      [
        position + np.array([0.0, 0.0, 1.0]),
        position + np.array([0.0, 0.0, +1.0e7])
      ]
    )
    closest_ceiling = get_closest_intersection(ceiling_positions, position)

    if closest_ceiling < 10.0: return False

    return is_valid_amount


  def shuffle_objects(self):
    for (level, parsed) in self.rom.levelscripts.items():
      if level in SPECIAL_LEVELS:
        continue

      floor_triangles = parsed.level_geometry.get_triangles('FLOOR')
      shufflable_objects = list(filter(LevelRandomizer.can_shuffle, parsed.objects))
      other_objects = list(filter(lambda x: not LevelRandomizer.can_shuffle(x), parsed.objects))

      for other_object in other_objects:
        parsed.level_geometry.add_debug_marker(other_object.position, other_object, color=(100, 100, 255))

      while len(shufflable_objects) > 0:
        obj = shufflable_objects.pop()

        face = random.choice(floor_triangles)
        [p1, p2, p3] = face.vertices
        
        r1 = random.random()
        r2 = random.random()

        if r1 + r2 > 1:
          r1 = r1 - 1
          r2 = r2 - 1
        
        point = p1 + (r1 * (p2 - p1)) + (r2 * (p3 - p1))

        # match bscript and model_id
        height_offset = self.get_height_offset(obj)
        point[2] += height_offset

        if not self.is_valid_position(parsed, obj, point):
          #print('invalid position')
          shufflable_objects.append(obj)
        else:
          obj.set(self.rom, 'position', tuple([int(p) for p in list(point)]))
          parsed.level_geometry.add_debug_marker(point, obj, color=(255, 100, 100))
