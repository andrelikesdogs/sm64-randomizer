from __version__ import __version__
from typing import NamedTuple
from tkinter import Tk, ttk, BOTH, LEFT, RIGHT, TOP, W, Frame, Label, Button, Entry, filedialog, StringVar, Checkbutton, BooleanVar, Menu
import re
import os
import sys

# Source: https://jakirkpatrick.wordpress.com/2012/02/01/making-a-hovering-box-in-tkinter/
class HoverInfo(Menu):
  def __init__(self, parent, text, command=None):
    self._com = command
    Menu.__init__(self,parent, tearoff=0)
    if not isinstance(text, str):
      raise TypeError('Trying to initialise a Hover Menu with a non string type: ' + text.__class__.__name__)
    toktext=re.split('\n', text)
    for t in toktext:
      self.add_command(label = t)
      self._displayed=False
    self.master.bind("<Enter>",self.Display )
    self.master.bind("<Leave>",self.Remove )

  def __del__(self):
    self.master.unbind("<Enter>")
    self.master.unbind("<Leave>")

  def Display(self,event):
    if not self._displayed:
      self._displayed=True
      self.post(event.x_root, event.y_root)
    if self._com != None:
      self.master.unbind_all("<Return>")
      self.master.bind_all("<Return>", self.Click)

  def Remove(self, event):
    if self._displayed:
      self._displayed=False
      self.unpost()
    if self._com != None:
      self.unbind_all("<Return>")

  def Click(self, event):
    self._com()
  
class SettingField(NamedTuple):
  type: str
  help: str
  label: str
  value: str = None
  choices: list = []

class GuiApplication:
  def __init__(self):
    self.window = Tk()
    self.window.wm_title(f"SM64 Randomizer by Andrey - v{__version__}")
    self.window.resizable(False, False)

    self.selections = {
      'input_rom': StringVar(),
      'output_rom': StringVar(),
      'shuffle_levels': BooleanVar(),
      'shuffle_objects': BooleanVar(),
      'shuffle_music': BooleanVar(),
      'shuffle_paintings': StringVar("off"),
      'shuffle_colors': BooleanVar(),
      'shuffle_mario_color': BooleanVar()
    }

    self.checkbox_text = {}

    self.notebook = ttk.Notebook(self.window)
    self.frames = {
      'rom-settings': ttk.Frame(self.notebook),
      'general': ttk.Frame(self.notebook),
      'asthetics': ttk.Frame(self.notebook),
    }

    self.notebook.add(self.frames['rom-settings'], text='ROM Options')
    self.notebook.add(self.frames['general'], text='Main Rules')
    self.notebook.add(self.frames['asthetics'], text='Asthetic Rules')

    self.add_rom_settings()
    self.add_general_settings()

    self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
    self.window.update_idletasks()
    self.window.mainloop()

  def select_rom_input(self):
    input_rom = filedialog.askopenfilename(title="Select Input ROM", filetypes=[("ROM Files", (".z64")), ("All Files", "*")])

    if input_rom != "":
      self.selections['input_rom'].set(input_rom)
      if self.selections['output_rom'].get() == "":
        path_parts = input_rom.split(".")
        guessed_output_file = f'{"".join(path_parts[:1])}.out.{path_parts[-1]}'
        self.selections['output_rom'].set(guessed_output_file)

  def select_rom_output(self):
    output_rom = filedialog.asksaveasfilename(title="Select Output Path", filetypes=[("ROM Files", (".z64"))], initialdir=self.selections["output_rom"], initialfile=self.selections["output_rom"].get().split(os.path.sep)[-1])

    if output_rom != "":
      self.selections['output_rom'].set(output_rom)

  def toggle_checkbox_label(self, key):
    def trigger():
      if bool(self.selections[key].get()):
        self.checkbox_text[key].set("Enabled")
      else:
        self.checkbox_text[key].set("Disabled")

    return trigger


  def add_setting_fields(self, settings, master):
    for key, fieldtuple in settings.items():
      optionFrame = Frame(master)

      self.checkbox_text[key] = StringVar()

      if bool(fieldtuple.value):
        self.checkbox_text[key].set("Enabled")
      else:
        self.checkbox_text[key].set("Disabled")

      optionLabel = Label(optionFrame, text=fieldtuple.label, width=20)
      optionLabel.pack(side=LEFT)

      if fieldtuple.type == 'checkbox':
        checkboxField = ttk.Checkbutton(optionFrame, command=self.toggle_checkbox_label(key), textvariable=self.checkbox_text[key], variable=self.selections[key])
        checkboxHover = HoverInfo(optionLabel, fieldtuple.help)
        checkboxField.pack(side=LEFT)
      elif fieldtuple.type == 'combobox':
        combo_field = ttk.Combobox(optionFrame, values=fieldtuple.choices.keys())
        combo_field.pack(side=LEFT)

      optionFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))

      

  def add_general_settings(self):
    general_settings = {
      'shuffle_levels': SettingField(
        type="checkbox",
        help="Enable shuffling of all level entries in the game",
        label="Shuffle Levels",
        value=False
      ),
      'shuffle_objects': SettingField(
        type="checkbox",
        help="Enable shuffling of all object positions in all levels",
        label="Shuffle Objects",
        value=False
      ),
      'shuffle_music': SettingField(
        type="checkbox",
        help="Enable shuffling of all songs in all levels",
        label="Shuffle Music"
      )
    }

    self.add_setting_fields(general_settings, self.frames['general'])

  def add_asthetic_settings(self):
    asthetic_settings = {
      'shuffle_paintings': SettingField(
        type="combobox",
        choices={"off": "Vanilla", "match": "Match Levels", "random": "Random Levels"},
        help="How should castle paintings behave? Vanilla - no change at all, same painting as before. Match - matches random levels (without random levels, this is vanilla). Random - Completely shuffles paintings.",
        label="Shuffle Paintings"
      ),
      'shuffle_colors': SettingField(
        type="checkbox",
        help="Shuffle colors of various objects",
        label="Shuffle Colors"
      ),
      'shuffle_mario_color': SettingField(
        type="checkbox",
        help="Shuffle various parts of marios",
        label="Shuffle Marios Color"
      )
    }
    
    self.add_setting_fields(asthetic_settings, self.frames['asthetics'])

  def add_rom_settings(self):
    inputFrame = Frame(self.frames['rom-settings'])

    baseRomLabel = Label(inputFrame, text="Input ROM", width=20)
    baseRomLabel.pack(side=LEFT, padx=(0,0))
    baseRomEntry = Entry(inputFrame, width=40, textvariable=self.selections['input_rom'])
    baseRomEntry.pack(side=LEFT)
    romSelectButton = ttk.Button(inputFrame, text='Select ROM', command=self.select_rom_input, width=10)
    romSelectButton.pack(side=LEFT)

    inputFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))

    outputFrame = Frame(self.frames['rom-settings'])

    outputPathLabel = Label(outputFrame, text="Output ROM", width=20)
    outputPathLabel.pack(side=LEFT, padx=(0,0))
    outputRomEntry = Entry(outputFrame, width=40, textvariable=self.selections['output_rom'])
    outputRomEntry.pack(side=LEFT)
    outputSelectButton = ttk.Button(outputFrame, text='Select Output', command=self.select_rom_output, width=10)
    outputSelectButton.pack(side=LEFT)

    outputFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))


GuiApplication()