from __version__ import __version__
from typing import NamedTuple
from tkinter import Tk, ttk, BOTH, LEFT, RIGHT, TOP, CENTER, W, X, Y, Frame, Label, Button, Entry, filedialog, StringVar, Checkbutton, BooleanVar, Menu, Toplevel, OptionMenu, messagebox, PhotoImage
import subprocess
import re
import os
import sys
import tempfile
import io
import json
import pyperclip
import base64
from platform import system
from Icons import ICON_WIN
from threading import Timer
from shlex import quote
from random import randint
import webbrowser

MAIN_TITLE = f"SM64 Randomizer by @andremeyer93 - v{__version__}"

# Source: https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
class CreateToolTip(object):
  '''
  create a tooltip for a given widget
  '''
  def __init__(self, widget, text='widget info'):
    self.widget = widget
    self.text = text
    self.widget.bind("<Enter>", self.enter)
    self.widget.bind("<Leave>", self.close)
  def enter(self, event=None):
    x = y = 0
    x, y, cx, cy = self.widget.bbox("insert")
    x += self.widget.winfo_rootx() + 25
    y += self.widget.winfo_rooty() + 20
    # creates a toplevel window
    self.tw = Toplevel(self.widget)
    # Leaves only the label and removes the app window
    self.tw.wm_overrideredirect(True)
    self.tw.wm_geometry("+%d+%d" % (x, y))
    label = Label(self.tw, text=self.text, justify='left',
      wraplength=200, background='white', padx=4, pady=4)
    label.pack(ipadx=1)
  def close(self, event=None):
    if self.tw:
      self.tw.destroy()


class SettingField(NamedTuple):
  type: str
  help: str
  label: str
  value: str = None
  choices: list = []
  initial: str = None

gameplay_settings = {
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
  ),
  'shuffle_dialog': SettingField(
    type="checkbox",
    help="Enable shuffling of all dialogs in cutscenes, signs, prompts and from NPCs. This might act weird with prompts, e.g. when Koopa the Quick asks for a race.",
    label="Shuffle Dialog"
  )
}

