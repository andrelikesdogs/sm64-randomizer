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

class Face:
  def __init__(self, vertices, triangle_index):
    self.vertices = np.array(vertices)
    self.index = triangle_index
    self.vertices_transposed = np.transpose(self.vertices)

    self.normal = np.array([0, 0, 0])
    self.type = None
    self.bounding_box = None

    self.calc_props()
  
  def calc_props(self):
    [p1, p2, p3] = self.vertices
    u = p2 - p1
    v = p3 - p1
    
    # calc normal
    cross = np.cross(u, v)
    #print(cross)
    biggest_var = np.max(np.abs(cross))

    if biggest_var != 0:
      self.normal = cross / np.max(np.abs(cross))

    is_floor = self.normal[1] > 0.01
    is_ceiling = self.normal[1] < -0.01

    if is_floor:
      self.type = 'FLOOR'
    elif is_ceiling:
      self.type = 'CEILING'
    else:
      self.type = 'WALL'
    
    self.center = np.mean(self.vertices, axis=0)
    self.bounding_box = (
      np.min(self.vertices_transposed[0]), # -X
      np.max(self.vertices_transposed[0]), # +X
      np.min(self.vertices_transposed[1]), # -Y
      np.max(self.vertices_transposed[1]), # +Y
      np.min(self.vertices_transposed[2]), # -Z
      np.max(self.vertices_transposed[2]), # +Z
    )
    

class Geometry:
  def __init__(self, vertices, triangles, collision_type, index):
    self.vertices = np.array(vertices)
    self.triangles = np.array(triangles)
    self.faces = []
    self.faces_by_type = {'FLOOR': [], 'CEILING': [], 'WALL': []}
    self.collision_type = collision_type
    self.index = index

    self.convert_to_faces()

  def convert_to_faces(self):
    for face_index, vertices in enumerate(self.vertices[self.triangles]):
      face = Face(vertices, face_index)
      self.faces.append(face)
      self.faces_by_type[face.type].append(face)

  def plot_get_color(self):
    colors = []

    colors = []
    type_colors = {
      'FLOOR': (0, 0, 1),
      'WALL': (0, 1, 0),
      'CEILING': (1, 0, 0),
    }
    for face in self.faces:
      colors.append(type_colors[face.type])
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
  
  def get_triangles(self, floor_type = None):
    faces = []
    for (area_id, areas) in self.area_geometries.items():
      for area in areas:
        if not floor_type:
          faces.extend(area.faces)
        else:
          faces.extend(area.faces_by_type[floor_type])
    return faces

  def plot(self):
    traces = []
    for (area_id, areas) in self.area_geometries.items():
      for area in areas:
        traces.append(area.plot())

    
    if len(traces) > 0:
      py.plot(traces, filename=f'{self.level.name}.html')