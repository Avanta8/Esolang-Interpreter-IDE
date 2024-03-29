from typing import Type

from PyQt5 import QtCore, QtGui, QtWidgets

from esolang_IDE.input_text import StandardInputText, HighlightInputText
from esolang_IDE.output_text import RunnerOutputText
import esolang_IDE.interpreters as interpreters


class RunnerThread(QtCore.QThread):

    started = QtCore.pyqtSignal()
    paused = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal()
    continued = QtCore.pyqtSignal()
    interrupted = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(Exception)

    _want_to_start = QtCore.pyqtSignal()

    _NO_INTERRUPT = 0
    _RESTART_INTERRUPT = 1
    _STOP_INTERRUPT = 2  # Stop interrupt is not currently used
    _INTERRUPT_INTERRUPT = 3

    def __init__(self, code_func, input_func, output_func):
        super().__init__()

        self._code_func = code_func
        self._input_func = input_func
        self._output_func = output_func

        self.interpreter_type = None
        self._interpreter = None
        self._run_call_interrupt = False

        self._want_to_start.connect(self.run_called)

    def run(self):
        self._interpreter_running = True
        try:
            while self._interpreter_running:
                if self._run_call_interrupt:
                    self._handle_interrupt()
                else:
                    self._interpreter.step()
        except interpreters.InterpreterError as error:
            self.error.emit(error)

    def _handle_interrupt(self):
        self._interpreter_running = False
        self._interpreter = None
        if self._run_call_interrupt == self._STOP_INTERRUPT:
            self.stopped.emit()
        elif self._run_call_interrupt == self._RESTART_INTERRUPT:
            self.stopped.emit()
            self._want_to_start.emit()
        elif self._run_call_interrupt == self._INTERRUPT_INTERRUPT:
            self.interrupted.emit()
        self._run_call_interrupt = self._NO_INTERRUPT

    def stop(self):
        self._interpreter_running = False
        self._interpreter = None
        self.stopped.emit()

    def pause(self):
        self._interpreter_running = False
        self.paused.emit()

    def run_called(self):
        """Called whenever the code runner is run by the user.
        Set the `_run_call_interrupt` flag if currently running. Otherwise, start self, and
        if there is no current interpreter, create a new interpreter."""
        if self.isRunning():
            self._run_call_interrupt = self._RESTART_INTERRUPT
        elif self._interpreter is None:
            self._start_interpreter()
        else:
            self.start()
            self.continued.emit()

    def interrupt(self):
        if self.isRunning():
            self._run_call_interrupt = self._INTERRUPT_INTERRUPT

    def _start_interpreter(self):
        if self.interpreter_type is None:
            return
        self.started.emit()
        try:
            self._interpreter = self.interpreter_type(
                self._code_func(),
                input_func=self._input_func,
                output_func=self._output_func,
            )
        except interpreters.ProgramSyntaxError as error:
            self.error.emit(error)
        else:
            self.start()

    def set_interpreter_type(self, interpreter_type: Type[interpreters.BaseInterpreter]):
        if interpreter_type is self.interpreter_type:
            return
        self.interpreter_type = interpreter_type
        self.interrupt()


class CodeRunner(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):

        self._input_text = StandardInputText()
        self._output_text = RunnerOutputText()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self._output_text)
        splitter.addWidget(self._input_text)

        self._error_text = QtWidgets.QLineEdit(self)
        self._error_text.setReadOnly(True)

        self._statusbar = QtWidgets.QStatusBar(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(splitter, stretch=1)
        layout.addWidget(self._error_text)
        layout.addWidget(self._statusbar)
        self.setLayout(layout)

    def set_error_message(self, message):
        self._error_text.setText(message)
        self._error_text.show()

    def clear_error_message(self):
        self._error_text.hide()

    def set_status_message(self, text):
        self._statusbar.showMessage(text)

    def get_input_text(self):
        return self._input_text

    def get_output_text(self):
        return self._output_text
