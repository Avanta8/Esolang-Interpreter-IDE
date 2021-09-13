from PyQt5 import QtCore, QtWidgets, QtGui

from visualisers.visualiser_widgets.base_visualiser_widget import BaseVisualiserWidget

import interpreters


class BrainfuckVisualiserWidget(BaseVisualiserWidget):

    _interpreter_type = interpreters.BrainfuckInterpreter

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

    def init_widgets(self):

        self.table = BrainfuckTable(self, min_column_width=40, column_counts=(20, 10, 5))
        self.table_model = BrainfuckTableModel()
        self.table.setModel(self.table_model)
        self.table.size_changed.connect(self.table_model.set_columns)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def reset_visual(self):
        self.table_model.reset()

    def configure_visual(self):
        self.table_model.set_tape(self._interpreter)

    def display_visual(self):
        self.table_model.display_changes()
        self.table.scrollTo(self.table_model.get_current_index())


class BrainfuckTable(QtWidgets.QTableView):
    """Table that displays the tape.
    Emit `size_changed` when the table is resized."""

    size_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, min_column_width=50, column_counts=()):
        super().__init__(parent=parent)

        self.min_column_width = min_column_width
        self.column_counts = sorted(column_counts, reverse=True)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.setSelectionMode(QtWidgets.QTableView.NoSelection)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        columns = self._get_columns(event.size().width())
        self.size_changed.emit(columns)

    def _get_columns(self, width):
        """Return the maximum number of columns that fit in `width`."""
        for column_count in self.column_counts:
            if width / column_count >= self.min_column_width:
                return column_count

        # Return this if there is not a specified number of columns
        # or if the table was too small to fit the smallest valid number of columns
        # but we must have at least one column
        return width // self.min_column_width or 1


class BrainfuckTableModel(QtCore.QAbstractTableModel):
    """AbstractTableModel for BrainfuckTable"""

    _current_cell_brush = QtGui.QBrush(QtGui.QColor('red'))

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._columns = 5

        self.reset()

    def rowCount(self, parent):
        """Return the number of rows."""
        return len(self._tape) // self._columns + (
            1 if len(self._tape) % self._columns else 0
        )

    def columnCount(self, parent):
        """Return the number of columns."""
        return self._columns

    def data(self, index, role):
        """If `role` is `DisplayRole`, then return value of the cell at `index`.
        If `role` is `BackgroundRole`, then return a coloured background if `index`
        if the current cell."""
        cell_index = index.row() * self._columns + index.column()
        if role == QtCore.Qt.DisplayRole:
            if 0 <= cell_index < len(self._tape):
                return self._tape[cell_index]
        elif role == QtCore.Qt.BackgroundRole:
            if cell_index == self._current_cell_index:
                return self._current_cell_brush
        return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        """"""
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return section
            else:
                return section * self._columns
        return QtCore.QVariant()

    def reset(self):
        """Reset data."""
        self._tape = [0] * 20
        self._current_cell_index = -1

    def set_tape(self, interpreter):
        """`interpreter` should be a BFInterpreter.
        Set the current data according to the data of the interpreter."""
        self._tape = interpreter.tape
        self._current_cell_index = interpreter.tape_pointer

    def display_changes(self):
        """Method called when changed to layout should be displayed."""
        self.layoutChanged.emit()

        # TODO:
        #   Store the specific changes whenever `set_tape` is called, then
        #   emit dataChanged instead: https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html?highlight=qabstractitemmodel#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.dataChanged
        #   This may make it more efficient

    def set_columns(self, columns):
        """Set the number of columns.
        If the number of columns changed, then emit `self.layoutChanged`."""
        if columns == self._columns:
            return

        self._columns = columns
        self.layoutChanged.emit()

    def get_current_index(self):
        """Return a QModelIndex of the current cell."""
        return self.createIndex(
            self._current_cell_index // self._columns,
            self._current_cell_index % self._columns,
        )
