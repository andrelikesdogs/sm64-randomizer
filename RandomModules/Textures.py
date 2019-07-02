from typing import List, Union, NamedTuple

class Texture(NamedTuple):
  position: int
  size: int
  width: int
  height: int
  name: str

class MultiTexture(NamedTuple):
  name: str
  textures: List[Texture]

paintings = [
  ('bob', 0xA800, 0xB800),
  ('ccm', 0xC800, 0xD800),
  ('wf', 0xE800, 0xF800),
  ('jrb', 0x10800, 0x11800),
  ('lll', 0x13800, 0x12800),
  ('ssl', 0x14800, 0x15800),
  ('wdw', 0x17800, 0x18800),
  ('thi', 0x19800, 0x1A800),
  ('ttm', 0x1B800, 0x1C800),
  ('ttc', 0x1D800, 0x1E800),
  ('sl', 0x1F800, 0x20800)
]

class TextureAtlas:
  definitions : dict = {}

  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def add_dynamic_positions(self):
    # castle paintings
    (paintings_start, _) = self.rom.segments_sequentially[26]
    for (lvl_name, upper, lower) in paintings:
      TextureAtlas.add_texture_definition(f'painting_{lvl_name}', MultiTexture(
        lvl_name,
        [
          Texture(
            paintings_start + upper,
            int(32*64*16 / 8),
            64,
            32,
            f'painting_{lvl_name}_upper'
          ),
          Texture(
            paintings_start + lower,
            int(32*64*16 / 8),
            64,
            32,
            f'painting_{lvl_name}_lower'
          ),
        ]
      ))

    # the "unknown" texture
    (castle_ground_textures_start, _) = self.rom.segments_sequentially[39]
    unknown_painting_start = castle_ground_textures_start + 0x1894
    TextureAtlas.add_texture_definition('painting_unknown', MultiTexture(
      'unknown',
      [
        Texture(
          unknown_painting_start + 0x6800,
            int(32*64*16 / 8),
            64,
            32,
            f'painting_unknown_upper'
        ),
          Texture(
            unknown_painting_start + 0x6800,
              int(32*64*16 / 8),
              64,
              32,
              f'painting_unknown_lower'
          )
      ]
    ))

    TextureAtlas.add_texture_definition('castle_grounds_tree_shadow', Texture(
      unknown_painting_start + 0xBC00,
      int(32*32*16/8),
      32,
      32,
      f'castle_grounds_tree_shadow'
    ))

  @staticmethod
  def hide_texture(rom : "ROM", name):
    if name not in TextureAtlas.definitions:
      raise ValueError(f"{name} is not defined as a texture")
    
    definition = TextureAtlas.definitions[name]
    empty_data = bytes([0x0 for i in range(definition.size)])
    print(f"deleting texture {name}: {len(empty_data)} bytes")
    rom.write_bytes(definition.position + 0x13, empty_data) # 0x13: header


  @staticmethod
  def add_texture_definition(name, texture : Union[Texture, MultiTexture]):
    TextureAtlas.definitions[name] = texture

  @staticmethod
  def has_texture(name):
    return name in TextureAtlas.definitions

  @staticmethod
  def copy_texture_from_to(rom : "ROM", name_a : str, name_b : str):
    if name_a not in TextureAtlas.definitions:
      raise ValueError(f'{name_a} not found as a defined texture')

    if name_b not in TextureAtlas.definitions:
      raise ValueError(f'{name_b} not found as a defined texture')

    if rom.rom_type != 'EXTENDED':
      raise ValueError(f'This ROM file is not extended, and thus can\'t modify textures (atleast right now)')

    texture_a = TextureAtlas.definitions[name_a]
    texture_b = TextureAtlas.definitions[name_b]
    if len(texture_a.textures) != len(texture_b.textures):
      raise ValueError('Can only swap textures between two texture groups with the same length right now')

    texs_a = []
    texs_b = []

    for texture in texture_a.textures:
      texs_a.append(rom.read_bytes(texture.position, texture.size))
    for texture in texture_b.textures:
      texs_b.append(rom.read_bytes(texture.position, texture.size))
    
    for idx in range(len(texs_a)):
      bytes_from = texs_b[idx]
      tex_to = texture_a.textures[idx]

      rom.write_byte(tex_to.position, bytes_from)
