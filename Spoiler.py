import os

class SpoilerLog:
  entries : dict = {}

  @staticmethod
  def add_entry(module : str, value : str):
    if module not in SpoilerLog.entries:
      SpoilerLog.entries[module] = []

    SpoilerLog.entries[module].append(value)

  @staticmethod
  def output():
    with open('sm64_rando_spoiler.log', 'w') as spoiler_log_file:
      for module in list(SpoilerLog.entries.keys()):
        spoiler_log_file.write(module.upper().center(40, '-') + '\n')
        for entry in SpoilerLog.entries[module]:
          spoiler_log_file.write(f'{entry}\n')