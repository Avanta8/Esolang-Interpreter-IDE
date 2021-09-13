from PyQt5 import QtWidgets

import main_window


def main():
    app = QtWidgets.QApplication([])
    _ = main_window.IDE()
    app.exec_()


if __name__ == "__main__":
    main()