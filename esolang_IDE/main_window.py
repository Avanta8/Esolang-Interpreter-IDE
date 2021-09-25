from typing import Optional
from PyQt5 import QtWidgets

# Look at: https://doc.qt.io/qtforpython/overviews/model-view-programming.html#using-views-with-an-existing-model
# for file system view


class IDE(QtWidgets.QMainWindow):
    def __init__(self, *args, menu_layout: Optional[dict[str, tuple[tuple]]] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.statusBar()

        if menu_layout:
            self.init_menubar(menu_layout)

    def init_menubar(self, menus: dict[str, tuple[tuple]]):

        menubar = self.menuBar()
        for name, actions in menus.items():
            menu = menubar.addMenu(name)
            for action, shortcut, statustip, connect in actions:
                action = QtWidgets.QAction(action, self)
                action.setShortcut(shortcut)
                action.setStatusTip(statustip)
                action.triggered.connect(connect)

                menu.addAction(action)
