from Functionality.Tweaks import TweaksFunctionality

class CutsceneFunctionality:
  def __init__(self, rom : 'ROM'):
    self.rom = rom
    self.tweaking = TweaksFunctionality(rom)

  def disable_all_cutscenes(self):
    self.tweaking.add_asm_patch(
      [
        (0x6BF0, bytes([0x24, 0x00])), # Peach Cutscene
        (0x6D90, bytes([0x24, 0x10, 0x00, 0x00])), # Lakitu Cutscene
        (0x4B7C, bytes([0x24, 0x00])), # Level Intros #1
        (0x4924, bytes([0x10, 0x00])), # Level Intros #2
      ]
    )