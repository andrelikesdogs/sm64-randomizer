# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Administrator\\Desktop\\sm64-randomizer'],
             binaries=[('Lib/site-packages/rtree/spatialindex*', '.')],
             datas=[('README.md', '.'), ('LICENSE', '.'), ('Data', '.'), ('Lib/site-packages/trimesh/resources', 'trimesh/resources/')],
             hiddenimports=[],
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
