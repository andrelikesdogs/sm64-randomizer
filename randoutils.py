import io
import math
from random import random

def hexlify(l):
  if type(l) == list or type(l) == tuple:
    return [(hexlify(v)) for v in l]
  else:
    if l == None:
      return 'None'
    else:
      return hex(l)

def format_binary(bin_data):
  if bin_data is None:
    return 'NO DATA'

  return ' '.join(hex(b)[2:].upper().rjust(2, '0') for b in bin_data)

def pretty_print_table(title, data):
  print(title.center(73, "-"))
  longest_line = max([len(label) for label in data.keys()])

  for (label, value ) in data.items():
    print(f' {str(label).ljust(longest_line + 2, " ")} {str(value).ljust(longest_line + 2, " ")}', end='\n')
    
  print("-" * 73)
  #print()

def format_float(f):
  return f"{f:.5f}"

def clamp(v, mi, ma):
  return max(v, min(v, ma), mi)

def generate_obj_for_level_geometry(level_geometry : "LevelGeometry"):
  print(f'generating .obj for {level_geometry.level.name}')
  output = ""

  output += f"# Collision Data for {level_geometry.level.name}\n"
  output += f"mtllib ./debug.mtl\n"

  vertex_total = 0
  #print(f'{len(level_geometry.area_geometries.keys())} areas')
  for (area_id, layers) in level_geometry.area_geometries.items():
    output += f"g level_area_{area_id}\n"
    
    for layer_index, geometry in enumerate(layers):
      #print(collision_entry)
      collision_type = geometry.collision_type
      #output += f"usemtl debug_{collision_type}\n"
      output += f"# Collision Type: {hex(collision_type)}\n"

      for vertex in geometry.vertices:
        output += "v " + " ".join(list(map(str, map(format_float, vertex)))) + "\n"
      
      # dont output triangles on layer 0, origin layer
      for (index, triangle) in enumerate(geometry.triangles):
        normal = round(clamp(abs(geometry.normals[index][1]), 0, 1000) / 1000)
        output += f"usemtl debug_gradient_{normal}\n"
        output += "f " + " ".join(list(map(lambda x: str(vertex_total + x + 1), triangle))) + "\n"


      """
      vertex_total += len(geometry.vertices)
      for (normal_index, normal) in enumerate(geometry.normals):
        normal_start = normal
        mag = math.sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
        norm = (normal[0] * mag, normal[1] * mag, normal[2] * mag)
        normal_end = tuple(map(lambda seq: normal[seq[0]] + seq[1] * norm[seq[0]] * 5, enumerate(normal)))
        output += "v " + " ".join(list(map(str, map(format_float, normal_start)))) + "\n"
        output += "v " + " ".join(list(map(str, map(format_float, normal_end)))) + "\n"
        output += "l " + str(vertex_total) + " " + str(vertex_total + 1) + "\n"
        vertex_total += 2
      """

  return output

distinguishable_colors = [(25, 25, 112), (0, 100, 0), (255, 0, 0), (255, 215, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255), (255, 182, 193)]
def generate_debug_materials():
  lines = []
  for index in range(2**16):
    r = random()
    g = random()
    b = random()
    lines.append(f'newmtl debug_{index}')
    lines.append(f'Ka {r} {g} {b}')
    lines.append(f'Kd {r} {g} {b}')
    lines.append('Ks 0.000 0.000 0.000')
    lines.append('Ns 10.000')
  
  for index in range(1000):
    c = index / 1000
    lines.append(f'newmtl debug_gradient_{index}')
    lines.append(f'Ka {c} {c} {c}')
    lines.append(f'Kd {c} {c} {c}')
    lines.append('Ks 0.000 0.000 0.000')
    lines.append('Ns 10.000')


  return "\n".join(lines)