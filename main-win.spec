# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

import os
libFolder = os.environ["pythonLocation"]+"\\lib" if "pythonLocation" in os.environ else "Lib"
print("LibFolder: \"" + libFolder + "\"")


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Administrator\\Desktop\\sm64-randomizer'],
             binaries=collect_dynamic_libs("rtree"),
             datas=[('README.md', '.'), ('LICENSE', '.'), ('Data', '.'), ('Assets', '.'), ('Config', '.'), (libFolder+'\\site-packages\\trimesh\\resources', 'trimesh\\resources\\')],
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
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='web\\favicon.ico')
