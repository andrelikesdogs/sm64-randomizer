from __version__ import __version__
from typing import NamedTuple
from tkinter import Tk, ttk, BOTH, LEFT, RIGHT, TOP, BOTTOM, CENTER, W, X, Y, Frame, Label, Entry, filedialog, StringVar, Checkbutton, BooleanVar, Menu, Toplevel, OptionMenu, messagebox, PhotoImage
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

class GuiApplication:
  def __init__(self):
    self.window = Tk()
    self.window.title(MAIN_TITLE)
    
    # this is so dumb
    if system() == 'Windows':
      with open('temp_icon.ico', 'wb') as temp_icon:
        temp_icon.write(base64.b64decode(ICON_WIN))
        self.window.iconbitmap('temp_icon.ico')
      os.remove('temp_icon.ico')

    self.window.wm_title(MAIN_TITLE)
    #self.window.resizable(False, False)

    # stupid shit only happens on mac???
    if system() == "Darwin":
      self.window.tk_setPalette(background="#e8e8e8")

    self.initialize_gui()

  def initialize_gui(self, initial_values = None):
    self.selections = {}
    self.combobox_selections = {}
    self.checkbox_text = {}

    self.main_frame = Frame(self.window)
    
    self.gridcontainer = Frame(self.main_frame)
    self.frames = {
      'rom-settings': ttk.LabelFrame(self.gridcontainer, text="ROM Settings"),
      'gameplay': ttk.LabelFrame(self.gridcontainer, text="Gameplay Settings"),
      'aesthetics': ttk.LabelFrame(self.gridcontainer, text="Aesthetic Settings"),
    }

    self.frames['rom-settings'].pack(side=TOP, fill=X, padx=2, pady=2)
    self.frames['gameplay'].pack(side=LEFT, fill=BOTH, expand=True, anchor="w", padx=2, pady=2)
    self.frames['aesthetics'].pack(side=RIGHT, fill=BOTH, expand=True, anchor="w", padx=2, pady=2)

    #self.gridcontainer.add(self.frames['rom-settings'], text='ROM Options')
    #self.gridcontainer.add(self.frames['gameplay'], text='Gameplay Rules')
    #self.gridcontainer.add(self.frames['aesthetic'], text='Aesthetic Rules')

    self.add_rom_settings()
    self.add_settings_from_file()

    self.add_main_settings()

    self.gridcontainer.pack(expand=True, fill=BOTH, anchor="center", padx=5, pady=5)
    self.main_frame.pack(expand=True, fill=BOTH)

    self.window.update_idletasks()
    self.window.mainloop()

  def select_rom_input(self):
    input_rom = filedialog.askopenfilename(title="Select Input ROM", filetypes=[("ROM Files", (".z64")), ("All Files", "*")])

    if input_rom != "":
      self.selections['input_rom'].set(input_rom)
      if self.selections['output_rom'].get() == "":
        path_parts = input_rom.split(".")
        guessed_output_file = f'{".".join(path_parts[:-1])}.out.{path_parts[-1]}'
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
    try:
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
          params.append(tkinter_var.get())
        elif isinstance(tkinter_var, BooleanVar):
          # boolean args work by adding the param or not
          if tkinter_var.get():
            params.append(key_in_arg_format)
        elif isinstance(tkinter_var, StringVar):
          params.append(key_in_arg_format)
          params.append(quote(tkinter_var.get()))
        else:
          raise NotImplementedError(f'arg format for {type(tkinter_var)} is not implemented yet')
      
      args = [input_rom, *params]
      from Rom import ROM

      test_output = os.path.join(tempfile.gettempdir(), 'test_output.z64')
      try:
        with ROM(input_rom, test_output) as test_rom:
          test_rom.verify_header()
      except Exception as excp:
        messagebox.showerror(title="ROM Generation failed", message=f'Sorry, the specified ROM is not valid. Verification failed with error: {excp}')
        
      sys.argv = ['main.py', *args]
      try:
        import CLI
      except Exception as err:
        messagebox.showerror(f"Unfortunately, generation failed with error:\n {err}\nPlease submit this error to the projects github: https://github.com/andre-meyer/sm64-randomizer/issues")
        print(err)

      rom_output = self.selections['output_rom'].get()
      (folder_containing_rom, filename_output) = os.path.split(rom_output)
      messagebox.showinfo(title="ROM Generation completed!", message=f"Your randomized ROM was created as \"{filename_output}\"! Have fun!")
      if system() == "Windows":
        subprocess.Popen('explorer /select,"' + rom_output.replace("/", "\\") + '"', shell=True)
      else:
        webbrowser.open("file:///" + folder_containing_rom)
      return True
    except Exception as excp:
      messagebox.showerror(title="ROM Generation failed", message=f'Sorry, ROM generation failed with error:\n {excp}\nPlease submit this error to the projects github: https://github.com/andre-meyer/sm64-randomizer/issues')
      
  def add_setting_field(self, field):
    master = self.frames[field['category']]
    optionFrame = Frame(master)
    key = field['name']

<<<<<<< HEAD
    if 'default' in field and type(field) is dict:
      if 'GUI' in field['default']:
        self.selections

