# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys
import logging


from PySide.QtGui import QMainWindow, QAction, QMenu, QSystemTrayIcon,\
    QApplication, QIcon, QDesktopServices, QMessageBox
from PySide.QtCore import QThread, QUrl

from trayshell.shell_base import ShellBase
from trayshell.utils import resource_path
import tornado

from app import main as webmain

_logger = logging.getLogger(__name__)


class MyWorkerThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        print('thread running')
        webmain()


class MainWnd(QMainWindow):
    def __init__(self, shell, icon):
        super(MainWnd, self).__init__()
        self._shell = shell
        self.icon = icon
        self.context_menu = None
        self.tray_icon = None
        self.myProcess = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            msg = "I couldn't detect any system tray on this system."
            _logger.error(msg)
            QMessageBox.critical(None, "Listen 1", msg)
            sys.exit(1)

        self.init_ui()

    def init_ui(self):
        self.setWindowIcon(self.icon)
        self.setWindowTitle('Listen 1')

        self.create_tray_icon(self.icon)
        self.tray_icon.show()
        self.on_start()

    def on_tray_activated(self, reason=None):
        _logger.debug("Tray icon activated.")

    def on_start(self):
        self.myProcess = MyWorkerThread()
        self.myProcess.start()

        QDesktopServices.openUrl('http://localhost:8888/')

    def on_open(self):
        if sys.platform.startswith('darwin'):
            url = '/Applications/Listen 1.app/Contents/MacOS/media/music/'
            QDesktopServices.openUrl(QUrl.fromLocalFile(url))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile('./media/music'))

    def on_quit(self):
        if self.myProcess is not None:
            # graceful shutdown web server
            tornado.ioloop.IOLoop.instance().stop()
        self._shell.quit_app()

    def create_actions(self):
        """ Creates QAction object for binding event handlers.
        """
        self.start_action = QAction(
            "&打开 Listen 1", self, triggered=self.on_start)
        self.open_action = QAction(
            "&离线音乐文件夹", self, triggered=self.on_open)
        self.quit_action = QAction(
            "&退出", self, triggered=self.on_quit)

    def create_context_menu(self):
        menu = QMenu(self)
        menu.addAction(self.start_action)
        menu.addAction(self.open_action)
        menu.addAction(self.quit_action)
        return menu

    def create_tray_icon(self, icon):
        self.create_actions()
        self.context_menu = self.create_context_menu()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setContextMenu(self.context_menu)
        self.tray_icon.setIcon(icon)
        self.tray_icon.activated.connect(self.on_tray_activated)


class Shell(ShellBase):
    """ Shell implementation using PySide
    """

    def __init__(self):
        super(Shell, self).__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 1
        self.icon = QIcon(resource_path('res/icon.png'))
        self.menu = None
        self.wnd = MainWnd(self, self.icon)

    def quit_app(self):
        self.app.quit()

    def run(self):
        _logger.info("Shell is running...")
        self.app.exec_()


if __name__ == '__main__':
    shell = Shell()
    shell.run()
