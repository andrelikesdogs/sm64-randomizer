import wx
import sys

class Application(wx.Frame):
  def __init__(self, *args, **kw):
    # ensure the parent's __init__ is called
    super(Application, self).__init__(*args, **kw)
    print("This doesn't work yet")
    sys.exit(2)

  def create_rom_settings(self):
    self.rom_settings_container = wx.StaticBox(self.panel, label="ROM Settings")
    self.box_sizes.Add(self.rom_settings_container)

  def create_setting_panels(self):
    self.settings_container = wx.StaticBox(self.panel, label="Randomizer Settings")
    self.box_sizes.Add(self.settings_container)

app = wx.App()
frm = Application(None, title='Super Mario 64 Randomizer by Andrey')
frm.Show()
app.MainLoop()