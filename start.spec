# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
         ( 'C:/Users/bronkscottema/Desktop/Development/Audible_Analytics/images/*.png', 'images' ),
         ( 'C:/Users/bronkscottema/Desktop/Development/Audible_Analytics/styles/*/*', 'styles' ),
         ( 'C:/Users/bronkscottema/Desktop/Development/Audible_Analytics/fonts/*', 'fonts' ),
         ]

a = Analysis(['C:\\Users\\bronkscottema\\Desktop\\Development\\Audible_Analytics\\start.py'],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [('proxima.ttf', 'fonts/proxima.ttf', 'DATA')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='start',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
