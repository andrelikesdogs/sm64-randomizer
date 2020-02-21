from PIL import Image
import numpy as np

class N64Image:
  def __init__(self, img : Image):
    self.img = img
    self.bytes_original = self.img.tobytes()

  @staticmethod
  def scale_8_to_5(val):
    return int(((((val) + 4) * 0x1F) / 0xFF))

  @staticmethod
  def scale_5_to_8(val):
    return int(int(val * 0xFF) / 0x1F)
  
  def read_rgba16(self):
    """ Returns the loaded image as a bytearray of the RGBA16 format present on the N64

    Returns:
      bytes -- A bytes object with the current image in RGBA16 format
    """

    (width, height) = self.img.size
    px = self.img.load()

    n64_img_bytes = bytearray(len(self.bytes_original))
    
    for y in range(0, height):
      for x in range(0, width):
        idx = (y * width + x) * 2

        (r, g, b, a) = px[x, y]

        r_5 = N64Image.scale_8_to_5(r)
        g_5 = N64Image.scale_8_to_5(g)
        b_5 = N64Image.scale_8_to_5(b)

        n64_img_bytes[idx] = int((r_5 << 3) | (g_5 >> 2))
        n64_img_bytes[idx+1] = int(((g & 0x03) << 6) | (b_5 << 1) | (1 if a > 0 else 0))
    
    return bytes(n64_img_bytes)

class Imaging:
  @staticmethod
  def parse_image(path):
    with open(path, "rb") as file:
      loaded_img = Image.open(file)

      return N64Image(loaded_img)

  @staticmethod
  def from_ingame(rom, texture):
    ingame_bytes = rom.read_bytes(texture.position, texture.size)
    
    width = texture.width
    height = texture.height

    img_bytes = np.zeros((width, height, 4), dtype="uint8")
    for y in range(0, height):
      for x in range(0, width):
        img_idx = (y * width + x)
        idx = img_idx * 2

        px1 = ingame_bytes[idx]
        px2 = ingame_bytes[idx+1]

        r = N64Image.scale_5_to_8((px1 & 0xF8) >> 3)
        g = N64Image.scale_5_to_8((px1 & 0x07) << 2 | ((px2 & 0xC0) >> 6))
        b = N64Image.scale_5_to_8((px1 & 0x3E) >> 1)
        a = 255 if (px2 & 0x1) > 0 else 0

        img_bytes[y,x,0] = r
        img_bytes[y,x,1] = g
        img_bytes[y,x,2] = b
        img_bytes[y,x,3] = a
    
    img = Image.fromarray(img_bytes)
    #img.show()
    return N64Image(img)