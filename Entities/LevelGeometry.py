import trimesh
import numpy as np
from random import choice
import Constants
import os
import logging
#trimesh.util.attach_to_log()

if "SM64R" in os.environ and os.environ["SM64R"] == 'PLOT':
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

    self.objects = []
    self.level_forbidden_boundaries = []
    self.area_forbidden_boundaries = {}
    self.area_object_bounding_meshes = {}

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

  def add_object_point_of_interest(self, object3d):
    self.objects.append(object3d)

  def add_object_bounding_mesh(self, object3d, area_id, bounding_mesh):
    if not object3d.mem_address:
      raise Exception("Object encountered without memory address")

    if area_id not in self.area_object_bounding_meshes:
      self.area_object_bounding_meshes[area_id] = {}

    #if object3d.mem_address not in self.area_object_bounding_meshes[area_id]:
    self.area_object_bounding_meshes[area_id][object3d.mem_address] = bounding_mesh


  def add_area(self, area_id, vertices, triangles, collision_type):
    #geometry = trimesh.Trimesh(vertices=vertices, faces=triangles, metadata=dict(collision=collision_type))
    
    if collision_type == 0x0 and len(triangles) == 2 and len(vertices) == 4:
      logging.debug(f"Removing Default-Floor in {self.level.name} (Area: {hex(area_id)})")
      return

    if area_id not in self.area_faces:
      self.area_faces[area_id] = []
    if area_id not in self.area_vertices:
      self.area_vertices[area_id] = []

    if area_id not in self.area_forbidden_boundaries:
      self.area_forbidden_boundaries[area_id] = []

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
    # sort by triangle type, creating a new dict of WALL, FLOOR and CEILING
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

      # add disabled bounding boxes for level and for areas
      if area_id in self.level.areas and "loading_zones" in self.level.areas[area_id].properties:
        # for the whole level (this is overlapping between all areas)
        # in most cases, this will work for example in WDW, if you overlay all area geometries together, it will simply
        # form the whole level, but in TTMs slide, the geometries would collide.

        for loading_zone in self.level.areas[area_id].properties["loading_zones"]:
          start = loading_zone["p1"]
          end = loading_zone["p2"]
          extents = [
            abs(start[0] - end[0]),
            abs(start[1] - end[1]),
            abs(start[2] - end[2])
          ]

          position = [
            (start[0] if start[0] > end[0] else end[0]) - (extents[0]/2),
            (start[1] if start[1] > end[1] else end[1]) - (extents[1]/2),
            (start[2] if start[2] > end[2] else end[2]) - (extents[2]/2),
          ]

          bounding_box = trimesh.creation.box(extents=extents, transform=trimesh.transformations.translation_matrix(position))
          if area_id not in self.area_forbidden_boundaries:
            self.area_forbidden_boundaries[area_id] = []
          self.area_forbidden_boundaries[area_id].append(bounding_box)

    # add disabled bounding boxes for level and for areas
    if "loading_zones" in self.level.properties:
      # for the whole level (this is overlapping between all areas)
      # in most cases, this will work for example in WDW, if you overlay all area geometries together, it will simply
      # form the whole level, but in TTMs slide, the geometries would collide.

      for loading_zone in self.level.properties["loading_zones"]:
        start = loading_zone["p1"]
        end = loading_zone["p2"]
        extents = [
          abs(start[0] - end[0]),
          abs(start[1] - end[1]),
          abs(start[2] - end[2])
        ]

        position = [
          start[0] - (extents[0]/2),
          start[1] - (extents[1]/2),
          start[2] - (extents[2]/2),
        ]

        bounding_box = trimesh.creation.box(extents=extents, transform=trimesh.transformations.translation_matrix(position))
        self.level_forbidden_boundaries.append(bounding_box)


  def plot(self):
    level_traces = []
    # Plot level wide boundaries
    for bb_index, bounding_box in enumerate(self.level_forbidden_boundaries):
      mesh_components = np.transpose(bounding_box.vertices)
      triangle_indices = np.transpose(bounding_box.faces)

      level_traces.append(
        go.Mesh3d(
          x=np.negative(mesh_components[0]), # x neg
          y=mesh_components[2], # y and z swapped
          z=mesh_components[1],
          i=triangle_indices[0],
          j=triangle_indices[1],
          k=triangle_indices[2],
          text=f"Level Loading Zone #{hex(bb_index)}",
          #facecolor=(1, 0, 0, 1),
          flatshading=True,
          #color='#FFB6C1',
          #hoverinfo="skip"
        )
      )
      
    # Plot area meshes
    for (area_id, area_geometry) in self.area_geometries.items():
      mesh_components = np.transpose(area_geometry.vertices)
      triangle_indices = np.transpose(area_geometry.faces)
      collision_types = []

      traces = [
        *level_traces,
      ]

      state_groups = {}
      
      # Plot objects
      for object3d in self.objects:
        if object3d.meta["randomization"] not in state_groups:
          state_groups[object3d.meta["randomization"]] = {
            "x": [],
            "y": [],
            "z": [],
            "text": []
          }
        
        state_groups[object3d.meta["randomization"]]["x"].append(-object3d.position[0]), # x neg
        state_groups[object3d.meta["randomization"]]["y"].append(object3d.position[2]), # y and z swapped
        state_groups[object3d.meta["randomization"]]["z"].append(object3d.position[1]),
        state_groups[object3d.meta["randomization"]]["text"].append(f'{object3d.meta["randomization"]}: {str(object3d.behaviour_name)}')

      for group, objs in state_groups.items():
        traces.append(
          go.Scatter3d(x=objs["x"], y=objs["y"], z=objs["z"], mode="markers", text=objs["text"], name=f'Objects: {group}')
        )
      
      # Plot geometry (with collision type)
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
      
      # Plot Forbidden Boundaries
      for bb_index, bounding_box in enumerate(self.area_forbidden_boundaries[area_id]):
        mesh_components = np.transpose(bounding_box.vertices)
        triangle_indices = np.transpose(bounding_box.faces)
        print("adding mesh for level area bounding box")
        traces.append(
          go.Mesh3d(
            x=np.negative(mesh_components[0]), # x neg
            y=mesh_components[2], # y and z swapped
            z=mesh_components[1],
            i=triangle_indices[0],
            j=triangle_indices[1],
            k=triangle_indices[2],
            text=f"Level-Area Loading Zone #{hex(bb_index)}",
            #facecolor=(1, 0, 0, 1),
            flatshading=True,
            #color='#FFB6C1',
            #hoverinfo="skip"
          )
        )
      
      # Plot object boundaries
      if area_id in self.area_object_bounding_meshes:
        for bounding_mesh in self.area_object_bounding_meshes[area_id].values():
          mesh_components = np.transpose(bounding_mesh.vertices)
          triangle_indices = np.transpose(bounding_mesh.faces)
          traces.append(
            go.Mesh3d(
              x=np.negative(mesh_components[0]), # x neg
              y=mesh_components[2], # y and z swapped
              z=mesh_components[1],
              i=triangle_indices[0],
              j=triangle_indices[1],
              k=triangle_indices[2],
              text=f"Object Boundary",
              #facecolor=(1, 0, 0, 1),
              flatshading=True,
              #color='#FFB6C1',
              #hoverinfo="skip"
            )
          )

      py.plot(traces, filename=f'dumps/level_plots/{self.level.name}_{hex(area_id)}.html', auto_open=False)