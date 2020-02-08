import collections

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
from input_text import StandardInputText
import interpreters


class RunnerThread(QtCore.QThread):

    def __init__(self, parent):
        super().__init__(parent)

        self.view = parent

        self.interpreter_type = None
        self._interpreter = None

    def run(self):
        self._running = True
        try:
            while self._running:
                self._interpreter.step()
        except interpreters.InterpreterError as error:
            self.handle_error(error)

    def stop(self):
        self._running = False

    def run_called(self):
        """Called whenever the code runner is run by the user.
        Do nothing if currently running. Otherwise, if `self` was paused by waiting for input,
        then continue. If not, create a new interpreter."""
        if self.isRunning():
            return
        if self._interpreter is None:
            self._start_interpreter()
        self.start()

    def _start_interpreter(self):
        if self.interpreter_type is None:
            return
        self._interpreter = self.interpreter_type(self.view.get_code_text(),
                                                  input_func=input,
                                                  output_func=self.view.buffer_output)
        self.view.runner_started()

    def handle_error(self, error):
        if isinstance(error, interpreters.NoInputError):
            self.view.runner_paused()
        else:
            self.view.runner_stopped()

    def set_interpreter_type(self, interpreter_type):
        if interpreter_type is self.interpreter_type:
            return
        self.interpreter_type = interpreter_type
        self.stop()


class CodeRunner(QtWidgets.QWidget):
    INTERPRETER_TYPES = {
        FileTypes.NONE: None,
        FileTypes.BRAINFUCK: interpreters.FastBrainfuckInterpreter,
    }

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.editor_page = parent

        self._output_buffer = collections.deque()

        self.init_widgets()

    def init_widgets(self):

        self.runner = RunnerThread(self)

        self.input_text = StandardInputText(self)

        self.output_text = QtWidgets.QPlainTextEdit(self)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setFamily('Source Code Pro')
        self.output_text.setFont(font)
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumBlockCount(1000)
        self.output_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.output_text)
        splitter.addWidget(self.input_text)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.buffer_timer = QtCore.QTimer(self)
        self.buffer_timer.timeout.connect(self.add_from_buffer)
        self.buffer_timer.setInterval(10)

    def set_filetype(self, filetype):
        self.input_text.set_filetype(filetype)
        self.runner.set_interpreter_type(self.INTERPRETER_TYPES[filetype])

    def run_code(self):
        self.runner.run_called()

    def runner_started(self):
        """Method should be called from `self.runner` whenever it is started."""
        self.running = True
        self.buffer_timer.start()

    def runner_stopped(self):
        """Method should be called from `self.runner` whenever it is stopped."""
        self.running = False

    def runner_paused(self):
        """Method should be called from `self.runner` whenever it is paused."""

    def get_code_text(self):
        return self.editor_page.get_text()

    def add_output(self, text):
        self.output_text.moveCursor(QtGui.QTextCursor.End)
        self.output_text.insertPlainText(text)
        self.output_text.ensureCursorVisible()

    def buffer_output(self, text):
        self._output_buffer.appendleft(text)

    def add_from_buffer(self):
        if self._output_buffer:
            length = min(100, len(self._output_buffer))
            text = ''.join(self._output_buffer.pop() for _ in range(length))
            self.add_output(text)
        else:
            if not self.running:
                self.buffer_timer.stop()
                self.output_text.appendPlainText('Finished.')
