from PIL import Image

class N64Image:
  def __init__(self, img : Image):
    self.img = img
    self.bytes_original = self.img.tobytes()

  def scale_8_to_5(self, val):
    return int(((((val) + 4) * 0x1F) / 0xFF))

  def read_rgba16(self):
    """ Returns the loaded image as a bytearray of the RGBA16 format present on the N64

    Returns:
      bytes -- A bytes object with the current image in RGBA16 format
    """

    (width, height) = self.img.size
    px = self.img.load()

    n64_img_bytes = bytearray(len(self.bytes_original))
    print(len(n64_img_bytes))
    for y in range(0, width):
      for x in range(0, height):
        idx = (y * width + x) * 2

        (r, g, b, a) = px[x, y]

        r_5 = self.scale_8_to_5(r)
        g_5 = self.scale_8_to_5(g)
        b_5 = self.scale_8_to_5(b)

        n64_img_bytes[idx] = int((r_5 << 3) | (g_5 >> 2))
        n64_img_bytes[idx+1] = int(((g & 0x03) << 6) | (b_5 << 1) | (1 if a > 0 else 0))
    
    print(len(self.bytes_original))
    return bytes(n64_img_bytes)

class Imaging:
  @staticmethod
  def parse_image(path):
    with open(path, "rb") as file:
      loaded_img = Image.open(file)

      return N64Image(loaded_img)
