from typing import List, Union, NamedTuple
import numpy as np
from PIL import Image
from pathlib import Path
import os

from sm64r.Parsers.Imaging import Imaging
from sm64r.Constants import application_path

class Texture(NamedTuple):
  position: int
  size: int
  width: int
  height: int
  name: str

class InMemoryTexture(NamedTuple):
  position: int
  size: int
  width: int
  height: int
  name: str
  data: bytes

class MultiTexture(NamedTuple):
  name: str
  textures: List[Texture]

'''
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
'''

class TextureAtlas:
  definitions : dict = {}

  def __init__(self, rom : 'ROM'):
    self.rom = rom

  def add_level_paintings(self):
    """ Adds all in-game paintings from the configuration to the TextureAtlas
    """
    for level in self.rom.config.levels:
      # load paintings
      if "shuffle_painting" in level.properties:
        for painting_shuffle in level.properties["shuffle_painting"]:
          # custom paintings get loaded on rom read
          # game paintings get loaded here
          if "game_painting" in painting_shuffle.keys():
            #print(f"added {level.name} painting")
            self.add_segmented_position_texture(painting_shuffle["game_painting"], painting_shuffle["sections"])
      

  def add_vanilla_portrait_custom_paintings(self):
    """ Loads the custom-made painting for levels that don't have a painting in the original game.
    """
    opts = self.rom.config

    # read custom paintings
    if opts.custom_paintings:
      for author in opts.custom_paintings.keys():
        for painting_definition in opts.custom_paintings[author]:
          TextureAtlas.import_texture(painting_definition['name'], painting_definition['file'], painting_definition['transform'])


    '''
    bbh_painting = Imaging.parse_image(os.path.join(application_path, "Assets/img/custom_portraits/distressedphilosopher/BBH.png"))
    full_img_bytes = bbh_painting.read_rgba16()

    bbh_painting_upper = full_img_bytes[0:4096] # upper part
    bbh_painting_lower = full_img_bytes[4096:8192] # lower part

    TextureAtlas.add_texture_definition('painting_bbh', MultiTexture(
      'bbh',
      [
        InMemoryTexture(
          None,
          int(32 * 64 * 16 / 8),
          64,
          32,
          'painting_bbh_upper',
          bbh_painting_upper
        ),
        InMemoryTexture(
          None,
          int(32 * 64 * 16 / 8),
          64,
          32,
          'painting_bbh_lower',
          bbh_painting_lower
        )
      ]
    ))

    self.copy_texture_from_to(self.rom, "painting_bbh", "painting_bob")
    '''

  @staticmethod
  def get_byte_size_for_format(texture_format, size):
    if texture_format == 'rgba16':
      return int(size[0] * size[1] * 16 / 8)
    else:
      raise ValueError(f'unknown format or not implemented: {texture_format}')

  def add_segmented_position_texture(self, name : str, sections):
    textures = []

    for section in sections:
      segment_start = self.rom.segments_sequentially[section["segment_index"]][0]
      position = segment_start + section["segment_offset"]

      textures.append(Texture(
        position,
        TextureAtlas.get_byte_size_for_format(section["format"] if "format" in section else "rgba16", section["size"]),
        section["size"][0],
        section["size"][1],
        section["name"]
      ))

    if not len(textures):
      raise ValueError("no sections parsed")

    if len(sections) > 1:
      TextureAtlas.add_texture_definition(name, MultiTexture(name, textures))
    else:
      TextureAtlas.add_texture_definition(name, textures[0])
    
  @staticmethod
  def import_texture(name, filepath, transforms = dict()):
    full_path = os.path.join(application_path, filepath)
    if not os.path.exists(full_path):
      raise ValueError(f'custom texture {name} could not be found: {filepath}')

    parsed_img = Imaging.parse_image(full_path)
    rgba_img = parsed_img.read_rgba16()

    sections = [InMemoryTexture(
      None,
      TextureAtlas.get_byte_size_for_format('rgba16', parsed_img.img.size),
      parsed_img.img.size[0],
      parsed_img.img.size[1],
      name,
      rgba_img,
    )]

    if transforms:
      for transform in transforms:
        if transform["type"] == "split-horizontal":
          full_size = int(parsed_img.img.size[0] * parsed_img.img.size[1] * 2)
          half_size = int(full_size / 2)
          #print(full_size, half_size)

          part_a = rgba_img[0:half_size]
          part_b = rgba_img[half_size+1:full_size]

          sections = [
            InMemoryTexture(
              f'{name}_a',
              TextureAtlas.get_byte_size_for_format('rgba16', parsed_img.img.size)/2,
              parsed_img.img.size[0],
              parsed_img.img.size[1]/2,
              f'{name}_a',
              part_a
            ),
            InMemoryTexture(
              f'{name}_b',
              TextureAtlas.get_byte_size_for_format('rgba16', parsed_img.img.size)/2,
              parsed_img.img.size[0],
              parsed_img.img.size[1]/2,
              f'{name}_b',
              part_b
            )
          ]

    if len(sections) > 1:
      TextureAtlas.add_texture_definition(name, MultiTexture(name, sections))
    else:
      TextureAtlas.add_texture_definition(name, sections[0])

  def add_dynamic_positions(self):
    # castle paintings
    # paintings start: 0xE0BB07
    '''
    (paintings_start, _) = self.rom.segments_sequentially[23]
    for (lvl_name, upper, lower) in paintings:
      # Paintings Start (USA, Extended): 0xE0BB07
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
    '''

    self.add_segmented_position_texture(
      'painting_unknown',
      [
        dict(
          segment_index = 37,
          segment_offset = 0x8094,
          size = [64, 32],
          name = 'painting_unknown_upper'
        ),dict(
          segment_index = 37,
          segment_offset = 0x8094,
          size = [64, 32],
          name = 'painting_unknown_lower'
        )
      ]
    )

    self.add_segmented_position_texture(
      'castle_grounds_tree_shadow',
      [
        dict(
          segment_index = 37,
          segment_offset = 0xD494,
          size = [32, 32],
          name = 'castle_grounds_tree_shadow'
        )
      ]
    )
    
    """
    (misc_textures_address_start, _) = self.rom.segments_sequentially[305]
    question_mark_icon = misc_textures_address_start + 0x818
    question_mark_texture = Texture(
      question_mark_icon,
      int(32*32*2),
      32,
      32,
      'question_mark'
    )
    
    image_bytes = TextureAtlas.add_texture_definition('question_mark', question_mark_texture)
    

    # load texture and resize
    b = self.rom.read_bytes(question_mark_texture.position, question_mark_texture.size)
    from_bytes = np.frombuffer(b, dtype=np.uint8)
    colors_format = np.zeros(from_bytes.size * 2, dtype=np.uint8)
    
    for idx in range(0, from_bytes.size, 2):
      c0 = from_bytes[idx]
      c1 = from_bytes[idx+1]

      new_idx = int(idx / 2)

      r = (((c0 & 0xF8) >> 3) * 0xFF) / 0x1F
      g = ((((c0 & 0x07) << 2) | ((c1 & 0xC0) >> 6)) * 0xFF) / 0x1F
      b = (((c1 & 0x3E) >> 1) * 0xFF) / 0x1F
      a = 255 if c1 & 0x1 > 0 else 0
      colors_format[new_idx * 4] = r
      colors_format[new_idx * 4 + 1] = g
      colors_format[new_idx * 4 + 2] = b
      colors_format[new_idx * 4 + 3] = a
    
    print(colors_format[0:100])
    colors_format = colors_format.reshape(question_mark_texture.width, question_mark_texture.height, 4)
    img = Image.fromarray(colors_format, 'RGBA')
    img_resized = img.resize((64, 64))
    img_upper = img_resized.crop((0, 0, 64, 32))
    img_lower = img_resized.crop((0, 32, 64, 64))
    
    TextureAtlas.add_texture_definition('painting_unknown', MultiTexture(
      'unknown',
      [
        InMemoryTexture(
          None,
          int(32*64*4)
        )
      ]
    ))
    """

  @staticmethod
  def hide_texture(rom : "ROM", name):
    if name not in TextureAtlas.definitions:
      raise ValueError(f"{name} is not defined as a texture")
    
    definition = TextureAtlas.definitions[name]
    empty_data = bytes([0x0 for i in range(definition.size)])
    #print(f"deleting texture {name}: {len(empty_data)} bytes")
    rom.write_bytes(definition.position + 0x13, empty_data) # 0x13: header

  @staticmethod
  def add_texture_definition(name, texture : Union[Texture, MultiTexture]):
    TextureAtlas.definitions[name] = texture

  @staticmethod
  def has_texture(name):
    return name in TextureAtlas.definitions

  @staticmethod
  def is_replacable(name):
    if name not in TextureAtlas.definitions:
      return False
      
    if type(TextureAtlas.definitions[name]) is MultiTexture:
      for defintion in TextureAtlas.definitions[name].textures:
        if type(defintion) is InMemoryTexture:
          return False
    
    if type(TextureAtlas.definitions[name]) is InMemoryTexture:
      return False
    
    return True

  @staticmethod
  def copy_texture_from_to(rom : "ROM", name_from : str, name_to : str):
    if name_from not in TextureAtlas.definitions:
      raise ValueError(f'{name_from} not found as a defined texture')

    if name_to not in TextureAtlas.definitions:
      raise ValueError(f'{name_to} not found as a defined texture')

    if rom.rom_type != 'EXTENDED':
      raise ValueError(f'This ROM file is not extended, and thus can\'t modify textures (atleast right now)')

    texture_from = TextureAtlas.definitions[name_from]
    texture_to = TextureAtlas.definitions[name_to]
    if len(texture_from.textures) != len(texture_to.textures):
      raise ValueError('Can only swap textures between two texture groups with the same length right now')

    if type(texture_to.textures[0]) is InMemoryTexture:
      raise ValueError(f'{name_to} is an in memory texture and can not be replaced')

    texs_from = []
    texs_to = []

    for texture in texture_from.textures:
      if type(texture) is InMemoryTexture:
        # read from var
        texs_from.append(texture.data)
      elif type(texture) is Texture:
        # read from rom
        texs_from.append(rom.read_bytes(texture.position, texture.size))

    for texture in texture_to.textures:
      if type(texture) is InMemoryTexture:
        # read from var
        texs_to.append(texture.data)
      elif type(texture) is Texture:
        # read from rom
        texs_to.append(rom.read_bytes(texture.position, texture.size))
        
    for idx in range(len(texs_from)):
      bytes_from = texs_from[idx]
      tex_to = texture_to.textures[idx]

      rom.write_byte(tex_to.position, bytes_from)
