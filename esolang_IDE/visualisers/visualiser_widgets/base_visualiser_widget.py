from PyQt5 import QtCore, QtWidgets

import interpreters


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
            self._interpreter = self._interpreter_type(
                self.main_visualiser.get_code_text(),
                input_func=self.main_visualiser.get_next_input,
                undo_input_func=self.main_visualiser.undo_input,
                output_func=self.main_visualiser.set_output,
            )
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
            raise Exception(
                f'self._interpreter is None in {type(self)}.back. This shouldn\'t happen'
            )
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
        self.main_visualiser.set_error(
            message,
            error.location if isinstance(error, interpreters.ProgramError) else None,
        )


class NoVisualiserWidget(BaseVisualiserWidget):
    pass
