import collections

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
from input_text import StandardInputText
import interpreters


class RunnerThread(QtCore.QThread):

    started = QtCore.pyqtSignal()
    paused = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal()
    continued = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.view = parent

        self.interpreter_type = None
        self._interpreter = None
        self._run_call_interrupt = False

    def run(self):
        self._interpreter_running = True
        try:
            while self._interpreter_running:
                if self._run_call_interrupt:
                    self._run_call_interrupt = False
                    self.stop()
                    self._start_interpreter()
                    self._interpreter_running = True
                self._interpreter.step()
        except interpreters.InterpreterError as error:
            self.handle_error(error)

    def stop(self):
        self._interpreter_running = False
        self._interpreter = None
        self.stopped.emit()

    def run_called(self):
        """Called whenever the code runner is run by the user.
        Set the `_run_call_interrupt` flag if currently running. Otherwise, start self, and
        if there is no current interpreter, create a new interpreter."""
        if self.isRunning():
            self._run_call_interrupt = True
        else:
            if self._interpreter is None:
                self._start_interpreter()
            else:
                self.continued.emit()
            self.start()

    def _start_interpreter(self):
        if self.interpreter_type is None:
            return
        self._interpreter = self.interpreter_type(self.view.get_code_text(),
                                                  input_func=self.view.get_next_input,
                                                  output_func=self.view.buffer_output)
        self.started.emit()

    def handle_error(self, error):
        if isinstance(error, interpreters.NoInputError):
            self._interpreter_running = False
            self.paused.emit()
        else:
            self.stop()

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
        self.runner.started.connect(self.runner_started)
        self.runner.paused.connect(self.runner_paused)
        self.runner.stopped.connect(self.runner_stopped)
        self.runner.continued.connect(self.runner_continued)

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
        """Method should be called from `RunnerThread` whenever it is started."""
        self.running = True
        self.finished = False
        self.output_text.clear()
        self._output_buffer.clear()
        self.buffer_timer.start()

    def runner_stopped(self):
        """Method should be called from `RunnerThread` whenever it is stopped."""
        self.running = False
        self.finished = True
        self.input_text.restart()

    def runner_paused(self):
        """Method should be called from `RunnerThread` whenever it is paused."""
        self.running = False

    def runner_continued(self):
        """Method should be called from `RunnerThread` whenever it is continued."""
        self.running = True
        self.buffer_timer.start()

    def get_code_text(self):
        return self.editor_page.get_text()

    def get_next_input(self):
        return self.input_text.next_()

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
                if self.finished:
                    self.output_text.appendPlainText('Finished.')
