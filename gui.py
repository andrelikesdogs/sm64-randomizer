import wx

class Application(wx.Frame):
  def __init__(self, *args, **kw):
    # ensure the parent's __init__ is called
    super(Application, self).__init__(*args, **kw)

    self.create_rom_settings()
    self.create_setting_panels()

  def create_rom_settings(self):
    self.rom_settings_container = wx.StaticBox(self, label="ROM Settings")
    self.rom_settings_container.set_sizer()

  def create_setting_panels(self):
    self.settings_container = wx.StaticBox(self, label="Randomizer Settings")

app = wx.App()
frm = Application(None, title='Super Mario 64 Randomizer by Andrey')
frm.Show()
app.MainLoop()å