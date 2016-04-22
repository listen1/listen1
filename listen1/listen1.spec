# -*- mode: python -*-
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

app_name = 'Listen 1'
exe_name = 'Listen 1'

res_path = os.path.join('.', 'res')

if sys.platform == 'win32':
    exe_name = exe_name + '.exe'
    run_upx = False

elif sys.platform.startswith('linux'):
    run_strip = True
    run_upx = False

elif sys.platform.startswith('darwin'):
    run_upx = True

else:
    print("Unsupported operating system")
    sys.exit(-1)

added_files = [
    ('media', 'media'),
    ('templates', 'templates')
]

a = Analysis(['trayshell/launcher.py'],
             datas=added_files,
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=exe_name,
          debug=False,
          strip=None,
          upx=True,
          icon= os.path.join(res_path, 'icon.ico'),
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               Tree(res_path, 'res', excludes=['*.pyc']),

               a.datas,
               strip=None,
               upx=run_upx,
               name=app_name)

if sys.platform.startswith('darwin'):
    app = BUNDLE(coll,
                name='Listen 1.app',
                appname=exe_name,
                icon=os.path.join(res_path, 'icon.icns'))