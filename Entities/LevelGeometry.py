import trimesh
import numpy as np
from random import choice
import Constants
import os
import logging
#trimesh.util.attach_to_log()

if "SM64R_DEBUG" in os.environ and os.environ["SM64R_DEBUG"] == 'PLOT':
  import plotly.offline as py
  import plotly.graph_objs as go

class LevelGeometry:
  def __init__(self, level):
    self.level = level
    self.area_geometries = {}
    self.area_geometry_triangle_collision_types = {}
    self.area_face_types = {}
    self.area_vertices = {}
    self.area_faces = {}

  def get_collision_type_for_triangle(self, area_id, triangle_index):
    if area_id not in self.area_geometry_triangle_collision_types:
      raise Exception("Area-ID not in collision types dict")
    
    for ((start, end), collision_type) in self.area_geometry_triangle_collision_types[area_id].items():
      if triangle_index >= start and triangle_index < end:
        return collision_type
  
  def get_random_point_in_area(self, area_id):
    if area_id not in self.area_face_types:
      raise Exception("Area-ID list geometry")
    
    random_floor_triangle_index = choice(self.area_face_types[area_id]['FLOOR'])
    triangle_center = self.area_geometries[area_id].triangles_center[random_floor_triangle_index]

    return list(triangle_center)

  def add_area(self, area_id, vertices, triangles, collision_type):
    #geometry = trimesh.Trimesh(vertices=vertices, faces=triangles, metadata=dict(collision=collision_type))
    
    if collision_type == 0x0 and len(triangles) == 2 and len(vertices) == 4:
      logging.debug(f"Removing Default-Floor in {self.level.name} (Area: {hex(area_id)})")
      return

    if area_id not in self.area_faces:
      self.area_faces[area_id] = []
    if area_id not in self.area_vertices:
      self.area_vertices[area_id] = []

    geometry_triangle_count = len(self.area_faces[area_id])
    self.area_faces[area_id].extend(triangles)
    self.area_vertices[area_id].extend(vertices)

    if area_id not in self.area_geometry_triangle_collision_types:
      self.area_geometry_triangle_collision_types[area_id] = {}

    self.area_geometry_triangle_collision_types[area_id][(
      geometry_triangle_count, # start
      geometry_triangle_count + len(triangles) # end
    )] = collision_type

  def process(self):
    for area_id in self.area_faces.keys():
      geometry = trimesh.Trimesh(vertices=self.area_vertices[area_id], faces=self.area_faces[area_id])

      for triangle_index, normal in enumerate(geometry.face_normals):

        self.area_face_types[area_id] = {
          'FLOOR': [],
          'WALL': [],
          'CEILING': []
        }

        tri_type = 'WALL'
        if normal[1] > 0.01:
          tri_type = 'FLOOR'
        elif normal[1] < -0.01:
          tri_type = 'CEILING'
        self.area_face_types[area_id][tri_type].append(triangle_index)
      self.area_geometries[area_id] = geometry


  def plot(self):
    for (area_id, area_geometry) in self.area_geometries.items():
      mesh_components = np.transpose(area_geometry.vertices)
      triangle_indices = np.transpose(area_geometry.faces)
      collision_types = []

      traces = []
      for (start, end), collision_type in self.area_geometry_triangle_collision_types[area_id].items():
        mesh_components = np.transpose(area_geometry.vertices)
        triangle_indices = np.transpose(area_geometry.faces[start:end])
        traces.append(
        go.Mesh3d(
          x=np.negative(mesh_components[0]), # x neg
          y=mesh_components[2], # y and z swapped
          z=mesh_components[1],
          i=triangle_indices[0],
          j=triangle_indices[1],
          k=triangle_indices[2],
          text=f"Collision Type: {hex(collision_type)} from ({start} to {end})",
          #facecolor=(1, 0, 0, 1),
          flatshading=True,
          #color='#FFB6C1',
          #hoverinfo="skip"
        )
      )

      for triangle_index, _ in enumerate(triangle_indices):
        collision_types.append(self.get_collision_type_for_triangle(area_id, triangle_index))

      py.plot(traces, filename=f'dumps/level_plots/{self.level.name}_{hex(area_id)}.html', auto_open=False)