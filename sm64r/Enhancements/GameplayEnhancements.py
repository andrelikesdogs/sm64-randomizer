from sm64r.Enhancements.Tweaks import Tweaking

class Gameplay:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
    self.tweaking = Tweaking(rom)

  def disable_all_cutscenes(self):
    if self.rom.region in ['NORTH_AMERICA', 'EUROPE']:
      self.tweaking.add_asm_patch(
        [
          (0x6BD4, bytes([0x24, 0x00])), # Peach Cutscene
          (0x6D90, bytes([0x24, 0x10, 0x00, 0x00])), # Lakitu Cutscene
          (0x4B7C, bytes([0x24, 0x00])), # Level Intros #1
          (0x4924, bytes([0x10, 0x00])), # Level Intros #2
          (0x123F8, bytes([0x10, 0x00])), # Disable "Milestone" Messages
        ]
      )
  
  def disable_starwarp(self):
    self.tweaking.add_asm_patch(
      [
        (0x8C50, bytes([0x24, 0x08, 0x00, 0x01])) # Make all stars act like 100-coin star
      ]
    )