WALKABLE_COLLISION_TYPES = [
  0x00, # environment default
  0x29, # default floor with noise
  0x14, # slightly slippery
  0x15, # anti slippery
  0x0B, # close camera
]

class Geometry:
  def __init__(self, vertices, triangles, collision_type, index):
    self.vertices = vertices
    self.triangles = triangles
    self.collision_type = collision_type
    self.index = index
    self.normals = []

    self.calc_normals()

  def calc_normals(self):
    for vertice_indices in self.triangles:
      (a, b, c) = tuple(map(lambda i : self.vertices[i], vertice_indices))

      u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
      v = (c[0] - a[0], c[1] - a[1], c[2] - c[2])

      normal = ((
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
      ))
      
      self.normals.append(normal)
    pass

class LevelGeometry:
  def __init__(self, level):
    self.level = level
    self.area_geometries = {}

  def add_area(self, area_id, vertices, triangles, collision_type):
    if area_id not in self.area_geometries:
      self.area_geometries[area_id] = []
    
    if area_id == 0x2: return
    
    self.area_geometries[area_id].append(Geometry(vertices, triangles, collision_type, len(self.area_geometries[area_id])))