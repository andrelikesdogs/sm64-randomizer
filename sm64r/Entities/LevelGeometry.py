from math import sqrt
import math
from secrets import choice
import trimesh
import numpy as np
from random import random
from sm64r.Randoutils import fast_choice
import os
import logging
from time import strftime
# trimesh.util.attach_to_log()

trimesh.util.attach_to_log(level=logging.CRITICAL)
logging.getLogger().setLevel(level=logging.ERROR)

if "SM64R" in os.environ and os.environ["SM64R"] == 'PLOT':
    import plotly.offline as py
    import plotly.graph_objs as go


class LevelGeometry:
    def __init__(self, level):
        self.level = level
        self.area_geometries = {}
        self.area_geometry_triangle_collision_types = {}
        self.area_collision_managers = {}
        self.area_face_types = {}
        self.area_vertices = {}
        self.area_faces = {}
        self.area_face_aabbs = {}

        self.objects = []
        self.level_forbidden_boundaries = []
        self.level_debug_boundaries = []
        self.area_level_debug_raytraces = {}
        self.area_forbidden_boundaries = {}
        self.area_object_bounding_meshes = {}

        self.area_floor_triangles = {}
        self.area_floor_triangles_weights = {}
        self.area_floor_triangles_weights_sum = {}

    def get_collision_type_for_triangle(self, area_id, triangle_index):
        if area_id not in self.area_geometry_triangle_collision_types:
            raise Exception("Area-ID not in collision types dict")

        for ((start, end), collision_type) in self.area_geometry_triangle_collision_types[area_id].items():
            if triangle_index >= start and triangle_index < end:
                return collision_type

    def get_random_point_in_area_weighted(self, area_id):
        if area_id not in self.area_face_types:
            raise Exception("Area-ID list geometry")

        # random_floor_triangle_index = choice(
        #     self.area_floor_triangles[area_id])

        random_floor_triangle_index = fast_choice(
            self.area_floor_triangles[area_id], self.area_floor_triangles_weights[area_id], self.area_floor_triangles_weights_sum[area_id])

        # (start,
        #  end) = self.area_face_aabbs[area_id][random_floor_triangle_index]

        (a, b, c) = self.area_faces[area_id][random_floor_triangle_index]
        cornerA = self.area_vertices[area_id][a]
        cornerB = self.area_vertices[area_id][b]
        cornerC = self.area_vertices[area_id][c]

        highest_point = max(np.transpose([cornerA, cornerB, cornerC])[1])

        r1 = random()
        r2 = random()

        sqrtr1 = sqrt(r1)

        random_pos = [
            round((1 - sqrtr1) * cornerA[0] + (sqrtr1 * (1 - r2)) *
                  cornerB[0] + (sqrtr1 * r2) * cornerC[0]),
            round(highest_point + 10),
            round((1 - sqrtr1) * cornerA[2] + (sqrtr1 * (1 - r2)) *
                  cornerB[2] + (sqrtr1 * r2) * cornerC[2]),
        ]

        return random_pos

    def add_object_point_of_interest(self, object3d):
        self.objects.append(object3d)

    def add_object_bounding_mesh(self, object3d, area_id, bounding_mesh):
        if not object3d.mem_address:
            raise Exception("Object encountered without memory address")

        if area_id not in self.area_object_bounding_meshes:
            self.area_object_bounding_meshes[area_id] = {}

        self.area_object_bounding_meshes[area_id][object3d.iid] = bounding_mesh

    def add_area_mesh_for_collision_type(self, area_id, vertices, triangles, collision_type):
        # geometry = trimesh.Trimesh(vertices=vertices, faces=triangles, metadata=dict(collision=collision_type))

        if collision_type == 0x0 and len(triangles) == 2 and len(vertices) == 4:
            # all levels have a collision-type 0x0 floor, which may or may not be the death floor
            # logging.debug(f"Removing Default-Floor in {self.level.name} (Area: {hex(area_id)})")
            return

        # initialize structures for new area_id
        if area_id not in self.area_faces:
            self.area_faces[area_id] = []
        if area_id not in self.area_vertices:
            self.area_vertices[area_id] = []
        if area_id not in self.area_forbidden_boundaries:
            self.area_forbidden_boundaries[area_id] = []
        if area_id not in self.area_face_aabbs:
            self.area_face_aabbs[area_id] = []

        geometry_triangle_count = len(self.area_faces[area_id])
        self.area_faces[area_id].extend(triangles)
        self.area_vertices[area_id].extend(vertices)

        if area_id not in self.area_geometry_triangle_collision_types:
            self.area_geometry_triangle_collision_types[area_id] = {}

        self.area_geometry_triangle_collision_types[area_id][(
            geometry_triangle_count,  # start
            geometry_triangle_count + len(triangles)  # end
        )] = collision_type

        for [a_index, b_index, c_index] in triangles:
            # positions of the 3 vertices that make up the face
            a = vertices[a_index]
            b = vertices[b_index]
            c = vertices[c_index]

            # min corner
            start = (
                min(a[0], b[0], c[0]),
                min(a[1], b[1], c[1]),
                min(a[2], b[2], c[2]),
            )
            # max corner
            end = (
                max(a[0], b[0], c[0]),
                max(a[1], b[1], c[1]),
                max(a[2], b[2], c[2]),
            )

            self.area_face_aabbs[area_id].append((start, end))

    def process(self):
        # sort by triangle type, creating a new dict of WALL, FLOOR and CEILING
        for area_id in self.area_faces.keys():
            self.area_face_types[area_id] = {
                'FLOOR': [],
                'WALL': [],
                'CEILING': []
            }

            geometry = trimesh.Trimesh(
                vertices=self.area_vertices[area_id], faces=self.area_faces[area_id])

            for triangle_index, normal in enumerate(geometry.face_normals):
                slope = np.dot(normal, (0, 1, 0))

                tri_type = 'WALL'
                if slope >= 0.8:
                    tri_type = 'FLOOR'
                elif slope <= -0.5:
                    tri_type = 'CEILING'
                self.area_face_types[area_id][tri_type].append(triangle_index)

            self.area_geometries[area_id] = geometry

            # after sorting triangles by type (wall, floor, ceiling)
            # generate weighted random for all floors

            self.area_floor_triangles_weights[area_id] = []

            triangle_weights = []
            triangle_weights_total = 0
            for tri in self.area_face_types[area_id]['FLOOR']:
                triangle_area = math.sqrt(geometry.area_faces[tri])
                triangle_weights.append(triangle_weights_total + triangle_area)
                triangle_weights_total += triangle_area

            self.area_floor_triangles[area_id] = self.area_face_types[area_id]['FLOOR']

            self.area_floor_triangles_weights[area_id] = triangle_weights
            self.area_floor_triangles_weights_sum[area_id] = triangle_weights_total

            # add disabled bounding boxes for an individual area
            if area_id in self.level.areas:
                # using the setting on the level properties will make the bounding box be overlapped
                # over all areas, which is useful for levels that continue into another with a loading zone

                area_forbidden_boundaries = []

                if "loading_zones" in self.level.areas[area_id].properties:
                    area_forbidden_boundaries = area_forbidden_boundaries + \
                        self.level.areas[area_id].properties["loading_zones"]

                if "forbidden_zones" in self.level.areas[area_id].properties:
                    area_forbidden_boundaries = area_forbidden_boundaries + \
                        self.level.areas[area_id].properties["forbidden_zones"]

                for loading_zone in area_forbidden_boundaries:
                    start = loading_zone["p1"]
                    end = loading_zone["p2"]
                    extents = [
                        abs(start[0] - end[0]),
                        abs(start[1] - end[1]),
                        abs(start[2] - end[2])
                    ]

                    position = [
                        (start[0] if start[0] > end[0]
                         else end[0]) - (extents[0]/2),
                        (start[1] if start[1] > end[1]
                            else end[1]) - (extents[1]/2),
                        (start[2] if start[2] > end[2]
                            else end[2]) - (extents[2]/2),
                    ]

                    bounding_box = trimesh.creation.box(
                        extents=extents, transform=trimesh.transformations.translation_matrix(position))
                    if area_id not in self.area_forbidden_boundaries:
                        self.area_forbidden_boundaries[area_id] = []
                    self.area_forbidden_boundaries[area_id].append(
                        bounding_box)

        # for the whole level (this is overlapping between all areas)
        # in most cases, this will work for example in WDW, if you overlay all area geometries together, it will simply
        # form the whole level, but in TTMs slide, the geometries would collide.

        level_forbidden_boundaries = []

        if "loading_zones" in self.level.properties:
            level_forbidden_boundaries = level_forbidden_boundaries + \
                self.level.properties["loading_zones"]

        if "forbidden_zones" in self.level.properties:
            level_forbidden_boundaries = level_forbidden_boundaries + \
                self.level.properties["forbidden_zones"]

        for boundary in level_forbidden_boundaries:
            start = boundary["p1"]
            end = boundary["p2"]
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

            bounding_box = trimesh.creation.box(
                extents=extents, transform=trimesh.transformations.translation_matrix(position))
            self.level_forbidden_boundaries.append(bounding_box)

    def plot_trace(self, obj, a, b):
        if obj.area_id not in self.area_level_debug_raytraces:
            self.area_level_debug_raytraces[obj.area_id] = []

        self.area_level_debug_raytraces[obj.area_id].append((a, b))

    def plot_placement(self, obj, *targets):
        # print("plotting placement")
        level_traces = []

        # Plot level wide boundaries
        for bb_index, bounding_box in enumerate(self.level_forbidden_boundaries):
            mesh_components = np.transpose(bounding_box.vertices)
            triangle_indices = np.transpose(bounding_box.faces)

            level_traces.append(
                go.Mesh3d(
                    x=np.negative(mesh_components[0]),  # x neg
                    y=mesh_components[2],  # y and z swapped
                    z=mesh_components[1],
                    i=triangle_indices[0],
                    j=triangle_indices[1],
                    k=triangle_indices[2],
                    text=f"Level Loading Zone #{hex(bb_index)}",
                    # facecolor=(1, 0, 0, 1),
                    flatshading=True,
                    # color='#FFB6C1',
                    # hoverinfo="skip"
                    opacity=0.5
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

            # Plot geometry (with collision type)
            for (start, end), collision_type in self.area_geometry_triangle_collision_types[area_id].items():
                mesh_components = np.transpose(area_geometry.vertices)
                triangle_indices = np.transpose(area_geometry.faces[start:end])

                traces.append(
                    go.Mesh3d(
                        x=np.negative(mesh_components[0]),  # x neg
                        y=mesh_components[2],  # y and z swapped
                        z=mesh_components[1],
                        i=triangle_indices[0],
                        j=triangle_indices[1],
                        k=triangle_indices[2],
                        text=f"Collision Type: {hex(collision_type)} from ({start} to {end}), Slope: ",
                        # facecolor=(1, 0, 0, 1),
                        flatshading=True,
                        # color='#FFB6C1',
                        # hoverinfo="skip"
                    )
                )

            # Plot geometry faces
            for triangle_index, _ in enumerate(triangle_indices):
                collision_types.append(
                    self.get_collision_type_for_triangle(area_id, triangle_index))

            # Plot Target
            for target_index, target in enumerate(targets):
                mesh_components = np.transpose(target.vertices)
                triangle_indices = np.transpose(target.faces)
                traces.append(
                    go.Mesh3d(
                        x=np.negative(mesh_components[0]),  # x neg
                        y=mesh_components[2],  # y and z swapped
                        z=mesh_components[1],
                        i=triangle_indices[0],
                        j=triangle_indices[1],
                        k=triangle_indices[2],
                        text=f"Target Geometry #{target_index+1}",
                        # facecolor=(1, 0, 0, 1),
                        flatshading=True,
                        # color='#FFB6C1',
                        # hoverinfo="skip"
                        opacity=0.5
                    )
                )

            if not os.path.exists("dumps/level_plots/placement_debug"):
                os.makedirs("dumps/level_plots/placement_debug")
            py.plot(
                traces, filename=f'dumps/level_plots/placement_debug/{self.level.name}_{hex(area_id)}_{strftime("%Y%m%d-%H%M%S")}.html', auto_open=False)

    def plot_bounding_box(self, obj, bounding_box):
        self.level_debug_boundaries.append((obj, bounding_box))

    def plot(self):
        level_traces = []
        # Plot level wide boundaries
        for bb_index, bounding_box in enumerate(self.level_forbidden_boundaries):
            mesh_components = np.transpose(bounding_box.vertices)
            triangle_indices = np.transpose(bounding_box.faces)

            level_traces.append(
                go.Mesh3d(
                    x=np.negative(mesh_components[0]),  # x neg
                    y=mesh_components[2],  # y and z swapped
                    z=mesh_components[1],
                    i=triangle_indices[0],
                    j=triangle_indices[1],
                    k=triangle_indices[2],
                    text=f"Level Loading Zone #{hex(bb_index)}",
                    # facecolor=(1, 0, 0, 1),
                    flatshading=True,
                    # color='#FFB6C1',
                    # hoverinfo="skip"
                    opacity=0.5
                )
            )

        for bb_index, (obj, bounding_box) in enumerate(self.level_debug_boundaries):
            mesh_components = np.transpose(bounding_box.vertices)
            triangle_indices = np.transpose(bounding_box.faces)

            level_traces.append(
                go.Mesh3d(
                    x=np.negative(mesh_components[0]),  # x neg
                    y=mesh_components[2],  # y and z swapped
                    z=mesh_components[1],
                    i=triangle_indices[0],
                    j=triangle_indices[1],
                    k=triangle_indices[2],
                    text=f"Bounding box for {obj.behaviour_name}",
                    # facecolor=(1, 0, 0, 1),
                    flatshading=True,
                    # color='#FFB6C1',
                    # hoverinfo="skip"
                    opacity=0.5
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
                if object3d.area_id != area_id:
                    continue

                if object3d.meta["randomization"] not in state_groups:
                    state_groups[object3d.meta["randomization"]] = {
                        "x": [],
                        "y": [],
                        "z": [],
                        "text": []
                    }

                state_groups[object3d.meta["randomization"]
                             ]["x"].append(-object3d.position[0]),  # x neg
                state_groups[object3d.meta["randomization"]]["y"].append(
                    object3d.position[2]),  # y and z swapped
                state_groups[object3d.meta["randomization"]
                             ]["z"].append(object3d.position[1]),
                state_groups[object3d.meta["randomization"]]["text"].append(
                    f'{object3d.meta["randomization"]}: {str(object3d.behaviour_name)}')

            for group, objs in state_groups.items():
                traces.append(
                    go.Scatter3d(x=objs["x"], y=objs["y"], z=objs["z"],
                                 mode="markers", text=objs["text"], name=f'Objects: {group}')
                )

            # Plot geometry (with collision type)
            # for tri_type, face_indices in self.area_face_types[area_id].items():
            #     # print(face_indices)
            #     if not len(face_indices):
            #         continue
            #     mesh_components = np.transpose(area_geometry.vertices)
            #     triangle_indices = np.transpose(
            #         list(map(lambda x: area_geometry.faces[x], face_indices)))
            for (start, end), collision_type in self.area_geometry_triangle_collision_types[area_id].items():
                mesh_components = np.transpose(area_geometry.vertices)
                triangle_indices = np.transpose(area_geometry.faces[start:end])

                traces.append(
                    go.Mesh3d(
                        x=np.negative(mesh_components[0]),  # x neg
                        y=mesh_components[2],  # y and z swapped
                        z=mesh_components[1],
                        i=triangle_indices[0],
                        j=triangle_indices[1],
                        k=triangle_indices[2],
                        text=f"Type: {collision_type} ({hex(collision_type)})",
                        # facecolor=(1, 0, 0, 1),
                        flatshading=True,
                        # color='#FFB6C1',
                        # hoverinfo="skip"
                    )
                )

            # Plot geometry faces
            for triangle_index, _ in enumerate(triangle_indices):
                collision_types.append(
                    self.get_collision_type_for_triangle(area_id, triangle_index))

            # Plot Forbidden Boundaries
            for bb_index, bounding_box in enumerate(self.area_forbidden_boundaries[area_id]):
                mesh_components = np.transpose(bounding_box.vertices)
                triangle_indices = np.transpose(bounding_box.faces)
                # print("adding mesh for level area bounding box")
                traces.append(
                    go.Mesh3d(
                        x=np.negative(mesh_components[0]),  # x neg
                        y=mesh_components[2],  # y and z swapped
                        z=mesh_components[1],
                        i=triangle_indices[0],
                        j=triangle_indices[1],
                        k=triangle_indices[2],
                        text=f"Level-Area Loading Zone #{hex(bb_index)}",
                        # facecolor=(1, 0, 0, 1),
                        flatshading=True,
                        # color='#FFB6C1',
                        # hoverinfo="skip"
                    )
                )

            if area_id in self.area_level_debug_raytraces:
                for (line_start, line_end) in self.area_level_debug_raytraces[area_id]:
                    # print(line_start, line_end)
                    traces.append(
                        go.Scatter3d(
                            x=[-line_start[0], -line_end[0]],
                            y=[line_start[2], line_end[2]],
                            z=[line_start[1], line_end[1]],
                            mode="lines"
                        )
                    )

            # Plot face AABBs
            # takes fucking *forever*
            '''
      for index, (c1, c2) in enumerate(self.area_face_aabbs[area_id]):
        # print progress
        print(str(index / len(self.area_face_aabbs[area_id]) * 100) + "%" + (" " * 10), end="\r")
        if index > 500: break # too many too display :(
        extent = (c2[0] - c1[0], c2[1] - c1[1], c2[2] - c1[2])
        tri_aabb = trimesh.creation.box(
          extents=extent,
          transform=trimesh.transformations.translation_matrix(
            (c1[0] + extent[0]/2, c1[1] + extent[1]/2, c1[2] + extent[2]/2)
          )
        )
        aabb_mesh_components = np.transpose(tri_aabb.vertices)
        aabb_triangle_indices = np.transpose(tri_aabb.faces)
        traces.append(
          go.Mesh3d(
            x=np.negative(aabb_mesh_components[0]), # x neg
            y=aabb_mesh_components[2], # y and z swapped
            z=aabb_mesh_components[1],
            i=aabb_triangle_indices[0],
            j=aabb_triangle_indices[1],
            k=aabb_triangle_indices[2],
            color='rgb(0, 0, 255)',
            opacity=0.3,
            hoverinfo="skip"
          )
        )
      '''

            # Plot object boundaries
            if area_id in self.area_object_bounding_meshes:
                for bounding_mesh in self.area_object_bounding_meshes[area_id].values():
                    mesh_components = np.transpose(bounding_mesh.vertices)
                    triangle_indices = np.transpose(bounding_mesh.faces)
                    traces.append(
                        go.Mesh3d(
                            x=np.negative(mesh_components[0]),  # x neg
                            y=mesh_components[2],  # y and z swapped
                            z=mesh_components[1],
                            i=triangle_indices[0],
                            j=triangle_indices[1],
                            k=triangle_indices[2],
                            text=f"Object Boundary",
                            # facecolor=(1, 0, 0, 1),
                            flatshading=True,
                            # color='#FFB6C1',
                            # hoverinfo="skip"
                            opacity=0.5
                        )
                    )

            # print(f'plotting {self.level.name} {hex(area_id)}')
            if not os.path.exists("dumps/level_plots"):
                os.makedirs("dumps/level_plots")
            py.plot(
                traces, filename=f'dumps/level_plots/{self.level.name}_{hex(area_id)}.html', auto_open=False)
            # print('done')