=======
>>>>>>> 4b060e46564f7771d95c8c5f8a3fa2f764ac6a08
    if field['type'] == 'checkbox':
      self.selections[key] = BooleanVar(optionFrame)
      checkboxField = ttk.Checkbutton(optionFrame, text=field['label'], variable=self.selections[key])
      if 'help' in field:
        CreateToolTip(checkboxField, field['help'])
      
      checkboxField.pack(side=LEFT)
    elif field['type'] == 'select':
      optionLabel = ttk.Label(optionFrame, text=field['label'])
      optionLabel.pack(side=LEFT)
      if 'help' in field:
        CreateToolTip(optionLabel, field['help'])
      
      self.selections[key] = StringVar(optionFrame)
      self.combobox_selections[key] = StringVar(optionFrame)

      choice_dict = { option['label']: option['value'] for option in field['options']}
      choice_dict_invert = { option['value']: option['label'] for option in field['options']}
      self.selections[key].set(field['options'][0]['value'])

      optionsField = ttk.OptionMenu(
        optionFrame,
        self.combobox_selections[key],
        field['options'][0]['label'],
        *[option['label'] for option in field['options']],
        command=lambda *args, sel_key=key, choices=choice_dict: self.selections[sel_key].set(choices[self.combobox_selections[sel_key].get()])
      )
      self.selections[key].trace('w', lambda *args, sel_key=key, choices=choice_dict_invert: self.combobox_selections[sel_key].set(choice_dict_invert[self.selections[sel_key].get()]))
      
      optionsField.pack(side=LEFT, fill=X, expand=True)


    optionFrame.pack(side=TOP, padx=5, pady=(5,1), fill=X)

  def add_settings_from_file(self):
    with open(os.path.join('Data', 'configurableParams.json')) as json_file:
      fields = json.loads(json_file.read())

      for field in fields:
        self.add_setting_field(field)

  """
  def add_gameplay_settings(self):
    self.add_setting_fields(gameplay_settings, self.frames['gameplay'])

  def add_aesthetic_settings(self):
    self.add_setting_fields(aesthetic_settings, self.frames['aesthetic'])
  """

  def add_main_settings(self):
    buttonsFrame = Frame(self.main_frame, padx=5, pady=5, height=60)
    buttonsFrame.pack_propagate(0)

    generateButton = ttk.Button(buttonsFrame, text="Generate ROM", command=self.generate_rom, width=10)
    generateButton.pack(side=LEFT, fill=BOTH, expand=True)
    self.copySettings = ttk.Button(buttonsFrame, text="Copy Settings to Clipboard", command=self.copy_to_clipboard, width=20)
    self.copySettings.pack(side=LEFT, fill=BOTH, expand=True)
    self.pasteSettings = ttk.Button(buttonsFrame, text="Paste Settings from Clipboard", command=self.read_from_clipboard, width=30)
    self.pasteSettings.pack(side=LEFT, fill=BOTH, expand=True)

    buttonsFrame.pack(fill=X, anchor="center", side=BOTTOM)

  def add_rom_settings(self):
    inputFrame = Frame(self.frames['rom-settings'])
    self.seed_entry = StringVar()
    self.seed_entry.trace('w', self.set_seed_as_num)

    self.selections['seed'] = StringVar()
    self.set_random_seed()
    seedFrame = Frame(inputFrame)

    seedLabel = Label(seedFrame, text="Seed", width=10)
    seedLabel.pack(side=LEFT)
    seedEntry = Entry(seedFrame, textvariable=self.seed_entry)
    seedEntry.pack(side=LEFT, fill=BOTH, expand=True)
    seedRandom = ttk.Button(seedFrame, text='New', command=self.set_random_seed, width=15)
    seedRandom.pack(side=RIGHT)

    seedFrame.pack(side=TOP, fill=X, expand=True)

    self.selections['input_rom'] = StringVar()

    baseRomLabel = Label(inputFrame, text="Input ROM", width=10)
    baseRomLabel.pack(side=LEFT, padx=(0,0))
    baseRomEntry = Entry(inputFrame, textvariable=self.selections['input_rom'])
    baseRomEntry.pack(side=LEFT, fill=BOTH, expand=True)
    romSelectButton = ttk.Button(inputFrame, text='Select ROM', command=self.select_rom_input, width=15)
    romSelectButton.pack(side=RIGHT)

    inputFrame.pack(side=TOP, fill=X, expand=True)

    outputFrame = Frame(self.frames['rom-settings'])
    self.selections['output_rom'] = StringVar()

    outputPathLabel = Label(outputFrame, text="Output ROM", width=10)
    outputPathLabel.pack(side=LEFT, padx=(0,0))
    outputRomEntry = Entry(outputFrame, textvariable=self.selections['output_rom'])
    outputRomEntry.pack(side=LEFT, fill=BOTH, expand=True)
    outputSelectButton = ttk.Button(outputFrame, text='Select Output', command=self.select_rom_output, width=15)
    outputSelectButton.pack(side=RIGHT)

    outputFrame.pack(side=TOP, fill=X, expand=True)


GuiApplication()