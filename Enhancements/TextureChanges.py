from RandomModules.Textures import TextureAtlas

class TextureChanges:
  def __init__(self, rom):
    self.rom = rom

  def remove_tree_shadows(self):
    TextureAtlas.hide_texture(self.rom, "castle_grounds_tree_shadow")
    