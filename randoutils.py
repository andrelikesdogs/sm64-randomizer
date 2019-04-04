def hexlify(l):
  if type(l) == list or type(l) == tuple:
    return [(hexlify(v)) for v in l]
  else:
    if l == None:
      return 'None'
    else:
      return hex(l)