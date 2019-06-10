import trimesh
import numpy as np
from random import choice
#trimesh.util.attach_to_log()

class LevelGeometry:
  def __init__(self, level):
    self.level = level
    self.area_geometries = {}
    self.area_geometry_triangle_collision_types = {}
    self.area_face_types = {}

  def get_collision_type_for_triangle(self, area_id, triangle_index):
    if area_id not in self.area_geometry_triangle_collision_types:
      raise Exception("Area-ID not in collision types dict")
    
    for ((start, end), collision_type) in self.area_geometry_triangle_collision_types[area_id].items():
      if triangle_index >= start and triangle_index <= end:
        return collision_type
  
  def get_random_point_in_area(self, area_id):
    if area_id not in self.area_face_types:
      raise Exception("Area-ID list geometry")
    
    random_floor_triangle_index = choice(self.area_face_types[area_id]['FLOOR'])
    triangle_center = self.area_geometries[area_id].triangles_center[random_floor_triangle_index]

    return list(triangle_center)
    

  def add_area(self, area_id, vertices, triangles, collision_type):
    geometry = trimesh.Trimesh(vertices=vertices, faces=triangles, metadata=dict(collision=collision_type))
    #for facet in geometry.facets:
    #  geometry.visual.face_colors[facet] = trimesh.visual.random_color()

    geometry_triangle_count = self.area_geometries[area_id].triangles.shape[0] if area_id in self.area_geometries else 0

    if area_id not in self.area_geometries:
      self.area_geometries[area_id] = geometry
    else:
      self.area_geometries[area_id] += geometry

    if area_id not in self.area_geometry_triangle_collision_types:
      self.area_geometry_triangle_collision_types[area_id] = {}

    if area_id not in self.area_face_types:
      self.area_face_types[area_id] = {
        'FLOOR': [],
        'WALL': [],
        'CEILING': []
      }

    for triangle_index, normal in enumerate(geometry.face_normals):
      tri_type = 'WALL'

      if normal[1] > 0.01:
        tri_type = 'FLOOR'
      elif normal[1] < -0.01:
        tri_type = 'CEILING'
      
      self.area_face_types[area_id][tri_type].append(triangle_index)

    self.area_geometry_triangle_collision_types[area_id][(
      geometry_triangle_count, # start
      geometry_triangle_count + len(triangles) # end
    )] = collision_type

    #geometry.show()
