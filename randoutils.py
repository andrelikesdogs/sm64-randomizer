def hexlify(l):
  if type(l) == list or type(l) == tuple:
    return [(hexlify(v)) for v in l]
  else:
    if l == None:
      return 'None'
    else:
      return hex(l)

def pretty_print_table(title, data):
  print(title.center(73, "-"))
  for (label, value ) in data.items():
    print(f' {str(label).ljust(30, " ")} {str(value).ljust(30, " ")}')
    
  print("-" * 73)
  print()