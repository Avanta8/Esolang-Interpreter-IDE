import enum


class ErrorTypes(enum.Enum):
    UNMATCHED_CLOSE_PAREN = enum.auto()
    UNMATCHED_OPEN_PAREN = enum.auto()
    INVALID_TAPE_CELL = enum.auto()


class InterpreterError(Exception):
    """Base class for exceptions to do with an interpreter.

    Attributes:
        message -- Optional message describing error"""

    def __init__(self, message=None):
        self.message = message


class ExecutionEndedError(InterpreterError):
    """Error raised when program has ended but `Interpreter.step` is still called"""


class NoPreviousExecutionError(InterpreterError):
    """Error raised when `Interpreter.back` is called but it is the first instruction being processed"""


class NoInputError(InterpreterError):
    """Error raised when no input returned from `Interpreter.input_func`"""


class ProgramError(InterpreterError):
    """Error raised when there is something wrong with a program.

    Attributes:
        error -- Source of error (default to None).
        location -- Location of error (default to None).
        message -- Optional mesage (default to None)."""

    def __init__(self, error=None, location=None, message=None):
        super().__init__(message)
        self.error = error
        self.location = location


class ProgramSyntaxError(ProgramError):
    """Error raised when there is a syntax error with the source code of a program."""


class ProgramRuntimeError(ProgramError):
    """Error raised when there is a error while the program is running. (Does not include missing input.)"""
