import numpy as np
import os

if "DEBUG" in os.environ and os.environ["DEBUG"] == 'PLOT':
  import plotly.offline as py
  import plotly.graph_objs as go

import math

WALKABLE_COLLISION_TYPES = [
  0x00, # environment default
  0x29, # default floor with noise
  0x14, # slightly slippery
  0x15, # anti slippery
  0x0B, # close camera
]

class Geometry:
  def __init__(self, vertices, triangles, collision_type, index):
    self.vertices = np.array(vertices)
    self.triangles = np.array(triangles)
    self.collision_type = collision_type
    self.index = index
    self.normals = []
    self.centroids = []
    self.triangle_types = []

    self.calc_normals()
    self.calc_centroids()


  def calc_centroids(self):
    for vertice_indices in self.triangles:
      (p1, p2, p3) = tuple(map(lambda i : self.vertices[i], vertice_indices))

      centroid = np.mean([p1, p2, p3], axis=0)
      self.centroids.append(centroid)

  def calc_normals(self):
    for vertice_indices in self.triangles:
      (p1, p2, p3) = tuple(map(lambda i : self.vertices[i], vertice_indices))

      u = p2 - p1
      v = p3 - p1
      cross = np.cross(u, v)
      #print(cross)
      norm = cross / np.max(np.abs(cross))
      self.normals.append(norm)

      is_floor = norm[1] > 0.01
      is_ceiling = norm[1] < -0.01
      
      triangle_type = "WALL"
      if is_floor:
        triangle_type = "FLOOR"
      elif is_ceiling:
        triangle_type = "CEILING"

      self.triangle_types.append(triangle_type)

  def get_floor_triangles(self):
    triangles = []
    for (triangle_index, vertice_indices) in enumerate(self.triangles):
      if self.triangle_types[triangle_index] == 'FLOOR':
        triangles.append(self.vertices[vertice_indices])
    
    return triangles

  def get_triangles(self):
    return self.vertices[self.triangles]

  def plot_get_color(self):
    mesh = self.vertices[self.triangles]

    ref = np.array([0, 1, 0])
    colors = []
    type_colors = [
      (0, 0, 1),
      (0, 1, 0),
      (1, 0, 0),
    ]
    for index, vert_indices in enumerate(self.triangles):
      normal_vec = self.normals[index]
      dot = np.dot(normal_vec, ref)
      angle = math.acos(dot)
      slope = math.tan(angle)
      slope_deg = slope * 180/math.pi
      is_floor = normal_vec[1] > 0.01
      is_ceiling = normal_vec[1] < -0.01
      #is_wall = not is_floor and not is_ceiling

      surface_type = 1
      if is_floor:
        surface_type = 0
      elif is_ceiling:
        surface_type = 2


      colors.append(type_colors[surface_type])

    return colors

  def plot(self):
    mesh_components = np.transpose(self.vertices)
    triangle_indices = np.transpose(self.triangles)

    if len(mesh_components) > 0:
      return go.Mesh3d(
        x=np.negative(mesh_components[0]),
        y=mesh_components[2],
        z=mesh_components[1],
        i=triangle_indices[0],
        j=triangle_indices[1],
        k=triangle_indices[2],
        facecolor=self.plot_get_color(),
        flatshading=True,
        color='#FFB6C1',
      )
    


class LevelGeometry:
  def __init__(self, level):
    self.level = level
    self.area_geometries = {}

  def add_area(self, area_id, vertices, triangles, collision_type):
    if area_id not in self.area_geometries:
      self.area_geometries[area_id] = []
    
    if area_id == 0x2: return
    
    geometry = Geometry(vertices, triangles, collision_type, len(self.area_geometries[area_id]))
    self.area_geometries[area_id].append(geometry)
  
  def get_triangles(self):
    triangles = []
    for (area_id, areas) in self.area_geometries.items():
      for area in areas:
        triangles.extend(area.get_triangles())
    
    return triangles

  def get_floor_triangles(self):
    triangles = []
    for (area_id, areas) in self.area_geometries.items():
      for area in areas:
        triangles.extend(area.get_floor_triangles())

    return triangles

  def plot(self):
    traces = []
    for (area_id, areas) in self.area_geometries.items():
      for area in areas:
        traces.append(area.plot())

    
    if len(traces) > 0:
      py.plot(traces, filename=f'{self.level.name}.html')