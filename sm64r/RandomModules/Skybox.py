# Skyboxes
SKYBOX_IDS = [
  0x00, # Bob-Omb's Battlefield
  0x01, # Lethal Lava Land
  0x02, # Wet Dry World
  0x03, # Rainbow Ride
  0x04, # Cool, Cool Mountain
  0x05, # Shifting Sand Land
  0x06, # Big Boo's Haunt
  0x07, # Bowser 1 Course
  0x08, # Jolly Roger Bay
  0x09, # Bowser 3 Course
]

class SkyboxRandomizer:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
