import enum

from esolang_IDE.code_runner import CodeRunner, RunnerThread
from esolang_IDE.code_text import CodeText
from esolang_IDE.constants import FileTypes
import esolang_IDE.interpreters as interpreters


class _RunnerStatus(enum.Enum):
    running = enum.auto()
    stopped = enum.auto()
    paused = enum.auto()

    def to_message(self):
        return {
            _RunnerStatus.running: 'Running',
            _RunnerStatus.stopped: 'Stopped',
            _RunnerStatus.paused: 'Paused',
        }[self]


class RunnerController:

    def __init__(self, code_text: CodeText, code_runner: CodeRunner):

        self._code_text = code_text
        self._code_runner = code_runner

        self._runner_thread = RunnerThread(
            code_func=self._code_text.text,
            input_func=self._input_text.next_,
            output_func=self._output_text.buffer_text,
        )

        self._connect_signals()

        self._status = _RunnerStatus.stopped

    def _connect_signals(self):
        self._runner_thread.started.connect(self._runner_started)
        self._runner_thread.paused.connect(self._runner_paused)
        self._runner_thread.stopped.connect(self._runner_stopped)
        self._runner_thread.continued.connect(self._runner_continued)
        self._runner_thread.interrupted.connect(self._runner_interrupted)
        self._runner_thread.error.connect(self._runner_error)

        self._output_text.interrupt.connect(self.interrupt)
        self._output_text.completed.connect(self._output_completed)

    def _runner_started(self):
        self._input_text.restart()  # May not be necessary here
        self._output_text.clear()
        self._runner_continued()

    def _runner_paused(self):
        self._status = _RunnerStatus.paused
        self._output_text.stop()

    def _runner_stopped(self):
        self._status = _RunnerStatus.stopped
        self._output_text.stop()

    def _runner_continued(self):
        self._status = _RunnerStatus.running
        self._output_text.continue_()
        self._code_runner.set_status_message(self._status.to_message())
        self._code_runner.clear_error_message()
        self._error_message = ''

    def _runner_interrupted(self):
        self._status = _RunnerStatus.stopped
        self._output_text.stop_immediate()

    def _runner_error(self, error):
        if isinstance(error, interpreters.NoInputError):
            self._runner_thread.pause()
        else:
            self._runner_thread.stop()

        message = ''
        if isinstance(error, interpreters.NoInputError):
            message = 'Enter Input'
        elif isinstance(error, interpreters.ProgramError):
            error_type = error.error
            if error_type is interpreters.ErrorTypes.UNMATCHED_OPEN_PAREN:
                message = 'Unmatched opening parentheses'
            elif error_type is interpreters.ErrorTypes.UNMATCHED_CLOSE_PAREN:
                message = 'Unmatched closing parentheses'
            elif error_type is interpreters.ErrorTypes.INVALID_TAPE_CELL:
                message = 'Tape pointer out of bounds'
            if error.location:
                message = f'{message} at location {error.location}'

        self._error_message = message

    def _output_completed(self):
        if self._error_message:
            self._code_runner.set_error_message(self._error_message)
        self._code_runner.set_status_message(self._status.to_message())
        if self._status is _RunnerStatus.stopped:
            self._input_text.restart()

    def run_code(self):
        self._runner_thread.run_called()

    def set_filetype(self, filetype: FileTypes):
        self._runner_thread.set_interpreter_type(filetype.to_runner_interpreter())
        self._input_text.set_decoder(filetype.to_input_decoder())

    def interrupt(self):
        self._runner_thread.interrupt()

    def get_code_runner(self):
        return self._code_runner

    @property
    def _input_text(self):
        return self._code_runner.get_input_text()

    @property
    def _output_text(self):
        return self._code_runner.get_output_text()
