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

# From stackoverflow: https://stackoverflow.com/a/34325723
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
  """
  Call in a loop to create terminal progress bar
  @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
  """
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + '-' * (length - filledLength)
  print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
  # Print New Line on Complete
  if iteration == total: 
      print()

def generate_obj_for_level_geometry(level_geometry : "LevelGeometry"):
  print(f'generating .obj for {level_geometry.level.name}')
  output = ""

  output += f"# Collision Data for {level_geometry.level.name}\n"
  output += f"mtllib ./debug.mtl\n"

  vertex_total = 0
  #print(f'{len(level_geometry.area_geometries.keys())} areas')
  for (area_id, geometry) in level_geometry.area_geometries.items():
    output += f"g level_area_{area_id}\n"
    
    #print(collision_entry)
    
    for vertex in geometry.vertices:
      output += "v " + " ".join(list(map(str, map(format_float, vertex)))) + "\n"
    
    # dont output triangles on layer 0, origin layer
    for (index, triangle) in enumerate(geometry.faces):
      #normal = round(clamp(abs(geometry.face_normals[index][1]), 0, 1000) / 1000)
      collision_type = level_geometry.get_collision_type_for_triangle(area_id, index)
      output += f"# Collision Type: {hex(collision_type)}\n"
      output += f"usemtl debug_{collision_type}\n"

      #output += f"usemtl debug_gradient_{normal}\n"
      output += "f " + " ".join(list(map(lambda x: str(vertex_total + x), triangle))) + "\n"

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