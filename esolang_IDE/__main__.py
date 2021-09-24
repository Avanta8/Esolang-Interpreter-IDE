from PyQt5 import QtWidgets

from esolang_IDE.main_window import IDE


def main():
    app = QtWidgets.QApplication([])
    _ = IDE()
    app.exec_()


if __name__ == "__main__":
    main()
