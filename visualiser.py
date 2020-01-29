from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
import interpreters


class CommandsWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()
        self._connect_signals()

        self.pressed_stop()

    def init_widgets(self):
        buttons = self._create_buttons()
        speed = self._create_speed()
        jump = self._create_jump()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttons)
        layout.addWidget(speed)
        layout.addWidget(jump)
        self.setLayout(layout)

    def _create_buttons(self):
        self.run_button = QtWidgets.QPushButton('Run')
        self.continue_button = QtWidgets.QPushButton('Continue')
        self.step_button = QtWidgets.QPushButton('Step')
        self.pause_button = QtWidgets.QPushButton('Pause')
        self.back_button = QtWidgets.QPushButton('Back')
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.buttons = {self.run_button, self.step_button,
                        self.pause_button, self.back_button,
                        self.stop_button, self.continue_button}

        self.button_layout = QtWidgets.QGridLayout()
        self.button_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        # self.button_layout.setColumnStretch(0, 1)
        # self.button_layout.setColumnStretch(1, 1)

        groupbox = QtWidgets.QGroupBox('Commands:')
        groupbox.setLayout(self.button_layout)
        return groupbox

    def _create_jump(self):
        jump_label = QtWidgets.QLabel('Steps:')
        self.jump_input = QtWidgets.QLineEdit()
        self.forwards_button = QtWidgets.QPushButton('Forward')
        self.backwards_button = QtWidgets.QPushButton('Backwards')

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(jump_label)
        top_layout.addWidget(self.jump_input)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.backwards_button)
        bottom_layout.addWidget(self.forwards_button)

        jump_layout = QtWidgets.QVBoxLayout()
        jump_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        jump_layout.addLayout(top_layout)
        jump_layout.addLayout(bottom_layout)

        groupbox = QtWidgets.QGroupBox('Jump:')
        groupbox.setLayout(jump_layout)
        return groupbox

    def _create_speed(self):
        # QSlider defaults to a range of 0 - 99 inclusive
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_checkbox = QtWidgets.QCheckBox('Faster')

        speed_layout = QtWidgets.QVBoxLayout()
        speed_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_checkbox)

        groupbox = QtWidgets.QGroupBox('Runspeed:')
        groupbox.setLayout(speed_layout)
        return groupbox

    def _connect_signals(self):
        self.run_button.clicked.connect(self.pressed_run)
        self.continue_button.clicked.connect(self.pressed_run)
        self.step_button.clicked.connect(self.pressed_step)
        self.pause_button.clicked.connect(self.pressed_pause)
        self.back_button.clicked.connect(self.pressed_back)
        self.stop_button.clicked.connect(self.pressed_stop)
        self.forwards_button.clicked.connect(self.pressed_forwards)
        self.backwards_button.clicked.connect(self.pressed_backwards)

    def pressed_run(self):
        self._display_buttons(
            self.stop_button,
            self.pause_button,
        )

    def pressed_step(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )
        self.parent().command_step()

    def pressed_stop(self):
        self._display_buttons(
            self.run_button,
            self.step_button
        )

    def pressed_pause(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def pressed_back(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def pressed_forwards(self):
        pass

    def pressed_backwards(self):
        pass

    def _display_buttons(self, a=None, b=None, c=None, d=None):
        self._clear_buttons()
        for i, button in enumerate((a, b, c, d)):
            if button is not None:
                self.button_layout.addWidget(button, i // 2, i % 2)
                button.show()

    def _clear_buttons(self):
        """Remove all buttons."""
        for button in self.buttons:
            if button.isVisible():
                self.button_layout.removeWidget(button)
                button.hide()


class IOWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):
        self.input_text = QtWidgets.QPlainTextEdit(self)
        self.output_text = QtWidgets.QPlainTextEdit(self)
        self.error_text = QtWidgets.QLineEdit(self)

        self.input_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.output_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.output_text.setReadOnly(True)
        self.error_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input:'))
        layout.addWidget(self.input_text)
        layout.addWidget(QtWidgets.QLabel('Output:'))
        layout.addWidget(self.output_text)
        layout.addWidget(self.error_text)
        self.setLayout(layout)


class BaseVisualiserWidget(QtWidgets.QWidget):

    _interpreter_type = None

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.main_visualiser = parent

        self._interpreter = None

        self.init_widgets()

    def init_widgets(self):
        pass

    def reset_visual(self):
        pass

    def configure_visual(self):
        pass

    def restart_interpreter(self):
        if self._interpreter_type is None:
            return False

        self.reset_visual()
        try:
            self._interpreter = self._interpreter_type(self.main_visualiser.get_code_text(),
                                                       input_func=self.main_visualiser.get_next_input,
                                                       undo_input_func=self.main_visualiser.undo_input,
                                                       output_func=self.main_visualiser.set_output)
        except interpreters.ProgramError as error:
            return False
        else:
            return True

    def step(self):
        if self._interpreter is None:
            if not self.restart_interpreter():
                return

        try:
            ret = self._interpreter.step()
        except interpreters.InterpreterError as error:
            return
        else:
            self.configure_visual()


class NoVisualiserWidget(BaseVisualiserWidget):
    pass


class BrainfuckVisualiserWidget(BaseVisualiserWidget):

    _interpreter_type = interpreters.BFInterpreter

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

    def init_widgets(self):

        self.table = QtWidgets.QTableView(self)
        self.table_model = BrainfuckTableModel()
        self.table.setModel(self.table_model)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def reset_visual(self):
        self.table_model.reset()

    def configure_visual(self):
        self.table_model.set_tape(self._interpreter)


class BrainfuckTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._columns = 5

        self.reset()

    def rowCount(self, parent):
        return len(self._tape) // self._columns + 1

    def columnCount(self, parent):
        return self._columns

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            cell_index = index.row() * self._columns + index.column()
            return self._tape[cell_index] if 0 <= cell_index < len(self._tape) else QtCore.QVariant()
        return QtCore.QVariant()

    def reset(self):
        self._tape = [0] * 20

    def set_tape(self, interpreter):
        self._tape = interpreter.tape
        self.layoutChanged.emit()


class MainVisualiser(QtWidgets.QSplitter):

    filetype_to_visualiser = {
        FileTypes.NONE: NoVisualiserWidget,
        FileTypes.BRAINFUCK: BrainfuckVisualiserWidget,
    }

    def __init__(self, parent, orientation=None):
        if orientation is None:
            super().__init__(parent)
        else:
            super().__init__(orientation, parent)

        self.editor_page = parent

        self.init_widgets()

    def init_widgets(self):
        self.visualiser_frame = NoVisualiserWidget(self)
        self.commands_frame = CommandsWidget(self)
        self.io_panel = IOWidget(self)

        self.addWidget(self.visualiser_frame)
        self.addWidget(self.commands_frame)
        self.addWidget(self.io_panel)

    def set_filetype(self, filetype):
        visualiser_type = self.filetype_to_visualiser[filetype]
        if isinstance(self.visualiser_frame, visualiser_type):
            return

        self.visualiser_frame.deleteLater()
        self.visualiser_frame = visualiser_type(self)
        self.insertWidget(0, self.visualiser_frame)

    def command_step(self):
        self.visualiser_frame.step()

    def get_code_text(self):
        return self.editor_page.get_text()

    def get_next_input(self):
        pass

    def undo_input(self):
        pass

    def set_output(self, output):
        print(output)
