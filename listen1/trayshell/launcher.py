# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from PySide.QtGui import *
from PySide.QtCore import *

from trayshell.shell_pyside import Shell
from multiprocessing import freeze_support

def main():
    shell = Shell()
    shell.run()

if __name__ == '__main__':
    freeze_support()
    main()
