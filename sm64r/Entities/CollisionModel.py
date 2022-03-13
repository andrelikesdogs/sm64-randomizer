import os
import trimesh
from sm64r.Parsers.CollisionPresets import SPECIAL_CD_WITH_PARAMS
from sm64r.Randoutils import format_binary


class CollisionModel:
    def __init__(self, id, vertices, triangles, collisiontypes):
        self.id = id
        self.vertices = vertices
        self.triangles = triangles
        self.collisiontypes = collisiontypes

        self.mesh = trimesh.Trimesh(
            vertices=vertices, faces=triangles)

        if 'SM64R' in os.environ:
            if 'EXPORT_COLLISION_DATA' in os.environ['SM64R']:
                if not os.path.exists(os.path.join("dumps", "collision_data")):
                    os.makedirs(os.path.join("dumps", "collision_data"))

                keepcharacters = (' ', '.', '_')
                save_filename = "".join(
                    c for c in self.id if c.isalnum() or c in keepcharacters).rstrip()

                with open(os.path.join('dumps', 'collision_data', f'{save_filename}.stl'), 'wb+') as output:
                    self.mesh.export(output, 'stl')

    @staticmethod
    def from_position(rom, start_pos, identifier=None):
        cursor = start_pos
        collision_type_group = rom.read_bytes(cursor, 2)
        cursor += 2

        if collision_type_group != b'\x00\x40':
            raise Exception('Collisiondata did not start with [00] [40], instead got ', format_binary(
                collision_type_group))

        vertex_count = rom.read_integer(cursor, 2)
        cursor += 2
        vertices = []

        for _ in range(vertex_count):
            vertices.append((
                rom.read_integer(cursor, 2, True),
                rom.read_integer(cursor + 2, 2, True),
                rom.read_integer(cursor + 4, 2, True)
            ))
            cursor += 6

        collision_data_start = cursor
        while True:
            collision_bytes = rom.read_bytes(cursor, 2)
            collision_bytes_int = rom.read_integer(cursor, 2)

            cursor += 2

            if collision_bytes == b'\x00\x41':
                # end byte
                break

            triangle_count = rom.read_integer(cursor, 2)
            cursor += 2

            entry_size = 8 if collision_bytes_int in SPECIAL_CD_WITH_PARAMS else 6

            triangles = []
            for _ in range(triangle_count):
                indices = (
                    rom.read_integer(cursor, 2),
                    rom.read_integer(cursor + 2, 2),
                    rom.read_integer(cursor + 4, 2)
                )
                cursor += entry_size
                triangles.append(indices)

            collisionmodel = CollisionModel(
                f"{hex(collision_data_start)}_{identifier}", vertices, triangles, collision_bytes_int)
            collision_data_start = cursor
            yield collisionmodel
