from PyQt5 import QtWidgets

from controllers import IOController


def main():
    app = QtWidgets.QApplication([])
    m = IOController()
    m.ide.show()
    app.exec_()


if __name__ == "__main__":
    main()