aesthetic_settings = {
  'shuffle_paintings': SettingField(
    type="select",
    choices=[("off", "Vanilla"), ("match", "Match Levels"), ("random", "Random Levels")],
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

class GuiApplication:
  def __init__(self):
    self.window = Tk()

    if system() == 'Windows':
      file_data = base64.decodebytes(ICON_WIN)
      icon = PhotoImage(data=file_data)
      self.window.iconphoto(True, icon)
    
    self.window.wm_title(MAIN_TITLE)
    self.window.resizable(False, False)

    self.initialize_gui()

  def initialize_gui(self, initial_values = None):
    self.selections = {}
    self.combobox_selections = {}
    self.checkbox_text = {}

    self.notebook = ttk.Notebook(self.window)
    self.frames = {
      'rom-settings': ttk.Frame(self.notebook),
      'gameplay': ttk.Frame(self.notebook),
      'aesthetic': ttk.Frame(self.notebook),
    }

    self.notebook.add(self.frames['rom-settings'], text='ROM Options')
    self.notebook.add(self.frames['gameplay'], text='Gameplay Rules')
    self.notebook.add(self.frames['aesthetic'], text='Aesthetic Rules')

    self.add_rom_settings()
    self.add_gameplay_settings()
    self.add_aesthetic_settings()

    self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
    self.add_main_settings()

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

  def set_random_seed(self):
    self.seed_entry.set(randint(0, 1e19))

  def set_seed_as_num(self, *args):
    byte_entry = bytes(self.seed_entry.get(), 'utf8')
    self.selections['seed'].set(int.from_bytes(byte_entry, 'little', signed=False))

  def check_validity(self):
    rom_file = self.selections['input_rom'].get()
    self.check_error = None

    if not len(rom_file):
      self.check_error = 'Please select a ROM-File first'
      return False
    
    if not os.path.isfile(rom_file):
      self.check_error = 'The selected ROM is invalid'
      return False

    out_file = self.selections['output_rom'].get()
    if not len(out_file):
      self.check_error = 'Please select an output path'
      return False

    return True

  def read_from_clipboard(self):
    data = pyperclip.paste()

    try:
      json_data = json.loads(data)
    except Exception:
      messagebox.showerror(title=MAIN_TITLE, message=f"Sorry, the settings in your clipboard are not valid. Please try again.")
      return
    
    if json_data['version'] != __version__:
      messagebox.showerror(title=MAIN_TITLE, message=f"Sorry, the settings version do not match. Please ensure you're using the same version when copying the settings.")
      return

    json_data["input_rom"] = self.selections['input_rom'].get()
    json_data["output_rom"] = self.selections['output_rom'].get()
    
    for (key, tkinter_var) in self.selections.items():
      if key in json_data:
        tkinter_var.set(json_data[key])
    self.seed_entry.set(json_data["seed"])
    self.set_seed_as_num()

    self.pasteSettings.configure(text="Settings applied!")
    self.window.update()
    s = Timer(2, lambda: self.pasteSettings.configure(text="Paste Settings from Clipboard"))
    s.start()

  def find_setting_definition(self, key):
    for setting_dict in [gameplay_settings, aesthetic_settings]:
      for (setting_key, definition) in setting_dict.items():
        if setting_key == key:
          return definition
    return None

  def copy_to_clipboard(self):
    output = {
      "version": __version__
    }
    
    data = {key: var.get() for (key, var) in self.selections.items()}
    output.update(data)

    # this makes no sense for other people
    del output['input_rom']
    del output['output_rom']
    output['seed'] = self.seed_entry.get()
    
    pyperclip.copy(json.dumps(output))

    self.copySettings.configure(text="Settings copied!")
    s = Timer(2, lambda: self.copySettings.configure(text="Copy Settings to Clipboard"))
    s.start()

  def generate_rom(self):
    if not self.check_validity():
      messagebox.showerror(title="ROM Generation Failed", message=self.check_error)
      return
    
    params = []
    input_rom = None

    for (key, tkinter_var) in self.selections.items():
      key_in_arg_format = f"--{key.replace('_', '-')}"
      
      if key == 'input_rom':
        input_rom = tkinter_var.get()
      elif key == 'output_rom':
        params.append('--out')
        params.append(os.path.relpath(tkinter_var.get()))
      elif isinstance(tkinter_var, BooleanVar):
        # boolean args work by adding the param or not
        if tkinter_var.get():
          params.append(key_in_arg_format)
      elif isinstance(tkinter_var, StringVar):
        params.append(key_in_arg_format)
        params.append(quote(tkinter_var.get()))
      else:
        raise NotImplementedError(f'arg format for {type(tkinter_var)} is not implemented yet')
    
    args = [os.path.relpath(input_rom), *params]
    from Rom import ROM

    test_output = os.path.join(tempfile.gettempdir(), 'test_output.z64')
    with ROM(input_rom, test_output) as test_rom:
      try:
        test_rom.verify_header()
      except Exception as err:
        messagebox.showerror(title="ROM Header Invalid", message=f'Sorry, the specified ROM is not valid. Verification failed with error: {err.message}')
    
    sys.argv = ['main.py', *args]
    try:
      import CLI
    except Exception as err:
      messagebox.showerror(f"Unfortunately, generation failed with error:\n {err}\nPlease submit this error to the projects github: https://github.com/andre-meyer/sm64-randomizer/issues")
      print(err)

    rom_output = self.selections['output_rom'].get()
    (folder_containing_rom, filename_output) = os.path.split(rom_output)
    messagebox.showinfo(title="ROM Generation completed!", message=f"Your randomized ROM was created as \"{filename_output}\"! Have fun!")
    webbrowser.open("file:///" + folder_containing_rom)
    return True

  def add_setting_fields(self, settings, master):
    for key, fieldtuple in settings.items():
      optionFrame = Frame(master)

      optionLabel = Label(optionFrame, text=fieldtuple.label, width=20)
      optionLabel.pack(side=LEFT)

      if fieldtuple.type == 'checkbox':
        self.selections[key] = BooleanVar(optionFrame)
        self.checkbox_text[key] = StringVar()

        if bool(fieldtuple.value):
          self.checkbox_text[key].set("Enabled")
        else:
          self.checkbox_text[key].set("Disabled")
        
        self.selections[key].trace('w', lambda *args, sel_key=key: self.checkbox_text[sel_key].set("Enabled" if self.selections[sel_key].get() else "Disabled"))
        checkboxField = ttk.Checkbutton(optionFrame, textvariable=self.checkbox_text[key], variable=self.selections[key])
        CreateToolTip(optionLabel, fieldtuple.help)
        checkboxField.pack(side=LEFT)
      elif fieldtuple.type == 'select':
        self.selections[key] = StringVar(optionFrame)
        self.combobox_selections[key] = StringVar(optionFrame)

        choice_dict = { label: value for (value, label) in fieldtuple.choices}
        choice_dict_invert = { value: label for (value, label) in fieldtuple.choices}
        self.selections[key].set(fieldtuple.choices[0][0])

        optionsField = ttk.OptionMenu(
          optionFrame,
          self.combobox_selections[key],
          fieldtuple.choices[0][1],
          *[label for (value, label) in fieldtuple.choices],
          command=lambda *args, sel_key=key, choices=choice_dict: self.selections[sel_key].set(choices[self.combobox_selections[sel_key].get()])
        )
        self.selections[key].trace('w', lambda *args, sel_key=key, choices=choice_dict_invert: self.combobox_selections[sel_key].set(choice_dict_invert[self.selections[sel_key].get()]))
        CreateToolTip(optionLabel, fieldtuple.help)
        
        optionsField.pack(side=LEFT)

      optionFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))

      

  def add_gameplay_settings(self):
    self.add_setting_fields(gameplay_settings, self.frames['gameplay'])

  def add_aesthetic_settings(self):
    self.add_setting_fields(aesthetic_settings, self.frames['aesthetic'])

  def add_main_settings(self):
    self.seed_entry = StringVar()
    self.seed_entry.trace('w', self.set_seed_as_num)

    self.selections['seed'] = StringVar()
    self.set_random_seed()
    seedFrame = Frame(self.window, padx=12, pady=8)

    seedLabel = Label(seedFrame, text="Seed")
    seedLabel.pack(side=LEFT)
    seedEntry = Entry(seedFrame, textvariable=self.seed_entry)
    seedRandom = ttk.Button(seedFrame, text='New', command=self.set_random_seed, width=10)
    seedRandom.pack(side=RIGHT)
    seedEntry.pack(expand=True, fill=X)

    seedFrame.pack(fill=BOTH)

    buttonsFrame = Frame(self.window, padx=12, pady=8, height=60)
    buttonsFrame.pack_propagate(0)

    generateButton = ttk.Button(buttonsFrame, text="Generate ROM", command=self.generate_rom, width=15)
    generateButton.pack(side=LEFT, fill=Y, expand=True)
    self.copySettings = ttk.Button(buttonsFrame, text="Copy Settings to Clipboard", command=self.copy_to_clipboard, width=30)
    self.copySettings.pack(side=LEFT, fill=Y, expand=False)
    self.pasteSettings = ttk.Button(buttonsFrame, text="Paste Settings from Clipboard", command=self.read_from_clipboard, width=30)
    self.pasteSettings.pack(side=LEFT, fill=Y, expand=True)

    buttonsFrame.pack(fill=BOTH, anchor=CENTER, expand=True, side=TOP)

  def add_rom_settings(self):
    inputFrame = Frame(self.frames['rom-settings'])
    self.selections['input_rom'] = StringVar()

    baseRomLabel = Label(inputFrame, text="Input ROM", width=20)
    baseRomLabel.pack(side=LEFT, padx=(0,0))
    baseRomEntry = Entry(inputFrame, width=40, textvariable=self.selections['input_rom'])
    baseRomEntry.pack(side=LEFT)
    romSelectButton = ttk.Button(inputFrame, text='Select ROM', command=self.select_rom_input, width=10)
    romSelectButton.pack(side=LEFT)

    inputFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))

    outputFrame = Frame(self.frames['rom-settings'])
    self.selections['output_rom'] = StringVar()

    outputPathLabel = Label(outputFrame, text="Output ROM", width=20)
    outputPathLabel.pack(side=LEFT, padx=(0,0))
    outputRomEntry = Entry(outputFrame, width=40, textvariable=self.selections['output_rom'])
    outputRomEntry.pack(side=LEFT)
    outputSelectButton = ttk.Button(outputFrame, text='Select Output', command=self.select_rom_output, width=10)
    outputSelectButton.pack(side=LEFT)

    outputFrame.pack(side=TOP, anchor=W, padx=5, pady=(5,1))


GuiApplication()