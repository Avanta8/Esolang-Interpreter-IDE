from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
from input_text import HighlighInputText
from output_text import OutputText
import interpreters


class CommandsWidget(QtWidgets.QWidget):

    button_pressed = QtCore.pyqtSignal()

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.main_visualiser = parent

        self.init_widgets()
        self._connect_signals()

        self.display_stopped()

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

        self.speed_slider.valueChanged.connect(self.main_visualiser.set_runspeed)
        self.speed_checkbox.stateChanged.connect(self.main_visualiser.set_runspeed)

    def pressed_run(self):
        self.button_pressed.emit()
        self.display_running()
        self.main_visualiser.command_run()

    def pressed_step(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_step()

    def pressed_stop(self):
        self.button_pressed.emit()
        self.display_stopped()
        self.main_visualiser.command_stop()

    def pressed_pause(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_pause()

    def pressed_back(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_back()

    def pressed_forwards(self):
        self.pressed_pause()
        steps = self._get_jump_steps()
        if steps is not None:
            self.main_visualiser.command_jump_forwards(steps)

    def pressed_backwards(self):
        self.pressed_pause()
        steps = self._get_jump_steps()
        if steps is not None:
            self.main_visualiser.command_jump_backwards(steps)

    def display_running(self):
        self._display_buttons(
            self.stop_button,
            self.pause_button,
        )

    def display_paused(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def display_stopped(self):
        self._display_buttons(
            self.run_button,
            self.step_button
        )

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

    def _get_jump_steps(self):
        try:
            return int(self.jump_input.text())
        except ValueError:
            self.main_visualiser.set_error('Invalid jump steps')
            return None


class IOWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

        self.error_text_active = True
        self.clear_error_text()

    def init_widgets(self):
        self._error_text_timer = QtCore.QTimer(self)
        self._error_text_timer.setSingleShot(True)
        self._error_text_timer.timeout.connect(self.clear_error_text)

        self.input_text = HighlighInputText(self)
        self.output_text = OutputText(self)
        self.error_text = QtWidgets.QLineEdit(self)

        self.error_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input:'))
        layout.addWidget(self.input_text)
        layout.addWidget(QtWidgets.QLabel('Output:'))
        layout.addWidget(self.output_text)
        layout.addWidget(self.error_text)
        self.setLayout(layout)

    def set_error_text(self, message):
        self._error_text_timer.stop()
        self.error_text.setText(message)
        self.error_text.show()
        self.error_text_active = True

    def timed_error_text(self, message, time=1000):
        self.set_error_text(message)
        self._error_text_timer.start(time)

    def clear_error_text(self):
        if not self.error_text_active:
            return
        self._error_text_timer.stop()
        self.error_text.clear()
        self.error_text.hide()
        self.error_text_active = False


class BaseVisualiserWidget(QtWidgets.QWidget):
    """This class should be subclassed."""

    _interpreter_type = None

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.main_visualiser = parent

        self._interpreter = None

        self.init_widgets()

    def init_widgets(self):
        # Should be overidden in a subclass
        pass

    def reset_visual(self):
        # Should be overidden in a subclass
        pass

    def configure_visual(self):
        """Method should be called after every step."""
        # Should be overidden in a subclass
        pass

    def display_visual(self):
        """Method should be called when the changes to the visualiser want
        to be displayed."""
        # Should be overidden in a subclass
        pass

    def restart_interpreter(self):
        """Initialise a new interpreter.
        Return whether it was successful.
        If successful, call `self.main_visualiser.visualiser_restarted`"""
        if self._interpreter_type is None:
            return False

        self.reset_visual()
        try:
            self._interpreter = self._interpreter_type(self.main_visualiser.get_code_text(),
                                                       input_func=self.main_visualiser.get_next_input,
                                                       undo_input_func=self.main_visualiser.undo_input,
                                                       output_func=self.main_visualiser.set_output)
        except interpreters.InterpreterError as error:
            self.handle_error(error)
            return False
        else:
            self.main_visualiser.visualiser_restarted()
            return True

    def step(self):
        """Step once.
        Return whether it was successful."""
        if self._interpreter is None:
            if not self.restart_interpreter():
                return False

        try:
            index, chars = self._interpreter.step()
        except interpreters.InterpreterError as error:
            self.handle_error(error)
            return False
        else:
            self.configure_visual()
            self.main_visualiser.set_current_position(index, chars)
            return True

    def back(self):
        """Step backwards.
        Return whether it was successful."""
        if self._interpreter is None:
            raise Exception(f'self._interpreter is None in {type(self)}.back. This shouldn\'t happen')
            return False

        try:
            index, chars = self._interpreter.back()
        except interpreters.InterpreterError as error:
            self.handle_error(error)
            return False
        else:
            self.configure_visual()
            self.main_visualiser.set_current_position(index, chars)
            return True

    def stop(self):
        """Delete the interpreter.
        Call `self.main_visualiser.visualiser_stopped`."""
        self._interpreter = None
        self.main_visualiser.visualiser_stopped()

    def handle_error(self, error):
        """Handle what should happen with `error`.
        Should call `self.main_visualiser.set_error` if the error is acted on."""
        message = None
        if isinstance(error, interpreters.ExecutionEndedError):
            message = 'Execution finished'
        elif isinstance(error, interpreters.NoPreviousExecutionError):
            message = 'No previous execution'
        elif isinstance(error, interpreters.NoInputError):
            message = 'Enter input'
        elif isinstance(error, interpreters.ProgramError):
            error_type = error.error
            if error_type is interpreters.ErrorTypes.UNMATCHED_OPEN_PAREN:
                message = 'Unmatched opening parentheses'
            elif error_type is interpreters.ErrorTypes.UNMATCHED_CLOSE_PAREN:
                message = 'Unmatched closing parentheses'
            elif error_type is interpreters.ErrorTypes.INVALID_TAPE_CELL:
                message = 'Tape pointer out of bounds'

        if message is None:
            raise error

        # Make this a signal instead?
        self.main_visualiser.set_error(message, error.location if isinstance(error, interpreters.ProgramError) else None)


class NoVisualiserWidget(BaseVisualiserWidget):
    pass


class BrainfuckVisualiserWidget(BaseVisualiserWidget):

    _interpreter_type = interpreters.BFInterpreter

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
        return len(self._tape) // self._columns + (1 if len(self._tape) % self._columns else 0)

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
        return self.createIndex(self._current_cell_index // self._columns,
                                self._current_cell_index % self._columns)


class MainVisualiser(QtWidgets.QWidget):
    """Main visualiser widget that contains each panel that displays widgets.
    Contols what happens when a button is pressed."""

    filetype_to_visualiser = {
        FileTypes.NONE: NoVisualiserWidget,
        FileTypes.BRAINFUCK: BrainfuckVisualiserWidget,
    }

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.editor_page = parent

        self.init_widgets()
        self.set_runspeed()

        self.visualiser_stopped()

    def init_widgets(self):
        self.run_timer = QtCore.QTimer(self)
        self.run_timer.timeout.connect(self.run_signal)

        self.visualiser_frame = NoVisualiserWidget(self)
        self.commands_frame = CommandsWidget(self)
        self.io_panel = IOWidget(self)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(self.visualiser_frame)
        self.splitter.addWidget(self.commands_frame)
        self.splitter.addWidget(self.io_panel)

        self.statusbar = QtWidgets.QStatusBar(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter, stretch=1)
        layout.addWidget(self.statusbar)
        self.setLayout(layout)

        self.commands_frame.button_pressed.connect(self.button_pressed)
        self.editor_page.code_text.key_during_visualisation.connect(self.key_during_visualisation)

    def set_filetype(self, filetype):
        visualiser_type = self.filetype_to_visualiser[filetype]
        if isinstance(self.visualiser_frame, visualiser_type):
            return

        # If the filetype is different, create a new visualiser
        # corresponding to `filetype`
        self.visualiser_frame.deleteLater()
        self.visualiser_frame = visualiser_type(self)
        self.splitter.insertWidget(0, self.visualiser_frame)

        self.io_panel.input_text.set_filetype(filetype)

    def set_current_position(self, position, chars):
        """Set the position in the `code_text` of the current command
        being executed.

        Arguments:
            - postition: index of start of command
            - chars: length of command in characters."""
        self._current_command_position = (position, chars)

    def highlight_current_position(self):
        """Highlight the current position in the code text."""
        self.editor_page.code_text.highlight_position(*self._current_command_position)

    def set_runspeed(self):
        """Method should be called whenever an option relating to runspeed is changed.
        Recalculate the runspeed."""
        if self.commands_frame.speed_checkbox.isChecked():
            runspeed = 10
            self.steps_skip = self.commands_frame.speed_slider.value() // 5
        else:
            value = self.commands_frame.speed_slider.value() + 1
            runspeed = int(1000 / (value * value * .0098 + 1))
            self.steps_skip = 0
        self.run_timer.setInterval(runspeed)

    def button_pressed(self):
        """Method should be called whenever a button is pressed.
        Remove all the error text."""
        self.io_panel.clear_error_text()
        self.editor_page.code_text.remove_errors()

    def command_step(self):
        """Step command"""
        self.visualiser_frame.step()
        self.visualiser_frame.display_visual()
        self.highlight_current_position()

    def command_run(self):
        """Run command"""
        self.run_timer.start()
        self.run_signal()

    def command_pause(self):
        """Pause command"""
        self.run_timer.stop()

    def command_stop(self):
        """Stop command"""
        self.run_timer.stop()
        self.visualiser_frame.stop()

    def command_back(self):
        """Back command"""
        self.visualiser_frame.back()
        self.visualiser_frame.display_visual()
        self.highlight_current_position()

    def command_jump_forwards(self, steps):
        """Jump forwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.visualiser_frame.step():
                succesful = False
                break
        else:
            succesful = True
        self.visualiser_frame.display_visual()
        self.highlight_current_position()
        return succesful

    def command_jump_backwards(self, steps):
        """Jump backwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.visualiser_frame.back():
                succesful = False
                break
        else:
            succesful = True
        self.visualiser_frame.display_visual()
        self.highlight_current_position()
        return succesful

    def run_signal(self):
        """Method called from `self.run_timer` timout."""
        success = self.command_jump_forwards(self.steps_skip + 1)
        if not success:
            self.commands_frame.display_paused()
            self.command_pause()

    def visualiser_restarted(self):
        """Method should be called whenever a new interpreter is started."""
        self.editor_page.code_text.visualisation_started()
        self.statusbar.showMessage('During execution')

    def visualiser_stopped(self):
        """Method should be called whenever a new interpreter is destroyed."""
        self.editor_page.code_text.visualisation_stopped()
        self.statusbar.showMessage('Visualiser not currently active')
        self.io_panel.input_text.restart()

    def set_error(self, message, location=None):
        """Set an error message `message`.
        If `location` is given, highlight it in the code text.
        `location` should be a tuple (start_position, no_of_chars)"""
        self.io_panel.set_error_text(message)
        if location is not None:
            self.editor_page.code_text.highlight_error(*location)

    def key_during_visualisation(self):
        """Key pressed in code text while intepreter is active."""
        self.io_panel.timed_error_text('Please stop visualiser before editing text')

    def get_code_text(self):
        return self.editor_page.get_text()

    def get_next_input(self):
        return self.io_panel.input_text.next_()

    def undo_input(self):
        self.io_panel.input_text.prev()

    def set_output(self, output):
        self.io_panel.output_text.set_text(output)

    def closed(self):
        """Method called when the visualiser containing `self` is closed."""
        self.commands_frame.display_paused()
        self.command_stop()
