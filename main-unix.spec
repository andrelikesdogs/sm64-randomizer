# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None
import os
libFolder = os.environ["pythonLocation"]+"/lib" if "pythonLocation" in os.environ else "lib"
print("LibFolder: \"" + libFolder + "\"")

a = Analysis(['main.py'],
             pathex=['/Users/andremeyer/Documents/Own/mario-64-rom-hacking/sm64-randomizer'],
             binaries=collect_dynamic_libs("rtree"),
             datas=[('README.md', '.'), ('LICENSE', '.'), ('Data', '.'), ('Assets', '.'), ('Config', '.'), (libFolder + '/python3.8/site-packages/trimesh/resources', 'trimesh/resources/')],
             hiddenimports=["pyperclip"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SM64_Randomizer_Generator',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='favicon.icns')
app = BUNDLE(exe,
             name='SM64_Randomizer_Generator.app',
             icon='favicon.icns',
             bundle_identifier='com.andremeyer.sm64-randomizer')
