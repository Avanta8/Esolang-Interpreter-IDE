from PyQt5 import QtCore, QtGui, QtWidgets

from controllers import IOController

# Look at: https://doc.qt.io/qtforpython/overviews/model-view-programming.html#using-views-with-an-existing-model
# for file system view


class IDE(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

        self.show()

    def init_widgets(self):
        self.controller = IOController(self)
        self.setGeometry(300, 200, 1280, 720)

        menus = {
            'File': (
                (
                    ('New', self),
                    ('Ctrl+N',),
                    ('New file',),
                    (self.controller.file_new,),
                ),
                (
                    ('Open', self),
                    ('Ctrl+O',),
                    ('Open file',),
                    (self.controller.file_open,),
                ),
                (
                    ('Save', self),
                    ('Ctrl+S',),
                    ('Save file',),
                    (self.controller.file_save,),
                ),
                (
                    ('Save As', self),
                    ('Ctrl+Shift+S',),
                    ('Save as',),
                    (self.controller.file_saveas,),
                ),
            ),
            'Run': (
                (
                    ('Run code', self),
                    ('Ctrl+B',),
                    ('Run code',),
                    (self.controller.run_code,),
                ),
                (
                    ('Open visualiser', self),
                    ('Ctrl+Shift+B',),
                    ('Visualise run code',),
                    (self.controller.open_visualier,),
                ),
            ),
        }

        menubar = self.menuBar()
        for name, actions in menus.items():
            menu = menubar.addMenu(name)
            for action, shortcut, statustip, connect in actions:
                action = QtWidgets.QAction(*action)
                action.setShortcut(*shortcut)
                action.setStatusTip(*statustip)
                action.triggered.connect(*connect)
                menu.addAction(action)

        self.statusBar()


        self.setCentralWidget(self.controller.get_main_widget())
